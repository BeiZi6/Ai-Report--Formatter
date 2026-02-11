/* eslint-disable @typescript-eslint/no-require-imports */
const { contextBridge, ipcRenderer } = require("electron");

const DESKTOP_API_BASE_URL = process.env.DESKTOP_API_BASE_URL ?? "http://127.0.0.1:8000";
const BACKEND_STATUS_CHANNEL = "desktop:backend-startup-status";

contextBridge.exposeInMainWorld("desktop", {
  apiBaseUrl: DESKTOP_API_BASE_URL,
  platform: process.platform,
  ping: () => ipcRenderer.invoke("desktop:ping"),
  getLogFilePath: () => ipcRenderer.invoke("desktop:get-log-file-path"),
  exportLogs: () => ipcRenderer.invoke("desktop:export-logs"),
  getBackendStartupStatus: () => ipcRenderer.invoke("desktop:get-backend-startup-status"),
  onBackendStartupStatus: (listener) => {
    const wrapped = (_event, payload) => {
      listener(payload);
    };
    ipcRenderer.on(BACKEND_STATUS_CHANNEL, wrapped);
    return () => {
      ipcRenderer.removeListener(BACKEND_STATUS_CHANNEL, wrapped);
    };
  },
});
