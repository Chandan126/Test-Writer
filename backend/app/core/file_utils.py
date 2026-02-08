import os
import hashlib
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class FileValidator:
    @staticmethod
    def validate_file_size(file: UploadFile) -> bool:
        """Validate file size against maximum allowed size"""
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return False
        return True
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension against allowed extensions"""
        if not filename:
            return False
        
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        return file_extension in settings.allowed_extensions_list
    
    @staticmethod
    def get_content_type(filename: str) -> str:
        """Get MIME type based on file extension"""
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'zip': 'application/zip',
            'json': 'application/json',
            'csv': 'text/csv'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    @staticmethod
    def calculate_file_hash(file_data: bytes) -> str:
        """Calculate SHA-256 hash of file data"""
        return hashlib.sha256(file_data).hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing potentially harmful characters"""
        # Remove path separators and special characters
        sanitized = os.path.basename(filename)
        # Remove characters that are problematic in filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized


class FileProcessor:
    def __init__(self):
        self.validator = FileValidator()
    
    def validate_upload_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        Returns (is_valid, error_message)
        """
        # Check if file was provided
        if not file or not file.filename:
            return False, "No file provided"
        
        # Validate file size
        if not self.validator.validate_file_size(file):
            return False, f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        
        # Validate file extension
        if not self.validator.validate_file_extension(file.filename):
            allowed = ', '.join(settings.allowed_extensions_list)
            return False, f"File type not allowed. Allowed types: {allowed}"
        
        return True, None
    
    async def process_upload(
        self, 
        file: UploadFile
    ) -> Tuple[bytes, str, str, int]:
        """
        Process uploaded file
        Returns (file_data, content_type, sanitized_filename, file_size)
        """
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
        
        # Get content type
        content_type = self.validator.get_content_type(file.filename)
        
        # Sanitize filename
        sanitized_filename = self.validator.sanitize_filename(file.filename)
        
        return file_content, content_type, sanitized_filename, file_size
    
    def generate_storage_filename(self, original_filename: str) -> str:
        """Generate unique storage filename"""
        import uuid
        extension = original_filename.split('.')[-1] if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{extension}" if extension else unique_id


# Global file processor instance
file_processor = FileProcessor()
