@echo off
setlocal
cd /d "%~dp0"
echo [EKOLE] Atelier enseignant local en edition, aucune publication PRF-22 automatique.
where py >nul 2>nul
if not errorlevel 1 (
 py -3 launcher.py --contenu none --edition --ouvrir %*
) else (
 python launcher.py --contenu none --edition --ouvrir %*
)
if errorlevel 1 pause
