# Schéma de la base de données graphe Neo4j E-commerce

## Vue d'ensemble

Ce document décrit le modèle de données utilisé pour représenter un système e-commerce dans Neo4j. Le graphe modélise les relations entre clients, commandes et produits.

## Modèle conceptuel

```
(Client) -[:A_EFFECTUE]-> (Commande) -[:CONTIENT]-> (Produit)
                                         |
                                         v
                                   (Produit) -[:SIMILAIRE]-> (Produit)
```

## Nœuds (Nodes)

### Client
Représente un client de la boutique en ligne.

**Label :** `Client`

**Propriétés :**
- `id` (String) : Identifiant unique du client (ex: "C001")
- `nom` (String) : Nom complet du client
- `email` (String) : Adresse email
- `age` (Integer) : Âge du client
- `ville` (String) : Ville de résidence

**Exemple :**
```cypher
(c:Client {
    id: 'C001', 
    nom: 'Jean Dupont', 
    email: 'jean.dupont@email.com', 
    age: 35, 
    ville: 'Paris'
})
```

### Commande
Représente une commande passée par un client.

**Label :** `Commande`

**Propriétés :**
- `id` (String) : Identifiant unique de la commande (ex: "O001")
- `date` (Date) : Date de la commande
- `total` (Float) : Montant total de la commande
- `statut` (String) : État de la commande (Livree, En_cours, Preparee)

**Exemple :**
```cypher
(o:Commande {
    id: 'O001', 
    date: date('2024-01-15'), 
    total: 929.98, 
    statut: 'Livree'
})
```

### Produit
Représente un produit disponible à la vente.

**Label :** `Produit`

**Propriétés :**
- `id` (String) : Identifiant unique du produit (ex: "P001")
- `nom` (String) : Nom du produit
- `prix` (Float) : Prix unitaire
- `categorie` (String) : Catégorie du produit
- `stock` (Integer) : Quantité en stock

**Exemple :**
```cypher
(p:Produit {
    id: 'P001', 
    nom: 'Smartphone Samsung Galaxy', 
    prix: 699.99, 
    categorie: 'Electronique', 
    stock: 25
})
```

## Relations (Relationships)

### A_EFFECTUE
Relation entre un client et une commande qu'il a passée.

**Type :** `A_EFFECTUE`
**Direction :** `(Client) -[:A_EFFECTUE]-> (Commande)`
**Propriétés :** Aucune

**Exemple :**
```cypher
(c:Client {id: 'C001'})-[:A_EFFECTUE]->(o:Commande {id: 'O001'})
```

### CONTIENT
Relation entre une commande et les produits qu'elle contient.

**Type :** `CONTIENT`
**Direction :** `(Commande) -[:CONTIENT]-> (Produit)`

**Propriétés :**
- `quantite` (Integer) : Quantité commandée
- `prix_unitaire` (Float) : Prix unitaire au moment de la commande

**Exemple :**
```cypher
(o:Commande {id: 'O001'})-[:CONTIENT {quantite: 2, prix_unitaire: 29.99}]->(p:Produit {id: 'P004'})
```

### SIMILAIRE
Relation entre produits similaires (pour les suggestions).

**Type :** `SIMILAIRE`
**Direction :** `(Produit) -[:SIMILAIRE]-> (Produit)`
**Propriétés :** Aucune

**Exemple :**
```cypher
(p1:Produit {id: 'P001'})-[:SIMILAIRE]->(p2:Produit {id: 'P008'})
```

## Contraintes et Index

### Contraintes d'unicité
```cypher
CREATE CONSTRAINT client_id_unique FOR (c:Client) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT commande_id_unique FOR (o:Commande) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT produit_id_unique FOR (p:Produit) REQUIRE p.id IS UNIQUE;
```

### Index de performance
```cypher
CREATE INDEX client_email_index FOR (c:Client) ON (c.email);
CREATE INDEX produit_categorie_index FOR (p:Produit) ON (p.categorie);
CREATE INDEX commande_date_index FOR (o:Commande) ON (o.date);
```

## Diagramme visuel

```
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │   Client    │       │  Commande   │       │   Produit   │
    │             │       │             │       │             │
    │ id: C001    │       │ id: O001    │       │ id: P001    │
    │ nom: Jean   │ ───── │ date: 2024  │ ───── │ nom: Phone  │
    │ email: ...  │A_EFFECTUE total: 929 │CONTIENT prix: 699  │
    │ age: 35     │       │ statut: ... │{qty:1} categorie:  │
    │ ville: Paris│       │             │       │ Electronique│
    └─────────────┘       └─────────────┘       └─────────────┘
                                                        │
                                                        │ SIMILAIRE
                                                        ▼
                                                ┌─────────────┐
                                                │   Produit   │
                                                │             │
                                                │ id: P008    │
                                                │ nom: Watch  │
                                                │ prix: 399   │
                                                │ categorie:  │
                                                │ Electronique│
                                                └─────────────┘
```

## Avantages de ce modèle

1. **Flexibilité** : Facilite l'ajout de nouveaux types de relations
2. **Performance** : Les requêtes de traversée sont optimisées
3. **Intuitivité** : Le modèle reflète naturellement les relations business
4. **Extensibilité** : Peut facilement intégrer de nouveaux concepts (catégories, fournisseurs, etc.)

## Exemples de requêtes typiques

1. **Navigation de graphe** : Suivre les chemins Client → Commande → Produit
2. **Recommandations** : Utiliser les relations SIMILAIRE et les patterns d'achat
3. **Analyses** : Agréger les données sur les relations pour des insights business
