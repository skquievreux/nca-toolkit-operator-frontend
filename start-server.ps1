# Smart Server Start Script
# Verhindert mehrfache Server-Starts

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 NCA Toolkit Server Manager         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Prüfe ob Server bereits läuft
Write-Host "🔍 Prüfe laufende Server..." -ForegroundColor Yellow
$existingProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mcp-nca-toolkit*server*" }

if ($existingProcesses) {
    Write-Host "⚠️  Server läuft bereits! ($($existingProcesses.Count) Prozesse)" -ForegroundColor Yellow
    Write-Host "`nOptionen:" -ForegroundColor Cyan
    Write-Host "  1) Bestehenden Server nutzen" -ForegroundColor Green
    Write-Host "  2) Server neu starten" -ForegroundColor Yellow
    Write-Host "  3) Server stoppen" -ForegroundColor Red
    Write-Host "  4) Abbrechen" -ForegroundColor Gray
    
    $choice = Read-Host "`nWählen Sie (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host "`n✅ Nutze bestehenden Server auf http://localhost:5000" -ForegroundColor Green
            Write-Host "🌐 Öffne Browser..." -ForegroundColor Cyan
            Start-Process "http://localhost:5000"
            exit 0
        }
        "2" {
            Write-Host "`n🛑 Versuche sanften Shutdown..." -ForegroundColor Yellow
            try {
                $null = Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/admin/shutdown" -TimeoutSec 2 -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
            catch {}
            
            Write-Host "🛑 Stoppe restliche Prozesse..." -ForegroundColor Yellow
            $existingProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Write-Host "✅ Server gestoppt!" -ForegroundColor Green
        }
        "3" {
            Write-Host "`n🛑 Stoppe Server..." -ForegroundColor Yellow
            try {
                $null = Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/admin/shutdown" -TimeoutSec 2 -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
            catch {}
            $existingProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Server beendet." -ForegroundColor Green
            exit 0
        }
        "4" {
            Write-Host "`n👋 Abgebrochen" -ForegroundColor Gray
            exit 0
        }
        default {
            Write-Host "`n❌ Ungültige Auswahl" -ForegroundColor Red
            exit 1
        }
    }
}

# 2. Prüfe Konfiguration
Write-Host "`n📝 Prüfe Konfiguration..." -ForegroundColor Yellow

# Stelle sicher, dass wir im Root-Verzeichnis sind
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Prüfe ob .env Dateien existieren
$rootEnvExists = Test-Path ".env"
$serverEnvExists = Test-Path "server\.env"

if (-not $rootEnvExists -and -not $serverEnvExists) {
    Write-Host "⚠️  Keine .env Dateien gefunden!" -ForegroundColor Yellow
    Write-Host "Verwende Standard-Konfiguration..." -ForegroundColor Cyan
    $apiKey = "343534sfklsjf343423"
}
else {
    # Versuche API-Key aus .env zu lesen
    $rootKey = $null
    $serverKey = $null
    
    if ($rootEnvExists) {
        $rootKeyLine = Get-Content .env | Select-String "^API_KEY=" | Select-Object -First 1
        if ($rootKeyLine) {
            $rootKey = $rootKeyLine.ToString().Split("=")[1].Trim()
        }
    }
    
    if ($serverEnvExists) {
        $serverKeyLine = Get-Content server\.env | Select-String "^NCA_API_KEY=" | Select-Object -First 1
        if ($serverKeyLine) {
            $serverKey = $serverKeyLine.ToString().Split("=")[1].Trim()
        }
    }
    
    # Verwende den ersten gefundenen Key
    $apiKey = if ($serverKey) { $serverKey } elseif ($rootKey) { $rootKey } else { "343534sfklsjf343423" }
    
    # Synchronisiere Keys wenn beide existieren aber unterschiedlich sind
    if ($rootKey -and $serverKey -and $rootKey -ne $serverKey) {
        Write-Host "⚠️  API-Keys stimmen nicht überein!" -ForegroundColor Red
        Write-Host "Root: $rootKey" -ForegroundColor Yellow
        Write-Host "Server: $serverKey" -ForegroundColor Yellow
        Write-Host "`n🔧 Fixe API-Keys..." -ForegroundColor Cyan
        
        $serverEnv = Get-Content server\.env
        $serverEnv = $serverEnv -replace "NCA_API_KEY=.*", "NCA_API_KEY=$rootKey"
        $serverEnv | Set-Content server\.env
        
        Write-Host "✅ API-Keys synchronisiert!" -ForegroundColor Green
        $apiKey = $rootKey
    }
}

Write-Host "✅ Konfiguration OK!" -ForegroundColor Green
Write-Host "  API-Key: $apiKey" -ForegroundColor Cyan

# 3. Starte Server
Write-Host "`n🚀 Starte Server..." -ForegroundColor Yellow
Write-Host "  Port: 5000" -ForegroundColor Cyan
Write-Host "  NCA Toolkit: http://localhost:8080" -ForegroundColor Cyan

# Stelle sicher, dass wir im server/ Verzeichnis sind
if (-not (Test-Path "server\app.py")) {
    Write-Host "❌ Kann server/app.py nicht finden!" -ForegroundColor Red
    Write-Host "Aktuelles Verzeichnis: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Set-Location server

# Starte in neuem Fenster mit Fehler-Pause
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { .\venv\Scripts\python.exe app.py; if (`$LASTEXITCODE -ne 0) { Write-Host '❌ Server Crash!' -ForegroundColor Red; Read-Host 'Press Enter...' } }" -WindowStyle Normal

# Warte bis Server bereit ist
Write-Host "`n⏳ Warte auf Server..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ Server läuft!" -ForegroundColor Green
        break
    }
    catch {
        $attempt++
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Host "`n❌ Server startet nicht!" -ForegroundColor Red
    Write-Host "Prüfen Sie das Server-Fenster für Fehler." -ForegroundColor Yellow
    exit 1
}

# 4. Öffne Browser
Write-Host "`n🌐 Öffne Browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5000"

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ SERVER LÄUFT!                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📋 Nützliche Befehle:" -ForegroundColor Yellow
Write-Host "  • Server stoppen: Schließen Sie das Server-Fenster" -ForegroundColor Cyan
Write-Host "  • Logs ansehen: Schauen Sie ins Server-Fenster" -ForegroundColor Cyan
Write-Host "  • Browser öffnen: http://localhost:5000" -ForegroundColor Cyan
Write-Host "  • Neu starten: Führen Sie dieses Script erneut aus`n" -ForegroundColor Cyan
