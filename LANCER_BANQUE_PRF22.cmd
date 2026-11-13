@echo off
setlocal
cd /d "%~dp0"
set "EKOLE_PRF22_BANQUE_ROOT=%~dp0banques\prf22\candidats-v0_4"
set "PY=py -3"
where py >nul 2>&1 || set "PY=python"
%PY% "outils\compositeur_prf22_v0_3\app\EXPLORER_BANQUE.pyw"
if errorlevel 1 (
  echo [ERREUR] Explorateur PRF-22. Verifier Python 3 et Tkinter.
  pause
  exit /b 1
)
