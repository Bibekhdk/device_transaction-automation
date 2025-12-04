# api/ipn_api.py
import logging
from typing import Dict, Any
from api.base_api import BaseAPI
import allure
import os

logger = logging.getLogger(__name__)

class IPNAPI(BaseAPI):
    """Client for IPN (Instant Payment Notification) API"""
    
    def __init__(self, base_url: str, scheme: str = "nchl"):
        """
        Initialize IPN API client
        
        Args:
            base_url: IPN API base URL
            scheme: Payment scheme (nchl or fonepay)
        """
        # Get API key based on scheme
        api_key = os.getenv(
            "NCHL_API_KEY" if scheme == "nchl" else "FONEPAY_API_KEY"
        )
        
        if not api_key:
            raise ValueError(f"API key not found for scheme: {scheme}")
        
        super().__init__(base_url, api_key)
        self.scheme = scheme
        
    @allure.step("Send {scheme} transaction notification")
    def send_transaction(
        self, 
        amount: str, 
        merchant_code: str = None, 
        merchant_id: str = None,
        store_id: str = None,
        terminal_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send transaction notification to IPN
        
        Args:
            amount: Transaction amount
            merchant_code: NCHL merchant code
            merchant_id: Fonepay merchant ID
            store_id: NCHL store ID
            terminal_id: Terminal ID
            **kwargs: Additional parameters
            
        Returns:
            Response from IPN API
        """
        endpoint = "/notify"  # Based on your Step 8
        
        # Build payload based on scheme
        payload = self._build_payload(
            amount, merchant_code, merchant_id, store_id, terminal_id, **kwargs
        )
        
        logger.info(f"Sending {self.scheme} transaction: {payload}")
        
        try:
            response = self.post(endpoint, json=payload)
            
            # Validate response
            expected_message = "notification delivered successfully"
            if response.get('message') == expected_message:
                logger.info(f"✅ {self.scheme.upper()} transaction successful: {amount}")
                return response
            else:
                error_msg = f"{self.scheme.upper()} transaction failed: {response}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"❌ {self.scheme.upper()} transaction failed: {str(e)}")
            raise
    
    @allure.step("Send NCHL transaction")
    def send_nchl_transaction(
        self, 
        amount: str, 
        store_id: str,
        terminal_id: str,
        merchant_code: str
    ) -> Dict[str, Any]:
        """
        Send NCHL scheme transaction
        
        Args:
            amount: Transaction amount (e.g., "33333")
            store_id: Store ID from device assignment
            terminal_id: Terminal ID from device assignment
            merchant_code: Merchant code from merchant creation
            
        Returns:
            Response from IPN API
        """
        # Create NCHL-specific client
        nchl_client = IPNAPI(self.base_url, scheme="nchl")
        
        return nchl_client.send_transaction(
            amount=amount,
            storeId=store_id,
            terminalId=terminal_id,
            merchantCode=merchant_code
        )
    
    @allure.step("Send Fonepay transaction")
    def send_fonepay_transaction(
        self, 
        amount: str, 
        merchant_id: str,
        terminal_id: str
    ) -> Dict[str, Any]:
        """
        Send Fonepay scheme transaction
        
        Args:
            amount: Transaction amount (e.g., "44444")
            merchant_id: Merchant ID from merchant creation
            terminal_id: Terminal ID from device assignment
            
        Returns:
            Response from IPN API
        """
        # Create Fonepay-specific client
        fonepay_client = IPNAPI(self.base_url, scheme="fonepay")
        
        return fonepay_client.send_transaction(
            amount=amount,
            merchantId=merchant_id,
            terminalId=terminal_id
        )
    
    def _build_payload(
        self, 
        amount: str,
        merchant_code: str = None,
        merchant_id: str = None,
        store_id: str = None,
        terminal_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build payload based on payment scheme"""
        if self.scheme == "nchl":
            payload = {
                "amount": str(amount),
                "storeId": store_id,
                "terminalId": terminal_id,
                "merchantCode": merchant_code
            }
        elif self.scheme == "fonepay":
            payload = {
                "amount": str(amount),
                "merchantId": merchant_id,
                "terminalId": terminal_id
            }
        else:
            raise ValueError(f"Unsupported scheme: {self.scheme}")
        
        # Add additional parameters if provided
        payload.update(kwargs)
        return payload
    
    @allure.step("Verify IPN API health")
    def health_check(self) -> bool:
        """Check if IPN API is accessible"""
        try:
            # Try a simple endpoint or base URL
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code < 500
        except:
            return False