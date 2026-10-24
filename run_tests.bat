@echo off
cd /d "%~dp0"
python -m py_compile CampusBot.py server.py tests\test_campusbot.py
if errorlevel 1 py -m py_compile CampusBot.py server.py tests\test_campusbot.py
if errorlevel 1 pause
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -v
if errorlevel 1 py -m unittest discover -s tests -v
pause
