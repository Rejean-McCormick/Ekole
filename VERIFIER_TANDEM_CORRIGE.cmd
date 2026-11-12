@echo off
setlocal
cd /d "%~dp0"
py -3 tools\verifier_tandem_corrige.py
set "CODE=%ERRORLEVEL%"
if "%CODE%"=="0" (
  echo [OK] Verification coordonnee terminee.
) else (
  echo [ATTENTION] Code de sortie %CODE%; lire le bilan plus haut.
)
pause
exit /b %CODE%
