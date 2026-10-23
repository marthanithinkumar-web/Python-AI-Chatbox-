@echo off
cd /d "%~dp0"
python -m unittest -v
if errorlevel 1 py -m unittest -v
pause
