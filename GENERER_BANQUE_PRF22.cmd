@echo off
setlocal
cd /d "%~dp0"
set "KONTEXTE=C:\mycode\Ekole\Kontexte"
if defined EKOLE_KONTEXTE_ROOT set "KONTEXTE=%EKOLE_KONTEXTE_ROOT%"
if not exist "%KONTEXTE%\data\catalogue\202_kristals.json" (
  echo [ERREUR] Kontexte introuvable : "%KONTEXTE%"
  pause
  exit /b 2
)
set "PY=py -3"
where py >nul 2>&1 || set "PY=python"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "ESTAMP=%%i"
if not defined ESTAMP set "ESTAMP=local"
set "OUTPUT=%~dp0banques\prf22\generations\%ESTAMP%"
echo [INFO] Generation candidate PRF-22 depuis Kontexte, sans modifications des sources.
%PY% "outils\compositeur_prf22_v0_3\app\bank_mass.py" --kontexte "%KONTEXTE%" --vers "%OUTPUT%"
if errorlevel 1 (
  echo [ERREUR] Generation interrompue. Aucun ancien dossier ecrase.
  pause
  exit /b 1
)
%PY% "outils\compositeur_prf22_v0_3\app\bank_mass.py" --kontexte "%KONTEXTE%" --vers "%OUTPUT%" --verifier
if errorlevel 1 (
  echo [ERREUR] Verification de la source echouee.
  pause
  exit /b 1
)
set "EKOLE_PRF22_BANQUE_ROOT=%OUTPUT%"
%PY% "outils\compositeur_prf22_v0_3\app\EXPLORER_BANQUE.pyw"
