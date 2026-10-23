@echo off
cd /d "%~dp0"
python CampusBot.py --console
if errorlevel 1 py CampusBot.py --console
pause
