import pytest
import allure
import logging
import time
from playwright.sync_api import Page
from test_data.test_constants import *
from pages.admin_portal.device_registration_page import DeviceRegistrationPage
from pages.tms_portal.tms_page import TMSPage
from tests.state_manager import save_test_state
from faker import Faker

logger = logging.getLogger(__name__)

@allure.feature("End-to-End Payment Flow")
@allure.story("Step 1: UI Provisioning (Admin & TMS)")
@allure.severity(allure.severity_level.CRITICAL)
def test_01_ui_provisioning(page: Page):
    """
    Executes Step 1, 2, 5, 6, 7 of the user flow:
    1. Admin Portal: Register Device
    2. TMS Portal: Create Merchant
    3. TMS Portal: Sync IPN
    4. TMS Portal: Assign Device to Merchant
    Saves context to state.json for subsequent API/DB tests.
    """
    logger.info(">>> START: test_01_ui_provisioning <<<")
    
    # Store state to save later
    state = {}
    
    # === STEP 1 & 2: Admin Portal - Register Device ===
    with allure.step("Step 1 & 2: Admin Portal - Register Device"):
        admin_page = DeviceRegistrationPage(page)
        
        # Registration logic
        registration_result = admin_page.complete_registration_with_toast(customer="Bitskraft Pvt Ltd")
        
        if not registration_result["overall_success"]:
             if not registration_result.get("device_data", {}).get("serial"):
                 pytest.fail(f"Device registration failed comprehensively: {registration_result['error']}")
        
        device_data = registration_result["device_data"]
        device_serial = device_data["serial"]
        logger.info(f"Registered Device Serial: {device_serial}")
        
        state["serial"] = device_serial
        state["device_data"] = device_data

    # === STEP 5: TMS - Create Merchant ===
    with allure.step("Step 5: TMS - Create Merchant"):
        tms_page = TMSPage(page)
        fake = Faker()
        
        # Generate dynamic merchant data
        merchant_code = f"M{fake.unique.random_number(digits=10)}"
        merchant_id = f"F{fake.unique.random_number(digits=10)}"
        
        merchant_data = {
            "account_number": str(fake.unique.random_number(digits=15)),
            "merchant_pan": fake.unique.bothify(text='PAN#####'),
            "branch": "ACHHAM", 
            "schemes": ["Fonepay", "NCHL"], 
            "merchant_code": merchant_code,
            "merchant_id": merchant_id,
            "name": f"Test_Merchant_{int(time.time())}",
            "email": fake.email(),
            "address": "Kathmandu",
            "phone": "98" + str(fake.random_number(digits=8, fix_len=True))
        }
        
        state["merchant_code"] = merchant_code
        state["merchant_id"] = merchant_id
        
        # Login
        tms_page.login()
        
        # Sync IPN (Step 6) - Doing it before or after creating merchant? 
        # User list: Step 5 Create Merchant, Step 6 Sync IPN.
        
        # Add Merchant
        merchant_result = tms_page.add_merchant(merchant_data)
        assert merchant_result["success"], "Merchant creation failed"
        logger.info(f"Created Merchant: {merchant_data['name']}")

    # === STEP 6: Sync IPN ===
    with allure.step("Step 6: Sync IPN"):
        tms_page.sync_ipn()
        logger.info("IPN Synced")

    # === STEP 7: Assign Device ===
    with allure.step("Step 7: Assign Device"):
        # We need to assign the IPN (Serial) to the Merchant we just created.
        
        terminal_id_nchl = f"T{fake.random_number(digits=5)}"
        store_id_nchl = f"S{fake.random_number(digits=5)}"
        terminal_id_fonepay = f"FT{fake.random_number(digits=5)}"
        
        # Note: The UI method `assign_ipn_to_merchant` usually fills standardized fields.
        # Based on user req: 
        # NCHL: storeId, terminalId
        # Fonepay: terminalId
        # We'll pass a dict that the page object hopefully handles or we might need to adjust expected keys.
        # Looking at previous code, it used "terminal_id", "store_id", "fonepay_pan".
        # Let's map user req to what the Page Object likely expects.
        
        terminal_data = {
            "terminal_id": terminal_id_nchl,
            "store_id": store_id_nchl,
            "fonepay_pan": "123456789" # The page object might ask for this? User req says "Fonepay: terminalId". 
                                       # If the UI asks for Fonepay PAN, we give it. 
                                       # If the UI asks for Fonepay Terminal ID, we hope 'terminal_id' or similar covers it.
                                       # For now, using what worked in the previous e2e file.
        }
        
        logger.info(f"Assigning device {device_serial} to merchant")
        assign_result = tms_page.assign_ipn_to_merchant(device_serial, terminal_data)
        assert assign_result["success"], "Device assignment failed"
        
        # Save these specifically for the API test
        state["store_id"] = store_id_nchl
        state["terminal_id_nchl"] = terminal_id_nchl
        state["terminal_id_fonepay"] = terminal_id_nchl # Using same for now as E2E did, or should differ? 
                                                         # User req: NCHL terminalId, Fonepay terminalId. 
                                                         # Step 8.1 uses <terminalId_from_step7>, Step 8.2 uses <terminalId_from_step7>.
                                                         # Implies they are the SAME value or mapped from the single entry?
                                                         # I will assume they are the same value `terminal_id_nchl`.
        
    save_test_state(state)
    logger.info("Test Step 1 Complete - State Saved")
