from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.core.s3_client import s3_client
from app.core.file_utils import file_processor
from app.crud.file import file as file_crud
from app.schemas.file import FileCreate, FileMetadata
from app.models.file import File


class FileService:
    def __init__(self):
        self.s3_client = s3_client
        self.file_processor = file_processor
        self.file_crud = file_crud
    
    async def upload_file(
        self, 
        db: Session, 
        file: UploadFile
    ) -> File:
        """
        Upload file to S3 and save metadata to database
        """
        # Validate file
        is_valid, error_message = self.file_processor.validate_upload_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Process file
        file_data, content_type, sanitized_name, file_size = await self.file_processor.process_upload(file)
        
        # Generate storage filename and S3 key
        storage_filename = self.file_processor.generate_storage_filename(sanitized_name)
        
        # Upload to S3
        uploaded_s3_key = self.s3_client.upload_file(file_data, storage_filename, content_type)
        if not uploaded_s3_key:
            raise HTTPException(status_code=500, detail="Failed to upload file to storage")
        
        # Save metadata to database
        file_create = FileCreate(
            filename=storage_filename,
            original_name=sanitized_name,
            file_size=file_size,
            content_type=content_type,
            s3_key=uploaded_s3_key
        )
        
        db_file = self.file_crud.create_with_metadata(db, obj_in=file_create)
        return db_file
    
    def download_file(self, db: Session, file_id: int) -> Tuple[bytes, str, str]:
        """
        Download file from S3
        Returns (file_data, content_type, original_name)
        """
        # Get file metadata from database
        db_file = self.file_crud.get(db, id=file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Download from S3
        file_data = self.s3_client.download_file(db_file.s3_key)
        if file_data is None:
            raise HTTPException(status_code=500, detail="Failed to download file from storage")
        
        return file_data, db_file.content_type, db_file.original_name
    
    def delete_file(self, db: Session, file_id: int) -> bool:
        """
        Delete file from S3 and database
        """
        # Get file metadata from database
        db_file = self.file_crud.get(db, id=file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from S3
        s3_deleted = self.s3_client.delete_file(db_file.s3_key)
        if not s3_deleted:
            # Log warning but continue with database deletion
            print(f"Warning: Failed to delete file from S3: {db_file.s3_key}")
        
        # Delete from database
        self.file_crud.remove(db, id=file_id)
        return True
    
    def get_file_metadata(self, db: Session, file_id: int) -> FileMetadata:
        """
        Get file metadata only
        """
        db_file = self.file_crud.get(db, id=file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileMetadata.from_orm(db_file)
    
    def list_files(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[FileMetadata], int]:
        """
        List files with pagination
        Returns (files, total_count)
        """
        files, total = self.file_crud.get_multi_with_pagination(db, skip=skip, limit=limit)
        file_metadata = [FileMetadata.from_orm(file) for file in files]
        return file_metadata, total
    
    def get_file_by_s3_key(self, db: Session, s3_key: str) -> Optional[File]:
        """
        Get file by S3 key
        """
        return self.file_crud.get_by_s3_key(db, s3_key=s3_key)
    
    def generate_download_url(self, db: Session, file_id: int, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for file download
        """
        db_file = self.file_crud.get(db, id=file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return self.s3_client.generate_presigned_url(db_file.s3_key, expiration)
    
    def check_file_exists(self, db: Session, file_id: int) -> bool:
        """
        Check if file exists in both database and S3
        """
        db_file = self.file_crud.get(db, id=file_id)
        if not db_file:
            return False
        
        return self.s3_client.file_exists(db_file.s3_key)


# Global file service instance
file_service = FileService()
