# Guide de déploiement MongoDB Standalone

Ce guide explique comment déployer et tester une instance MongoDB standalone à l'aide de Docker.

## Prérequis

- Docker et Docker Compose
- Python 3.8+ (pour les tests d'intégration)
- Pip (gestionnaire de paquets Python)

## Déploiement

1. Placez-vous dans le dossier `mongo/standalone`:

```bash
cd mongo/standalone
```

2. Démarrez le container MongoDB:

```bash
docker-compose up -d
```

3. Vérifiez que le container est en cours d'exécution:

```bash
docker ps
```

Vous devriez voir un container nommé `mongodb_standalone` en cours d'exécution.

## Connexion à MongoDB

### Via MongoDB Shell (mongosh)

Pour se connecter à MongoDB en tant qu'administrateur:

```bash
docker exec -it mongodb_standalone mongosh -u admin -p password --authenticationDatabase admin

// then create user if not created

use testdb
db.getUsers()

// if no user create

db.createUser({
  user: "testuser",
  pwd: "testpassword",
  roles: [{ role: "readWrite", db: "testdb" }]
});
```

Pour se connecter en tant qu'utilisateur testdb:

```bash
docker exec -it mongodb_standalone mongosh -u testuser -p testpassword --authenticationDatabase admin testdb
```

### Via MongoDB Compass

Utilisez l'URI de connexion suivant dans MongoDB Compass:

```
mongodb://admin:password@localhost:27017/admin
```

ou

```
mongodb://testuser:testpassword@localhost:27017/testdb
```

## Test de l'intégration Python

1. Installez les dépendances Python:

```bash
cd ../../integration/python
pip install -r requirements.txt
```

2. Exécutez le script de test pour la configuration standalone:

```bash
python tests/test_standalone.py
```
> resultat
![](./image.png)

## Exemples d'opérations MongoDB (mongosh)
### Insertion

```javascript
// Insertion d'un document
db.test_collection.insertOne({
  name: "Document 1",
  value: 42,
  tags: ["test", "sample"]
});

// Insertion de plusieurs documents
db.test_collection.insertMany([
  { name: "Document 2", value: 43 },
  { name: "Document 3", value: 44 }
]);
```

### Requêtes

```javascript
// Trouver tous les documents
db.test_collection.find();

// Trouver avec filtre
db.test_collection.find({ value: { $gt: 42 } });

// Trouver un seul document
db.test_collection.findOne({ name: "Document 1" });
```

### Mise à jour

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

### Suppression

```javascript
// Supprimer un document
db.test_collection.deleteOne({ name: "Document 2" });

// Supprimer plusieurs documents
db.test_collection.deleteMany({ updated: true });
```

## Arrêt du service

Pour arrêter MongoDB:

```bash
docker-compose down
```

Pour arrêter MongoDB et supprimer les volumes (efface toutes les données):

```bash
docker-compose down -v
```