"""
Single Test: Complete Device Registration with Toast Capture
"""
import pytest
import allure
import logging
from playwright.sync_api import Page
from pages.admin_portal.device_registration_page import DeviceRegistrationPage

logger = logging.getLogger(__name__)

@pytest.mark.device
@pytest.mark.e2e
@allure.feature("Device Registration")
@allure.story("Complete Registration Flow with Toast Capture")
@allure.severity(allure.severity_level.CRITICAL)
def test_complete_device_registration_with_toast(page: Page):
    """
    SINGLE TEST: Complete device registration with exact toast verification
    Verifies that "device added" toast appears after successful registration
    """
    logger.info("🚀🚀🚀 Starting SINGLE test: Complete device registration with toast capture")
    
    # Initialize page object
    device_page = DeviceRegistrationPage(page)
    
    # Execute complete flow
    result = device_page.complete_registration_with_toast(customer="Anugya")
    
    # ==================== ASSERTIONS ====================
    
    # 1. Check overall success
    assert result["overall_success"] is True, \
        f"❌ Registration FAILED. Details:\n{result}"
    
    # 2. Check all steps completed successfully
    steps = result.get("steps", {})
    assert steps.get("login") is True, "❌ Login step failed"
    assert steps.get("navigate_to_device") is True, "❌ Navigation to device section failed"
    assert steps.get("open_form") is True, "❌ Open add device form failed"
    assert steps.get("fill_form") is True, "❌ Fill device form failed"
    assert steps.get("submit_form") is True, "❌ Submit form failed"
    
    logger.info("✅ All steps completed successfully")
    
    # 3. Verify device data
    device_data = result.get("device_data", {})
    assert "sim" in device_data, "❌ SIM number not generated"
    assert len(device_data["sim"]) == 10, f"❌ SIM should be 10 digits, got: {device_data['sim']}"
    assert "serial" in device_data, "❌ Serial number not generated"
    assert len(device_data["serial"]) == 10, f"❌ Serial should be 10 digits, got: {device_data['serial']}"
    assert "imei" in device_data, "❌ IMEI not generated"
    assert len(device_data["imei"]) == 15, f"❌ IMEI should be 15 digits, got: {device_data['imei']}"
    assert device_data["customer"] == "Anugya", f"❌ Wrong customer: {device_data.get('customer')}"
    assert device_data["batch"] == "testautomation", f"❌ Wrong batch: {device_data.get('batch')}"
    
    logger.info(f"✅ Device data verified: SIM={device_data.get('sim')}, Serial={device_data.get('serial')}")
    
    # 4. EXACT TOAST VERIFICATION - Most Important!
    toast_result = result.get("toast_result", {})
    
    # 4a. Check toast was captured
    assert toast_result.get("success") is True, \
        f"❌ Toast NOT captured: {toast_result.get('error', 'Unknown error')}"
    
    # 4b. Check toast contains "device added" (case insensitive)
    assert toast_result.get("contains_device_added") is True, \
        f"❌ Toast should contain 'device added'. Actual toast text: '{toast_result.get('text', 'NO TEXT')}'"
    
    # 4c. Log the exact toast text
    toast_text = toast_result.get("text", "")
    logger.info(f"✅ Toast captured: '{toast_text}'")
    
    # 4d. Check if it's exact match (optional)
    if toast_result.get("is_exact_match"):
        logger.info("✅ Perfect! Toast text is exactly 'device added'")
    else:
        logger.info(f"ℹ️  Toast contains 'device added' but full text is: '{toast_text}'")
    
    # 4e. Check wait time was recorded
    wait_time = toast_result.get("wait_time_ms", 0)
    assert wait_time > 0, "❌ Toast wait time not recorded"
    logger.info(f"✅ Toast appeared in {wait_time}ms")
    
    # ==================== LOGGING SUCCESS ====================
    
    logger.info("🎉🎉🎉 ALL ASSERTIONS PASSED! 🎉🎉🎉")
    logger.info(f"📋 Device registered successfully!")
    logger.info(f"   • SIM: {device_data.get('sim')}")
    logger.info(f"   • Serial: {device_data.get('serial')}")
    logger.info(f"   • IMEI: {device_data.get('imei')}")
    logger.info(f"   • Customer: {device_data.get('customer')}")
    logger.info(f"🎯 Toast verified: '{toast_text}'")
    
    # ==================== ALLURE REPORTING ====================
    
    # Attach complete result
    allure.attach(
        str(result),
        name="Complete Registration Result",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Attach device data
    allure.attach(
        str(device_data),
        name="Registered Device Data",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Attach toast details
    allure.attach(
        str(toast_result),
        name="Toast Verification Details",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Create a summary report
    summary = f"""
    ====== TEST SUMMARY ======
    STATUS: ✅ PASSED
    DEVICE: 
      • SIM: {device_data.get('sim')}
      • Serial: {device_data.get('serial')}
      • IMEI: {device_data.get('imei')}
      • Customer: {device_data.get('customer')}
    TOAST:
      • Text: '{toast_text}'
      • Contains 'device added': ✅ YES
      • Wait time: {wait_time}ms
    ==========================
    """
    
    allure.attach(
        summary,
        name="Test Summary",
        attachment_type=allure.attachment_type.TEXT
    )
    
    logger.info("🏁🏁🏁 TEST COMPLETED SUCCESSFULLY! 🏁🏁🏁")