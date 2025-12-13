"""
Debug test to isolate the TargetClosedError
"""
import pytest
import logging
from playwright.sync_api import Page
import time

logger = logging.getLogger(__name__)

def test_debug_simple_login(page: Page):
    """Simple test to debug the page issue"""
    logger.info("Starting debug test")
    
    # Navigate
    page.goto("https://admin-staging.koilifin.com/")
    logger.info(f"Page title: {page.title()}")
    logger.info(f"Page URL: {page.url}")
    
    # Wait for page to load
    page.wait_for_load_state("networkidle")
    
    # Check if page is usable
    assert not page.is_closed(), "Page is closed!"
    
    # Try simple interaction
    email_field = page.get_by_role("textbox", name="Email Address")
    email_field.wait_for(state="visible", timeout=10000)
    email_field.fill("anugya@koilifin.com")
    
    logger.info("✅ Debug test passed - Page is usable")
    
    # Take screenshot
    page.screenshot(path="./debug_simple_login.png")
    time.sleep(2)  # Keep browser open to see