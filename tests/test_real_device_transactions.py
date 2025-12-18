import pytest
import allure
import logging
import time
import os
from test_data.test_constants import *
from api.ipn_api import IPNAPI
from database.mongo_handler import MongoHandler

logger = logging.getLogger(__name__)

@pytest.mark.real_device
@allure.feature("Real Device Transaction Verification")
def test_real_device_transactions():
    """
    Verify that transactions can be sent and recorded for a real device/merchant setup.
    Skips UI setup as the merchant and device are already linked.
    """
    
    serial_number = TEST_SERIAL_NUMBER
    logger.info(f" Starting Transaction Verification for Serial: {serial_number}")
    
    # === STEP 1: Send NCHL Transaction ===
    with allure.step("Step 1: Send NCHL Transaction"):
        logger.info(f"Sending NCHL Transaction... Amount: {NCHL_TRANSACTION_AMOUNT}")
        
        nchl_api = IPNAPI(base_url=API_IPN_NOTIFY_ENDPOINT, scheme="nchl", api_key=API_KEY_NCHL)
        nchl_resp = nchl_api.send_transaction(
            amount=NCHL_TRANSACTION_AMOUNT,
            merchant_code=TEST_MERCHANT_CODE_NCHL,
            store_id=TEST_STORE_ID,
            terminal_id=TEST_TERMINAL_ID_NCHL
        )
        
        logger.info(f"NCHL Response: {nchl_resp}")
        assert nchl_resp.get("message") == EXPECTED_IPN_SUCCESS_MSG, f"NCHL Transaction Failed: {nchl_resp}"

    # === STEP 2: Send Fonepay Transaction ===
    with allure.step("Step 2: Send Fonepay Transaction"):
        logger.info(f"Sending Fonepay Transaction... Amount: {FONEPAY_TRANSACTION_AMOUNT}")
        
        # Note: Fonepay usually requires just Terminal ID and Merchant ID? 
        # Using the constants provided by user.
        fonepay_api = IPNAPI(base_url=API_IPN_NOTIFY_ENDPOINT, scheme="fonepay", api_key=API_KEY_FONEPAY)
        fonepay_resp = fonepay_api.send_transaction(
            amount=FONEPAY_TRANSACTION_AMOUNT,
            merchant_id=TEST_MERCHANT_ID_FONEPAY,
            terminal_id=TEST_TERMINAL_ID_FONEPAY
        )
        
        logger.info(f"Fonepay Response: {fonepay_resp}")
        assert fonepay_resp.get("message") == EXPECTED_IPN_SUCCESS_MSG, f"Fonepay Transaction Failed: {fonepay_resp}"

    # === STEP 3: Verify Transactions in MongoDB ===
    with allure.step("Step 3: Verify in MongoDB (registry_audit)"):
        logger.info("Waiting for transactions to propagate to DB...")
        time.sleep(10) 
        
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            pytest.fail("MONGO_URI not set")
            
        mongo = MongoHandler(connection_string=mongo_uri, database=MONGO_DB_NAME)
        
        try:
            # Verify NCHL
            logger.info("Verifying NCHL Transaction...")
            found_nchl = mongo.verify_transaction_exists(
                serial_number=serial_number,
                amount=int(NCHL_TRANSACTION_AMOUNT),
                scheme="nchl"
            )
            assert found_nchl, "NCHL Transaction NOT found in MongoDB!"
            logger.info(" NCHL Transaction Verified")
            
            # Verify Fonepay
            logger.info("Verifying Fonepay Transaction...")
            found_fonepay = mongo.verify_transaction_exists(
                serial_number=serial_number,
                amount=int(FONEPAY_TRANSACTION_AMOUNT),
                scheme="fonepay"
            )
            assert found_fonepay, "Fonepay Transaction NOT found in MongoDB!"
            logger.info(" Fonepay Transaction Verified")
            
        finally:
            mongo.disconnect()
            
    logger.info(" REAL DEVICE TRANSACTION TEST PASSED")
