# test_dps_with_response.py
#!/usr/bin/env python
"""Test DPS API with the actual response format"""
import sys
sys.path.append('.')
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

from api.dps_api import DPSAPI
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dps_api():
    """Test DPS API with actual device"""
    
    print("\n" + "="*60)
    print(" DPS API TEST")
    print("="*60)
    
    # Initialize DPS API
    try:
        dps_api = DPSAPI(base_url="https://dps-staging.koilifin.com")
        print(f" DPS API initialized")
        print(f"   Base URL: {dps_api.base_url}")
        
        # Show headers (mask auth)
        headers = dict(dps_api.session.headers)
        if 'Authorization' in headers:
            headers['Authorization'] = headers['Authorization'][:20] + "..."
        if 'X-API-Key' in headers:
            headers['X-API-Key'] = headers['X-API-Key'][:10] + "..."
        print(f"   Headers: {headers}")
        
    except Exception as e:
        print(f" Failed to initialize DPS API: {e}")
        return
    
    # Test with your device serial
    test_serial = "38250820332278"  # From your Excel
    
    print(f"\n Testing with device: {test_serial}")
    
    try:
        # Send DPS request
        print(f" Sending DPS request to /ipn/provision...")
        response = dps_api.send_dps_request(test_serial)
        
        print(f"\n SUCCESS! DPS Response:")
        print(f"   Status: Success")
        print(f"   Host: {response.get('host')}")
        
        # Mask the key for security
        key = response.get('key', '')
        if key:
            print(f"   Key: {key[:20]}... (length: {len(key)} chars)")
        
        # Verify the response
        is_valid = dps_api.verify_dps_response(response, test_serial)
        print(f"   Verification: {' PASS' if is_valid else ' FAIL'}")
        
        # Extract IoT Hub details
        iot_details = dps_api.extract_iot_hub_details(response)
        if iot_details.get('is_valid'):
            print(f"\n IoT Hub Connection Details:")
            print(f"   IoT Hub Host: {iot_details.get('iot_hub_host')}")
            print(f"   Connection String (partial): {iot_details.get('connection_string')[:50]}...")
        
    except Exception as e:
        print(f"\n FAILED! Error: {e}")
        
        # Check for common errors
        error_msg = str(e).lower()
        if any(err in error_msg for err in ['401', '403', 'unauthorized', 'forbidden']):
            print("\n AUTHENTICATION ERROR!")
            print("Possible issues:")
            print("1. DPS_AUTH_TOKEN not set in .env file")
            print("2. Token is expired or invalid")
            print("3. Incorrect token format")
            
            current_token = os.getenv("DPS_AUTH_TOKEN", "NOT_SET")
            if current_token == "NOT_SET":
                print(f"   Current token: NOT SET")
            else:
                print(f"   Current token (first 20 chars): {current_token[:20]}...")
    
    # Test health check
    print(f"\n🩺 Health Check:")
    is_healthy = dps_api.health_check()
    print(f"   API Health: {' Healthy' if is_healthy else ' Not Healthy'}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

def simulate_dps_response():
    """Simulate the DPS response you provided"""
    print("\n🔧 SIMULATED DPS RESPONSE (for reference):")
    simulated_response = {
        "key": "w/jP/S33ZUYcBI+lZfUlwOenp38p8PAwuogH0qhprew=",
        "host": "koili-iot-staging.azure-devices.net"
    }
    
    print(json.dumps(simulated_response, indent=2))
    
    # Analyze the response
    print("\n RESPONSE ANALYSIS:")
    print(f"   Key length: {len(simulated_response['key'])} characters")
    print(f"   Key appears to be: Base64 encoded SharedAccessSignature")
    print(f"   Host: Azure IoT Hub instance")
    print(f"   Full IoT Hub URL: https://{simulated_response['host']}")
    
    return simulated_response

if __name__ == "__main__":
    # First show what we expect
    simulate_dps_response()
    
    # Then run actual test
    test_dps_api()