# utils/toast_handler.py
import logging
import allure
from playwright.sync_api import Page, TimeoutError
from datetime import datetime
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class ToastHandler:
    """
    Advanced toast notification handler for TMS portal.
    Uses multiple capture strategies for fast-disappearing toasts.
    """
    
    # Toast selectors based on your portal
    TOAST_SELECTOR = "[role='alert']"
    TOAST_TEXT_SELECTOR = "[role='alert'] span, [role='alert'] div"
    
    def __init__(self, page: Page):
        self.page = page
        self.captured_toasts = []
        
    def _take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        return screenshot
    
    @allure.step("Capture toast notification")
    def capture_toast(self, 
                     expected_text: Optional[str] = None,
                     timeout_ms: int = 5000,
                     must_contain: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Capture toast with multiple strategies.
        
        Args:
            expected_text: Text to expect in toast (None = capture any toast)
            timeout_ms: Maximum time to wait for toast
            must_contain: If True, expected_text must be contained in toast
        
        Returns:
            Tuple of (success: bool, captured_text: Optional[str])
        """
        try:
            logger.info(f"Waiting for toast (timeout: {timeout_ms}ms)")
            
            # Strategy 1: Wait for toast to appear
            self.page.wait_for_selector(
                self.TOAST_SELECTOR,
                state="attached",
                timeout=timeout_ms
            )
            
            # Strategy 2: Get all toast elements
            toast_elements = self.page.locator(self.TOAST_SELECTOR)
            count = toast_elements.count()
            
            if count == 0:
                logger.warning("Toast selector found but no elements")
                self._take_screenshot("toast_missing")
                return False, None
            
            # Capture text from all toasts
            captured_texts = []
            for i in range(count):
                try:
                    element = toast_elements.nth(i)
                    text = element.text_content(timeout=2000)
                    if text:
                        text = text.strip()
                        captured_texts.append(text)
                        logger.info(f"Captured toast {i+1}: '{text}'")
                except Exception as e:
                    logger.debug(f"Could not get text from toast {i+1}: {e}")
            
            if not captured_texts:
                logger.warning("No text captured from toast elements")
                self._take_screenshot("toast_no_text")
                return False, None
            
            # Join all captured texts
            full_text = " | ".join(captured_texts)
            self.captured_toasts.append({
                "timestamp": datetime.now().isoformat(),
                "text": full_text,
                "screenshot": self._take_screenshot(f"toast_{len(self.captured_toasts)}")
            })
            
            # Validate if expected text provided
            if expected_text:
                if must_contain:
                    success = expected_text in full_text
                else:
                    success = expected_text == full_text
                
                if success:
                    logger.info(f"Toast validation passed: Found '{expected_text}' in '{full_text}'")
                else:
                    logger.error(f"Toast validation failed: Expected '{expected_text}', got '{full_text}'")
                
                return success, full_text
            
            return True, full_text
            
        except TimeoutError:
            logger.warning(f"Toast did not appear within {timeout_ms}ms")
            self._take_screenshot("toast_timeout")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error capturing toast: {e}")
            self._take_screenshot("toast_error")
            return False, None
    
    @allure.step("Wait for success toast")
    def wait_for_success_toast(self, 
                              success_text: str = "successfully",
                              timeout_ms: int = 10000) -> bool:
        """Wait for a success toast containing specific text"""
        success, text = self.capture_toast(
            expected_text=success_text,
            timeout_ms=timeout_ms,
            must_contain=True
        )
        
        if success:
            allure.attach(
                text or "Success toast captured",
                name="Success Toast",
                attachment_type=allure.attachment_type.TEXT
            )
        
        return success
    
    def get_captured_toasts(self):
        """Get all captured toasts in this session"""
        return self.captured_toasts.copy()