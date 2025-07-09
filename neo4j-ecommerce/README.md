# Exercice Neo4j - Modélisation E-commerce

## Objectif
Mise en place d'une base de données graphe avec Neo4j pour modéliser les relations entre clients, commandes et produits dans un contexte e-commerce.

## Structure du projet

```
neo4j-ecommerce/
├── README.md                 # Documentation principale
├── docker-compose.yml        # Configuration Neo4j
├── data/
│   ├── schema.cypher        # Modèle de données
│   ├── insert-data.cypher   # Insertion des données
│   └── queries.cypher       # Requêtes d'exploitation
├── app/
│   ├── app.py              # API REST Flask
│   ├── requirements.txt    # Dépendances Python
│   ├── config.py           # Configuration
│   └── templates/
│       └── index.html      # Interface web
├── docs/
│   ├── schema-diagram.md   # Schéma du graphe
│   └── queries-doc.md      # Documentation des requêtes
└── RAPPORT.md              # Rapport final
```

## Démarrage rapide

1. **Installation Neo4j** :
   ```bash
   docker compose up -d
   ```

2. **Chargement des données** :
   ```bash
   # Accéder à Neo4j Browser : http://localhost:7474
   # Charger le schéma et les données
   ```

3. **Lancement de l'application** :
   ```bash
   cd app
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

4. **Accès aux services** :
   - Neo4j Browser : http://localhost:7474
   - Application web : http://localhost:5000

## Modèle de données

### Nœuds
- **Client** : `(c:Client {id, nom, email, age, ville})`
- **Commande** : `(o:Commande {id, date, total, statut})`
- **Produit** : `(p:Produit {id, nom, prix, categorie, stock})`

### Relations
- **A_EFFECTUÉ** : `(Client)-[:A_EFFECTUÉ]->(Commande)`
- **CONTIENT** : `(Commande)-[:CONTIENT {quantite, prix_unitaire}]->(Produit)`
- **SIMILAIRE** : `(Produit)-[:SIMILAIRE]->(Produit)`

## Requêtes principales

1. Produits achetés par un client
2. Clients ayant acheté un produit
3. Commandes contenant un produit
4. Suggestions de produits basées sur les achats similaires

## Technologies utilisées

- **Base de données** : Neo4j 5.x
- **Backend** : Python Flask
- **Frontend** : HTML/JavaScript/CSS
- **Conteneurisation** : Docker
