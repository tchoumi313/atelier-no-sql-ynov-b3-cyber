// Insertion des données de test pour l'e-commerce
// Script à exécuter dans Neo4j Browser

// Suppression des données existantes (optionnel)
MATCH (n) DETACH DELETE n;

// 1. Création des clients
CREATE (c1:Client {id: 'C001', nom: 'Jean Dupont', email: 'jean.dupont@email.com', age: 35, ville: 'Paris'})
CREATE (c2:Client {id: 'C002', nom: 'Marie Martin', email: 'marie.martin@email.com', age: 28, ville: 'Lyon'})
CREATE (c3:Client {id: 'C003', nom: 'Pierre Bernard', email: 'pierre.bernard@email.com', age: 42, ville: 'Marseille'})
CREATE (c4:Client {id: 'C004', nom: 'Sophie Dubois', email: 'sophie.dubois@email.com', age: 31, ville: 'Toulouse'})
CREATE (c5:Client {id: 'C005', nom: 'Luc Moreau', email: 'luc.moreau@email.com', age: 39, ville: 'Nice'});

// 2. Création des produits
CREATE (p1:Produit {id: 'P001', nom: 'Smartphone Samsung Galaxy', prix: 699.99, categorie: 'Electronique', stock: 25})
CREATE (p2:Produit {id: 'P002', nom: 'Laptop Dell XPS', prix: 1299.99, categorie: 'Electronique', stock: 15})
CREATE (p3:Produit {id: 'P003', nom: 'Casque Audio Sony', prix: 199.99, categorie: 'Electronique', stock: 30})
CREATE (p4:Produit {id: 'P004', nom: 'T-shirt Nike', prix: 29.99, categorie: 'Vetements', stock: 100})
CREATE (p5:Produit {id: 'P005', nom: 'Jeans Levis', prix: 89.99, categorie: 'Vetements', stock: 50})
CREATE (p6:Produit {id: 'P006', nom: 'Chaussures Adidas', prix: 119.99, categorie: 'Vetements', stock: 40})
CREATE (p7:Produit {id: 'P007', nom: 'Livre "Neo4j Guide"', prix: 39.99, categorie: 'Livres', stock: 20})
CREATE (p8:Produit {id: 'P008', nom: 'Montre Apple Watch', prix: 399.99, categorie: 'Electronique', stock: 12})
CREATE (p9:Produit {id: 'P009', nom: 'Sac à dos Eastpak', prix: 59.99, categorie: 'Accessoires', stock: 35})
CREATE (p10:Produit {id: 'P010', nom: 'Clavier mecanique', prix: 149.99, categorie: 'Electronique', stock: 18});

// 3. Création des commandes
CREATE (o1:Commande {id: 'O001', date: date('2024-01-15'), total: 929.98, statut: 'Livree'})
CREATE (o2:Commande {id: 'O002', date: date('2024-01-20'), total: 199.99, statut: 'Livree'})
CREATE (o3:Commande {id: 'O003', date: date('2024-02-05'), total: 1419.98, statut: 'En_cours'})
CREATE (o4:Commande {id: 'O004', date: date('2024-02-10'), total: 239.97, statut: 'Livree'})
CREATE (o5:Commande {id: 'O005', date: date('2024-02-15'), total: 89.99, statut: 'Livree'})
CREATE (o6:Commande {id: 'O006', date: date('2024-03-01'), total: 549.98, statut: 'Preparee'})
CREATE (o7:Commande {id: 'O007', date: date('2024-03-05'), total: 179.98, statut: 'Livree'})
CREATE (o8:Commande {id: 'O008', date: date('2024-03-10'), total: 39.99, statut: 'Livree'});

// 4. Relations CLIENT -> COMMANDE (A_EFFECTUÉ)
MATCH (c1:Client {id: 'C001'}), (o1:Commande {id: 'O001'}) CREATE (c1)-[:A_EFFECTUE]->(o1);
MATCH (c1:Client {id: 'C001'}), (o3:Commande {id: 'O003'}) CREATE (c1)-[:A_EFFECTUE]->(o3);
MATCH (c2:Client {id: 'C002'}), (o2:Commande {id: 'O002'}) CREATE (c2)-[:A_EFFECTUE]->(o2);
MATCH (c2:Client {id: 'C002'}), (o6:Commande {id: 'O006'}) CREATE (c2)-[:A_EFFECTUE]->(o6);
MATCH (c3:Client {id: 'C003'}), (o4:Commande {id: 'O004'}) CREATE (c3)-[:A_EFFECTUE]->(o4);
MATCH (c3:Client {id: 'C003'}), (o7:Commande {id: 'O007'}) CREATE (c3)-[:A_EFFECTUE]->(o7);
MATCH (c4:Client {id: 'C004'}), (o5:Commande {id: 'O005'}) CREATE (c4)-[:A_EFFECTUE]->(o5);
MATCH (c5:Client {id: 'C005'}), (o8:Commande {id: 'O008'}) CREATE (c5)-[:A_EFFECTUE]->(o8);

