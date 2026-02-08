from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automatic Test Writer API with file storage",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For POC - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Test Writer API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "redoc": f"{settings.API_V1_STR}/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "test-writer-api"}


@app.get(f"{settings.API_V1_STR}/info")
async def api_info():
    """API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "api_version": settings.API_V1_STR,
        "features": {
            "file_upload": True,
            "file_download": True,
            "metadata_tracking": True,
            "s3_storage": True,
            "postgresql": True
        },
        "limits": {
            "max_file_size": settings.MAX_FILE_SIZE,
            "allowed_extensions": settings.allowed_extensions_list
        }
    }
