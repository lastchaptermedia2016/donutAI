@echo off
echo ========================================
echo   Setting up Donut AI
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11+ is required. Download from https://python.org
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js 20+ is required. Download from https://nodejs.org
    pause
    exit /b 1
)

:: Create .env if not exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env >nul
    echo.
    echo ACTION REQUIRED: Edit .env and add your GROQ_API_KEY
    echo You can get one at: https://console.groq.com
    echo.
    pause
)

:: Setup backend
echo.
echo Setting up backend...
cd backend
python -m venv .venv
call .venv\Scripts\activate
pip install -q -e .[dev]
cd ..

:: Setup frontend
echo.
echo Setting up frontend...
cd frontend
call npm install
cd ..

:: Create data directory
if not exist data mkdir data

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start Donut AI:
echo   Windows: start.bat
echo   Linux/Mac: ./start.sh
echo.
pause