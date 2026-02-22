import logging
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.pipeline_coordinator import PipelineState, PipelineStatus
from app.services.file_extraction_service import content_extraction_service
from app.services.document_agents import DocumentUnderstandingAgent, RequirementsDecompositionAgent, EdgeCaseAgent
from app.services.test_case_agents import TestCaseWriterAgent, TestReviewAgent, FinalTestSetAgent

logger = logging.getLogger(__name__)


class TestWriterPipelineService:
    """Main service for orchestrating the 7-agent test case writer pipeline"""
    
    def __init__(self):
        self.active_pipelines: Dict[str, PipelineState] = {}
        self.pipeline_results: Dict[str, Any] = {}
        
        # Initialize all agents
        self.document_understanding_agent = DocumentUnderstandingAgent()
        self.requirements_decomposition_agent = RequirementsDecompositionAgent()
        self.edge_case_agent = EdgeCaseAgent()
        self.test_case_writer_agent = TestCaseWriterAgent()
        self.test_review_agent = TestReviewAgent()
        self.final_test_set_agent = FinalTestSetAgent()
    
    def create_pipeline(self, document_id: int) -> str:
        """Create a new pipeline instance"""
        pipeline_id = str(uuid.uuid4())
        pipeline_state = PipelineState(document_id)
        self.active_pipelines[pipeline_id] = pipeline_state
        
        logger.info(f"🚀 Created pipeline {pipeline_id} for document {document_id}")
        return pipeline_id
    
    async def execute_pipeline(self, pipeline_id: str, db: Session) -> bool:
        """Execute the complete 7-agent pipeline"""
        try:
            pipeline_state = self.active_pipelines.get(pipeline_id)
            if not pipeline_state:
                logger.error(f"❌ Pipeline {pipeline_id} not found")
                return False
            
            logger.info(f"🔄 Starting pipeline execution: {pipeline_id}")
            pipeline_state.status = PipelineStatus.PROCESSING
            
            # Step 1: Text Extraction (using existing service)
            logger.info("📄 Step 1: Text Extraction")
            extracted_content = await content_extraction_service.extract_content_from_file(db, pipeline_state.document_id)
            if extracted_content:
                pipeline_state.extracted_content = extracted_content
                pipeline_state.update_agent_result("text_extraction", extracted_content)
                logger.info("✅ Text extraction completed")
            else:
                pipeline_state.set_error("Text extraction failed")
                return False
            
            # Step 2: Document Understanding
            logger.info("🧠 Step 2: Document Understanding")
            pipeline_state = await self.document_understanding_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Step 3: Requirements Decomposition
            logger.info("📋 Step 3: Requirements Decomposition")
            pipeline_state = await self.requirements_decomposition_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Step 4: Edge Case Analysis
            logger.info("🔬 Step 4: Edge Case Analysis")
            pipeline_state = await self.edge_case_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Step 5: Test Case Writing
            logger.info("✍️ Step 5: Test Case Writing")
            pipeline_state = await self.test_case_writer_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Step 6: Test Case Review
            logger.info("🔍 Step 6: Test Case Review")
            pipeline_state = await self.test_review_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Step 7: Final Test Case Set
            logger.info("📚 Step 7: Final Test Case Set")
            pipeline_state = await self.final_test_set_agent.process(pipeline_state)
            if pipeline_state.has_error():
                return False
            
            # Store final results
            self.pipeline_results[pipeline_id] = pipeline_state.final_test_cases
            logger.info(f"🎉 Pipeline {pipeline_id} completed successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Pipeline {pipeline_id} execution failed: {str(e)}")
            if pipeline_id in self.active_pipelines:
                self.active_pipelines[pipeline_id].set_error(f"Pipeline execution failed: {str(e)}")
            return False
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a pipeline"""
        pipeline_state = self.active_pipelines.get(pipeline_id)
        if not pipeline_state:
            return None
        
        return {
            "pipeline_id": pipeline_id,
            "document_id": pipeline_state.document_id,
            "current_agent": pipeline_state.current_agent,
            "status": pipeline_state.status,
            "error": pipeline_state.error,
            "agent_results": list(pipeline_state.agent_results.keys()),
            "progress": self._calculate_progress(pipeline_state)
        }
    
    def get_pipeline_results(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get final results of a completed pipeline"""
        if pipeline_id not in self.pipeline_results:
            return None
        
        pipeline_state = self.active_pipelines.get(pipeline_id)
        if not pipeline_state or not pipeline_state.is_complete():
            return None
        
        return {
            "pipeline_id": pipeline_id,
            "document_id": pipeline_state.document_id,
            "status": pipeline_state.status,
            "results": pipeline_state.final_test_cases,
            "execution_summary": {
                "total_agents": 7,
                "completed_agents": len(pipeline_state.agent_results),
                "total_test_cases": len(pipeline_state.final_test_cases.get("final_test_cases", [])),
                "execution_time": "N/A"  # Could add timing if needed
            }
        }
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline"""
        if pipeline_id in self.active_pipelines:
            pipeline_state = self.active_pipelines[pipeline_id]
            pipeline_state.status = PipelineStatus.CANCELLED
            logger.info(f"⏹️ Pipeline {pipeline_id} cancelled")
            return True
        return False
    
    def cleanup_pipeline(self, pipeline_id: str) -> bool:
        """Clean up completed pipeline resources"""
        if pipeline_id in self.active_pipelines:
            del self.active_pipelines[pipeline_id]
        if pipeline_id in self.pipeline_results:
            del self.pipeline_results[pipeline_id]
        logger.info(f"🧹 Cleaned up pipeline {pipeline_id}")
        return True
    
    def list_active_pipelines(self) -> Dict[str, Dict[str, Any]]:
        """List all active pipelines"""
        return {
            pipeline_id: self.get_pipeline_status(pipeline_id)
            for pipeline_id in self.active_pipelines.keys()
        }
    
    def _calculate_progress(self, pipeline_state: PipelineState) -> float:
        """Calculate pipeline progress percentage"""
        agent_order = [
            "text_extraction",
            "document_understanding", 
            "requirements_decomposition",
            "edge_case_analysis",
            "test_case_writing",
            "test_case_review",
            "final_test_case_set"
        ]
        
        completed_agents = len(pipeline_state.agent_results)
        total_agents = len(agent_order)
        
        if pipeline_state.status == PipelineStatus.COMPLETED:
            return 100.0
        elif pipeline_state.status == PipelineStatus.FAILED:
            return (completed_agents / total_agents) * 100
        else:
            return (completed_agents / total_agents) * 100
    
    def get_agent_details(self) -> Dict[str, str]:
        """Get details about all agents in the pipeline"""
        return {
            "text_extraction": "Extracts content from uploaded documents",
            "document_understanding": "Analyzes document structure and purpose",
            "requirements_decomposition": "Breaks down requirements into testable units",
            "edge_case_analysis": "Identifies boundary conditions and error scenarios",
            "test_case_writing": "Generates detailed test procedures",
            "test_case_review": "Validates and improves test cases",
            "final_test_case_set": "Organizes final test documentation"
        }


# Create singleton instance
test_writer_pipeline_service = TestWriterPipelineService()
