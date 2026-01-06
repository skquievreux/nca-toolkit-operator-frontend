# NCA Toolkit Backend Server - Setup & Start
# Dieses Skript richtet das virtuelle Environment ein und startet den Server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NCA Toolkit Backend Server Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Wechsle ins server-Verzeichnis
Set-Location -Path "$PSScriptRoot\server"

# 1. Prüfe Python
Write-Host "[1/5] Prüfe Python-Installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion gefunden" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python 3.9+ von python.org" -ForegroundColor Red
    exit 1
}

# 2. Erstelle virtuelles Environment
Write-Host ""
Write-Host "[2/5] Erstelle virtuelles Environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ venv existiert bereits" -ForegroundColor Green
}
else {
    python -m venv venv
    Write-Host "✓ venv erstellt" -ForegroundColor Green
}

# 3. Aktiviere Environment
Write-Host ""
Write-Host "[3/5] Aktiviere Environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Environment aktiviert" -ForegroundColor Green

# 4. Installiere Dependencies
Write-Host ""
Write-Host "[4/5] Installiere Dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "✓ Dependencies installiert" -ForegroundColor Green

# 5. Erstelle .env falls nicht vorhanden
Write-Host ""
Write-Host "[5/5] Prüfe Konfiguration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env erstellt (bitte API-Key anpassen!)" -ForegroundColor Yellow
}
else {
    Write-Host "✓ .env vorhanden" -ForegroundColor Green
}

# Fertig!
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup abgeschlossen!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Server starten mit:" -ForegroundColor Cyan
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Oder direkt starten:" -ForegroundColor Cyan
Write-Host ""

# Starte Server
Write-Host "Server wird gestartet..." -ForegroundColor Yellow
Write-Host ""
python app.py
