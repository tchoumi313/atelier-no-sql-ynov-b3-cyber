#!/usr/bin/env python3
"""
Application Flask pour l'interface avec Neo4j E-commerce
API REST et interface web pour interroger la base de données graphe
"""

import json
from datetime import datetime

from config import Config
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Connexion Neo4j
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query, parameters=None):
        """Exécute une requête et retourne les résultats"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Instance de connexion Neo4j
try:
    neo4j_conn = Neo4jConnection(
        Config.NEO4J_URI, 
        Config.NEO4J_USER, 
        Config.NEO4J_PASSWORD
    )
    print("✅ Connexion Neo4j établie")
except Exception as e:
    print(f"❌ Erreur connexion Neo4j: {e}")
    neo4j_conn = None

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Récupère la liste de tous les clients"""
    try:
        query = """
        MATCH (c:Client)
        RETURN c.id AS id, c.nom AS nom, c.email AS email, 
               c.age AS age, c.ville AS ville
        ORDER BY c.nom
        """
        clients = neo4j_conn.execute_query(query)
        return jsonify(clients)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produits', methods=['GET'])
def get_produits():
    """Récupère la liste de tous les produits"""
    try:
        query = """
        MATCH (p:Produit)
        RETURN p.id AS id, p.nom AS nom, p.prix AS prix,
               p.categorie AS categorie, p.stock AS stock
        ORDER BY p.categorie, p.nom
        """
        produits = neo4j_conn.execute_query(query)
        return jsonify(produits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/client/<client_id>/produits', methods=['GET'])
def get_client_produits(client_id):
    """Récupère tous les produits achetés par un client"""
    try:
        query = """
        MATCH (c:Client {id: $client_id})-[:A_EFFECTUE]->(o:Commande)-[r:CONTIENT]->(p:Produit)
        RETURN c.nom AS client_nom,
               p.id AS produit_id,
               p.nom AS produit_nom, 
               p.prix AS prix,
               p.categorie AS categorie,
               r.quantite AS quantite,
               r.prix_unitaire AS prix_unitaire,
               o.id AS commande_id,
               o.date AS date_commande
        ORDER BY o.date DESC
        """
        produits = neo4j_conn.execute_query(query, {'client_id': client_id})
        return jsonify(produits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produit/<produit_id>/clients', methods=['GET'])
def get_produit_clients(produit_id):
    """Récupère tous les clients ayant acheté un produit"""
    try:
        query = """
        MATCH (p:Produit {id: $produit_id})<-[r:CONTIENT]-(o:Commande)<-[:A_EFFECTUE]-(c:Client)
        RETURN p.nom AS produit_nom,
               c.id AS client_id,
               c.nom AS client_nom, 
               c.email AS email,
               c.ville AS ville,
               r.quantite AS quantite_achetee,
               o.date AS date_achat,
               o.total AS total_commande
        ORDER BY o.date DESC
        """
        clients = neo4j_conn.execute_query(query, {'produit_id': produit_id})
        return jsonify(clients)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggestions/<client_id>', methods=['GET'])
def get_suggestions(client_id):
    """Obtient des suggestions de produits pour un client"""
    try:
        # Méthode 1: Basée sur les achats d'autres clients similaires
        query_collaborative = """
        MATCH (client:Client {id: $client_id})-[:A_EFFECTUE]->(o1:Commande)-[:CONTIENT]->(p1:Produit)
        MATCH (p1)<-[:CONTIENT]-(o2:Commande)<-[:A_EFFECTUE]-(autres_clients:Client)
        WHERE autres_clients <> client
        MATCH (autres_clients)-[:A_EFFECTUE]->(o3:Commande)-[:CONTIENT]->(produits_suggeres:Produit)
        WHERE NOT EXISTS((client)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(produits_suggeres))
        RETURN produits_suggeres.id AS id,
               produits_suggeres.nom AS nom,
               produits_suggeres.prix AS prix,
               produits_suggeres.categorie AS categorie,
               COUNT(DISTINCT autres_clients) AS nb_clients_similaires,
               'collaborative' AS methode
        ORDER BY nb_clients_similaires DESC, produits_suggeres.prix ASC
        LIMIT 3
        """
        
        # Méthode 2: Basée sur les produits similaires
        query_similaires = """
        MATCH (client:Client {id: $client_id})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p_achetes:Produit)
        MATCH (p_achetes)-[:SIMILAIRE]->(p_similaires:Produit)
        WHERE NOT EXISTS((client)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p_similaires))
        RETURN DISTINCT p_similaires.id AS id,
               p_similaires.nom AS nom,
               p_similaires.prix AS prix,
               p_similaires.categorie AS categorie,
               COUNT(p_achetes) AS score_similarite,
               'similaire' AS methode
        ORDER BY score_similarite DESC, p_similaires.prix ASC
        LIMIT 3
        """
        
        suggestions_collaborative = neo4j_conn.execute_query(query_collaborative, {'client_id': client_id})
        suggestions_similaires = neo4j_conn.execute_query(query_similaires, {'client_id': client_id})
        
        return jsonify({
            'collaborative': suggestions_collaborative,
            'similaires': suggestions_similaires
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produit/<produit_id>/commandes', methods=['GET'])
def get_produit_commandes(produit_id):
    """Récupère toutes les commandes contenant un produit"""
    try:
        query = """
        MATCH (p:Produit {id: $produit_id})<-[r:CONTIENT]-(o:Commande)<-[:A_EFFECTUE]-(c:Client)
        RETURN o.id AS commande_id,
               o.date AS date,
               o.total AS total,
               o.statut AS statut,
               r.quantite AS quantite,
               r.prix_unitaire AS prix_unitaire,
               c.nom AS client_nom,
               c.ville AS client_ville
        ORDER BY o.date DESC
        """
        commandes = neo4j_conn.execute_query(query, {'produit_id': produit_id})
        return jsonify(commandes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-produits', methods=['GET'])
def get_top_produits():
    """Analyse: Top des produits les plus vendus"""
    try:
        query = """
        MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
        RETURN p.id AS id,
               p.nom AS nom,
               p.categorie AS categorie,
               SUM(r.quantite) AS total_vendu,
               SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires,
               COUNT(DISTINCT r) AS nb_commandes
        ORDER BY total_vendu DESC
        LIMIT 10
        """
        top_produits = neo4j_conn.execute_query(query)
        return jsonify(top_produits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/clients-actifs', methods=['GET'])
def get_clients_actifs():
    """Analyse: Clients les plus actifs"""
    try:
        query = """
        MATCH (c:Client)-[:A_EFFECTUE]->(o:Commande)
        RETURN c.id AS id,
               c.nom AS nom,
               c.email AS email,
               c.ville AS ville,
               COUNT(o) AS nb_commandes,
               SUM(o.total) AS total_depense
        ORDER BY nb_commandes DESC, total_depense DESC
        LIMIT 10
        """
        clients_actifs = neo4j_conn.execute_query(query)
        return jsonify(clients_actifs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/categories', methods=['GET'])
def get_analytics_categories():
    """Analyse: Revenus par catégorie"""
    try:
        query = """
        MATCH (p:Produit)<-[r:CONTIENT]-(:Commande)
        RETURN p.categorie AS categorie,
               COUNT(DISTINCT p) AS nb_produits_differents,
               SUM(r.quantite) AS quantite_totale,
               SUM(r.quantite * r.prix_unitaire) AS chiffre_affaires
        ORDER BY chiffre_affaires DESC
        """
        analytics = neo4j_conn.execute_query(query)
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiques générales de la base"""
    try:
        query = """
        MATCH (c:Client) WITH COUNT(c) AS nb_clients
        MATCH (o:Commande) WITH nb_clients, COUNT(o) AS nb_commandes
        MATCH (p:Produit) WITH nb_clients, nb_commandes, COUNT(p) AS nb_produits
        MATCH ()-[r:CONTIENT]->() WITH nb_clients, nb_commandes, nb_produits, COUNT(r) AS nb_achats
        RETURN nb_clients, nb_commandes, nb_produits, nb_achats
        """
        stats = neo4j_conn.execute_query(query)
        return jsonify(stats[0] if stats else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test de la connexion Neo4j"""
    try:
        query = "RETURN 'Neo4j connection OK' AS message"
        result = neo4j_conn.execute_query(query)
        return jsonify({'status': 'success', 'message': result[0]['message']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Démarrage de l'application Neo4j E-commerce")
    print(f"📡 Neo4j URI: {Config.NEO4J_URI}")
    print("🌐 Application disponible sur http://localhost:5000")
    
    try:
        app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
    finally:
        if neo4j_conn:
            neo4j_conn.close()
