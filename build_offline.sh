#!/bin/bash

# Broiler Farm Manager - Offline Build Script

echo "🐔 Building Offline Broiler Farm Manager..."

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create build directory structure
print_status "Creating build directory structure..."
mkdir -p offline_build
cd offline_build

# Copy and modify frontend
print_status "Preparing frontend..."
cp -r ../frontend ./
cd frontend

# Update package.json to set homepage for Electron
print_status "Updating frontend configuration for Electron..."
sed -i 's/"homepage": ".*"/"homepage": ".\/"/g' package.json || true

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

# Build frontend
print_status "Building React frontend..."
npm run build

cd ..

# Copy backend with modifications
print_status "Preparing backend..."
cp -r ../offline_backend ./backend

# Copy Electron configuration
print_status "Preparing Electron app..."
cp -r ../electron_app/* ./

# Update Electron package.json paths
print_status "Updating Electron configuration..."
cat > package.json << 'EOF'
{
  "name": "broiler-farm-manager",
  "version": "1.0.0",
  "description": "Offline Broiler Chicken Cost Calculation Application",
  "main": "main.js",
  "homepage": "./",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "pack": "electron-builder --dir",
    "dist": "electron-builder",
    "postinstall": "electron-builder install-app-deps"
  },
  "build": {
    "appId": "com.broilerfarm.manager",
    "productName": "Broiler Farm Manager",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "backend/**/*",
      "frontend/build/**/*",
      "node_modules/**/*"
    ],
    "extraResources": [
      {
        "from": "backend/",
        "to": "backend/"
      }
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": [
            "x64"
          ]
        }
      ]
    },
    "nsis": {
      "oneClick": false,
      "perMachine": true,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    },
    "mac": {
      "target": "dmg"
    },
    "linux": {
      "target": "AppImage"
    }
  },
  "devDependencies": {
    "electron": "^27.0.0",
    "electron-builder": "^24.6.4"
  },
  "dependencies": {
    "electron-is-dev": "^2.0.0",
    "ps-tree": "^1.2.0"
  }
}
EOF

# Install Electron dependencies
print_status "Installing Electron dependencies..."
npm install

# Create Python executable using PyInstaller
print_status "Creating Python executable..."
cd backend

# Create PyInstaller spec file
cat > server.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.logging',
        'pydantic',
        'fastapi',
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
    name='broiler_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Check if PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    print_status "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build Python executable
print_status "Building Python backend executable..."
pyinstaller server.spec --clean --distpath ./dist

# Copy the executable to the backend directory
if [ -f "dist/broiler_backend.exe" ]; then
    cp dist/broiler_backend.exe ./
    print_success "Python executable created: broiler_backend.exe"
elif [ -f "dist/broiler_backend" ]; then
    cp dist/broiler_backend ./
    print_success "Python executable created: broiler_backend"
else
    print_error "Failed to create Python executable"
    exit 1
fi

cd ..

# Create assets directory with default icon
print_status "Creating application assets..."
mkdir -p assets

# Create a simple icon placeholder (you can replace with actual icons)
echo "Creating placeholder icon..."
# This is a placeholder - in production you'd have actual icon files

# Build Electron app
print_status "Building Electron application..."
npm run build

# Check if build was successful
if [ -d "dist" ]; then
    print_success "Build completed successfully!"
    print_status "Build artifacts are in: $(pwd)/dist"
    
    # List build artifacts
    echo ""
    echo "📦 Build Artifacts:"
    ls -la dist/
    
    # Get the size of the main executable/installer
    if [ -f "dist/*.exe" ]; then
        EXE_SIZE=$(du -h dist/*.exe | cut -f1)
        print_status "Installer size: $EXE_SIZE"
    fi
    
    echo ""
    print_success "🎉 Offline Broiler Farm Manager build complete!"
    print_status "You can now distribute the files in the 'dist' directory"
    
else
    print_error "Build failed - no dist directory found"
    exit 1
fi

# Create portable version instructions
print_status "Creating portable version instructions..."
cat > PORTABLE_INSTRUCTIONS.md << 'EOF'
# Broiler Farm Manager - Portable Version

## Installation
1. Extract all files to a folder of your choice
2. Run the executable file
3. The application will create a local database file in the same directory

## Features
- Fully offline operation
- Local SQLite database
- PDF report generation
- No internet connection required
- Portable - can run from USB drive

## Data Storage
- Database file: `broiler_data.db`
- Export files: `exports/` folder
- All data is stored locally

## System Requirements
- Windows 10/11 (64-bit)
- 100MB free disk space
- No additional software required

## Troubleshooting
- If the app doesn't start, check Windows Defender/antivirus settings
- Make sure you have write permissions to the folder
- Check the console for error messages

EOF

print_success "Created portable version instructions"
print_status "Build process completed! 🐔"