"""
Test cases for service functions

This file tests the business logic functions (services).
These are the functions that do the actual work:
- Generating metadata (policy type, section, etc.)
- Processing query results
- Cleaning output text

"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.generate_metadata import (
    infer_policy_type,
    infer_section,
    infer_location,
    infer_employee_type
)
from services.final_result import extract_context, clean_output
from services.handbook_services import get_result
from fastapi import HTTPException


class TestGenerateMetadata:
    """Test cases for metadata generation functions"""
    
    def test_infer_policy_type_leave(self):
        """
        Test policy type inference for leave
        
        ARRANGE: Text containing leave-related keywords
        ACT: Call infer_policy_type function
        ASSERT: Should return "Leave"
        
        This is a simple unit test - no mocking needed because
        the function doesn't depend on external services.
        """
        # ARRANGE: Text that should be classified as "Leave"
        text = "Employees can take paid time off for vacation"
        
        # ACT: Call the function
        result = infer_policy_type(text)
        
        # ASSERT: Should correctly identify as "Leave"
        assert result == "Leave", f"Expected 'Leave' but got '{result}'"
    
    def test_infer_policy_type_benefits(self):
        """Test policy type inference for benefits"""
        text = "Health insurance benefits are provided to all employees"
        result = infer_policy_type(text)
        assert result == "Benefits"
    
    def test_infer_policy_type_general(self):
        """Test policy type inference returns General for unmatched text"""
        text = "This is some random text without keywords"
        result = infer_policy_type(text)
        assert result == "General"
    
    def test_infer_section_policies(self):
        """Test section inference for policies"""
        text = "Company policies and regulations must be followed"
        result = infer_section(text)
        assert result == "Policies"
    
    def test_infer_location_remote(self):
        """Test location inference for remote"""
        text = "Work from home is available for remote employees"
        result = infer_location(text)
        assert result == "Remote"
    
    def test_infer_employee_type_fulltime(self):
        """Test employee type inference for full-time"""
        text = "Full-time employees receive benefits"
        result = infer_employee_type(text)
        assert result == "Full-Time"
    


class TestFinalResult:
    """Test cases for final result processing functions"""
    
    def test_extract_context_success(self):
        """Test successful context extraction"""
        query_result = {
            "results": [
                {
                    "id": "1",
                    "score": 0.9,
                    "payload": {"text": "This is context text 1"}
                },
                {
                    "id": "2",
                    "score": 0.8,
                    "payload": {"text": "This is context text 2"}
                }
            ]
        }
        
        context = extract_context(query_result)
        assert len(context) == 2
        assert "context text 1" in context[0]
        assert "context text 2" in context[1]
    
    def test_extract_context_invalid_structure(self):
        """Test context extraction with invalid structure"""
        query_result = {}
        
        with pytest.raises(HTTPException):
            extract_context(query_result)
    
    def test_clean_output_success(self):
        """Test successful output cleaning"""
        text = "Of course, here is the answer.\nThis is the actual content.\nSure, here is more."
        cleaned = clean_output(text)
        
        assert len(cleaned) > 0
        assert "Of course" not in cleaned[0] if cleaned else True
        assert "actual content" in " ".join(cleaned)
    
    def test_clean_output_empty(self):
        """Test clean_output with empty text"""
        result = clean_output("")
        assert result == []


class TestHandbookServices:
    """Test cases for handbook services"""
    
    @pytest.mark.asyncio
    @patch("services.handbook_services.get_query_retriever")
    @patch("services.handbook_services.extract_context")
    @patch("services.handbook_services.answer_chain")
    @patch("services.handbook_services.clean_output")
    async def test_get_result_success(self, mock_clean, mock_chain, mock_extract, mock_retriever):
        """Test successful get_result"""
        # Setup mocks
        mock_retriever.return_value = {
            "results": [
                {"id": "1", "payload": {"text": "Context"}}
            ]
        }
        mock_extract.return_value = ["Context text"]
        mock_chain.invoke.return_value = "This is the answer"
        mock_clean.return_value = ["Cleaned answer"]
        
        result = await get_result("What is the policy?", limit=5)
        
        assert isinstance(result, list)
        assert len(result) > 0
        mock_retriever.assert_called_once()
        mock_extract.assert_called_once()
        mock_chain.invoke.assert_called_once()
        mock_clean.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_result_empty_query(self):
        """Test get_result with empty query"""
        # get_result catches ValueError and raises HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_result("", limit=5)
        assert exc_info.value.status_code == 500
        assert "empty" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    @patch("services.handbook_services.get_query_retriever")
    async def test_get_result_no_results(self, mock_retriever):
        """Test get_result when no results found"""
        mock_retriever.return_value = {"results": []}
        
        result = await get_result("What is the policy?", limit=5)
        
        assert isinstance(result, dict)
        assert "answer" in result
        assert "sources" in result