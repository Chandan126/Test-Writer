from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.schemas.file import FileCreate, FileUpdate
from app.models.file import File


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    def get_by_s3_key(self, db: Session, *, s3_key: str) -> Optional[File]:
        """Get file by S3 key"""
        return db.query(File).filter(File.s3_key == s3_key).first()
    
    def get_by_original_name(self, db: Session, *, original_name: str) -> List[File]:
        """Get files by original name (can have duplicates)"""
        return db.query(File).filter(File.original_name == original_name).all()
    
    def create_with_metadata(self, db: Session, *, obj_in: FileCreate) -> File:
        """Create file with metadata"""
        db_obj = File(
            filename=obj_in.filename,
            original_name=obj_in.original_name,
            file_size=obj_in.file_size,
            content_type=obj_in.content_type,
            s3_key=obj_in.s3_key
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_multi_with_pagination(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[File], int]:
        """Get multiple files with pagination and total count"""
        query = db.query(File)
        total = query.count()
        files = query.offset(skip).limit(limit).all()
        return files, total
    
    def get_files_by_size_range(
        self, 
        db: Session, 
        *, 
        min_size: Optional[int] = None, 
        max_size: Optional[int] = None
    ) -> List[File]:
        """Get files within size range"""
        query = db.query(File)
        if min_size is not None:
            query = query.filter(File.file_size >= min_size)
        if max_size is not None:
            query = query.filter(File.file_size <= max_size)
        return query.all()


file = CRUDFile(File)
