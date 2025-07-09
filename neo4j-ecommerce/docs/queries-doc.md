# Documentation des Requêtes Neo4j E-commerce

## Vue d'ensemble

Ce document présente l'ensemble des requêtes Cypher développées pour explorer et exploiter la base de données graphe e-commerce. Chaque requête est documentée avec son objectif, son usage et des exemples.

## 1. Requêtes de base - Exploration des données

### 1.1 Trouver tous les produits achetés par un client

**Objectif :** Récupérer l'historique d'achat d'un client spécifique.

**Requête :**
```cypher
MATCH (c:Client {id: $client_id})-[:A_EFFECTUE]->(o:Commande)-[r:CONTIENT]->(p:Produit)
RETURN c.nom AS client, 
       p.nom AS produit, 
       p.categorie AS categorie,
       r.quantite AS quantite,
       r.prix_unitaire AS prix_unitaire,
       o.date AS date_commande
ORDER BY o.date DESC;
```

**Usage :** 
- Interface client pour afficher l'historique
- Service client pour le support
- Analyse du comportement d'achat

**Exemple de résultat :**
```
client      | produit           | categorie     | quantite | prix_unitaire | date_commande
Jean Dupont | Smartphone Galaxy | Electronique  | 1        | 699.99        | 2024-01-15
Jean Dupont | T-shirt Nike      | Vetements     | 2        | 29.99         | 2024-01-15
```

### 1.2 Identifier les clients ayant acheté un produit donné

**Objectif :** Connaître la base de clients pour un produit spécifique.

**Requête :**
```cypher
MATCH (p:Produit {id: $produit_id})<-[r:CONTIENT]-(o:Commande)<-[:A_EFFECTUE]-(c:Client)
RETURN c.nom AS client, 
       c.email AS email, 
       c.ville AS ville,
       r.quantite AS quantite_achetee,
       o.date AS date_achat,
       o.total AS total_commande
ORDER BY o.date DESC;
```

**Usage :**
- Campagnes marketing ciblées
- Étude de marché
- Relance commerciale

### 1.3 Lister les commandes contenant un produit spécifique

**Objectif :** Analyser les ventes d'un produit particulier.

**Requête :**
```cypher
MATCH (p:Produit {id: $produit_id})<-[r:CONTIENT]-(o:Commande)
RETURN o.id AS commande_id,
       o.date AS date,
       o.total AS total,
       o.statut AS statut,
       r.quantite AS quantite,
       r.prix_unitaire AS prix_unitaire
ORDER BY o.date DESC;
```

**Usage :**
- Suivi des ventes par produit
- Analyse de la performance
- Gestion des stocks

## 2. Requêtes de recommandation

### 2.1 Suggestions basées sur les achats similaires (Collaborative Filtering)

**Objectif :** Recommander des produits basés sur le comportement d'autres clients similaires.

**Requête :**
```cypher
MATCH (client:Client {id: $client_id})-[:A_EFFECTUE]->(o1:Commande)-[:CONTIENT]->(p1:Produit)
MATCH (p1)<-[:CONTIENT]-(o2:Commande)<-[:A_EFFECTUE]-(autres_clients:Client)
WHERE autres_clients <> client
MATCH (autres_clients)-[:A_EFFECTUE]->(o3:Commande)-[:CONTIENT]->(produits_suggeres:Produit)
WHERE NOT EXISTS((client)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(produits_suggeres))
RETURN produits_suggeres.nom AS produit_suggere,
       produits_suggeres.prix AS prix,
       produits_suggeres.categorie AS categorie,
       COUNT(DISTINCT autres_clients) AS nb_clients_similaires
ORDER BY nb_clients_similaires DESC, produits_suggeres.prix ASC
LIMIT 5;
```

**Algorithme :**
1. Trouve les produits achetés par le client cible
2. Identifie les autres clients ayant acheté ces mêmes produits
3. Recommande les produits achetés par ces clients similaires
4. Exclut les produits déjà achetés par le client cible

### 2.2 Suggestions basées sur la similarité de produits

**Objectif :** Recommander des produits similaires à ceux déjà achetés.

**Requête :**
```cypher
MATCH (client:Client {id: $client_id})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p_achetes:Produit)
MATCH (p_achetes)-[:SIMILAIRE]->(p_similaires:Produit)
WHERE NOT EXISTS((client)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p_similaires))
RETURN DISTINCT p_similaires.nom AS produit,
       p_similaires.prix AS prix,
       p_similaires.categorie AS categorie,
       COUNT(p_achetes) AS score_similarite
ORDER BY score_similarite DESC, p_similaires.prix ASC
LIMIT 3;
```

### 2.3 Produits fréquemment achetés ensemble

**Objectif :** Identifier les associations de produits pour le cross-selling.

