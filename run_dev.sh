#!/bin/bash
# Lancer Ping ü depuis l'environnement de développement

cd "$(dirname "$0")"
source .venv/bin/activate
python3 Pingu.py "$@"
