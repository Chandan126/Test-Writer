from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.crud.base import CRUDBase
from app.models.test_case import PipelineExecution, TestCase, DocumentAnalysis, Requirement, EdgeCase
from app.schemas.test_case import PipelineExecutionCreate, PipelineExecutionUpdate, TestCaseCreate, TestCaseUpdate
import uuid


class CRUDPipelineExecution(CRUDBase[PipelineExecution, PipelineExecutionCreate, PipelineExecutionUpdate]):
    """CRUD operations for pipeline executions"""
    
    def create_with_document(self, db: Session, *, obj_in: PipelineExecutionCreate, document_id: int) -> PipelineExecution:
        """Create pipeline execution with document reference"""
        obj_in_data = obj_in.dict()
        obj_in_data["document_id"] = document_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_document(self, db: Session, *, document_id: int) -> List[PipelineExecution]:
        """Get all pipeline executions for a document"""
        return db.query(self.model).filter(self.model.document_id == document_id).all()
    
    def get_active_pipelines(self, db: Session) -> List[PipelineExecution]:
        """Get all active (not completed/failed/cancelled) pipelines"""
        return db.query(self.model).filter(
            self.model.status.in_(["pending", "processing"])
        ).all()
    
    def update_status(self, db: Session, *, pipeline_id: str, status: str, error_message: Optional[str] = None) -> Optional[PipelineExecution]:
        """Update pipeline status"""
        db_obj = self.get(db, id=pipeline_id)
        if not db_obj:
            return None
        
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message
        if status == "completed":
            update_data["completed_at"] = func.now()
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def update_progress(self, db: Session, *, pipeline_id: str, current_agent: str, progress: int, agent_results: Dict[str, Any]) -> Optional[PipelineExecution]:
        """Update pipeline progress"""
        db_obj = self.get(db, id=pipeline_id)
        if not db_obj:
            return None
        
        update_data = {
            "current_agent": current_agent,
            "progress_percentage": progress,
            "agent_results": agent_results
        }
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)


class CRUDTestCase(CRUDBase[TestCase, TestCaseCreate, TestCaseUpdate]):
    """CRUD operations for test cases"""
    
    def create_with_pipeline(self, db: Session, *, obj_in: TestCaseCreate, pipeline_execution_id: str) -> TestCase:
        """Create test case with pipeline reference"""
        obj_in_data = obj_in.dict()
        obj_in_data["pipeline_execution_id"] = pipeline_execution_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_pipeline(self, db: Session, *, pipeline_execution_id: str) -> List[TestCase]:
        """Get all test cases for a pipeline execution"""
        return db.query(self.model).filter(self.model.pipeline_execution_id == pipeline_execution_id).all()
    
    def get_by_priority(self, db: Session, *, pipeline_execution_id: str, priority: str) -> List[TestCase]:
        """Get test cases by priority for a pipeline"""
        return db.query(self.model).filter(
            and_(
                self.model.pipeline_execution_id == pipeline_execution_id,
                self.model.priority == priority
            )
        ).all()
    
    def get_by_type(self, db: Session, *, pipeline_execution_id: str, test_type: str) -> List[TestCase]:
        """Get test cases by type for a pipeline"""
        return db.query(self.model).filter(
            and_(
                self.model.pipeline_execution_id == pipeline_execution_id,
                self.model.test_type == test_type
            )
        ).all()
    
    def get_by_requirement(self, db: Session, *, pipeline_execution_id: str, requirement_id: str) -> List[TestCase]:
        """Get test cases that cover a specific requirement"""
        return db.query(self.model).filter(
            and_(
                self.model.pipeline_execution_id == pipeline_execution_id,
                self.model.requirement_ids.contains([requirement_id])
            )
        ).all()


class CRUDDocumentAnalysis(CRUDBase[DocumentAnalysis, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations for document analysis"""
    
    def create_with_document(self, db: Session, *, analysis_data: Dict[str, Any], document_id: int) -> DocumentAnalysis:
        """Create document analysis with document reference"""
        db_obj = self.model(
            id=str(uuid.uuid4()),
            document_id=document_id,
            **analysis_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_document(self, db: Session, *, document_id: int) -> Optional[DocumentAnalysis]:
        """Get document analysis by document ID"""
        return db.query(self.model).filter(self.model.document_id == document_id).first()


class CRUDRequirement(CRUDBase[Requirement, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations for requirements"""
    
    def create_with_document(self, db: Session, *, requirement_data: Dict[str, Any], document_id: int) -> Requirement:
        """Create requirement with document reference"""
        db_obj = self.model(
            id=requirement_data.get("id", str(uuid.uuid4())),
            document_id=document_id,
            **requirement_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_document(self, db: Session, *, document_id: int) -> List[Requirement]:
        """Get all requirements for a document"""
        return db.query(self.model).filter(self.model.document_id == document_id).all()
    
    def get_by_type(self, db: Session, *, document_id: int, requirement_type: str) -> List[Requirement]:
        """Get requirements by type for a document"""
        return db.query(self.model).filter(
            and_(
                self.model.document_id == document_id,
                self.model.requirement_type == requirement_type
            )
        ).all()


class CRUDEdgeCase(CRUDBase[EdgeCase, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations for edge cases"""
    
    def create_with_document(self, db: Session, *, edge_case_data: Dict[str, Any], document_id: int) -> EdgeCase:
        """Create edge case with document reference"""
        db_obj = self.model(
            id=str(uuid.uuid4()),
            document_id=document_id,
            **edge_case_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_document(self, db: Session, *, document_id: int) -> List[EdgeCase]:
        """Get all edge cases for a document"""
        return db.query(self.model).filter(self.model.document_id == document_id).all()
    
    def get_by_type(self, db: Session, *, document_id: int, edge_case_type: str) -> List[EdgeCase]:
        """Get edge cases by type for a document"""
        return db.query(self.model).filter(
            and_(
                self.model.document_id == document_id,
                self.model.edge_case_type == edge_case_type
            )
        ).all()
    
    def get_by_requirement(self, db: Session, *, document_id: int, requirement_id: str) -> List[EdgeCase]:
        """Get edge cases for a specific requirement"""
        return db.query(self.model).filter(
            and_(
                self.model.document_id == document_id,
                self.model.requirement_id == requirement_id
            )
        ).all()


# Create CRUD instances
pipeline_execution_crud = CRUDPipelineExecution(PipelineExecution)
test_case_crud = CRUDTestCase(TestCase)
document_analysis_crud = CRUDDocumentAnalysis(DocumentAnalysis)
requirement_crud = CRUDRequirement(Requirement)
edge_case_crud = CRUDEdgeCase(EdgeCase)