**Requête :**
```cypher
MATCH (p1:Produit)<-[:CONTIENT]-(o:Commande)-[:CONTIENT]->(p2:Produit)
WHERE p1 <> p2
RETURN p1.nom AS produit1,
       p2.nom AS produit2,
       COUNT(o) AS fois_achetes_ensemble
ORDER BY fois_achetes_ensemble DESC
LIMIT 10;
```

## 3. Requêtes d'analyse business

### 3.1 Top des produits les plus vendus

**Objectif :** Identifier les produits performants.

**Requête :**
```cypher
MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
RETURN p.nom AS produit,
       p.categorie AS categorie,
       SUM(r.quantite) AS total_vendu,
       SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires,
       COUNT(DISTINCT r) AS nb_commandes
ORDER BY total_vendu DESC
LIMIT 10;
```

**Métriques calculées :**
- Quantité totale vendue
- Chiffre d'affaires généré
- Nombre de commandes distinctes

### 3.2 Clients les plus actifs

**Objectif :** Segmenter les clients par activité.

**Requête :**
```cypher
MATCH (c:Client)-[:A_EFFECTUE]->(o:Commande)
RETURN c.nom AS client,
       c.email AS email,
       c.ville AS ville,
       COUNT(o) AS nb_commandes,
       SUM(o.total) AS total_depense
ORDER BY nb_commandes DESC, total_depense DESC
LIMIT 10;
```

### 3.3 Analyse des revenus par catégorie

**Objectif :** Comprendre la performance des catégories de produits.

**Requête :**
```cypher
MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
RETURN p.categorie AS categorie,
       COUNT(DISTINCT p) AS nb_produits_differents,
       SUM(r.quantite) AS quantite_totale,
       SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires
ORDER BY chiffre_affaires DESC;
```

## 4. Requêtes d'analyse géographique

### 4.1 Clients similaires par ville

**Objectif :** Analyser les préférences locales.

**Requête :**
```cypher
MATCH (c1:Client {ville: $ville})-[:A_EFFECTUE]->(o1:Commande)-[:CONTIENT]->(p:Produit)
MATCH (c2:Client {ville: $ville})-[:A_EFFECTUE]->(o2:Commande)-[:CONTIENT]->(p)
WHERE c1 <> c2
RETURN c1.nom AS client1,
       c2.nom AS client2,
       COUNT(DISTINCT p) AS produits_communs,
       COLLECT(DISTINCT p.nom) AS produits
ORDER BY produits_communs DESC;
```

## 5. Requêtes de statistiques générales

### 5.1 Vue d'ensemble de la base

**Objectif :** Obtenir des métriques globales.

**Requête :**
```cypher
MATCH (c:Client) WITH COUNT(c) AS nb_clients
MATCH (o:Commande) WITH nb_clients, COUNT(o) AS nb_commandes
MATCH (p:Produit) WITH nb_clients, nb_commandes, COUNT(p) AS nb_produits
MATCH ()-[r:CONTIENT]->() WITH nb_clients, nb_commandes, nb_produits, COUNT(r) AS nb_achats
RETURN nb_clients, nb_commandes, nb_produits, nb_achats;
```

## 6. Optimisations et bonnes pratiques

### 6.1 Utilisation des paramètres

Toujours utiliser des paramètres pour éviter l'injection et optimiser le cache :
```cypher
// ✅ Bon
MATCH (c:Client {id: $client_id})

// ❌ Mauvais
MATCH (c:Client {id: 'C001'})
```

### 6.2 Index et contraintes

Les requêtes bénéficient des index créés :
- `client_id_unique` : recherche rapide par ID client
- `produit_categorie_index` : filtrage par catégorie
- `commande_date_index` : tri par date

### 6.3 Limitation des résultats

Utiliser `LIMIT` pour les requêtes pouvant retourner beaucoup de résultats :
```cypher
MATCH (p:Produit)
RETURN p
ORDER BY p.prix DESC
LIMIT 10;
```

## 7. Cas d'usage avancés

### 7.1 Détection de fraude

Identifier des patterns suspects :
```cypher
MATCH (c:Client)-[:A_EFFECTUE]->(o:Commande)
WHERE o.total > 1000
AND o.date > date('2024-01-01')
RETURN c.nom, COUNT(o) AS commandes_importantes
ORDER BY commandes_importantes DESC;
```

### 7.2 Analyse de la fidélité

Clients récurrents par période :
```cypher
MATCH (c:Client)-[:A_EFFECTUE]->(o:Commande)
WHERE o.date >= date('2024-01-01') AND o.date <= date('2024-03-31')
RETURN c.nom, 
       COUNT(o) AS commandes_trimestre,
       SUM(o.total) AS depense_totale
HAVING commandes_trimestre > 1
ORDER BY commandes_trimestre DESC;
```
