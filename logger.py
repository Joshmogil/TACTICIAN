"""Logger setup for brain simulation."""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Set up and return the logger."""
    # Create logger
    logger = logging.getLogger("brain")
    logger.setLevel(logging.DEBUG)

    # Console handler - minimal output
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_format = logging.Formatter('%(message)s')
    console.setFormatter(console_format)

    # File handler - detailed output
    file_handler = RotatingFileHandler('brain.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger

# Create the logger
logger = setup_logger()