@echo off
setlocal
cd /d "%~dp0" || goto :echec

where node.exe >nul 2>&1 || goto :node_absent
where npm.cmd >nul 2>&1 || goto :node_absent

node -e "require('playwright')" >nul 2>&1
if errorlevel 1 (
    echo [Ekole] Installation de Playwright...
    call npm.cmd install --no-audit --no-fund
    if errorlevel 1 goto :echec
)

if not defined EKOLE_CHROMIUM (
    node -e "if (!require('node:fs').existsSync(require('playwright').chromium.executablePath())) process.exit(1)" >nul 2>&1
    if errorlevel 1 (
        echo [Ekole] Installation de Chromium...
        call "%~dp0node_modules\.bin\playwright.cmd" install chromium
        if errorlevel 1 goto :echec
    )
)

call npm.cmd run visite -- %*
if errorlevel 1 goto :echec
exit /b 0

:node_absent
echo [Ekole] Node.js et npm sont requis. Installe Node.js 20 ou plus recent.
goto :echec

:echec
echo [Ekole] La visite n'a pas pu demarrer. Consulte le message ci-dessus.
pause
exit /b 1
