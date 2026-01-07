# 🎯 Troubleshooting-Konzept: Von Minimal bis Komplex

## Problem-Analyse

**Aktueller Status:**
- ✅ Flask Server läuft
- ✅ Docker Container läuft
- ❌ Keine Ergebnisse vom NCA Toolkit
- ❓ API-Key korrekt?
- ❓ NCA Toolkit erreichbar?

---

## Level 1: MINIMAL - Basis-Tests (5 Minuten)

### Test 1.1: Ist der NCA Toolkit Container erreichbar?

```powershell
# Direkt NCA Toolkit testen (OHNE Flask)
curl http://localhost:8080/
```

**Erwartetes Ergebnis:**
```json
{
  "message": "Welcome to NCA Toolkit API",
  "version": "1.0.0"
}
```

**Wenn FEHLER:** Container läuft nicht richtig
**Lösung:** `docker-compose restart`

---

### Test 1.2: API-Key prüfen

```powershell
# .env Datei prüfen
Get-Content .env | Select-String "API_KEY"
```

**Sollte sein:**
```
API_KEY=change_me_to_secure_key_123
```

**Wenn anders:** API-Key stimmt nicht überein!

---

### Test 1.3: NCA Toolkit Test-Endpoint

```powershell
# Direkt NCA Toolkit API testen
$headers = @{
    "x-api-key" = "change_me_to_secure_key_123"
}

Invoke-RestMethod -Uri "http://localhost:8080/v1/toolkit/test" -Headers $headers
```

**Erwartetes Ergebnis:**
```json
{
  "status": "ok",
  "message": "NCA Toolkit is running"
}
```

**Wenn FEHLER:** API-Key falsch oder Container Problem

---

## Level 2: EINFACH - Flask Backend Tests (10 Minuten)

### Test 2.1: Flask Health Check

```powershell
curl http://localhost:5000/api/health
```

**Erwartetes Ergebnis:**
```json
{
  "status": "healthy",
  "nca_toolkit": {
    "status": "healthy" oder "unreachable"
  }
}
```

---

### Test 2.2: Flask → NCA Toolkit Verbindung

```powershell
# Test ob Flask mit NCA Toolkit kommunizieren kann
$body = @{
    message = "Teste die API"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Body $body -ContentType "application/json"
```

**Erwartetes Ergebnis:**
```json
{
  "success": true,
  "intent": {
    "endpoint": "/v1/toolkit/test",
    "confidence": 0.9
  },
  "result": {
    "status": "ok"
  }
}
```

**Wenn FEHLER:**
- Prüfen Sie Flask-Logs
- Prüfen Sie NCA_API_URL in server/.env
- Prüfen Sie NCA_API_KEY in server/.env

---

## Level 3: MITTEL - Konfiguration prüfen (15 Minuten)

### Test 3.1: Alle Umgebungsvariablen prüfen

```powershell
# Root .env
Write-Host "=== ROOT .env ===" -ForegroundColor Cyan
Get-Content .env

# Server .env
Write-Host "`n=== SERVER .env ===" -ForegroundColor Cyan
Get-Content server/.env
```

**Sollte enthalten:**

**Root .env:**
```
API_KEY=change_me_to_secure_key_123
LOCAL_STORAGE_PATH=./data
```

**Server .env:**
```
NCA_API_URL=http://localhost:8080
NCA_API_KEY=change_me_to_secure_key_123
GEMINI_API_KEY=  # Optional
```

---

### Test 3.2: Docker Container Status

```powershell
# Container Status
docker ps --filter "name=nca-toolkit"

# Container Logs (letzte 50 Zeilen)
docker logs nca-toolkit-mcp --tail=50

# Container Health
docker inspect nca-toolkit-mcp --format='{{.State.Health.Status}}'
```

**Erwartetes Ergebnis:**
- Status: `running`
- Health: `healthy`

**Wenn unhealthy:**
```powershell
docker-compose restart
```

---

## Level 4: KOMPLEX - Vollständiger Diagnose-Flow (30 Minuten)

### Test 4.1: End-to-End Test mit Logging

```powershell
# Erstelle Test-Script
$testScript = @'
Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔍 VOLLSTÄNDIGER DIAGNOSE-TEST       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Docker Container
Write-Host "1️⃣  Docker Container Status..." -ForegroundColor Yellow
$containerStatus = docker ps --filter "name=nca-toolkit" --format "{{.Status}}"
Write-Host "   Status: $containerStatus" -ForegroundColor $(if ($containerStatus -like "*Up*") { "Green" } else { "Red" })

