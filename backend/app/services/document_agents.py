import json
import logging
from typing import Dict, Any, List
from app.core.pipeline_coordinator import BaseAgent, PipelineState

logger = logging.getLogger(__name__)


class DocumentUnderstandingAgent(BaseAgent):
    """Analyzes document structure, purpose, and key concepts"""
    
    def __init__(self):
        super().__init__("Document Understanding Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Analyze document and extract key information"""
        try:
            logger.info(f"🔍 {self.name}: Starting document analysis")
            
            if not state.extracted_content:
                state.set_error("No extracted content available for analysis")
                return state
            
            # Create analysis prompt
            prompt = f"""
            Analyze the following document and provide a comprehensive analysis:

            Document Content:
            {state.extracted_content[:8000]}

            Please provide analysis in the following JSON format:
            {{
                "document_type": "type of document (e.g., requirements, specification, user manual)",
                "purpose": "main purpose of this document",
                "domain": "business domain or industry",
                "key_concepts": ["concept1", "concept2", "concept3"],
                "terminology": {{"term": "definition", "term2": "definition2"}},
                "user_personas": ["persona1", "persona2"],
                "use_cases": ["use case 1", "use case 2"],
                "complexity": "low/medium/high",
                "scope": "narrow/medium/broad"
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    analysis = json.loads(result)
                    state.document_analysis = analysis
                    state.update_agent_result(self.name, analysis)
                    logger.info(f"✅ {self.name}: Document analysis completed")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.document_analysis = {
                        "document_type": "unknown",
                        "purpose": "extracted from document",
                        "domain": "general",
                        "key_concepts": [],
                        "terminology": {},
                        "user_personas": [],
                        "use_cases": [],
                        "complexity": "medium",
                        "scope": "medium"
                    }
                    state.update_agent_result(self.name, state.document_analysis)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using fallback")
            else:
                state.set_error("Failed to analyze document with AI")
                return state
            
            state.advance_to_agent("requirements_decomposition")
            return state
            
        except Exception as e:
            state.set_error(f"Document understanding failed: {str(e)}")
            return state


class RequirementsDecompositionAgent(BaseAgent):
    """Breaks down document into testable requirements"""
    
    def __init__(self):
        super().__init__("Requirements Decomposition Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Extract and decompose requirements from document analysis"""
        try:
            logger.info(f"📋 {self.name}: Starting requirements decomposition")
            
            if not state.document_analysis:
                state.set_error("No document analysis available")
                return state
            
            # Create requirements extraction prompt
            prompt = f"""
            Based on the following document analysis, extract and decompose requirements:

            Document Analysis:
            {json.dumps(state.document_analysis, indent=2)}

            Original Document Content:
            {state.extracted_content[:8000]}

            Please provide requirements in the following JSON format:
            {{
                "functional_requirements": [
                    {{
                        "id": "FR001",
                        "title": "requirement title",
                        "description": "detailed description",
                        "acceptance_criteria": ["criteria1", "criteria2"],
                        "priority": "high/medium/low",
                        "user_story": "as a user, I want to..."
                    }}
                ],
                "non_functional_requirements": [
                    {{
                        "id": "NFR001",
                        "type": "performance/security/usability/reliability",
                        "title": "requirement title",
                        "description": "detailed description",
                        "criteria": ["criteria1", "criteria2"],
                        "priority": "high/medium/low"
                    }}
                ],
                "test_scenarios": [
                    {{
                        "scenario": "test scenario description",
                        "requirements_covered": ["FR001", "NFR001"]
                    }}
                ]
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    requirements = json.loads(result)
                    state.requirements = requirements
                    state.update_agent_result(self.name, requirements)
                    logger.info(f"✅ {self.name}: Requirements decomposition completed")
                    logger.info(f"📊 {self.name}: Found {len(requirements.get('functional_requirements', []))} functional requirements")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.requirements = {
                        "functional_requirements": [],
                        "non_functional_requirements": [],
                        "test_scenarios": []
                    }
                    state.update_agent_result(self.name, state.requirements)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using fallback")
            else:
                state.set_error("Failed to decompose requirements with AI")
                return state
            
            state.advance_to_agent("edge_case_analysis")
            return state
            
        except Exception as e:
            state.set_error(f"Requirements decomposition failed: {str(e)}")
            return state


class EdgeCaseAgent(BaseAgent):
    """Identifies boundary conditions and exceptional scenarios"""
    
    def __init__(self):
        super().__init__("Edge Case Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Identify edge cases and boundary conditions"""
        try:
            logger.info(f"🔬 {self.name}: Starting edge case analysis")
            
            if not state.requirements:
                state.set_error("No requirements available for edge case analysis")
                return state
            
            # Create edge case analysis prompt
            prompt = f"""
            Based on the following requirements, identify comprehensive edge cases and boundary conditions:

            Requirements:
            {json.dumps(state.requirements, indent=2)}

            Please provide edge cases in the following JSON format:
            {{
                "boundary_values": [
                    {{
                        "requirement_id": "FR001",
                        "parameter": "parameter name",
                        "min_value": "minimum boundary",
                        "max_value": "maximum boundary",
                        "test_points": ["min-1", "min", "min+1", "max-1", "max", "max+1"]
                    }}
                ],
                "error_conditions": [
                    {{
                        "requirement_id": "FR001",
                        "scenario": "error scenario description",
                        "expected_behavior": "how system should handle error",
                        "test_method": "how to trigger this error"
                    }}
                ],
                "unusual_inputs": [
                    {{
                        "requirement_id": "FR001",
                        "input_type": "data type",
                        "unusual_value": "unusual input value",
                        "reason": "why this is unusual"
                    }}
                ],
                "performance_scenarios": [
                    {{
                        "requirement_id": "NFR001",
                        "scenario": "performance test scenario",
                        "metric": "response time/throughput/memory",
                        "target": "performance target",
                        "stress_condition": "how to stress test"
                    }}
                ]
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    edge_cases = json.loads(result)
                    state.edge_cases = edge_cases
                    state.update_agent_result(self.name, edge_cases)
                    logger.info(f"✅ {self.name}: Edge case analysis completed")
                    logger.info(f"🔬 {self.name}: Found {len(edge_cases.get('boundary_values', []))} boundary values")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.edge_cases = {
                        "boundary_values": [],
                        "error_conditions": [],
                        "unusual_inputs": [],
                        "performance_scenarios": []
                    }
                    state.update_agent_result(self.name, state.edge_cases)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using fallback")
            else:
                state.set_error("Failed to analyze edge cases with AI")
                return state
            
            state.advance_to_agent("test_case_writing")
            return state
            
        except Exception as e:
            state.set_error(f"Edge case analysis failed: {str(e)}")
            return state