// 5. Relations COMMANDE -> PRODUIT (CONTIENT)
// Commande O001 (Jean Dupont)
MATCH (o1:Commande {id: 'O001'}), (p1:Produit {id: 'P001'}) CREATE (o1)-[:CONTIENT {quantite: 1, prix_unitaire: 699.99}]->(p1);
MATCH (o1:Commande {id: 'O001'}), (p4:Produit {id: 'P004'}) CREATE (o1)-[:CONTIENT {quantite: 2, prix_unitaire: 29.99}]->(p4);
MATCH (o1:Commande {id: 'O001'}), (p9:Produit {id: 'P009'}) CREATE (o1)-[:CONTIENT {quantite: 1, prix_unitaire: 59.99}]->(p9);

// Commande O002 (Marie Martin)
MATCH (o2:Commande {id: 'O002'}), (p3:Produit {id: 'P003'}) CREATE (o2)-[:CONTIENT {quantite: 1, prix_unitaire: 199.99}]->(p3);

// Commande O003 (Jean Dupont)
MATCH (o3:Commande {id: 'O003'}), (p2:Produit {id: 'P002'}) CREATE (o3)-[:CONTIENT {quantite: 1, prix_unitaire: 1299.99}]->(p2);
MATCH (o3:Commande {id: 'O003'}), (p6:Produit {id: 'P006'}) CREATE (o3)-[:CONTIENT {quantite: 1, prix_unitaire: 119.99}]->(p6);

// Commande O004 (Pierre Bernard)
MATCH (o4:Commande {id: 'O004'}), (p4:Produit {id: 'P004'}) CREATE (o4)-[:CONTIENT {quantite: 3, prix_unitaire: 29.99}]->(p4);
MATCH (o4:Commande {id: 'O004'}), (p10:Produit {id: 'P010'}) CREATE (o4)-[:CONTIENT {quantite: 1, prix_unitaire: 149.99}]->(p10);

// Commande O005 (Sophie Dubois)
MATCH (o5:Commande {id: 'O005'}), (p5:Produit {id: 'P005'}) CREATE (o5)-[:CONTIENT {quantite: 1, prix_unitaire: 89.99}]->(p5);

// Commande O006 (Marie Martin)
MATCH (o6:Commande {id: 'O006'}), (p8:Produit {id: 'P008'}) CREATE (o6)-[:CONTIENT {quantite: 1, prix_unitaire: 399.99}]->(p8);
MATCH (o6:Commande {id: 'O006'}), (p10:Produit {id: 'P010'}) CREATE (o6)-[:CONTIENT {quantite: 1, prix_unitaire: 149.99}]->(p10);

// Commande O007 (Pierre Bernard)
MATCH (o7:Commande {id: 'O007'}), (p3:Produit {id: 'P003'}) CREATE (o7)-[:CONTIENT {quantite: 1, prix_unitaire: 199.99}]->(p3);

// Commande O008 (Luc Moreau)
MATCH (o8:Commande {id: 'O008'}), (p7:Produit {id: 'P007'}) CREATE (o8)-[:CONTIENT {quantite: 1, prix_unitaire: 39.99}]->(p7);

// 6. Relations de similarité entre produits (pour les suggestions)
MATCH (p1:Produit {id: 'P001'}), (p8:Produit {id: 'P008'}) CREATE (p1)-[:SIMILAIRE]->(p8);
MATCH (p8:Produit {id: 'P008'}), (p1:Produit {id: 'P001'}) CREATE (p8)-[:SIMILAIRE]->(p1);
MATCH (p2:Produit {id: 'P002'}), (p10:Produit {id: 'P010'}) CREATE (p2)-[:SIMILAIRE]->(p10);
MATCH (p10:Produit {id: 'P010'}), (p2:Produit {id: 'P002'}) CREATE (p10)-[:SIMILAIRE]->(p2);
MATCH (p3:Produit {id: 'P003'}), (p1:Produit {id: 'P001'}) CREATE (p3)-[:SIMILAIRE]->(p1);
MATCH (p4:Produit {id: 'P004'}), (p5:Produit {id: 'P005'}) CREATE (p4)-[:SIMILAIRE]->(p5);
MATCH (p5:Produit {id: 'P005'}), (p6:Produit {id: 'P006'}) CREATE (p5)-[:SIMILAIRE]->(p6);
MATCH (p6:Produit {id: 'P006'}), (p4:Produit {id: 'P004'}) CREATE (p6)-[:SIMILAIRE]->(p4);
