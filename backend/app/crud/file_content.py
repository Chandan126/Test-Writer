from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.file_content import FileContent
from app.schemas.file_content import FileContentCreate


class CRUDFileContent(CRUDBase[FileContent, FileContentCreate, dict]):
    def create_with_file(
        self, db: Session, *, obj_in: FileContentCreate
    ) -> FileContent:
        """Create file content linked to existing file"""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_file_id(
        self, db: Session, file_id: int
    ) -> Optional[FileContent]:
        """Get all content records for a specific file"""
        return (
            db.query(self.model)
            .filter(FileContent.file_id == file_id)
            .order_by(FileContent.extracted_at.desc())
            .all()
        )
    
    def get_latest_by_file_id(
        self, db: Session, file_id: int
    ) -> Optional[FileContent]:
        """Get the latest content record for a file"""
        return (
            db.query(self.model)
            .filter(FileContent.file_id == file_id)
            .order_by(FileContent.extracted_at.desc())
            .first()
        )
    
    def update_status(
        self, db: Session, file_id: int, status: str
    ) -> Optional[FileContent]:
        """Update processing status for all content of a file"""
        db.query(self.model).filter(FileContent.file_id == file_id).update(
            {"status": status}
        )
        db.commit()
        return self.get_latest_by_file_id(db, file_id)
    
    def update_content(
        self, db: Session, file_id: int, content: str
    ) -> Optional[FileContent]:
        """Update content for the latest record of a file"""
        latest_content = self.get_latest_by_file_id(db, file_id)
        if latest_content:
            latest_content.content = content
            latest_content.status = "completed"
            db.commit()
            db.refresh(latest_content)
        return latest_content


# Create a singleton instance
file_content_crud = CRUDFileContent(FileContent)
