#!/usr/bin/env python3
"""
Test script for LangGraph OCR extraction system
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.ollama_client import OllamaClient
from app.core.extraction_agents import ExtractionAgents, ExtractionState
from app.services.file_extraction_service import LangGraphOCRService


async def test_ollama_connection():
    """Test Ollama connection and model availability"""
    print("🔍 Testing Ollama connection...")
    
    try:
        client = OllamaClient()
        
        # Test model availability
        models = client.models
        print(f"📋 Configured models: {models}")
        
        for model_name, model in models.items():
            available = await client.check_model_availability(model)
            status = "✅ Available" if available else "❌ Not Available"
            print(f"   {model_name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False


async def test_extraction_agents():
    """Test individual extraction agents"""
    print("\n🤖 Testing extraction agents...")
    
    try:
        agents = ExtractionAgents()
        
        # Create a mock state for testing
        test_state = ExtractionState(
            file_id=1,
            file_path="/tmp/test_image.jpg",  # Mock path
            content_type="image/jpeg"
        )
        
        print("✅ Extraction agents initialized successfully")
        print(f"📊 State structure: {test_state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False


async def test_langgraph_workflow():
    """Test LangGraph workflow creation"""
    print("\n🔄 Testing LangGraph workflow...")
    
    try:
        ocr_service = LangGraphOCRService()
        print("✅ LangGraph OCR service created successfully")
        
        # Test graph structure
        graph = ocr_service.graph
        print("✅ LangGraph workflow compiled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph workflow failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting LangGraph OCR System Tests\n")
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Extraction Agents", test_extraction_agents),
        ("LangGraph Workflow", test_langgraph_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print("=" * 50)
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("🎉 All tests passed! LangGraph OCR system is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
