@echo off
cd /d "%~dp0.."
py -3 tools\ekole.py verify
if errorlevel 1 exit /b 1
py -3 tools\ekole.py build
if errorlevel 1 exit /b 1
py -3 tools\ekole.py preview
