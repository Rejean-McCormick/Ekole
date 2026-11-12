@echo off
setlocal
cd /d "%~dp0"
py -3 "outils\compositeur_prf22_v0_3\app\Atelier_PRF22.pyw"
if errorlevel 1 (
  echo [ECHEC] Atelier PRF-22. Verifier que Python 3 et Tkinter sont installes.
  pause
  exit /b 1
)
