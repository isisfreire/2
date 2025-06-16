#!/bin/bash

# Advanced .exe Build Script for Broiler Farm Manager

echo "🐔 Building Advanced .exe Broiler Farm Manager..."

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    print_status "Installing PyInstaller..."
    pip install pyinstaller
fi

# Create advanced build directory
print_status "Creating advanced build environment..."
mkdir -p advanced_broiler_exe
cd advanced_broiler_exe

# Copy and prepare backend
print_status "Preparing backend for compilation..."
cp -r ../offline_backend ./backend
cd backend

# Create enhanced PyInstaller spec
print_status "Creating PyInstaller specification..."
cat > broiler_server.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add all necessary data files and hidden imports
a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('*.py', '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off', 
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.logging',
        'fastapi',
        'fastapi.responses',
        'fastapi.middleware.cors',
        'pydantic',
        'sqlite3',
        'json',
        'pathlib',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.lib.enums',
        'reportlab.pdfbase._fontdata_enc_winansi',
        'reportlab.pdfbase._fontdata_enc_macroman',
        'reportlab.pdfbase._fontdata_enc_standard',
        'reportlab.pdfbase._fontdata_enc_symbol',
        'reportlab.pdfbase._fontdata_enc_zapfdingbats',
        'reportlab.pdfbase._fontdata_widths_courier',
        'reportlab.pdfbase._fontdata_widths_courierbold',
        'reportlab.pdfbase._fontdata_widths_courieroblique',
        'reportlab.pdfbase._fontdata_widths_courierboldoblique',
        'reportlab.pdfbase._fontdata_widths_helvetica',
        'reportlab.pdfbase._fontdata_widths_helveticabold',
        'reportlab.pdfbase._fontdata_widths_helveticaoblique',
        'reportlab.pdfbase._fontdata_widths_helveticaboldoblique',
        'reportlab.pdfbase._fontdata_widths_timesroman',
        'reportlab.pdfbase._fontdata_widths_timesbold',
        'reportlab.pdfbase._fontdata_widths_timesitalic',
        'reportlab.pdfbase._fontdata_widths_timesbolditalic',
        'reportlab.pdfbase._fontdata_widths_symbol',
        'reportlab.pdfbase._fontdata_widths_zapfdingbats'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BroilerBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Add icon file path here if you have one
)
EOF

# Build the backend executable
print_status "Compiling backend to .exe..."
pyinstaller broiler_server.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/BroilerBackend.exe" ]; then
    print_success "Backend .exe created successfully!"
else
    print_error "Failed to create backend .exe"
    exit 1
fi

cd ..

# Prepare frontend
print_status "Preparing frontend..."
cp -r ../frontend ./
cd frontend

# Build frontend with correct configuration
echo "REACT_APP_BACKEND_URL=http://127.0.0.1:8001" > .env
npm install
npm run build

cd ..

# Create main launcher
print_status "Creating main application launcher..."
cat > BroilerFarmManager.py << 'EOF'
#!/usr/bin/env python3
"""
Broiler Farm Manager - Main Application Launcher
This script starts both the backend server and opens the frontend in the default browser.
"""

import subprocess
import time
import webbrowser
import os
import sys
import threading
import signal
from pathlib import Path

# Configuration
BACKEND_EXE = "BroilerBackend.exe"
FRONTEND_PORT = 3000
BACKEND_PORT = 8001
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

class BroilerFarmManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        
    def start_backend(self):
        """Start the backend server"""
        try:
            backend_path = self.base_dir / BACKEND_EXE
            if not backend_path.exists():
                raise FileNotFoundError(f"Backend executable not found: {backend_path}")
            
            print("Starting backend server...")
            self.backend_process = subprocess.Popen(
                [str(backend_path)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for backend to start
            time.sleep(3)
            
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                raise RuntimeError(f"Backend failed to start: {stderr.decode()}")
                
            print(f"✅ Backend server started (PID: {self.backend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        try:
            frontend_build_dir = self.base_dir / "frontend" / "build"
            if not frontend_build_dir.exists():
                raise FileNotFoundError(f"Frontend build directory not found: {frontend_build_dir}")
            
            print("Starting frontend server...")
            
            # Start Python HTTP server for frontend
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", str(FRONTEND_PORT),
                "--bind", "127.0.0.1"
            ], cwd=str(frontend_build_dir))
            
            # Wait for frontend to start
            time.sleep(2)
            
            if self.frontend_process.poll() is not None:
                raise RuntimeError("Frontend server failed to start")
                
            print(f"✅ Frontend server started (PID: {self.frontend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def open_browser(self):
        """Open the application in the default browser"""
        try:
            print(f"Opening browser to {FRONTEND_URL}...")
            webbrowser.open(FRONTEND_URL)
            print("✅ Browser opened successfully")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print(f"Please manually open: {FRONTEND_URL}")
    
    def stop_services(self):
        """Stop all services"""
        print("\nStopping services...")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend server stopped")
            except:
                self.frontend_process.kill()
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Backend server stopped")
            except:
                self.backend_process.kill()
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C and other termination signals"""
        print("\nReceived termination signal...")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Main application entry point"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🐔 Broiler Farm Manager Starting...")
        print("=" * 50)
        
        try:
            # Start backend
            if not self.start_backend():
                return 1
            
            # Start frontend  
            if not self.start_frontend():
                return 1
            
            # Open browser
            self.open_browser()
            
            print("\n" + "=" * 50)
            print("🎉 Broiler Farm Manager is running!")
            print(f"📱 Access the app at: {FRONTEND_URL}")
            print("💾 Data is stored locally in: broiler_data.db")
            print("📄 Reports are saved in: exports/")
            print("\nPress Ctrl+C to stop the application")
            print("=" * 50)
            
            # Keep the application running
            try:
                while True:
                    time.sleep(1)
                    # Check if processes are still running
                    if (self.backend_process and self.backend_process.poll() is not None or
                        self.frontend_process and self.frontend_process.poll() is not None):
                        print("⚠️  A service has stopped unexpectedly")
                        break
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"❌ Application error: {e}")
            return 1
        finally:
            self.stop_services()
        
        return 0

if __name__ == "__main__":
    app = BroilerFarmManager()
    sys.exit(app.run())
EOF

# Create main launcher spec
cat > BroilerFarmManager.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['BroilerFarmManager.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/build', 'frontend/build'),
        ('BroilerBackend.exe', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BroilerFarmManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for status messages
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
EOF

# Copy the backend executable to current directory
cp backend/dist/BroilerBackend.exe ./

# Build the main application
print_status "Building main application .exe..."
pyinstaller BroilerFarmManager.spec --clean --noconfirm

# Create final package
print_status "Creating final package..."
mkdir -p final_package

if [ -f "dist/BroilerFarmManager.exe" ]; then
    cp dist/BroilerFarmManager.exe final_package/
    
    # Create additional files for the package
    cat > final_package/README.txt << 'EOF'
Broiler Farm Manager - Offline Application

QUICK START:
1. Double-click BroilerFarmManager.exe
2. Wait for the application to start (may take 30 seconds first time)
3. Your web browser will open automatically
4. Start using the application!

FEATURES:
✅ Fully offline operation
✅ Local data storage
✅ PDF report generation
✅ No internet required
✅ Complete broiler farm management

DATA STORAGE:
- All data is stored locally in broiler_data.db
- Reports are saved in the exports/ folder
- Your data never leaves your computer

SYSTEM REQUIREMENTS:
- Windows 10 or later (64-bit)
- 100MB free disk space
- Web browser (Chrome, Firefox, Edge)

TROUBLESHOOTING:
- If Windows blocks the app, click "More info" then "Run anyway"
- If your antivirus blocks it, add an exception
- Make sure ports 3000 and 8001 are not in use
- Check the console window for error messages

For support, please check the documentation or contact support.
EOF

    # Create uninstall instructions
    cat > final_package/UNINSTALL.txt << 'EOF'
To uninstall Broiler Farm Manager:

1. Close the application if it's running
2. Delete the application folder
3. No registry entries or system files are modified

To keep your data:
- Copy broiler_data.db before deleting
- Copy the exports/ folder for your reports

To completely remove everything:
- Just delete the entire application folder
EOF

    print_success "✅ .exe application created successfully!"
    print_status "Location: $(pwd)/final_package/"
    print_status "Main executable: BroilerFarmManager.exe"
    
    # Get file size
    EXE_SIZE=$(du -h final_package/BroilerFarmManager.exe | cut -f1)
    print_status "Size: $EXE_SIZE"
    
    echo ""
    echo "🎉 Your standalone .exe Broiler Farm Manager is ready!"
    echo ""
    echo "📦 Package contents:"
    ls -la final_package/
    echo ""
    echo "To distribute:"
    echo "1. Copy the entire final_package folder"
    echo "2. Users just need to run BroilerFarmManager.exe"
    echo "3. No installation required!"
    
else
    print_warning "Main executable not found. Check for build errors."
    exit 1
fi

print_success "Advanced .exe build completed! 🚀"