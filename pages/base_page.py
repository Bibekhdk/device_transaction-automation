"""
Base Page Object Model for all page classes
"""
import allure
import logging
from playwright.sync_api import Page
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logger
        self.default_timeout = 30000
    
    # ==================== COMMON ACTIONS ====================
    def navigate(self, url: str, timeout: int = None) -> None:
        """Navigate to URL"""
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url, timeout=timeout or self.default_timeout)
    
    def click(self, selector: str, element_name: str = "") -> None:
        """Click on element"""
        self.logger.info(f"Clicking on {element_name or selector}")
        self.page.click(selector)
    
    def fill(self, selector: str, text: str, element_name: str = "") -> None:
        """Fill input field"""
        self.logger.info(f"Filling {element_name or selector}: {text}")
        self.page.fill(selector, text)
    
    def select_option(self, selector: str, value: str, element_name: str = "") -> None:
        """Select option from dropdown"""
        self.logger.info(f"Selecting {value} in {element_name or selector}")
        self.page.select_option(selector, value)
    
    def wait_for_element(self, selector: str, element_name: str = "", timeout: int = None) -> None:
        """Wait for element to be present"""
        self.logger.info(f"Waiting for {element_name or selector}")
        self.page.wait_for_selector(selector, timeout=timeout or self.default_timeout)
    
    def is_element_present(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is present"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout, state="attached")
            return True
        except:
            return False
    
    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            return True
        except:
            return False
    
    # ==================== UTILITY METHODS ====================
    def take_screenshot(self, name: str) -> None:
        """Take screenshot and attach to allure"""
        screenshot = self.page.screenshot()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    
    def refresh_page(self) -> None:
        """Refresh current page"""
        self.logger.info("Refreshing page")
        self.page.reload()
    
    def get_element_text(self, selector: str, timeout: int = 5000) -> str:
        """Get text content of element"""
        try:
            return self.page.locator(selector).first.text_content(timeout=timeout)
        except:
            return ""
    
    def wait_for_element_to_disappear(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to disappear"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout, state="detached")
            return True
        except:
            return False
    
    @allure.step("Wait for {seconds} seconds")
    def wait(self, seconds: int) -> None:
        """Wait for specified seconds"""
        time.sleep(seconds)