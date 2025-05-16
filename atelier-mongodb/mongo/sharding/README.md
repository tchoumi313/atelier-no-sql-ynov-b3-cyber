# Guide de déploiement MongoDB Sharded Cluster

Ce guide explique comment déployer et tester un cluster MongoDB avec sharding à l'aide de Docker.

## Prérequis

- Docker et Docker Compose
- Python 3.8+ (pour les tests d'intégration)
- Pip (gestionnaire de paquets Python)

## Architecture du Cluster

Notre cluster shardé est composé de:
- 3 shards (chacun constitué d'un replica set minimal à 1 nœud)
- 1 serveur de configuration (config server, également un replica set minimal)
- 1 router mongos qui distribue les requêtes
- 1 service d'initialisation qui configure le cluster

## Déploiement

1. Placez-vous dans le dossier `mongo/sharding`:

```bash
cd mongo/sharding
```

2. Assurez-vous que le script d'initialisation est exécutable:

```bash
chmod +x setup-sharding.sh
```

3. Démarrez les conteneurs:

```bash
docker-compose up -d
```

4. Vérifiez que les conteneurs sont en cours d'exécution:

```bash
docker ps
```

Vous devriez voir les conteneurs: `configsvr`, `shard1`, `shard2`, `shard3`, `mongos` et `mongo-shard-setup`.

5. Le script `setup-sharding.sh` initialise automatiquement le cluster. Pour vérifier l'état du sharding, connectez-vous au router mongos:

```bash
docker exec -it mongos mongosh
```

Puis dans le shell MongoDB:

```javascript
sh.status()
```

Vous devriez voir les 3 shards configurés et la base de données `sharddb` avec sa collection `users` en mode shardé sur la clé `userId`.

## Connexion au Cluster Shardé

Pour se connecter au cluster shardé, utilisez le router mongos:

```bash
docker exec -it mongos mongosh
```

Ou via URI depuis une application:

```
mongodb://localhost:27020/sharddb
```

## Test de l'intégration Python

1. Installez les dépendances Python:

```bash
cd ../../integration/python
pip install -r requirements.txt
```

2. Exécutez le script de test pour la configuration shardée:

```bash
python tests/test_sharded.py
```

## Exploration du Sharding

### Vérifier la distribution des données

Pour voir comment les données sont distribuées entre les shards:

```javascript
use sharddb
db.users.getShardDistribution()
```

### Ajouter des données et observer la distribution

Pour ajouter plus de données:

```javascript
// Insérer des documents
for (let i = 1; i <= 100; i++) {
  db.users.insertOne({
    userId: 1000 + i,
    name: 'User ' + (1000 + i),
    email: 'user' + (1000 + i) + '@example.com',
    region: ['EU', 'US', 'ASIA'][i % 3]
  });
}

// Vérifier à nouveau la distribution
db.users.getShardDistribution()
```

### Explorer les chunks

Pour voir les chunks (morceaux de données) et leur distribution:

```javascript
use config
db.chunks.find({ns: "sharddb.users"}).pretty()
```

## Comprendre la clé de sharding

Notre cluster utilise une clé de sharding hachée sur le champ `userId`:

```javascript
sh.shardCollection('sharddb.users', { 'userId': 'hashed' })
```

Avantages de cette approche:
- Distribution plus uniforme des données entre les shards
- Réduction des "hot spots" qu'on pourrait avoir avec un sharding par plage

## Arrêt du Cluster

Pour arrêter tous les conteneurs:

```bash
docker-compose down
```

Pour arrêter et supprimer les volumes (efface toutes les données):

```bash
docker-compose down -v
```