import logging
import os
import io
from typing import Optional
from sqlalchemy.orm import Session
from app.core.ollama_client import ollama_client
from app.core.s3_client import s3_client
from app.crud.file_content import file_content_crud
from app.crud.file import file as file_crud
from app.schemas.file_content import FileContentCreate
import PyPDF2
import pandas as pd

logger = logging.getLogger(__name__)


class SimpleContentExtractionService:
    """Content extraction service with AI cleanup"""
    
    SUPPORTED_TYPES = {
        'application/pdf',
        'text/csv', 
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    async def extract_content_from_file(self, db: Session, file_id: int) -> Optional[str]:
        """Extract content from file and clean with AI"""
        try:
            print(f"🔥 CONTENT EXTRACTION STARTED for file {file_id}")  # Debug log
            logger.info(f"🚀 Starting content extraction for file {file_id}")
            
            # Step 1: Get file information
            logger.info(f"📁 Step 1: Retrieving file information for file {file_id}")
            db_file = file_crud.get(db, file_id)
            if not db_file:
                logger.error(f"❌ File {file_id} not found in database")
                return None
            
            logger.info(f"✅ File found: {db_file.original_name}, type: {db_file.content_type}, size: {db_file.file_size} bytes")
            
            # Step 2: Validate file type
            if db_file.content_type not in self.SUPPORTED_TYPES:
                logger.error(f"❌ Unsupported file type: {db_file.content_type}. Supported types: {self.SUPPORTED_TYPES}")
                return None
            
            # Step 3: Update file status to processing
            logger.info(f"🔄 Step 3: Updating file status to 'processing'")
            file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "processing"})
            logger.info(f"✅ File status updated to processing")
            
            # Step 4: Download file from S3
            logger.info(f"⬇️ Step 4: Downloading file from S3 with key: {db_file.s3_key}")
            file_content = await self._download_file_from_s3(db_file.s3_key)
            if not file_content:
                logger.error(f"❌ Failed to download file {file_id} from S3")
                file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "failed"})
                return None
            
            logger.info(f"✅ Successfully downloaded {len(file_content)} bytes from S3")
            
            # Step 5: Extract raw content based on file type
            logger.info(f"📄 Step 5: Extracting raw content from {db_file.content_type}")
            raw_content = None
            
            if db_file.content_type == 'application/pdf':
                raw_content = await self._extract_from_pdf(file_content, file_id)
            elif db_file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                raw_content = await self._extract_from_spreadsheet(file_content, db_file.content_type, file_id)
            
            if not raw_content:
                logger.error(f"❌ Failed to extract raw content from file {file_id}")
                file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "failed"})
                return None
            
            logger.info(f"✅ Successfully extracted {len(raw_content)} characters of raw content")
            
            # Step 6: Clean content with AI
            logger.info(f"🤖 Step 6: Cleaning extracted content with AI")
            cleaned_content = await self._clean_content_with_ai(raw_content, db_file.content_type, file_id)
            
            if not cleaned_content:
                logger.error(f"❌ AI cleaning failed for file {file_id}")
                file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "failed"})
                return None
            
            logger.info(f"✅ Successfully cleaned content to {len(cleaned_content)} characters")
            
            # Step 7: Save result to database
            logger.info(f"💾 Step 7: Saving cleaned content to database")
            await self._save_extraction_result(db, cleaned_content, db_file)
            logger.info(f"✅ Successfully extracted and saved content for file {file_id}")
            
            return cleaned_content
                    
        except Exception as e:
            logger.error(f"💥 Extraction failed for file {file_id}: {e}")
            # Update file status to failed
            try:
                db_file = file_crud.get(db, file_id)
                if db_file:
                    file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "failed"})
                    logger.info(f"✅ File status updated to 'failed'")
            except Exception as e:
                logger.error(f"❌ Failed to update file status for file {file_id}: {e}")
            return None
    
    async def _clean_content_with_ai(self, raw_content: str, content_type: str, file_id: int) -> Optional[str]:
        """Clean and structure extracted content using AI"""
        try:
            logger.info(f"🤖 Sending content to AI for cleaning and structuring")
            
            # Use the new clean_text method from ollama_client
            cleaned_content = await ollama_client.clean_text(raw_content, content_type)
            
            if cleaned_content:
                logger.info(f"✅ AI cleaned content from {len(raw_content)} to {len(cleaned_content)} characters")
                return cleaned_content
            else:
                logger.error(f"❌ AI cleaning returned None for file {file_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ AI content cleaning failed for file {file_id}: {e}")
            # Return raw content as fallback
            logger.info(f"🔄 Returning raw content as fallback")
            return raw_content
    
    async def _extract_from_pdf(self, file_content: bytes, file_id: int) -> Optional[str]:
        """Extract text content from PDF using PyPDF2"""
        try:
            logger.info(f"📄 Extracting text from PDF using PyPDF2")
            
            # Read PDF content
            pdf_stream = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text.strip()}\n"
                        logger.info(f"📄 Extracted {len(page_text)} characters from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not extract text from page {page_num + 1}: {e}")
            
            if text_content.strip():
                logger.info(f"✅ Successfully extracted {len(text_content)} characters from PDF")
                return text_content.strip()
            else:
                logger.warning(f"⚠️ No text content found in PDF for file {file_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ PDF text extraction failed for file {file_id}: {e}")
            return None
    
    async def _extract_from_spreadsheet(self, file_content: bytes, content_type: str, file_id: int) -> Optional[str]:
        """Extract content from spreadsheet files"""
        try:
            logger.info(f"📊 Extracting content from spreadsheet: {content_type}")
            
            # Read spreadsheet content
            spreadsheet_stream = io.BytesIO(file_content)
            
            if content_type == 'text/csv':
                # Handle CSV files
                df = pd.read_csv(spreadsheet_stream)
                content = df.to_string(index=False)
                logger.info(f"✅ Successfully extracted {len(content)} characters from CSV")
                return content
            else:
                # Handle Excel files
                df = pd.read_excel(spreadsheet_stream)
                content = df.to_string(index=False)
                logger.info(f"✅ Successfully extracted {len(content)} characters from Excel")
                return content
                
        except Exception as e:
            logger.error(f"❌ Spreadsheet extraction failed for file {file_id}: {e}")
            return None
    
    async def _extract_from_text(self, file_content: bytes, file_id: int) -> Optional[str]:
        """Extract content from text files"""
        try:
            logger.info(f"📝 Extracting content from text file")
            
            # Decode text content
            text_content = file_content.decode('utf-8', errors='ignore')
            logger.info(f"✅ Successfully extracted {len(text_content)} characters from text file")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"❌ Text file extraction failed for file {file_id}: {e}")
            return None
    
    async def _download_file_from_s3(self, s3_key: str) -> Optional[bytes]:
        """Download file content from S3"""
        try:
            logger.info(f"📥 Attempting to download file from S3: {s3_key}")
            content = s3_client.download_file(s3_key)
            logger.info(f"✅ Successfully downloaded {len(content)} bytes from S3")
            return content
        except Exception as e:
            logger.error(f"❌ S3 download failed for {s3_key}: {e}")
            return None
    
    async def _save_extraction_result(self, db: Session, content: str, db_file):
        """Save extraction result to database"""
        try:
            logger.info(f"💾 Saving extraction result for file {db_file.id}")
            logger.info(f"📊 Content length: {len(content)} characters")
            
            # Create content record
            content_data = FileContentCreate(
                file_id=db_file.id,
                content=content,
                status="completed",
                content_type=db_file.content_type
            )
            
            logger.info(f"📝 Creating FileContent record")
            file_content_crud.create_with_file(db, obj_in=content_data)
            logger.info(f"✅ FileContent record created successfully")
            
            # Update file status
            logger.info(f"🔄 Updating file status to 'completed'")
            file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "completed"})
            logger.info(f"✅ File status updated successfully")
            
            logger.info(f"🎉 Extraction result saved successfully for file {db_file.id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save extraction result for file {db_file.id}: {e}")
            logger.error(f"🔄 Updating file status to 'failed' due to save error")
            file_crud.update(db, db_obj=db_file, obj_in={"processing_status": "failed"})


# Create singleton instance
content_extraction_service = SimpleContentExtractionService()
