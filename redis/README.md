# Atelier Redis - Solution Complete

## Vue d'ensemble

Cet atelier couvre l'installation, la configuration distribuée et l'intégration de Redis dans une application web.

## Structure du projet

```
redis/
├── README.md                 # Documentation principale
├── docker-compose.yml        # Configuration Redis Master/Slave
├── redis-master.conf         # Configuration du serveur master
├── redis-slave.conf          # Configuration du serveur slave
├── app/
│   ├── app.py               # Application web Flask
│   ├── requirements.txt     # Dépendances Python
│   └── templates/
│       └── index.html       # Interface web
└── scripts/
    ├── install.sh           # Script d'installation
    ├── test-redis.sh        # Tests Redis
    └── demo.sh              # Démonstration complète
```

## Démarrage rapide

1. **Installation et lancement** :
   ```bash
   cd redis
   chmod +x scripts/*.sh
   ./scripts/install.sh
   ```

2. **Lancement de l'infrastructure Redis** :
   ```bash
   docker-compose up -d
   ```

3. **Test de la réplication** :
   ```bash
   ./scripts/test-redis.sh
   ```

4. **Lancement de l'application web** :
   ```bash
   cd app
   python app.py
   ```

5. **Démonstration complète** :
   ```bash
   ./scripts/demo.sh
   ```

## Accès aux services

- **Application web** : http://localhost:5000
- **Redis Master** : localhost:6379
- **Redis Slave** : localhost:6380

## Parties de l'atelier

### ✅ Partie 1 - Installation Redis
- Redis déployé via Docker pour simplicité
- Configuration pour accès distant
- Vérification du fonctionnement

### ✅ Partie 2 - Architecture distribuée (Réplication Master/Slave)
- 1 serveur master (port 6379)
- 1 serveur slave (port 6380)
- Réplication automatique des données
- Tests de fonctionnement

### ✅ Partie 3 - Application web avec cache
- Application Flask en Python
- Stratégie cache-aside
- Simulation de base de données lente (2s)
- TTL des données cachées (60s)

### ✅ Partie 4 - Démonstration
- Gain de performance visible
- Expiration des données
- Fonctionnement de la réplication

## Tests et vérifications

L'atelier inclut des scripts automatisés pour :
- Vérifier l'installation Redis
- Tester la réplication Master/Slave
- Démontrer le gain de performance
- Vérifier l'expiration des données
