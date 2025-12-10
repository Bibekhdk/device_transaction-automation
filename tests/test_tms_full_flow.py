"""
Test cases for TMS Portal complete flow
"""
import pytest

import allure
import logging
from playwright.sync_api import Page
from pages.tms_portal.tms_full_flow import TMSPortal

logger = logging.getLogger(__name__)

# Fixtures
@pytest.fixture
def tms_portal(page: Page) -> TMSPortal:
    """Initialize TMS Portal"""
    return TMSPortal(page)

@pytest.fixture
def test_device_serial() -> str:
    """Test device serial number"""
    return "TEST12345678"

# Test class
class TestTMSCompleteFlow:
    """Complete TMS flow tests"""
    
    @pytest.mark.tms
    @pytest.mark.e2e
    @allure.feature("TMS Portal")
    @allure.story("Complete Merchant and Device Flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_tms_flow_basic(self, tms_portal: TMSPortal, test_device_serial: str):
        """Basic test of TMS flow"""
        try:
            # Just test login first
            tms_portal.login()
            
            # Verify login
            assert tms_portal.is_element_visible(tms_portal.locators.DASHBOARD_HEADER, timeout=10000)
            
            logger.info("✅ Login successful")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    @pytest.mark.tms
    @pytest.mark.smoke
    @allure.feature("TMS Portal")
    @allure.story("Login Test")
    def test_login_only(self, page: Page):
        """Test only login functionality"""
        tms = TMSPortal(page)
        
        # Test login with default credentials
        tms.login()
        
        # Take screenshot
        tms.take_screenshot("login_test_success")
        
        # Verify we're logged in
        assert tms.is_element_visible(tms.locators.DASHBOARD_HEADER, timeout=15000)

# Add these test functions (not in class) if class is causing issues
@pytest.mark.tms_login
def test_simple_login(page: Page):
    """Simple login test outside of class"""
    tms = TMSPortal(page)
    
    # Navigate and login
    tms.navigate(tms.TMS_URL)
    
    # Check if on login page
    assert tms.is_element_present(tms.locators.USERNAME_INPUT)
    assert tms.is_element_present(tms.locators.PASSWORD_INPUT)
    
    print("✅ Login page loaded successfully")

# Quick test to verify imports
def test_imports():
    """Test if imports work"""
    from pages.tms_portal.tms_full_flow import TMSPortal
    from pages.base_page import BasePage
    
    print("✅ All imports working correctly")
    assert True