#!/bin/bash
# Script de nettoyage pour Raspberry Pi
# Force l'arrêt de tous les processus Ping ü

echo "🧹 Nettoyage des processus Ping ü..."

# 1. Supprimer le fichier PID s'il existe
if [ -f "pingu_headless.pid" ]; then
    echo "Suppression du fichier PID..."
    rm -f pingu_headless.pid
fi

if [ -f "pingu_headless.stop" ]; then
    echo "Suppression du fichier stop..."
    rm -f pingu_headless.stop
fi

# 2. Tuer les processus Python exécutant Pingu.py
echo "Arrêt des processus Python..."
pkill -f "Pingu.py" 2>/dev/null
sleep 2

# 3. Vérifier s'il reste des processus
if pgrep -f "Pingu.py" > /dev/null; then
    echo "⚠️  Processus résistants détectés, force kill..."
    pkill -9 -f "Pingu.py" 2>/dev/null
    sleep 1
fi

# 4. Libérer le port 9090 si nécessaire
PORT_PID=$(lsof -ti:9090 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "Libération du port 9090 (PID: $PORT_PID)..."
    kill -9 $PORT_PID 2>/dev/null
fi

# 5. Vérification finale
sleep 1
if pgrep -f "Pingu.py" > /dev/null; then
    echo "❌ Erreur : Des processus sont toujours actifs"
    ps aux | grep Pingu.py | grep -v grep
    exit 1
else
    echo "✅ Nettoyage terminé avec succès"
    echo ""
    echo "Vous pouvez maintenant relancer l'application:"
    echo "  python Pingu.py -start"
    exit 0
fi

