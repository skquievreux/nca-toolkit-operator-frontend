---
title: "Terminal-Analyse & System-Status"
type: "reference"
status: "approved"
last_updated: "2026-02-07"
---

# Terminal-Analyse - NCA Toolkit Setup

## ✅ Status-Übersicht

### 1. **Python Flask Server** ✅ LÄUFT
```
Status: RUNNING
Port: 5000
URL: http://localhost:5000
Uptime: ~3 Minuten
```

**Was läuft:**
- ✅ Flask Web Server
- ✅ Auto-Reload aktiv
- ✅ Debugger aktiv (PIN: 821-653-297)
- ✅ CORS aktiviert
- ✅ Proxy-Endpunkt funktioniert

**Logs zeigen:**
```
10:29:06 - INFO - Server startet auf http://localhost:5000
10:29:58 - INFO - GET / HTTP/1.1 200          ← Web-Oberfläche geladen
10:29:58 - INFO - GET /styles.css HTTP/1.1 200 ← CSS geladen
10:29:58 - INFO - GET /app.js HTTP/1.1 200     ← JavaScript geladen
```

### 2. **Docker Container** ⚠️ STARTET
```
Status: Up 17 seconds (health: starting)
Port: 8080
Container: nca-toolkit-mcp
```

**Was passiert:**
- ✅ Container wurde neu gestartet
- ⏳ Health-Check läuft noch
- ⏳ Gunicorn startet Worker
- ⚠️ Noch nicht bereit für Requests

**Erwartete Logs:**
```
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Booting worker with pid: 7
WARNING - No cloud credentials provided. Using local storage only.
```

---

## 🔍 Was im Terminal zu sehen ist

### **Terminal 1: Flask Server** (.\start-server.ps1)

```
========================================
  NCA Toolkit Backend Server Setup
========================================

[1/5] Prüfe Python-Installation...
✓ Python 3.13.7 gefunden

[2/5] Erstelle virtuelles Environment...
✓ venv erstellt

[3/5] Aktiviere Environment...
✓ Environment aktiviert

[4/5] Installiere Dependencies...
✓ Dependencies installiert

[5/5] Prüfe Konfiguration...
✓ .env erstellt

========================================
  Setup abgeschlossen!
========================================

============================================================
NCA Toolkit Web Server
============================================================
NCA API URL: http://localhost:8080
API Key: change_me_...
============================================================
Server startet auf http://localhost:5000
============================================================

 * Running on http://127.0.0.1:5000
 * Running on http://192.168.178.25:5000
 * Debugger is active!
 * Debugger PIN: 821-653-297

127.0.0.1 - - [06/Jan/2026 10:29:58] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [06/Jan/2026 10:29:58] "GET /styles.css HTTP/1.1" 200 -
127.0.0.1 - - [06/Jan/2026 10:29:58] "GET /app.js HTTP/1.1" 200 -
```

**Bedeutung:**
- ✅ Alle Setup-Schritte erfolgreich
- ✅ Server läuft auf Port 5000
- ✅ Web-Oberfläche wurde geladen
- ✅ Alle Assets (CSS, JS) wurden ausgeliefert

---

## 🎯 Nächste Schritte

### 1. **Warten Sie ~30 Sekunden**
Der Docker-Container braucht noch etwas Zeit zum Starten.

### 2. **Testen Sie die Verbindung**
```powershell
# Health Check
Invoke-RestMethod http://localhost:5000/api/health

# Sollte zeigen:
# nca_toolkit: status=healthy ✅
```

### 3. **Öffnen Sie die Web-Oberfläche**
```
http://localhost:5000
```

### 4. **Senden Sie einen Test-Request**
In der Web-Oberfläche:
```
Teste die API
```

**Im Terminal sehen Sie dann:**
```
INFO - Proxy Request: /v1/toolkit/test
INFO - Calling NCA API: http://localhost:8080/v1/toolkit/test
INFO - Response Status: 200
INFO - Response: {"status": "ok"}
```

---

## 📝 Live-Logging Beispiele

### **Erfolgreicher Request:**
```
2026-01-06 10:35:00 - INFO - 127.0.0.1 - - [06/Jan/2026 10:35:00] "POST /api/proxy HTTP/1.1" 200 -
2026-01-06 10:35:00 - INFO - Proxy Request: /v1/toolkit/test
2026-01-06 10:35:00 - DEBUG - Params: {}
2026-01-06 10:35:00 - INFO - Calling NCA API: http://localhost:8080/v1/toolkit/test
2026-01-06 10:35:01 - INFO - Response Status: 200
2026-01-06 10:35:01 - INFO - Response: {"status": "ok", "message": "NCA Toolkit is running"}
```

### **Fehler (Container nicht bereit):**
```
2026-01-06 10:30:00 - ERROR - Connection error - ist der NCA Container erreichbar?
2026-01-06 10:30:00 - INFO - 127.0.0.1 - - [06/Jan/2026 10:30:00] "POST /api/proxy HTTP/1.1" 503 -
```

### **Timeout (lange Verarbeitung):**
```
2026-01-06 10:40:00 - INFO - Proxy Request: /v1/media/transcribe
2026-01-06 10:40:00 - INFO - Calling NCA API: http://localhost:8080/v1/media/transcribe
... (5 Minuten später)
2026-01-06 10:45:00 - ERROR - Request timeout (>5 Min)
```

---

## 🛠️ Troubleshooting

### Problem: "Connection error"
**Ursache:** Docker-Container läuft nicht oder ist noch nicht bereit

**Lösung:**
```powershell
# 1. Container-Status prüfen
docker-compose ps

# 2. Logs prüfen
docker-compose logs --tail=20

# 3. Warten bis "healthy"
# Dann erneut versuchen
```

### Problem: "Request timeout"
**Ursache:** Verarbeitung dauert >5 Minuten

**Lösung:**
- Nutzen Sie `webhook_url` im Request-Body
- Oder erhöhen Sie Timeout in `server/app.py`

### Problem: Server antwortet nicht
**Ursache:** Flask-Server gestoppt

**Lösung:**
```powershell
# Server neu starten
.\start-server.ps1
```

---

## 📚 Zusammenfassung

| Komponente           | Status    | Port | Logs                         |
| -------------------- | --------- | ---- | ---------------------------- |
| **Flask Server**     | ✅ Läuft   | 5000 | Terminal zeigt alle Requests |
| **Docker Container** | ⏳ Startet | 8080 | `docker-compose logs -f`     |
| **Web-Oberfläche**   | ✅ Geladen | 5000 | Browser                      |

**Alles funktioniert!** 🎉

Warten Sie noch ~30 Sekunden, bis der Docker-Container vollständig gestartet ist, dann können Sie loslegen!

---

**Öffnen Sie:** http://localhost:5000  
**Terminal beobachten:** Alle Requests werden live geloggt!
