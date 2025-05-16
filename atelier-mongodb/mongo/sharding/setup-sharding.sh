#!/bin/bash
echo "Waiting for containers to start..."
sleep 10

echo "Initializing Config Server replica set..."
mongosh --host configsvr --eval "
  rs.initiate({
    _id: 'configrs',
    configsvr: true,
    members: [
      { _id: 0, host: 'configsvr:27017' }
    ]
  })
"

echo "Initializing Shard 1 replica set..."
mongosh --host shard1 --eval "
  rs.initiate({
    _id: 'shard1rs',
    members: [
      { _id: 0, host: 'shard1:27017' }
    ]
  })
"

echo "Initializing Shard 2 replica set..."
mongosh --host shard2 --eval "
  rs.initiate({
    _id: 'shard2rs',
    members: [
      { _id: 0, host: 'shard2:27017' }
    ]
  })
"

echo "Initializing Shard 3 replica set..."
mongosh --host shard3 --eval "
  rs.initiate({
    _id: 'shard3rs',
    members: [
      { _id: 0, host: 'shard3:27017' }
    ]
  })
"

echo "Waiting for replica sets to initialize..."
sleep 20

echo "Adding shards to cluster..."
mongosh --host mongos --eval "
  sh.addShard('shard1rs/shard1:27017');
  sh.addShard('shard2rs/shard2:27017');
  sh.addShard('shard3rs/shard3:27017');
"

echo "Enabling sharding on database 'sharddb'..."
mongosh --host mongos --eval "
  sh.enableSharding('sharddb');
"

echo "Creating sample collection and defining shard key..."
mongosh --host mongos --eval "
  use sharddb;
  db.createCollection('users');
  sh.shardCollection('sharddb.users', { 'userId': 'hashed' });
"

echo "Inserting sample data..."
mongosh --host mongos --eval "
  use sharddb;
  for (let i = 1; i <= 1000; i++) {
    db.users.insertOne({
      userId: i,
      name: 'User ' + i,
      email: 'user' + i + '@example.com',
      region: ['EU', 'US', 'ASIA'][i % 3]
    });
  }
"

echo "Sharding setup complete. Checking status..."
mongosh --host mongos --eval "
  sh.status();
"