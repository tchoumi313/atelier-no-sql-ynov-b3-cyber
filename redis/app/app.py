#!/usr/bin/env python3
"""
Application web démonstrant l'utilisation de Redis comme cache
Atelier Redis - Stratégie Cache-Aside
"""

import json
import os
import time
from datetime import datetime

import redis
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Configuration Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_SLAVE_PORTS = [6380, 6381, 6382]  # 3 slaves
CACHE_TTL = 60  # 60 secondes

# Connexions Redis
try:
    redis_master = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_slaves = []
    for port in REDIS_SLAVE_PORTS:
        slave = redis.Redis(host=REDIS_HOST, port=port, decode_responses=True)
        redis_slaves.append(slave)
    print("Connexion Redis établie")
except Exception as e:
    print(f"Erreur connexion Redis: {e}")
    redis_master = None
    redis_slaves = []

# Simulation de base de données lente
def simulate_slow_database(query):
    """Simule une réponse lente de base de données"""
    print(f"Simulation base de données lente pour: {query}")
    time.sleep(2)  # Simulation de 2 secondes
    
    # Données fictives basées sur la requête
    data = {
        'query': query,
        'result': f"Résultat pour '{query}'",
        'timestamp': datetime.now().isoformat(),
        'source': 'database',
        'processing_time': '2.0s'
    }
    return data

def get_from_cache(key):
    """Récupère une donnée du cache Redis"""
    try:
        if redis_master is None:
            return None
        
        data = redis_master.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Erreur lecture cache: {e}")
        return None

def set_to_cache(key, data, ttl=CACHE_TTL):
    """Enregistre une donnée dans le cache Redis"""
    try:
        if redis_master is None:
            return False
        
        redis_master.setex(key, ttl, json.dumps(data))
        return True
    except Exception as e:
        print(f"Erreur écriture cache: {e}")
        return False

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    """Endpoint principal - implémente la stratégie cache-aside"""
    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Requête vide'}), 400
    
    cache_key = f"query:{query}"
    start_time = time.time()
    
    # 1. Chercher d'abord dans le cache
    print(f"Recherche dans le cache: {cache_key}")
    cached_data = get_from_cache(cache_key)
    
    if cached_data:
        # Données trouvées dans le cache
        response_time = time.time() - start_time
        cached_data['source'] = 'cache'
        cached_data['response_time'] = f"{response_time:.3f}s"
        cached_data['cache_hit'] = True
        print(f"Cache HIT - Réponse en {response_time:.3f}s")
        return jsonify(cached_data)
    
    # 2. Si pas dans le cache, consulter la "base de données"
    print(f"Cache MISS - Consultation base de données")
    data = simulate_slow_database(query)
    response_time = time.time() - start_time
    data['response_time'] = f"{response_time:.3f}s"
    data['cache_hit'] = False
    
    # 3. Enregistrer le résultat dans le cache
    if set_to_cache(cache_key, data):
        print(f"Données enregistrées dans le cache avec TTL {CACHE_TTL}s")
    
    return jsonify(data)

@app.route('/api/cache/stats')
def cache_stats():
    """Statistiques du cache Redis"""
    try:
        if redis_master is None:
            return jsonify({'error': 'Redis non disponible'}), 500
        
        # Informations sur le master
        master_info = redis_master.info()
        
        # Informations sur les slaves
        slaves_info = []
        for i, slave in enumerate(redis_slaves):
            try:
                slave_info = slave.info()
                slaves_info.append({
                    'id': f'slave{i+1}',
                    'port': REDIS_SLAVE_PORTS[i],
                    'connected': True,
                    'keys': slave.dbsize(),
                    'memory_used': slave_info.get('used_memory_human', 'N/A'),
                    'role': slave_info.get('role', 'unknown')
                })
            except Exception as e:
                slaves_info.append({
                    'id': f'slave{i+1}',
                    'port': REDIS_SLAVE_PORTS[i],
                    'connected': False,
                    'keys': 0,
                    'memory_used': 'N/A',
                    'role': 'disconnected',
                    'error': str(e)
                })
        
        stats = {
            'master': {
                'connected': True,
                'keys': redis_master.dbsize(),
                'memory_used': master_info.get('used_memory_human', 'N/A'),
                'uptime': master_info.get('uptime_in_seconds', 0),
                'role': master_info.get('role', 'unknown')
            },
            'slaves': slaves_info
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear')
def clear_cache():
    """Vide le cache Redis"""
    try:
        if redis_master is None:
            return jsonify({'error': 'Redis non disponible'}), 500
        
        redis_master.flushdb()
        return jsonify({'message': 'Cache vidé avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/keys')
def list_cache_keys():
    """Liste les clés dans le cache"""
    try:
        if redis_master is None:
            return jsonify({'error': 'Redis non disponible'}), 500
        
        keys = redis_master.keys('query:*')
        cache_contents = {}
        
        for key in keys:
            ttl = redis_master.ttl(key)
            data = redis_master.get(key)
            cache_contents[key] = {
                'ttl': ttl,
                'data': json.loads(data) if data else None
            }
        
        return jsonify(cache_contents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Démarrage de l'application Redis Cache Demo")
    print(f"Redis Master: {REDIS_HOST}:{REDIS_PORT}")
    for i, port in enumerate(REDIS_SLAVE_PORTS):
        print(f"Redis Slave{i+1}: {REDIS_HOST}:{port}")
    print(f"TTL du cache: {CACHE_TTL} secondes")
    print("Application disponible sur http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
