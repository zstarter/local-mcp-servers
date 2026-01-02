@echo off
setlocal enabledelayedexpansion

echo 🔧 Installing Local MCP Servers for Windows...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.6 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Using Python:
python --version

echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Running configuration...
echo.
echo    Note: All credential fields are required and cannot be left empty.
echo    Required: Jira username, API token, project key, Sumo Access ID, Access Key, and index
echo    You'll be prompted again if any field is skipped.
echo.
python install.py
if errorlevel 1 (
    echo Error: Configuration failed
    pause
    exit /b 1
)

echo.
echo Installation complete! Please restart Kiro to load the new MCP servers.
pause
