@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul 2>&1

rem Ekole - Lanceur local Windows.
rem Deposer ce fichier a la RACINE du projet, a cote des dossiers site et tools.
cd /d "%~dp0"

if not exist "tools\ekole.py" goto MISSING_PROJECT
if not exist "site\index.html" goto MISSING_PROJECT

set "EK_PY=py -3"
py -3 --version >nul 2>&1
if not errorlevel 1 goto PY_READY

set "EK_PY=python"
python --version >nul 2>&1
if not errorlevel 1 goto PY_READY

echo.
echo [ERREUR] Python 3 est introuvable.
echo Installer Python 3 avec le lanceur py, puis relancer ce fichier.
goto ERROR

:PY_READY
if /i "%~1"=="--serve" goto SERVER

echo.
echo ===============================================
echo                EKOLE - ACCUEIL
 echo ===============================================
echo Racine : "%CD%"
echo Adresse : http://127.0.0.1:8765/
echo.

rem Ne pas regenerer les fichiers de l'utilisateur si l'index existe deja.
if not exist "site\data\index.json" (
    echo [INFO] Index absent : construction locale necessaire.
    %EK_PY% "tools\ekole.py" build
    if errorlevel 1 goto BUILD_ERROR
)

rem Eviter de lancer plusieurs serveurs sur le port 8765.
%EK_PY% -c "import socket,sys; s=socket.socket(); rc=s.connect_ex(('127.0.0.1',8765)); s.close(); sys.exit(1 if rc==0 else 0)" >nul 2>&1
if errorlevel 1 goto PORT_IN_USE

start "Ekole - Serveur local" "%ComSpec%" /k ""%~f0" --serve"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"
echo [OK] Le site a ete lance dans une nouvelle fenetre.
echo Pour l'arreter : fermer la fenetre "Ekole - Serveur local".
exit /b 0

:SERVER
 echo [EKOLE] Serveur web local sur http://127.0.0.1:8765/
 echo [EKOLE] Arret : Ctrl+C ou fermer cette fenetre.
 %EK_PY% "tools\ekole.py" preview
 if errorlevel 1 (
     echo.
     echo [ERREUR] Le serveur Ekole n'a pas demarre.
     echo Verifier le message ci-dessus et le port 8765.
 )
 exit /b %errorlevel%

:PORT_IN_USE
echo [ATTENTION] Le port 8765 est deja occupe.
echo Un serveur Ekole est peut-etre deja en cours d'execution.
echo Adresse a verifier : http://127.0.0.1:8765/
echo Aucun deuxieme serveur n'a ete demarre.
pause
exit /b 1

:MISSING_PROJECT
echo.
echo [ERREUR] Racine Ekole introuvable.
echo Placer LANCER_EKOLE.bat dans le dossier qui contient :
echo   tools\ekole.py
echo   site\index.html
goto ERROR

:BUILD_ERROR
echo.
echo [ERREUR] La construction des donnees du site a echoue.
:ERROR
pause
exit /b 1
