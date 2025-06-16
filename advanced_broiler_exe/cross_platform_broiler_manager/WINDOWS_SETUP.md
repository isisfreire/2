# Windows Setup Instructions

Since this was built on Linux, the executable is for Linux systems. For Windows users, here are the options:

## Option 1: Use Python Directly (Recommended)
1. Install Python 3.7+ from https://python.org
2. Install required packages:
   ```
   pip install fastapi uvicorn pydantic reportlab
   ```
3. Replace the `BroilerBackend` file with the Python source files
4. Run `python BroilerFarmManager.py`

## Option 2: Use Pre-built Portable Version
1. Use the `portable_broiler_app` folder instead
2. Run `start_broiler_app.bat`
3. This uses Python scripts directly (no compilation needed)

## Option 3: Build Windows .exe
If you have PyInstaller on Windows:
1. Copy the source files to Windows
2. Install: `pip install pyinstaller`
3. Run: `pyinstaller --onefile server.py`
4. This creates a Windows .exe file

## Recommended for Windows Users
Use the portable version from the `portable_broiler_app` folder as it's the most compatible option.
