# config/__init__.py
"""
Configuration module for Device Transaction Automation
"""

import os
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "config.yaml")
            
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                raise FileNotFoundError(f"Please create {config_path}")
            
            with open(config_path, 'r') as file:
                self._config = yaml.safe_load(file)
            
            logger.info(f"✅ Configuration loaded from {config_path}")
            
            # Override with environment variables if present
            self._override_from_env()
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def _override_from_env(self):
        """Override configuration with environment variables"""
        # Environment
        if os.getenv("ENVIRONMENT"):
            self._config["active_environment"] = os.getenv("ENVIRONMENT")
        
        # URLs
        if os.getenv("ADMIN_PORTAL_URL"):
            self._config["urls"]["admin_portal"] = os.getenv("ADMIN_PORTAL_URL")
        if os.getenv("TMS_PORTAL_URL"):
            self._config["urls"]["tms_portal"] = os.getenv("TMS_PORTAL_URL")
        if os.getenv("IPN_API_URL"):
            self._config["urls"]["ipn_api"] = os.getenv("IPN_API_URL")
        
        # Test settings
        if os.getenv("HEADLESS"):
            self._config["test"]["headless"] = os.getenv("HEADLESS").lower() == "true"
        if os.getenv("MAX_RETRIES"):
            self._config["api"]["max_retries"] = int(os.getenv("MAX_RETRIES"))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        if not self._config:
            return default
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get configuration for active environment"""
        env = self.get("active_environment", "staging")
        env_config = self.get(f"environments.{env}", {})
        return {**env_config, "name": env}
    
    def get_urls(self) -> Dict[str, str]:
        """Get all URLs"""
        return self.get("urls", {})
    
    def get_test_config(self) -> Dict[str, Any]:
        """Get test configuration"""
        return self.get("test", {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.get("api", {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return self.get("data", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.get("database", {})

# Create a global instance
config = Config()