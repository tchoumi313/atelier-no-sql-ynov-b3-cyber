#!/bin/bash

echo "Démonstration complète de l'atelier Redis"
echo "=========================================="

# Vérifier les prérequis
if ! docker ps | grep -q redis-master; then
    echo "Redis n'est pas démarré. Lancement..."
    docker compose up -d
    sleep 5
fi

echo "Redis est démarré"

# Vider le cache pour commencer proprement
echo ""
echo "Nettoyage du cache..."
docker exec redis-master redis-cli flushdb > /dev/null

# Démonstration 1: Cache Miss (requête lente)
echo ""
echo "DÉMONSTRATION 1: Cache Miss (première requête)"
echo "=============================================="
echo "Simulation d'une requête 'utilisateurs actifs'..."

START_TIME=$(date +%s.%N)
curl -s -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"utilisateurs actifs"}' | python3 -m json.tool
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

echo "Temps total: ${DURATION}s (incluant simulation 2s + traitement)"

# Pause pour l'effet
sleep 2

# Démonstration 2: Cache Hit (requête rapide)
echo ""
echo "DÉMONSTRATION 2: Cache Hit (requête depuis le cache)"
echo "===================================================="
echo "Même requête 'utilisateurs actifs' (depuis le cache)..."

START_TIME=$(date +%s.%N)
curl -s -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"utilisateurs actifs"}' | python3 -m json.tool
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

echo "Temps total: ${DURATION}s (gain de performance !)"

# Démonstration 3: Statistiques Redis
echo ""
echo "DÉMONSTRATION 3: Statistiques Redis"
echo "===================================="
curl -s http://localhost:5000/api/cache/stats | python3 -m json.tool

# Démonstration 4: Contenu du cache
echo ""
echo "DÉMONSTRATION 4: Contenu du cache"
echo "================================="
curl -s http://localhost:5000/api/cache/keys | python3 -m json.tool

# Démonstration 5: Test de réplication
echo ""
echo "DÉMONSTRATION 5: Test de réplication Master/Slave"
echo "================================================="
./scripts/test-redis.sh

# Démonstration 6: Expiration des données
echo ""
echo "DÉMONSTRATION 6: Test d'expiration (TTL)"
echo "========================================"
echo "TTL de la clé 'query:utilisateurs actifs':"
docker exec redis-master redis-cli ttl "query:utilisateurs actifs"

echo ""
echo "Attendre 10 secondes et vérifier de nouveau..."
sleep 10
echo "TTL après 10 secondes:"
docker exec redis-master redis-cli ttl "query:utilisateurs actifs"

echo ""
echo "DÉMONSTRATION TERMINÉE !"
echo "========================"
echo ""
echo "RÉSUMÉ DES FONCTIONNALITÉS DÉMONTRÉES:"
echo "- Installation et configuration Redis"
echo "- Architecture Master + 3 Slaves avec réplication"
echo "- Application web avec stratégie cache-aside"
echo "- Gain de performance visible"
echo "- Expiration automatique des données (TTL)"
echo "- Fonctionnement distribué vérifié"
echo ""
echo "Interface web: http://localhost:5000"
echo "Redis Master: localhost:6379"
echo "Redis Slave1: localhost:6380"
echo "Redis Slave2: localhost:6381"
echo "Redis Slave3: localhost:6382"
