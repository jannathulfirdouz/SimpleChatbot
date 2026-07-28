@echo off
REM =============================================================================
REM SimpleChatbot - CLI Runner (Windows)
REM =============================================================================
REM This script activates the virtual environment, installs dependencies,
REM and launches the CLI chatbot interface for testing.
REM =============================================================================

echo =============================================
echo   SimpleChatbot - CLI Interface
echo   Build the Builder Workshop
echo =============================================
echo.

REM Navigate to the project root directory
cd /d "%~dp0\.."

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: python is not installed or not in PATH.
    echo Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade the package in editable mode
echo Installing dependencies...
pip install -e . --quiet
echo Dependencies installed.
echo.

REM Run the CLI chatbot
echo Starting SimpleChatbot CLI...
echo.
python -m simplechatbot.cli

REM Keep the window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
