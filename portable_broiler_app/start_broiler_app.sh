#!/bin/bash

echo "Starting Broiler Farm Manager..."
echo

# Start Python backend
echo "Starting backend server..."
cd backend
python3 server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend (simple HTTP server)
echo "Starting frontend..."
echo "Open your browser to: http://127.0.0.1:3000"
cd frontend/build
python3 -m http.server 3000 --bind 127.0.0.1 &
FRONTEND_PID=$!

# Wait for user to press Ctrl+C
echo
echo "Press Ctrl+C to stop the application"
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
