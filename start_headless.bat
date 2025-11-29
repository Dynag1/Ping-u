@echo off
REM Script pour démarrer Ping ü en mode headless (Windows)

echo.
echo ========================================
echo   Ping ü - Mode Headless (Windows)
echo ========================================
echo.

REM Vérifier l'environnement virtuel
if not exist .venv\Scripts\python.exe (
    echo [ERREUR] Environnement virtuel non trouve
    echo Creez-le avec: python -m venv .venv
    echo Puis installez les dependances: .venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Environnement virtuel trouve

REM Démarrer l'application en mode headless (arrière-plan avec pythonw)
echo.
echo Demarrage de l'application en mode headless...
.venv\Scripts\pythonw.exe Pingu.py -start

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Le demarrage a echoue (code: %ERRORLEVEL%^)
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [OK] Application demarree en arriere-plan
echo     Interface web: http://localhost:5000/admin
echo     Identifiants: admin / a
echo.
echo Pour arreter: stop_headless.bat
pause