# 2. NCA Toolkit direkt
Write-Host "`n2️⃣  NCA Toolkit direkt testen..." -ForegroundColor Yellow
try {
    $ncaTest = Invoke-RestMethod -Uri "http://localhost:8080/" -TimeoutSec 5
    Write-Host "   ✅ NCA Toolkit erreichbar" -ForegroundColor Green
} catch {
    Write-Host "   ❌ NCA Toolkit NICHT erreichbar!" -ForegroundColor Red
    Write-Host "   Fehler: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Flask Backend
Write-Host "`n3️⃣  Flask Backend testen..." -ForegroundColor Yellow
try {
    $flaskHealth = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
    Write-Host "   ✅ Flask erreichbar" -ForegroundColor Green
    Write-Host "   NCA Toolkit Status: $($flaskHealth.nca_toolkit.status)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Flask NICHT erreichbar!" -ForegroundColor Red
}

# 4. API-Keys prüfen
Write-Host "`n4️⃣  API-Keys prüfen..." -ForegroundColor Yellow
$rootKey = (Get-Content .env | Select-String "API_KEY=").ToString().Split("=")[1]
$serverKey = (Get-Content server/.env | Select-String "NCA_API_KEY=").ToString().Split("=")[1]
if ($rootKey -eq $serverKey) {
    Write-Host "   ✅ API-Keys stimmen überein: $rootKey" -ForegroundColor Green
} else {
    Write-Host "   ❌ API-Keys UNTERSCHIEDLICH!" -ForegroundColor Red
    Write-Host "   Root: $rootKey" -ForegroundColor Yellow
    Write-Host "   Server: $serverKey" -ForegroundColor Yellow
}

# 5. End-to-End Test
Write-Host "`n5️⃣  End-to-End Test..." -ForegroundColor Yellow
$body = @{ message = "Teste die API" } | ConvertTo-Json
try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($result.success) {
        Write-Host "   ✅ END-TO-END TEST ERFOLGREICH!" -ForegroundColor Green
        Write-Host "   Intent: $($result.intent.endpoint)" -ForegroundColor Cyan
        Write-Host "   Confidence: $([math]::Round($result.intent.confidence * 100))%" -ForegroundColor Cyan
        
        if ($result.result) {
            Write-Host "`n   📦 ERGEBNIS:" -ForegroundColor Yellow
            $result.result | ConvertTo-Json | Write-Host -ForegroundColor White
        }
    } else {
        Write-Host "   ⚠️  Request nicht erfolgreich" -ForegroundColor Yellow
        Write-Host "   Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ End-to-End Test FEHLGESCHLAGEN!" -ForegroundColor Red
    Write-Host "   Fehler: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ✅ DIAGNOSE ABGESCHLOSSEN             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan
'@

$testScript | Out-File -FilePath "diagnose.ps1" -Encoding UTF8
Write-Host "✅ Diagnose-Script erstellt: diagnose.ps1" -ForegroundColor Green
Write-Host "Führen Sie aus: .\diagnose.ps1" -ForegroundColor Yellow
```

---

## Level 5: EXPERT - Netzwerk & Container Deep-Dive

### Test 5.1: Netzwerk-Verbindungen prüfen

```powershell
# Welche Prozesse nutzen Port 5000 und 8080?
netstat -ano | findstr ":5000"
netstat -ano | findstr ":8080"

# Docker Netzwerk
docker network inspect bridge
```

### Test 5.2: Container-Logs Live

```powershell
# Terminal 1: Flask Logs
cd server
.\venv\Scripts\python.exe app.py

# Terminal 2: Docker Logs
docker logs nca-toolkit-mcp --follow

# Terminal 3: Test ausführen
.\diagnose.ps1
```

---

## 🎯 Empfohlener Workflow

### Schritt 1: Basis-Tests (JETZT!)

```powershell
# 1. NCA Toolkit direkt testen
curl http://localhost:8080/

# 2. Flask Health Check
curl http://localhost:5000/api/health

# 3. API-Keys prüfen
Get-Content .env | Select-String "API_KEY"
Get-Content server/.env | Select-String "NCA_API_KEY"
```

### Schritt 2: Wenn Basis-Tests OK

```powershell
# End-to-End Test
$body = @{ message = "Teste die API" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Body $body -ContentType "application/json"
```

### Schritt 3: Wenn immer noch Probleme

```powershell
# Vollständige Diagnose
.\diagnose.ps1
```

---

## 🔧 Häufige Probleme & Lösungen

### Problem 1: "Connection refused"
**Ursache:** Container läuft nicht  
**Lösung:** `docker-compose up -d`

### Problem 2: "API Key invalid"
**Ursache:** API-Keys stimmen nicht überein  
**Lösung:** Prüfen Sie .env Dateien

### Problem 3: "Timeout"
**Ursache:** NCA Toolkit überlastet  
**Lösung:** `docker-compose restart`

### Problem 4: "No intent found"
**Ursache:** LLM-Fallback funktioniert nicht  
**Lösung:** Prüfen Sie llm_service.py

### Problem 5: Mehrere Server laufen
**Ursache:** Alte Prozesse nicht gestoppt  
**Lösung:**
```powershell
Get-Process python | Where-Object {$_.Path -like "*mcp-nca-toolkit*"} | Stop-Process -Force
```

---

## ✅ Erfolgs-Kriterien

**Minimal:**
- ✅ NCA Toolkit antwortet auf http://localhost:8080/
- ✅ Flask antwortet auf http://localhost:5000/api/health

**Einfach:**
- ✅ End-to-End Test gibt Ergebnis zurück
- ✅ Intent wird erkannt

**Komplett:**
- ✅ Screenshot-Funktion funktioniert
- ✅ Datei-Upload funktioniert
- ✅ Alle 19 Funktionen verfügbar

---

**Nächster Schritt:** Führen Sie die Basis-Tests aus! 🚀
