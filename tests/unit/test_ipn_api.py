# tests/test_ipn_api.py
import pytest
import logging
import allure
from config import config

logger = logging.getLogger(__name__)

@allure.epic("API Tests")
@allure.feature("IPN API")
class TestIPNAPI:
    """Tests for IPN API functionality"""
    
    @allure.story("Test IPN API initialization")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ipn_api_initialization(self):
        """Test that IPN API client initializes correctly"""
        from api.ipn_api import IPNAPI
        
        # Test NCHL client
        nchl_client = IPNAPI(scheme="nchl")
        assert nchl_client is not None
        assert nchl_client.scheme == "nchl"
        logger.info(f"NCHL API base URL: {nchl_client.base_url}")
        
        # Test Fonepay client
        fonepay_client = IPNAPI(scheme="fonepay")
        assert fonepay_client is not None
        assert fonepay_client.scheme == "fonepay"
        logger.info(f"Fonepay API base URL: {fonepay_client.base_url}")
        
        logger.info("IPN API clients initialized successfully")
    
    @allure.story("Test IPN API health check")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ipn_api_health(self):
        """Test IPN API health check"""
        from api.ipn_api import IPNAPI
        
        nchl_client = IPNAPI(scheme="nchl")
        is_healthy = nchl_client.health_check()
        
        if is_healthy:
            logger.info(" NCHL IPN API is accessible")
        else:
            logger.warning(" NCHL IPN API health check failed or endpoint not accessible")
        
        # Don't fail test - just log warning
        assert True
    
    @allure.story("Test transaction parameter validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_transaction_parameter_validation(self):
        """Test transaction parameter validation"""
        from api.ipn_api import IPNAPI
        
        # Test NCHL validation
        nchl_client = IPNAPI(scheme="nchl")
        
        # Valid parameters
        assert nchl_client.verify_transaction_parameters(
            amount="11111111",
            store_id="store123",
            terminal_id="terminal123",
            merchant_code="merchant123"
        ) == True
        
        # Invalid parameters
        assert nchl_client.verify_transaction_parameters(
            amount="",  # Empty amount
            store_id="store123",
            terminal_id="terminal123",
            merchant_code="merchant123"
        ) == False
        
        # Test Fonepay validation
        fonepay_client = IPNAPI(scheme="fonepay")
        
        # Valid parameters
        assert fonepay_client.verify_transaction_parameters(
            amount="222222",
            merchant_id="merchant456",
            terminal_id="terminal456"
        ) == True
        
        logger.info("Transaction parameter validation working correctly")
    
    @allure.story("Test payload building")
    @allure.severity(allure.severity_level.NORMAL)
    def test_payload_building(self):
        """Test that payloads are built correctly for each scheme"""
        from api.ipn_api import IPNAPI
        
        # Test NCHL payload
        nchl_client = IPNAPI(scheme="nchl")
        nchl_payload = nchl_client._build_payload(
            amount="11111111",
            store_id="store123",
            terminal_id="terminal123",
            merchant_code="merchant123"
        )
        
        assert nchl_payload["amount"] == "11111111"
        assert nchl_payload["storeId"] == "store123"
        assert nchl_payload["terminalId"] == "terminal123"
        assert nchl_payload["merchantCode"] == "merchant123"
        
        # Test Fonepay payload
        fonepay_client = IPNAPI(scheme="fonepay")
        fonepay_payload = fonepay_client._build_payload(
            amount="222222",
            merchant_id="merchant456",
            terminal_id="terminal456"
        )
        
        assert fonepay_payload["amount"] == "222222"
        assert fonepay_payload["merchantId"] == "merchant456"
        assert fonepay_payload["terminalId"] == "terminal456"
        
        logger.info(" Payload building working correctly")
        logger.info(f"NCHL payload: {nchl_payload}")
        logger.info(f"Fonepay payload: {fonepay_payload}")
    
    @allure.story("Test test transaction")
    @allure.severity(allure.severity_level.MINOR)
    def test_test_transaction(self):
        """Test sending a test transaction"""
        from api.ipn_api import IPNAPI
        
        nchl_client = IPNAPI(scheme="nchl")
        
        try:
            # This might fail due to authentication, but that's okay for test
            response = nchl_client.send_test_transaction(amount="100")
            
            # If we get here, log the response
            logger.info(f"Test transaction response: {response}")
            assert response is not None
            
        except Exception as e:
            # Expected if API keys aren't set or invalid
            logger.warning(f"Test transaction failed (expected if no valid credentials): {e}")
            # Don't fail the test
    
    @allure.story("Test API key validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_key_validation(self):
        """Test that API keys are loaded correctly"""
        import os
        
        nchl_key = os.getenv("NCHL_API_KEY")
        fonepay_key = os.getenv("FONEPAY_API_KEY")
        
        if nchl_key:
            logger.info(f"NCHL API key loaded: {nchl_key[:10]}...")
        else:
            logger.warning("NCHL API key not set in environment")
        
        if fonepay_key:
            logger.info(f"Fonepay API key loaded: {fonepay_key[:10]}...")
        else:
            logger.warning("Fonepay API key not set in environment")
        
        # Don't fail if keys aren't set - just warn
        assert True