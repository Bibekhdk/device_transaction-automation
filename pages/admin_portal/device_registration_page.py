"""
Device Registration Page - Complete Flow with Toast Capture
"""
import allure
import logging
import random
import re
import time
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class DeviceRegistrationPage:
    """Page Object for device registration with toast capture"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logger
    
    # ==================== UTILITY METHODS ====================
    def wait(self, seconds: int):
        """Simple wait"""
        time.sleep(seconds)
    
    def take_screenshot(self, name: str):
        """Take screenshot"""
        try:
            screenshot = self.page.screenshot()
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            self.logger.warning(f"Could not take screenshot: {e}")
    
    def get_current_url(self):
        """Get current URL"""
        return self.page.url
    
    # ==================== LOGIN ====================
    @allure.step("Login to Admin Portal")
    def login(self):
        """Login to admin portal"""
        self.logger.info("Logging in to admin portal")
        
        try:
            # Navigate
            self.page.goto("https://admin-staging.koilifin.com/", wait_until="networkidle")
            self.wait(2)
            
            # Fill credentials
            email_field = self.page.get_by_role("textbox", name="Email Address")
            email_field.wait_for(state="visible", timeout=10000)
            email_field.click()
            email_field.fill("anugya@koilifin.com")
            
            password_field = self.page.get_by_role("textbox", name="Password")
            password_field.wait_for(state="visible", timeout=5000)
            password_field.click()
            password_field.fill("anugya123")
            
            signin_button = self.page.get_by_role("button", name="Sign in", exact=True)
            signin_button.wait_for(state="visible", timeout=5000)
            signin_button.click()
            
            # Wait for dashboard
            self.wait(5)
            
            # Verify login - using simpler method
            try:
                # Try multiple ways to verify login
                self.page.wait_for_selector("div:has-text('Koili')", timeout=15000)
                self.logger.info("✅ Login verified - Found 'Koili' text")
            except:
                # Check if we're on admin page
                current_url = self.page.url
                if "admin" in current_url.lower():
                    self.logger.info(f"✅ Login verified - On admin page: {current_url}")
                else:
                    raise Exception(f"Not on admin page after login: {current_url}")
            
            self.take_screenshot("login_success")
            self.logger.info("✅ Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Login failed: {str(e)}")
            self.take_screenshot("login_failed")
            raise
    
    # ==================== DEVICE REGISTRATION FLOW ====================
    @allure.step("Navigate to Device Section")
    def navigate_to_device_section(self):
        """Go to device management"""
        self.logger.info("Navigating to device section")
        
        device_button = self.page.get_by_role("button", name="Device")
        device_button.wait_for(state="visible", timeout=10000)
        device_button.click()
        self.wait(2)
        return True
    
    @allure.step("Open Add Device Form")
    def open_add_device_form(self):
        """Open the add device form"""
        self.logger.info("Opening add device form")
        
        add_button = self.page.get_by_role("button", name="Add")
        add_button.wait_for(state="visible", timeout=10000)
        add_button.click()
        self.wait(3)
        self.take_screenshot("form_opened")
        return True
    
    # ==================== DATA GENERATION ====================
    def generate_random_sim(self):
        """Generate random SIM number"""
        return str(random.randint(1000000000, 9999999999))
    
    def generate_random_serial(self):
        """Generate random serial number"""
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
    
    # ==================== FORM FILLING ====================
    @allure.step("Fill Device Form")
    def fill_device_form(self, customer="Anugya"):
        """Fill the device registration form"""
        self.logger.info(f"Filling form for customer: {customer}")
        
        try:
            # Generate data
            sim = self.generate_random_sim()
            serial = self.generate_random_serial()
            imei = self.generate_random_imei()
            
            # Fill SIM
            sim_field = self.page.get_by_role("textbox", name="SIM")
            sim_field.wait_for(state="visible", timeout=10000)
            sim_field.click()
            sim_field.fill(sim)
            self.wait(0.5)
            
            # Select Model
            model_dropdown = self.page.get_by_role("combobox", name="Model")
            model_dropdown.wait_for(state="visible", timeout=5000)
            model_dropdown.click()
            
            model_option = self.page.get_by_role("option", name="ET389 static")
            model_option.wait_for(state="visible", timeout=5000)
            model_option.click()
            self.wait(0.5)
            
            # Select Customer
            customer_dropdown = self.page.locator("#select-customer")
            customer_dropdown.wait_for(state="visible", timeout=5000)
            customer_dropdown.click()
            
            if customer == "Bitskraft Pvt Ltd":
                customer_option = self.page.get_by_role("option", name="Bitskraft Pvt Ltd")
            else:
                customer_option = self.page.get_by_role("option", name="Anugya")
            
            customer_option.wait_for(state="visible", timeout=5000)
            customer_option.click()
            self.wait(0.5)
            
            # Select Language
            language_dropdown = self.page.get_by_role("combobox", name="Language")
            language_dropdown.wait_for(state="visible", timeout=5000)
            language_dropdown.click()
            
            language_option = self.page.get_by_role("option", name="English")
            language_option.wait_for(state="visible", timeout=5000)
            language_option.click()
            self.wait(0.5)
            
            # Fill Serial
            serial_field = self.page.get_by_role("textbox", name="Serial Number")
            serial_field.wait_for(state="visible", timeout=5000)
            serial_field.click()
            serial_field.fill(serial)
            self.wait(0.5)
            
            # Fill IMEI
            imei_field = self.page.get_by_role("textbox", name="IMEI")
            imei_field.wait_for(state="visible", timeout=5000)
            imei_field.click()
            imei_field.fill(imei)
            self.wait(0.5)
            
            # Fill Batch
            batch_field = self.page.get_by_role("textbox", name="Batch")
            batch_field.wait_for(state="visible", timeout=5000)
            batch_field.click()
            batch_field.fill("testautomation")
            
            self.take_screenshot("form_filled")
            
            # Return generated data for verification
            return {
                "sim": sim,
                "serial": serial,
                "imei": imei,
                "customer": customer,
                "batch": "testautomation"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fill device form: {e}")
            self.take_screenshot("fill_form_failed")
            raise
    
    # ==================== TOAST CAPTURE ====================
    @allure.step("Capture Success Toast")
    def capture_success_toast(self, timeout=15000):
        """
        Wait for and capture the 'device added' success toast
        Returns dictionary with toast details
        """
        self.logger.info("Waiting for 'device added' success toast...")
        
        start_time = time.time()
        
        try:
            # Wait for toast container (top-right position)
            self.page.locator(".Toastify__toast-container--top-right").wait_for(
                state="visible", timeout=timeout
            )
            
            # Wait for success toast specifically
            toast = self.page.locator(".Toastify__toast--success")
            toast.wait_for(state="visible", timeout=timeout)
            
            # Get the toast body text
            toast_body = toast.locator(".Toastify__toast-body")
            toast_text = toast_body.text_content(timeout=2000) or ""
            
            # Clean up the text - remove extra whitespace
            toast_text_clean = toast_text.strip()
            
            # Get toast ID
            toast_id = toast.get_attribute("id") or ""
            
            # Wait for toast to be fully visible
            self.wait(1)
            
            elapsed_time = int((time.time() - start_time) * 1000)
            
            # Check if text exactly contains "device added" (case insensitive)
            contains_exact_text = "device added" in toast_text_clean.lower()
            
            toast_details = {
                "success": True,
                "text": toast_text_clean,
                "original_text": toast_text,
                "id": toast_id,
                "contains_device_added": contains_exact_text,
                "is_exact_match": toast_text_clean.lower() == "device added",
                "wait_time_ms": elapsed_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if contains_exact_text:
                self.logger.info(f"✅ Toast captured: '{toast_text_clean}' in {elapsed_time}ms")
            else:
                self.logger.warning(f"⚠️ Toast captured but doesn't contain 'device added': '{toast_text_clean}'")
            
            self.take_screenshot(f"toast_captured")
            
            return toast_details
            
        except Exception as e:
            elapsed_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"❌ Failed to capture toast: {e} (waited {elapsed_time}ms)")
            
            return {
                "success": False,
                "error": str(e),
                "wait_time_ms": elapsed_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    # ==================== COMPLETE FLOW ====================
    @allure.step("Complete Device Registration with Toast Capture")
    def complete_registration_with_toast(self, customer="Anugya"):
        """
        Complete registration flow with toast capture
        Returns dictionary with all results
        """
        self.logger.info(f"🚀 Starting complete registration for: {customer}")
        
        result = {
            "overall_success": False,
            "steps": {},
            "device_data": {},
            "toast_result": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Step 1: Login
            self.logger.info("Step 1: Logging in...")
            result["steps"]["login"] = self.login()
            
            # Step 2: Navigate to device section
            self.logger.info("Step 2: Navigating to device section...")
            result["steps"]["navigate_to_device"] = self.navigate_to_device_section()
            
            # Step 3: Open form
            self.logger.info("Step 3: Opening add device form...")
            result["steps"]["open_form"] = self.open_add_device_form()
            
            # Step 4: Fill form and get device data
            self.logger.info("Step 4: Filling device form...")
            device_data = self.fill_device_form(customer)
            result["device_data"] = device_data
            result["steps"]["fill_form"] = True
            
            # Step 5: Submit form
            self.logger.info("Step 5: Submitting device form...")
            submit_button = self.page.get_by_role("button", name="Add")
            submit_button.wait_for(state="visible", timeout=5000)
            submit_button.click()
            result["steps"]["submit_form"] = True
            
            # Handle confirmation if appears
            try:
                confirm_button = self.page.locator("[id='1']")
                if confirm_button.is_visible(timeout=3000):
                    confirm_button.click()
                    self.logger.info("Clicked confirmation button")
                    self.wait(2)
            except:
                pass
            
            # Wait 4-5 seconds for toast to appear (as you mentioned)
            self.logger.info("Waiting 4-5 seconds for toast to appear...")
            self.wait(4)
            
            # Step 6: Capture toast
            self.logger.info("Step 6: Capturing success toast...")
            toast_result = self.capture_success_toast(timeout=10000)
            result["toast_result"] = toast_result
            
            # Determine overall success
            # ALL steps must succeed AND toast must contain "device added"
            overall_success = (
                result["steps"].get("login") and
                result["steps"].get("navigate_to_device") and
                result["steps"].get("open_form") and
                result["steps"].get("fill_form") and
                result["steps"].get("submit_form") and
                toast_result.get("success") and
                toast_result.get("contains_device_added")
            )
            
            result["overall_success"] = overall_success
            
            if overall_success:
                self.logger.info("✅✅✅ Complete registration SUCCESSFUL with toast verification!")
                self.logger.info(f"    Device: SIM={device_data.get('sim')}, Serial={device_data.get('serial')}")
                self.logger.info(f"    Toast: '{toast_result.get('text', '')}'")
                self.take_screenshot("complete_registration_success")
            else:
                self.logger.warning("⚠️⚠️⚠️ Registration completed but verification failed")
                self.logger.warning(f"    Steps: {result['steps']}")
                self.logger.warning(f"    Toast: {toast_result}")
                self.take_screenshot("complete_registration_warning")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌❌❌ Complete registration FAILED: {str(e)}")
            self.take_screenshot("complete_registration_failed")
            
            result["overall_success"] = False
            result["error"] = str(e)
            
            return result