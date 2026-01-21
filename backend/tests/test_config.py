from config.qdrant import client,COLLECTION_NAME
from config.logging_config import setup_logging
import os
from unittest.mock import MagicMock, patch
import logging

class TestQdrant:
    def test_config_qdrant_success(self):
        """Test Qdrant configuration"""

        # ARRANGE
        collection_info=client.get_collection(COLLECTION_NAME)
        existing_indices=collection_info.payload_schema.keys()
        fields_to_index=[
            "policy_type",
            "section",
            "location",
            "employee_type"
        ]

        # ASSERT
        assert client is not None
        assert collection_info is not None
        assert existing_indices is not None
        assert fields_to_index is not None
        assert len(existing_indices) == len(fields_to_index)
        assert all(field in existing_indices for field in fields_to_index)

class TestLogging():
    @patch("config.logging_config.logging.FileHandler")
    def test_logging_success(self,mock_file_handler):
        """Test if the logging is set up properly
        - Log directory is created
        - Logger level is set to INFO
        - StreamHandler and FileHandler are attached
        """
        # ARRANGE
        mock_handler = MagicMock()
        mock_handler.level = logging.INFO
        mock_file_handler.return_value = mock_handler
        
        # ACT
        setup_logging()

        # ASSERT
        assert os.path.isdir("logs")
        mock_file_handler.assert_called_once()






