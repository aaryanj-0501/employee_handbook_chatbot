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
def sample_pdf_content():
    """Fixture providing sample PDF content for testing"""
    return b"%PDF-1.4\nfake pdf content for testing"

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
                    "section": "Policies"
                }
            },
            {
                "id": "2",
                "score": 0.8,
                "payload": {
                    "text": "Leave requests must be submitted at least 2 weeks in advance.",
                    "source": "employee_handbook",
                    "policy_type": "Leave",
                    "section": "Procedures"
                }
            }
        ]
    }