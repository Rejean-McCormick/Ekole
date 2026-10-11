@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if not errorlevel 1 goto launch_py
where python >nul 2>nul
if not errorlevel 1 goto launch_python
echo Python 3 introuvable. Installer Python 3, puis recommencer.
pause
exit /b 1
:launch_py
py -3 opsconsole\ekole_ops.py
goto done
:launch_python
python opsconsole\ekole_ops.py
:done
if errorlevel 1 pause
endlocal
