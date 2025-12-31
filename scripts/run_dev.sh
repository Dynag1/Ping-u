#!/bin/bash
# Lancer Ping ü depuis l'environnement de développement

# Se placer à la racine du projet (parent du dossier scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

source .venv/bin/activate
python3 Pingu.py "$@"
