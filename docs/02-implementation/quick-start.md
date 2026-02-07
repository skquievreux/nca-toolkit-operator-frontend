---
title: "Quick Start Guide"
type: "implementation"
status: "approved"
last_updated: "2026-02-07"
---

# Quick Start Guide

## Einfacher Server-Start (wie `pnpm run dev`)

### Option 1: NPM-Style Commands
```powershell
# Server starten
npm run dev

# Docker starten
npm run docker:start

# Logs ansehen
npm run docker:logs

# Health Check
npm run test
```

### Option 2: PowerShell-Alias
```powershell
# Einmalig in PowerShell Profile einfügen:
# notepad $PROFILE

function nca-dev { cd C:\CODE\GIT\MCP-NCA-TOOLKIT; npm run dev }
function nca-logs { docker logs nca-toolkit-mcp --follow }
function nca-restart { docker-compose restart }

# Dann einfach:
nca-dev
nca-logs
```

### Option 3: Batch-Datei
```batch
@echo off
cd /d C:\CODE\GIT\MCP-NCA-TOOLKIT\server
python app.py
```
Speichern als `start-dev.bat` und doppelklicken!

---

## 🧪 Schneller Funktionstest

### Test 1: API Health Check (SOFORT!)
```powershell
curl http://localhost:5000/api/health
```

**Erwartet:**
```json
{
  "status": "healthy",
  "nca_toolkit": {
    "status": "healthy"
  }
}
```

### Test 2: NCA Toolkit Test (5 Sekunden)
**Im Frontend:**
```
"Teste die API"
```

**Oder PowerShell:**
```powershell
$body = @{ message = "Teste die API" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Body $body -ContentType "application/json"
```

### Test 3: Screenshot (30 Sekunden)
**Im Frontend:**
```
"Screenshot von https://example.com"
```

**Ergebnis:** Screenshot-URL zum Download!

---

## 📚 Feature-Beispiele für Frontend

### Schnelle Tests (< 30 Sekunden):
1. ✅ "Teste die API" → Toolkit-Test
2. ✅ "Screenshot von https://github.com" → Webseiten-Screenshot  
3. ✅ "Metadaten von [Video]" → Video-Info

### Mittlere Tests (30-60 Sekunden):
4. "Konvertiere zu MP3" + [Video] → MP3-Konvertierung
5. "Erstelle Thumbnail" + [Video] → Thumbnail
6. "Transkribiere" + [Audio] → Speech-to-Text

### Lange Tests (1-3 Minuten):
7. "Füge zusammen" + [Video, Audio] → Video mit Audio
8. "Füge zusammen" + [Video1, Video2] → Video-Concatenation
9. "Ändere Größe auf 1280x720" + [Video] → Video-Resize

---

## 🔧 Timeout-Problem beheben

### Problem:
```
Read timed out. (read timeout=300)
```

### Lösung 1: Timeout erhöht (DONE!)
```python
# In app.py: timeout=600 (10 Minuten)
```

### Lösung 2: Docker Container neu starten
```powershell
docker-compose restart
```

### Lösung 3: Kleinere Dateien testen
- Verwenden Sie Videos < 10MB
- Oder nutzen Sie schnelle Funktionen (Screenshot, Test)

---

## ✅ Proof of Concept - Funktionierender Test

### Schritt 1: Server starten
```powershell
npm run dev
```

### Schritt 2: Frontend öffnen
```
http://localhost:5000
```

### Schritt 3: Schnelltest
```
Eingabe: "Teste die API"
Klick: Senden
```

### Schritt 4: Ergebnis
```json
{
  "success": true,
  "intent": {
    "endpoint": "/v1/toolkit/test",
    "confidence": 0.9
  },
  "result": {
    "status": "ok",
    "message": "NCA Toolkit is running"
  }
}
```

**✅ FUNKTIONIERT = Proof of Concept erfolgreich!**

---

## 📊 Alle verfügbaren Befehle

```powershell
# Development
npm run dev              # Server starten
npm run install          # Dependencies installieren

# Docker
npm run docker:start     # Docker starten
npm run docker:stop      # Docker stoppen
npm run docker:restart   # Docker neu starten
npm run docker:logs      # Docker Logs live

# Testing
npm run test             # Health Check
```

---

**Jetzt testen Sie:** `npm run dev` 🚀
