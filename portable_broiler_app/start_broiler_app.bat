@echo off
echo Starting Broiler Farm Manager...
echo.

REM Start Python backend
echo Starting backend server...
cd backend
start /B python server.py
cd ..

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend (simple HTTP server)
echo Starting frontend...
cd frontend/build
python -m http.server 3000 --bind 127.0.0.1
