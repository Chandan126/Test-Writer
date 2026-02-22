from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.file_service import file_service
from app.crud.file import file as file_crud
from app.schemas.file import FileMetadata, FileList
import asyncio
import io
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
        
        # Trigger automatic content extraction and test writer pipeline in background
        try:
            import asyncio
            asyncio.create_task(file_service.extract_content_with_test_writer(db, db_file.id))
        except Exception as e:
            # Log error but don't fail the upload
            logger.error(f"Failed to trigger content extraction and test writer pipeline for file {db_file.id}: {e}")
        
        return FileMetadata.from_orm(db_file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/{file_id}/start-test-writer")
async def start_test_writer_pipeline(
    file_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start 7-agent test case writer pipeline for a file after content extraction
    """
    try:
        # Verify file exists and has extracted content
        db_file = file_crud.get(db, file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        # Check if content has been extracted
        from app.crud.file_content import file_content_crud
        extracted_content = file_content_crud.get_by_file_id(db, file_id=file_id)
        if not extracted_content:
            raise HTTPException(
                status_code=400, 
                detail=f"File {file_id} content has not been extracted yet. Please wait for extraction to complete."
            )
        
        # Import and use test writer pipeline service
        from app.services.test_writer_pipeline import test_writer_pipeline_service
        
        # Create pipeline
        pipeline_id = test_writer_pipeline_service.create_pipeline(file_id)
        
        # Start pipeline execution in background
        background_tasks.add_task(
            test_writer_pipeline_service.execute_pipeline,
            pipeline_id,
            db
        )
        
        logger.info(f"🚀 Started test writer pipeline {pipeline_id} for file {file_id}")
        
        return {
            "pipeline_id": pipeline_id,
            "file_id": file_id,
            "status": "started",
            "message": "Test case writer pipeline started successfully",
            "content_preview": extracted_content.content[:200] + "..." if len(extracted_content.content) > 200 else extracted_content.content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to start test writer pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start test writer pipeline: {str(e)}")


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


@router.post("/{file_id}/extract", response_model=dict)
async def extract_file_content(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Extract content from file using LangGraph OCR system
    """
    try:
        content = await file_service.extract_content(db, file_id)
        if content:
            return {
                "file_id": file_id,
                "content": content,
                "status": "completed"
            }
        else:
            return {
                "file_id": file_id,
                "content": "",
                "status": "failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract content: {str(e)}")
