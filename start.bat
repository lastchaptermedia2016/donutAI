@echo off
echo ========================================
echo   Starting Donut AI
echo ========================================
echo.

:: Check .env has API key
findstr /C:"GROQ_API_KEY=your_groq_api" .env >nul
if %errorlevel% equ 0 (
    echo ERROR: Please edit .env and add your GROQ_API_KEY
    echo Get one at: https://console.groq.com
    pause
    exit /b 1
)

:: Create data dir
if not exist data mkdir data

:: Start backend in background
echo Starting backend on http://localhost:8000 ...
cd backend
start "Donut Backend" cmd /k "call .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
cd ..

:: Wait for backend
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

:: Start frontend
echo Starting frontend on http://localhost:3000 ...
cd frontend
start "Donut Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Donut AI is starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop both servers...
pause >nul

:: Kill both servers
taskkill /FI "WindowTitle eq Donut Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Donut Frontend*" /T /F >nul 2>&1
echo Donut AI stopped.