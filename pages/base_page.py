"""
Universal Base Page Object Model for all applications
Supports both Admin Portal and TMS Portal
"""
import allure
import logging
from playwright.sync_api import Page, TimeoutError, Locator
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class BasePage:
    """Base class for all page objects - Works for both Admin and TMS"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logger
        self.default_timeout = 30000
        self._is_closed = False
    
    def _check_page_alive(self):
        """Check if page is still usable"""
        if self._is_closed:
            raise Exception("Page has been closed")
        try:
            # Quick check if page is still responsive
            self.page.title()
        except Exception as e:
            self._is_closed = True
            raise Exception(f"Page is no longer usable: {str(e)}")
    
    # ==================== TOAST/ALERT HANDLING METHODS ====================
    
    def capture_toast_message(self, expected_text: str = None, timeout: int = 10000):
        """
        Universal toast message capture for both Admin and TMS portals
        Returns dict with toast details
        """
        self._check_page_alive()
        self.logger.info(f"Waiting for toast message (timeout: {timeout}ms)")
        
        start_time = time.time()
        
        try:
            # Try multiple toast selectors (Admin Toastify, TMS Material-UI, etc.)
            toast_selectors = [
                ".Toastify__toast",  # Admin Portal (Toastify)
                ".Toastify__toast--success",  # Admin success toast
                ".Toastify__toast-container",  # Admin toast container
                "[role='alert']",  # TMS Portal (Material-UI alert)
                "[data-testid^='toast-']",  # User suggested TestID pattern (e.g. toast-profile-updated)
                ".MuiSnackbar-root",  # TMS (Material-UI snackbar)
                ".MuiAlert-root",  # TMS (Material-UI alert)
                ".ant-message",  # Ant Design
                "div[class*='toast']",  # Generic toast
                "div[class*='snackbar']",  # Generic snackbar
                "div[class*='message']",  # Generic message
            ]
            
            for selector in toast_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=2000, state="visible")
                    toast = self.page.locator(selector)
                    toast_text = toast.text_content(timeout=1000) or ""
                    
                    elapsed_time = int((time.time() - start_time) * 1000)
                    
                    toast_details = {
                        "success": True,
                        "text": toast_text.strip(),
                        "selector": selector,
                        "contains_expected": expected_text.lower() in toast_text.lower() if expected_text else True,
                        "expected_text": expected_text,
                        "wait_time_ms": elapsed_time,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.logger.info(f"Toast captured: '{toast_text.strip()}'")
                    self.take_screenshot(f"toast_{int(time.time())}")
                    
                    return toast_details
                    
                except:
                    continue
            
            # If no toast found with selectors, check for any success/alert text
            try:
                success_texts = ["success", "Success", "created", "assigned", "added", "updated", "device", "merchant", "ipn"]
                for text in success_texts:
                    element = self.page.get_by_text(text, exact=False)
                    if element.is_visible(timeout=1000):
                        element_text = element.text_content() or ""
                        elapsed_time = int((time.time() - start_time) * 1000)
                        
                        toast_details = {
                            "success": True,
                            "text": element_text.strip(),
                            "selector": f"text containing '{text}'",
                            "contains_expected": expected_text.lower() in element_text.lower() if expected_text else True,
                            "expected_text": expected_text,
                            "wait_time_ms": elapsed_time,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        self.logger.info(f" Success message found: '{element_text.strip()}'")
                        return toast_details
            except:
                pass
            
            raise Exception("No toast message found within timeout")
            
        except Exception as e:
            elapsed_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Failed to capture toast: {e} (waited {elapsed_time}ms)")
            
            return {
                "success": False,
                "error": str(e),
                "wait_time_ms": elapsed_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def verify_toast_message(self, expected_text: str, timeout: int = 10000):
        """
        Verify specific toast message appears
        Returns toast details if successful
        """
        toast_result = self.capture_toast_message(expected_text, timeout)
        
        if toast_result["success"] and toast_result.get("contains_expected"):
            self.logger.info(f"Toast verified: '{toast_result['text']}'")
            return toast_result
        else:
            self.logger.warning(f" Toast verification failed. Expected: '{expected_text}', Got: '{toast_result.get('text', 'NO TEXT')}'")
            return toast_result
    
    def wait_for_toast_and_capture(self, expected_text: str = None, timeout: int = 15000):
        """
        Wait for toast message, capture details, and take screenshot
        Enhanced version for better toast handling
        """
        self._check_page_alive()
        self.logger.info(f"Waiting for toast with text: '{expected_text}'")
        
        start_time = time.time()
        
        try:
            # First wait a bit for toast to appear
            self.wait(2)
            
            # Try to capture toast
            toast_result = self.capture_toast_message(expected_text, timeout)
            
            if toast_result["success"]:
                # Additional verification for specific applications
                if "Toastify" in toast_result.get("selector", ""):
                    self.logger.info("🔹 Admin Portal Toastify toast detected")
                elif "Mui" in toast_result.get("selector", ""):
                    self.logger.info("🔹 TMS Portal Material-UI toast detected")
                
                return toast_result
            else:
                raise Exception(f"Toast capture failed: {toast_result.get('error', 'Unknown')}")
                
        except Exception as e:
            elapsed_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Failed to capture toast: {e} (waited {elapsed_time}ms)")
            
            return {
                "success": False,
                "error": str(e),
                "wait_time_ms": elapsed_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    # ==================== CODE-GEN STYLE LOCATOR METHODS ====================
    
    def locate_by_role(self, role: str, name: str = None, exact: bool = False) -> Locator:
        """Get element by role (Codegen style)"""
        self._check_page_alive()
        if name:
            return self.page.get_by_role(role, name=name, exact=exact)
        return self.page.get_by_role(role)
    
    def locate_by_text(self, text: str, exact: bool = False) -> Locator:
        """Get element by text (Codegen style)"""
        self._check_page_alive()
        return self.page.get_by_text(text, exact=exact)
    
    def locate_by_placeholder(self, placeholder: str, exact: bool = False) -> Locator:
        """Get element by placeholder (Codegen style)"""
        self._check_page_alive()
        return self.page.get_by_placeholder(placeholder, exact=exact)
    
    def locate_by_label(self, label: str) -> Locator:
        """Get element by label (Codegen style)"""
        self._check_page_alive()
        return self.page.get_by_label(label)
    
    def locate_by_test_id(self, test_id: str) -> Locator:
        """Get element by test id (Codegen style)"""
        self._check_page_alive()
        return self.page.get_by_test_id(test_id)
    
    # ==================== CODE-GEN STYLE ACTION METHODS ====================
    
    def click_by_role(self, role: str, name: str = None, element_name: str = "", 
                     exact: bool = False, timeout: int = None) -> None:
        """Click element by role (Codegen style)"""
        self._check_page_alive()
        element_name = element_name or f"{role} {name or ''}"
        self.logger.info(f"Clicking on {element_name}")
        try:
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.click()
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to click {element_name}: {e}")
            raise
    
    def fill_by_role(self, role: str, name: str = None, text: str = "", 
                    element_name: str = "", exact: bool = False, 
                    timeout: int = None) -> None:
        """Fill element by role (Codegen style)"""
        self._check_page_alive()
        element_name = element_name or f"{role} {name or ''}"
        self.logger.info(f"Filling {element_name}: {text}")
        try:
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.fill(text)
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to fill {element_name}: {e}")
            raise
    
    def select_option_by_role(self, role: str, name: str = None, value: str = "",
                            element_name: str = "", exact: bool = False,
                            timeout: int = None) -> None:
        """Select option by role (Codegen style)"""
        self._check_page_alive()
        element_name = element_name or f"{role} {name or ''}"
        self.logger.info(f"Selecting {value} in {element_name}")
        try:
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.select_option(value)
        except Exception as e:
            self.logger.error(f"Failed to select option {value} in {element_name}: {e}")
            raise
    
    def click_by_text(self, text: str, element_name: str = "", exact: bool = False,
                     timeout: int = None) -> None:
        """Click element by text (Codegen style)"""
        self._check_page_alive()
        element_name = element_name or text
        self.logger.info(f"Clicking on text: {element_name}")
        try:
            locator = self.locate_by_text(text, exact)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.click()
        except TimeoutError:
            self.logger.error(f"Timeout waiting for text element: {element_name}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to click text element {element_name}: {e}")
            raise
    
    # ==================== ORIGINAL CSS SELECTOR METHODS (Backward Compatible) ====================
    
    def navigate(self, url: str, timeout: int = None) -> None:
        """Navigate to URL"""
        self._check_page_alive()
        self.logger.info(f"Navigating to: {url}")
        try:
            self.page.goto(url, timeout=timeout or self.default_timeout,
                          wait_until="networkidle")
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    def click(self, selector: str, element_name: str = "", timeout: int = None) -> None:
        """Click on element by CSS selector"""
        self._check_page_alive()
        self.logger.info(f"Clicking on {element_name or selector}")
        try:
            element = self.page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout or self.default_timeout)
            element.click()
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name or selector}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to click {element_name or selector}: {e}")
            raise
    
    def fill(self, selector: str, text: str, element_name: str = "", timeout: int = None) -> None:
        """Fill input field by CSS selector"""
        self._check_page_alive()
        self.logger.info(f"Filling {element_name or selector}: {text}")
        try:
            element = self.page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout or self.default_timeout)
            element.fill(text)
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name or selector}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to fill {element_name or selector}: {e}")
            raise
    
    def select_option(self, selector: str, value: str, element_name: str = "", timeout: int = None) -> None:
        """Select option from dropdown by CSS selector"""
        self._check_page_alive()
        self.logger.info(f"Selecting {value} in {element_name or selector}")
        try:
            element = self.page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout or self.default_timeout)
            self.page.select_option(selector, value)
        except Exception as e:
            self.logger.error(f"Failed to select option {value}: {e}")
            raise
    
    # ==================== UTILITY METHODS ====================
    
    def wait_for_element_by_role(self, role: str, name: str = None, element_name: str = "", 
                                timeout: int = None, state: str = "visible", exact: bool = False) -> None:
        """Wait for element by role"""
        self._check_page_alive()
        element_name = element_name or f"{role} {name or ''}"
        self.logger.info(f"Waiting for {element_name} (state: {state})")
        try:
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state=state, timeout=timeout or self.default_timeout)
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name}")
            raise
    
    def wait_for_element(self, selector: str, element_name: str = "", timeout: int = None, state: str = "visible") -> None:
        """Wait for element by CSS selector"""
        self._check_page_alive()
        self.logger.info(f"Waiting for {element_name or selector} (state: {state})")
        try:
            self.page.wait_for_selector(selector, timeout=timeout or self.default_timeout, state=state)
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: {element_name or selector}")
            raise
    
    def is_element_present_by_role(self, role: str, name: str = None, timeout: int = 5000, exact: bool = False) -> bool:
        """Check if element by role is present"""
        try:
            self._check_page_alive()
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state="attached", timeout=timeout)
            return True
        except:
            return False
    
    def is_element_visible_by_role(self, role: str, name: str = None, timeout: int = 5000, exact: bool = False) -> bool:
        """Check if element by role is visible"""
        try:
            self._check_page_alive()
            locator = self.locate_by_role(role, name, exact)
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def is_element_present(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is present by CSS selector"""
        try:
            self._check_page_alive()
            self.page.wait_for_selector(selector, timeout=timeout, state="attached")
            return True
        except:
            return False
    
    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible by CSS selector"""
        try:
            self._check_page_alive()
            self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            return True
        except:
            return False
    
    def get_element_text_by_role(self, role: str, name: str = None, timeout: int = 5000, exact: bool = False) -> str:
        """Get text content of element by role"""
        try:
            self._check_page_alive()
            locator = self.locate_by_role(role, name, exact)
            return locator.text_content(timeout=timeout) or ""
        except:
            return ""
    
    def get_element_text(self, selector: str, timeout: int = 5000) -> str:
        """Get text content of element by CSS selector"""
        try:
            self._check_page_alive()
            return self.page.locator(selector).first.text_content(timeout=timeout) or ""
        except:
            return ""
    
    # ==================== COMMON UTILITY METHODS ====================
    
    def take_screenshot(self, name: str) -> None:
        """Take screenshot and attach to allure"""
        try:
            self._check_page_alive()
            screenshot = self.page.screenshot(full_page=True)
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
            self.logger.info(f"Screenshot taken: {name}")
        except Exception as e:
            self.logger.warning(f"Could not take screenshot {name}: {e}")
    
    def refresh_page(self) -> None:
        """Refresh current page"""
        self._check_page_alive()
        self.logger.info("Refreshing page")
        self.page.reload()
    
    def wait(self, seconds: int) -> None:
        """Wait for specified seconds"""
        time.sleep(seconds)
    
    def wait_for_page_load(self, timeout: int = 30000) -> None:
        """Wait for page to load completely"""
        self._check_page_alive()
        self.logger.info("Waiting for page to load")
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        self._check_page_alive()
        return self.page.url
    
    def get_page_title(self) -> str:
        """Get page title"""
        self._check_page_alive()
        return self.page.title()
    
    # ==================== DROPDOWN HELPER METHODS ====================
    
    def select_dropdown_option_by_role(self, dropdown_role: str, dropdown_name: str = None,
                                      option_text: str = "", exact: bool = True) -> None:
        """Select dropdown option by role (Codegen style for comboboxes)"""
        self._check_page_alive()
        self.logger.info(f"Selecting dropdown option: {option_text}")
        
        # Click the dropdown to open it
        dropdown = self.locate_by_role(dropdown_role, dropdown_name, exact=False)
        dropdown.click()
        self.wait(1)
        
        # Select the option
        option = self.locate_by_role("option", option_text, exact=exact)
        option.click()
        self.wait(0.5)
    
    def click_locator(self, locator: Locator, element_name: str = "", timeout: int = None) -> None:
        """Click a pre-located element"""
        self._check_page_alive()
        element_name = element_name or "element"
        self.logger.info(f"Clicking on {element_name}")
        try:
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.click()
        except Exception as e:
            self.logger.error(f"Failed to click {element_name}: {e}")
            raise
    
    def fill_locator(self, locator: Locator, text: str, element_name: str = "", timeout: int = None) -> None:
        """Fill a pre-located element"""
        self._check_page_alive()
        element_name = element_name or "element"
        self.logger.info(f"Filling {element_name}: {text}")
        try:
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.fill(text)
        except Exception as e:
            self.logger.error(f"Failed to fill {element_name}: {e}")
            raise
    
    # ==================== DEBUG METHODS ====================
    
    def debug_screenshot(self, prefix: str = "debug") -> None:
        """Take debug screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./debug/{prefix}_{timestamp}.png"
        try:
            self._check_page_alive()
            self.page.screenshot(path=filename, full_page=True)
            self.logger.info(f"Debug screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save debug screenshot: {e}")
    
    def log_page_info(self) -> None:
        """Log current page information"""
        try:
            self._check_page_alive()
            self.logger.info(f"Current URL: {self.page.url}")
            self.logger.info(f"Page Title: {self.page.title()}")
            self.logger.info(f"Total frames: {len(self.page.frames)}")
        except Exception as e:
            self.logger.error(f"Could not get page info: {e}")
    
    # ==================== APPLICATION-SPECIFIC TOAST METHODS ====================
    
    def capture_admin_toast(self, expected_text: str = "device added", timeout: int = 15000):
        """
        Specifically for Admin Portal toast messages (Toastify)
        """
        self.logger.info(f"Waiting for Admin Portal toast: '{expected_text}'")
        
        try:
            # Admin uses Toastify - wait for specific container
            self.page.locator(".Toastify__toast-container").wait_for(
                state="visible", timeout=timeout
            )
            
            # Get success toast specifically
            toast = self.page.locator(".Toastify__toast--success")
            toast.wait_for(state="visible", timeout=timeout)
            
            toast_text = toast.text_content(timeout=2000) or ""
            
            result = {
                "success": True,
                "text": toast_text.strip(),
                "contains_expected": expected_text.lower() in toast_text.lower(),
                "app_type": "admin",
                "toast_type": "Toastify"
            }
            
            self.logger.info(f" Admin toast captured: '{toast_text.strip()}'")
            return result
            
        except Exception as e:
            self.logger.error(f" Failed to capture Admin toast: {e}")
            return {"success": False, "error": str(e), "app_type": "admin"}
    
    def capture_tms_toast(self, expected_text: str = None, timeout: int = 15000):
        """
        Specifically for TMS Portal toast messages - Delegates to universal capture
        because TMS might use Alerts, Snackbars, or custom TestID toasts.
        """
        self.logger.info(f"Waiting for TMS Portal toast (Robust): '{expected_text}'")
        return self.capture_toast_message(expected_text, timeout)
    
    # ==================== VALIDATION HELPER METHODS ====================
    
    def validate_result_with_toast(self, result: dict, expected_toast_keywords: list):
        """
        Validate test result with toast verification
        Returns tuple of (is_valid, validation_message)
        """
        toast_result = result.get("toast_result", {})
        
        if not result.get("success", False):
            return False, "Test execution failed"
        
        if not toast_result.get("success", False):
            return False, "Toast not captured"
        
        toast_text = toast_result.get("text", "").lower()
        
        # Check if any expected keyword is in toast text
        for keyword in expected_toast_keywords:
            if keyword.lower() in toast_text:
                return True, f"Validated with keyword: '{keyword}'"
        
        return False, f"No expected keywords found in toast. Keywords: {expected_toast_keywords}, Toast: '{toast_text}'"
    
    def generate_test_report(self, result: dict, test_name: str = "Test"):
        """
        Generate a structured test report
        """
        report = {
            "test_name": test_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_success": result.get("overall_success", False),
            "steps": result.get("steps", {}),
            "toast_verification": result.get("toast_result", {}),
            "data": result.get("data", {}),
            "error": result.get("error", None)
        }
        
        # Log report summary
        self.logger.info(f" Test Report: {test_name}")
        self.logger.info(f"   Status: {' PASSED' if report['overall_success'] else ' FAILED'}")
        
        if report.get("toast_verification", {}).get("success"):
            self.logger.info(f"   Toast: '{report['toast_verification'].get('text', '')}'")
        
        # Attach to Allure
        allure.attach(
            str(report),
            name=f"{test_name}_Report",
            attachment_type=allure.attachment_type.JSON
        )
        
        return report