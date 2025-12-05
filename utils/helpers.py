# utils/helpers.py
import time
import random
import string
from datetime import datetime
from typing import Optional, Callable, Any
import logging
from functools import wraps
import os

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: int = 2, exceptions: tuple = (Exception,)):
    """
    Retry decorator for flaky operations
    
    Example:
        @retry(max_attempts=3, delay=2)
        def call_api():
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = delay * attempt  # Exponential backoff
                        logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def generate_random_string(length: int = 10, prefix: str = "") -> str:
    """Generate random string for test data"""
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{random_str}"

def generate_imei() -> str:
    """Generate valid 15-digit IMEI number"""
    # Generate 14 random digits
    imei_base = ''.join(str(random.randint(0, 9)) for _ in range(14))
    
    # Calculate Luhn check digit
    def luhn_checksum(number: str) -> int:
        def digits_of(n: str):
            return [int(d) for d in str(n)]
        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10
    
    check_digit = (10 - luhn_checksum(imei_base)) % 10
    return f"{imei_base}{check_digit}"

def generate_sim_details() -> dict:
    """Generate random SIM details"""
    operators = ["NTC", "Ncell", "Smart Cell"]
    return {
        "number": f"984{random.randint(1000000, 9999999)}",
        "operator": random.choice(operators),
        "type": "Prepaid"
    }

def timer(func: Callable) -> Callable:
    """Decorator to measure execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{func.__name__} executed in {duration:.2f} seconds")
        
        # Warn if execution exceeds threshold
        if duration > 600:  # 10 minutes
            logger.warning(f"{func.__name__} exceeded 10 minutes!")
            
        return result
    return wrapper

def validate_device_serial(serial_number: str) -> bool:
    """Validate device serial number format"""
    # Your device serials: 38250820332278 (14 digits)
    if not serial_number or not isinstance(serial_number, str):
        return False
    
    # Remove any whitespace
    serial = serial_number.strip()
    
    # Check if it's numeric and length is 14
    if serial.isdigit() and len(serial) == 14:
        return True
    
    logger.warning(f"Invalid serial number format: {serial_number}")
    return False

def get_timestamp(format: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """Get current timestamp in specified format"""
    return datetime.now().strftime(format)

def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Directory created/verified: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def read_env_var(key: str, default: Any = None) -> Any:
    """Read environment variable with fallback"""
    value = os.getenv(key, default)
    if value is None:
        logger.warning(f"Environment variable {key} not set, using default: {default}")
    return value

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout(seconds: int):
    """
    Timeout decorator
    
    Example:
        @timeout(10)
        def long_running_task():
            time.sleep(20)  # Will raise TimeoutError
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set signal handler
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable alarm
                signal.alarm(0)
            
            return result
        return wrapper
    return decorator

def mask_sensitive_data(data: Any, fields: list = None) -> Any:
    """
    Mask sensitive data in logs
    
    Args:
        data: Data to mask (dict, list, or string)
        fields: List of field names to mask (default: common sensitive fields)
    
    Returns:
        Masked data
    """
    if fields is None:
        fields = ['key', 'password', 'token', 'secret', 'auth', 'api_key', 'authorization']
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in fields):
                if value and isinstance(value, str):
                    masked[key] = f"{value[:10]}..." if len(value) > 10 else "***"
                else:
                    masked[key] = "***"
            else:
                masked[key] = mask_sensitive_data(value, fields)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, fields) for item in data]
    else:
        return data