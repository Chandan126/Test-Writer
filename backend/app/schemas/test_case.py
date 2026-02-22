from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.test_case import PipelineExecutionStatus


class PipelineExecutionBase(BaseModel):
    """Base schema for pipeline execution"""
    document_id: int
    status: PipelineExecutionStatus = PipelineExecutionStatus.PENDING
    current_agent: Optional[str] = None
    error_message: Optional[str] = None
    agent_results: Optional[Dict[str, Any]] = None
    progress_percentage: int = 0


class PipelineExecutionCreate(PipelineExecutionBase):
    """Schema for creating pipeline execution"""
    pass


class PipelineExecutionUpdate(BaseModel):
    """Schema for updating pipeline execution"""
    status: Optional[PipelineExecutionStatus] = None
    current_agent: Optional[str] = None
    error_message: Optional[str] = None
    agent_results: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = None


class PipelineExecution(PipelineExecutionBase):
    """Schema for pipeline execution response"""
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TestCaseStep(BaseModel):
    """Schema for individual test step"""
    step: int
    action: str
    expected_result: str
    actual_result: Optional[str] = None


class TestData(BaseModel):
    """Schema for test data"""
    input_data: Optional[str] = None
    expected_output: Optional[str] = None


class TestCaseBase(BaseModel):
    """Base schema for test case"""
    title: str
    description: str
    requirement_ids: Optional[List[str]] = None
    priority: str = Field(..., regex="^(critical|high|medium|low)$")
    test_type: str = Field(..., regex="^(functional|integration|performance|security)$")
    preconditions: Optional[List[str]] = None
    test_steps: List[TestCaseStep]
    test_data: Optional[TestData] = None
    acceptance_criteria: Optional[List[str]] = None
    edge_case_covered: Optional[str] = None
    execution_notes: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    """Schema for creating test case"""
    pass


class TestCaseUpdate(BaseModel):
    """Schema for updating test case"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_ids: Optional[List[str]] = None
    priority: Optional[str] = None
    test_type: Optional[str] = None
    preconditions: Optional[List[str]] = None
    test_steps: Optional[List[TestCaseStep]] = None
    test_data: Optional[TestData] = None
    acceptance_criteria: Optional[List[str]] = None
    edge_case_covered: Optional[str] = None
    execution_notes: Optional[str] = None


class TestCase(TestCaseBase):
    """Schema for test case response"""
    id: str
    pipeline_execution_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentAnalysisBase(BaseModel):
    """Base schema for document analysis"""
    document_type: str
    purpose: str
    domain: str
    key_concepts: Optional[List[str]] = None
    terminology: Optional[Dict[str, str]] = None
    user_personas: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    complexity: str = Field(..., regex="^(low|medium|high)$")
    scope: str = Field(..., regex="^(narrow|medium|broad)$")


class DocumentAnalysis(DocumentAnalysisBase):
    """Schema for document analysis response"""
    id: str
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RequirementBase(BaseModel):
    """Base schema for requirement"""
    requirement_type: str = Field(..., regex="^(functional|non_functional)$")
    title: str
    description: str
    acceptance_criteria: Optional[List[str]] = None
    priority: str = Field(..., regex="^(high|medium|low)$")
    user_story: Optional[str] = None
    criteria: Optional[List[str]] = None


class RequirementCreate(RequirementBase):
    """Schema for creating requirement"""
    id: Optional[str] = None


class Requirement(RequirementBase):
    """Schema for requirement response"""
    id: str
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EdgeCaseBase(BaseModel):
    """Base schema for edge case"""
    requirement_id: Optional[str] = None
    edge_case_type: str = Field(..., regex="^(boundary_value|error_condition|unusual_input|performance)$")
    scenario: str
    expected_behavior: Optional[str] = None
    test_method: Optional[str] = None
    parameter: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    test_points: Optional[List[str]] = None
    input_type: Optional[str] = None
    unusual_value: Optional[str] = None
    reason: Optional[str] = None
    metric: Optional[str] = None
    target: Optional[str] = None
    stress_condition: Optional[str] = None


class EdgeCaseCreate(EdgeCaseBase):
    """Schema for creating edge case"""
    id: Optional[str] = None


class EdgeCase(EdgeCaseBase):
    """Schema for edge case response"""
    id: str
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PipelineStatusResponse(BaseModel):
    """Schema for pipeline status response"""
    pipeline_id: str
    document_id: int
    current_agent: str
    status: str
    error: Optional[str] = None
    agent_results: List[str]
    progress: float


class PipelineResultsResponse(BaseModel):
    """Schema for pipeline results response"""
    pipeline_id: str
    document_id: int
    status: str
    results: Dict[str, Any]
    execution_summary: Dict[str, Any]


class TestCasesByPriority(BaseModel):
    """Schema for test cases organized by priority"""
    critical: List[str]
    high: List[str]
    medium: List[str]
    low: List[str]


class TestCasesByType(BaseModel):
    """Schema for test cases organized by type"""
    functional: List[str]
    integration: List[str]
    performance: List[str]
    security: List[str]


class TestCasesByRequirement(BaseModel):
    """Schema for test cases organized by requirement"""
    requirement_id: List[str]


class OrganizedTestCases(BaseModel):
    """Schema for organized test cases"""
    by_priority: TestCasesByPriority
    by_type: TestCasesByType
    by_requirement: Dict[str, List[str]]


class QualityMetrics(BaseModel):
    """Schema for quality metrics"""
    test_case_quality: str
    completeness_score: float
    maintainability: str


class CoverageReport(BaseModel):
    """Schema for coverage report"""
    requirements_coverage: float
    edge_case_coverage: float
    test_types_covered: List[str]


class TestDocumentation(BaseModel):
    """Schema for test documentation"""
    executive_summary: str
    test_strategy: str
    coverage_report: CoverageReport
    quality_metrics: QualityMetrics


class TestExecutionPlan(BaseModel):
    """Schema for test execution plan"""
    total_test_cases: int
    execution_phases: List[Dict[str, Any]]
    resource_requirements: Dict[str, Any]


class FinalTestSet(BaseModel):
    """Schema for final test case set"""
    test_execution_plan: TestExecutionPlan
    organized_test_cases: OrganizedTestCases
    test_documentation: TestDocumentation
    final_test_cases: List[TestCase]


class AgentDetails(BaseModel):
    """Schema for agent details"""
    agent_name: str
    description: str


class AgentsResponse(BaseModel):
    """Schema for agents response"""
    agents: Dict[str, str]
    total_agents: int
    pipeline_description: str


class PipelinesListResponse(BaseModel):
    """Schema for pipelines list response"""
    pipelines: Dict[str, PipelineStatusResponse]
    total_active: int
