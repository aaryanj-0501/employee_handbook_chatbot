import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        
        # Render's default PORT is 10000, use environment variable if set
        port = int(os.getenv("PORT", 10000))
        host = "0.0.0.0"
        
        print(f"Starting server on {host}:{port}", flush=True)
        print(f"PORT environment variable: {os.getenv('PORT', 'not set (using default 10000)')}", flush=True)
        
        # Start uvicorn server - this will bind to the port and start listening
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"Error starting server: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)