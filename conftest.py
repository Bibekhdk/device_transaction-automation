"""
Pytest configuration and fixtures
"""
import pytest
from playwright.sync_api import Page, BrowserContext, Browser
import allure
import logging

logger = logging.getLogger(__name__)

# ==================== PLAYWRIGHT FIXTURES ====================

@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }

@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args):
    """Create context for each test"""
    context = browser.new_context(**browser_context_args)
    
    # Grant permissions if needed
    context.grant_permissions(['clipboard-read', 'clipboard-write'])
    
    yield context
    
    # Close context
    try:
        context.close()
    except:
        pass

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Create page for each test - MUST be function scope"""
    page = context.new_page()
    
    # Set timeouts
    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)
    
    yield page
    
    # Clean up - but don't force close if test is still using it
    try:
        if not page.is_closed():
            page.close()
    except:
        pass

# ==================== PAGE OBJECT FIXTURES ====================

@pytest.fixture(scope="function")
def device_page(page: Page):
    """Provide DeviceRegistrationPage instance"""
    from pages.admin_portal.device_registration_page import DeviceRegistrationPage
    return DeviceRegistrationPage(page)

# ==================== HOOKS FOR DEBUGGING ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take screenshot on test failure"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        try:
            # Check if page fixture exists
            if "page" in item.funcargs:
                page = item.funcargs["page"]
                if not page.is_closed():
                    screenshot = page.screenshot(full_page=True)
                    allure.attach(screenshot, name="failure_screenshot",
                                attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            logger.warning(f"Could not take failure screenshot: {e}")

# ==================== TEST SETUP/TEARDOWN ====================

@pytest.fixture(scope="function", autouse=True)
def setup_teardown(page: Page):
    """Setup and teardown for each test"""
    logger.info("=== Test Setup ===")
    
    # Setup
    yield
    
    # Teardown
    logger.info("=== Test Teardown ===")
    try:
        # Take final screenshot
        if not page.is_closed():
            page.screenshot(path=f"./screenshots/final_{pytest.current_test_name}.png")
    except:
        pass