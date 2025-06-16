const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Menu events
  onMenuNewBatch: (callback) => ipcRenderer.on('menu-new-batch', callback),
  onMenuExportData: (callback) => ipcRenderer.on('menu-export-data', callback),
  onMenuPerformance: (callback) => ipcRenderer.on('menu-performance', callback),
  onMenuBatchManagement: (callback) => ipcRenderer.on('menu-batch-management', callback),
  onMenuSettings: (callback) => ipcRenderer.on('menu-settings', callback),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Get backend URL
  getBackendURL: () => {
    // This will be set by the main process
    return process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8001';
  },
  
  // Platform info
  platform: process.platform,
  
  // App version
  appVersion: require('./package.json').version
});

// Set backend URL for React app
window.REACT_APP_BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8001';