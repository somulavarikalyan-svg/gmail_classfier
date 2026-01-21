"""
Logging configuration for the Gmail Cleanup Agent.
Provides structured JSON logging for machine parsing and human-readable console output.
"""
import logging
import json
import os
from datetime import datetime
from typing import Any, Dict
from .config import LOG_FILE

class JsonFormatter(logging.Formatter):
    """
    Formatter to output logs as JSON objects for easier parsing and observability.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        # Include extra fields if passed in 'extra' dict
        if hasattr(record, 'props'):
            log_record.update(record.props)  # type: ignore
        
        return json.dumps(log_record)

def setup_logger() -> logging.Logger:
    """
    Configures and returns the application logger.
    Logs are written to a file in JSON format and to the console in text format.
    """
    logger = logging.getLogger("GmailAgent")
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times if function is called repeatedly
    if logger.hasHandlers():
        return logger

    # File Handler (JSON)
    try:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

    # Console Handler (Human readable)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger

# Singleton logger instance
logger = setup_logger()
