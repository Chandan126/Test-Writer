from fastapi import APIRouter
from app.api.v1.endpoints import files
from app.api.v1.endpoints import file_content
from app.api.v1.endpoints import test_writer_pipeline

api_router = APIRouter()

api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(file_content.router, prefix="/files", tags=["file-content"])
api_router.include_router(test_writer_pipeline.router, prefix="/test-writer", tags=["test-writer-pipeline"])
