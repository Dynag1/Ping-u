# Script de build automatique pour Ping u avec Python 3.13
# Inclut l'installation des dependances

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Build Ping u - Python 3.13 + Inno Setup    " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Etape 1 : Verification de Python 3.13
Write-Host "`n[1/6] Verification de Python 3.13..." -ForegroundColor Yellow
py -3.13 --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur : Python 3.13 non trouve!" -ForegroundColor Red
    Write-Host "Telechargez-le : https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Python 3.13 trouve" -ForegroundColor Green

# Etape 2 : Installation/Mise a jour des dependances
Write-Host "`n[2/6] Installation des dependances..." -ForegroundColor Yellow
py -3.13 -m pip install --upgrade pip
py -3.13 -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de l'installation des dependances!" -ForegroundColor Red
    exit 1
}
Write-Host "Dependances installees" -ForegroundColor Green

# Etape 3 : Nettoyage des anciens builds
Write-Host "`n[3/6] Nettoyage des anciens builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Write-Host "Nettoyage termine" -ForegroundColor Green

# Etape 4 : Compilation avec PyInstaller (Python 3.13)
Write-Host "`n[4/6] Compilation avec PyInstaller..." -ForegroundColor Yellow
py -3.13 -m PyInstaller Ping_u.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de la compilation PyInstaller!" -ForegroundColor Red
    exit 1
}
Write-Host "Compilation PyInstaller reussie" -ForegroundColor Green

# Etape 5 : Creation de l'installateur avec Inno Setup
Write-Host "`n[5/6] Creation de l'installateur..." -ForegroundColor Yellow
$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    Write-Host "Inno Setup non trouve !" -ForegroundColor Yellow
    Write-Host "Cherchez ISCC.exe dans:" -ForegroundColor White
    Write-Host "  - C:\Program Files\Inno Setup 6\ISCC.exe" -ForegroundColor White
    Write-Host "  - C:\Program Files (x86)\Inno Setup 6\ISCC.exe" -ForegroundColor White
    
    # Tentative alternative
    $innoSetupPath = "C:\Program Files\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $innoSetupPath)) {
        Write-Host "Inno Setup introuvable - Installation manuelle requise" -ForegroundColor Red
        Write-Host "Telechargez : https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        Write-Host "`nL'exe est cree dans dist\ mais pas d'installateur" -ForegroundColor Yellow
        exit 1
    }
}

& $innoSetupPath "setup.iss"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de la creation de l'installateur!" -ForegroundColor Red
    exit 1
}
Write-Host "Installateur cree" -ForegroundColor Green

# Etape 6 : Resume
Write-Host "`n[6/6] Resume du build" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Build termine avec succes !" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fichiers generes :" -ForegroundColor White
Write-Host "  - Executable : dist\Pingu.exe" -ForegroundColor Green
Write-Host "  - Installateur : Output\Ping_u_Setup.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes :" -ForegroundColor White
Write-Host "  1. Testez l executable dans le dossier dist" -ForegroundColor Cyan
Write-Host "  2. Installez avec le fichier dans Output" -ForegroundColor Cyan
Write-Host ""
