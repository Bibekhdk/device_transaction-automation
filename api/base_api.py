# api/base_api.py
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import time
from utils.helpers import retry

logger = logging.getLogger(__name__)

class BaseAPI:
    """Base class for all API clients"""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.timeout = 30
        self.max_retries = 3
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': 'DeviceTransactionAutomation/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if api_key:
            self.session.headers.update({'Subscription-Key': api_key})
    
    @retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = urljoin(self.base_url, endpoint)
        
        # Add timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            logger.info(f"{method} {url} - Status: {response.status_code}")
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise
    
    def post(self, endpoint: str, data: Dict = None, json: Dict = None, **kwargs) -> Dict:
        """Make POST request"""
        response = self._make_request('POST', endpoint, data=data, json=json, **kwargs)
        return response.json() if response.content else {}
    
    def get(self, endpoint: str, **kwargs) -> Dict:
        """Make GET request"""
        response = self._make_request('GET', endpoint, **kwargs)
        return response.json() if response.content else {}
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code < 500
        except:
            return False