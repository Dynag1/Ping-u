#!/bin/bash
# Script de démarrage Ping ü en mode headless (Linux/Mac)

# Aller dans le répertoire du script
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "🚀 Démarrage de Ping ü en mode headless..."
echo "=========================================="
echo "📂 Répertoire: $SCRIPT_DIR"

# Définir le chemin Python du venv
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    PIP_CMD="$SCRIPT_DIR/.venv/bin/pip"
    echo "✅ Venv trouvé: .venv"
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    PIP_CMD="$SCRIPT_DIR/venv/bin/pip"
    echo "✅ Venv trouvé: venv"
else
    echo "❌ Aucun environnement virtuel trouvé !"
    echo "Créez-en un avec: python3 -m venv .venv"
    exit 1
fi

echo "🐍 Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Vérifier les modules essentiels
echo ""
echo "🔍 Vérification des modules..."

MISSING_MODULES=""

check_module() {
    if ! $PYTHON_CMD -c "import $1" 2>/dev/null; then
        echo "   ❌ $1 manquant"
        MISSING_MODULES="$MISSING_MODULES $2"
    else
        echo "   ✅ $1"
    fi
}

check_module "flask" "Flask"
check_module "flask_socketio" "Flask-SocketIO"
check_module "flask_cors" "Flask-Cors"
check_module "requests" "requests"
check_module "eventlet" "eventlet"

# Installer les modules manquants
if [ -n "$MISSING_MODULES" ]; then
    echo ""
    echo "📦 Installation des modules manquants..."
    $PIP_CMD install $MISSING_MODULES
fi

# Nettoyer le cache Python
echo ""
echo "🧹 Nettoyage du cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Vérifier si l'application est déjà en cours
if [ -f "pingu_headless.pid" ]; then
    OLD_PID=$(cat pingu_headless.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo ""
        echo "⚠️  Une instance est déjà en cours (PID: $OLD_PID)"
        echo "Utilisez ./stop_headless.sh pour l'arrêter"
        exit 1
    else
        rm -f pingu_headless.pid
    fi
fi

# Démarrer l'application
echo ""
echo "🚀 Lancement de l'application..."

# Utiliser le chemin complet du Python pour nohup
nohup "$PYTHON_CMD" "$SCRIPT_DIR/Pingu.py" --headless > "$SCRIPT_DIR/pingu_headless.log" 2>&1 &
NEW_PID=$!

# Attendre et vérifier
sleep 3

if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ Application démarrée (PID: $NEW_PID)"
    echo ""
    echo "📝 Informations:"
    echo "   - Logs: tail -f pingu_headless.log"
    echo "   - Web:  http://localhost:9090/admin"
    echo "   - Stop: ./stop_headless.sh"
    echo ""
    echo "   Identifiants par défaut: admin / a"
else
    echo "❌ L'application a échoué au démarrage !"
    echo ""
    echo "📋 Dernières lignes du log:"
    tail -30 "$SCRIPT_DIR/pingu_headless.log"
    exit 1
fi
