# 🚀 NCA Toolkit Backend Server

## Setup

### 1. Virtuelles Environment erstellen
```powershell
cd server
python -m venv venv
```

### 2. Environment aktivieren
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Dependencies installieren
```powershell
pip install -r requirements.txt
```

### 4. Konfiguration
```powershell
# .env.example nach .env kopieren
Copy-Item .env.example .env

# .env bearbeiten und API-Key anpassen
```

### 5. Server starten
```powershell
python app.py
```

Server läuft auf: **http://localhost:5000**

## Endpoints

### Frontend
- `GET /` - Web-Oberfläche

### API
- `GET /api/endpoints` - Alle verfügbaren Endpunkte
- `POST /api/proxy` - Proxy zu NCA Toolkit API
- `GET /api/health` - Health Check
- `GET /api/logs` - Log-Einträge

## Verwendung

### Proxy Request
```json
POST /api/proxy
{
  "endpoint": "/v1/toolkit/test",
  "params": {}
}
```

### Response
```json
{
  "success": true,
  "data": {
    "status": "ok"
  }
}
```

## Features

- ✅ Proxy zu NCA Toolkit API
- ✅ Error Handling
- ✅ Request/Response Logging
- ✅ CORS Support
- ✅ Health Checks
- ✅ Timeout Handling (5 Min)

## Logs

Der Server loggt alle Requests und Responses:
```
2026-01-06 10:00:00 - INFO - Proxy Request: /v1/toolkit/test
2026-01-06 10:00:01 - INFO - Response Status: 200
```
