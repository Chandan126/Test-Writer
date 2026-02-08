from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FileContentBase(BaseModel):
    content: str = Field(..., description="Extracted text content from file")
    status: str = Field(..., description="Processing status (pending/processing/completed/failed)")
    content_type: str = Field(..., description="Type of content extraction")


class FileContentCreate(FileContentBase):
    file_id: int = Field(..., description="Foreign key to File table")


class FileContentUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated content")
    status: Optional[str] = Field(None, description="Updated status")


class FileContent(FileContentBase):
    id: int
    file_id: int
    content: str
    status: str
    content_type: str
    extracted_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FileContentList(BaseModel):
    """Schema for listing multiple file contents"""
    contents: list[FileContent]
    total: int
    skip: int
    limit: int
