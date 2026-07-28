@echo off
REM =============================================================================
REM SimpleChatbot - Main Agent Setup & Deployment (Windows)
REM =============================================================================
REM This script validates prerequisites, installs the AgentCore CLI,
REM scaffolds the agent project, and deploys to Amazon Bedrock AgentCore Runtime.
REM
REM Usage:
REM   scripts\setup_main_agents.bat          Full setup and deploy
REM   scripts\setup_main_agents.bat dev      Local development only
REM   scripts\setup_main_agents.bat deploy   Deploy only (skip scaffold)
REM =============================================================================

echo =============================================
echo   SimpleChatbot - Main Agent Setup
echo   Amazon Bedrock AgentCore Runtime
echo =============================================
echo.

REM Navigate to the project root directory
cd /d "%~dp0\.."
set PROJECT_DIR=%CD%
set AGENT_DIR=%PROJECT_DIR%\agents\mainagent

REM ---------------------------------------------------------------------------
REM Step 1: Validate Prerequisites
REM ---------------------------------------------------------------------------

echo [1/7] Validating prerequisites...

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed. Please install Python 3.10+.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
echo   Python %PYTHON_VERSION%

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js 20+.
    echo   Install: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo   Node.js %NODE_VERSION%

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm is not installed.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo   npm %NPM_VERSION%

REM Check AWS CLI
where aws >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: AWS CLI is not installed.
    echo   Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)
echo   AWS CLI installed

REM Check AWS credentials
aws sts get-caller-identity >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: AWS credentials not configured or expired.
    echo   Run: aws configure
    pause
    exit /b 1
)
echo   AWS credentials: valid

REM Check uv
where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo   uv installed
) else (
    echo   uv: not found (will use pip instead)
)

echo.
echo   All prerequisites validated.
echo.

REM ---------------------------------------------------------------------------
REM Step 2: Install AgentCore CLI
REM ---------------------------------------------------------------------------

echo [2/7] Checking AgentCore CLI...

where agentcore >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo   AgentCore CLI already installed.
) else (
    echo   Installing @aws/agentcore CLI...
    npm install -g @aws/agentcore
    echo   AgentCore CLI installed successfully.
)
echo.

REM ---------------------------------------------------------------------------
REM Step 3: Handle command argument
REM ---------------------------------------------------------------------------

set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=full

if "%COMMAND%"=="dev" (
    echo [3/7] Starting local development server...
    echo.
    echo   Starting agentcore dev on port 8080...
    echo   Test with: curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d "{\"prompt\": \"Hello!\"}"
    echo.
    cd /d "%AGENT_DIR%"
    agentcore dev --no-browser
    exit /b 0
)

if "%COMMAND%"=="deploy" (
    echo [3/7] Deploying to AgentCore Runtime...
    cd /d "%AGENT_DIR%"
    agentcore deploy
    echo.
    echo   Deployment complete!
    echo.
    echo   Next steps:
    echo     agentcore invoke "{\"prompt\": \"Hello from SimpleChatbot!\"}"
    echo     agentcore status
    echo     agentcore logs
    pause
    exit /b 0
)

REM ---------------------------------------------------------------------------
REM Step 4: Scaffold Agent Project (if not already done)
REM ---------------------------------------------------------------------------

echo [3/7] Scaffolding agent project...

if exist "%AGENT_DIR%\agentcore" (
    echo   Agent project already scaffolded. Skipping.
) else (
    cd /d "%AGENT_DIR%"
    agentcore create --name mainagent --framework Strands --protocol HTTP --model-provider Bedrock --memory none
    echo   Agent project scaffolded.
)
echo.

REM ---------------------------------------------------------------------------
REM Step 5: Verify agent code
REM ---------------------------------------------------------------------------

echo [4/7] Verifying agent code...

if not exist "%AGENT_DIR%\main.py" (
    echo ERROR: main.py not found in agents\mainagent\
    echo   Please ensure the agent code exists at: %AGENT_DIR%\main.py
    pause
    exit /b 1
)
echo   main.py found in agents\mainagent\

if not exist "%AGENT_DIR%\pyproject.toml" (
    echo ERROR: pyproject.toml not found in agents\mainagent\
    pause
    exit /b 1
)
echo   pyproject.toml found in agents\mainagent\
echo.

REM ---------------------------------------------------------------------------
REM Step 6: Install dependencies
REM ---------------------------------------------------------------------------

echo [5/7] Installing dependencies...

cd /d "%AGENT_DIR%"

where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    uv sync
    echo   Dependencies installed with uv.
) else (
    python -m pip install -e . --quiet
    echo   Dependencies installed with pip.
)
echo.

REM ---------------------------------------------------------------------------
REM Step 7: Local testing prompt
REM ---------------------------------------------------------------------------

echo [6/7] Ready for local testing...
echo.
echo   To test locally, run:
echo     cd %AGENT_DIR%
echo     agentcore dev --no-browser
echo.
echo   Then in another terminal:
echo     curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d "{\"prompt\": \"Hello from SimpleChatbot!\"}"
echo.

REM ---------------------------------------------------------------------------
REM Step 8: Deploy
REM ---------------------------------------------------------------------------

echo [7/7] Deploy to AgentCore Runtime...
echo.

set /p DEPLOY_CONFIRM="  Deploy to AWS now? (y/N): "

if /i "%DEPLOY_CONFIRM%"=="y" (
    agentcore deploy
    echo.
    echo =============================================
    echo   Deployment Complete!
    echo =============================================
    echo.
    echo   Next steps:
    echo     agentcore invoke "{\"prompt\": \"Hello from SimpleChatbot!\"}"
    echo     agentcore status
    echo     agentcore logs
) else (
    echo.
    echo   Deployment skipped. To deploy later, run:
    echo     cd %AGENT_DIR%
    echo     agentcore deploy
)

echo.
echo   Done!
pause
