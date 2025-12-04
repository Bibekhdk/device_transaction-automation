# api/dps_api.py
import logging
from typing import Dict, Any
from api.base_api import BaseAPI
import allure

logger = logging.getLogger(__name__)

class DPSAPI(BaseAPI):
    """Client for DPS (Device Provisioning Service) API"""
    
    def __init__(self, base_url: str):
        super().__init__(base_url)
        
    @allure.step("Send DPS request for device {serial_number}")
    def send_dps_request(self, serial_number: str) -> Dict[str, Any]:
        """
        Send DPS request to provision device
        
        Args:
            serial_number: Device serial number
            
        Returns:
            Response from DPS API
        """
        endpoint = "/ipn/provision"  
        
        payload = {
            "serial_number": serial_number,
            "action": "provision",
            "timestamp": self._get_timestamp()
        }
        
        logger.info(f"Sending DPS request for device: {serial_number}")
        
        try:
            response = self.post(endpoint, json=payload)
            
            # Validate response
            if response.get('status') == 'success' or response.get('status_code') == 200:
                logger.info(f"✅ DPS request successful for {serial_number}")
                return response
            else:
                error_msg = f"DPS request failed: {response}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"❌ DPS request failed for {serial_number}: {str(e)}")
            raise
    
    @allure.step("Check DPS status for device {serial_number}")
    def check_dps_status(self, serial_number: str) -> Dict[str, Any]:
        """
        Check DPS provisioning status
        
        Args:
            serial_number: Device serial number
            
        Returns:
            DPS status response
        """
        endpoint = f"/ipn/provision{serial_number}"  # Update with actual endpoint
        
        logger.info(f"Checking DPS status for device: {serial_number}")
        
        try:
            response = self.get(endpoint)
            logger.info(f"DPS status for {serial_number}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to check DPS status: {str(e)}")
            raise
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"