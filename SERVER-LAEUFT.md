# 🎉 Python Backend Server läuft!

## ✅ Status

Der **Flask Backend Server** ist erfolgreich gestartet!

```
✓ Python 3.13.7
✓ Virtuelles Environment erstellt
✓ Dependencies installiert
✓ Server läuft auf http://localhost:5000
```

---

## 🌐 Web-Oberfläche öffnen

### Option 1: Im Browser
```
http://localhost:5000
```

### Option 2: PowerShell
```powershell
start http://localhost:5000
```

---

## 📊 Live-Logs

Der Server zeigt **automatisch alle Requests** im Terminal an:

```
2026-01-06 10:29:06 - INFO - Server startet auf http://localhost:5000
2026-01-06 10:29:06 - INFO - NCA API URL: http://localhost:8080
```

**Wenn Sie einen Request senden, sehen Sie:**
```
2026-01-06 10:30:00 - INFO - Proxy Request: /v1/toolkit/test
2026-01-06 10:30:00 - INFO - Calling NCA API: http://localhost:8080/v1/toolkit/test
2026-01-06 10:30:01 - INFO - Response Status: 200
2026-01-06 10:30:01 - INFO - Response: {"status": "ok"}
```

---

## 🎯 Vorteile des Python-Servers

### ✅ Was jetzt besser ist:

1. **Live-Logging**: Alle Requests werden im Terminal angezeigt
2. **Error Handling**: Bessere Fehlermeldungen
3. **Timeout Handling**: 5 Minuten Timeout für lange Prozesse
4. **CORS Support**: Keine Browser-Probleme mehr
5. **Health Checks**: `/api/health` Endpunkt
6. **Proxy-Funktion**: Saubere Trennung Frontend/Backend

### 🔍 Debug-Modus aktiv

- **Auto-Reload**: Code-Änderungen werden automatisch geladen
- **Debugger**: Bei Fehlern wird der Debugger aktiviert
- **Detaillierte Logs**: Alle Requests/Responses werden geloggt

---

## 🚀 Verwendung

### 1. Web-Oberfläche nutzen

Öffnen Sie: **http://localhost:5000**

Die Web-Oberfläche kommuniziert jetzt mit dem Python-Backend!

### 2. API direkt testen

```powershell
# Health Check
Invoke-RestMethod http://localhost:5000/api/health

# Verfügbare Endpunkte
Invoke-RestMethod http://localhost:5000/api/endpoints

# Test-Request
$body = @{
    endpoint = "/v1/toolkit/test"
    params = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/proxy -Method POST -Body $body -ContentType "application/json"
```

---

## 📝 Live-Logs beobachten

### Das Terminal zeigt automatisch:

✅ **Alle eingehenden Requests**
```
INFO - Proxy Request: /v1/media/transcribe
```

✅ **API-Calls zum NCA Toolkit**
```
INFO - Calling NCA API: http://localhost:8080/v1/media/transcribe
```

✅ **Responses**
```
INFO - Response Status: 200
INFO - Response: {"output_url": "..."}
```

✅ **Fehler**
```
ERROR - API Error: 401 - Unauthorized
ERROR - Connection error - ist der NCA Container erreichbar?
```

---

## 🛠️ Server-Verwaltung

### Server läuft im aktuellen Terminal

- **Stoppen**: `Strg+C`
- **Neu starten**: `.\start-server.ps1`
- **Logs**: Werden automatisch im Terminal angezeigt

### Manuell starten

```powershell
cd server
.\venv\Scripts\Activate.ps1
python app.py
```

---

## 🔧 Konfiguration

### API-Key ändern

Bearbeiten Sie `server\.env`:
```env
NCA_API_KEY=ihr_neuer_api_key
```

Dann Server neu starten.

### NCA Toolkit URL ändern

Falls der Container auf einem anderen Port läuft:
```env
NCA_API_URL=http://localhost:8081
```

---

## 🎬 Beispiel: Request mit Live-Logs

### 1. Terminal beobachten
Das Terminal mit dem laufenden Server zeigt automatisch alle Logs.

### 2. Request senden
Öffnen Sie http://localhost:5000 und senden Sie einen Request.

### 3. Logs erscheinen automatisch
```
2026-01-06 10:30:00 - INFO - 127.0.0.1 - - [06/Jan/2026 10:30:00] "POST /api/proxy HTTP/1.1" 200 -
2026-01-06 10:30:00 - INFO - Proxy Request: /v1/toolkit/test
2026-01-06 10:30:00 - DEBUG - Params: {}
2026-01-06 10:30:00 - INFO - Calling NCA API: http://localhost:8080/v1/toolkit/test
2026-01-06 10:30:01 - INFO - Response Status: 200
2026-01-06 10:30:01 - INFO - Response: {"status": "ok", "message": "NCA Toolkit is running"}
```

---

## 🆘 Troubleshooting

### Server startet nicht

**Fehler**: `Python nicht gefunden`
```powershell
# Python installieren von python.org
# Dann erneut versuchen
.\start-server.ps1
```

**Fehler**: `Port 5000 bereits belegt`
```powershell
# Anderen Port verwenden
# In server/app.py ändern: port=5001
```

### NCA Toolkit nicht erreichbar

**Logs zeigen**: `Connection error`
```powershell
# 1. Prüfe ob Container läuft
docker-compose ps

# 2. Starte Container falls nötig
docker-compose up -d

# 3. Teste direkt
Invoke-WebRequest http://localhost:8080
```

### Requests hängen

**Timeout nach 5 Minuten**
- Das ist normal für lange Prozesse
- Nutzen Sie `webhook_url` für sehr lange Prozesse
- Logs zeigen: `Request timeout (>5 Min)`

---

## 📚 Weitere Informationen

- **Backend-Dokumentation**: `server/README.md`
- **Web-Interface**: `web/README.md`
- **API-Referenz**: `API-QUICK-START.md`
- **Monitoring**: `MONITORING-GUIDE.md`

---

## 🎉 Fertig!

Sie haben jetzt:
- ✅ Docker Container (NCA Toolkit API)
- ✅ Python Backend Server (Flask)
- ✅ Web-Oberfläche mit AI
- ✅ **Live-Logging im Terminal!**

**Öffnen Sie http://localhost:5000 und legen Sie los!** 🚀

---

**Server läuft auf**: http://localhost:5000  
**API läuft auf**: http://localhost:8080  
**Debugger PIN**: 821-653-297
