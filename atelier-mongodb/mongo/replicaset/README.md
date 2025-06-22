# Guide de déploiement MongoDB Replica Set

Ce guide explique comment déployer et tester un replica set MongoDB à l'aide de Docker.

## Prérequis

- Docker et Docker Compose
- Python 3.8+ (pour les tests d'intégration)
- Pip (gestionnaire de paquets Python)

## Déploiement

1. Placez-vous dans le dossier `mongo/replicaset`, créer un fichier key(requis pour le replicat):

```bash
cd mongo/replicaset
openssl rand -base64 756 > mongo-keyfile
chmod 400 mongo-keyfile


```

2. Démarrez les containers MongoDB:

```bash
docker-compose up -d
```

3. Vérifiez que les containers sont en cours d'exécution:

```bash
docker ps
```
Vous devriez voir 4 containers: `mongo1`, `mongo2`, `mongo3` et `mongo-init`.

![](./image.png)
## Connexion au Replica Set

### Via MongoDB Shell (mongosh)

Pour se connecter au nœud primaire:

```bash
docker exec -it mongo1 mongosh -u admin -p password --authenticationDatabase admin
```

Pour se connecter à un nœud secondaire:

```bash
docker exec -it mongo2 mongosh -u admin -p password --authenticationDatabase admin
```

### Via Chaîne de Connexion URI

Pour se connecter au replica set depuis une application (comme notre script Python):

```
mongodb://testuser:testpassword@localhost:27017,localhost:27018,localhost:27019/testdb?replicaSet=rs0
```

## Test de l'intégration Python

1. Installez les dépendances Python:

```bash
cd ../../integration/python
pip install -r requirements.txt
```

2. Exécutez le script de test pour la configuration replica set:

```bash
python tests/test_replicaset.py
```

## Lecture depuis les Secondaires

Par défaut, MongoDB permet uniquement la lecture depuis le nœud primaire. Pour lire depuis les secondaires, vous devez définir une préférence de lecture. Dans le shell MongoDB:

```javascript
// Activer la lecture depuis les secondaires
db.getMongo().setReadPref("secondaryPreferred")
```

Ou dans votre application Python:

```python
client = MongoClient(uri, readPreference='secondaryPreferred')
```

Les différentes options de préférence de lecture sont:
- `primary`: lecture uniquement depuis le primaire (par défaut)
- `primaryPreferred`: lecture depuis le primaire, mais utilise un secondaire si le primaire n'est pas disponible
- `secondary`: lecture uniquement depuis les secondaires
- `secondaryPreferred`: lecture depuis les secondaires, mais utilise le primaire si aucun secondaire n'est disponible
- `nearest`: lecture depuis le membre avec la latence la plus faible

## Gestion des Pannes

Le replica set permet une haute disponibilité. Pour simuler une panne du nœud primaire et observer le basculement automatique:

```bash
docker stop mongo1
```

Vérifiez ensuite à nouveau le statut:

```bash
docker exec -it mongo2 mongosh -u admin -p password --authenticationDatabase admin
```

Puis dans le shell MongoDB:

```javascript
rs.status()
```

Vous devriez observer qu'un des nœuds secondaires a été promu au rôle de primaire.

## Arrêt du Replica Set

Pour arrêter tous les conteneurs:

```bash
docker-compose down
```

Pour arrêter et supprimer les volumes (efface toutes les données):

```bash
docker-compose down -v
```