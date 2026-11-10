@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python tools\raccorder_parcours_roles.py %*
) else (
    py -3 tools\raccorder_parcours_roles.py %*
)
if errorlevel 1 (
    pause
    exit /b 1
)
