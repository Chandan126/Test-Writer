from fastapi import APIRouter
from app.api.v1.endpoints import files
from app.api.v1.endpoints import file_content

api_router = APIRouter()

api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(file_content.router, prefix="/files", tags=["file-content"])
