# 7-Agent Test Case Writer Pipeline

## 🎯 Overview

This system implements a sophisticated 7-agent AI pipeline that transforms uploaded documents into comprehensive test cases through sequential analysis, decomposition, and refinement.

## 🔄 Pipeline Architecture

```
Upload Doc → Text Extraction → Document Understanding → Requirements Decomposition → Edge Case Analysis → Test Case Writing → Review → Final Test Set
```

## 🤖 Agent Specifications

### 1. Text Extraction Agent
- **Purpose**: Extract clean text from uploaded documents
- **Technology**: Uses existing SimpleContentExtractionService
- **Supported Formats**: PDF, CSV, Excel files
- **AI Model**: qwen3:8b for text cleaning

### 2. Document Understanding Agent
- **Purpose**: Analyze document structure, purpose, and key concepts
- **Capabilities**:
  - Identify document type and domain
  - Extract key concepts and terminology
  - Understand user personas and use cases
  - Assess complexity and scope

### 3. Requirements Decomposition Agent
- **Purpose**: Break down document into testable requirements
- **Capabilities**:
  - Extract functional and non-functional requirements
  - Define acceptance criteria
  - Map user stories to test scenarios
  - Prioritize requirements

### 4. Edge Case Agent
- **Purpose**: Identify boundary conditions and exceptional scenarios
- **Capabilities**:
  - Boundary value analysis
  - Error condition generation
  - Unusual input scenarios
  - Performance and stress testing

### 5. Test Case Writer Agent
- **Purpose**: Generate detailed test procedures
- **Capabilities**:
  - Step-by-step test creation
  - Expected result specification
  - Test data requirements
  - Setup and teardown procedures

### 6. Test Review Agent
- **Purpose**: Validate and refine test cases
- **Capabilities**:
  - Quality assurance checks
  - Coverage validation
  - Logical consistency review
  - Clarity improvements

### 7. Final Test Case Set Agent
- **Purpose**: Organize and format final documentation
- **Capabilities**:
  - Test case organization by priority/type
  - Execution plan creation
  - Documentation formatting
  - Quality metrics reporting

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Ollama with qwen3:8b model
- Python 3.11+

### Setup
```bash
# Clone and navigate to project
cd backend

# Start services
docker compose up -d

# Verify Ollama has qwen3:8b
docker exec -it ollama ollama list
```

### Usage
```bash
# Test the complete pipeline
python test_pipeline_integration.py

# Or use API endpoints directly
curl -X POST "http://localhost:8000/api/v1/test-writer/pipeline/upload?document_id=1"
```

## 📊 API Endpoints

### Pipeline Management
- `POST /api/v1/test-writer/pipeline/upload` - Start pipeline for document
- `GET /api/v1/test-writer/pipeline/{pipeline_id}/status` - Check pipeline status
- `GET /api/v1/test-writer/pipeline/{pipeline_id}/results` - Get final results
- `GET /api/v1/test-writer/pipeline/{pipeline_id}/download` - Download test cases
- `POST /api/v1/test-writer/pipeline/{pipeline_id}/cancel` - Cancel pipeline
- `DELETE /api/v1/test-writer/pipeline/{pipeline_id}` - Clean up pipeline

### Information
- `GET /api/v1/test-writer/pipelines` - List active pipelines
- `GET /api/v1/test-writer/agents` - Get agent details
- `POST /api/v1/test-writer/pipeline/quick-start` - Quick start with URLs

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── test_writer_pipeline.py    # Pipeline API endpoints
│   │   └── files.py                   # File upload endpoints
│   ├── services/
│   │   ├── test_writer_pipeline.py    # Main pipeline service
│   │   ├── document_agents.py         # Document processing agents
│   │   ├── test_case_agents.py        # Test generation agents
│   │   └── file_extraction_service.py # Text extraction service
│   ├── core/
│   │   ├── pipeline_coordinator.py    # Pipeline state management
│   │   └── ollama_client.py           # AI model client
│   ├── models/
│   │   └── test_case.py               # Database models
│   ├── schemas/
│   │   └── test_case.py               # Pydantic schemas
│   └── crud/
│       └── test_case.py               # Database operations
├── test_pipeline_integration.py      # Integration test
└── implementation_documents/         # Documentation
```

## 🎯 Sample Output

### Input Document
```
E-Commerce Platform Requirements

User Management:
1. Users must be able to register with email and password
2. Users must be able to login with valid credentials
...

Payment Processing:
1. Users must be able to checkout with items in cart
2. System must accept credit card payments
...
```

### Generated Test Cases
```json
{
  "final_test_cases": [
    {
      "id": "TC001",
      "title": "User Registration with Valid Email",
      "priority": "critical",
      "test_type": "functional",
      "test_steps": [
        {
          "step": 1,
          "action": "Navigate to registration page",
          "expected_result": "Registration form displayed"
        },
        {
          "step": 2,
          "action": "Enter valid email and password",
          "expected_result": "User account created successfully"
        }
      ]
    }
  ],
  "test_execution_plan": {
    "total_test_cases": 45,
    "execution_phases": [
      {
        "phase": "smoke",
        "test_cases": ["TC001", "TC002"],
        "estimated_duration": "15 minutes"
      }
    ]
  }
}
```

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/test_writer_db
MINIO_ENDPOINT=http://minio:9000
OLLAMA_HOST=http://ollama:11434
```

### Agent Customization
Each agent can be customized by modifying their prompts in:
- `app/services/document_agents.py`
- `app/services/test_case_agents.py`

## 📈 Benefits

### Quality Assurance
- **Comprehensive Coverage**: All requirements thoroughly tested
- **Edge Case Handling**: Boundary conditions and error scenarios included
- **Multi-Agent Review**: Quality validation through multiple AI perspectives
- **Consistent Documentation**: Standardized test case format

### Efficiency
- **Automated Generation**: No manual test case writing required
- **Fast Processing**: Parallel agent execution
- **Reusable Pipeline**: Apply to any document type
- **Scalable**: Handle multiple documents simultaneously

### Intelligence
- **Document Understanding**: AI comprehends context and domain
- **Smart Decomposition**: Logical requirement breakdown
- **Creative Edge Cases**: Comprehensive scenario generation
- **Quality Metrics**: Automated coverage and quality assessment

## 🚨 Error Handling

### Common Issues
1. **Pipeline Timeout**: Increase timeout for large documents
2. **AI Model Unavailable**: Ensure qwen3:8b is pulled in Ollama
3. **Document Upload Failed**: Check file format and size limits
4. **Database Connection**: Verify PostgreSQL is running

### Monitoring
```bash
# Check pipeline status
curl "http://localhost:8000/api/v1/test-writer/pipelines"

# View backend logs
docker compose logs backend -f

# Monitor Ollama
docker exec -it ollama ollama logs
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Support for additional document formats (Word, PowerPoint)
- [ ] Custom agent prompt templates
- [ ] Test case execution automation
- [ ] Integration with CI/CD pipelines
- [ ] Test case versioning and history
- [ ] Multi-language support

### Performance Optimizations
- [ ] Agent result caching
- [ ] Parallel document processing
- [ ] Streaming pipeline results
- [ ] Resource usage optimization

## 📞 Support

### Troubleshooting
1. Check backend logs for detailed error messages
2. Verify all services are running: `docker compose ps`
3. Ensure Ollama model is available: `docker exec -it ollama ollama list`
4. Test with simple documents first

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

---

This 7-agent pipeline represents the cutting edge of AI-powered test case generation, transforming any document into comprehensive, high-quality test cases through intelligent sequential processing.
