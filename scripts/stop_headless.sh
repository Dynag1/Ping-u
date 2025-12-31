#!/bin/bash
# Script d'arrêt Ping ü en mode headless (Linux/Mac)
 
# Se placer à la racine du projet (parent du dossier scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

echo "🛑 Arrêt de Ping ü..."
echo "===================="

# Vérifier et utiliser l'environnement virtuel
if [ -d ".venv" ] && [ -f ".venv/bin/python" ]; then
    source .venv/bin/activate
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
elif [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    source venv/bin/activate
    PYTHON_CMD="$PROJECT_ROOT/venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Méthode 1: Via le fichier PID
if [ -f "pingu_headless.pid" ]; then
    PID=$(cat pingu_headless.pid)
    echo "📍 PID trouvé: $PID"
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔄 Arrêt du processus..."
        kill $PID 2>/dev/null
        
        # Attendre l'arrêt
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Forcer si nécessaire
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Arrêt forcé..."
            kill -9 $PID 2>/dev/null
        fi
    else
        echo "⚠️  Processus déjà arrêté"
    fi
    
    rm -f pingu_headless.pid
fi

# Méthode 3: Via le port 9090
PORT=9090
echo "🔍 Vérification du port $PORT..."
if command -v lsof >/dev/null 2>&1; then
    PORT_PIDS=$(lsof -t -i :$PORT 2>/dev/null)
    if [ -n "$PORT_PIDS" ]; then
        echo "🔄 Arrêt des processus utilisant le port $PORT: $PORT_PIDS"
        kill $PORT_PIDS 2>/dev/null
        sleep 2
        kill -9 $PORT_PIDS 2>/dev/null
    fi
elif command -v fuser >/dev/null 2>&1; then
    echo "🔄 Arrêt des processus utilisant le port $PORT via fuser"
    fuser -k $PORT/tcp 2>/dev/null
fi

# Méthode 4: Tuer tous les processus Pingu.py
PIDS=$(pgrep -f "Pingu.py" 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "🔄 Arrêt des processus restants: $PIDS"
    pkill -f "Pingu.py" 2>/dev/null
    sleep 1
    pkill -9 -f "Pingu.py" 2>/dev/null
fi

# Nettoyer
rm -f pingu_headless.pid

echo ""
echo "✅ Terminé"
