@echo off
cd /d "%~dp0"
set "MOODSCOPE_PYTHON=.venv\Scripts\python.exe"
if exist ".venv-modern\.moodscope-validated" if exist ".venv-modern\Scripts\python.exe" set "MOODSCOPE_PYTHON=.venv-modern\Scripts\python.exe"
"%MOODSCOPE_PYTHON%" scripts\launch.py
if errorlevel 1 pause
