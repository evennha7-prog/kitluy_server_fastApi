@echo off
title KITLUY FastAPI Server

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment (.venv)...
    ".venv\Scripts\python.exe" run.py
) else (
    echo [INFO] Using system python...
    python run.py
)

pause
