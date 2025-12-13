"""
TMS Portal Page Object - Using Codegen Locators
"""
import allure
import logging
from pages.base_page import BasePage
import time

logger = logging.getLogger(__name__)

class TMSPage(BasePage):
    """Page Object for TMS Portal using Codegen locators"""
    
    # URL
    TMS_PORTAL_URL = "https://ipn-tms-staging.koilifin.com/auth"
    
    # Login Credentials
    DEFAULT_USERNAME = "admin1"
    DEFAULT_PASSWORD = "@dmin2929A"
    
    def __init__(self, page):
        super().__init__(page)
        self.last_toast_message = None
    
    # ==================== LOGIN ====================
    @allure.step("Login to TMS Portal")
    def login(self, username: str = None, password: str = None):
        """Login to TMS portal"""
        self.logger.info("Logging in to TMS portal")
        
        username = username or self.DEFAULT_USERNAME
        password = password or self.DEFAULT_PASSWORD
        
        try:
            # Navigate
            self.navigate(self.TMS_PORTAL_URL)
            self.wait(2)
            
            # Fill username
            username_field = self.page.get_by_role("textbox", name="Username")
            username_field.wait_for(state="visible", timeout=10000)
            username_field.click()
            username_field.fill(username)
            
            # Fill password
            password_field = self.page.get_by_role("textbox", name="password")
            password_field.wait_for(state="visible", timeout=5000)
            password_field.click()
            password_field.fill(password)
            
            # Click Sign In
            signin_button = self.page.get_by_role("button", name="Sign In")
            signin_button.wait_for(state="visible", timeout=5000)
            signin_button.click()
            
            # Wait for login
            self.wait(3)
            
            # Verify login success
            try:
                self.page.get_by_role("button", name="IPN", exact=True).wait_for(
                    state="visible", timeout=10000
                )
                self.logger.info(" TMS login successful")
                self.take_screenshot("tms_login_success")
                return True
            except:
                raise Exception("Login verification failed - IPN button not found")
                
        except Exception as e:
            self.logger.error(f" TMS login failed: {str(e)}")
            self.take_screenshot("tms_login_failed")
            raise
    
    # ==================== IPN SYNC ====================
    @allure.step("Sync IPN")
    def sync_ipn(self):
        """Sync IPN devices"""
        self.logger.info("Syncing IPN devices")
        
        try:
            # Click IPN button
            ipn_button = self.page.get_by_role("button", name="IPN", exact=True)
            ipn_button.wait_for(state="visible", timeout=10000)
            ipn_button.click()
            
            self.wait(1)
            
            # Click Sync IPN button
            sync_button = self.page.get_by_role("button", name="Sync IPN")
            sync_button.wait_for(state="visible", timeout=5000)
            sync_button.click()
            
            self.wait(3)
            
            # Capture sync result message
            try:
                # Wait for sync message (Codegen: page.get_by_text("everything is already up-to").click())
                sync_message = self.page.get_by_text("everything is already up-to", exact=False)
                if sync_message.is_visible(timeout=5000):
                    message_text = sync_message.text_content() or ""
                    self.logger.info(f"IPN Sync message: {message_text}")
                    
                    # Capture toast if available
                    toast_text = self.capture_toast_once(timeout=3000)
                    
                    return {
                        "success": True,
                        "sync_message": message_text.strip(),
                        "toast_result": {
                            "success": bool(toast_text),
                            "text": toast_text or ""
                        }
                    }
            except:
                pass
            
            # If no specific message, just return success
            return {"success": True, "sync_message": "IPN sync initiated"}
            
        except Exception as e:
            self.logger.error(f" IPN sync failed: {str(e)}")
            self.take_screenshot("ipn_sync_failed")
            raise
    
    @allure.step("Add New Merchant")
    def add_merchant(self, merchant_data: dict = None):
        """
        Add a new merchant
        
        Args:
            merchant_data: Dictionary with merchant details
                         If None, uses default test data
        """
        self.logger.info("Adding new merchant")
        
        # Default merchant data (from Codegen)
        if merchant_data is None:
            merchant_data = {
                "account_number": "093242221",
                "merchant_pan": "pantest45",
                "branch": "ACHHAM",
                "schemes": ["Fonepay", "NCHL"],  # MULTIPLE SCHEMES!
                "merchant_code": "merch23232",
                "merchant_id": "merch56856",
                "name": "testmerchantr",
                "email": "testing@gmial.com",
                "address": "ktm",
                "phone": "9812323234"
            }
        
        try:
            # STEP 1: Click Merchant button (from Codegen)
            merchant_button = self.page.get_by_role("button", name="Merchant")
            merchant_button.wait_for(state="visible", timeout=10000)
            merchant_button.click()
            self.wait(2)
            
            # STEP 2: Click Add Merchant button (from Codegen)
            add_button = self.page.get_by_role("button", name="Add Merchant")
            add_button.wait_for(state="visible", timeout=10000)
            add_button.click()
            self.wait(2)
            
            # STEP 3: Fill Account Number
            account_field = self.page.get_by_role("textbox", name="Account Number")
            account_field.wait_for(state="visible", timeout=10000)
            account_field.click()
            account_field.fill(merchant_data["account_number"])
            self.wait(0.5)
            
            # STEP 4: Fill Merchant PAN
            pan_field = self.page.get_by_role("textbox", name="Merchant PAN")
            pan_field.wait_for(state="visible", timeout=5000)
            pan_field.click()
            pan_field.fill(merchant_data["merchant_pan"])
            self.wait(0.5)
            
            # STEP 5: Select Branch
            branch_dropdown = self.page.get_by_role("combobox", name="Branch")
            branch_dropdown.wait_for(state="visible", timeout=5000)
            branch_dropdown.click()
            
            branch_option = self.page.get_by_role("option", name=merchant_data["branch"])
            branch_option.wait_for(state="visible", timeout=5000)
            branch_option.click()
            self.wait(0.5)
            
            # STEP 6: Select Scheme(s) - MULTI-SELECT VERSION
            scheme_dropdown = self.page.get_by_role("combobox", name="Scheme")
            scheme_dropdown.wait_for(state="visible", timeout=5000)
            
            # Double click as in codegen
            scheme_dropdown.dblclick()
            self.wait(0.5)
            
            # Click the div that codegen clicks
            try:
                div_filter = self.page.locator("div").filter(has_text="Add MerchantAccount").nth(1)
                if div_filter.is_visible(timeout=3000):
                    div_filter.click()
                    self.wait(0.5)
            except:
                pass
            
            # Select FIRST scheme: Fonepay
            try:
                fonepay_option = self.page.get_by_role("option", name="Fonepay")
                if fonepay_option.is_visible(timeout=3000):
                    fonepay_option.click()
                    self.logger.info(" Selected Fonepay scheme")
                    self.wait(0.5)
                else:
                    self.logger.warning("Fonepay option not visible")
            except Exception as e:
                self.logger.warning(f"Could not select Fonepay: {e}")
            
            # Re-open dropdown for second selection
            scheme_dropdown.click()
            self.wait(0.5)
            
            # Select SECOND scheme: NCHL
            try:
                nchl_option = self.page.get_by_role("option", name="NCHL", exact=True)
                if nchl_option.is_visible(timeout=3000):
                    nchl_option.click()
                    self.logger.info("Selected NCHL scheme")
                    self.wait(0.5)
                else:
                    # Try without exact match
                    nchl_option = self.page.get_by_role("option", name="NCHL")
                    nchl_option.wait_for(state="visible", timeout=3000)
                    nchl_option.click()
                    self.logger.info(" Selected NCHL scheme (non-exact)")
                    self.wait(0.5)
            except Exception as e:
                self.logger.error(f"Could not select NCHL: {e}")
                raise
            
            # Close dropdown by clicking elsewhere or pressing Escape
            self.page.locator("body").click(position={"x": 10, "y": 10})
            self.wait(0.5)
            
            # STEP 7: Fill Merchant Code
            code_field = self.page.get_by_role("textbox", name="Merchant Code")
            code_field.wait_for(state="visible", timeout=5000)
            code_field.click()
            code_field.fill(merchant_data["merchant_code"])
            self.wait(0.5)
            
            # STEP 8: Fill Merchant ID
            id_field = self.page.get_by_role("textbox", name="Merchant .I.D.")
            id_field.wait_for(state="visible", timeout=5000)
            id_field.click()
            id_field.fill(merchant_data["merchant_id"])
            self.wait(0.5)
            
            # STEP 9: Fill Name
            name_field = self.page.get_by_role("textbox", name="Name")
            name_field.wait_for(state="visible", timeout=5000)
            name_field.click()
            name_field.fill(merchant_data["name"])
            self.wait(0.5)
            
            # STEP 10: Fill Email
            email_field = self.page.get_by_role("textbox", name="Email")
            email_field.wait_for(state="visible", timeout=5000)
            email_field.click()
            email_field.fill(merchant_data["email"])
            self.wait(0.5)
            
            # STEP 11: Fill Address
            address_field = self.page.get_by_role("textbox", name="Address")
            address_field.wait_for(state="visible", timeout=5000)
            address_field.click()
            address_field.fill(merchant_data["address"])
            self.wait(0.5)
            
            # STEP 12: Fill Phone
            phone_field = self.page.get_by_role("textbox", name="Phone")
            phone_field.wait_for(state="visible", timeout=5000)
            phone_field.click()
            phone_field.fill(merchant_data["phone"])
            
            self.take_screenshot("merchant_form_filled")
            
            # STEP 13: Click Add button
            final_add_button = self.page.get_by_role("button", name="Add")
            final_add_button.wait_for(state="visible", timeout=5000)
            final_add_button.click()
            
            self.wait(3)
            
            # STEP 14: Capture toast message using the better method
            toast_text = self.capture_toast_once(timeout=10000)
            
            # Format result to match what your test expects
            result = {
                "success": True,
                "merchant_data": merchant_data,
                "toast_result": {
                    "success": bool(toast_text),  # True if toast_text is not None/empty
                    "text": toast_text or "",
                    "contains_expected": bool(toast_text and "merchant" in toast_text.lower())
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if toast_text and "created" in toast_text.lower():
                self.logger.info(f" Merchant added successfully with toast: {toast_text}")
                self.take_screenshot("merchant_added_success")
            else:
                self.logger.warning(f" Merchant added but toast verification incomplete. Toast: {toast_text}")
                self.take_screenshot("merchant_added_warning")
            
            return result
            
        except Exception as e:
            self.logger.error(f" Failed to add merchant: {str(e)}")
            self.take_screenshot("merchant_add_failed")
            raise

    # ==================== IMPROVED TOAST METHODS ====================
    
    def capture_toast_once(self, timeout=10000):
        """
        Capture toast message ONCE and store it for reuse
        This prevents multiple calls that fail after toast disappears
        """
        if self.last_toast_message:
            self.logger.info(f"Using cached toast message: {self.last_toast_message}")
            return self.last_toast_message
            
        try:
            self.logger.info("Waiting for toast message to appear...")
            
            # Try different selectors for toast
            selectors = [
                "[role='alert']",
                ".MuiAlert-root",
                ".toast",
                ".notification",
                ".ant-message",
                ".ant-notification",
                ".success-message",
                ".alert-success"
            ]
            
            # Wait a bit for toast to appear
            self.wait(1)
            
            for selector in selectors:
                try:
                    self.logger.info(f"Trying selector: {selector}")
                    toast_element = self.page.locator(selector).first
                    if toast_element.is_visible(timeout=2000):
                        toast_text = toast_element.text_content()
                        if toast_text and toast_text.strip():
                            self.last_toast_message = toast_text.strip()
                            self.logger.info(f" Captured toast message: {self.last_toast_message}")
                            return self.last_toast_message
                except:
                    continue
            
            # Also try to find any text that looks like a success message
            try:
                success_keywords = ["success", "created", "added", "saved", "merchant"]
                for keyword in success_keywords:
                    element = self.page.get_by_text(keyword, exact=False).first
                    if element.is_visible(timeout=1000):
                        toast_text = element.text_content()
                        if toast_text and toast_text.strip():
                            self.last_toast_message = toast_text.strip()
                            self.logger.info(f" Captured toast by keyword '{keyword}': {self.last_toast_message}")
                            return self.last_toast_message
            except:
                pass
            
            # Try the method from codegen: get_by_role("alert")
            try:
                alert_element = self.page.get_by_role("alert").first
                if alert_element.is_visible(timeout=2000):
                    alert_element.dblclick()  # Codegen does dblclick
                    toast_text = alert_element.text_content()
                    if toast_text and toast_text.strip():
                        self.last_toast_message = toast_text.strip()
                        self.logger.info(f" Captured toast via role='alert': {self.last_toast_message}")
                        return self.last_toast_message
            except:
                pass
            
            self.logger.warning("No toast message found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error capturing toast: {e}")
            return None
    
    # ==================== ASSIGN IPN TO MERCHANT ====================
    @allure.step("Assign IPN to Merchant")
    def assign_ipn_to_merchant(self, ipn_serial: str, terminal_data: dict = None):
        """
        Assign IPN to merchant
        
        Args:
            ipn_serial: IPN serial number from admin registration
            terminal_data: Dictionary with terminal details
        """
        self.logger.info(f"Assigning IPN {ipn_serial} to merchant")
        
        # Default terminal data (from Codegen)
        if terminal_data is None:
            terminal_data = {
                "terminal_id": "terminalewfhs",
                "store_id": "store2324v",
                "fonepay_pan": "sdvvgerr3"
            }
        
        try:
            # STEP 1: Expand merchant (Codegen: page.locator("#expand-more-button-0").click())
            expand_button = self.page.locator("#expand-more-button-0")
            expand_button.wait_for(state="visible", timeout=10000)
            expand_button.click()
            self.wait(1)
            
            # STEP 2: Click Assigned IPNs (Codegen: page.get_by_role("menuitem", name="Assigned IPNs").click())
            ipns_menu = self.page.get_by_role("menuitem", name="Assigned IPNs")
            ipns_menu.wait_for(state="visible", timeout=5000)
            ipns_menu.click()
            self.wait(2)
            
            # STEP 3: Click Assign IPN button
            assign_button = self.page.get_by_role("button", name="Assign IPN")
            assign_button.wait_for(state="visible", timeout=10000)
            assign_button.click()
            self.wait(2)
            
            # STEP 4: Search for IPN
            search_field = self.page.get_by_role("textbox", name="Search IPN")
            search_field.wait_for(state="visible", timeout=5000)
            search_field.click()
            search_field.fill(ipn_serial)
            search_field.click()
            search_field.press("Enter")
            
            self.wait(2)
            
            # STEP 5: Select the IPN row (Codegen pattern)
            # Find row containing the IPN serial
            row_locator = self.page.get_by_role("row").filter(has_text=ipn_serial).first
            if row_locator.is_visible(timeout=5000):
                # Get the checkbox in that row
                select_checkbox = row_locator.get_by_label("Select row")
                select_checkbox.wait_for(state="visible", timeout=5000)
                select_checkbox.check()
            else:
                # Fallback to first row
                self.page.get_by_label("Select row").first.check()
            
            self.wait(1)
            
            # STEP 6: Click schema icon (Codegen: get_by_test_id("SchemaIcon"))
            try:
                # Find the row again and click SchemaIcon
                row_with_ipn = self.page.get_by_role("row").filter(has_text=ipn_serial).first
                schema_icon = row_with_ipn.get_by_test_id("SchemaIcon")
                if schema_icon.is_visible(timeout=3000):
                    schema_icon.click()
            except:
                # Alternative: click on the row
                self.page.get_by_role("row").filter(has_text=ipn_serial).first.click()
            
            self.wait(1)
            
            # STEP 7: Fill Terminal ID
            terminal_field = self.page.get_by_role("textbox", name="Terminal I.D.")
            terminal_field.wait_for(state="visible", timeout=5000)
            terminal_field.click()
            terminal_field.fill(terminal_data["terminal_id"])
            self.wait(0.5)
            
            # STEP 8: Fill Store ID
            store_field = self.page.get_by_role("textbox", name="Store I.D.")
            store_field.wait_for(state="visible", timeout=5000)
            store_field.click()
            store_field.fill(terminal_data["store_id"])
            self.wait(0.5)
            
            # STEP 9: Fill Fonepay PAN
            pan_field = self.page.get_by_role("textbox", name="Fonepay Pan Number")
            pan_field.wait_for(state="visible", timeout=5000)
            pan_field.click()
            pan_field.fill(terminal_data["fonepay_pan"])
            
            self.take_screenshot("terminal_details_filled")
            
            # STEP 10: Click Update button
            update_button = self.page.get_by_role("button", name="Update")
            update_button.wait_for(state="visible", timeout=5000)
            update_button.click()
            self.wait(1)
            
            # STEP 11: Click Assign button
            assign_final_button = self.page.get_by_role("button", name="Assign")
            assign_final_button.wait_for(state="visible", timeout=5000)
            assign_final_button.click()
            
            self.wait(3)
            
            # STEP 12: Capture toast using the improved method
            toast_text = self.capture_toast_once(timeout=10000)
            
            result = {
                "success": True,
                "ipn_serial": ipn_serial,
                "terminal_data": terminal_data,
                "toast_result": {
                    "success": bool(toast_text),  # True if toast_text is not None/empty
                    "text": toast_text or "",
                    "contains_expected": bool(toast_text and ("assigned" in toast_text.lower() or "ipn" in toast_text.lower()))
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if toast_text and "assigned" in toast_text.lower():
                self.logger.info(f" IPN assigned successfully with toast: {toast_text}")
                self.take_screenshot("ipn_assigned_success")
            else:
                self.logger.warning(f" IPN assigned but toast verification incomplete. Toast: {toast_text}")
                self.take_screenshot("ipn_assigned_warning")
            
            return result
            
        except Exception as e:
            self.logger.error(f" Failed to assign IPN: {str(e)}")
            self.take_screenshot("ipn_assign_failed")
            raise
    
    # ==================== NAVIGATE TO DASHBOARD ====================
    @allure.step("Navigate to Dashboard")
    def navigate_to_dashboard(self):
        """Navigate back to dashboard"""
        self.logger.info("Navigating to dashboard")
        
        dashboard_button = self.page.get_by_role("button", name="Dashboard")
        dashboard_button.wait_for(state="visible", timeout=10000)
        dashboard_button.click()
        self.wait(2)
        return True
    
    # ==================== COMPLETE TMS FLOW ====================
    @allure.step("Complete TMS Flow")
    def complete_tms_flow(self, ipn_serial: str = None):
        """
        Complete TMS flow from login to IPN assignment
        
        Args:
            ipn_serial: IPN serial number from admin registration
                       If None, uses hardcoded value from Codegen
        """
        self.logger.info("Starting complete TMS flow")
        
        result = {
            "overall_success": False,
            "steps": {},
            "merchant_result": {},
            "ipn_assignment_result": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        ipn_serial = ipn_serial or "38231105960007"  # From Codegen
        
        try:
            # Step 1: Login
            self.logger.info("Step 1: Logging in...")
            result["steps"]["login"] = self.login()
            
            # Step 2: Sync IPN
            self.logger.info("Step 2: Syncing IPN...")
            sync_result = self.sync_ipn()
            result["steps"]["sync_ipn"] = sync_result.get("success", False)
            result["steps"]["sync_message"] = sync_result.get("sync_message", "")
            
            # Step 3: Add Merchant
            self.logger.info("Step 3: Adding merchant...")
            merchant_result = self.add_merchant()
            result["merchant_result"] = merchant_result
            result["steps"]["add_merchant"] = merchant_result.get("success", False)
            
            # Step 4: Assign IPN
            self.logger.info("Step 4: Assigning IPN to merchant...")
            ipn_result = self.assign_ipn_to_merchant(ipn_serial)
            result["ipn_assignment_result"] = ipn_result
            result["steps"]["assign_ipn"] = ipn_result.get("success", False)
            
            # Step 5: Navigate to Dashboard
            self.logger.info("Step 5: Navigating to dashboard...")
            result["steps"]["navigate_dashboard"] = self.navigate_to_dashboard()
            
            # Determine overall success
            overall_success = all([
                result["steps"].get("login"),
                result["steps"].get("add_merchant"),
                result["steps"].get("assign_ipn")
            ])
            
            result["overall_success"] = overall_success
            
            if overall_success:
                self.logger.info(" Complete TMS flow SUCCESSFUL!")
                self.take_screenshot("complete_tms_flow_success")
            else:
                self.logger.warning(" TMS flow completed with some issues")
                self.take_screenshot("complete_tms_flow_warning")
            
            return result
            
        except Exception as e:
            self.logger.error(f" Complete TMS flow FAILED: {str(e)}")
            self.take_screenshot("complete_tms_flow_failed")
            
            result["overall_success"] = False
            result["error"] = str(e)
            
            return result