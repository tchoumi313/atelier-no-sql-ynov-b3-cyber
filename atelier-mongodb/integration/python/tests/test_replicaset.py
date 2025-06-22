"""
MongoDB Replica Set Test Script

This script tests a connection to a MongoDB replica set
and performs read/write operations demonstrating replica set functionality.
"""

import datetime
import pprint
import time

from pymongo import MongoClient, ReadPreference


def test_replicaset_connection():
    # Connection URI with authentication and replica set configuration
    uri = "mongodb://admin:pass@localhost:27017/admin?replicaSet=rs0"
    
    print("Connecting to MongoDB replica set...")
    client = MongoClient(uri)
    
    try:
        # Test connection with server_info
        info = client.server_info()
        print(f"Successfully connected to MongoDB version {info.get('version')}")
        
        # Check replica set status
        rs_status = client.admin.command('replSetGetStatus')
        primary = None
        secondaries = []
        
        for member in rs_status['members']:
            if member['state'] == 1:  # PRIMARY
                primary = member['name']
            elif member['state'] == 2:  # SECONDARY
                secondaries.append(member['name'])
        
        print(f"\nReplica Set Status:")
        print(f"  PRIMARY: {primary}")
        print(f"  SECONDARIES: {', '.join(secondaries)}")
        
        # Access the test database and collection
        db = client.testdb
        collection = db.replica_test
        
        # Write to primary (default behavior)
        print("\nWriting to PRIMARY node...")
        test_doc = {
            "name": "Replica Set Test",
            "timestamp": datetime.datetime.now(),
            "operation": "write to primary"
        }
        
        result = collection.insert_one(test_doc)
        print(f"Inserted document with ID: {result.inserted_id}")
        
        # Read from primary
        print("\nReading from PRIMARY node...")
        client_primary = MongoClient(uri, readPreference="primary")
        db_primary = client_primary.testdb
        found_doc = db_primary.replica_test.find_one({"name": "Replica Set Test"})
        print("Document from PRIMARY:")
        pprint.pprint(found_doc)
        
        # Allow time for replication to occur
        print("\nWaiting for replication to occur...")
        time.sleep(2)
        
        # Read from secondary
        print("\nReading from SECONDARY node...")
        client_secondary = MongoClient(uri, readPreference="secondary")
        db_secondary = client_secondary.testdb
        found_doc = db_secondary.replica_test.find_one({"name": "Replica Set Test"})
        print("Document from SECONDARY:")
        pprint.pprint(found_doc)
        
        # Clean up by removing the test document
        collection.delete_one({"_id": result.inserted_id})
        print("\nTest document removed. Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Connection closed")

if __name__ == "__main__":
    test_replicaset_connection()