"""
Device Registration Page - Refactored to Pro QA Standards
Inherits from BasePage and uses extracted Locators
"""
import allure
import logging
import random
import time
import os
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.admin_portal.locators import AdminLocators

logger = logging.getLogger(__name__)

class DeviceRegistrationPage(BasePage):
    """Page Object for device registration"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = AdminLocators

        # Device serial no hardcoded
        self.test_serial_number = "38231105740018"  # Your hardcoded serial
    
    # ==================== DATA GENERATION ====================
    def generate_random_sim(self):
        """Generate random SIM number"""
        return str(random.randint(1000000000, 9999999999))
    
    def generate_random_imei(self):
        """Generate 15-digit IMEI"""
        imei_base = ''.join(str(random.randint(0, 9)) for _ in range(14))
        total = 0
        for i, digit in enumerate(imei_base):
            num = int(digit)
            if i % 2 == 0:
                total += num
            else:
                doubled = num * 2
                total += doubled if doubled < 10 else doubled - 9
        check_digit = (10 - (total % 10)) % 10
        return imei_base + str(check_digit)

    # ==================== ACTIONS ====================
    
    @allure.step("Login to Admin Portal")
    def login(self):
        """Login to admin portal"""
        try:
            self.navigate("https://admin-staging.koilifin.com/")
            
            email = os.getenv("ADMIN_PORTAL_EMAIL")
            password = os.getenv("ADMIN_PORTAL_PASSWORD")
            
            if not email or not password:
                raise ValueError("Admin Portal credentials not found in environment variables")
                
            self.fill_by_role(**self.locators.LOGIN_EMAIL, text=email)
            self.fill_by_role(**self.locators.LOGIN_PASSWORD, text=password)
            self.click_by_role(**self.locators.LOGIN_BUTTON)
            
            self.wait(5)
            
            # Use BasePage verification logic? Or custom?
            # Custom logic from before was robust, let's adapt it using BasePage methods
            try:
                self.wait_for_element(f"div:has-text('{self.locators.LOGIN_VERIFY_TEXT}')", timeout=15000)
                self.logger.info("Login verified")
            except:
                if "admin" in self.get_current_url().lower():
                    self.logger.info("Login verified via URL")
                else:
                    raise Exception("Login failed")
            
            self.take_screenshot("login_success")
            return True
        except Exception as e:
            self.logger.error(f" Login failed: {e}")
            self.take_screenshot("login_failed")
            raise

    @allure.step("Navigate to Device Section")
    def navigate_to_device_section(self):
        self.click_by_role(**self.locators.NAV_DEVICE)
        self.wait(2)
        return True

    @allure.step("Open Add Device Form")
    def open_add_device_form(self):
        self.click_by_role(**self.locators.ADD_DEVICE_BUTTON)
        self.wait(3)
        self.take_screenshot("form_opened")
        return True

    @allure.step("Fill Device Form")
    def fill_device_form(self, customer="Test"):
        """Fill device details"""
        try:
            sim = self.generate_random_sim()
            serial = self.test_serial_number  # Use hardcoded serial instead of random
            imei = self.generate_random_imei()
            
            logger.info(f"Using hardcoded serial: {serial}")
            
            # Fill SIM
            self.fill_by_role(**self.locators.FORM_SIM, text=sim)
            self.wait(0.5)
            
            # Select Model
            self.click_by_role(**self.locators.FORM_MODEL_DROPDOWN)
            self.click_by_role(**self.locators.FORM_MODEL_OPTION)
            self.wait(0.5)
            
            # Select Customer
            self.page.get_by_role(**self.locators.FORM_CUSTOMER_DROPDOWN).click()
            self.wait(0.5)

            # Choose customer - comment/uncomment as needed
            if customer == "TMS Staging":
                self.page.get_by_role(**self.locators.FORM_CUSTOMER_TEST).click()
            else:
                self.page.get_by_role(**self.locators.FORM_CUSTOMER_BITSKRAFT).click()
            self.wait(0.5)

            # Select Language
            self.click_by_role(**self.locators.FORM_LANGUAGE_DROPDOWN)
            self.click_by_role(**self.locators.FORM_LANGUAGE_OPTION)
            self.wait(0.5)
            
            # Fill identifiers
            self.fill_by_role(**self.locators.FORM_SERIAL, text=serial)
            self.wait(0.5)
            self.fill_by_role(**self.locators.FORM_IMEI, text=imei)
            self.wait(0.5)
            self.fill_by_role(**self.locators.FORM_BATCH, text="testautomation")
            
            self.take_screenshot("form_filled")
            
            return {
                "sim": sim,
                "serial": serial,
                "imei": imei,
                "customer": customer,
                "batch": "testautomation"
            }
        except Exception as e:
            self.logger.error(f"Failed to fill form: {e}")
            self.take_screenshot("fill_form_failed")
            raise

    @allure.step("Complete Device Registration with Toast Capture")
    def complete_registration_with_toast(self, customer="Test"):
        """Orchestrate the flow"""
        self.logger.info(f" Starting complete registration for: {customer}")
        
        result = {
            "overall_success": False,
            "steps": {},
            "device_data": {},
            "toast_result": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Login
            result["steps"]["login"] = self.login()
            
            # Navigate
            result["steps"]["navigate_to_device"] = self.navigate_to_device_section()
            
            # Open Form
            result["steps"]["open_form"] = self.open_add_device_form()
            
            # Fill Form
            device_data = self.fill_device_form(customer)
            result["device_data"] = device_data
            result["steps"]["fill_form"] = True
            
            # Submit
            self.click_by_role(**self.locators.FORM_SUBMIT_BUTTON)
            result["steps"]["submit_form"] = True
            
            # Handle Confirm (Optional)
            if self.is_element_visible(self.locators.FORM_CONFIRM_BUTTON, timeout=2000):
                 self.click(self.locators.FORM_CONFIRM_BUTTON)
                 self.wait(2)
            
            # Wait for Toast (Admin uses Toastify)
            toast_result = self.capture_admin_toast(expected_text=self.locators.TOAST_DEVICE_ADDED)
            result["toast_result"] = toast_result
            
            # Validation
            success = (
                all(result["steps"].values()) and 
                toast_result["success"] and 
                toast_result.get("contains_expected")
            )
            result["overall_success"] = success
            
            if success:
                self.logger.info(f" Registration Successful: {device_data['serial']}")
            else:
                self.logger.warning(" Registration completed with issues")
                
            return result
            
        except Exception as e:
            self.logger.error(f" Registration Failed: {e}")
            result["error"] = str(e)
            self.take_screenshot("registration_failed")
            return result