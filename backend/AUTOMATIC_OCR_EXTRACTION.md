# Automatic Content Extraction on File Upload

## 🎯 Overview

The system now automatically triggers content extraction when files are uploaded, providing a seamless user experience for PDF, CSV, and Excel file processing with AI-powered text cleaning.

## 🔄 Workflow

### 1. File Upload Process
```
User Uploads File → API Endpoint → S3 Storage → Database Record → Background Content Extraction Trigger
```

### 2. Automatic Extraction Trigger
```python
# In upload endpoint (app/api/v1/endpoints/files.py)
@router.post("/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile, db: Session):
    db_file = await file_service.upload_file(db, file)
    
    # 🚀 AUTOMATIC CONTENT EXTRACTION TRIGGERED HERE
    asyncio.create_task(file_service.extract_content(db, db_file.id))
    
    return FileMetadata.from_orm(db_file)
```

### 3. Simplified Processing Pipeline
```
Background Task → Direct Text Extraction → AI Text Cleaning → Database Storage
```

**Supported File Types:**
- 📄 **PDF**: Direct text extraction with PyPDF2
- 📊 **CSV/Excel**: Data extraction with pandas
- 🤖 **AI Cleanup**: qwen3:8b model for text cleaning and structuring

## 📊 API Endpoints

### Upload with Auto-Extraction
```bash
POST /api/v1/files/upload
Content-Type: multipart/form-data

# Response
{
  "id": 123,
  "filename": "unique_name.pdf",
  "original_name": "document.pdf",
  "file_size": 1024000,
  "content_type": "application/pdf",
  "s3_key": "uuid-filename.pdf",
  "processing_status": "pending",  # Status updates during extraction
  "created_at": "2024-02-08T12:00:00Z"
}
```

### Manual Extraction Trigger
```bash
POST /api/v1/files/{file_id}/extract

# Response
{
  "file_id": 123,
  "content": "Cleaned and structured text content here...",
  "status": "completed"
}
```

### Get Extracted Content
```bash
GET /api/v1/files/{file_id}/content

# Response
{
  "id": 456,
  "file_id": 123,
  "content": "Final cleaned content from AI processing",
  "status": "completed",
  "content_type": "application/pdf",
  "extracted_at": "2024-02-08T12:05:00Z"
}
```

## 🧪 Testing

### Run Upload + Extraction Test
```bash
cd backend
python test_upload_extraction.py
```

**Test Coverage:**
- ✅ File upload to S3
- ✅ Database record creation
- ✅ Background content extraction trigger
- ✅ Direct text extraction (PDF/CSV/Excel)
- ✅ AI text cleaning with qwen3
- ✅ Content database storage
- ✅ API endpoint responses

### Expected Output
```
🚀 Testing Upload + Automatic Content Extraction

📤 Uploading test file...
✅ File uploaded successfully! File ID: 123
📊 File metadata: {...}

🔍 Checking extraction status...
📝 Extraction Status: completed
✅ Extraction successful!
📄 Extracted Content Preview:
--------------------------------------------------
This is cleaned and structured content from the document...
--------------------------------------------------
✅ Content saved to database successfully!
```

## 🔧 Configuration

### Background Processing
- **Non-blocking**: Upload returns immediately
- **Async Task**: Content extraction runs in background
- **Status Updates**: File processing_status field tracks progress
- **Error Handling**: Upload succeeds even if extraction fails

### Processing States
```python
processing_status = "pending"      # File uploaded, extraction not started
processing_status = "processing"  # Extraction agents are running
processing_status = "completed"  # Extraction completed successfully
processing_status = "failed"     # Extraction failed, check logs
```

### Supported File Types
```python
SUPPORTED_TYPES = {
    'application/pdf',
    'text/csv', 
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}
```

## 📈 Benefits

### User Experience
- **Immediate Response**: Upload completes quickly
- **Transparent Status**: Users can check extraction progress
- **Reliable**: Background processing doesn't block uploads
- **Clean Output**: AI-powered text cleaning improves quality

### System Architecture
- **Simplified**: No complex multi-agent system
- **Efficient**: Direct text extraction (no OCR)
- **AI Enhanced**: qwen3 model for text cleaning
- **Fault Tolerant**: Extraction failures don't break uploads

## 🚨 Error Handling

### Upload Success, Extraction Failure
```python
# Upload succeeds even if extraction fails
try:
    asyncio.create_task(file_service.extract_content(db, db_file.id))
except Exception as e:
    print(f"Failed to trigger content extraction for file {db_file.id}: {e}")
    # Upload still succeeds!
```

### Status Monitoring
- **Database**: processing_status field shows current state
- **Logs**: Detailed extraction processing logs
- **API**: Status endpoints for monitoring
- **Recovery**: Manual re-trigger possible

## 🔮 Usage Examples

### Frontend Integration
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/v1/files/upload', {
  method: 'POST',
  body: formData
});

const uploadedFile = await response.json();

// Check extraction status
const extractResponse = await fetch(`/api/v1/files/${uploadedFile.id}/extract`, {
  method: 'POST'
});

const extractResult = await extractResponse.json();
console.log('Extraction status:', extractResult.status);
```

### Batch Processing
```python
# Upload multiple files with automatic extraction
for file in files:
    upload_response = upload_file(file)
    file_id = upload_response['id']
    
    # Content extraction runs automatically in background
    # Can monitor status individually
```

## 📋 Monitoring

### Check Processing Status
```bash
# Get file with current status
curl http://localhost:8000/api/v1/files/123

# Response shows processing_status
{
  "processing_status": "completed",
  "contents": [...]
}
```

### Backend Logs
```bash
# Monitor content extraction processing
docker compose logs backend -f

# Look for these messages:
# "Starting content extraction for file 123"
# "Successfully extracted X characters from PDF"
# "AI cleaned content from X to Y characters"
# "Saved extraction result for file 123"
```

## 🤖 AI Model Configuration

### qwen3:8b Model
- **Purpose**: Text cleaning and structuring
- **Host**: ollama:11434 (Docker service)
- **Auto-pull**: Automatically downloaded if not available
- **Context**: Optimized for cleaning extracted text

### Cleaning Prompts
- **PDF**: Remove formatting artifacts, fix extraction errors
- **CSV/Excel**: Ensure data consistency, organize tabular format
- **General**: Structure content in readable format

## 📁 File Type Processing

### PDF Files
```python
# Direct text extraction with PyPDF2
pdf_reader = PyPDF2.PdfReader(pdf_stream)
text_content = ""
for page in pdf_reader.pages:
    text_content += page.extract_text()
```

### CSV/Excel Files
```python
# Data extraction with pandas
df = pd.read_csv(csv_stream)  # or pd.read_excel()
content = df.to_string(index=False)
```

### AI Text Cleaning
```python
# Clean and structure with qwen3
cleaned_content = await ollama_client.clean_text(raw_content, content_type)
```

This simplified extraction system provides efficient, reliable processing for structured document types with AI-enhanced text quality.
