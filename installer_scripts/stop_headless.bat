@echo off
cd /d "%~dp0"
echo ========================================
echo   Ping u - Arret Mode Headless
echo ========================================
echo.
echo Arret de l'application...
"Ping_u.exe" -stop

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] L'arret a echoue (code: %ERRORLEVEL%)
    echo Essayez de fermer le processus manuellement.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [OK] Application arretee
pause

