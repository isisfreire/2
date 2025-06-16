#!/bin/bash

# Simple Offline Build Script for Broiler Farm Manager

echo "🐔 Building Offline Broiler Farm Manager (Simplified)..."

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Create portable app directory
print_status "Creating portable application..."
mkdir -p portable_broiler_app
cd portable_broiler_app

# Copy the working frontend
print_status "Copying frontend..."
cp -r ../frontend ./

# Build frontend with proper configuration
cd frontend
print_status "Building React frontend..."

# Update .env to point to local backend
echo "REACT_APP_BACKEND_URL=http://127.0.0.1:8001" > .env

# Install and build
npm install
npm run build

cd ..

# Copy offline backend
print_status "Copying backend..."
cp -r ../offline_backend ./backend

# Install Python dependencies
cd backend
print_status "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Create startup script for Windows
print_status "Creating startup scripts..."
cat > start_broiler_app.bat << 'EOF'
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
EOF

# Create startup script for Linux/Mac
cat > start_broiler_app.sh << 'EOF'
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
EOF

chmod +x start_broiler_app.sh

# Create README for users
cat > README.md << 'EOF'
# Broiler Farm Manager - Portable Version

## Quick Start

### Windows
1. Double-click `start_broiler_app.bat`
2. Wait for the services to start
3. Open your browser to: http://127.0.0.1:3000

### Linux/Mac
1. Open terminal in this folder
2. Run: `./start_broiler_app.sh`
3. Open your browser to: http://127.0.0.1:3000

## Features
- ✅ Fully offline operation
- ✅ Local SQLite database
- ✅ PDF report generation
- ✅ No internet connection required
- ✅ Portable - runs from any folder

## What's Included
- `backend/` - Python FastAPI server with SQLite database
- `frontend/` - React web application (built)
- `start_broiler_app.*` - Startup scripts
- `exports/` - Generated reports will be saved here

## Data Storage
- Database: `backend/broiler_data.db`
- Reports: `exports/` folder
- All data stays on your computer

## Requirements
- Python 3.7+ installed
- Modern web browser (Chrome, Firefox, Edge, Safari)
- 50MB free disk space

## Troubleshooting
- If port 3000 or 8001 are in use, close other applications using those ports
- Check that Python is installed: `python --version`
- Make sure your antivirus isn't blocking the application
- Check the console/terminal for error messages

## Support
This is a portable version of the Broiler Farm Manager application.
All features from the web version are available offline.
EOF

# Create simple requirements file for user reference
cat > REQUIREMENTS.txt << 'EOF'
System Requirements:
- Python 3.7 or higher
- Web browser (Chrome, Firefox, Edge, Safari)
- 50MB free disk space
- Windows 10+, macOS 10.14+, or Linux

Python packages included:
- FastAPI
- Uvicorn
- Pydantic
- ReportLab (for PDF generation)
EOF

print_success "Portable application created successfully!"
print_status "Location: $(pwd)"
print_status "Size: $(du -sh . | cut -f1)"

echo ""
echo "📦 Your portable Broiler Farm Manager is ready!"
echo ""
echo "To use:"
echo "1. Copy this entire folder to any computer"
echo "2. Run the startup script for your operating system"
echo "3. Open http://127.0.0.1:3000 in your browser"
echo ""
print_success "Build completed! 🎉"