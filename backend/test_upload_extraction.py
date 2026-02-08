#!/usr/bin/env python3
"""
Test script to verify automatic OCR extraction on file upload
"""

import asyncio
import sys
import os
import requests
from pathlib import Path

# Add to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def test_upload_and_extraction():
    """Test file upload with automatic OCR extraction"""
    
    print("🚀 Testing Upload + Automatic OCR Extraction\n")
    
    # Test file path (create a simple test file)
    test_file_path = "test_document.txt"
    test_content = "This is a test document for OCR extraction testing."
    
    # Create test file
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    try:
        # Upload file to backend
        print("📤 Uploading test file...")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            response = requests.post(
                'http://localhost:8000/api/v1/files/upload',
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            file_data = response.json()
            file_id = file_data.get('id')
            
            print(f"✅ File uploaded successfully! File ID: {file_id}")
            print(f"📊 File metadata: {file_data}")
            
            # Wait a moment for background extraction to start
            await asyncio.sleep(2)
            
            # Check extraction status
            print("🔍 Checking extraction status...")
            
            # Try to get extracted content
            extract_response = requests.post(
                f'http://localhost:8000/api/v1/files/{file_id}/extract',
                timeout=60  # Longer timeout for OCR processing
            )
            
            if extract_response.status_code == 200:
                extract_data = extract_response.json()
                status = extract_data.get('status', 'unknown')
                content = extract_data.get('content', '')
                
                print(f"📝 Extraction Status: {status}")
                
                if status == 'completed' and content:
                    print(f"✅ Extraction successful!")
                    print(f"📄 Extracted Content Preview:")
                    print("-" * 50)
                    print(content[:200] + "..." if len(content) > 200 else content)
                    print("-" * 50)
                    
                    # Check if content was saved to database
                    content_response = requests.get(
                        f'http://localhost:8000/api/v1/files/{file_id}/content',
                        timeout=10
                    )
                    
                    if content_response.status_code == 200:
                        saved_content = content_response.json().get('content', '')
                        if saved_content:
                            print(f"✅ Content saved to database successfully!")
                        else:
                            print(f"⚠️  Content not found in database")
                    else:
                        print(f"❌ Failed to retrieve saved content: {content_response.status_code}")
                        
                elif status == 'processing':
                    print("⏳ Extraction is still processing...")
                    print("💡 This is normal for large files or first-time OCR")
                    
                elif status == 'failed':
                    print("❌ Extraction failed!")
                    print("🔧 Check backend logs for detailed error information")
                    
                else:
                    print(f"❓ Unknown status: {status}")
                    
            else:
                print(f"❌ Extraction request failed: {extract_response.status_code}")
                print(f"📄 Response: {extract_response.text}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure the backend is running on http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 The OCR extraction may take longer for large files")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print("🧹 Cleaned up test file")


async def main():
    """Run the upload and extraction test"""
    print("🧪 Upload + OCR Extraction Test")
    print("=" * 50)
    
    await test_upload_and_extraction()
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Check backend logs for detailed OCR processing")
    print("   2. Verify Ollama models are available: ollama list")
    print("   3. Test with different file types (images, PDFs)")
    print("   4. Monitor processing status in database")


if __name__ == "__main__":
    asyncio.run(main())
