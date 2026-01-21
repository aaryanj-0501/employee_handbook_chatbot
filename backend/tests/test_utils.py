from utils.pdf_loader import load_pdf
from utils.chunker import chunk_text,clean_text
from utils.embeddings import get_embedding
from utils.llm_setup import set_llm
import pytest
from unittest.mock import patch
from conftest import sample_pdf_path

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


