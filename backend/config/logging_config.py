import os
import logging
import sys
from datetime import datetime

def setup_logging():
    handlers = [logging.StreamHandler(sys.stdout)]  # Console output
    
    # Try to create logs directory and file handler, but don't fail if it's not possible
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        handlers.append(
            logging.FileHandler(filename=log_file, mode='a')
        )
    except (OSError, PermissionError) as e:
        # If we can't create log files, just use console logging
        print(f"Warning: Could not set up file logging: {e}", flush=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        root_logger.addHandler(handler)

    logging.info("Logging config loaded")