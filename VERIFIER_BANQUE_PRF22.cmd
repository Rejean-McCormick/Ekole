@echo off
setlocal
cd /d "%~dp0"
set "PY=py -3"
where py >nul 2>&1 || set "PY=python"
%PY% "outils\compositeur_prf22_v0_3\app\prf22_repo_check.py" --banque "banques\prf22\candidats-v0_4"
if errorlevel 1 (
  echo [ERREUR] Controle de la banque versionnee.
  pause
  exit /b 1
)
%PY% -m unittest discover -s "outils\compositeur_prf22_v0_3\tests" -p "test_*.py" -v
if errorlevel 1 (
  echo [ERREUR] Tests des propositions.
  pause
  exit /b 1
)
echo [OK] Banque candidate verifiee (non qualifiee pedagogiquement).
pause
