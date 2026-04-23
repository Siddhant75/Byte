const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    onToggleChat: (callback) => ipcRenderer.on('toggle-chat', (_event, ...args) => callback(...args))
});
