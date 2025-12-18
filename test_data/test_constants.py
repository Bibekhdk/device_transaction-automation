import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- Shared Test Data for E2E Flow ---

TEST_MODEL_NAME = "ET389 static"
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

MONGO_DB_NAME = "koili_staging"
MONGO_DEVICE_COLLECTION = "device_registry"
MONGO_AUDIT_COLLECTION = "registry_audit"

# Validations
EXPECTED_IPN_SUCCESS_MSG = "notification delivered successfully"
