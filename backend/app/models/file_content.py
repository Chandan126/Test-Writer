from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class FileContent(Base):
    __tablename__ = "file_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Store extracted text content
    status = Column(String(50), nullable=False, default="pending")  # pending/processing/completed/failed
    content_type = Column(String(100), nullable=False)  # text/plain, application/pdf, etc.
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship back to File table
    file = relationship("File", back_populates="contents")
