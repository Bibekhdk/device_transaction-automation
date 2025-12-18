import json
import os
import logging

STATE_FILE = "test_state.json"
logger = logging.getLogger(__name__)

def save_test_state(data: dict):
    """Saves dictionary data to a JSON file for persistence between test runs."""
    try:
        # Load existing state if any to merge
        existing_data = load_test_state()
        existing_data.update(data)
        
        with open(STATE_FILE, 'w') as f:
            json.dump(existing_data, f, indent=4)
        logger.info(f"State saved to {STATE_FILE}: {data.keys()}")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

def load_test_state() -> dict:
    """Loads data from the JSON state file."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return {}
