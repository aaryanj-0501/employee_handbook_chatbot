import time
from utils.rate_limiter import get_rate_limiter
from utils.pdf_loader import load_pdf
from utils.chunker import chunk_text,clean_text
from utils.embeddings import get_embedding
from utils.llm_setup import set_llm
import pytest
from fastapi import status,FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from middleware.rate_limit_middleware import RateLimitMiddleware

class TestPdfLoader:
    def test_pdf_loader_success(self,sample_pdf_path):
        """Test PDF loader"""

        # ARRANGE
        # ACT
        text=load_pdf(str(sample_pdf_path))
        print(text)

        # ASSERT
        assert text is not None
        assert isinstance(text,str)

    def test_pdf_loader_failure(self):
        """Test PDF loader failure"""

        # ARRANGE
        invalid_content="invalid.txt"
        # ACT
        text=load_pdf(str(invalid_content))

        # ASSERT
        assert text == ""

class TestChunker:
    def test_chunk_text_success(self,sample_pdf_path):
        """Test chunk text success"""

        # ARRANGE
        text=sample_pdf_path.read_text()

        # ACT
        chunks=chunk_text(text)

        # ASSERT
        assert chunks is not None
        assert len(chunks)>0

    def test_chunk_text_failure(self):
        "Test chunk test failure"

        # ARRANGE
        text=None

        # ACT
        chunks=chunk_text(text)

        # ASSERT
        assert chunks is None

    def test_clean_text_success(self):
        """Test clean text success"""

        # ARRANGE
        text = "a\tb\nc\r\n  d"
        # ACT
        cleaned=clean_text(text)

        # ASSERT
        assert cleaned is not None
        assert len(cleaned)>0

    def test_clean_text_failure(self):
        """Test clean text failure"""

        # ARRANGE
        text = None
        # ACT
        cleaned=clean_text(text)

        # ASSERT
        assert cleaned is None

class TestEmbeddings:
    @patch("utils.embeddings.embedding_model")
    def test_get_embedding_success(self,mock_emb,sample_query_data):
        # ARRANGE
        query = sample_query_data["question"]
        fake_vec=[0.1,0.2,0.3]
        
        mock_emb.embed_query.return_value=fake_vec

        # ACT 
        embedding = get_embedding(query)

        # ASSERT
        assert embedding == fake_vec
        mock_emb.embed_query.assert_called_once_with(query)
    
    @patch("utils.embeddings.embedding_model")
    def test_get_embedding_failure(self,mock_emb):
        """If the query is none an error should be raised"""
        mock_emb.embed_query.side_effect=TypeError("Text must be str")
        with pytest.raises(TypeError):
            get_embedding(None)

class TestLLMSetup:
    def test_llm_setup_success(self):
        """Test LLM setup success"""

        # ARRANGE
        type="query"

        # ACT
        llm=set_llm(type)

        # ASSERT
        assert llm is not None

class TestRateLimiter:
    def test_clean_old_enteries_success(self):
        # ARRANGE
        limiter=get_rate_limiter()
        now=time.time()
        limiter._storage["test"]["test"]=[now-11]

        # ACT
        limiter._cleanup_old_entries(identifier="test",window="test",window_seconds=10)

        # ASSERT
        assert limiter._storage["test"]["test"]==[]

    def test_check_rate_limit_allows_first_request(self):
        limiter = get_rate_limiter()
        limiter.reset()

        allowed, retry_after = limiter.check_rate_limit(
            identifier="user1",
            limit=5,
            window_seconds=10,
            window_name="default"
        )

        assert allowed is True
        assert retry_after is None

    def test_check_rate_limit_allows_under_limit(self):
        limiter = get_rate_limiter()
        limiter.reset()

        for _ in range(3):
            allowed, _ = limiter.check_rate_limit("user1", 5, 10)

        assert allowed is True

    def test_check_rate_limit_blocks_when_limit_exceeded(self):
        limiter = get_rate_limiter()
        limiter.reset()

        for _ in range(3):
            limiter.check_rate_limit("user1", 3, 10)

        allowed, retry_after = limiter.check_rate_limit("user1", 3, 10)

        assert allowed is False
        assert retry_after is not None
        assert retry_after >= 1

    def test_check_multiple_limits_all_allowed(self):
        limiter = get_rate_limiter()
        limiter.reset()

        limits = {
            "per_minute": (5, 60),
            "per_hour": (100, 3600)
        }

        allowed, retry_after, violated = limiter.check_multiple_limits("user1", limits)

        assert allowed is True
        assert retry_after is None
        assert violated is None

    def test_check_multiple_limits_blocks_on_violation(self):
        limiter = get_rate_limiter()
        limiter.reset()

        for _ in range(2):
            limiter.check_rate_limit("user1", 2, 60, "per_minute")

        limits = {
            "per_minute": (2, 60),
            "per_hour": (100, 3600)
        }

        allowed, retry_after, violated = limiter.check_multiple_limits("user1", limits)

        assert allowed is False
        assert retry_after is not None
        assert violated == "per_minute"
        
    def test_reset_all_identifiers(self):
        limiter = get_rate_limiter()
        limiter.reset()

        limiter.check_rate_limit("user1", 5, 10)
        limiter.check_rate_limit("user2", 5, 10)

        limiter.reset()

        assert limiter._storage == {}

def create_test_app():
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "OK"}

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        return app

class TestRateMiddleware:

    def test_excluded_path_skips_rate_limiting(self):
        app=create_test_app()
        app.add_middleware(RateLimitMiddleware)
        client=TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_rate_limit_allowed(self):
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = (True, None)

        app = create_test_app()
        middleware = RateLimitMiddleware(app, limiter=mock_limiter)
        client = TestClient(middleware)

        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        mock_limiter.check_rate_limit.assert_called_once()