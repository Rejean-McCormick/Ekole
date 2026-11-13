@echo off
setlocal
cd /d "%~dp0"
set "KONTEXTE=C:\mycode\Ekole\Kontexte"
if defined EKOLE_KONTEXTE_ROOT set "KONTEXTE=%EKOLE_KONTEXTE_ROOT%"
set "PY=py -3"
where py >nul 2>nul || set "PY=python"
%PY% "outils\compositeur_prf22_v0_3\app\bank_enrich.py" --kontexte "%KONTEXTE%" --vers "banques\prf22\candidats-v0_6" --verifier
if errorlevel 1 (echo [ERREUR] Banque PRF-22 v0.6 non conforme. & pause & exit /b 1)
echo [OK] Banque v0.6 verifiee structurellement; qualification enseignante requise.
pause
