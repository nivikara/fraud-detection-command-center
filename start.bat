@echo off
color 0A
echo ===================================================
echo   Starting Fraud Detection Command Center...
echo ===================================================
echo.

REM 1. Start the Python Flask Backend in a new window
echo Starting Backend (Flask)...
cd backend
start "Fraud API (Backend)" cmd /k "python app.py"
cd ..

REM 2. Start the Angular Frontend in a new window
echo Starting Frontend (Angular)...
cd frontend
start "Fraud UI (Frontend)" cmd /k "ng serve --open"
cd ..

echo.
echo ===================================================
echo   SUCCESS! Both servers are booting up.
echo   Angular will open your browser automatically.
echo ===================================================
pause