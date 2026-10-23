@echo off
cd /d "%~dp0"
python CampusBot.py
if errorlevel 1 py CampusBot.py
if errorlevel 1 pause
