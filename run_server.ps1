# PowerShell Script to manage NCA Toolkit Server
# This script kills any running python.exe processes (specifically for this app) and restarts the server.

Write-Host "🔄 Restarting NCA Toolkit Backend..." -ForegroundColor Cyan

# 1. Kill any existing python instances running app.py
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.CommandLine -like "*app.py*" 
}

if ($processes) {
    Write-Host "🛑 Stopping existing server processes..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
}

# 2. Wait a moment
Start-Sleep -Seconds 1

# 3. Start the server
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
cd "$PSScriptRoot"
& "server\venv\Scripts\python.exe" "server\app.py"
