# Script de réinstallation de l'environnement virtuel
# Ce script nettoie et recr

ée l'environnement virtuel avec les bonnes versions

Write-Host "=== Nettoyage et recréation de l'environnement virtuel ===" -ForegroundColor Cyan

# 1. Suppression de l'ancien environnement virtuel
Write-Host "`n[1/4] Suppression de l'ancien .venv..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "✅ Ancien .venv supprimé" -ForegroundColor Green
}

# 2. Création d'un nouveau .venv avec Python 3.12
Write-Host "`n[2/4] Création d'un nouveau .venv..." -ForegroundColor Yellow
python -m venv .venv
Write-Host "✅ Nouveau .venv créé" -ForegroundColor Green

# 3. Mise à jour de pip
Write-Host "`n[3/4] Mise à jour de pip..." -ForegroundColor Yellow
.venv\Scripts\python.exe -m pip install --upgrade pip
Write-Host "✅ Pip mis à jour" -ForegroundColor Green

# 4. Installation des dépendances
Write-Host "`n[4/4] Installation des dépendances..." -ForegroundColor Yellow
.venv\Scripts\pip install -r requirements.txt
Write-Host "✅ Dépendances installées" -ForegroundColor Green

# 5. Vérification
Write-Host "`n=== Vérification ===" -ForegroundColor Cyan
.venv\Scripts\python.exe -c "import pysnmp; print(f'✅ pysnmp version: {pysnmp.__version__}')"
.venv\Scripts\python.exe -c "from pysnmp.hlapi import getCmd; print('✅ Import getCmd OK')"

Write-Host "`n=== Environnement virtuel prêt! ===" -ForegroundColor Green
