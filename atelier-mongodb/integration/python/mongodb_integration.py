"""
MongoDB Integration Example - Python with PyMongo

This script demonstrates connecting to MongoDB in different deployment modes
and performing basic CRUD operations.
"""

import os
import pprint
import time
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# MongoDB connection functions

def connect_standalone():
    """Connect to MongoDB Standalone instance"""
    try:
        # URI de connexion avec authentification
        uri = "mongodb://testuser:testpassword@localhost:27017/testdb"
        client = MongoClient(uri)
        # Verify the connection
        client.admin.command('ping')
        print("Connected to MongoDB Standalone successfully!")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB Standalone: {e}")
        return None

def connect_replicaset():
    """Connect to MongoDB Replica Set"""
    try:
        # URI avec les membres du replica set
        uri = "mongodb://testuser:testpassword@localhost:27017,localhost:27018,localhost:27019/testdb?replicaSet=rs0"
        # Spécifier readPreference pour permettre la lecture depuis les secondaires
        client = MongoClient(uri, readPreference='secondaryPreferred')
        # Verify the connection
        client.admin.command('ping')
        print("Connected to MongoDB Replica Set successfully!")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB Replica Set: {e}")
        return None

def connect_sharded():
    """Connect to MongoDB Sharded Cluster"""
    try:
        # URI pour se connecter au mongos router
        uri = "mongodb://localhost:27020/sharddb"
        client = MongoClient(uri)
        # Verify the connection
        client.admin.command('ping')
        print("Connected to MongoDB Sharded Cluster successfully!")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB Sharded Cluster: {e}")
        return None

# CRUD Operations

def perform_crud_operations(client, db_name='testdb', collection_name='test_collection'):
    """Perform basic CRUD operations on the specified database and collection"""
    if not client:
        print("No client connection provided.")
        return
    
    try:
        # Get database and collection
        db = client[db_name]
        collection = db[collection_name]
        
        print("\n--- CRUD Operations ---")
        
        # Create: Insert documents
        print("\n[CREATE] Inserting documents...")
        
        # Insert a single document
        document = {
            "name": "Test Document",
            "value": 42,
            "tags": ["python", "mongodb", "integration"],
            "created_at": datetime.now()
        }
        result = collection.insert_one(document)
        print(f"Inserted document with ID: {result.inserted_id}")
        
        # Insert multiple documents
        documents = [
            {"name": "Document 1", "value": 10, "tags": ["python"]},
            {"name": "Document 2", "value": 20, "tags": ["mongodb"]},
            {"name": "Document 3", "value": 30, "tags": ["database", "nosql"]}
        ]
        result = collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents")
        
        # Read: Query documents
        print("\n[READ] Querying documents...")
        
        # Find all documents
        print("\nAll documents:")
        cursor = collection.find()
        for doc in cursor:
            pprint.pprint(doc)
        
        # Find with filter
        print("\nDocuments with value > 25:")
        cursor = collection.find({"value": {"$gt": 25}})
        for doc in cursor:
            pprint.pprint(doc)
        
        # Find one document
        print("\nFinding one document by name:")
        doc = collection.find_one({"name": "Document 1"})
        pprint.pprint(doc)
        
        # Update: Modify documents
        print("\n[UPDATE] Updating documents...")
        
        # Update one document
        update_result = collection.update_one(
            {"name": "Document 1"},
            {"$set": {"updated": True, "value": 11}}
        )
        print(f"Modified {update_result.modified_count} document")
        
        # Update many documents
        update_result = collection.update_many(
            {"value": {"$gt": 20}},
            {"$set": {"high_value": True}}
        )
        print(f"Modified {update_result.modified_count} documents")
        
        # Show updated documents
        print("\nUpdated documents:")
        for doc in collection.find({"updated": True}):
            pprint.pprint(doc)
        
        # Delete: Remove documents
        print("\n[DELETE] Deleting documents...")
        
        # Delete one document
        delete_result = collection.delete_one({"name": "Document 2"})
        print(f"Deleted {delete_result.deleted_count} document")
        
        # Delete many documents
        delete_result = collection.delete_many({"high_value": True})
        print(f"Deleted {delete_result.deleted_count} documents")
        
        # Show remaining documents
        print("\nRemaining documents:")
        for doc in collection.find():
            pprint.pprint(doc)
        
    except OperationFailure as e:
        print(f"An error occurred during database operations: {e}")
    finally:
        print("\nFinished CRUD operations")

def test_all_deployments():
    """Test connections and operations with all MongoDB deployment types"""
    
    # Test Standalone
    print("\n===== TESTING MONGODB STANDALONE =====")
    client = connect_standalone()
    if client:
        perform_crud_operations(client)
        client.close()
    
    # Test Replica Set
    print("\n===== TESTING MONGODB REPLICA SET =====")
    client = connect_replicaset()
    if client:
        perform_crud_operations(client)
        client.close()
    
    # Test Sharded Cluster
    print("\n===== TESTING MONGODB SHARDED CLUSTER =====")
    client = connect_sharded()
    if client:
        # For sharded cluster, use the sharddb database and users collection
        perform_crud_operations(client, 'sharddb', 'users')
        client.close()

if __name__ == "__main__":
    # Make sure MongoDB is running before testing
    print("Testing MongoDB integration...")
    
    test_all_deployments()