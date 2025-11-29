#!/bin/bash
# Script d'arrêt Ping ü en mode headless (Linux/Mac)

echo "🛑 Arrêt de Ping ü..."
echo "===================="

# Déterminer quel python utiliser
PYTHON_CMD="python3"
if [ -f ".venv/bin/python3" ]; then
    PYTHON_CMD=".venv/bin/python3"
fi

# Arrêter l'application
$PYTHON_CMD Pingu.py -stop

echo ""
echo "✅ Terminé"
