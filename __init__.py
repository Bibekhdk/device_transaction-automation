# utils/__init__.py
"""
Utilities module for Device Transaction Automation
"""

from .logger import (
    setup_logger,
    get_logger,
    set_log_level,
    add_file_handler,
    log_test_start,
    log_test_end,
    log_step,
    log_screenshot,
    log_api_request,
    log_api_response
)

from .helpers import (
    retry,
    generate_random_string,
    generate_imei,
    generate_sim_details,
    timer,
    validate_device_serial,
    get_timestamp,
    create_directory,
    read_env_var,
    TimeoutError,
    timeout,
    mask_sensitive_data
)

__all__ = [
    # Logger functions
    'setup_logger',
    'get_logger',
    'set_log_level',
    'add_file_handler',
    'log_test_start',
    'log_test_end',
    'log_step',
    'log_screenshot',
    'log_api_request',
    'log_api_response',
    
    # Helper functions
    'retry',
    'generate_random_string',
    'generate_imei',
    'generate_sim_details',
    'timer',
    'validate_device_serial',
    'get_timestamp',
    'create_directory',
    'read_env_var',
    'TimeoutError',
    'timeout',
    'mask_sensitive_data'
]