const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const fs = require('fs');
const psTree = require('ps-tree');

let mainWindow;
let backendProcess;

// Backend server configuration
const BACKEND_PORT = 8001;
const BACKEND_HOST = '127.0.0.1';

// Function to find available port
function findAvailablePort(startPort) {
  return new Promise((resolve) => {
    const net = require('net');
    const server = net.createServer();
    
    server.listen(startPort, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
    
    server.on('error', () => {
      resolve(findAvailablePort(startPort + 1));
    });
  });
}

// Function to start Python backend
async function startBackend() {
  try {
    console.log('Starting Python backend...');
    
    // Determine backend path
    let backendPath;
    if (isDev) {
      backendPath = path.join(__dirname, '..', 'offline_backend');
    } else {
      backendPath = path.join(process.resourcesPath, 'backend');
    }
    
    console.log('Backend path:', backendPath);
    
    // Check if backend files exist
    const serverPath = path.join(backendPath, 'server.py');
    if (!fs.existsSync(serverPath)) {
      throw new Error(`Backend server not found at: ${serverPath}`);
    }
    
    // Find available port
    const port = await findAvailablePort(BACKEND_PORT);
    console.log(`Using port: ${port}`);
    
    // Start Python server
    const pythonExecutable = isDev ? 'python' : 'python';
    
    backendProcess = spawn(pythonExecutable, [
      '-m', 'uvicorn',
      'server:app',
      '--host', BACKEND_HOST,
      '--port', port.toString(),
      '--reload' // Remove in production
    ], {
      cwd: backendPath,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    // Handle backend output
    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend stdout: ${data}`);
    });
    
    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend stderr: ${data}`);
    });
    
    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      dialog.showErrorBox('Backend Error', `Failed to start backend server: ${error.message}`);
    });
    
    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
      if (code !== 0 && mainWindow) {
        dialog.showErrorBox('Backend Error', `Backend server crashed with code ${code}`);
      }
    });
    
    // Wait for server to start
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('Backend started successfully');
    return port;
    
  } catch (error) {
    console.error('Error starting backend:', error);
    dialog.showErrorBox('Startup Error', `Failed to start backend: ${error.message}`);
    throw error;
  }
}

// Function to stop backend
function stopBackend() {
  return new Promise((resolve) => {
    if (backendProcess && !backendProcess.killed) {
      console.log('Stopping backend process...');
      
      // Kill process tree (including child processes)
      psTree(backendProcess.pid, (err, children) => {
        if (err) {
          console.error('Error getting process tree:', err);
          backendProcess.kill('SIGTERM');
          resolve();
          return;
        }
        
        // Kill all child processes
        children.forEach(child => {
          try {
            process.kill(child.PID);
          } catch (e) {
            console.error('Error killing child process:', e);
          }
        });
        
        // Kill main process
        backendProcess.kill('SIGTERM');
        
        setTimeout(() => {
          if (!backendProcess.killed) {
            backendProcess.kill('SIGKILL');
          }
          resolve();
        }, 2000);
      });
    } else {
      resolve();
    }
  });
}

// Function to create main window
async function createWindow() {
  try {
    // Start backend first
    const port = await startBackend();
    
    // Create the browser window
    mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1000,
      minHeight: 700,
      icon: path.join(__dirname, 'assets', 'icon.png'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js')
      },
      show: false // Don't show until ready
    });
    
    // Set backend URL for frontend
    global.BACKEND_URL = `http://${BACKEND_HOST}:${port}`;
    
    // Load the frontend
    const frontendPath = isDev 
      ? 'http://localhost:3000' 
      : `file://${path.join(__dirname, 'frontend', 'build', 'index.html')}`;
    
    console.log('Loading frontend from:', frontendPath);
    await mainWindow.loadURL(frontendPath);
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      
      // Focus on window
      if (isDev) {
        mainWindow.webContents.openDevTools();
      }
    });
    
    // Handle window closed
    mainWindow.on('closed', () => {
      mainWindow = null;
    });
    
    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
    
    // Handle navigation
    mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
      const parsedUrl = new URL(navigationUrl);
      
      if (parsedUrl.origin !== `http://${BACKEND_HOST}:${port}` && !navigationUrl.startsWith('file://')) {
        event.preventDefault();
        shell.openExternal(navigationUrl);
      }
    });
    
  } catch (error) {
    console.error('Error creating window:', error);
    dialog.showErrorBox('Startup Error', `Failed to start application: ${error.message}`);
    app.quit();
  }
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', async () => {
  console.log('All windows closed, stopping backend...');
  await stopBackend();
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', async (event) => {
  if (backendProcess && !backendProcess.killed) {
    event.preventDefault();
    console.log('Stopping backend before quit...');
    await stopBackend();
    app.quit();
  }
});

// Handle app quit
process.on('SIGINT', async () => {
  console.log('Received SIGINT, stopping backend...');
  await stopBackend();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('Received SIGTERM, stopping backend...');
  await stopBackend();
  process.exit(0);
});

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Batch',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-new-batch');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Export Data',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-export-data');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.reload();
            }
          }
        },
        {
          label: 'Force Reload',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.reloadIgnoringCache();
            }
          }
        },
        {
          label: 'Toggle Developer Tools',
          accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Actual Size',
          accelerator: 'CmdOrCtrl+0',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.setZoomLevel(0);
            }
          }
        },
        {
          label: 'Zoom In',
          accelerator: 'CmdOrCtrl+Plus',
          click: () => {
            if (mainWindow) {
              const currentZoom = mainWindow.webContents.getZoomLevel();
              mainWindow.webContents.setZoomLevel(currentZoom + 1);
            }
          }
        },
        {
          label: 'Zoom Out',
          accelerator: 'CmdOrCtrl+-',
          click: () => {
            if (mainWindow) {
              const currentZoom = mainWindow.webContents.getZoomLevel();
              mainWindow.webContents.setZoomLevel(currentZoom - 1);
            }
          }
        }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Performance Analysis',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-performance');
            }
          }
        },
        {
          label: 'Batch Management',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-batch-management');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Settings',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-settings');
            }
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Broiler Farm Manager',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Broiler Farm Manager',
              message: 'Broiler Farm Manager v1.0.0',
              detail: 'Offline broiler chicken cost calculation and farm management application.\n\nBuilt with Electron, React, FastAPI, and SQLite.'
            });
          }
        },
        {
          label: 'User Guide',
          click: () => {
            shell.openExternal('https://github.com/broiler-farm-manager/user-guide');
          }
        },
        { type: 'separator' },
        {
          label: 'Report Issue',
          click: () => {
            shell.openExternal('https://github.com/broiler-farm-manager/issues');
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
  createMenu();
});

// Export for use in renderer process
module.exports = { BACKEND_URL: global.BACKEND_URL };