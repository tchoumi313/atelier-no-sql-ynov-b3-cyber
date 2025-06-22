#!/bin/bash

echo "🚀 Installation de l'atelier Redis"
echo "=================================="

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    echo "   sudo apt update && sudo apt install docker.io docker-compose"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    echo "   sudo apt update && sudo apt install docker-compose"
    exit 1
fi

echo "✅ Docker et Docker Compose sont installés"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python 3 est installé"

# Créer l'environnement virtuel Python
echo "🔧 Création de l'environnement virtuel Python..."
cd app
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activer l'environnement virtuel et installer les dépendances
echo "📦 Installation des dépendances Python..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Installation terminée !"
echo ""
echo "🔧 Pour démarrer l'atelier :"
echo "   1. docker compose up -d"
echo "   2. cd app && source venv/bin/activate && python app.py"
echo "   3. Ouvrir http://localhost:5000"
echo ""
echo "🧪 Pour tester la réplication Redis :"
echo "   ./scripts/test-redis.sh"
