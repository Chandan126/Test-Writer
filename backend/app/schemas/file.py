from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FileBase(BaseModel):
    original_name: str = Field(..., description="Original filename uploaded by user")
    content_type: str = Field(..., description="MIME type of the file")


class FileCreate(FileBase):
    filename: str = Field(..., description="Unique storage filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    s3_key: str = Field(..., description="S3 object key")


class FileUpdate(BaseModel):
    original_name: Optional[str] = Field(None, description="Updated filename")
    content_type: Optional[str] = Field(None, description="Updated MIME type")


class File(FileBase):
    id: int
    filename: str
    file_size: int
    s3_key: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Schema for file metadata only (without download info)"""
    id: int
    filename: str
    original_name: str
    file_size: int
    content_type: str
    s3_key: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FileList(BaseModel):
    """Schema for listing multiple files"""
    files: list[FileMetadata]
    total: int
    skip: int
    limit: int
