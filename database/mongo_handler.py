# database/mongo_handler.py (FIXED - NO CIRCULAR IMPORT)
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import urllib.parse
import allure
from datetime import timezone 
logger = logging.getLogger(__name__)

class MongoHandler:
    """Handler for MongoDB operations with Azure Cosmos DB compatibility"""
    
    def __init__(self, connection_string: str = None, database: str = None, timeout_ms: int = 10000):
        """
        Initialize MongoDB connection for Azure Cosmos DB
        
        Args:
            connection_string: MongoDB connection string
            database: Database name (use koili_staging)
            timeout_ms: Connection timeout in milliseconds
        """
        self.connection_string = connection_string or os.getenv("MONGO_URI")
        self.database_name = database or os.getenv("MONGO_DB", "koili_staging")
        self.timeout_ms = timeout_ms
        self.client = None
        self.db = None
        self.is_connected = False
        self._connect_with_retry()
    
    def _mask_connection_string(self, conn_str: str) -> str:
        """Mask credentials in connection string for logging"""
        if not conn_str:
            return "Not provided"
        
        if "@" in conn_str:
            parts = conn_str.split("@")
            if ":" in parts[0]:
                cred_part = parts[0].split(":")
                if len(cred_part) > 1:
                    cred_part[1] = "***"
                parts[0] = ":".join(cred_part)
            return "@".join(parts)
        return conn_str
    
    def _connect_with_retry(self, max_retries: int = 2) -> None:
        """Establish connection with retry logic for Azure Cosmos DB"""
        for attempt in range(max_retries + 1):
            try:
                self._connect()
                return
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                if attempt == max_retries:
                    logger.error(f"[FAIL] Failed to connect after {max_retries + 1} attempts: {e}")
                    raise
                logger.warning(f"[RETRY] Connection attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(1)
    
    def _connect(self) -> None:
        """Establish connection to Azure Cosmos DB"""
        try:
            if not self.connection_string:
                error_msg = "MongoDB connection string is required. Set MONGO_URI environment variable."
                logger.error(f"[FAIL] {error_msg}")
                raise ValueError(error_msg)
            
            logger.info(f"[INFO] Connecting to Azure Cosmos DB: {self.database_name}")
            logger.info(f"[INFO] Connection: {self._mask_connection_string(self.connection_string)}")
            
            # Azure Cosmos DB connection parameters
            connection_params = {
                'serverSelectionTimeoutMS': self.timeout_ms,
                'socketTimeoutMS': self.timeout_ms,
                'connectTimeoutMS': self.timeout_ms,
                'retryWrites': False,
                'maxIdleTimeMS': 120000
            }
            
            # Parse and enhance connection string
            # For Azure Cosmos DB, we might need to be careful with extra params if using SRV
            # Increasing timeout significantly for slow connections
            
            # Simplified connection approach - let pymongo handle parsing mostly
            # but ensure SSL/TLS is on which is default for Cosmos
            
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=self.timeout_ms * 3, # 30s
                connectTimeoutMS=self.timeout_ms * 3,
                socketTimeoutMS=self.timeout_ms * 3,
                
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.is_connected = True
            
            logger.info(f"[PASS] Connected to Azure Cosmos DB: {self.database_name}")
            
            # Get server info
            try:
                server_info = self.client.server_info()
                logger.info(f"[INFO] MongoDB API version: {server_info.get('version')}")
            except Exception as info_err:
                logger.info(f"[INFO] Using Azure Cosmos DB MongoDB API")
            
        except ServerSelectionTimeoutError as e:
            logger.error(f"[FAIL] Connection timeout to Azure Cosmos DB: {e}")
            logger.error("[TROUBLESHOOTING] Check:")
            logger.error("  1. Is your IP whitelisted in Azure Cosmos DB firewall?")
            logger.error("  2. Do you need VPN access to Azure?")
            logger.error("  3. Is the Cosmos DB instance running?")
            raise
        except ConnectionFailure as e:
            logger.error(f"[FAIL] Azure Cosmos DB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error connecting to Azure Cosmos DB: {e}")
            raise
    
    @allure.step("Get all collections")
    def get_all_collections(self) -> List[str]:
        """Get list of all collections in database"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collections = self.db.list_collection_names()
            logger.info(f"[INFO] Found {len(collections)} collections")
            return collections
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error getting collections: {e}")
            return []
    
    @allure.step("Find device in device_registry")
    def find_device(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Find device in device_registry collection using serial_number field"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collection = self.db['device_registry']
            
            # Your database uses serial_number, not serial
            device = collection.find_one({"serial_number": serial_number})
            
            if device:
                logger.info(f"[INFO] Found device: {serial_number}")
                # Clean up _id for logging
                device_copy = device.copy()
                if '_id' in device_copy:
                    device_copy['_id'] = str(device_copy['_id'])
                logger.debug(f"[DEBUG] Device data: {device_copy}")
            else:
                logger.warning(f"[WARN] Device not found: {serial_number}")
                # Also try alternative field names
                alt_device = collection.find_one({"$or": [
                    {"serial": serial_number},
                    {"device_serial": serial_number},
                    {"terminal_serial": serial_number}
                ]})
                if alt_device:
                    logger.info(f"[INFO] Found device with alternative field: {serial_number}")
                    device = alt_device
                
            return device
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error finding device {serial_number}: {e}")
            return None
    
    @allure.step("Get transactions for device")
    def get_transactions_by_device(
        self, 
        serial_number: str, 
        time_window_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get transactions for a device from registry_audit"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collection = self.db['registry_audit']
            
            # Calculate time threshold
            time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)


            
            # Query for device transactions within time window
            # Your database uses nested device.serial_number
            query = {
                "device.serial_number": serial_number,
                "created_at": {"$gte": time_threshold}
            }
            
            transactions = list(collection.find(query).sort("created_at", -1))
            
            logger.info(f"[INFO] Found {len(transactions)} transactions for device {serial_number}")
            
            return transactions
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error getting transactions for device {serial_number}: {e}")
            return []
    
    @allure.step("Verify transaction exists")
    def verify_transaction_exists(
        self, 
        serial_number: str, 
        amount: float,
        scheme: str,
        status: str = "FIRED"
    ) -> bool:
        """Verify if specific transaction exists"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collection = self.db['registry_audit']
            
            query = {
                "device.serial_number": serial_number,
                "amount": amount,
                "scheme": scheme,
                "status": status
            }
            
            transaction = collection.find_one(query)
            
            if transaction:
                logger.info(f"[PASS] Transaction verified: {scheme} - {amount} - {status}")
                return True
            else:
                logger.warning(f"[WARN] Transaction not found: {scheme} - {amount} - {status}")
                return False
                
        except PyMongoError as e:
            logger.error(f"[FAIL] Error verifying transaction: {e}")
            return False
    
    @allure.step("Count transactions for device")
    def count_transactions(
        self, 
        serial_number: str, 
        time_window_minutes: int = 60
    ) -> int:
        """Count transactions for a device within time window"""
        transactions = self.get_transactions_by_device(serial_number, time_window_minutes)
        return len(transactions)
    
    @allure.step("Get latest transaction")
    def get_latest_transaction(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get the latest transaction for a device"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collection = self.db['registry_audit']
            
            query = {"device.serial_number": serial_number}
            transaction = collection.find_one(query, sort=[("created_at", -1)])
            
            if transaction:
                logger.info(f"[INFO] Latest transaction ID: {transaction.get('_id')}")
                logger.info(f"[INFO] Latest transaction amount: {transaction.get('amount')}")
            return transaction
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error getting latest transaction: {e}")
            return None
    
    @allure.step("Get collection statistics")
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            if collection_name not in self.db.list_collection_names():
                return {"error": f"Collection '{collection_name}' not found"}
            
            collection = self.db[collection_name]
            
            # Get count
            count = collection.count_documents({})
            
            # Get sample document
            sample = collection.find_one()
            
            # Get field names if sample exists
            fields = list(sample.keys()) if sample else []
            
            stats = {
                "collection": collection_name,
                "document_count": count,
                "fields": fields[:10],
                "sample_id": str(sample.get('_id')) if sample else None
            }
            
            logger.info(f"[INFO] Collection {collection_name}: {count} documents")
            
            return stats
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error getting collection stats: {e}")
            return {"error": str(e)}
    
    @allure.step("Check collection exists")
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
                
            collections = self.db.list_collection_names()
            return collection_name in collections
            
        except PyMongoError as e:
            logger.error(f"[FAIL] Error checking collection: {e}")
            return False
    
    def get_cosmos_db_info(self) -> Dict[str, Any]:
        """Get Azure Cosmos DB specific information"""
        try:
            if not self.is_connected:
                self._connect_with_retry()
            
            info = {
                "database": self.database_name,
                "collections": self.db.list_collection_names(),
                "collections_count": len(self.db.list_collection_names()),
                "connection_type": "Azure Cosmos DB with MongoDB API",
                "connected": self.is_connected
            }
            
            # Try to get database stats
            try:
                db_stats = self.db.command("dbStats")
                info.update({
                    "data_size": db_stats.get("dataSize", 0),
                    "storage_size": db_stats.get("storageSize", 0),
                    "objects": db_stats.get("objects", 0)
                })
            except:
                pass
            
            return info
            
        except PyMongoError as e:
            return {"error": str(e), "database": self.database_name}
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("[INFO] Azure Cosmos DB connection closed")