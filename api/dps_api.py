# api/dps_api.py
import logging
from typing import Dict, Any, Optional
from api.base_api import BaseAPI
import allure
import os

logger = logging.getLogger(__name__)

class DPSAPI(BaseAPI):
    """Client for DPS (Device Provisioning Service) API"""
    
    def __init__(self, base_url: str = None, auth_token: str = None):
        """
        Initialize DPS API client
        
        Args:
            base_url: DPS API base URL
            auth_token: Fixed authentication token for DPS
        """
        # Use provided URL or default
        if not base_url:
            base_url = "dps-staging.koilifin.com"
        
        # Get token from parameter, env, or use placeholder
        if not auth_token:
            auth_token = os.getenv("DPS_AUTH_TOKEN", "YOUR_FIXED_DPS_TOKEN_HERE")
        
        # Initialize with auth_token (DPS seems to use token auth)
        super().__init__(base_url, auth_token=auth_token, auth_type='token')
        
        # Store the actual token for reference
        self.dps_token = auth_token
        
    @allure.step("Send DPS request for device {serial_number}")
    def send_dps_request(self, serial_number: str) -> Dict[str, Any]:
        """
        Send DPS request to provision device
        
        Args:
            serial_number: Device serial number
            
        Returns:
            Response from DPS API with keys: "key" and "host"
            
        Response format: {"key": "...", "host": "..."}
        """
        endpoint = "/ipn/provision"  
        
        # Payload is just serial number
        payload = {
            "serial_number": serial_number
        }
        
        logger.info(f"Sending DPS request for device: {serial_number}")
        logger.debug(f"Payload: {payload}")
        
        try:
            # Make the request
            response = self.post(endpoint, json=payload)
            
            # Log response for debugging (mask key for security)
            self._log_response_safely(response)
            
            # Validate response format
            self._validate_dps_response(response, serial_number)
            
            logger.info(f"✅ DPS request successful for {serial_number}")
            return response
                
        except Exception as e:
            logger.error(f"❌ DPS request failed for {serial_number}: {str(e)}")
            raise
    
    def _log_response_safely(self, response: Dict):
        """Log response without exposing sensitive data"""
        if response and isinstance(response, dict):
            masked_response = response.copy()
            
            # Mask the key if present
            if "key" in masked_response and masked_response["key"]:
                key = masked_response["key"]
                masked_response["key"] = f"{key[:20]}... (length: {len(key)} chars)"
            
            logger.debug(f"DPS Response: {masked_response}")
        else:
            logger.debug(f"DPS Response: {response}")
    
    def _validate_dps_response(self, response: Dict, serial_number: str):
        """Validate DPS response contains required fields"""
        if not isinstance(response, dict):
            raise Exception(f"Invalid response format. Expected dict, got: {type(response)}")
        
        # Check for required fields
        required_fields = ["key", "host"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            raise Exception(f"Missing required fields in DPS response: {missing_fields}. Response: {response}")
        
        # Validate field contents
        key = response["key"]
        host = response["host"]
        
        if not key or not isinstance(key, str):
            raise Exception(f"Invalid 'key' field in DPS response: {key}")
        
        if not host or not isinstance(host, str):
            raise Exception(f"Invalid 'host' field in DPS response: {host}")
        
        # Additional validations
        if len(key) < 20:
            logger.warning(f"DPS key appears short ({len(key)} chars) for device {serial_number}")
        
        if "azure-devices.net" not in host:
            logger.warning(f"DPS host doesn't contain expected domain for device {serial_number}: {host}")
    
    @allure.step("Verify DPS response")
    def verify_dps_response(self, response: Dict, serial_number: str) -> bool:
        """Verify DPS response is valid"""
        try:
            self._validate_dps_response(response, serial_number)
            logger.info(f"✅ DPS response verified for device {serial_number}")
            return True
        except Exception as e:
            logger.error(f"❌ DPS response verification failed for {serial_number}: {e}")
            return False
    
    @allure.step("Check DPS status")
    def check_dps_status(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Check DPS provisioning status"""
        endpoint = f"/status/{serial_number}"  # Adjust based on actual endpoint
        
        logger.info(f"Checking DPS status for device: {serial_number}")
        
        try:
            response = self.get(endpoint)
            
            if response and isinstance(response, dict):
                logger.info(f"DPS status for {serial_number}: {response}")
                return response
            return None
                
        except Exception as e:
            logger.warning(f"DPS status check failed for {serial_number}: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if DPS API is accessible"""
        try:
            # Try to make a test request
            test_payload = {"serial_number": "TEST1234567890"}
            response = self.post("/ipn/provision", json=test_payload)
            
            # We might get an error for test serial, but that's okay
            # As long as we get some response
            return response is not None
            
        except Exception as e:
            # Check if it's a 404 (test device not found) vs connection error
            if "404" in str(e) or "not found" in str(e).lower():
                # Got a response, so API is accessible
                return True
            logger.warning(f"DPS API health check warning: {e}")
            return False
    
    @allure.step("Extract IoT Hub connection details")
    def extract_iot_hub_details(self, dps_response: Dict) -> Dict[str, str]:
        """Extract IoT Hub connection details from DPS response"""
        try:
            key = dps_response.get("key", "")
            host = dps_response.get("host", "")
            
            # Parse the host to get IoT Hub name
            if "azure-devices.net" in host:
                iot_hub_name = host.replace(".azure-devices.net", "")
            else:
                iot_hub_name = host
            
            return {
                "iot_hub_host": host,
                "iot_hub_name": iot_hub_name,
                "device_key": key,
                "connection_string": f"HostName={host};DeviceId=test;SharedAccessKey={key}",
                "is_valid": bool(key and host)
            }
        except Exception as e:
            logger.error(f"Failed to extract IoT Hub details: {e}")
            return {"is_valid": False}