#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "  Ping u - Mode Headless"
echo "========================================"
echo
echo "Demarrage de l'application en mode headless..."
./Ping_u -start &

echo
echo "[OK] Application demarree en arriere-plan (PID: $!)"
echo "    Interface web: http://localhost:9090/admin"
echo "    Identifiants: admin / a"
echo
echo "Pour arreter: ./stop_headless.sh"

