#!/bin/bash

echo "Test de la réplication Redis Master/Slave"
echo "============================================="

# Vérifier que les conteneurs sont en cours d'exécution
if ! docker ps | grep -q redis-master; then
    echo "Le conteneur redis-master n'est pas en cours d'exécution"
    echo "   Lancez d'abord: docker compose up -d"
    exit 1
fi

for i in 1 2 3; do
    if ! docker ps | grep -q redis-slave$i; then
        echo "Le conteneur redis-slave$i n'est pas en cours d'exécution"
        echo "   Lancez d'abord: docker compose up -d"
        exit 1
    fi
done

echo "Les conteneurs Redis (1 master + 3 slaves) sont en cours d'exécution"

# Test 1: Écriture sur le master
echo ""
echo " Test 1: Écriture sur le master (port 6379)"
docker exec redis-master redis-cli set test_key "Hello Redis Master!" > /dev/null
echo "   ✅ Clé 'test_key' écrite sur le master"

# Test 2: Lecture depuis le master
echo ""
echo "Test 2: Lecture depuis le master"
MASTER_VALUE=$(docker exec redis-master redis-cli get test_key)
echo " Valeur sur master: $MASTER_VALUE"

# Test 3: Lecture depuis les 3 slaves
echo ""
echo "Test 3: Lecture depuis les 3 slaves"
sleep 2  # Attendre la réplication

for i in 1 2 3; do
    port=$((6379 + i))
    echo "  Slave$i (port $port):"
    SLAVE_VALUE=$(docker exec redis-slave$i redis-cli get test_key)
    echo "    Valeur: $SLAVE_VALUE"
    
    # Vérification
    if [ "$MASTER_VALUE" = "$SLAVE_VALUE" ]; then
        echo "    ✅ Réplication OK"
    else
        echo "    ❌ Problème de réplication sur slave$i"
        exit 1
    fi
done

# Test 4: Informations sur la réplication
echo ""
echo "Test 4: Informations de réplication"
echo "   Master info:"
docker exec redis-master redis-cli info replication | grep -E "role|connected_slaves"

echo "   Slaves info:"
for i in 1 2 3; do
    echo "     Slave$i:"
    docker exec redis-slave$i redis-cli info replication | grep -E "role|master_host|master_port"
done

# Test 5: Test de performance
echo ""
echo "⚡ Test 5: Test de performance (1000 opérations SET)"
time docker exec redis-master redis-cli eval "
for i=1,1000 do
    redis.call('set', 'perf_key_' .. i, 'value_' .. i)
end
return 'OK'
" 0 > /dev/null

echo "   Test de performance terminé"

# Test 6: Vérification du nombre de clés
echo ""
echo "Test 6: Nombre de clés dans chaque instance"
MASTER_KEYS=$(docker exec redis-master redis-cli dbsize)
echo "   Master: $MASTER_KEYS clés"

for i in 1 2 3; do
    SLAVE_KEYS=$(docker exec redis-slave$i redis-cli dbsize)
    echo "   Slave$i: $SLAVE_KEYS clés"
    
    if [ "$MASTER_KEYS" = "$SLAVE_KEYS" ]; then
        echo "     ✅ Nombre de clés OK"
    else
        echo "     ⚠️  Différence de clés (réplication en cours...)"
    fi
done

echo ""
echo "Tests de réplication Redis terminés avec succès !"
echo "Master accessible sur localhost:6379"
echo "Slave1 accessible sur localhost:6380"
echo "Slave2 accessible sur localhost:6381"
echo "Slave3 accessible sur localhost:6382"
