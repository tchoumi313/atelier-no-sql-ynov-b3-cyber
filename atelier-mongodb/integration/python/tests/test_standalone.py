"""
MongoDB Standalone Test Script

This script tests a basic connection to a standalone MongoDB instance
and performs a simple insert and find operation.
"""

import datetime
import pprint

from pymongo import MongoClient


def test_standalone_connection():
    # Connection URI with authentication
    uri = "mongodb://testuser:testpassword@localhost:27017/testdb"
    
    print("Connecting to MongoDB standalone instance...")
    client = MongoClient(uri)
    
    try:
        # Test connection with server_info
        info = client.server_info()
        print(f"Successfully connected to MongoDB version {info.get('version')}")
        
        # Access the test database and collection
        db = client.testdb
        collection = db.test_collection
        
        # Insert a test document
        test_doc = {
            "name": "Connection Test",
            "timestamp": datetime.datetime.now(),
            "status": "success"
        }
        
        result = collection.insert_one(test_doc)
        print(f"Inserted document with ID: {result.inserted_id}")
        
        # Find the document
        found_doc = collection.find_one({"name": "Connection Test"})
        print("\nRetrieved document:")
        pprint.pprint(found_doc)
        
        # Clean up by removing the test document
        collection.delete_one({"_id": result.inserted_id})
        print("Test document removed. Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Connection closed")

if __name__ == "__main__":
    test_standalone_connection()