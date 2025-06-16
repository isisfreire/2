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
BACKEND_EXE = "./BroilerBackend"
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
            backend_path = self.base_dir / "BroilerBackend"
            if not backend_path.exists():
                raise FileNotFoundError(f"Backend executable not found: {backend_path}")
            
            # Make executable
            os.chmod(backend_path, 0o755)
            
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
            ], cwd=str(frontend_build_dir),
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
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
