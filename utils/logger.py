# utils/logger.py
import logging
import sys
from datetime import datetime
import os
from typing import Optional

def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_to_console: Whether to log to console
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with timestamp if not provided
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"automation_{timestamp}.log")
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(file_handler)
    
    # Console handler (if enabled)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    
    # Log initialization info
    logger.info(f"Logger initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Console logging: {log_to_console}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Name of the module (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def set_log_level(log_level: str):
    """
    Set log level for all handlers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, log_level.upper()))
    
    logger.info(f"Log level changed to: {log_level}")

def add_file_handler(log_file: str):
    """
    Add an additional file handler
    
    Args:
        log_file: Path to log file
    """
    logger = logging.getLogger()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger.level)
    
    # Add to logger
    logger.addHandler(file_handler)
    
    logger.info(f"Added additional log file: {log_file}")

def log_test_start(test_name: str, **kwargs):
    """
    Log test start information
    
    Args:
        test_name: Name of the test
        **kwargs: Additional test parameters
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"STARTING TEST: {test_name}")
    logger.info("=" * 60)
    
    if kwargs:
        logger.info("Test Parameters:")
        for key, value in kwargs.items():
            logger.info(f"  {key}: {value}")

def log_test_end(test_name: str, status: str, duration: float = None):
    """
    Log test end information
    
    Args:
        test_name: Name of the test
        status: Test status (PASS, FAIL, SKIP)
        duration: Test duration in seconds (optional)
    """
    logger = logging.getLogger(__name__)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    
    logger.info("=" * 60)
    logger.info(f"{status_icon} TEST COMPLETED: {test_name}")
    logger.info(f"Status: {status}")
    
    if duration is not None:
        logger.info(f"Duration: {duration:.2f} seconds")
    
    logger.info("=" * 60)

def log_step(step_name: str):
    """
    Log a test step
    
    Args:
        step_name: Name of the step
    """
    logger = logging.getLogger(__name__)
    logger.info(f"➡️  STEP: {step_name}")

def log_screenshot(screenshot_path: str):
    """
    Log screenshot information
    
    Args:
        screenshot_path: Path to screenshot file
    """
    logger = logging.getLogger(__name__)
    logger.info(f"📸 Screenshot saved: {screenshot_path}")

def log_api_request(method: str, url: str, payload: dict = None):
    """
    Log API request information
    
    Args:
        method: HTTP method
        url: Request URL
        payload: Request payload (optional)
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"🌐 API Request: {method} {url}")
    
    if payload:
        # Mask sensitive data
        from .helpers import mask_sensitive_data
        masked_payload = mask_sensitive_data(payload)
        logger.debug(f"Request payload: {masked_payload}")

def log_api_response(response: dict, status_code: int = None):
    """
    Log API response information
    
    Args:
        response: API response
        status_code: HTTP status code
    """
    logger = logging.getLogger(__name__)
    
    if status_code:
        status_icon = "✅" if 200 <= status_code < 300 else "❌"
        logger.info(f"{status_icon} API Response: Status {status_code}")
    
    if response:
        # Mask sensitive data
        from .helpers import mask_sensitive_data
        masked_response = mask_sensitive_data(response)
        logger.debug(f"Response: {masked_response}")