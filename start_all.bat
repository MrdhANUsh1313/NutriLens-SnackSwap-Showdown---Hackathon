@echo off
echo ============================================================
echo   🥑 NutriLens: SnackSwap Showdown - Hackathon Runner
echo ============================================================
echo.
echo [1/2] Starting Backend API Server (Port 8000)...
start "NutriLens Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0run_backend.ps1"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend Vite Mobile App (Port 5173)...
start "NutriLens Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0run_frontend.ps1"

echo.
echo Both servers initiated!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
pause
