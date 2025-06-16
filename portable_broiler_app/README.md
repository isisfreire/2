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
