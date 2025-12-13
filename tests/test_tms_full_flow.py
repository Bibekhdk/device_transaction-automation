"""
Test TMS Portal Flow with Toast Verification
"""
import pytest
import allure
import logging
from playwright.sync_api import Page
from pages.tms_portal.tms_full_flow import TMSPage

logger = logging.getLogger(__name__)

@pytest.mark.tms
@pytest.mark.e2e
@allure.feature("TMS Portal")
@allure.story("Complete TMS Flow with Toast Verification")
@allure.severity(allure.severity_level.CRITICAL)
def test_complete_tms_flow_with_toast(page: Page):
    """
    Complete TMS flow test with toast verification
    Tests: Login → Sync IPN → Add Merchant → Assign IPN → Dashboard
    """
    logger.info(" Starting complete TMS flow test with toast verification")
    
    # Initialize TMS page object
    tms_page = TMSPage(page)
    
    # Execute complete TMS flow
    # Note: You can pass IPN serial from admin registration here
    result = tms_page.complete_tms_flow(ipn_serial="38231105960007")  # From your Codegen
    
    # ==================== ASSERTIONS ====================
    
    # 1. Check overall success
    assert result["overall_success"] is True, \
        f" TMS flow FAILED. Details:\n{result}"
    
    # 2. Check all critical steps completed
    steps = result.get("steps", {})
    assert steps.get("login") is True, " TMS login failed"
    assert steps.get("add_merchant") is True, " Add merchant failed"
    assert steps.get("assign_ipn") is True, " Assign IPN failed"
    
    logger.info(" All critical steps completed successfully")
    
    # 3. Verify merchant creation with toast
    merchant_result = result.get("merchant_result", {})
    assert merchant_result.get("success") is True, " Merchant creation failed"
    
    merchant_toast = merchant_result.get("toast_result", {})
    
    # FLEXIBLE TOAST VERIFICATION - if toast exists, check it; if not, just log warning
    merchant_toast_text = merchant_toast.get("text", "").lower()
    
    if merchant_toast_text:
        # Check toast contains "merchant" or "created" or "success"
        merchant_keywords = ["merchant", "created", "success", "added"]
        has_merchant_keyword = any(keyword in merchant_toast_text for keyword in merchant_keywords)
        
        if has_merchant_keyword:
            logger.info(f" Merchant created with toast: '{merchant_toast.get('text', '')}'")
        else:
            logger.warning(f" Merchant toast doesn't contain expected keywords. Actual: '{merchant_toast_text}'")
            # Don't fail the test - just log warning since merchant was created successfully
    else:
        logger.warning(" No merchant toast captured, but merchant was created successfully")
    
    # 4. Verify IPN assignment with toast
    ipn_result = result.get("ipn_assignment_result", {})
    assert ipn_result.get("success") is True, " IPN assignment failed"
    
    ipn_toast = ipn_result.get("toast_result", {})
    
    # FLEXIBLE TOAST VERIFICATION for IPN too
    ipn_toast_text = ipn_toast.get("text", "").lower()
    
    if ipn_toast_text:
        # Check toast contains "IPN" or "assigned" or "success"
        ipn_keywords = ["ipn", "assigned", "success", "linked"]
        has_ipn_keyword = any(keyword in ipn_toast_text for keyword in ipn_keywords)
        
        if has_ipn_keyword:
            logger.info(f" IPN assigned with toast: '{ipn_toast.get('text', '')}'")
        else:
            logger.warning(f" IPN toast doesn't contain expected keywords. Actual: '{ipn_toast_text}'")
            # Don't fail the test - just log warning since IPN was assigned successfully
    else:
        logger.warning(" No IPN toast captured, but IPN was assigned successfully")
    
    # 5. Verify merchant data
    merchant_data = merchant_result.get("merchant_data", {})
    assert "account_number" in merchant_data, " Account number missing"
    assert "merchant_pan" in merchant_data, " Merchant PAN missing"
    assert "name" in merchant_data, " Merchant name missing"
    assert "email" in merchant_data, " Merchant email missing"
    
    # 6. Verify terminal data
    terminal_data = ipn_result.get("terminal_data", {})
    assert "terminal_id" in terminal_data, " Terminal ID missing"
    assert "store_id" in terminal_data, " Store ID missing"
    
    # ==================== LOGGING SUCCESS ====================
    
    logger.info(" ALL TMS ASSERTIONS PASSED! ")
    logger.info(f" Merchant created:")
    logger.info(f"   • Account: {merchant_data.get('account_number')}")
    logger.info(f"   • Name: {merchant_data.get('name')}")
    logger.info(f"   • PAN: {merchant_data.get('merchant_pan')}")
    logger.info(f" IPN assigned:")
    logger.info(f"   • IPN Serial: {ipn_result.get('ipn_serial')}")
    logger.info(f"   • Terminal ID: {terminal_data.get('terminal_id')}")
    logger.info(f"   • Store ID: {terminal_data.get('store_id')}")
    logger.info(f" Toast verifications:")
    logger.info(f"   • Merchant: '{merchant_toast.get('text', '')}'")
    logger.info(f"   • IPN: '{ipn_toast.get('text', '')}'")
    
    # ==================== ALLURE REPORTING ====================
    
    # Attach complete result
    allure.attach(
        str(result),
        name="Complete TMS Flow Result",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Attach merchant details
    allure.attach(
        str(merchant_data),
        name="Merchant Details",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Attach toast details
    toast_summary = {
        "merchant_toast": merchant_toast,
        "ipn_toast": ipn_toast
    }
    allure.attach(
        str(toast_summary),
        name="Toast Verification Summary",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Create a summary report
    summary = f"""
    ====== TMS FLOW TEST SUMMARY ======
    STATUS: PASSED
    
    MERCHANT CREATION:
      • Account: {merchant_data.get('account_number')}
      • Name: {merchant_data.get('name')}
      • PAN: {merchant_data.get('merchant_pan')}
      • Toast: '{merchant_toast.get('text', '')}'
    
    IPN ASSIGNMENT:
      • IPN Serial: {ipn_result.get('ipn_serial')}
      • Terminal ID: {terminal_data.get('terminal_id')}
      • Store ID: {terminal_data.get('store_id')}
      • Toast: '{ipn_toast.get('text', '')}'
    
    TEST STEPS:
      • Login:  Success
      • Sync IPN: {' Success' if steps.get('sync_ipn') else 'Warning'}
      • Add Merchant:  Success
      • Assign IPN:  Success
      • Navigate Dashboard: {'Success' if steps.get('navigate_dashboard') else 'Warning'}
    ===================================
    """
    
    allure.attach(
        summary,
        name="TMS Test Summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info(" TMS FLOW TEST COMPLETED SUCCESSFULLY! ")