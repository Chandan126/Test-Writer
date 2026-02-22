from app.models.file import File
from app.models.file_content import FileContent
from app.models.test_case import PipelineExecution, TestCase, DocumentAnalysis, Requirement, EdgeCase
from sqlalchemy.orm import relationship

# Add relationship to File model for pipeline executions
File.pipeline_executions = relationship("PipelineExecution", back_populates="document")