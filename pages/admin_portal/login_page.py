# pages/admin_portal/login_page.py
import logging
from pages.base_page import BasePage
import allure
from typing import Optional
import os

logger = logging.getLogger(__name__)

class AdminLoginPage(BasePage):
    """Admin Portal Login Page"""
    
    # Locators
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    
    def __init__(self, page):
        super().__init__(page)
        self.url = os.getenv("ADMIN_PORTAL_URL", "https://admin-staging.koiliifn.com")
    
    @allure.step("Navigate to Admin Portal")
    def goto(self):
        """Navigate to Admin Portal"""
        self.navigate(self.url)
    
    @allure.step("Login to Admin Portal")
    def login(self, username: str = None, password: str = None):
        """
        Login to Admin Portal
        
        Args:
            username: Admin username (defaults from env)
            password: Admin password (defaults from env)
        """
        # Get credentials from environment if not provided
        if not username:
            username = os.getenv("ADMIN_USERNAME")
        if not password:
            password = os.getenv("ADMIN_PASSWORD")
        
        if not username or not password:
            raise ValueError("Admin credentials not provided or found in environment")
        
        logger.info(f"Logging in as: {username}")
        
        # Navigate to portal
        self.goto()
        
        # Fill credentials
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        
        # Click login
        self.click(self.LOGIN_BUTTON)
        
        # Wait for navigation/loading
        self.page.wait_for_load_state("networkidle")
        
        # Verify login success (you might need to adjust this based on actual portal)
        if self.is_login_successful():
            logger.info("✅ Admin login successful")
        else:
            error_msg = "❌ Admin login failed"
            self.take_screenshot("admin_login_failed.png")
            raise Exception(error_msg)
    
    def is_login_successful(self) -> bool:
        """Check if login was successful"""
        # Adjust this based on actual portal behavior
        # Could check for dashboard elements, user menu, etc.
        try:
            # Check for dashboard or any element that appears after login
            dashboard_elements = [
                "div.dashboard",
                "nav.main-nav",
                "a[href*='dashboard']",
                "text=Welcome"
            ]
            
            for element in dashboard_elements:
                if self.is_element_visible(element, timeout=10000):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    @allure.step("Get login error message")
    def get_error_message(self) -> Optional[str]:
        """Get error message if login failed"""
        try:
            if self.is_element_visible(self.ERROR_MESSAGE, timeout=5000):
                return self.get_text(self.ERROR_MESSAGE)
        except:
            pass
        return None