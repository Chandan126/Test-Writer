from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.file_content import file_content_crud
from app.schemas.file_content import FileContent, FileContentCreate
from app.models.file import File

router = APIRouter()


@router.get("/{file_id}/content", response_model=FileContent)
async def get_file_content(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest extracted content for a file"""
    content = file_content_crud.get_latest_by_file_id(db, file_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.post("/{file_id}/content", response_model=FileContent)
async def create_file_content(
    file_id: int,
    content: str,
    status: str = "completed",
    db: Session = Depends(get_db)
):
    """Create new content record for a file"""
    # Verify file exists
    file_crud = __import__("app.crud.file", fromlist=["file"])
    db_file = file_crud.get(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Create content record
    content_data = FileContentCreate(
        file_id=file_id,
        content=content,
        status=status,
        content_type=db_file.content_type
    )
    
    return file_content_crud.create_with_file(db, obj_in=content_data)


@router.put("/{file_id}/content/status")
async def update_content_status(
    file_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update processing status for all content of a file"""
    # Verify file exists
    file_crud = __import__("app.crud.file", fromlist=["file"])
    db_file = file_crud.get(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    updated_content = file_content_crud.update_status(db, file_id=file_id, status=status)
    if not updated_content:
        raise HTTPException(status_code=500, detail="Failed to update status")
    
    return {"message": f"Status updated to {status}", "content": updated_content}
