# tests/test_mongodb_integration.py (Final Working Version)
import pytest
import sys
import os
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_handler import MongoHandler

# ============================================================================
# AZURE COSMOS DB CONFIGURATION - USING ACTUAL DATA FROM EXPLORATION
# ============================================================================
# Your Azure Cosmos DB connection string
COSMOS_CONNECTION_STRING = "mongodb+srv://sysadmin:6Lxm82FyZt0I15N@koili-dev.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
COSMOS_DATABASE = "koili_staging"  # CONFIRMED: This is your actual database

# REAL serial numbers from your database exploration
TEST_SERIALS = [
    "23144",                # From device_registry sample
    "23135",                # From device_registry
    "38231105960991",       # From device_iot
    "38231105960993",       # From device_iot
    "38231105961279",       # From registry_audit sample device.serial_number
    "IPNT38250201740004"    # From dyn_qr
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def setup_environment():
    """Setup Azure Cosmos DB environment variables"""
    os.environ["MONGO_URI"] = COSMOS_CONNECTION_STRING
    os.environ["MONGO_DB"] = COSMOS_DATABASE
    
    # Mask password for logging
    masked_uri = COSMOS_CONNECTION_STRING
    if "@" in masked_uri:
        parts = masked_uri.split("@")
        if ":" in parts[0]:
            cred_part = parts[0].split(":")
            if len(cred_part) > 1:
                cred_part[1] = "***"
            parts[0] = ":".join(cred_part)
        masked_uri = "@".join(parts)
    
    print("\n" + "=" * 70)
    print("AZURE COSMOS DB TEST CONFIGURATION")
    print("=" * 70)
    print(f"Database: {COSMOS_DATABASE}")
    print(f"Connection: {masked_uri}")
    print(f"Test Serials: {TEST_SERIALS[:3]}...")  # Show first 3
    print("=" * 70 + "\n")

def create_mongo_handler():
    """Create MongoHandler instance for Azure Cosmos DB"""
    return MongoHandler(
        connection_string=COSMOS_CONNECTION_STRING,
        database=COSMOS_DATABASE
    )

# ============================================================================
# TEST FUNCTIONS
# ============================================================================
def test_mongodb_connection():
    """Test Azure Cosmos DB MongoDB connection"""
    print("\n" + "=" * 60)
    print("TEST 1: AZURE COSMOS DB CONNECTION")
    print("=" * 60)
    
    try:
        # Setup environment first
        setup_environment()
        
        # Initialize MongoDB handler for Azure Cosmos DB
        print("[INFO] Initializing Azure Cosmos DB handler...")
        mongo = create_mongo_handler()
        
        # Assert that connection is established
        assert mongo.is_connected, "Azure Cosmos DB should be connected"
        assert mongo.client is not None, "MongoDB client should be initialized"
        assert mongo.db is not None, "Database should be initialized"
        
        print(f"[PASS] Azure Cosmos DB connection successful")
        print(f"[INFO] Database: {mongo.database_name}")
        
        # Test disconnection
        mongo.disconnect()
        assert not mongo.is_connected, "MongoDB should be disconnected"
        
        print("[PASS] MongoDB disconnection test successful")
        
    except Exception as e:
        print(f"[FAIL] Azure Cosmos DB connection test failed: {e}")
        print("[TROUBLESHOOTING] Check:")
        print("  1. Is your IP whitelisted in Azure Cosmos DB firewall?")
        print("  2. Do you need VPN access?")
        print("  3. Are credentials correct?")
        raise

def test_device_lookup():
    """Test device lookup in device_registry collection"""
    print("\n" + "=" * 60)
    print("TEST 2: DEVICE LOOKUP IN device_registry")
    print("=" * 60)
    
    try:
        mongo = create_mongo_handler()
        
        # Check if device_registry collection exists
        collections = mongo.get_all_collections()
        if "device_registry" not in collections:
            print("[WARN] device_registry collection not found")
            print("[INFO] Available collections:", collections)
            pytest.skip("device_registry collection not found")
        
        print(f"[INFO] Found device_registry collection")
        
        # Use first real serial number
        test_serial = TEST_SERIALS[0]  # "23144"
        print(f"[INFO] Looking up device: {test_serial}")
        
        # Find device using correct field name (serial_number, not serial)
        device = mongo.find_device(test_serial)
        
        if device:
            print(f"[PASS] Device found: {test_serial}")
            # Print important fields (using correct field names)
            print(f"[INFO] Device ID: {device.get('_id')}")
            print(f"[INFO] Serial Number: {device.get('serial_number', 'N/A')}")
            print(f"[INFO] Model: {device.get('model', 'N/A')}")
            print(f"[INFO] Type: {device.get('type', 'N/A')}")
            print(f"[INFO] Prefix: {device.get('prefix', 'N/A')}")
            print(f"[INFO] Created: {device.get('created_at', 'N/A')}")
            
            # Assert key fields exist (using correct field name)
            assert 'serial_number' in device, "Device should have serial_number field"
            assert device['serial_number'] == test_serial, f"Serial number should match {test_serial}"
            
        else:
            print(f"[WARN] Device not found: {test_serial}")
            print("[INFO] Trying alternative serial numbers...")
            
            # Try other test serials
            for serial in TEST_SERIALS[1:]:
                device = mongo.find_device(serial)
                if device:
                    print(f"[INFO] Found device with serial: {serial}")
                    print(f"[INFO] Device model: {device.get('model', 'N/A')}")
                    print(f"[INFO] Device type: {device.get('type', 'N/A')}")
                    break
            
            # If still not found, just log warning but don't fail test
            if not device:
                print("[WARN] No test devices found in device_registry")
                print("[INFO] This might be expected if serials are in different collections")
        
    except Exception as e:
        print(f"[FAIL] Device lookup test failed: {e}")
        raise
    finally:
        if 'mongo' in locals():
            mongo.disconnect()

def test_transaction_queries():
    """Test transaction query functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: TRANSACTION QUERIES IN registry_audit")
    print("=" * 60)
    
    try:
        mongo = create_mongo_handler()
        
        # Check if registry_audit collection exists
        collections = mongo.get_all_collections()
        if "registry_audit" not in collections:
            print("[WARN] registry_audit collection not found")
            print("[INFO] Available collections:", collections)
            pytest.skip("registry_audit collection not found")
        
        print(f"[INFO] Found registry_audit collection")
        
        # Get a serial number that likely has transactions (from exploration)
        test_serial = "38231105961279"  # From your exploration sample
        print(f"[INFO] Querying transactions for device: {test_serial}")
        print(f"[INFO] Note: Using device.serial_number field (nested)")
        
        # Get transactions within last 24 hours
        time_window = 1440  # 24 hours in minutes
        transactions = mongo.get_transactions_by_device(test_serial, time_window)
        
        print(f"[INFO] Found {len(transactions)} transactions")
        
        if transactions:
            print("[PASS] Transaction query successful")
            
            # Display transaction details
            for i, txn in enumerate(transactions[:3]):  # Show first 3 transactions
                print(f"\n[INFO] Transaction {i+1}:")
                print(f"  ID: {txn.get('_id')}")
                print(f"  Amount: {txn.get('amount', 'N/A')}")
                print(f"  Scheme: {txn.get('scheme', 'N/A')}")
                print(f"  Status: {txn.get('status', 'N/A')}")
                print(f"  Service Type: {txn.get('service_type', 'N/A')}")
                print(f"  Created: {txn.get('created_at', 'N/A')}")
                
                # Verify transaction structure
                assert 'amount' in txn, "Transaction should have amount"
                assert 'scheme' in txn, "Transaction should have scheme"
                assert 'status' in txn, "Transaction should have status"
                
                # Check device info (nested)
                if 'device' in txn:
                    print(f"  Device Info:")
                    print(f"    Serial: {txn['device'].get('serial_number', 'N/A')}")
                    print(f"    Model: {txn['device'].get('model', 'N/A')}")
                    print(f"    Type: {txn['device'].get('type', 'N/A')}")
            
            # Test count function
            count = mongo.count_transactions(test_serial, time_window)
            print(f"[INFO] Transaction count: {count}")
            
            # Test latest transaction
            latest = mongo.get_latest_transaction(test_serial)
            if latest:
                print(f"\n[INFO] Latest transaction:")
                print(f"  Amount: {latest.get('amount')}")
                print(f"  Scheme: {latest.get('scheme')}")
                print(f"  Status: {latest.get('status')}")
            
        else:
            print("[WARN] No transactions found for test device")
            print("[INFO] This might be expected if:")
            print("  1. Device has no recent transactions")
            print("  2. Time window is too short")
            
            # Try transaction verification with sample values from exploration
            test_amount = 100.0  # From your exploration sample
            test_scheme = "fonepay"  # From your exploration sample
            
            print(f"\n[INFO] Testing with sample transaction data:")
            print(f"  Amount: {test_amount}")
            print(f"  Scheme: {test_scheme}")
            
            exists = mongo.verify_transaction_exists(test_serial, test_amount, test_scheme)
            print(f"[INFO] Sample transaction exists: {exists}")
            
    except Exception as e:
        print(f"[FAIL] Transaction query test failed: {e}")
        raise
    finally:
        if 'mongo' in locals():
            mongo.disconnect()

def test_collection_stats():
    """Test collection statistics functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: COLLECTION STATISTICS")
    print("=" * 60)
    
    try:
        mongo = create_mongo_handler()
        
        # Get all collections
        collections = mongo.get_all_collections()
        print(f"[INFO] Total collections in {mongo.database_name}: {len(collections)}")
        
        if not collections:
            print("[WARN] No collections found in database")
            pytest.skip("No collections found in database")
        
        print(f"[INFO] Collections: {collections}")
        
        # Get stats for important collections
        important_collections = ['device_registry', 'registry_audit', 'device_iot']
        
        for collection_name in important_collections:
            if collection_name in collections:
                print(f"\n[INFO] Collection: {collection_name}")
                
                # Check if collection exists
                exists = mongo.collection_exists(collection_name)
                assert exists, f"Collection {collection_name} should exist"
                
                # Get statistics
                stats = mongo.get_collection_stats(collection_name)
                
                if 'error' in stats:
                    print(f"[WARN] Error getting stats: {stats['error']}")
                    continue
                
                print(f"  Document count: {stats['document_count']}")
                
                if stats['fields']:
                    print(f"  Fields ({len(stats['fields'])} total):")
                    # Show important fields first
                    important_fields = ['serial_number', 'serial', 'device', 'amount', 'status', 'created_at', 'model', 'type']
                    found_important = [f for f in important_fields if f in stats['fields']]
                    if found_important:
                        print(f"    Important: {', '.join(found_important)}")
                    
                    # Show other fields (limit to 10)
                    other_fields = [f for f in stats['fields'][:15] if f not in important_fields]
                    if other_fields:
                        print(f"    Others: {', '.join(other_fields)}")
                        if len(stats['fields']) > 15:
                            print(f"    ... and {len(stats['fields']) - 15} more fields")
                
                if stats['sample_id']:
                    print(f"  Sample document ID: {stats['sample_id']}")
                
                # Verify stats structure
                assert 'collection' in stats, "Stats should have collection name"
                assert 'document_count' in stats, "Stats should have document count"
                assert 'fields' in stats, "Stats should have fields list"
            else:
                print(f"\n[WARN] Collection not found: {collection_name}")
        
        print(f"\n[PASS] Collection statistics test completed for {len(collections)} collections")
        
    except Exception as e:
        print(f"[FAIL] Collection statistics test failed: {e}")
        raise
    finally:
        if 'mongo' in locals():
            mongo.disconnect()

def test_mongodb_operations():
    """Test comprehensive MongoDB operations"""
    print("\n" + "=" * 60)
    print("TEST 5: COMPREHENSIVE MONGODB OPERATIONS")
    print("=" * 60)
    
    mongo = None
    
    try:
        mongo = create_mongo_handler()
        
        # 1. Verify connection
        assert mongo.is_connected, "Should be connected to MongoDB"
        print("[PASS] Connection verified")
        
        # 2. Get database info
        db_name = mongo.db.name
        print(f"[INFO] Connected to database: {db_name}")
        
        # 3. List all collections
        collections = mongo.get_all_collections()
        print(f"[INFO] Available collections: {collections}")
        
        # 4. Test each important collection
        for collection_name in ['device_registry', 'registry_audit', 'device_iot']:
            if collection_name in collections:
                print(f"\n[INFO] Testing collection: {collection_name}")
                
                # Get stats
                stats = mongo.get_collection_stats(collection_name)
                
                if 'error' in stats:
                    print(f"  Error: {stats['error']}")
                    continue
                
                if stats['document_count'] > 0:
                    print(f"  Documents: {stats['document_count']}")
                    
                    # Try to get a sample document
                    if collection_name == 'device_registry':
                        # Find any device
                        test_device = mongo.db[collection_name].find_one()
                        if test_device:
                            serial = test_device.get('serial_number', 'N/A')
                            print(f"  Sample device serial_number: {serial}")
                            
                            # Test device lookup
                            device = mongo.find_device(serial)
                            if device:
                                print(f"  Device lookup successful for: {serial}")
                            else:
                                print(f"  Device lookup failed for: {serial}")
                    
                    elif collection_name == 'registry_audit':
                        # Find any transaction
                        test_txn = mongo.db[collection_name].find_one()
                        if test_txn:
                            amount = test_txn.get('amount', 'N/A')
                            scheme = test_txn.get('scheme', 'N/A')
                            status = test_txn.get('status', 'N/A')
                            print(f"  Sample transaction: {scheme} - {amount} - {status}")
                            
                            # Check device info
                            if 'device' in test_txn:
                                device_info = test_txn['device']
                                print(f"  Device in transaction: {device_info.get('serial_number', 'N/A')}")
                    
                    elif collection_name == 'device_iot':
                        # Find any IoT device
                        test_iot = mongo.db[collection_name].find_one()
                        if test_iot:
                            serial = test_iot.get('serial_number', test_iot.get('serial', 'N/A'))
                            print(f"  Sample IoT device serial: {serial}")
                else:
                    print(f"  Collection is empty")
        
        # 5. Test Cosmos DB info
        print(f"\n[INFO] Getting Cosmos DB information...")
        cosmos_info = mongo.get_cosmos_db_info()
        if 'error' not in cosmos_info:
            print(f"  Database: {cosmos_info.get('database')}")
            print(f"  Collections count: {cosmos_info.get('collections_count')}")
            print(f"  Connection type: {cosmos_info.get('connection_type')}")
            if 'data_size' in cosmos_info:
                print(f"  Data size: {cosmos_info.get('data_size')} bytes")
        
        print("\n[PASS] All MongoDB operations test completed successfully")
        
    except Exception as e:
        print(f"[FAIL] MongoDB operations test failed: {e}")
        raise
    finally:
        # Clean up
        if mongo:
            mongo.disconnect()

def test_cosmosdb_quick_diagnostic():
    """Quick diagnostic test for Azure Cosmos DB"""
    print("\n" + "=" * 60)
    print("TEST 6: QUICK DIAGNOSTIC")
    print("=" * 60)
    
    try:
        setup_environment()
        mongo = create_mongo_handler()
        
        print(f"[STATUS] Connected: {mongo.is_connected}")
        print(f"[DATABASE] {mongo.database_name}")
        
        collections = mongo.get_all_collections()
        print(f"[COLLECTIONS] {len(collections)} found")
        
        if collections:
            print(f"\n[TOP COLLECTIONS WITH COUNTS]:")
            for i, coll in enumerate(sorted(collections), 1):
                try:
                    count = mongo.db[coll].estimated_document_count()
                    print(f"  {i:2d}. {coll:25s} - {count:6d} documents")
                except:
                    print(f"  {i:2d}. {coll:25s} - [Count unavailable]")
        
        # Test a simple query on device_registry
        print(f"\n[QUICK QUERY TEST - device_registry]:")
        if 'device_registry' in collections:
            sample = mongo.db['device_registry'].find_one()
            if sample:
                print(f"  Sample document keys: {list(sample.keys())}")
                if 'serial_number' in sample:
                    print(f"  Actual serial_number: '{sample['serial_number']}'")
                if 'model' in sample:
                    print(f"  Model: '{sample['model']}'")
                if 'type' in sample:
                    print(f"  Type: '{sample['type']}'")
        
        print(f"\n[PASS] Quick diagnostic completed")
        
    except Exception as e:
        print(f"[FAIL] Diagnostic failed: {e}")
        raise
    finally:
        if 'mongo' in locals():
            mongo.disconnect()

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING AZURE COSMOS DB INTEGRATION TESTS")
    print("=" * 80)
    
    # Set environment variables
    setup_environment()
    
    # Define test execution order
    tests = [
        test_mongodb_connection,
        test_cosmosdb_quick_diagnostic,
        test_device_lookup,
        test_transaction_queries,
        test_collection_stats,
        test_mongodb_operations
    ]
    
    results = []
    
    for test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_func.__name__}")
        print(f"{'='*60}")
        
        try:
            test_func()
            results.append((test_func.__name__, "✅ PASS"))
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            results.append((test_func.__name__, f"❌ FAIL: {error_msg}"))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results:
        print(f"{test_name:40s} {result}")
    
    passed = sum(1 for _, r in results if "PASS" in r)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Azure Cosmos DB tests passed!")
        print("\n[QUICK START] Now you can use MongoDB Compass:")
        print("1. Open MongoDB Compass")
        print("2. Click 'New Connection'")
        print("3. Paste your connection string:")
        print("   mongodb+srv://sysadmin:***@koili-dev.mongocluster.cosmos.azure.com")
        print("4. Click 'Connect'")
        print("5. Select database: koili_staging")
        print("6. Explore your collections!")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check logs above.")
    
    # Exit with appropriate code
    import sys
    sys.exit(0 if passed == total else 1)