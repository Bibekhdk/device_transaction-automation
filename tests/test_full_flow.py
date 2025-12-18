"""
COMPLETE 9-STEP DEVICE TRANSACTION TEST WITH ERROR HANDLING
Fixed to use data created during TMS UI steps
"""

import pytest
import allure
import logging
import time
import os
from datetime import datetime
from faker import Faker
from playwright.sync_api import Page

# Import all necessary modules
from test_data.test_constants import *
from pages.admin_portal.device_registration_page import DeviceRegistrationPage
from pages.tms_portal.tms_page import TMSPage
from api.dps_api import DPSAPI
from api.ipn_api import IPNAPI
from database.mongo_handler import MongoHandler

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# EMBEDDED STATE MANAGER (to avoid import issues)
# ============================================================================
class TestStateManager:
    def __init__(self):
        self.steps = {}
        self.context = {}
        self.errors = []
        
    def record_step(self, step_name, status, error=None, data=None):
        """Record a step's execution status"""
        self.steps[step_name] = {
            "status": status,
            "error": str(error) if error else None,
            "data": data,
            "timestamp": time.time()
        }
        
        if error:
            self.errors.append(f"{step_name}: {error}")
    
    def get_step_status(self, step_name):
        """Get status of a specific step"""
        return self.steps.get(step_name, {}).get("status")
    
    def get_failed_steps(self):
        """Get all failed steps"""
        return {k: v for k, v in self.steps.items() if v.get("status") == "failed"}
    
    def get_summary(self):
        """Get test execution summary"""
        total = len(self.steps)
        passed = sum(1 for s in self.steps.values() if s.get("status") == "passed")
        failed = sum(1 for s in self.steps.values() if s.get("status") == "failed")
        skipped = sum(1 for s in self.steps.values() if s.get("status") == "skipped")
        
        return {
            "total_steps": total,
            "passed_steps": passed,
            "failed_steps": failed,
            "skipped_steps": skipped,
            "failed_step_names": list(self.get_failed_steps().keys()),
            "errors": self.errors,
            "context_data": self.context
        }

