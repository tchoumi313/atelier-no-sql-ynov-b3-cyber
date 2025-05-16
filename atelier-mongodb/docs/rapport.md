# Rapport d'Atelier MongoDB

Ce document détaille les étapes réalisées pour mettre en place MongoDB selon différents modes de déploiement et l'intégrer dans une application.

## Table des matières

1. [MongoDB Standalone](#1-mongodb-standalone)
2. [MongoDB Replica Set](#2-mongodb-replica-set)
3. [Intégration dans une application](#3-intégration-dans-une-application)
4. [MongoDB Sharding (Bonus)](#4-mongodb-sharding-bonus)

## 1. MongoDB Standalone

### Méthode de déploiement

Nous utilisons Docker pour déployer une instance MongoDB standalone. Cette approche offre plusieurs avantages :
- Isolation de l'environnement
- Facilité de configuration
- Portabilité entre différents systèmes

### Configuration et démarrage

Le fichier `docker-compose.yml` dans le dossier `mongo/standalone` définit notre configuration :

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:7.0
    container_name: mongodb_standalone
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js
    command: ["--auth"]

volumes:
  mongodb_data:
```

Le script `init-mongo.js` initialise un utilisateur supplémentaire et une base de données de test :

```javascript
db.createUser({
  user: "testuser",
  pwd: "testpassword",
  roles: [
    { role: "readWrite", db: "testdb" }
  ]
});

db = db.getSiblingDB('testdb');
db.createCollection('test_collection');
```

### Création d'utilisateur

L'utilisateur admin est créé via les variables d'environnement dans docker-compose. Un utilisateur supplémentaire `testuser` est créé via le script d'initialisation avec des droits limités à la base `testdb`.

### Connexion à la base

Plusieurs méthodes de connexion sont possibles :

1. **Via le shell mongo (mongosh) :**
   ```bash
   # Connexion en tant qu'admin
   mongosh -u admin -p password --authenticationDatabase admin
   
   # Connexion en tant que testuser
   mongosh -u testuser -p testpassword --authenticationDatabase admin
   ```

2. **Via une chaîne de connexion URI :**
   ```
   mongodb://admin:password@localhost:27017/admin
   mongodb://testuser:testpassword@localhost:27017/testdb
   ```

3. **Via MongoDB Compass :**
   En utilisant l'URI de connexion dans l'interface graphique.

### Opérations CRUD

Voici les commandes de base pour manipuler les données :

#### Insertion
```javascript
// Insertion d'un document
db.test_collection.insertOne({
  name: "Document 1",
  value: 42,
  tags: ["test", "sample"],
  metadata: {
    created: new Date(),
    author: "admin"
  }
});

// Insertion de plusieurs documents
db.test_collection.insertMany([
  { name: "Document 2", value: 43 },
  { name: "Document 3", value: 44 }
]);
```

#### Requêtes
```javascript
// Trouver tous les documents
db.test_collection.find();

// Trouver avec filtre
db.test_collection.find({ value: { $gt: 42 } });

// Trouver un seul document
db.test_collection.findOne({ name: "Document 1" });
```

#### Mise à jour
```javascript
// Mettre à jour un document
db.test_collection.updateOne(
  { name: "Document 1" },
  { $set: { value: 100 } }
);

// Mettre à jour plusieurs documents
db.test_collection.updateMany(
  { value: { $gt: 42 } },
  { $set: { updated: true } }
);
```

#### Suppression
```javascript
// Supprimer un document
db.test_collection.deleteOne({ name: "Document 2" });

// Supprimer plusieurs documents
db.test_collection.deleteMany({ updated: true });
```

## 2. MongoDB Replica Set

### Configuration des membres du replica set

Nous utilisons Docker Compose pour déployer un replica set de 3 nœuds. Le fichier `docker-compose.yml` dans le dossier `mongo/replicaset` définit notre configuration :

```yaml
version: '3.8'
services:
  mongo1:
    image: mongo:7.0
    container_name: mongo1
    command: ["--replSet", "rs0", "--bind_ip_all", "--port", "27017", "--auth"]
    volumes:
      - mongo1_data:/data/db
      - ./init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    networks:
      - mongo_network

  mongo2:
    image: mongo:7.0
    container_name: mongo2
    command: ["--replSet", "rs0", "--bind_ip_all", "--port", "27017", "--auth"]
    volumes:
      - mongo2_data:/data/db
    ports:
      - "27018:27017"
    depends_on:
      - mongo1
    networks:
      - mongo_network

  mongo3:
    image: mongo:7.0
    container_name: mongo3
    command: ["--replSet", "rs0", "--bind_ip_all", "--port", "27017", "--auth"]
    volumes:
      - mongo3_data:/data/db
    ports:
      - "27019:27017"
    depends_on:
      - mongo1
    networks:
      - mongo_network

  mongo-init:
    image: mongo:7.0
    container_name: mongo-init
    depends_on:
      - mongo1
      - mongo2
      - mongo3
    command: >
      mongosh --host mongo1:27017 -u admin -p password --authenticationDatabase admin --eval "
        rs.initiate({
          _id: 'rs0',
          members: [
            { _id: 0, host: 'mongo1:27017', priority: 2 },
            { _id: 1, host: 'mongo2:27017', priority: 1 },
            { _id: 2, host: 'mongo3:27017', priority: 1 }
          ]
        });
      "
    networks:
      - mongo_network

networks:
  mongo_network:
    driver: bridge

volumes:
  mongo1_data:
  mongo2_data:
  mongo3_data:
```

### Initialisation du replica set

Le replica set est initialisé automatiquement via le service `mongo-init`. Ce service utilise la commande `rs.initiate()` pour configurer le replica set avec trois membres :
- mongo1 - nœud primaire (avec une priorité plus élevée)
- mongo2 - nœud secondaire
- mongo3 - nœud secondaire

Alternativement, le replica set peut être initialisé manuellement :

```javascript
rs.initiate({
  _id: 'rs0',
  members: [
    { _id: 0, host: 'mongo1:27017', priority: 2 },
    { _id: 1, host: 'mongo2:27017', priority: 1 },
    { _id: 2, host: 'mongo3:27017', priority: 1 }
  ]
});
```

### Vérification du statut du replica set

Pour vérifier l'état du replica set :

```javascript
rs.status();
```

Cette commande affiche des informations détaillées sur chaque membre, leur état (PRIMARY ou SECONDARY), et la santé du replica set.

### Connexion au replica set

La connexion à un replica set utilise une chaîne de connexion URI spéciale incluant tous les membres et le nom du replica set :

```
mongodb://admin:password@mongo1:27017,mongo2:27017,mongo3:27017/admin?replicaSet=rs0
```

Pour se connecter depuis une machine locale vers les conteneurs exposés :

```
mongodb://admin:password@localhost:27017,localhost:27018,localhost:27019/admin?replicaSet=rs0
```

### Lecture depuis les secondaires

Par défaut, MongoDB ne permet pas la lecture depuis les secondaires. Pour autoriser cela, on peut utiliser l'option `readPreference` :

```javascript
// Se connecter avec une préférence de lecture
const client = new MongoClient("mongodb://admin:password@mongo1:27017,mongo2:27017,mongo3:27017/admin?replicaSet=rs0&readPreference=secondaryPreferred");
```

Ou dans le shell MongoDB :

```javascript
// Activer la lecture depuis les secondaires
db.getMongo().setReadPref("secondaryPreferred");
```

Les différentes options de `readPreference` sont :
- `primary` - lit toujours depuis le primaire (par défaut)
- `primaryPreferred` - lit depuis le primaire, mais utilise un secondaire si le primaire n'est pas disponible
- `secondary` - lit uniquement depuis les secondaires
- `secondaryPreferred` - lit depuis les secondaires, mais utilise le primaire si aucun secondaire n'est disponible
- `nearest` - lit depuis le membre avec la latence réseau la plus faible

## 3. Intégration dans une application

Pour notre exemple d'intégration, nous utilisons Python avec la bibliothèque PyMongo.

### Installation des dépendances

```bash
pip install pymongo
```

### Code de connexion

```python
from pymongo import MongoClient
import pprint

# Connexion à MongoDB Standalone
def connect_standalone():
    # URI de connexion avec authentification
    uri = "mongodb://testuser:testpassword@localhost:27017/testdb"
    client = MongoClient(uri)
    return client

# Connexion à MongoDB Replica Set
def connect_replicaset():
    # URI avec les membres du replica set
    uri = "mongodb://testuser:testpassword@localhost:27017,localhost:27018,localhost:27019/testdb?replicaSet=rs0"
    # Spécifier readPreference pour permettre la lecture depuis les secondaires
    client = MongoClient(uri, readPreference='secondaryPreferred')
    return client

# Fonction principale pour tester les connexions
def test_connection(connection_type="standalone"):
    if connection_type == "standalone":
        client = connect_standalone()
    else:
        client = connect_replicaset()
    
    try:
        # Vérifier la connexion
        server_info = client.server_info()
        print(f"Connecté à MongoDB version {server_info['version']}")
        
        # Obtenir une référence à notre base de données
        db = client.testdb
        
        # Créer ou se référer à une collection
        collection = db.test_collection
        
        # Insérer un document
        document = {
            "name": "Test integration",
            "value": 1000,
            "tags": ["python", "integration"],
            "timestamp": datetime.now()
        }
        insert_result = collection.insert_one(document)
        print(f"Document inséré avec ID: {insert_result.inserted_id}")
        
        # Requête simple
        results = collection.find({"tags": "python"})
        print("Documents trouvés:")
        for doc in results:
            pprint.pprint(doc)
        
        # Mise à jour
        update_result = collection.update_one(
            {"name": "Test integration"},
            {"$set": {"updated": True}}
        )
        print(f"Documents mis à jour: {update_result.modified_count}")
        
        # Suppression
        delete_result = collection.delete_many({"name": "Test integration"})
        print(f"Documents supprimés: {delete_result.deleted_count}")
        
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        client.close()
        print("Connexion fermée")

if __name__ == "__main__":
    from datetime import datetime
    
    print("Test avec MongoDB Standalone")
    test_connection("standalone")
    
    print("\nTest avec MongoDB Replica Set")
    test_connection("replicaset")
```

Ce code démontre :
- La connexion sécurisée avec authentification
- L'insertion de documents
- Les requêtes avec filtres
- La mise à jour et la suppression de documents
- L'utilisation de différentes chaînes de connexion selon le mode de déploiement

### Test et résultats

Les résultats attendus de l'exécution du script :

```
Test avec MongoDB Standalone
Connecté à MongoDB version 7.0.x
Document inséré avec ID: 64f32a8b9c1d2a3b4e5f6a7b
Documents trouvés:
{'_id': ObjectId('64f32a8b9c1d2a3b4e5f6a7b'),
 'name': 'Test integration',
 'tags': ['python', 'integration'],
 'timestamp': datetime.datetime(2025, 5, 16, 10, 30, 0, 123000),
 'value': 1000}
Documents mis à jour: 1
Documents supprimés: 1
Connexion fermée

Test avec MongoDB Replica Set
Connecté à MongoDB version 7.0.x
Document inséré avec ID: 64f32a8b9c1d2a3b4e5f6a7c
Documents trouvés:
{'_id': ObjectId('64f32a8b9c1d2a3b4e5f6a7c'),
 'name': 'Test integration',
 'tags': ['python', 'integration'],
 'timestamp': datetime.datetime(2025, 5, 16, 10, 30, 0, 456000),
 'value': 1000}
Documents mis à jour: 1
Documents supprimés: 1
Connexion fermée
```

## 4. MongoDB Sharding (Bonus)

### Architecture choisie

Pour notre architecture de sharding, nous utilisons :
- 3 shards (chacun constitué d'un replica set à 1 nœud)
- 1 config server (replica set à 1 nœud)
- 1 mongos router

Cette configuration est suffisante pour démontrer les principes du sharding tout en minimisant les ressources nécessaires.

Le fichier `docker-compose.yml` dans le dossier `mongo/sharding` définit notre configuration :

```yaml
version: '3.8'
services:
  # Config Server
  configsvr:
    image: mongo:7.0
    container_name: configsvr
    command: mongod --configsvr --replSet configrs --port 27017 --dbpath /data/db
    volumes:
      - configsvr_data:/data/db
    networks:
      - mongo_network

  # Shard 1
  shard1:
    image: mongo:7.0
    container_name: shard1
    command: mongod --shardsvr --replSet shard1rs --port 27017 --dbpath /data/db
    volumes:
      - shard1_data:/data/db
    networks:
      - mongo_network

  # Shard 2
  shard2:
    image: mongo:7.0
    container_name: shard2
    command: mongod --shardsvr --replSet shard2rs --port 27017 --dbpath /data/db
    volumes:
      - shard2_data:/data/db
    networks:
      - mongo_network

  # Shard 3
  shard3:
    image: mongo:7.0
    container_name: shard3
    command: mongod --shardsvr --replSet shard3rs --port 27017 --dbpath /data/db
    volumes:
      - shard3_data:/data/db
    networks:
      - mongo_network

  # Router
  mongos:
    image: mongo:7.0
    container_name: mongos
    command: mongos --configdb configrs/configsvr:27017 --port 27017
    ports:
      - "27020:27017"
    depends_on:
      - configsvr
      - shard1
      - shard2
      - shard3
    networks:
      - mongo_network

  # Service d'initialisation
  mongo-shard-setup:
    image: mongo:7.0
    container_name: mongo-shard-setup
    depends_on:
      - configsvr
      - shard1
      - shard2
      - shard3
      - mongos
    volumes:
      - ./setup-sharding.sh:/setup-sharding.sh
    entrypoint: ["bash", "/setup-sharding.sh"]
    networks:
      - mongo_network

networks:
  mongo_network:
    driver: bridge

volumes:
  configsvr_data:
  shard1_data:
  shard2_data:
  shard3_data:
```

Le script `setup-sharding.sh` initialise les replica sets et configure le sharding :

```bash
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
```

### Choix de la clé de sharding

Pour notre collection `users`, nous avons choisi `userId` comme clé de sharding avec une stratégie de hachage :

```javascript
sh.shardCollection('sharddb.users', { 'userId': 'hashed' });
```

**Justification :**
- **Hashed sharding** - Permet une distribution plus uniforme des données entre les shards
- **Basé sur userId** - Garantit une bonne distribution car les IDs des utilisateurs sont généralement bien répartis
- **Alternative à une clé par plage** - Évite les problèmes de "hot spots" que pourrait causer une clé par plage (range sharding)

Autres stratégies considérées :
- **Sharding par plage sur region** - Pourrait causer un déséquilibre si certaines régions ont beaucoup plus d'utilisateurs
- **Clé composée (region, userId)** - Utile si nous voulions co-localiser les utilisateurs d'une même région

### Observation de la distribution

Après l'insertion de 1000 documents, la commande `sh.status()` montre comment les données sont distribuées entre les shards.

Résultat attendu :
```
--- Sharding Status ---
  sharding version: {
    ...
  }
  
  shards:
    {  "_id" : "shard1rs",  "host" : "shard1rs/shard1:27017",  "state" : 1 }
    {  "_id" : "shard2rs",  "host" : "shard2rs/shard2:27017",  "state" : 1 }
    {  "_id" : "shard3rs",  "host" : "shard3rs/shard3:27017",  "state" : 1 }
  
  active mongoses:
    "5.0.x" : 1
  
  databases:
    {  "_id" : "sharddb",  "primary" : "shard1rs",  "partitioned" : true }
      sharddb.users
        shard key: { "userId" : "hashed" }
        chunks:
            shard1rs  12
            shard2rs  13
            shard3rs  11
        { "userId" : { "$minKey" : 1 } } -->> { "userId" : NumberLong("-6148914691236517204") } on : shard3rs
        ...
```

L'utilisation d'une clé de sharding hachée a réparti les chunks de données de manière relativement uniforme entre les trois shards, avec une légère variation normale dans la distribution.

### Connexion au cluster shardé

Pour se connecter au cluster shardé, nous utilisons le router mongos :

```
mongodb://localhost:27020/sharddb
```

Le router mongos se charge d'acheminer les requêtes vers les bons shards en fonction de la clé de sharding.