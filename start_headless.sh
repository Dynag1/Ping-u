#!/bin/bash
# Script de démarrage Ping ü en mode headless (Linux/Mac)

echo "🚀 Démarrage de Ping ü en mode headless..."
echo "=========================================="

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si l'application est déjà en cours
if [ -f "pingu_headless.pid" ]; then
    echo "⚠️  Une instance est déjà en cours d'exécution"
    echo "Pour l'arrêter: ./stop_headless.sh"
    exit 1
fi

# Démarrer l'application en arrière-plan
nohup python3 Pingu.py -start > pingu_headless.log 2>&1 &

echo "✅ Application démarrée"
echo ""
echo "📝 Informations:"
echo "   - Logs: tail -f pingu_headless.log"
echo "   - Web:  http://localhost:5000/admin"
echo "   - Stop: ./stop_headless.sh"
echo ""
echo "   Identifiants par défaut: admin / a"

