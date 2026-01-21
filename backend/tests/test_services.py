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
from conftest import sample_query_result,sample_query_data
from services.generate_metadata import (
    infer_policy_type,
    infer_section,
    infer_location,
    infer_employee_type
)
from services.query_retriever import extract_metadata,build_filter,get_query_retriever
from services.final_result import extract_context, clean_output
from services.handbook_services import add_vectors, get_result
from fastapi import HTTPException
from qdrant_client.models import Filter


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

    @pytest.mark.asyncio
    @patch("services.handbook_services.extract_context")
    @patch("services.handbook_services.get_query_retriever")
    async def test_get_result_no_context(
        self,
        mock_get_query_retriever,
        mock_extract_context,
    ):
        # ARRANGE
        query = "What are working hours?"

        mock_get_query_retriever.return_value = {
            "results": [
                {"text": "Some irrelevant chunk"}
            ]
        }
        mock_extract_context.return_value = None  # <- triggers `if not context`

        # ACT
        result = await get_result(query)

        # ASSERT
        assert result == {
            "answer": "According to the employee handbook this information is not specified.",
            "sources": []
        }

        mock_get_query_retriever.assert_called_once_with(query, 5)
        mock_extract_context.assert_called_once()

    @pytest.mark.asyncio
    @patch("services.handbook_services.get_query_retriever")
    async def test_get_result_internal_exception(self,mock_get_query_retriever):
        # ARRANGE
        query = "What is leave policy?"

        mock_get_query_retriever.side_effect = Exception("DB failure")

        # ACT + ASSERT
        with pytest.raises(HTTPException) as exc_info:
            await get_result(query)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to process query"

        mock_get_query_retriever.assert_called_once_with(query, 5)


    @patch("services.handbook_services.client")
    @patch("services.handbook_services.uuid.uuid4")
    @patch("services.handbook_services.infer_employee_type")
    @patch("services.handbook_services.infer_location")
    @patch("services.handbook_services.infer_section")
    @patch("services.handbook_services.infer_policy_type")
    @patch("services.handbook_services.get_embedding")
    @patch("services.handbook_services.clean_text")
    def test_add_vectors_success(self,
        mock_clean_text,
        mock_get_embedding,
        mock_infer_policy,
        mock_infer_section,
        mock_infer_location,
        mock_infer_employee,
        mock_uuid,
        mock_client,
    ):
        # ARRANGE
        chunks = ["Leave policy text", "WFH policy text"]

        mock_clean_text.side_effect = lambda x: x
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        mock_infer_policy.return_value = "Leave"
        mock_infer_section.return_value = "Policies"
        mock_infer_location.return_value = "General"
        mock_infer_employee.return_value = "Full-Time"
        mock_uuid.return_value = "test-uuid"

        # ACT
        add_vectors(chunks)

        # ASSERT
        mock_client.upsert.assert_called_once()

        args, kwargs = mock_client.upsert.call_args
        points = kwargs["points"]

        assert len(points) == 2
        assert points[0]["id"] == "test-uuid"
        assert points[0]["vector"] == [0.1, 0.2, 0.3]
        assert points[0]["payload"]["text"] == "Leave policy text"
        assert points[0]["payload"]["policy_type"] == "Leave"

    @patch("services.handbook_services.client")
    def test_add_vectors_empty_chunks(self,mock_client):
        # ARRANGE
        chunks = []

        # ACT + ASSERT
        with pytest.raises(ValueError, match="No chunks to process"):
            add_vectors(chunks)

        mock_client.upsert.assert_not_called()

    @patch("services.handbook_services.client")
    def test_add_vectors_none_chunks(self,mock_client):
        with pytest.raises(ValueError):
            add_vectors(None)

        mock_client.upsert.assert_not_called()

class TestQueryRetriever:
    @patch("services.query_retriever.query_chain")
    def test_extract_metadata(self,mock_query_chain):
        """Test extract metadata success"""
        mock_query_chain.invoke.return_value={"policy_type":"Leave","section":"Policies","location":"General","employee_type":"General"}

        metadata=extract_metadata(sample_query_data)

        assert isinstance(metadata, dict)
        assert all(key in metadata 
                   for key in ["policy_type", "section", "location", "employee_type"])
        mock_query_chain.invoke.assert_called_once()

    def test_build_filter_success(self):
        # ARRANGE
        metadata = {
            "policy_type": "Leave",
            "section": "Policies",
            "location": "General",
            "employee_type": "General",
        }

        # ACT
        filter_obj = build_filter(metadata)

        # ASSERT
        assert isinstance(filter_obj, Filter)
        assert filter_obj.should is not None
        assert len(filter_obj.should) == len(metadata)

    def test_build_filter_none(self):
        # ACT
        result = build_filter(None)

        # ASSERT
        assert result is None

    @patch("services.query_retriever.get_embedding")
    @patch("services.query_retriever.client")
    @patch("services.query_retriever.extract_metadata")
    def test_get_query_retriever(
        self,
        mock_extract_metadata,
        mock_client,
        mock_get_embedding
    ):
        # ARRANGE
        query = "What is the leave policy?"
        fake_embedding = [0.1, 0.2, 0.3]

        mock_extract_metadata.return_value = {
            "policy_type": "Leave",
            "section": "Policies",
            "location": "General",
            "employee_type": "General"
        }

        mock_get_embedding.return_value = fake_embedding

        # fake Qdrant response
        mock_point = MagicMock()
        mock_point.id = "123"
        mock_point.score = 0.95
        mock_point.payload = {"text": "Leave policy content"}

        mock_search_result = MagicMock()
        mock_search_result.points = [mock_point]

        mock_client.query_points.return_value = mock_search_result

        # ACT
        result = get_query_retriever(query, limit=5)

        # ASSERT
        assert result["query"] == query
        assert len(result["results"]) == 1

        item = result["results"][0]
        assert item["id"] == "123"
        assert item["score"] == 0.95
        assert item["payload"]["text"] == "Leave policy content"

        mock_extract_metadata.assert_called_once_with(query)
        mock_get_embedding.assert_called_once_with(query)
        mock_client.query_points.assert_called_once()