# database/mongo_handler.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import os
import allure

logger = logging.getLogger(__name__)

class MongoHandler:
    """Handler for MongoDB operations"""
    
    def __init__(self, connection_string: str = None, database: str = None):
        self.connection_string = connection_string or os.getenv("MONGO_URI")
        self.database_name = database or os.getenv("MONGO_DB", "koili_staging")
        self.client = None
        self.db = None
        self.connect()
        
    def connect(self) -> None:
        """Establish connection to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB: {self.database_name}")
            self.client = MongoClient(self.connection_string)
            
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info("✅ MongoDB connection successful")
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    @allure.step("Find device in device_registry")
    def find_device(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Find device in device_registry collection"""
        try:
            collection = self.db['device_registry']
            device = collection.find_one({"serial": serial_number})
            
            if device:
                logger.info(f"Found device: {serial_number}")
            else:
                logger.warning(f"Device not found: {serial_number}")
                
            return device
            
        except PyMongoError as e:
            logger.error(f"Error finding device {serial_number}: {e}")
            return None
    
    @allure.step("Get transactions for device")
    def get_transactions_by_device(
        self, 
        serial_number: str, 
        time_window_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get transactions for a device within time window
        
        Args:
            serial_number: Device serial number
            time_window_minutes: Look back window in minutes
            
        Returns:
            List of transaction documents
        """
        try:
            collection = self.db['registry_audit']
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            # Query for device transactions within time window
            query = {
                "device.serial_number": serial_number,
                "created_at": {"$gte": time_threshold}
            }
            
            transactions = list(collection.find(query).sort("created_at", -1))
            logger.info(f"Found {len(transactions)} transactions for device {serial_number}")
            
            return transactions
            
        except PyMongoError as e:
            logger.error(f"Error getting transactions for device {serial_number}: {e}")
            return []
    
    @allure.step("Verify transaction exists")
    def verify_transaction_exists(
        self, 
        serial_number: str, 
        amount: int, 
        scheme: str,
        status: str = "FIRED"
    ) -> bool:
        """
        Verify if specific transaction exists
        
        Args:
            serial_number: Device serial number
            amount: Transaction amount
            scheme: Transaction scheme (nchl/fonepay)
            status: Expected transaction status
            
        Returns:
            bool: True if transaction exists
        """
        try:
            collection = self.db['registry_audit']
            
            query = {
                "device.serial_number": serial_number,
                "amount": amount,
                "scheme": scheme,
                "status": status,
                "service_type": "NOTIFY"
            }
            
            transaction = collection.find_one(query)
            
            if transaction:
                logger.info(f"Transaction verified: {scheme} - {amount} - {status}")
                return True
            else:
                logger.warning(f" Transaction not found: {scheme} - {amount} - {status}")
                return False
                
        except PyMongoError as e:
            logger.error(f"Error verifying transaction: {e}")
            return False
    
    @allure.step("Count transactions for device")
    def count_transactions(
        self, 
        serial_number: str, 
        time_window_minutes: int = 5
    ) -> int:
        """Count transactions for a device within time window"""
        transactions = self.get_transactions_by_device(serial_number, time_window_minutes)
        return len(transactions)
    
    @allure.step("Get latest transaction")
    def get_latest_transaction(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get the latest transaction for a device"""
        try:
            collection = self.db['registry_audit']
            
            query = {"device.serial_number": serial_number}
            transaction = collection.find_one(query, sort=[("created_at", -1)])
            
            if transaction:
                logger.info(f"Latest transaction: {transaction.get('_id')}")
            return transaction
            
        except PyMongoError as e:
            logger.error(f"Error getting latest transaction: {e}")
            return None
    
    @allure.step("Verify exactly 2 transactions exist")
    def verify_exactly_two_transactions(
        self, 
        serial_number: str, 
        expected_amounts: tuple = (33333, 44444),
        expected_schemes: tuple = ("nchl", "fonepay")
    ) -> bool:
        """
        Verify exactly 2 transactions exist with expected amounts and schemes
        
        Args:
            serial_number: Device serial number
            expected_amounts: Tuple of expected amounts (nchl, fonepay)
            expected_schemes: Tuple of expected schemes
            
        Returns:
            bool: True if verification passes
        """
        transactions = self.get_transactions_by_device(serial_number)
        
        if len(transactions) != 2:
            logger.error(f"Expected 2 transactions, found {len(transactions)}")
            return False
        
        # Check amounts and schemes
        found_amounts = []
        found_schemes = []
        
        for txn in transactions:
            found_amounts.append(txn.get('amount'))
            found_schemes.append(txn.get('scheme'))
        
        # Sort to compare
        found_amounts.sort()
        found_schemes.sort()
        
        expected_amounts_sorted = sorted(expected_amounts)
        expected_schemes_sorted = sorted(expected_schemes)
        
        if (found_amounts == expected_amounts_sorted and 
            found_schemes == expected_schemes_sorted):
            logger.info(" Transaction amounts and schemes match expected values")
            return True
        else:
            logger.error(f"Amounts mismatch: expected {expected_amounts_sorted}, got {found_amounts}")
            logger.error(f"Schemes mismatch: expected {expected_schemes_sorted}, got {found_schemes}")
            return False