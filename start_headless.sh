#!/bin/bash
# Script de démarrage Ping ü en mode headless (Linux/Mac)
 
# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Démarrage de Ping ü en mode headless..."
echo "=========================================="
echo "📂 Répertoire: $SCRIPT_DIR"

# Nettoyer le cache Python (peut causer des problèmes)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Vérifier et utiliser l'environnement virtuel
if [ -d ".venv" ] && [ -f ".venv/bin/python" ]; then
    source .venv/bin/activate
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    echo "✅ Environnement virtuel activé (.venv)"
elif [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    source venv/bin/activate
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    echo "✅ Environnement virtuel activé (venv)"
else
    PYTHON_CMD="python3"
    echo "⚠️  Pas d'environnement virtuel trouvé, utilisation de python3 système"
fi

# Vérifier Python
echo "🐍 Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Vérifier cryptography
echo "🔐 Vérification cryptography..."
if ! $PYTHON_CMD -c "from cryptography.hazmat.primitives.ciphers import Cipher" 2>/dev/null; then
    echo "❌ Module cryptography non trouvé ! Installation..."
    $PYTHON_CMD -m pip install cryptography
fi

# Vérifier si l'application est déjà en cours
if [ -f "pingu_headless.pid" ]; then
    OLD_PID=$(cat pingu_headless.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "⚠️  Une instance est déjà en cours (PID: $OLD_PID)"
        echo "Utilisez ./stop_headless.sh pour l'arrêter"
        exit 1
    else
        echo "🧹 Nettoyage ancien fichier PID..."
        rm -f pingu_headless.pid
    fi
fi

# Démarrer l'application en arrière-plan
echo "🚀 Lancement de l'application..."
nohup $PYTHON_CMD Pingu.py --headless > pingu_headless.log 2>&1 &
NEW_PID=$!

# Attendre un peu et vérifier que ça démarre
sleep 2

if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ Application démarrée (PID: $NEW_PID)"
else
    echo "❌ L'application a échoué au démarrage !"
    echo "Consultez les logs: tail -20 pingu_headless.log"
    tail -20 pingu_headless.log
    exit 1
fi

echo ""
echo "📝 Informations:"
echo "   - Logs: tail -f pingu_headless.log"
echo "   - Web:  http://localhost:9090/admin"
echo "   - Stop: ./stop_headless.sh"
echo ""
echo "   Identifiants par défaut: admin / a"
