# tests/explore_cosmosdb.py
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your Azure connection string
COSMOS_CONNECTION_STRING = "mongodb+srv://sysadmin:6Lxm82FyZt0I15N@koili-dev.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
COSMOS_DATABASE = "koili_staging"

# Set environment
os.environ["MONGO_URI"] = COSMOS_CONNECTION_STRING
os.environ["MONGO_DB"] = COSMOS_DATABASE

from database.mongo_handler import MongoHandler

def explore_cosmosdb():
    """Explore what's actually in your Cosmos DB"""
    print("\n" + "="*80)
    print("EXPLORING AZURE COSMOS DB")
    print("="*80)
    
    try:
        # Connect
        mongo = MongoHandler()
        print(f"✅ Connected to: {mongo.database_name}")
        
        # Get ALL collections (not just pattern matches)
        all_collections = mongo.db.list_collection_names()
        print(f"\n📁 ALL COLLECTIONS ({len(all_collections)}):")
        
        if not all_collections:
            print("   Database is empty - no collections found")
            return
        
        # Show all collections with counts
        for i, collection_name in enumerate(sorted(all_collections), 1):
            try:
                count = mongo.db[collection_name].estimated_document_count()
                print(f"   {i:2d}. {collection_name:30s} - {count:6d} documents")
            except:
                print(f"   {i:2d}. {collection_name:30s} - [Error getting count]")
        
        # Explore sample documents
        print(f"\n🔍 EXPLORING SAMPLE DOCUMENTS:")
        
        for collection_name in all_collections[:3]:  # First 3 collections
            print(f"\n   Collection: {collection_name}")
            
            try:
                # Get a sample document
                sample = mongo.db[collection_name].find_one()
                
                if sample:
                    print(f"   Sample document keys: {list(sample.keys())}")
                    
                    # Show important fields
                    important_fields = ['serial', 'id', 'name', 'type', 'status', 'created', 'amount', 'device']
                    for field in important_fields:
                        if field in sample:
                            print(f"     {field}: {sample[field]}")
                    
                    # Show first 5 key-value pairs
                    print(f"   First 5 values:")
                    for i, (key, value) in enumerate(sample.items()):
                        if i >= 5:
                            print(f"     ... and {len(sample) - 5} more fields")
                            break
                        print(f"     {key}: {value}")
                else:
                    print(f"   Collection is empty")
                    
            except Exception as e:
                print(f"   Error exploring collection: {e}")
        
        # Check for any device-like data
        print(f"\n📱 SEARCHING FOR DEVICE-RELATED DATA:")
        
        # Look in ALL collections for serial numbers
        serials_found = []
        
        for collection_name in all_collections:
            try:
                # Get a few documents
                docs = list(mongo.db[collection_name].find().limit(2))
                
                for doc in docs:
                    # Check for serial-like fields
                    for key, value in doc.items():
                        if any(term in str(key).lower() for term in ['serial', 'device', 'terminal', 'sn']):
                            if value and len(str(value)) < 50:  # Reasonable length
                                print(f"   Found in '{collection_name}': {key} = {value}")
                                if 'serial' in str(key).lower():
                                    serials_found.append(str(value))
            except:
                pass
        
        if serials_found:
            print(f"\n✅ Found {len(serials_found)} potential device serials:")
            for serial in serials_found[:10]:  # Show first 10
                print(f"   - {serial}")
        else:
            print(f"   No device serials found in any collection")
        
        # Database info
        print(f"\n📊 DATABASE INFO:")
        try:
            db_stats = mongo.db.command("dbStats")
            print(f"   Data size: {db_stats.get('dataSize', 0)} bytes")
            print(f"   Storage size: {db_stats.get('storageSize', 0)} bytes")
            print(f"   Objects: {db_stats.get('objects', 0)}")
        except:
            print(f"   Could not get database stats")
        
        print(f"\n🎉 Exploration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'mongo' in locals():
            mongo.disconnect()

if __name__ == "__main__":
    explore_cosmosdb()