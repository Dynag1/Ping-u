# Script de nettoyage forcé et rebuild
# Pour résoudre les problèmes de verrouillage

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Nettoyage forcé et Rebuild - Ping ü        " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Fermer tous les processus Ping_u
Write-Host "[1/5] Fermeture des processus Ping_u..." -ForegroundColor Yellow
$processes = Get-Process -Name "Ping_u*" -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "  Processus trouvés : $($processes.Count)" -ForegroundColor White
    $processes | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  Processus fermés" -ForegroundColor Green
} else {
    Write-Host "  Aucun processus en cours" -ForegroundColor Green
}

# Attendre que les processus se terminent
Write-Host "  Attente de fermeture complète..." -ForegroundColor White
Start-Sleep -Seconds 3

# Étape 2 : Nettoyage forcé avec cmd
Write-Host "`n[2/5] Nettoyage des dossiers..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Write-Host "  Suppression de dist..." -ForegroundColor White
    cmd /c "rd /s /q dist" 2>$null
    Start-Sleep -Seconds 1
}
if (Test-Path "build") {
    Write-Host "  Suppression de build..." -ForegroundColor White
    cmd /c "rd /s /q build" 2>$null
    Start-Sleep -Seconds 1
}
Write-Host "  Nettoyage terminé" -ForegroundColor Green

# Étape 3 : Vérification de Python 3.13
Write-Host "`n[3/5] Vérification de Python 3.13..." -ForegroundColor Yellow
py -3.13 --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Erreur : Python 3.13 non trouvé!" -ForegroundColor Red
    exit 1
}
Write-Host "  Python 3.13 trouvé" -ForegroundColor Green

# Étape 4 : Vérification des dépendances
Write-Host "`n[4/5] Vérification des dépendances Flask..." -ForegroundColor Yellow
py -3.13 -c "import flask; import flask_socketio; import flask_cors; print('✅ Flask et Socket.IO installés')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installation des dépendances..." -ForegroundColor Yellow
    py -3.13 -m pip install flask flask-socketio flask-cors --quiet
}

# Étape 5 : Compilation avec PyInstaller
Write-Host "`n[5/5] Compilation avec PyInstaller..." -ForegroundColor Yellow
Write-Host "  Ceci peut prendre 2-3 minutes..." -ForegroundColor White
py -3.13 -m PyInstaller Ping_u.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERREUR lors de la compilation!" -ForegroundColor Red
    Write-Host "Consultez les messages d'erreur ci-dessus" -ForegroundColor Yellow
    exit 1
}

# Résumé
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   BUILD TERMINÉ AVEC SUCCÈS !                 " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fichier créé : dist\Ping_u\Ping_u.exe" -ForegroundColor Green

# Vérifier le fichier
if (Test-Path "dist\Ping_u\Ping_u.exe") {
    $exe = Get-Item "dist\Ping_u\Ping_u.exe"
    $sizeMB = [math]::Round($exe.Length / 1MB, 1)
    Write-Host "Taille : $sizeMB MB" -ForegroundColor White
    Write-Host "Date : $($exe.LastWriteTime)" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ Le serveur web avec async_mode='threading' est inclus !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur : Ping_u.exe n'a pas été créé" -ForegroundColor Red
    exit 1
}

# Vérifier les templates
if (Test-Path "dist\Ping_u\_internal\src\web\templates\index.html") {
    Write-Host "✅ Templates web inclus" -ForegroundColor Green
} else {
    Write-Host "⚠️  Templates web manquants" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pour tester :" -ForegroundColor White
Write-Host "  1. cd dist\Ping_u" -ForegroundColor Cyan
Write-Host "  2. .\Ping_u.exe" -ForegroundColor Cyan
Write-Host "  3. Menu → Serveur Web → Démarrer le serveur" -ForegroundColor Cyan
Write-Host ""
Write-Host "L'erreur 'Invalid async_mode' devrait être corrigée !" -ForegroundColor Green
Write-Host ""

