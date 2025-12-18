"""
Locators for Admin Portal
"""

class AdminLocators:
    # Login
    LOGIN_EMAIL = {"role": "textbox", "name": "Email Address"}
    LOGIN_PASSWORD = {"role": "textbox", "name": "Password"}
    LOGIN_BUTTON = {"role": "button", "name": "Sign in", "exact": True}
    LOGIN_VERIFY_TEXT = "Koili"
    
    # Navigation
    NAV_DEVICE = {"role": "button", "name": "Device"}
    
    # Device Registration List
    ADD_DEVICE_BUTTON = {"role": "button", "name": "Add"}
    
    # Device Registration Form
    FORM_SIM = {"role": "textbox", "name": "SIM"}
    FORM_MODEL_DROPDOWN = {"role": "combobox", "name": "Model"}
    FORM_MODEL_OPTION = {"role": "option", "name": "ET389 static"}
    
    # Selector for Customer dropdown
    FORM_CUSTOMER_DROPDOWN = {"role": "combobox", "name": "​", "exact": True}
    FORM_CUSTOMER_TEST = {"role": "option", "name": "Test"}   #use this during test
    # FORM_CUSTOMER_BITSKRAFT = {"role": "option", "name": "Bitskraft Private Limited"} use this during real tests
    
  
    FORM_LANGUAGE_DROPDOWN = {"role": "combobox", "name": "Language"}
    FORM_LANGUAGE_OPTION = {"role": "option", "name": "Nepali"}
    
    FORM_SERIAL = {"role": "textbox", "name": "Serial Number"}
    FORM_IMEI = {"role": "textbox", "name": "IMEI"}
    FORM_BATCH = {"role": "textbox", "name": "Batch"}
    
    FORM_SUBMIT_BUTTON = {"role": "button", "name": "Add"}
    FORM_CONFIRM_BUTTON = "[id='1']"  # Odd selector but from legacy code
    
    # Toasts
    TOAST_CONTAINER = ".Toastify__toast-container"
    TOAST_SUCCESS = ".Toastify__toast--success"
    TOAST_DEVICE_ADDED = "device added"
