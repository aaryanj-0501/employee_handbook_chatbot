"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ.setdefault("TESTING", "true")

@pytest.fixture
def sample_pdf_path():
    """Fixture providing sample PDF content for testing"""
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    pdf_path = test_data_dir / "test.pdf"
    
    # Create a minimal valid PDF content
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 0\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
    
    with open(pdf_path, "wb") as file:
        file.write(test_pdf_content)
    
    return pdf_path

@pytest.fixture
def sample_query_data():
    """Fixture providing sample query data"""
    return {"question": "What is the leave policy?"}

@pytest.fixture
def sample_query_result():
    """Fixture providing sample query result structure"""
    return {
        "query": "What is the leave policy?",
        "results": [
            {
                "id": "1",
                "score": 0.9,
                "payload": {
                    "text": "Employees are entitled to 20 days of paid leave per year.",
                    "source": "employee_handbook",
                    "policy_type": "Leave",
                    "section": "Policies",
                    "location":"General",
                    "employee_type":"General"
                }
            },
            {
                "id": "2",
                "score": 0.8,
                "payload": {
                    "text": "Leave requests must be submitted at least 2 weeks in advance.",
                    "source": "employee_handbook",
                    "policy_type": "Leave",
                    "section": "Procedures",
                    "location":"General",
                    "employee_type":"General"
                }
            }
        ]
    }