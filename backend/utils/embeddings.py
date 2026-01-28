from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import logging

logger=logging.getLogger(__name__)

load_dotenv()

MODEL_NAME=os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# Lazy-load the embedding model
_embedding_model = None

def get_embedding_model():
    """Get or initialize the embedding model with lazy loading."""
    global _embedding_model
    
    if _embedding_model is not None:
        return _embedding_model
    
    try:
        _embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        logger.info(f"Initialized embedding model: {MODEL_NAME}")
        return _embedding_model
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise

def get_embedding(text:str):
    try:
        model = get_embedding_model()
        response = model.embed_query(text)
        logger.info("Generated embedding successfully.")
        return response
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise



