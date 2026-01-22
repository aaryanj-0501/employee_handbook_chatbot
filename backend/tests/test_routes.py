"""
Test cases for API routes

This file tests the HTTP endpoints (routes) of our API.
It uses TestClient which acts like a fake web browser.

Key concepts:
- TestClient: Simulates HTTP requests to our API
- Mocking: Replaces real functions with fake ones during testing
- Status codes: 200 = success, 400 = bad request, 422 = validation error, 500 = server error
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app

# Create a test client - this simulates making HTTP requests to our API
client = TestClient(app)

"""Ensure dependency override is set
from conftest import client
from auth.dependencies import get_current_user
app.dependency_overrides[get_current_user] = client.override_get_current_user()
"""

class TestWelcomeEndpoint:
    """
    Test cases for the welcome endpoint (GET /)
    
    This is the simplest endpoint - it just returns a welcome message.
    No mocking needed because it doesn't call any complex services.
    """
    
    def test_welcome_endpoint_success(self):
        """
        Test that welcome endpoint returns correct message
        
        ARRANGE: No setup needed (simple endpoint)
        ACT: Make a GET request to the root path "/"
        ASSERT: Check that we get a 200 status and the correct message
        """
        # ACT: Make a GET request to the root endpoint
        response = client.get("/")
        
        # ASSERT: Check the response
        assert response.status_code == 200, "Should return success status (200)"
        assert "message" in response.json(), "Response should contain 'message' key"
        assert "Welcome to Employee Handbook Bot" in response.json()["message"], \
            "Message should contain welcome text"
        
    def test_welcome_endpoint_invalid_method(self):
        """
        Test the welcome endpoint fail for http method

        ARRANGE: No setup needed
        ACT: Make a POST request to the root path "/"
        ASSERT: Check that we get a 405 Method not allowed
        """

        # ACT
        response=client.post("/")

        # ASSERT
        assert response.status_code == 405
        assert response.json()["detail"] == "Method Not Allowed"

class TestHealthEndpoint:
    def test_health_endpoint_success(self):
        """
        Test that health endpoint returns correct message
        
        Arrange: No setup
        Act: Make a get request to the /health endpoint
        Assert: Check hether the api returns a correct status code and message
        """

        # ACT
        response=client.get("/health")

        # ASSERT
        assert response.status_code == 200
        assert response.json()["status"] == "OK"
        assert "Employee Handbook Bot" in response.json()["service"]

class TestUploadHandbookEndpoint:
    """Test cases for the upload handbook endpoint"""

    @patch("services.handbook_services.pdf_loader")
    @patch("services.handbook_services.chunk_text") 
    @patch("services.handbook_services.add_vectors")
    def test_upload_handbook_success(self,mock_load,mock_chunk,mock_add,client):
        """
        Test successful PDF upload
        
        ARRANGE: Create fake PDF content and mock the processing functions
        ACT: Upload the file via POST request
        ASSERT: Check that upload was accepted
        
        Why we mock: We don't want to actually process PDFs in tests
        (it's slow and requires real files). We just want to test that
        the endpoint accepts valid uploads.
        """
        # ARRANGE: Create minimal valid PDF content (just enough to pass validation)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 0\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        files = {"file": ("test_handbook.pdf", pdf_content, "application/pdf")}
           
        # Tell the mocks what to return (fake results)
        mock_load.load_pdf.return_value = "Sample text from PDF"
        mock_chunk.return_value = ["chunk1", "chunk2"]
        mock_add.return_value = None
        
        # ACT: Make the upload request
        response = client.post("/upload-handbook", files=files)
        
        # ASSERT: Check that upload was accepted
        assert response.status_code == 200, "Should return success status"
        assert "status" in response.json(), "Response should have status field"
        status_text = response.json()["status"].lower()
        assert "uploaded" in status_text or "processing" in status_text, \
            "Status should indicate upload/processing started"
    
    def test_upload_handbook_invalid_format(self,client):
        """Test upload with non-PDF file"""
        files = {"file": ("test.txt", b"text content", "text/plain")}
        response = client.post("/upload-handbook", files=files)
        
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]
    
    def test_upload_handbook_missing_file(self,client):
        """Test upload without file"""
        response = client.post("/upload-handbook")
        
        assert response.status_code == 422  # Validation error


class TestChatEndpoint:
    """Test cases for the chat endpoint"""
    
    @patch("routes.handbook_routes.get_result")
    def test_chat_endpoint_success(self,mock_get_result,client):
        """
        Test successful chat query
        
        ARRANGE: Prepare question data and mock the result function
        ACT: Send POST request with the question
        ASSERT: Check that we get a successful response with answer
        
        Why we mock get_result: We don't want to actually query the database
        or call the LLM in tests. We just test that the endpoint works correctly.
        """
        # ARRANGE: Prepare the question data
        query_data = {"question": "What is the leave policy?"}

        # Tell the mock what to return (fake answer)
        mock_get_result.return_value = ["Employees are entitled to 20 days of leave per year."]
        
        # ACT: Make the POST request to /chat endpoint
        response = client.post("/chat?limit=5", json=query_data)
        
        # ASSERT: Check the response
        assert response.status_code == 200, "Should return success status"
        assert isinstance(response.json(), list), "Response should be a list of answer lines"
    
    def test_chat_endpoint_empty_question(self,client):
        """Test chat with empty question"""
        query_data = {"question": ""}
        response = client.post("/chat", json=query_data)
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_chat_endpoint_missing_question(self,client):
        """Test chat without question field"""
        response = client.post("/chat", json={})
        
        assert response.status_code == 422  # Validation error