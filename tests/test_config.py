# tests/test_config.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔧 Testing configuration module...\n")

try:
    import config
    print("✅ Config module imported successfully")
    
    # Access the config instance
    print(f"Config instance: {config.config}")
    
    # Test getting values
    print("\n📋 Testing configuration values:")
    
    # Test URLs
    urls = config.config.get_urls()
    print(f"✅ URLs loaded: {len(urls)} URLs")
    print(f"   Admin Portal: {urls.get('admin_portal')}")
    print(f"   TMS Portal: {urls.get('tms_portal')}")
    print(f"   IPN API: {urls.get('ipn_api')}")
    
    # Test dot notation
    admin_url = config.config.get("urls.admin_portal")
    print(f"✅ Dot notation test: {admin_url}")
    
    # Test data config
    data_config = config.config.get_data_config()
    print(f"✅ Data config: Customer: {data_config.get('default_customer')}")
    print(f"   Batch: {data_config.get('default_batch')}")
    
    # Test database config
    db_config = config.config.get_database_config()
    print(f"✅ Database config: DB: {db_config.get('mongo_db')}")
    
    print("\n🎉 All configuration tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()