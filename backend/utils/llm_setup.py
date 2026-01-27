from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

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
    # Determine which model to use
    model_name = ANSWER_MODEL if type == "answer" else QUERY_MODEL
    
    # Base configuration
    llm_config = {
        "model": model_name,
        "temperature": 0,
        "base_url": OLLAMA_BASE_URL,
    }
    
    # Add API key authentication for cloud Ollama if provided
    if OLLAMA_API_KEY:
        
        # Set the API key as an environment variable for the underlying HTTP client
        os.environ["OLLAMA_API_KEY"] = OLLAMA_API_KEY
        
        # Some ChatOllama versions support headers parameter directly
        # Try adding headers if the version supports it
        try:
            llm_config["headers"] = {
                "Authorization": f"Bearer {OLLAMA_API_KEY}"
            }
        except (TypeError, ValueError):
            # If headers parameter is not supported, the API key in env var
            # should be picked up by the underlying HTTP client
            pass
    
    llm = ChatOllama(**llm_config)
    return llm