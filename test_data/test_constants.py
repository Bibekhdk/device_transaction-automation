import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- Shared Test Data for E2E Flow ---

# Device Data
# Using a generated serial number logic in the test, but keeping a constant for reference/fallback
TEST_SERIAL_NUMBER = "38250820332270" 
TEST_MODEL_NAME = "ET389 static"
# IMEI will be generated randomly in the test

# Merchant & Scheme Data
# Dynamic name will be generated in the test
TEST_MERCHANT_CODE_NCHL = "merchant32322244"
TEST_MERCHANT_ID_FONEPAY = "fonepay032928383"

# Device Assignment Data (Created in TMS UI)
TEST_STORE_ID = "storeid32"
TEST_TERMINAL_ID_NCHL = "terminalid32"
TEST_TERMINAL_ID_FONEPAY = "fonepaycode32"

# Transaction Data
NCHL_TRANSACTION_AMOUNT = "12121"
FONEPAY_TRANSACTION_AMOUNT = "242432"

# API Configuration
# DPS
DPS_AUTH_TOKEN = os.getenv("DPS_AUTH_TOKEN")
if not DPS_AUTH_TOKEN:
    raise ValueError("DPS_AUTH_TOKEN not found in environment variables")

API_DPS_ENDPOINT = "https://dps-staging.koilifin.com" # Assuming this is the correct base URL based on previous context or defaults
# IPN
API_IPN_NOTIFY_ENDPOINT = "https://ipn-dev.qrsoundboxnepal.com/api/v1-stg/notify"

# API Keys (SENSITIVE)
API_KEY_NCHL = os.getenv("API_KEY_NCHL")
if not API_KEY_NCHL:
    raise ValueError("API_KEY_NCHL not found in environment variables")

API_KEY_FONEPAY = os.getenv("API_KEY_FONEPAY")
if not API_KEY_FONEPAY:
    raise ValueError("API_KEY_FONEPAY not found in environment variables")

# MongoDB Configuration
# User provided: mongodb://your_user:your_password@your_host:port/
# Assuming env var or secure vault in real life, but user asked to use constants.
# Since I cannot know the real password from the prompt (it said "credentials required" but didn't provide DB password in the text explicitly, only UI passwords),
# I will assume the environment variable MONGO_URI is set, or I will use a placeholder that the user must replace.
# However, the user said "Credentials Required: ... Secure storage ...".
# And in Step 10 request: "see all my code ...".
# Existing `mongo_handler.py` uses `os.getenv("MONGO_URI")`.
# I will rely on `os.getenv("MONGO_URI")` being present in the user's environment or .env file.
# If it's missing, the test will fail, but that's expected if config is missing.
MONGO_DB_NAME = "koili_staging"
MONGO_DEVICE_COLLECTION = "device_registry"
MONGO_AUDIT_COLLECTION = "registry_audit"

# Validations
EXPECTED_IPN_SUCCESS_MSG = "notification delivered successfully"
