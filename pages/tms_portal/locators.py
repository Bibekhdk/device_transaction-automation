"""
Locators for TMS Portal
"""

class TMSLocators:
    # Login
    LOGIN_USERNAME = {"role": "textbox", "name": "Username"}
    LOGIN_PASSWORD = {"role": "textbox", "name": "password"}
    LOGIN_BUTTON = {"role": "button", "name": "Sign In"}
    LOGIN_VERIFY_BTN = {"role": "button", "name": "IPN", "exact": True}
    
    # Dashboard / Navigation
    NAV_IPN = {"role": "button", "name": "IPN", "exact": True}
    NAV_MERCHANT = {"role": "button", "name": "Merchant", "exact": True}
    NAV_DASHBOARD = {"role": "button", "name": "Dashboard"}
    
    # IPN Management
    IPN_SYNC_BUTTON = {"role": "button", "name": "Sync IPN"}
    IPN_ASSIGNED_MENU = {"role": "menuitem", "name": "Assigned IPNs"}
    IPN_ASSIGN_BUTTON = {"role": "button", "name": "Assign IPN"}
    IPN_SEARCH_FIELD = {"role": "textbox", "name": "Search IPN"}
    
    IPN_ROW = "role=row" # Simplified for logic use
    IPN_SELECT_ROW_CHECKBOX = {"label": "Select row"}
    IPN_SCHEMA_ICON = "SchemaIcon" # TestID
    
    # Merchant Management
    MERCHANT_ADD_BUTTON = {"role": "button", "name": "Add Merchant"}
    
    # Merchant Form
    MERCHANT_ACCOUNT = {"role": "textbox", "name": "Account Number"}
    MERCHANT_PAN = {"role": "textbox", "name": "Merchant PAN"}
    MERCHANT_BRANCH_DROPDOWN = {"role": "combobox", "name": "Branch"}
    MERCHANT_SCHEME_DROPDOWN = {"role": "combobox", "name": "Scheme"}
    
    MERCHANT_SCHEME_OPTION_FONEPAY = {"role": "option", "name": "Fonepay"}
    MERCHANT_SCHEME_OPTION_NCHL = {"role": "option", "name": "NCHL"}
    
    MERCHANT_CODE = {"role": "textbox", "name": "Merchant Code"}
    MERCHANT_ID = {"role": "textbox", "name": "Merchant .I.D."}
    MERCHANT_NAME = {"role": "textbox", "name": "Name"}
    MERCHANT_EMAIL = {"role": "textbox", "name": "Email"}
    MERCHANT_ADDRESS = {"role": "textbox", "name": "Address"}
    MERCHANT_PHONE = {"role": "textbox", "name": "Phone"}
    
    MERCHANT_SUBMIT_BUTTON = {"role": "button", "name": "Add"}
    
    # Assign IPN To Merchant Form
    EXPAND_MERCHANT_BUTTON = "#expand-more-button-0"
    
    ASSIGN_TERMINAL_ID = {"role": "textbox", "name": "Terminal I.D."}
    ASSIGN_STORE_ID = {"role": "textbox", "name": "Store I.D."}
    ASSIGN_FONEPAY_PAN = {"role": "textbox", "name": "Fonepay Pan Number"}
    
    ASSIGN_UPDATE_BUTTON = {"role": "button", "name": "Update"}
    ASSIGN_FINAL_BUTTON = {"role": "button", "name": "Assign"}
    
    # Toast / Alerts
    TOAST_MESSAGE = "[role='alert']"
    SUCCESS_TOAST = "Merchant created successfully"
    MERCHANT_EXISTS_TOAST = "Merchant already exists"
    ACCOUNT_ASSOCIATED_DIFFERENT_PAN_TOAST = "This account number is already associated with a different PAN"
    
    TOAST_SYNC_UP_TO_DATE = "everything up to date"
    TOAST_SYNC_DEVICE_ADDED = "device added"
    
    TOAST_ASSIGN_IDENTIFIERS = "identifiers added"
    TOAST_ASSIGN_SUCCESS = "device assigned successfully"
    
    ALERT = {"role": "alert"}
