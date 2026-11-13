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
where py >nul 2>nul || set "PY=python"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "ESTAMP=%%i"
if not defined ESTAMP set "ESTAMP=local"
set "OUTPUT=%~dp0banques\prf22\generations\%ESTAMP%-enrichi"
echo [INFO] Generation d'une nouvelle banque candidate PRF-22 v0.6 ; les anciennes sont conservees.
%PY% "outils\compositeur_prf22_v0_3\app\bank_enrich.py" --kontexte "%KONTEXTE%" --vers "%OUTPUT%"
if errorlevel 1 (echo [ERREUR] Generation interrompue. & pause & exit /b 1)
%PY% "outils\compositeur_prf22_v0_3\app\bank_enrich.py" --kontexte "%KONTEXTE%" --vers "%OUTPUT%" --verifier
if errorlevel 1 (echo [ERREUR] Verification echouee. & pause & exit /b 1)
echo [OK] Banque candidate conservee sous %OUTPUT%
echo [INFO] Pour consulter la banque versionnee, ouvrir l'espace enseignant : /prf22/index.html
pause
