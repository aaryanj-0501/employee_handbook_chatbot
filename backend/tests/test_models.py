"""
Test cases for Pydantic models

This is the simplest test file - perfect for beginners!
It tests data models (the structure of our data).
"""
import pytest
from models.handbook_model import HandbookQuery
from pydantic import ValidationError


class TestHandbookQuery:
    """
    Test cases for HandbookQuery model
    
    This model represents a question asked to the handbook bot.
    It has one field: 'question' (a string).
    """
    
    def test_valid_query(self):
        """
        Test creating a valid query
        
        ARRANGE: Prepare a valid question string
        ACT: Create a HandbookQuery object with the question
        ASSERT: Check that the question was stored correctly
        """
        # ARRANGE: A valid question
        question_text = "What is the leave policy?"
        
        # ACT: Create the model object
        query = HandbookQuery(question=question_text)
        
        # ASSERT: The question should be stored correctly
        assert query.question == question_text
    
    def test_query_missing_field(self):
        with pytest.raises(ValidationError):
            # This will fail because 'question' is required
            HandbookQuery()
    
    def test_query_none_value(self):
        """
        Test query with None value
        
        This should fail because 'question' cannot be None.
        """
        with pytest.raises(ValidationError):
            HandbookQuery(question=None)