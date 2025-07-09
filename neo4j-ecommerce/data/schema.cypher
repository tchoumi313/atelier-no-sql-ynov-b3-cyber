// Schéma de la base de données Neo4j E-commerce
// Définition des contraintes et index

// Contraintes d'unicité
CREATE CONSTRAINT client_id_unique IF NOT EXISTS FOR (c:Client) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT commande_id_unique IF NOT EXISTS FOR (o:Commande) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT produit_id_unique IF NOT EXISTS FOR (p:Produit) REQUIRE p.id IS UNIQUE;

// Index pour améliorer les performances
CREATE INDEX client_email_index IF NOT EXISTS FOR (c:Client) ON (c.email);
CREATE INDEX produit_categorie_index IF NOT EXISTS FOR (p:Produit) ON (p.categorie);
CREATE INDEX commande_date_index IF NOT EXISTS FOR (o:Commande) ON (o.date);
