@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher py.exe introuvable. Installer Python 3.
  pause
  exit /b 1
)
echo [Ekole] Synchronisation des 202 références pour Ekole Élève...
py -3 tools\synchroniser_ekole_apps.py --root "%CD%"
if errorlevel 1 (
  echo Impossible de synchroniser Ekole. Verifiez les propositions et les fichiers source.
  pause
  exit /b 1
)
echo [Ekole] Validation et compilation des outils interactifs v14...
py -3 tools\compiler_activites_v14.py --root "%CD%"
if errorlevel 1 (
 echo Compilation des associations v14 echouee. Corriger les references avant de lancer Ekole.
 pause
 exit /b 1
)
echo [Ekole] Demarrage du portail Core + Eleve (port 8765)...
start "Ekole Core et Eleve" cmd /k "py -3 tools\ekole.py preview"
echo [Ekole] Demarrage de l'application Enseignant (port 8766, session locale)...
start "Ekole Enseignant" cmd /k "py -3 tools\serve_enseignant.py --open"
timeout /t 2 >nul
start "" "http://127.0.0.1:8765/"
exit /b 0
