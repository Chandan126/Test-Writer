import json
import logging
from app.core.pipeline_coordinator import BaseAgent, PipelineState

logger = logging.getLogger(__name__)


class TestCaseWriterAgent(BaseAgent):
    """Generates detailed test cases from requirements and edge cases"""
    
    def __init__(self):
        super().__init__("Test Case Writer Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Generate comprehensive test cases"""
        try:
            logger.info(f"✍️ {self.name}: Starting test case generation")
            
            if not state.requirements or not state.edge_cases:
                state.set_error("Missing requirements or edge cases for test case generation")
                return state
            
            # Create test case generation prompt
            prompt = f"""
            Based on the following requirements and edge cases, generate comprehensive test cases:

            Requirements:
            {json.dumps(state.requirements, indent=2)}

            Edge Cases:
            {json.dumps(state.edge_cases, indent=2)}

            Document Analysis:
            {json.dumps(state.document_analysis, indent=2)}

            Please provide test cases in the following JSON format:
            {{
                "test_cases": [
                    {{
                        "id": "TC001",
                        "title": "test case title",
                        "description": "detailed description",
                        "requirement_ids": ["FR001", "NFR001"],
                        "priority": "critical/high/medium/low",
                        "test_type": "functional/integration/performance/security",
                        "preconditions": ["precondition1", "precondition2"],
                        "test_steps": [
                            {{
                                "step": 1,
                                "action": "action to perform",
                                "expected_result": "expected outcome"
                            }}
                        ],
                        "test_data": {{
                            "input_data": "test input data",
                            "expected_output": "expected output"
                        }},
                        "acceptance_criteria": ["criteria1", "criteria2"],
                        "edge_case_covered": "boundary value/error condition covered"
                    }}
                ],
                "test_data_requirements": [
                    {{
                        "data_type": "user credentials",
                        "specifications": "valid/invalid formats",
                        "examples": ["example1", "example2"]
                    }}
                ]
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    test_cases = json.loads(result)
                    state.draft_test_cases = test_cases
                    state.update_agent_result(self.name, test_cases)
                    logger.info(f"✅ {self.name}: Test case generation completed")
                    logger.info(f"📝 {self.name}: Generated {len(test_cases.get('test_cases', []))} test cases")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.draft_test_cases = {
                        "test_cases": [],
                        "test_data_requirements": []
                    }
                    state.update_agent_result(self.name, state.draft_test_cases)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using fallback")
            else:
                state.set_error("Failed to generate test cases with AI")
                return state
            
            state.advance_to_agent("test_case_review")
            return state
            
        except Exception as e:
            state.set_error(f"Test case generation failed: {str(e)}")
            return state


class TestReviewAgent(BaseAgent):
    """Validates and refines generated test cases"""
    
    def __init__(self):
        super().__init__("Test Review Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Review and improve test cases"""
        try:
            logger.info(f"🔍 {self.name}: Starting test case review")
            
            if not state.draft_test_cases:
                state.set_error("No draft test cases available for review")
                return state
            
            # Create test case review prompt
            prompt = f"""
            Review and improve the following test cases for quality, completeness, and clarity:

            Draft Test Cases:
            {json.dumps(state.draft_test_cases, indent=2)}

            Original Requirements:
            {json.dumps(state.requirements, indent=2)}

            Edge Cases:
            {json.dumps(state.edge_cases, indent=2)}

            Please review and provide improved test cases in the following JSON format:
            {{
                "review_summary": {{
                    "total_test_cases": number,
                    "critical_issues": ["issue1", "issue2"],
                    "improvements_made": ["improvement1", "improvement2"],
                    "coverage_score": "percentage of requirements covered"
                }},
                "improved_test_cases": [
                    {{
                        "id": "TC001",
                        "title": "improved test case title",
                        "description": "improved description",
                        "requirement_ids": ["FR001", "NFR001"],
                        "priority": "critical/high/medium/low",
                        "test_type": "functional/integration/performance/security",
                        "preconditions": ["precondition1", "precondition2"],
                        "test_steps": [
                            {{
                                "step": 1,
                                "action": "clear action description",
                                "expected_result": "clear expected outcome"
                            }}
                        ],
                        "test_data": {{
                            "input_data": "specific test input",
                            "expected_output": "specific expected output"
                        }},
                        "acceptance_criteria": ["clear criteria1", "clear criteria2"],
                        "edge_case_covered": "specific edge case covered",
                        "review_notes": "improvements made during review"
                    }}
                ],
                "missing_requirements": ["FR002", "NFR003"],
                "additional_recommendations": ["recommendation1", "recommendation2"]
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    reviewed_cases = json.loads(result)
                    state.reviewed_test_cases = reviewed_cases
                    state.update_agent_result(self.name, reviewed_cases)
                    logger.info(f"✅ {self.name}: Test case review completed")
                    logger.info(f"🔍 {self.name}: Reviewed {len(reviewed_cases.get('improved_test_cases', []))} test cases")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.reviewed_test_cases = state.draft_test_cases
                    state.update_agent_result(self.name, state.reviewed_test_cases)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using draft test cases")
            else:
                state.set_error("Failed to review test cases with AI")
                return state
            
            state.advance_to_agent("final_test_case_set")
            return state
            
        except Exception as e:
            state.set_error(f"Test case review failed: {str(e)}")
            return state


class FinalTestSetAgent(BaseAgent):
    """Organizes and formats final test case documentation"""
    
    def __init__(self):
        super().__init__("Final Test Case Set Agent")
    
    async def process(self, state: PipelineState) -> PipelineState:
        """Create final organized test case set"""
        try:
            logger.info(f"📚 {self.name}: Starting final test case set creation")
            
            if not state.reviewed_test_cases:
                state.set_error("No reviewed test cases available for finalization")
                return state
            
            # Create final test set prompt
            prompt = f"""
            Organize the following reviewed test cases into a final comprehensive test set:

            Reviewed Test Cases:
            {json.dumps(state.reviewed_test_cases, indent=2)}

            Document Analysis:
            {json.dumps(state.document_analysis, indent=2)}

            Please create a final test case set in the following JSON format:
            {{
                "test_execution_plan": {{
                    "total_test_cases": number,
                    "execution_phases": [
                        {{
                            "phase": "smoke/integration/regression",
                            "test_cases": ["TC001", "TC002"],
                            "estimated_duration": "time estimate",
                            "dependencies": ["dependency1", "dependency2"]
                        }}
                    ],
                    "resource_requirements": {{
                        "test_environment": "environment setup",
                        "test_data": "data requirements",
                        "tools": ["tool1", "tool2"]
                    }}
                }},
                "organized_test_cases": {{
                    "by_priority": {{
                        "critical": ["TC001", "TC002"],
                        "high": ["TC003", "TC004"],
                        "medium": ["TC005", "TC006"],
                        "low": ["TC007", "TC008"]
                    }},
                    "by_type": {{
                        "functional": ["TC001", "TC002"],
                        "integration": ["TC003", "TC004"],
                        "performance": ["TC005", "TC006"],
                        "security": ["TC007", "TC008"]
                    }},
                    "by_requirement": {{
                        "FR001": ["TC001", "TC002"],
                        "FR002": ["TC003", "TC004"],
                        "NFR001": ["TC005", "TC006"]
                    }}
                }},
                "test_documentation": {{
                    "executive_summary": "summary for stakeholders",
                    "test_strategy": "overall testing approach",
                    "coverage_report": {{
                        "requirements_coverage": "percentage",
                        "edge_case_coverage": "percentage",
                        "test_types_covered": ["type1", "type2"]
                    }},
                    "quality_metrics": {{
                        "test_case_quality": "high/medium/low",
                        "completeness_score": "percentage",
                        "maintainability": "high/medium/low"
                    }}
                }},
                "final_test_cases": [
                    {{
                        "id": "TC001",
                        "title": "final test case title",
                        "description": "final description",
                        "priority": "critical/high/medium/low",
                        "test_type": "functional/integration/performance/security",
                        "preconditions": ["precondition1", "precondition2"],
                        "test_steps": [
                            {{
                                "step": 1,
                                "action": "action description",
                                "expected_result": "expected result",
                                "actual_result": "to be filled during execution"
                            }}
                        ],
                        "test_data": {{
                            "input_data": "specific input",
                            "expected_output": "specific output"
                        }},
                        "acceptance_criteria": ["criteria1", "criteria2"],
                        "execution_notes": "notes for test executor"
                    }}
                ]
            }}
            """
            
            result = await self.call_ai_model(prompt)
            if result:
                try:
                    final_test_set = json.loads(result)
                    state.final_test_cases = final_test_set
                    state.update_agent_result(self.name, final_test_set)
                    logger.info(f"✅ {self.name}: Final test case set created")
                    logger.info(f"📚 {self.name}: Organized {len(final_test_set.get('final_test_cases', []))} final test cases")
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    state.final_test_cases = {
                        "test_execution_plan": {},
                        "organized_test_cases": {},
                        "test_documentation": {},
                        "final_test_cases": state.reviewed_test_cases.get("improved_test_cases", [])
                    }
                    state.update_agent_result(self.name, state.final_test_cases)
                    logger.warning(f"⚠️ {self.name}: JSON parsing failed, using fallback")
            else:
                state.set_error("Failed to create final test case set with AI")
                return state
            
            state.status = "completed"
            state.advance_to_agent("completed")
            logger.info(f"🎉 {self.name}: Pipeline completed successfully!")
            return state
            
        except Exception as e:
            state.set_error(f"Final test case set creation failed: {str(e)}")
            return state
