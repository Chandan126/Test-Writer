from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.file_service import file_service
from app.schemas.file import FileMetadata, FileList
import io

router = APIRouter()


@router.post("/upload", response_model=FileMetadata)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file to S3 and save metadata to database
    """
    try:
        db_file = await file_service.upload_file(db, file)
        return FileMetadata.from_orm(db_file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a file by ID
    Returns the file content as streaming response
    """
    try:
        file_data, content_type, original_name = file_service.download_file(db, file_id)
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={original_name}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Get file metadata only (no download)
    """
    try:
        return file_service.get_file_metadata(db, file_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")


@router.get("/", response_model=FileList)
async def list_files(
    skip: int = Query(0, ge=0, description="Number of files to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    db: Session = Depends(get_db)
):
    """
    List all files with pagination
    """
    try:
        files, total = file_service.list_files(db, skip=skip, limit=limit)
        return FileList(
            files=files,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a file from S3 and database
    """
    try:
        file_service.delete_file(db, file_id)
        return {"message": f"File {file_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/{file_id}/url")
async def get_download_url(
    file_id: int,
    expiration: Optional[int] = Query(3600, ge=60, le=86400, description="URL expiration in seconds"),
    db: Session = Depends(get_db)
):
    """
    Generate a presigned URL for file download
    Useful for direct browser access
    """
    try:
        url = file_service.generate_download_url(db, file_id, expiration)
        if url is None:
            raise HTTPException(status_code=500, detail="Failed to generate download URL")
        
        return {"download_url": url, "expires_in": expiration}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate URL: {str(e)}")


@router.get("/{file_id}/exists")
async def check_file_exists(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if file exists in both database and S3
    """
    try:
        exists = file_service.check_file_exists(db, file_id)
        return {"file_id": file_id, "exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check file existence: {str(e)}")
