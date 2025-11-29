@echo off
cd /d "%~dp0"
echo ========================================
echo   Ping u - Mode Headless
echo ========================================
echo.
echo Demarrage de l'application en mode headless...
start "" "Ping_u.exe" -start

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Le demarrage a echoue (code: %ERRORLEVEL%)
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