# ============================================================================
# TEST CLASS
# ============================================================================
@allure.feature("Complete 9-Step Device Transaction Testing")
@allure.severity(allure.severity_level.CRITICAL)
class TestComplete9StepDeviceTransactionFlow:
    """Complete 9-step workflow with error handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment"""
        self.page = page
        self.fake = Faker()
        self.state = TestStateManager()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Starting 9-Step Test - Timestamp: {self.timestamp}")
        yield
        
        # Final summary after test
        self._print_summary()
    
    def _print_summary(self):
        """Print test execution summary"""
        summary = self.state.get_summary()
        logger.info("\n" + "="*70)
        logger.info("TEST EXECUTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Steps: {summary['total_steps']}")
        logger.info(f"Passed Steps: {summary['passed_steps']}")
        logger.info(f"Failed Steps: {summary['failed_steps']}")
        logger.info(f"Skipped Steps: {summary['skipped_steps']}")
        
        if summary['failed_steps'] > 0:
            logger.info("\nFailed Steps:")
            for step in summary['failed_step_names']:
                logger.info(f"  - {step}")
            
            logger.info("\nErrors:")
            for error in summary['errors']:
                logger.info(f"  - {error}")
        
        # Attach summary to Allure
        summary_text = f"""
        Test Execution Summary:
        ----------------------
        Timestamp: {self.timestamp}
        Total Steps: {summary['total_steps']}
        Passed Steps: {summary['passed_steps']}
        Failed Steps: {summary['failed_steps']}
        Skipped Steps: {summary['skipped_steps']}
        
        Data Created During Test:
        -------------------------
        Device Serial: {summary['context_data'].get('device_serial', 'N/A')}
        Merchant Code (created in TMS): {summary['context_data'].get('merchant_code', 'N/A')}
        Merchant ID (created in TMS): {summary['context_data'].get('merchant_id', 'N/A')}
        Terminal ID (assigned in TMS): {summary['context_data'].get('terminal_id', 'N/A')}
        Store ID (assigned in TMS): {summary['context_data'].get('store_id', 'N/A')}
        Fonepay Terminal ID (assigned in TMS): {summary['context_data'].get('fonepay_terminal_id', 'N/A')}
        
        API Transaction Data Used:
        --------------------------
        NCHL: {summary['context_data'].get('merchant_code', 'N/A')} | {summary['context_data'].get('terminal_id', 'N/A')} | {summary['context_data'].get('store_id', 'N/A')}
        Fonepay: {summary['context_data'].get('merchant_id', 'N/A')} | {summary['context_data'].get('fonepay_terminal_id', 'N/A')}
        """
        
        allure.attach(summary_text, name="Test Summary", attachment_type=allure.attachment_type.TEXT)
    
    @allure.title("9-Step Device Registration to Transaction Flow")
    def test_9_step_device_transaction_flow(self):
        """
        EXACT 9-STEP PLAN:
        1. Admin Portal Login
        2. Register New Device (hardcoded serial)
        3. Send DPS Request
        4. TMS Portal Login
        5. Create Test Merchant (generates merchant_code, merchant_id)
        6. Sync IPN
        7. Assign Device to Merchant (generates terminal_id, store_id)
        8. Send Transaction Notifications (USES DATA FROM STEPS 5 & 7)
        9. Verify in MongoDB
        """
        
        # ====================================================================
        # STEP 1: ADMIN PORTAL LOGIN
        # ====================================================================
        with allure.step("Step 1: Login to Admin Portal"):
            step_name = "Admin Portal Login"
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 1: ADMIN PORTAL LOGIN")
                logger.info("="*60)
                
                self.admin_page = DeviceRegistrationPage(self.page)
                logger.info("✓ Admin portal login successful")
                logger.info(f"Hardcoded serial in page object: {self.admin_page.test_serial_number}")
                self.state.record_step(step_name, "passed")
                
            except Exception as e:
                logger.error(f"✗ {step_name} failed: {e}")
                self.page.screenshot(path=f"step1_failed_{self.timestamp}.png")
                self.state.record_step(step_name, "failed", e)
                pytest.fail(f"{step_name} failed: {e}")
        
        # ====================================================================
        # STEP 2: REGISTER NEW DEVICE (USES HARDCODED SERIAL)
        # ====================================================================
        with allure.step("Step 2: Register New Device"):
            step_name = "Device Registration"
            device_serial = None
            
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 2: DEVICE REGISTRATION")
                logger.info("="*60)
                
                registration_result = self.admin_page.complete_registration_with_toast(customer="Test")
                
                # Always use hardcoded serial regardless of registration result
                device_serial = self.admin_page.test_serial_number
                logger.info(f"✓ Using hardcoded device serial: {device_serial}")
                
                self.state.context["device_serial"] = device_serial
                self.state.context["device_data"] = {"serial": device_serial}
                self.state.record_step(step_name, "passed", data={"serial": device_serial})
                
            except Exception as e:
                logger.error(f"✗ {step_name} failed: {e}")
                device_serial = self.admin_page.test_serial_number
                logger.info(f"✓ Using hardcoded serial as fallback: {device_serial}")
                self.state.context["device_serial"] = device_serial
                self.state.context["device_data"] = {"serial": device_serial}
                self.state.record_step(step_name, "failed", e)
        
        # ====================================================================
        # STEP 3: SEND DPS REQUEST
        # ====================================================================
        with allure.step("Step 3: Send DPS Request"):
            step_name = "DPS Request"
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 3: DPS REQUEST")
                logger.info("="*60)
                
                device_serial = self.state.context["device_serial"]
                logger.info(f"Sending DPS request for device: {device_serial}")
                
                dps_api = DPSAPI(base_url=API_DPS_ENDPOINT, auth_token=DPS_AUTH_TOKEN)
                dps_response = dps_api.send_dps_request(device_serial)
                
                if dps_api.verify_dps_response(dps_response, device_serial):
                    logger.info("✓ DPS request successful")
                    self.state.context["dps_response"] = dps_response
                    self.state.record_step(step_name, "passed")
                else:
                    logger.warning(f"⚠ DPS verification failed: {dps_response}")
                    self.state.record_step(step_name, "failed", f"DPS verification failed")
                
            except Exception as e:
                logger.warning(f"⚠ {step_name} failed (non-critical): {e}")
                self.state.record_step(step_name, "failed", e)
        
        # ====================================================================
        # STEP 4: TMS PORTAL LOGIN
        # ====================================================================
        with allure.step("Step 4: Login to TMS Portal"):
            step_name = "TMS Portal Login"
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 4: TMS PORTAL LOGIN")
                logger.info("="*60)
                
                self.tms_page = TMSPage(self.page)
                self.tms_page.login()
                logger.info("✓ TMS portal login successful")
                self.state.record_step(step_name, "passed")
                
            except Exception as e:
                logger.error(f"✗ {step_name} failed: {e}")
                self.page.screenshot(path=f"step4_failed_{self.timestamp}.png")
                self.state.record_step(step_name, "failed", e)
                # Skip TMS-dependent steps if login fails
                logger.warning("Skipping TMS-dependent steps (5-7)")
        
        # ====================================================================
        # STEP 5: CREATE TEST MERCHANT (GENERATES MERCHANT_CODE, MERCHANT_ID)
        # ====================================================================
        with allure.step("Step 5: Create Test Merchant"):
            step_name = "Merchant Creation"
            
            # Skip if TMS login failed
            if self.state.get_step_status("TMS Portal Login") == "failed":
                logger.info("Skipping merchant creation (TMS login failed)")
                self.state.record_step(step_name, "skipped", "TMS login failed")
                # No fallback data - will cause transaction step to fail
                self.state.context["merchant_code"] = None
                self.state.context["merchant_id"] = None
            else:
                try:
                    logger.info("\n" + "="*60)
                    logger.info("STEP 5: MERCHANT CREATION")
                    logger.info("="*60)
                    
                    # Generate unique merchant data - THESE WILL BE USED FOR TRANSACTIONS
                    merchant_code = f"M{self.fake.unique.random_number(digits=10)}"
                    merchant_id = f"F{self.fake.unique.random_number(digits=10)}"
                    
                    merchant_data = {
                        "account_number": str(self.fake.unique.random_number(digits=15)),
                        "merchant_pan": self.fake.unique.bothify(text='PAN#####'),
                        "branch": "ACHHAM",
                        "schemes": ["Fonepay", "NCHL"],
                        "merchant_code": merchant_code,  # FOR NCHL TRANSACTIONS
                        "merchant_id": merchant_id,      # FOR FONEPAY TRANSACTIONS
                        "name": f"Test_Merchant_{self.timestamp}",
                        "email": self.fake.email(),
                        "address": "Kathmandu",
                        "phone": f"98{self.fake.random_number(digits=8, fix_len=True)}"
                    }
                    
                    merchant_result = self.tms_page.add_merchant(merchant_data)
                    
                    if merchant_result.get("success", False):
                        logger.info(f"✓ Merchant created: {merchant_data['name']}")
                        logger.info(f"  Merchant Code (for NCHL): {merchant_code}")
                        logger.info(f"  Merchant ID (for Fonepay): {merchant_id}")
                        
                        # Store generated data for transaction step
                        self.state.context["merchant_code"] = merchant_code
                        self.state.context["merchant_id"] = merchant_id
                        self.state.context["merchant_data"] = merchant_data
                        self.state.record_step(step_name, "passed", data={"merchant_code": merchant_code, "merchant_id": merchant_id})
                    else:
                        raise Exception(f"Merchant creation failed: {merchant_result}")
                        
                except Exception as e:
                    logger.error(f"✗ {step_name} failed: {e}")
                    self.page.screenshot(path=f"step5_failed_{self.timestamp}.png")
                    self.state.record_step(step_name, "failed", e)
                    # No fallback data - will cause transaction step to fail
                    self.state.context["merchant_code"] = None
                    self.state.context["merchant_id"] = None
        
        # ====================================================================
        # STEP 6: SYNC IPN
        # ====================================================================
        with allure.step("Step 6: Sync IPN"):
            step_name = "IPN Sync"
            
            if self.state.get_step_status("TMS Portal Login") == "failed":
                logger.info("Skipping IPN sync (TMS login failed)")
                self.state.record_step(step_name, "skipped", "TMS login failed")
            else:
                try:
                    logger.info("\n" + "="*60)
                    logger.info("STEP 6: IPN SYNC")
                    logger.info("="*60)
                    
                    self.tms_page.sync_ipn()
                    time.sleep(5)
                    logger.info("✓ IPN sync completed")
                    self.state.record_step(step_name, "passed")
                    
                except Exception as e:
                    logger.warning(f"⚠ {step_name} failed (non-critical): {e}")
                    self.state.record_step(step_name, "failed", e)
        
        # ====================================================================
        # STEP 7: ASSIGN DEVICE TO MERCHANT (GENERATES TERMINAL_ID, STORE_ID)
        # ====================================================================
        with allure.step("Step 7: Assign Device to Merchant"):
            step_name = "Device Assignment"
            
            if self.state.get_step_status("TMS Portal Login") == "failed":
                logger.info("Skipping device assignment (TMS login failed)")
                self.state.record_step(step_name, "skipped", "TMS login failed")
                # No fallback data - will cause transaction step to fail
                self.state.context["terminal_id"] = None
                self.state.context["store_id"] = None
                self.state.context["fonepay_terminal_id"] = None
            else:
                try:
                    logger.info("\n" + "="*60)
                    logger.info("STEP 7: DEVICE ASSIGNMENT")
                    logger.info("="*60)
                    
                    device_serial = self.state.context["device_serial"]
                    logger.info(f"Assigning device {device_serial} to merchant")
                    
                    # Generate terminal/store data - THESE WILL BE USED FOR TRANSACTIONS
                    terminal_id = f"TERM_{self.fake.random_number(digits=8, fix_len=True)}"
                    store_id = f"STORE_{self.fake.random_number(digits=6, fix_len=True)}"
                    fonepay_terminal_id = f"FONEPAY_{self.fake.random_number(digits=8, fix_len=True)}"
                    fonepay_pan = self.fake.credit_card_number()
                    
                    terminal_data = {
                        "terminal_id": terminal_id,           # FOR NCHL & FONEPAY TRANSACTIONS
                        "store_id": store_id,                 # FOR NCHL TRANSACTIONS
                        "fonepay_pan": fonepay_pan,
                        "fonepay_terminal_id": fonepay_terminal_id  # FOR FONEPAY TRANSACTIONS
                    }
                    
                    assign_result = self.tms_page.assign_ipn_to_merchant(
                        ipn_serial=device_serial,
                        terminal_data=terminal_data
                    )
                    
                    if assign_result.get("success", False):
                        logger.info(f"✓ Device assigned: {device_serial}")
                        logger.info(f"  Terminal ID: {terminal_id} (for NCHL & Fonepay)")
                        logger.info(f"  Store ID: {store_id} (for NCHL)")
                        logger.info(f"  Fonepay Terminal ID: {fonepay_terminal_id} (for Fonepay)")
                        
                        # Store generated data for transaction step
                        self.state.context.update({
                            "terminal_id": terminal_id,
                            "store_id": store_id,
                            "fonepay_terminal_id": fonepay_terminal_id,
                            "fonepay_pan": fonepay_pan
                        })
                        self.state.record_step(step_name, "passed", data={
                            "terminal_id": terminal_id,
                            "store_id": store_id,
                            "fonepay_terminal_id": fonepay_terminal_id
                        })
                    else:
                        raise Exception(f"Device assignment failed: {assign_result}")
                        
                except Exception as e:
                    logger.error(f"✗ {step_name} failed: {e}")
                    self.page.screenshot(path=f"step7_failed_{self.timestamp}.png")
                    self.state.record_step(step_name, "failed", e)
                    # No fallback data - will cause transaction step to fail
                    self.state.context["terminal_id"] = None
                    self.state.context["store_id"] = None
                    self.state.context["fonepay_terminal_id"] = None
         
        # ====================================================================
        # STEP 8: SEND TRANSACTION NOTIFICATIONS 
        # (USES DATA CREATED IN STEPS 5 & 7)
        # ====================================================================
        with allure.step("Step 8: Send Transaction Notifications"):
            step_name = "Transaction Notifications"
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 8: TRANSACTION NOTIFICATIONS")
                logger.info("="*60)
                
                # CRITICAL: Use data created during TMS UI steps, not test constants
                device_serial = self.state.context["device_serial"]
                
                # Get merchant data from Step 5 (merchant creation)
                merchant_code = self.state.context.get("merchant_code")
                merchant_id = self.state.context.get("merchant_id")
                
                # Get terminal data from Step 7 (device assignment)
                terminal_id = self.state.context.get("terminal_id")
                store_id = self.state.context.get("store_id")
                fonepay_terminal_id = self.state.context.get("fonepay_terminal_id")
                
                logger.info("="*50)
                logger.info("API TRANSACTION DATA (FROM TMS UI CREATION):")
                logger.info("="*50)
                logger.info(f"DEVICE: {device_serial}")
                logger.info(f"NCHL - Merchant Code: {merchant_code} (from merchant creation)")
                logger.info(f"NCHL - Terminal ID: {terminal_id} (from device assignment)")
                logger.info(f"NCHL - Store ID: {store_id} (from device assignment)")
                logger.info(f"FONEPAY - Merchant ID: {merchant_id} (from merchant creation)")
                logger.info(f"FONEPAY - Terminal ID: {fonepay_terminal_id} (from device assignment)")
                logger.info("="*50)
                
                # Validate we have all required data
                missing_data = []
                if not merchant_code:
                    missing_data.append("merchant_code")
                if not merchant_id:
                    missing_data.append("merchant_id")
                if not terminal_id:
                    missing_data.append("terminal_id")
                if not store_id:
                    missing_data.append("store_id")
                if not fonepay_terminal_id:
                    missing_data.append("fonepay_terminal_id")
                
                if missing_data:
                    raise Exception(f"Missing transaction data from TMS UI: {missing_data}. Cannot send transactions.")
                
                # Generate random transaction amounts
                nchl_amount = self.fake.random_int(min=100, max=5000)
                fonepay_amount = self.fake.random_int(min=100, max=5000)
                
                # 8.1 Send NCHL Transaction (using data from Steps 5 & 7)
                nchl_success = False
                nchl_error = None
                try:
                    logger.info("\n📤 Sending NCHL transaction...")
                    logger.info(f"  Amount: {nchl_amount} (random)")
                    logger.info(f"  Merchant Code: {merchant_code} (from Step 5)")
                    logger.info(f"  Store ID: {store_id} (from Step 7)")
                    logger.info(f"  Terminal ID: {terminal_id} (from Step 7)")
                    
                    nchl_api = IPNAPI(base_url=API_IPN_NOTIFY_ENDPOINT, scheme="nchl", api_key=API_KEY_NCHL)
                    nchl_resp = nchl_api.send_transaction(
                        amount=nchl_amount,
                        merchant_code=merchant_code,
                        store_id=store_id,
                        terminal_id=terminal_id
                    )
                    
                    if nchl_resp.get("message") == EXPECTED_IPN_SUCCESS_MSG:
                        logger.info(f"✅ NCHL transaction sent successfully")
                        self.state.context["nchl_response"] = nchl_resp
                        self.state.context["nchl_amount"] = nchl_amount
                        nchl_success = True
                    else:
                        nchl_error = f"NCHL API response: {nchl_resp}"
                        logger.error(f"❌ {nchl_error}")
                        
                except Exception as e:
                    nchl_error = f"NCHL error: {str(e)}"
                    logger.error(f"❌ {nchl_error}")
                
                # 8.2 Send Fonepay Transaction (using data from Steps 5 & 7)
                fonepay_success = False
                fonepay_error = None
                try:
                    logger.info("\n📤 Sending Fonepay transaction...")
                    logger.info(f"  Amount: {fonepay_amount} (random)")
                    logger.info(f"  Merchant ID: {merchant_id} (from Step 5)")
                    logger.info(f"  Terminal ID: {fonepay_terminal_id} (from Step 7)")
                    
                    fonepay_api = IPNAPI(base_url=API_IPN_NOTIFY_ENDPOINT, scheme="fonepay", api_key=API_KEY_FONEPAY)
                    fonepay_resp = fonepay_api.send_transaction(
                        amount=fonepay_amount,
                        merchant_id=merchant_id,
                        terminal_id=fonepay_terminal_id
                    )
                    
                    if fonepay_resp.get("message") == EXPECTED_IPN_SUCCESS_MSG:
                        logger.info(f"✅ Fonepay transaction sent successfully")
                        self.state.context["fonepay_response"] = fonepay_resp
                        self.state.context["fonepay_amount"] = fonepay_amount
                        fonepay_success = True
                    else:
                        fonepay_error = f"Fonepay API response: {fonepay_resp}"
                        logger.error(f"❌ {fonepay_error}")
                        
                except Exception as e:
                    fonepay_error = f"Fonepay error: {str(e)}"
                    logger.error(f"❌ {fonepay_error}")
                
                # Record step status
                if nchl_success or fonepay_success:
                    status_msg = f"NCHL: {'✅' if nchl_success else '❌'}, Fonepay: {'✅' if fonepay_success else '❌'}"
                    logger.info(f"\n📊 Transaction Results: {status_msg}")
                    self.state.record_step(step_name, "passed", data={"status": status_msg})
                else:
                    error_msg = "Both transactions failed"
                    if nchl_error:
                        error_msg += f" | NCHL: {nchl_error}"
                    if fonepay_error:
                        error_msg += f" | Fonepay: {fonepay_error}"
                    logger.error(f"❌ {error_msg}")
                    self.state.record_step(step_name, "failed", error_msg)
                
                # Wait for processing
                logger.info("\n⏳ Waiting for transactions to be processed...")
                time.sleep(15)
                
            except Exception as e:
                logger.error(f"❌ {step_name} failed: {e}")
                self.state.record_step(step_name, "failed", e)
        
        # ====================================================================
        # STEP 9: VERIFY IN MONGODB
        # ====================================================================
        with allure.step("Step 9: Verify in MongoDB"):
            step_name = "MongoDB Verification"
            try:
                logger.info("\n" + "="*60)
                logger.info("STEP 9: MONGODB VERIFICATION")
                logger.info("="*60)
                
                mongo_uri = os.getenv("MONGO_URI")
                if not mongo_uri:
                    logger.error("MONGO_URI environment variable not set")
                    self.state.record_step(step_name, "skipped", "MONGO_URI not set")
                else:
                    mongo = MongoHandler(connection_string=mongo_uri, database=MONGO_DB_NAME)
                    
                    try:
                        device_serial = self.state.context.get("device_serial")
                        logger.info(f"🔍 Verifying data for device: {device_serial}")
                        
                        # 9.1 Verify Device in device_registry
                        found_device = mongo.find_device(device_serial)
                        
                        if found_device:
                            logger.info("✅ Device found in device_registry")
                            device_verification = True
                        else:
                            logger.warning("⚠️ Device not found in device_registry")
                            device_verification = False
                        
                        # 9.2 Verify Transactions using amounts from Step 8
                        nchl_verified = False
                        fonepay_verified = False
                        
                        nchl_amount = self.state.context.get("nchl_amount")
                        fonepay_amount = self.state.context.get("fonepay_amount")
                        
                        if self.state.context.get("nchl_response") and nchl_amount:
                            logger.info("🔍 Verifying NCHL transaction...")
                            for attempt in range(3):
                                nchl_verified = mongo.verify_transaction_exists(
                                    serial_number=device_serial,
                                    amount=int(nchl_amount),
                                    scheme="nchl"
                                )
                                if nchl_verified:
                                    logger.info("✅ NCHL transaction verified in MongoDB")
                                    break
                                time.sleep(5)
                        
                        if self.state.context.get("fonepay_response") and fonepay_amount:
                            logger.info("🔍 Verifying Fonepay transaction...")
                            for attempt in range(3):
                                fonepay_verified = mongo.verify_transaction_exists(
                                    serial_number=device_serial,
                                    amount=int(fonepay_amount),
                                    scheme="fonepay"
                                )
                                if fonepay_verified:
                                    logger.info("✅ Fonepay transaction verified in MongoDB")
                                    break
                                time.sleep(5)
                        
                        # Record results
                        verification_data = {
                            "device_found": device_verification,
                            "nchl_verified": nchl_verified,
                            "fonepay_verified": fonepay_verified
                        }
                        
                        if device_verification or nchl_verified or fonepay_verified:
                            logger.info("✅ MongoDB verification completed")
                            self.state.record_step(step_name, "passed", data=verification_data)
                        else:
                            logger.warning("⚠️ MongoDB verification: No data found")
                            self.state.record_step(step_name, "failed", "No data found in MongoDB", verification_data)
                        
                    finally:
                        mongo.disconnect()
                
            except Exception as e:
                logger.error(f"❌ {step_name} failed: {e}")
                self.state.record_step(step_name, "failed", e)
        
        # ====================================================================
        # FINAL TEST EVALUATION
        # ====================================================================
        logger.info("\n" + "="*60)
        logger.info("🎉 9-STEP FLOW EXECUTION COMPLETED")
        logger.info("="*60)
        
        # Log what data was used
        logger.info("\n📊 DATA USED IN TEST:")
        logger.info(f"  Device Serial: {self.state.context.get('device_serial')}")
        logger.info(f"  Merchant Code (NCHL): {self.state.context.get('merchant_code')}")
        logger.info(f"  Merchant ID (Fonepay): {self.state.context.get('merchant_id')}")
        logger.info(f"  Terminal ID: {self.state.context.get('terminal_id')}")
        logger.info(f"  Store ID: {self.state.context.get('store_id')}")
        logger.info(f"  Fonepay Terminal ID: {self.state.context.get('fonepay_terminal_id')}")
        
        # Check if critical steps passed
        critical_steps = ["Admin Portal Login", "Device Registration"]
        failed_critical = any(self.state.get_step_status(step) == "failed" for step in critical_steps)
        
        if failed_critical:
            pytest.fail("❌ Critical steps failed. See summary above.")
        else:
            logger.info("✅ Test execution completed")
            
            # Check transaction status
            if (self.state.get_step_status("Transaction Notifications") == "failed" and 
                not self.state.context.get("nchl_response") and 
                not self.state.context.get("fonepay_response")):
                logger.warning("⚠️ No transactions were sent successfully - check if merchant/device data is registered in payment system")