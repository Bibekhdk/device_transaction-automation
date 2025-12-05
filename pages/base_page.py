# pages/base_page.py
from playwright.sync_api import Page, Locator, expect
import logging
import allure
import time
import os
from datetime import datetime
from typing import Optional 

logger = logging.getLogger(__name__)

class BasePage:
    """Base page class with common methods"""
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000  # 30 seconds default timeout
        self.screenshot_dir = "reports/screenshots"
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def take_screenshot(self, name: str = None) -> str:
        """Take screenshot and return file path"""
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}.png"
        
        screenshot_path = os.path.join(self.screenshot_dir, name)
        self.page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Attach to Allure report
        allure.attach.file(
            screenshot_path,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        
        return screenshot_path
    
    @allure.step("Navigate to {url}")
    def navigate(self, url: str):
        """Navigate to URL"""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="networkidle")
    
    @allure.step("Click element: {selector}")
    def click(self, selector: str, timeout: int = None):
        """Click element by selector"""
        timeout = timeout or self.timeout
        logger.debug(f"Clicking: {selector}")
        self.page.click(selector, timeout=timeout)
    
    @allure.step("Fill {selector} with {value}")
    def fill(self, selector: str, value: str, timeout: int = None):
        """Fill input field"""
        timeout = timeout or self.timeout
        logger.debug(f"Filling {selector} with: {value}")
        self.page.fill(selector, value, timeout=timeout)
    
    @allure.step("Select option {value} from {selector}")
    def select_option(self, selector: str, value: str, timeout: int = None):
        """Select option from dropdown"""
        timeout = timeout or self.timeout
        logger.debug(f"Selecting {value} from {selector}")
        self.page.select_option(selector, value, timeout=timeout)
    
    @allure.step("Wait for element: {selector}")
    def wait_for_element(self, selector: str, timeout: int = None) -> Locator:
        """Wait for element to be visible"""
        timeout = timeout or self.timeout
        logger.debug(f"Waiting for element: {selector}")
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=timeout)
        return element
    
    @allure.step("Get text from element: {selector}")
    def get_text(self, selector: str, timeout: int = None) -> str:
        """Get text from element"""
        element = self.wait_for_element(selector, timeout)
        text = element.inner_text()
        logger.debug(f"Got text from {selector}: {text}")
        return text
    
    @allure.step("Verify element contains text: {text}")
    def verify_text_contains(self, selector: str, text: str, timeout: int = None):
        """Verify element contains text"""
        element = self.wait_for_element(selector, timeout)
        expect(element).to_contain_text(text)
        logger.info(f"Verified {selector} contains: {text}")
    
    def is_element_visible(self, selector: str, timeout: int = None) -> bool:
        """Check if element is visible"""
        try:
            self.wait_for_element(selector, timeout)
            return True
        except:
            return False
    
    @allure.step("Wait for {seconds} seconds")
    def wait(self, seconds: int):
        """Explicit wait"""
        logger.debug(f"Waiting for {seconds} seconds")
        time.sleep(seconds)