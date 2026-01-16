import os
import logging
import sys
from datetime import datetime

def setup_logging():
    os.makedirs('logs',exist_ok=True)
    handlers=[
        logging.StreamHandler(sys.stdout), #Console output
        logging.FileHandler(
            filename=os.path.join(os.path.dirname(__file__), f'../logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
            mode='a'
        ) #Daily log files
    ]

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        root_logger.addHandler(handler)

    logging.info("Logging config loaded")