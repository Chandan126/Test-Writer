from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class PipelineExecutionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineExecution(Base):
    """Pipeline execution tracking"""
    __tablename__ = "pipeline_executions"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    status = Column(Enum(PipelineExecutionStatus), default=PipelineExecutionStatus.PENDING)
    current_agent = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    agent_results = Column(JSON, nullable=True)
    progress_percentage = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("File", back_populates="pipeline_executions")
    test_cases = relationship("TestCase", back_populates="pipeline_execution", cascade="all, delete-orphan")


class TestCase(Base):
    """Generated test cases"""
    __tablename__ = "test_cases"
    
    id = Column(String, primary_key=True, index=True)
    pipeline_execution_id = Column(String, ForeignKey("pipeline_executions.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirement_ids = Column(JSON, nullable=True)  # List of requirement IDs
    priority = Column(String, nullable=False)  # critical, high, medium, low
    test_type = Column(String, nullable=False)  # functional, integration, performance, security
    preconditions = Column(JSON, nullable=True)  # List of preconditions
    test_steps = Column(JSON, nullable=False)  # List of test steps
    test_data = Column(JSON, nullable=True)  # Test input/output data
    acceptance_criteria = Column(JSON, nullable=True)  # List of acceptance criteria
    edge_case_covered = Column(String, nullable=True)
    execution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline_execution = relationship("PipelineExecution", back_populates="test_cases")


class DocumentAnalysis(Base):
    """Document analysis results"""
    __tablename__ = "document_analyses"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    document_type = Column(String, nullable=False)
    purpose = Column(Text, nullable=False)
    domain = Column(String, nullable=False)
    key_concepts = Column(JSON, nullable=True)
    terminology = Column(JSON, nullable=True)
    user_personas = Column(JSON, nullable=True)
    use_cases = Column(JSON, nullable=True)
    complexity = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("File")


class Requirement(Base):
    """Extracted requirements"""
    __tablename__ = "requirements"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    requirement_type = Column(String, nullable=False)  # functional, non_functional
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    acceptance_criteria = Column(JSON, nullable=True)
    priority = Column(String, nullable=False)  # high, medium, low
    user_story = Column(Text, nullable=True)
    criteria = Column(JSON, nullable=True)  # For non-functional requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("File")


class EdgeCase(Base):
    """Identified edge cases"""
    __tablename__ = "edge_cases"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    requirement_id = Column(String, nullable=True)
    edge_case_type = Column(String, nullable=False)  # boundary_value, error_condition, unusual_input, performance
    scenario = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=True)
    test_method = Column(Text, nullable=True)
    parameter = Column(String, nullable=True)
    min_value = Column(String, nullable=True)
    max_value = Column(String, nullable=True)
    test_points = Column(JSON, nullable=True)
    input_type = Column(String, nullable=True)
    unusual_value = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    metric = Column(String, nullable=True)
    target = Column(String, nullable=True)
    stress_condition = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("File")
