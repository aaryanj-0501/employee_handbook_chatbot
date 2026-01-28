import os
import sys
import uvicorn
from pathlib import Path
import logging
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
load_dotenv()

# Setup basic logging before everything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Check for required environment variables
        required_vars = ["QDRANT_URL", "QDRANT_API_KEY", "JWT_SECRET_KEY", 
                        "CHAT_MODEL_NAME", "ANSWER_MODEL", "OLLAMA_BASE_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.info("Server will still start but may have limited functionality")
        
        # Render's default PORT is 10000, use environment variable if set
        port = int(os.getenv("PORT", 10000))
        host = "0.0.0.0"
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Environment variables configured: QDRANT_URL={bool(os.getenv('QDRANT_URL'))}, "
                   f"JWT_SECRET_KEY={bool(os.getenv('JWT_SECRET_KEY'))}, "
                   f"CHAT_MODEL_NAME={os.getenv('CHAT_MODEL_NAME', 'not set')}, "
                   f"OLLAMA_BASE_URL={os.getenv('OLLAMA_BASE_URL', 'not set')}")
        
        # Start uvicorn server - this will bind to the port and start listening
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)