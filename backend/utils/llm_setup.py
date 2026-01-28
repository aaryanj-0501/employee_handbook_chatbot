from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

QUERY_MODEL = os.getenv("CHAT_MODEL_NAME")
ANSWER_MODEL = os.getenv("ANSWER_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

def set_llm(type: str):
    """
    Create and return a ChatOllama LLM instance.
    
    Args:
        type: Either "answer" or "query" to determine which model to use
        
    Returns:
        ChatOllama instance configured for cloud or local Ollama
    """
    try:
        # Determine which model to use
        model_name = ANSWER_MODEL if type == "answer" else QUERY_MODEL
        
        if not model_name:
            logger.warning(f"Model name not configured for type '{type}'")
            raise ValueError(f"Model not configured for type: {type}")
        
        # Base configuration
        llm_config = {
            "model": model_name,
            "temperature": 0,
            "base_url": OLLAMA_BASE_URL,
        }
        
        # Add API key authentication for cloud Ollama if provided
        if OLLAMA_API_KEY:
            # The ollama client uses the OLLAMA_API_KEY environment variable
            # Set it before creating the client
            os.environ["OLLAMA_API_KEY"] = OLLAMA_API_KEY
            llm_config["headers"]={
                "Authorization":f"Bearer {OLLAMA_API_KEY}"
            }
            logger.info(f"Using Ollama API key for authentication")
        
        llm = ChatOllama(**llm_config)
        logger.info(f"Initialized LLM for type '{type}' with model '{model_name}'")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM for type '{type}': {e}")
        raise