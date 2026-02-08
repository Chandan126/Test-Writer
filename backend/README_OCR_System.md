# LangGraph OCR Extraction System

A sophisticated multi-agent OCR system using LangGraph and Ollama models for robust file content extraction.

## 🏗️ Architecture

### 3-Agent Workflow
```
File Upload → Agent 1 (glm-ocr) ↘
                               → Agent 3 (qwen3:8b) → Final Content → Database
File Upload → Agent 2 (qwen3-vl:4b) ↗
```

### Agents Overview

#### Agent 1: OCR Reader (glm-ocr:latest)
- **Purpose**: Specialized OCR text extraction
- **Strengths**: Optimized for text recognition
- **Output**: Raw extracted text with high confidence

#### Agent 2: Vision Reader (qwen3-vl:4b)
- **Purpose**: Vision-based content understanding
- **Strengths**: Better layout and context analysis
- **Output**: Structured content with spatial awareness

#### Agent 3: Reviewer Agent (qwen3:8b)
- **Purpose**: Content review and consolidation
- **Strengths**: Higher reasoning capacity for quality assessment
- **Output**: Final validated and consolidated content

## 🚀 Features

### Multi-Model Accuracy
- **Redundant Extraction**: Two different models extract content
- **Cross-Validation**: Third model reviews and validates results
- **Conflict Resolution**: Intelligent merging of different extraction results

### File Type Support
- **Images**: JPG, PNG, GIF, WebP
- **Documents**: PDF (first page extraction)
- **Text Files**: TXT, CSV (converted to image for OCR)
- **Extensible**: Easy to add new file type handlers

### Robust Error Handling
- **Model Failures**: Graceful fallbacks when models fail
- **Network Issues**: Retry logic and timeout handling
- **File Processing**: Comprehensive error tracking and logging

## 📦 Dependencies

```python
langgraph>=0.0.40      # Workflow orchestration
ollama>=0.1.7          # Local AI model management
Pillow>=10.0.0           # Image processing
pdf2image>=1.16.0        # PDF to image conversion
```

## 🔧 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull glm-ocr:latest
ollama pull qwen3-vl:4b
ollama pull qwen3:8b

# Start Ollama service
ollama serve
```

### 3. Database Setup
```bash
# Start services with Docker
docker-compose up -d

# Create database tables (handled automatically on startup)
```

## 🌐 API Usage

### Extract Content from File
```bash
POST /api/v1/files/{file_id}/extract
```

**Response:**
```json
{
  "file_id": 123,
  "content": "Extracted text content here...",
  "status": "completed"
}
```

### Get Extracted Content
```bash
GET /api/v1/files/{file_id}/content
```

### Check Processing Status
```bash
GET /api/v1/files/{file_id}
```

## 🧪 Testing

### Run System Tests
```bash
cd backend
python test_ocr_system.py
```

**Test Coverage:**
- ✅ Ollama connection and model availability
- ✅ Agent initialization and state management
- ✅ LangGraph workflow compilation
- ✅ End-to-end extraction pipeline

## 📊 Workflow Process

### 1. File Preparation
- Download file from S3 storage
- Convert to appropriate format (JPEG for OCR)
- Optimize image size and quality
- Create temporary processing file

### 2. Parallel Extraction
- **Agent 1**: Extract using glm-ocr model
- **Agent 2**: Extract using qwen3-vl model
- Both agents run independently for redundancy

### 3. Content Review
- **Agent 3**: Receives both extraction results
- Compares and validates content quality
- Resolves conflicts and consolidates final output
- Assigns confidence scores

### 4. Database Storage
- Save final content to FileContent table
- Update file processing status
- Store extraction metadata and confidence scores

## 🔍 Configuration

### Model Configuration
```python
# In app/core/ollama_client.py
self.models = {
    "ocr": "glm-ocr:latest",
    "vision": "qwen3-vl:4b", 
    "reviewer": "qwen3:8b"
}
```

### File Processing Limits
- **Max Image Size**: 2000x2000 pixels
- **PDF DPI**: 200 for optimal OCR
- **Text Limit**: 1000 characters for text-to-image fallback
- **Timeout**: 30 seconds per agent

## 🚨 Error Handling

### Common Issues & Solutions

#### Ollama Connection Failed
- **Check**: Ollama service running on localhost:11434
- **Solution**: Start Ollama with `ollama serve`

#### Model Not Available
- **Check**: Model pulled with `ollama list`
- **Solution**: Pull missing models with `ollama pull <model>`

#### Extraction Failed
- **Check**: File format supported
- **Solution**: Verify file not corrupted, try different format

#### Memory Issues
- **Check**: Available RAM for large models
- **Solution**: Use smaller models or increase system memory

## 📈 Performance

### Expected Processing Times
- **Small Images (<1MB)**: 10-30 seconds
- **Large Images (>5MB)**: 30-60 seconds
- **PDF Documents**: 20-45 seconds per page

### Optimization Tips
- **Batch Processing**: Process multiple files concurrently
- **Model Caching**: Keep models loaded in memory
- **Image Optimization**: Pre-process images for optimal OCR

## 🔮 Future Enhancements

### Planned Features
- **Multi-Page PDF**: Extract all pages, not just first
- **Batch OCR**: Process multiple files simultaneously
- **Model Selection**: Choose optimal model per file type
- **Confidence Scoring**: Detailed confidence metrics
- **Progress Tracking**: Real-time extraction progress

### Integration Opportunities
- **AI Writer**: Direct integration with test generation
- **Content Analysis**: Advanced content understanding
- **Format Conversion**: Support for more file types
- **Cloud Models**: Option for cloud-based OCR services

## 🤝 Contributing

### Adding New Agents
1. Create agent method in `ExtractionAgents` class
2. Add agent to LangGraph workflow
3. Update Ollama client with new model
4. Add corresponding tests

### Supporting New File Types
1. Add handler in `_prepare_file_for_processing`
2. Update content type detection
3. Add specific test cases
4. Update documentation

This system provides a robust, scalable foundation for AI-powered content extraction and analysis.
