@echo off
chcp 65001 >nul
setlocal

REM Set working directory
cd /d "%~dp0"

REM Check Python environment
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please make sure Python is installed and added to system PATH.
    pause
    exit /b 1
)

REM Check Poetry installation
poetry --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Poetry not found. Please install Poetry first.
    echo Follow installation instructions: https://python-poetry.org/docs/#installation
    pause
    exit /b 1
)

REM Start MCP Helper Service in a new window
echo Starting MCP Helper Service...
cd mcp_helper_project && start "MCP Helper Service" poetry run python mcp_helper_service.py && cd ..
REM Run main program with Poetry
echo Starting AIstudioProxy using Poetry...
poetry run python gui_launcher.py

REM Pause if error
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Program exited with code: %ERRORLEVEL%
    pause
)

endlocal