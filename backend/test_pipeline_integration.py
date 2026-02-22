#!/usr/bin/env python3
"""
Test script for the 7-agent test case writer pipeline
"""

import asyncio
import sys
import os
import requests
import json
from pathlib import Path

# Add to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def test_pipeline_workflow():
    """Test the complete 7-agent pipeline workflow"""
    
    print("🚀 Testing 7-Agent Test Case Writer Pipeline\n")
    
    # Test data - simulate a simple requirements document
    test_document_content = """
    E-Commerce Platform Requirements
    
    User Management:
    1. Users must be able to register with email and password
    2. Users must be able to login with valid credentials
    3. Users must be able to reset their password
    4. Users must be able to update their profile information
    
    Product Catalog:
    1. Users must be able to browse products by category
    2. Users must be able to search products by name
    3. Users must be able to view product details
    4. Users must be able to add products to cart
    
    Payment Processing:
    1. Users must be able to checkout with items in cart
    2. System must accept credit card payments
    3. System must validate payment information
    4. System must handle payment failures gracefully
    
    Non-Functional Requirements:
    1. System must respond within 2 seconds for normal operations
    2. System must handle 1000 concurrent users
    3. System must be available 99.9% of the time
    4. User data must be encrypted and secure
    """
    
    try:
        # Step 1: Test pipeline creation
        print("📝 Step 1: Creating test document...")
        
        # Create a test file
        test_file_path = "test_requirements.txt"
        with open(test_file_path, 'w') as f:
            f.write(test_document_content)
        
        # Upload the test file
        print("📤 Uploading test document...")
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            upload_response = requests.post(
                'http://localhost:8000/api/v1/files/upload',
                files=files,
                timeout=30
            )
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return False
        
        upload_data = upload_response.json()
        document_id = upload_data.get('id')
        print(f"✅ Document uploaded successfully! Document ID: {document_id}")
        
        # Step 2: Start the 7-agent pipeline
        print("\n🤖 Step 2: Starting 7-Agent Pipeline...")
        pipeline_response = requests.post(
            f'http://localhost:8000/api/v1/test-writer/pipeline/upload?document_id={document_id}',
            timeout=10
        )
        
        if pipeline_response.status_code != 200:
            print(f"❌ Pipeline start failed: {pipeline_response.status_code}")
            return False
        
        pipeline_data = pipeline_response.json()
        pipeline_id = pipeline_data.get('pipeline_id')
        print(f"✅ Pipeline started! Pipeline ID: {pipeline_id}")
        
        # Step 3: Monitor pipeline progress
        print("\n🔄 Step 3: Monitoring Pipeline Progress...")
        
        max_wait_time = 300  # 5 minutes
        wait_interval = 10
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            # Check pipeline status
            status_response = requests.get(
                f'http://localhost:8000/api/v1/test-writer/pipeline/{pipeline_id}/status',
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_agent = status_data.get('current_agent', 'unknown')
                status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                
                print(f"📊 Current Agent: {current_agent}")
                print(f"📈 Status: {status}")
                print(f"📉 Progress: {progress:.1f}%")
                
                if status == 'completed':
                    print("✅ Pipeline completed successfully!")
                    break
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Pipeline failed: {error}")
                    return False
                elif status == 'cancelled':
                    print("⏹️ Pipeline was cancelled")
                    return False
                
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
            
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        if elapsed_time >= max_wait_time:
            print("⏰ Pipeline timed out")
            return False
        
        # Step 4: Get pipeline results
        print("\n📚 Step 4: Getting Pipeline Results...")
        results_response = requests.get(
            f'http://localhost:8000/api/v1/test-writer/pipeline/{pipeline_id}/results',
            timeout=10
        )
        
        if results_response.status_code != 200:
            print(f"❌ Results retrieval failed: {results_response.status_code}")
            return False
        
        results_data = results_response.json()
        results = results_data.get('results', {})
        execution_summary = results_data.get('execution_summary', {})
        
        print(f"📊 Execution Summary:")
        print(f"   Total Agents: {execution_summary.get('total_agents', 0)}")
        print(f"   Completed Agents: {execution_summary.get('completed_agents', 0)}")
        print(f"   Total Test Cases: {execution_summary.get('total_test_cases', 0)}")
        
        # Display sample test cases
        final_test_cases = results.get('final_test_cases', [])
        if final_test_cases:
            print(f"\n📝 Sample Test Cases (showing first 3):")
            for i, test_case in enumerate(final_test_cases[:3]):
                print(f"\n   Test Case {i+1}:")
                print(f"   ID: {test_case.get('id', 'N/A')}")
                print(f"   Title: {test_case.get('title', 'N/A')}")
                print(f"   Priority: {test_case.get('priority', 'N/A')}")
                print(f"   Type: {test_case.get('test_type', 'N/A')}")
                test_steps = test_case.get('test_steps', [])
                if test_steps:
                    print(f"   Steps: {len(test_steps)} steps")
                    for j, step in enumerate(test_steps[:2]):  # Show first 2 steps
                        print(f"     Step {j+1}: {step.get('action', 'N/A')}")
        
        # Step 5: Download test cases
        print("\n💾 Step 5: Downloading Test Cases...")
        download_response = requests.get(
            f'http://localhost:8000/api/v1/test-writer/pipeline/{pipeline_id}/download',
            timeout=10
        )
        
        if download_response.status_code == 200:
            download_data = download_response.json()
            downloaded_test_cases = download_data.get('test_cases', [])
            
            # Save to file
            output_file = f"generated_test_cases_{pipeline_id}.json"
            with open(output_file, 'w') as f:
                json.dump(download_data, f, indent=2)
            
            print(f"✅ Test cases downloaded and saved to: {output_file}")
            print(f"📊 Total test cases in download: {len(downloaded_test_cases)}")
        
        # Step 6: Cleanup
        print("\n🧹 Step 6: Cleaning up...")
        
        # Clean up pipeline
        cleanup_response = requests.delete(
            f'http://localhost:8000/api/v1/test-writer/pipeline/{pipeline_id}',
            timeout=10
        )
        
        if cleanup_response.status_code == 200:
            print("✅ Pipeline cleaned up successfully")
        
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print("✅ Test file cleaned up")
        
        print("\n🎉 7-Agent Pipeline Test Completed Successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure the backend is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 The pipeline may take longer for complex documents")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


async def main():
    """Run the pipeline test"""
    print("🧪 7-Agent Test Case Writer Pipeline Test")
    print("=" * 60)
    
    success = await test_pipeline_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 Test Completed Successfully!")
        print("\n💡 Next Steps:")
        print("   1. Review generated test cases")
        print("   2. Test with different document types")
        print("   3. Integrate with CI/CD pipeline")
        print("   4. Customize agent prompts for your domain")
    else:
        print("❌ Test Failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check backend logs for errors")
        print("   2. Verify Ollama is running with qwen3:8b model")
        print("   3. Ensure all dependencies are installed")


if __name__ == "__main__":
    asyncio.run(main())
