# Document Upload System with S3 Storage and PostgreSQL

This plan outlines the implementation of a simplified document upload system using FastAPI with S3-compatible object storage (MinIO) for file storage and PostgreSQL for file metadata management, focusing on POC functionality without user management.

## Architecture Overview

The system will consist of:
1. **FastAPI Backend**: REST API for document upload/download operations
2. **MinIO Container**: S3-compatible object storage for actual files
3. **PostgreSQL Container**: Database for file metadata only
4. **Docker Compose**: Orchestration of all services

## Implementation Plan

### 1. Docker Infrastructure Setup
- Create `docker-compose.yml` with PostgreSQL and MinIO services
- Configure environment variables for both services
- Set up persistent volumes for data storage

### 2. Database Schema Design
- Create `File` model with fields: id, filename, original_name, file_size, content_type, s3_key, created_at, updated_at
- No user management - simplified POC approach
- Focus on file metadata tracking only

### 3. S3 Integration Layer
- Install and configure `boto3` for S3 operations
- Create S3 client wrapper for upload/download/delete operations
- Implement file key generation strategy (e.g., UUID-based)
- Add error handling for S3 operations

### 4. API Endpoints
- `POST /files/upload` - Upload document with metadata
- `GET /files/{file_id}` - Download file by ID
- `GET /files/` - List all files (no user filtering)
- `DELETE /files/{file_id}` - Delete file and metadata
- `GET /files/{file_id}/metadata` - Get file metadata only

### 5. File Processing Features
- File type validation and size limits
- Thumbnail generation for images (optional)
- Virus scanning integration point
- Duplicate detection based on file hash

### 6. Security & Authentication
- No authentication for POC simplicity
- File access control based on file ID only
- Rate limiting for upload operations
- Input validation and sanitization

### 7. Configuration Management
- Environment-based configuration
- S3 bucket and endpoint configuration
- Database connection settings
- File upload limits and allowed types

## Technical Stack
- **Backend**: FastAPI with SQLAlchemy ORM
- **Storage**: MinIO (S3-compatible)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **File Handling**: boto3 for S3 operations

## File Structure
```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   └── files.py              # File upload/download endpoints
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   └── s3_client.py           # S3 operations wrapper
│   ├── models/
│   │   └── file.py                # File metadata model
│   ├── schemas/
│   │   └── file.py                # File schemas
│   ├── crud/
│   │   └── file.py                # File CRUD operations
│   ├── db/
│   │   ├── session.py             # Database session
│   │   └── base_class.py          # SQLAlchemy base
│   └── main.py                    # FastAPI application
├── docker-compose.yml             # Service orchestration
├── Dockerfile                     # Application container
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

## Key Features
- File upload/download with metadata tracking
- S3 integration using boto3 with local MinIO
- File validation and security controls
- Simple POC without user management
- Resumable uploads for large files
- File sharing with expiring links
- Comprehensive audit logging
- Automatic cleanup of orphaned files
