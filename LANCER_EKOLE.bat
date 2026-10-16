@echo off
setlocal
cd /d "%~dp0"
echo [EKOLE] Choisir le lanceur dans ekole-quebec ou ecole-pastorale.
echo [EKOLE] Demarrage du moteur sans contenu.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 launcher.py --contenu none --ouvrir %*
) else (
  python launcher.py --contenu none --ouvrir %*
)
if errorlevel 1 pause
