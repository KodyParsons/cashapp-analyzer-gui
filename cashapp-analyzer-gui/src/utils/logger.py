"""Logging utilities for Cash App Analyzer"""
import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str = "CashAppAnalyzer", 
                log_file: Optional[str] = None,
                level: int = logging.INFO) -> logging.Logger:
    """Set up application logger"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    return logger

# Default logger instance
logger = setup_logger()

def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper
