@echo off
echo ========================================
echo    Tomato Disease Detection System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend...
start "Backend" cmd /k "cd /d %~dp0backend && python app.py"

echo [2/3] Starting Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [3/3] Waiting...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    Services Started!
echo ========================================
echo.
echo    Frontend: http://localhost:5173
echo    Backend:  http://127.0.0.1:5000
echo    Admin:    http://localhost:5173/admin
echo.
echo    Account:  admin / password123
echo ========================================
echo.

start http://localhost:5173

pause
