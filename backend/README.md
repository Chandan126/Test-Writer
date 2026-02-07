# Test Writer API - Document Upload System

A FastAPI backend with MinIO S3 storage and PostgreSQL for automatic test writer document management.

## Quick Start

### 1. Start Docker Services
```bash
docker compose up -d
```

### 2. Verify Services
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **PostgreSQL**: localhost:5432
- **API**: http://localhost:8000

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 4. Test Upload (curl example)
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf"
```

## Services

### PostgreSQL
- **Database**: test_writer_db
- **User**: postgres
- **Password**: postgres
- **Port**: 5432

### MinIO
- **Endpoint**: http://localhost:9000
- **Console**: http://localhost:9001
- **Access Key**: minioadmin
- **Secret Key**: minioadmin
- **Bucket**: test_writer_files

### FastAPI Backend
- **Port**: 8000
- **API Base**: /api/v1
- **Auto Docs**: /api/v1/docs

## API Endpoints

### Files
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/{file_id}/download` - Download file
- `GET /api/v1/files/{file_id}/metadata` - Get file metadata
- `GET /api/v1/files/` - List files (paginated)
- `DELETE /api/v1/files/{file_id}` - Delete file
- `GET /api/v1/files/{file_id}/url` - Get download URL
- `GET /api/v1/files/{file_id}/exists` - Check file exists

### System
- `GET /` - Root info
- `GET /health` - Health check
- `GET /api/v1/info` - API information

## Features

- ✅ File upload/download with S3 storage
- ✅ PostgreSQL metadata tracking
- ✅ File validation (size, type)
- ✅ UUID-based file keys
- ✅ Presigned URLs for secure access
- ✅ Paginated file listings
- ✅ Auto-generated API docs
- ✅ Docker containerization

## Configuration

Environment variables in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `MINIO_ENDPOINT` - MinIO endpoint URL
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET` - MinIO bucket name
- `MAX_FILE_SIZE` - Maximum file size (bytes)
- `ALLOWED_EXTENSIONS` - Comma-separated file extensions

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development
```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## File Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/files.py    # File API endpoints
│   ├── core/
│   │   ├── config.py                # Configuration
│   │   ├── s3_client.py             # S3 operations
│   │   └── file_utils.py            # File utilities
│   ├── services/file_service.py     # Business logic
│   ├── models/file.py               # Database models
│   ├── schemas/file.py              # Pydantic schemas
│   ├── crud/file.py                 # Database operations
│   ├── db/session.py                # Database session
│   └── main.py                      # FastAPI app
├── docker-compose.yml              # Docker services
├── Dockerfile                       # App container
├── requirements.txt                 # Python deps
└── .env                            # Environment variables
```
