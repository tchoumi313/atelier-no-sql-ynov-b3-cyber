# Atelier MongoDB

Ce projet documente l'implémentation de MongoDB selon différents modes de déploiement, ainsi que son intégration dans une application.

## Objectifs pédagogiques

- Comprendre les principes d'une base de données orientée document
- Déployer MongoDB selon différents modes : standalone, replica set, puis sharding (bonus)
- Intégrer MongoDB dans une application avec un langage de programmation
- Documenter toutes les étapes de l'atelier
- Versionner le projet avec Git

## Structure du projet

```
atelier-mongodb/
├── docs/
│   └── rapport.md
├── mongo/
│   ├── standalone/
│   ├── replicaset/
│   └── sharding/         # Bonus
├── integration/
│   └── python/           # Le langage choisi pour l'intégration
│       └── tests/
└── README.md
```

## Contenu

1. **MongoDB Standalone** - Installation et configuration d'une instance MongoDB unique
2. **MongoDB Replica Set** - Déploiement d'un ensemble de réplication avec plusieurs instances
3. **Intégration dans une application** - Utilisation de MongoDB dans une application simple
4. **MongoDB Sharding** (Bonus) - Configuration d'un cluster MongoDB avec sharding

## Prérequis

- Docker et Docker Compose (optionnel mais recommandé)
- Python 3.8+ (pour l'intégration)
- Git

## Guide rapide

Voir le fichier [docs/rapport.md](docs/rapport.md) pour une documentation détaillée des étapes de chaque partie.