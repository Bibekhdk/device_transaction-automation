# api/ipn_api.py
import logging
from typing import Dict, Any
from api.base_api import BaseAPI
import allure
import os

logger = logging.getLogger(__name__)

class IPNAPI(BaseAPI):
    """Client for IPN (Instant Payment Notification) API"""
    
    def __init__(self, base_url: str = None, scheme: str = "nchl", **kwargs):
        """
        Initialize IPN API client
        
        Args:
            base_url: IPN API base URL (optional)
            scheme: Payment scheme (nchl or fonepay)
        """
        # Get base URL - use provided or default
        if not base_url:
            base_url = "https://ipn-dev.qrsoundboxnepal.com/api/v1-stg/notify"
        
        # Get API key based on scheme
        api_key = kwargs.get("api_key")
        if not api_key:
            api_key = os.getenv(
                "NCHL_API_KEY" if scheme == "nchl" else "FONEPAY_API_KEY"
            )
        
        if not api_key:
            logger.warning(f"API key not found for scheme: {scheme}")
            # Don't raise error - will fail when trying to make request
            api_key = ""
        
        super().__init__(base_url, api_key)
        self.scheme = scheme
        
        logger.info(f"IPN API initialized for {scheme.upper()} scheme")
        logger.debug(f"Base URL: {base_url}")
    
    @allure.step("Send transaction notification")
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
        endpoint = ""  # Base URL already includes /notify
        
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
                logger.info(f" {self.scheme.upper()} transaction successful: {amount}")
                return response
            else:
                error_msg = f"{self.scheme.upper()} transaction failed: {response}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f" {self.scheme.upper()} transaction failed: {str(e)}")
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
        nchl_client = IPNAPI(scheme="nchl", api_key=self.api_key if self.scheme == 'nchl' else None)
        
        return nchl_client.send_transaction(
            amount=amount,
            store_id=store_id,
            terminal_id=terminal_id,
            merchant_code=merchant_code
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
        fonepay_client = IPNAPI(scheme="fonepay", api_key=self.api_key if self.scheme == 'fonepay' else None)
        
        return fonepay_client.send_transaction(
            amount=amount,
            merchant_id=merchant_id,
            terminal_id=terminal_id
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
        
        # Remove None values
        return {k: v for k, v in payload.items() if v is not None}
    
    @allure.step("Verify transaction parameters")
    def verify_transaction_parameters(
        self,
        amount: str,
        merchant_code: str = None,
        merchant_id: str = None,
        store_id: str = None,
        terminal_id: str = None
    ) -> bool:
        """
        Verify transaction parameters before sending
        
        Returns:
            bool: True if parameters are valid
        """
        errors = []
        
        # Validate amount
        if not amount or not isinstance(amount, str):
            errors.append("Amount must be a non-empty string")
        elif not amount.isdigit():
            errors.append("Amount must contain only digits")
        elif int(amount) <= 0:
            errors.append("Amount must be positive")
        
        # Validate scheme-specific parameters
        if self.scheme == "nchl":
            if not store_id:
                errors.append("Store ID is required for NCHL transactions")
            if not terminal_id:
                errors.append("Terminal ID is required for NCHL transactions")
            if not merchant_code:
                errors.append("Merchant code is required for NCHL transactions")
        elif self.scheme == "fonepay":
            if not merchant_id:
                errors.append("Merchant ID is required for Fonepay transactions")
            if not terminal_id:
                errors.append("Terminal ID is required for Fonepay transactions")
        
        if errors:
            logger.error(f"Transaction parameter validation failed: {', '.join(errors)}")
            return False
        
        logger.info(f" Transaction parameters validated for {self.scheme.upper()}")
        return True
    
    @allure.step("Verify IPN API health")
    def health_check(self) -> bool:
        """Check if IPN API is accessible"""
        try:
            # Try a simple endpoint or base URL
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code < 500
        except:
            return False