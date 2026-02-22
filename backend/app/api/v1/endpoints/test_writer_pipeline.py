from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.test_writer_pipeline import test_writer_pipeline_service
from app.crud.file import file as file_crud
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/pipeline/upload")
async def start_test_writer_pipeline(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start the 7-agent test case writer pipeline for a document
    """
    try:
        # Verify document exists
        db_file = file_crud.get(db, document_id)
        if not db_file:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        # Create pipeline
        pipeline_id = test_writer_pipeline_service.create_pipeline(document_id)
        
        # Start pipeline execution in background
        background_tasks.add_task(
            test_writer_pipeline_service.execute_pipeline,
            pipeline_id,
            db
        )
        
        logger.info(f"🚀 Started test writer pipeline {pipeline_id} for document {document_id}")
        
        return {
            "pipeline_id": pipeline_id,
            "document_id": document_id,
            "status": "started",
            "message": "Test case writer pipeline started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to start pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")


@router.get("/pipeline/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str):
    """
    Get current status of a test writer pipeline
    """
    try:
        status = test_writer_pipeline_service.get_pipeline_status(pipeline_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get pipeline status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")


@router.get("/pipeline/{pipeline_id}/results")
async def get_pipeline_results(pipeline_id: str):
    """
    Get final results of a completed test writer pipeline
    """
    try:
        results = test_writer_pipeline_service.get_pipeline_results(pipeline_id)
        if not results:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found or not completed")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get pipeline results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline results: {str(e)}")


@router.post("/pipeline/{pipeline_id}/cancel")
async def cancel_pipeline(pipeline_id: str):
    """
    Cancel a running test writer pipeline
    """
    try:
        success = test_writer_pipeline_service.cancel_pipeline(pipeline_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        return {
            "pipeline_id": pipeline_id,
            "status": "cancelled",
            "message": "Pipeline cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel pipeline: {str(e)}")


@router.delete("/pipeline/{pipeline_id}")
async def cleanup_pipeline(pipeline_id: str):
    """
    Clean up a completed pipeline resources
    """
    try:
        success = test_writer_pipeline_service.cleanup_pipeline(pipeline_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        return {
            "pipeline_id": pipeline_id,
            "status": "cleaned_up",
            "message": "Pipeline resources cleaned up successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cleanup pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup pipeline: {str(e)}")


@router.get("/pipelines")
async def list_active_pipelines():
    """
    List all active test writer pipelines
    """
    try:
        pipelines = test_writer_pipeline_service.list_active_pipelines()
        
        return {
            "pipelines": pipelines,
            "total_active": len(pipelines)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list pipelines: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list pipelines: {str(e)}")


@router.get("/agents")
async def get_agent_details():
    """
    Get details about all agents in the test writer pipeline
    """
    try:
        agents = test_writer_pipeline_service.get_agent_details()
        
        return {
            "agents": agents,
            "total_agents": len(agents),
            "pipeline_description": "7-agent pipeline for automated test case generation from documents"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get agent details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent details: {str(e)}")


@router.get("/pipeline/{pipeline_id}/download")
async def download_test_cases(pipeline_id: str):
    """
    Download test cases in a formatted format
    """
    try:
        results = test_writer_pipeline_service.get_pipeline_results(pipeline_id)
        if not results:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found or not completed")
        
        # Format test cases for download (could return as JSON, CSV, or other formats)
        test_cases = results.get("results", {}).get("final_test_cases", [])
        
        return {
            "pipeline_id": pipeline_id,
            "download_format": "json",
            "test_cases": test_cases,
            "metadata": {
                "total_test_cases": len(test_cases),
                "generated_at": "N/A",  # Could add timestamp
                "pipeline_version": "1.0"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to download test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download test cases: {str(e)}")


@router.post("/pipeline/quick-start")
async def quick_start_pipeline(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Quick start pipeline with automatic status polling
    """
    try:
        # Start pipeline
        pipeline_response = await start_test_writer_pipeline(
            document_id, background_tasks, db
        )
        
        pipeline_id = pipeline_response["pipeline_id"]
        
        return {
            "pipeline_id": pipeline_id,
            "document_id": document_id,
            "status_url": f"/api/v1/test-writer/pipeline/{pipeline_id}/status",
            "results_url": f"/api/v1/test-writer/pipeline/{pipeline_id}/results",
            "download_url": f"/api/v1/test-writer/pipeline/{pipeline_id}/download",
            "message": "Pipeline started. Use the URLs above to monitor progress and get results."
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to quick start pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to quick start pipeline: {str(e)}")
