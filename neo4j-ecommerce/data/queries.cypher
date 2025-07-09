// Requêtes d'exploitation de la base de données Neo4j E-commerce
// Collection de requêtes utiles pour analyser les données

// 1. TROUVER TOUS LES PRODUITS ACHETÉS PAR UN CLIENT
// Exemple : Produits achetés par Jean Dupont (C001)
MATCH (c:Client {id: 'C001'})-[:A_EFFECTUE]->(o:Commande)-[r:CONTIENT]->(p:Produit)
RETURN c.nom AS client, 
       p.nom AS produit, 
       p.prix AS prix, 
       r.quantite AS quantite,
       o.date AS date_commande
ORDER BY o.date DESC;

// Version générique pour n'importe quel client
MATCH (c:Client {nom: $client_nom})-[:A_EFFECTUE]->(o:Commande)-[r:CONTIENT]->(p:Produit)
RETURN c.nom AS client, 
       p.nom AS produit, 
       p.categorie AS categorie,
       r.quantite AS quantite,
       r.prix_unitaire AS prix_unitaire,
       o.date AS date_commande
ORDER BY o.date DESC;

// 2. IDENTIFIER LES CLIENTS AYANT ACHETÉ UN PRODUIT DONNÉ
// Exemple : Clients ayant acheté le T-shirt Nike
MATCH (p:Produit {nom: 'T-shirt Nike'})<-[r:CONTIENT]-(o:Commande)<-[:A_EFFECTUE]-(c:Client)
RETURN c.nom AS client, 
       c.email AS email, 
       c.ville AS ville,
       r.quantite AS quantite_achetee,
       o.date AS date_achat
ORDER BY o.date DESC;

// Version générique
MATCH (p:Produit {id: $produit_id})<-[r:CONTIENT]-(o:Commande)<-[:A_EFFECTUE]-(c:Client)
RETURN c.nom AS client, 
       c.email AS email, 
       c.ville AS ville,
       r.quantite AS quantite_achetee,
       o.date AS date_achat,
       o.total AS total_commande
ORDER BY o.date DESC;

// 3. LISTER LES COMMANDES CONTENANT UN PRODUIT SPÉCIFIQUE
MATCH (p:Produit {nom: 'Smartphone Samsung Galaxy'})<-[r:CONTIENT]-(o:Commande)
RETURN o.id AS commande_id,
       o.date AS date,
       o.total AS total,
       o.statut AS statut,
       r.quantite AS quantite,
       r.prix_unitaire AS prix_unitaire
ORDER BY o.date DESC;

// 4. SUGGESTIONS DE PRODUITS BASÉES SUR LES ACHATS SIMILAIRES
// Recommandations pour un client basées sur ce qu'ont acheté d'autres clients similaires
MATCH (client:Client {id: 'C001'})-[:A_EFFECTUE]->(o1:Commande)-[:CONTIENT]->(p1:Produit)
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

// 5. PRODUITS SIMILAIRES DIRECTS
MATCH (p:Produit {id: $produit_id})-[:SIMILAIRE]->(produits_similaires:Produit)
RETURN produits_similaires.nom AS produit,
       produits_similaires.prix AS prix,
       produits_similaires.categorie AS categorie,
       produits_similaires.stock AS stock;

// 6. ANALYSES BUSINESS

// Top 5 des produits les plus vendus
MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
RETURN p.nom AS produit,
       p.categorie AS categorie,
       SUM(r.quantite) AS total_vendu,
       SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires
ORDER BY total_vendu DESC
LIMIT 5;

// Clients les plus actifs (par nombre de commandes)
MATCH (c:Client)-[:A_EFFECTUE]->(o:Commande)
RETURN c.nom AS client,
       c.email AS email,
       COUNT(o) AS nb_commandes,
       SUM(o.total) AS total_depense
ORDER BY nb_commandes DESC, total_depense DESC;

// Revenus par catégorie de produits
MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
RETURN p.categorie AS categorie,
       COUNT(DISTINCT p) AS nb_produits_differents,
       SUM(r.quantite) AS quantite_totale,
       SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires
ORDER BY chiffre_affaires DESC;

// 7. REQUÊTES DE RECOMMANDATION AVANCÉES

// Produits fréquemment achetés ensemble
MATCH (p1:Produit)<-[:CONTIENT]-(o:Commande)-[:CONTIENT]->(p2:Produit)
WHERE p1 <> p2
RETURN p1.nom AS produit1,
       p2.nom AS produit2,
       COUNT(o) AS fois_achetes_ensemble
ORDER BY fois_achetes_ensemble DESC
LIMIT 10;

// Clients dans la même ville ayant des goûts similaires
MATCH (c1:Client {ville: $ville})-[:A_EFFECTUE]->(o1:Commande)-[:CONTIENT]->(p:Produit)
MATCH (c2:Client {ville: $ville})-[:A_EFFECTUE]->(o2:Commande)-[:CONTIENT]->(p)
WHERE c1 <> c2
RETURN c1.nom AS client1,
       c2.nom AS client2,
       COUNT(DISTINCT p) AS produits_communs,
       COLLECT(DISTINCT p.nom) AS produits
ORDER BY produits_communs DESC;

// 8. STATISTIQUES GÉNÉRALES

// Vue d'ensemble de la base
MATCH (c:Client) WITH COUNT(c) AS nb_clients
MATCH (o:Commande) WITH nb_clients, COUNT(o) AS nb_commandes
MATCH (p:Produit) WITH nb_clients, nb_commandes, COUNT(p) AS nb_produits
MATCH ()-[r:CONTIENT]->() WITH nb_clients, nb_commandes, nb_produits, COUNT(r) AS nb_achats
RETURN nb_clients, nb_commandes, nb_produits, nb_achats;
