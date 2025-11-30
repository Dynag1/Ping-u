#!/bin/bash
# Script de démarrage Ping ü en mode headless (Linux/Mac)

echo "🚀 Démarrage de Ping ü en mode headless..."
echo "=========================================="

# Déterminer quel python utiliser
PYTHON_CMD="python3"
if [ -f ".venv/bin/python3" ]; then
    PYTHON_CMD=".venv/bin/python3"
    echo "✅ Utilisation de l'environnement virtuel (.venv)"
fi

# Vérifier si Python est installé
if ! $PYTHON_CMD --version &> /dev/null; then
    echo "❌ Python n'est pas trouvé ($PYTHON_CMD)"
    exit 1
fi

# Vérifier si l'application est déjà en cours
if [ -f "pingu_headless.pid" ]; then
    echo "⚠️  Une instance semble déjà en cours d'exécution (fichier PID présent)"
    echo "Si ce n'est pas le cas, supprimez pingu_headless.pid"
    # On continue quand même, l'app gérera
fi

# Démarrer l'application en arrière-plan
nohup $PYTHON_CMD Pingu.py -start > pingu_headless.log 2>&1 &

echo "✅ Application démarrée"
echo ""
echo "📝 Informations:"
echo "   - Logs: tail -f pingu_headless.log"
echo "   - Web:  http://localhost:6666/admin"
echo "   - Stop: ./stop_headless.sh"
echo ""
echo "   Identifiants par défaut: admin / a"
