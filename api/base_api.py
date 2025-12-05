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
    
    def __init__(self, base_url: str, api_key: str = None, auth_token: str = None, auth_type: str = "api_key"):
        """
        Initialize Base API client
        
        Args:
            base_url: Base URL for API
            api_key: API key for authentication
            auth_token: Authentication token (Bearer, JWT, etc.)
            auth_type: Type of authentication ('api_key', 'bearer', 'token', 'basic')
        """
        self.base_url = base_url if base_url.startswith('http') else f'https://{base_url}'
        self.api_key = api_key
        self.auth_token = auth_token
        self.auth_type = auth_type
        self.session = requests.Session()
        self.timeout = 30
        self.max_retries = 3
        
        # Setup session headers
        self._setup_headers()
        
        # Log initialization (without exposing secrets)
        self._log_initialization()
    
    def _setup_headers(self):
        """Setup session headers with authentication"""
        headers = {
            'User-Agent': 'DeviceTransactionAutomation/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add authentication based on type
        if self.auth_type == 'api_key' and self.api_key:
            headers['Subscription-Key'] = self.api_key
            headers['X-API-Key'] = self.api_key
        elif self.auth_type == 'bearer' and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        elif self.auth_type == 'token' and self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        elif self.auth_type == 'basic' and self.auth_token:
            headers['Authorization'] = f'Basic {self.auth_token}'
        elif self.auth_token:  # Default to Bearer if auth_token provided but no type specified
            # Auto-detect token type
            if self.auth_token.startswith('eyJ') and '.' in self.auth_token:  # JWT token
                headers['Authorization'] = f'Bearer {self.auth_token}'
            elif len(self.auth_token) > 50:  # Long token, likely API key
                headers['X-API-Key'] = self.auth_token
            else:  # Simple token
                headers['Authorization'] = f'Bearer {self.auth_token}'
        
        self.session.headers.update(headers)
    
    def _log_initialization(self):
        """Log API initialization without exposing secrets"""
        # Mask sensitive information
        masked_url = self.base_url
        if '@' in self.base_url:  # Contains credentials
            parts = self.base_url.split('@')
            masked_url = f"***@{parts[1]}" if len(parts) > 1 else "***"
        
        # Mask auth tokens
        auth_info = ""
        if self.api_key:
            masked_key = f"{self.api_key[:10]}..." if len(self.api_key) > 10 else "***"
            auth_info = f" with API key: {masked_key}"
        elif self.auth_token:
            masked_token = f"{self.auth_token[:15]}..." if len(self.auth_token) > 15 else "***"
            auth_info = f" with {self.auth_type} auth: {masked_token}"
        
        logger.info(f"Initialized API client for {masked_url}{auth_info}")
    
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
            
            # Log response status
            logger.info(f"{method} {url} - Status: {response.status_code}")
            
            # For debugging, log response for non-2xx
            if not response.ok:
                logger.warning(f"Request returned {response.status_code}: {response.text[:200]}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout for {url} after {self.timeout}s")
            raise
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            error_text = e.response.text[:200] if e.response else str(e)
            
            # Special handling for common status codes
            if status_code == 401:
                logger.error(f"Authentication failed (401) for {url}")
                logger.error("Check your API key or auth token")
            elif status_code == 403:
                logger.error(f"Access forbidden (403) for {url}")
                logger.error("Check your permissions")
            elif status_code == 404:
                logger.error(f"Endpoint not found (404) for {url}")
            elif status_code == 429:
                logger.error(f"Rate limited (429) for {url}")
                logger.error("Too many requests, try again later")
            else:
                logger.error(f"HTTP error {status_code} for {url}: {error_text}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {url}: {str(e)}")
            logger.error("Check network connectivity and URL")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise
    
    def post(self, endpoint: str, data: Dict = None, json: Dict = None, **kwargs) -> Dict:
        """Make POST request"""
        response = self._make_request('POST', endpoint, data=data, json=json, **kwargs)
        return self._parse_response(response)
    
    def get(self, endpoint: str, **kwargs) -> Dict:
        """Make GET request"""
        response = self._make_request('GET', endpoint, **kwargs)
        return self._parse_response(response)
    
    def put(self, endpoint: str, data: Dict = None, json: Dict = None, **kwargs) -> Dict:
        """Make PUT request"""
        response = self._make_request('PUT', endpoint, data=data, json=json, **kwargs)
        return self._parse_response(response)
    
    def delete(self, endpoint: str, **kwargs) -> Dict:
        """Make DELETE request"""
        response = self._make_request('DELETE', endpoint, **kwargs)
        return self._parse_response(response)
    
    def _parse_response(self, response: requests.Response) -> Dict:
        """Parse response and handle errors"""
        try:
            if response.content:
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    return response.json()
                elif 'text/' in content_type:
                    return {"text": response.text, "status_code": response.status_code}
                else:
                    # Try to parse as JSON anyway
                    try:
                        return response.json()
                    except:
                        return {
                            "content": response.content.decode('utf-8', errors='ignore'),
                            "status_code": response.status_code
                        }
            return {"status_code": response.status_code}
        except ValueError as e:
            logger.warning(f"Failed to parse response as JSON: {e}")
            logger.debug(f"Raw response: {response.text[:200]}")
            return {"text": response.text, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return {"error": str(e), "status_code": response.status_code}
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            # Try a HEAD request first (lightweight)
            response = self.session.head(self.base_url, timeout=5)
            return response.status_code < 500
        except requests.RequestException:
            # If HEAD fails, try GET
            try:
                response = self.session.get(self.base_url, timeout=5)
                return response.status_code < 500
            except:
                return False
    
    def set_timeout(self, timeout: int):
        """Set default timeout for requests"""
        self.timeout = timeout
        logger.info(f"Set request timeout to {timeout} seconds")
    
    def set_max_retries(self, max_retries: int):
        """Set maximum retry attempts"""
        self.max_retries = max_retries
        logger.info(f"Set maximum retries to {max_retries}")
    
    def add_header(self, key: str, value: str):
        """Add custom header to session"""
        self.session.headers[key] = value
        logger.debug(f"Added header: {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    def remove_header(self, key: str):
        """Remove header from session"""
        if key in self.session.headers:
            del self.session.headers[key]
            logger.debug(f"Removed header: {key}")
    
    def clear_headers(self):
        """Clear all custom headers"""
        self.session.headers.clear()
        self._setup_headers()  # Re-setup default headers
        logger.debug("Cleared all headers and reset to defaults")