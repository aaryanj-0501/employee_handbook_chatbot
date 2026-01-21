import logging
from unittest.mock import patch, MagicMock
from starlette.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from main import app


class TestAppLifespan:

    @patch("main.setup_logging")
    @patch("main.logging.getLogger")
    def test_app_lifespan_startup_and_shutdown(
        self,
        mock_get_logger,
        mock_setup_logging
    ):
        # ARRANGE
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # ACT
        with TestClient(app) as client:
            response = client.get("/docs")  # triggers startup

        # ASSERT — startup
        mock_setup_logging.assert_called_once()
        mock_logger.info.assert_any_call("Starting Employee Handbook Chatbot")

        # ASSERT — shutdown
        mock_logger.info.assert_any_call("Shutting down Employee Handbook Chatbot")

def test_router_is_registered():
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200

def test_cors_middleware_configured():
    middleware_classes = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_classes

