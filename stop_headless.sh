#!/bin/bash
# Script d'arrêt Ping ü en mode headless (Linux/Mac)

echo "🛑 Arrêt de Ping ü..."
echo "===================="

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Arrêter l'application
python3 Pingu.py -stop

echo ""
echo "✅ Terminé"

