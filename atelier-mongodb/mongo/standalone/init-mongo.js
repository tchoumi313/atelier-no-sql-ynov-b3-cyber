db.createUser({
  user: "testuser",
  pwd: "testpassword",
  roles: [
    { role: "readWrite", db: "testdb" }
  ]
});

db = db.getSiblingDB('testdb');
db.createCollection('test_collection');