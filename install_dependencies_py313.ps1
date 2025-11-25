# Guide d'installation des dépendances pour Python 3.13
# Exécutez ces commandes dans l'ordre

Write-Host "=== Installation des dépendances Ping ü pour Python 3.13 ===" -ForegroundColor Cyan

# 1. Vérification de Python 3.13
Write-Host "`n[1/4] Vérification de Python 3.13..." -ForegroundColor Yellow
py -3.13 --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python 3.13 n'est pas installé!" -ForegroundColor Red
    Write-Host "Téléchargez-le : https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Python 3.13 trouvé" -ForegroundColor Green

# 2. Mise à jour de pip
Write-Host "`n[2/4] Mise à jour de pip..." -ForegroundColor Yellow
py -3.13 -m pip install --upgrade pip
Write-Host "✅ Pip à jour" -ForegroundColor Green

# 3. Installation des dépendances
Write-Host "`n[3/4] Installation des dépendances..." -ForegroundColor Yellow
py -3.13 -m pip install -r requirements.txt
Write-Host "✅ Dépendances installées" -ForegroundColor Green

# 4. Vérification des modules critiques
Write-Host "`n[4/4] Vérification des modules critiques..." -ForegroundColor Yellow

$modules = @(
    "PySide6",
    "pysnmp",
    "pythonping",
    "openpyxl",
    "pyinstaller"
)

foreach ($module in $modules) {
    py -3.13 -c "import $module; print('✅ $module OK')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ $module ERREUR" -ForegroundColor Red
    }
}

Write-Host "`n=== Installation terminée ! ===" -ForegroundColor Green
Write-Host "`nVous pouvez maintenant :" -ForegroundColor Cyan
Write-Host "  1. Lancer l'application : py -3.13 Pingu.py" -ForegroundColor White
Write-Host "  2. Compiler l'exe : .\build-py313.ps1" -ForegroundColor White
