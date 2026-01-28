import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        # Import the app directly to catch any import errors
        from backend.main import app
        
        port = int(os.getenv("PORT", 8000))
        print(f"Starting server on port {port}", flush=True)
        print(f"Host: 0.0.0.0", flush=True)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)