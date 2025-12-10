"""
TMS Portal Page Object Model
Complete implementation of all TMS UI automation steps
"""
import allure
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class TMSPortal(BasePage):
    """TMS Portal Page Object with all business logic"""
    
    # ==================== URL CONFIG ====================
    TMS_URL = "https://ipn-tms-staging.koilifin.com"
    
    # ==================== LOCATORS ====================
    class Locators:
        # Login Page
        USERNAME_INPUT = 'input[id="username"]'
        PASSWORD_INPUT = 'css=#outlined-adornment-password-1'
        LOGIN_BUTTON = "button:has-text('Sign In')"
        DASHBOARD_HEADER = "text='TMS Dashboard'"
        
        # Navigation
        IPN_MENU = "role=button[name='IPN']"
        MERCHANT_MENU = "div[role='button'] >> text=Merchant"
        
        # IPN Sync
        SYNC_IPN_BUTTON = "label:has-text('Sync IPN')"
        SYNC_SUCCESS_INDICATOR = "text='Last Sync'"
        
        # Merchant Creation
        ADD_MERCHANT_BUTTON = "button:has-text('Add Merchant')"
        ACCOUNT_NUMBER_INPUT = '[role="textbox"][name="account_number"]'
        PAN_INPUT = '[role="textbox"][id="pan"]'
        BRANCH_SELECT = '[role="combobox"][id="branch"]'
        SCHEME_SELECT = '[role="combobox"][id="scheme-select-box"]'
        NCHL_MERCHANT_CODE_INPUT = '#nchl_merchantCode'
        FONEPAY_MERCHANT_ID_INPUT = '#fonepay_merchantId'
        CATEGORY_CODE_SELECT = '[role="combobox"][id="category-code-search"]'
        NAME_INPUT = '#name'
        ADDRESS_INPUT = '#address'
        EMAIL_INPUT = '#email'
        PHONE_INPUT = '#phone'
        ADD_SUBMIT_BUTTON = 'button:text("Add")'
        
        # Merchant List
        MERCHANT_TABLE = '.merchant-table'
        FIRST_MERCHANT_ROW = '.merchant-table tbody tr:first-child'
        MERCHANT_NAME_CELL = 'td:nth-child(2)'
        
        # Device Assignment
        ACTION_MENU_BUTTON = '[data-testid="MoreHorizIcon"]'
        ASSIGNED_IPNS_MENU_ITEM = '[role="menuitem"]:text("Assigned IPNs")'
        ASSIGN_IPN_BUTTON = 'button:text("Assign IPN")'
        SEARCH_INPUT = "input[placeholder='Search by serial']"
        IPN_CHECKBOX = '[data-testid="CheckBoxOutlineBlankIcon"]'
        
        # Scheme Identifiers
        SCHEME_ICON_BUTTON = '[data-testid="SchemaIcon"]'
        NCHL_TERMINAL_ID_INPUT = '#nchl_terminalId'
        NCHL_STORE_ID_INPUT = '#nchl_storeId'
        FONEPAY_TERMINAL_ID_INPUT = '#fonepay_terminalId'
        UPDATE_IDENTIFIERS_BUTTON = 'button:has-text("Update")'
        ASSIGN_FINAL_BUTTON = 'button:has-text("Assign")'
        
        # Common Elements
        LOADING_SPINNER = '.loading-spinner'
        TOAST_MESSAGE = '.toast-message'
    
    def __init__(self, page):
        super().__init__(page)
        self.locators = self.Locators()
        logger.info("Initialized TMS Portal POM")
    
    # ==================== STEP 1: LOGIN ====================
    @allure.step("Login to TMS Portal")
    def login(self, username: str = "admin1", password: str = "@dmin2929A") -> 'TMSPortal':
        """Login to TMS Portal"""
        logger.info(f"Logging in with username: {username}")
        
        # Navigate to TMS
        self.navigate(self.TMS_URL)
        self.take_screenshot("login_page")
        
        # Fill credentials
        self.fill(self.locators.USERNAME_INPUT, username, "Username")
        self.fill(self.locators.PASSWORD_INPUT, password, "Password")
        
        # Click login
        self.click(self.locators.LOGIN_BUTTON, "Login Button")
        
        # Verify login success
        self.wait_for_element(self.locators.DASHBOARD_HEADER, "Dashboard Header", timeout=15000)
        self.take_screenshot("dashboard_loaded")
        
        logger.info(" Login successful")
        return self
    
    # ==================== STEP 2: SYNC IPN ====================
    @allure.step("Sync IPN Devices")
    def sync_ipn_devices(self) -> 'TMSPortal':
        """Sync IPN devices from admin portal"""
        logger.info("Starting IPN sync")
        
        # Navigate to IPN section
        self.click(self.locators.IPN_MENU, "IPN Menu")
        self.wait(2)
        
        # Click sync button
        self.click(self.locators.SYNC_IPN_BUTTON, "Sync IPN Button")
        self.wait(3)  # Wait for sync to complete
        
        # Verify sync
        if self.is_element_present(self.locators.SYNC_SUCCESS_INDICATOR):
            logger.info(" IPN sync completed")
        else:
            logger.warning("Sync indicator not found")
        
        self.take_screenshot("ipn_synced")
        return self
    
    # ==================== STEP 3 & 4: CREATE MERCHANT ====================
    @allure.step("Create New Merchant")
    def create_merchant(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create merchant with NCHL and Fonepay schemes"""
        logger.info(f"Creating merchant: {merchant_data.get('name')}")
        
        # Navigate to Merchant section
        self.click(self.locators.MERCHANT_MENU, "Merchant Menu")
        self.wait(2)
        
        # Open add merchant form
        self.click(self.locators.ADD_MERCHANT_BUTTON, "Add Merchant Button")
        self.wait(1)
        self.take_screenshot("merchant_form")
        
        # Fill form
        self._fill_merchant_form(merchant_data)
        self.take_screenshot("form_filled")
        
        # Submit form
        self.click(self.locators.ADD_SUBMIT_BUTTON, "Submit Button")
        
        # Validate creation
        success = self._validate_merchant_creation()
        if not success:
            raise Exception("Merchant creation failed")
        
        # Verify in list
        self.refresh_page()
        self.wait(3)
        self._verify_merchant_in_list(merchant_data["name"])
        
        # Return result
        result = merchant_data.copy()
        result.update({
            "created_at": datetime.now().isoformat(),
            "created_successfully": True
        })
        
        logger.info(f" Merchant created: {merchant_data['name']}")
        return result
    
    def _fill_merchant_form(self, merchant_data: Dict[str, Any]) -> None:
        """Fill all merchant form fields"""
        # Basic information
        self.fill(self.locators.ACCOUNT_NUMBER_INPUT, merchant_data["account_number"], "Account Number")
        self.fill(self.locators.PAN_INPUT, merchant_data["pan"], "PAN")
        self.select_option(self.locators.BRANCH_SELECT, merchant_data.get("branch", "AACHAM"), "Branch")
        
        # Select schemes
        self._select_schemes()
        self.wait(2)
        
        # Merchant codes
        self.fill(self.locators.NCHL_MERCHANT_CODE_INPUT, merchant_data["nchl_merchant_code"], "NCHL Code")
        self.fill(self.locators.FONEPAY_MERCHANT_ID_INPUT, merchant_data["fonepay_merchant_id"], "Fonepay ID")
        
        # Category code (optional)
        self._select_category_code()
        
        # Contact details
        self.fill(self.locators.NAME_INPUT, merchant_data["name"], "Name")
        self.fill(self.locators.ADDRESS_INPUT, merchant_data["address"], "Address")
        self.fill(self.locators.EMAIL_INPUT, merchant_data["email"], "Email")
        self.fill(self.locators.PHONE_INPUT, merchant_data["phone"], "Phone")
    
    def _select_schemes(self) -> None:
        """Select both NCHL and Fonepay schemes"""
        self.click(self.locators.SCHEME_SELECT, "Scheme Dropdown")
        self.wait(0.5)
        
        # Select NCHL
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        self.wait(0.5)
        
        # Select Fonepay
        self.click(self.locators.SCHEME_SELECT, "Scheme Dropdown")
        self.wait(0.5)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        
        logger.info("Selected NCHL and Fonepay schemes")
    
    def _select_category_code(self) -> None:
        """Select first category code (optional)"""
        try:
            if self.is_element_present(self.locators.CATEGORY_CODE_SELECT):
                self.click(self.locators.CATEGORY_CODE_SELECT, "Category Code")
                self.wait(0.5)
                self.page.keyboard.press("ArrowDown")
                self.page.keyboard.press("Enter")
        except:
            pass  # Not mandatory
    
    def _validate_merchant_creation(self) -> bool:
        """Validate merchant creation toast message"""
        try:
            # Wait for toast message
            self.wait_for_element(self.locators.TOAST_MESSAGE, "Toast Message", timeout=10000)
            toast_text = self.get_element_text(self.locators.TOAST_MESSAGE)
            
            if "successfully" in toast_text.lower():
                logger.info(f"Merchant creation toast: {toast_text}")
                return True
            elif "already exists" in toast_text.lower():
                raise Exception(f"Merchant already exists: {toast_text}")
            else:
                logger.error(f"Unexpected toast: {toast_text}")
                return False
        except Exception as e:
            logger.error(f"Toast validation error: {e}")
            return False
    
    def _verify_merchant_in_list(self, merchant_name: str) -> bool:
        """Verify merchant appears in list"""
        try:
            if self.is_element_present(self.locators.MERCHANT_TABLE, timeout=5000):
                name_cell = self.page.locator(f"{self.locators.FIRST_MERCHANT_ROW} {self.locators.MERCHANT_NAME_CELL}")
                if name_cell.is_visible():
                    actual_name = name_cell.text_content(timeout=2000)
                    if merchant_name in actual_name:
                        logger.info(f" Merchant in list: {actual_name}")
                        return True
            return False
        except:
            return False
    
    # ==================== STEP 5: ASSIGN DEVICE ====================
    @allure.step("Assign Device to Merchant")
    def assign_device_to_merchant(self, merchant_name: str, device_serial: str,
                                 identifiers: Dict[str, str]) -> bool:
        """Assign device to merchant with identifiers"""
        logger.info(f"Assigning device {device_serial} to {merchant_name}")
        
        try:
            # Refresh and open assignment
            self.refresh_page()
            self.wait(2)
            
            # Open merchant actions
            self.click(self.locators.ACTION_MENU_BUTTON, "Action Menu")
            self.wait(1)
            self.click(self.locators.ASSIGNED_IPNS_MENU_ITEM, "Assigned IPNs")
            self.wait(2)
            
            # Open assign modal
            self.click(self.locators.ASSIGN_IPN_BUTTON, "Assign IPN Button")
            self.wait(1)
            self.take_screenshot("assign_modal")
            
            # Search and select device
            self.fill(self.locators.SEARCH_INPUT, device_serial, "Device Search")
            self.wait(2)
            self.click(self.locators.IPN_CHECKBOX, "Device Checkbox")
            self.wait(0.5)
            
            # Enter identifiers
            self.click(self.locators.SCHEME_ICON_BUTTON, "Scheme Icon")
            self.wait(1)
            
            self.fill(self.locators.NCHL_TERMINAL_ID_INPUT, identifiers["nchl_terminal_id"], "NCHL Terminal ID")
            self.fill(self.locators.NCHL_STORE_ID_INPUT, identifiers["nchl_store_id"], "NCHL Store ID")
            self.fill(self.locators.FONEPAY_TERMINAL_ID_INPUT, identifiers["fonepay_terminal_id"], "Fonepay Terminal ID")
            
            self.take_screenshot("identifiers_filled")
            
            # Update identifiers
            self.click(self.locators.UPDATE_IDENTIFIERS_BUTTON, "Update Button")
            self.wait(2)
            
            # Final assign
            self.click(self.locators.ASSIGN_FINAL_BUTTON, "Final Assign Button")
            self.wait(2)
            
            # Verify assignment
            if self.is_element_present(self.locators.TOAST_MESSAGE):
                toast_text = self.get_element_text(self.locators.TOAST_MESSAGE)
                if "successfully" in toast_text.lower():
                    logger.info(f" Assignment successful: {toast_text}")
                    self.take_screenshot("assignment_complete")
                    return True
            
            logger.error("Assignment failed - no success toast")
            return False
            
        except Exception as e:
            logger.error(f"Assignment failed: {e}")
            self.take_screenshot("assignment_failed")
            return False
    
    # ==================== COMPLETE FLOW ====================
    @allure.step("Execute Complete TMS Flow")
    def execute_complete_flow(self, device_serial: str,
                             custom_merchant_data: Optional[Dict] = None,
                             custom_identifiers: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute complete TMS flow"""
        logger.info("Starting complete TMS flow")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "success": False,
            "errors": []
        }
        
        try:
            # Generate test data
            merchant_data = custom_merchant_data or self.generate_merchant_data()
            identifiers = custom_identifiers or self.generate_identifiers_data()
            
            # Step 1: Login
            self.login()
            results["steps_completed"].append("login")
            
            # Step 2: Sync IPN
            self.sync_ipn_devices()
            results["steps_completed"].append("sync_ipn")
            
            # Steps 3&4: Create Merchant
            merchant_result = self.create_merchant(merchant_data)
            results["steps_completed"].append("create_merchant")
            results["merchant"] = merchant_result
            
            # Step 5: Assign Device
            assignment_success = self.assign_device_to_merchant(
                merchant_name=merchant_result["name"],
                device_serial=device_serial,
                identifiers=identifiers
            )
            
            if assignment_success:
                results["steps_completed"].append("assign_device")
                results["success"] = True
                results["device"] = device_serial
                logger.info(" TMS flow completed successfully")
            else:
                results["errors"].append("Device assignment failed")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f" TMS flow failed: {error_msg}")
            results["errors"].append(error_msg)
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    # ==================== TEST DATA GENERATORS ====================
    @staticmethod
    def generate_merchant_data() -> Dict[str, Any]:
        """Generate unique merchant test data"""
        timestamp = int(time.time())
        return {
            "account_number": f"ACCT{timestamp}",
            "pan": f"PAN{timestamp % 10000:04d}",
            "branch": "AACHAM",
            "nchl_merchant_code": f"merchant{timestamp}",
            "fonepay_merchant_id": f"fonepay{timestamp}",
            "name": f"Test_Merchant_{timestamp}",
            "address": f"Test Address {timestamp}",
            "email": f"test{timestamp}@example.com",
            "phone": f"98{(timestamp % 10000):07d}"
        }
    
    @staticmethod
    def generate_identifiers_data() -> Dict[str, str]:
        """Generate unique identifiers test data"""
        timestamp = int(time.time()) % 1000
        return {
            "nchl_terminal_id": f"terminalid{timestamp:03d}",
            "nchl_store_id": f"storeid{timestamp:03d}",
            "fonepay_terminal_id": f"fonepaycode{timestamp:03d}"
        }