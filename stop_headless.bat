@echo off
REM Script pour arrêter Ping ü en mode headless (Windows)

echo.
echo ========================================
echo   Ping ü - Arret Mode Headless
echo ========================================
echo.

REM Vérifier l'environnement virtuel
if not exist .venv\Scripts\python.exe (
    echo [ERREUR] Environnement virtuel non trouve
    pause
    exit /b 1
)

REM Arrêter l'application
.venv\Scripts\python.exe Pingu.py -stop

pause
