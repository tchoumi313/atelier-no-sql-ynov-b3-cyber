"""
MongoDB Sharded Cluster Test Script

This script tests a connection to a MongoDB sharded cluster
and performs operations to demonstrate sharding functionality.
"""

import datetime
import pprint
import random

from pymongo import MongoClient


def test_sharded_connection():
    # Connection URI to the mongos router
    uri = "mongodb://localhost:27020/sharddb"
    
    print("Connecting to MongoDB sharded cluster...")
    client = MongoClient(uri)
    
    try:
        # Test connection with server_info
        info = client.server_info()
        print(f"Successfully connected to MongoDB version {info.get('version')}")
        
        # Get sharding status
        sh_status = client.admin.command('serverStatus')
        if 'sharding' in sh_status:
            print("\nConnected to a sharded MongoDB cluster")
        else:
            print("\nWarning: Not connected to a sharded MongoDB cluster")
            
        # Get detailed sharding information
        try:
            sharding_status = client.admin.command('listShards')
            print(f"\nShards in the cluster:")
            for shard in sharding_status['shards']:
                print(f"  {shard['_id']} - {shard['host']}")
        except Exception as e:
            print(f"Could not retrieve shard info: {e}")
            
        # Access the sharded database and collection
        db = client.sharddb
        collection = db.users
        
        # Insert test documents with different shard key values
        print("\nInserting test documents across shards...")
        inserted_ids = []
        
        for i in range(10):
            userId = random.randint(1, 10000)
            test_doc = {
                "userId": userId,
                "name": f"User {userId}",
                "email": f"user{userId}@example.com",
                "region": ["EU", "US", "ASIA"][i % 3],
                "timestamp": datetime.datetime.now()
            }
            result = collection.insert_one(test_doc)
            inserted_ids.append(result.inserted_id)
            print(f"Inserted document with userId: {userId}, ID: {result.inserted_id}")
        
        # Check distribution of data
        print("\nChecking shard distribution (this is approximate)...")
        try:
            stats = db.command("collStats", "users")
            if 'shards' in stats:
                print(f"Distribution of data across shards:")
                for shard_name, shard_stats in stats['shards'].items():
                    print(f"  {shard_name}: {shard_stats.get('count', 'N/A')} documents")
            else:
                print("Collection is not sharded or data not distributed yet")
        except Exception as e:
            print(f"Could not get collection stats: {e}")
            
        # Perform a find operation
        print("\nRetrieving documents...")
        docs = list(collection.find({"userId": {"$gt": 5000}}).limit(5))
        print(f"Found {len(docs)} documents with userId > 5000:")
        for doc in docs:
            pprint.pprint(doc)
            
        # Clean up by removing the test documents
        print("\nCleaning up test documents...")
        for doc_id in inserted_ids:
            collection.delete_one({"_id": doc_id})
        print(f"Removed {len(inserted_ids)} test documents")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Connection closed")

if __name__ == "__main__":
    test_sharded_connection()