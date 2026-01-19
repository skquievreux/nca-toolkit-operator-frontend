# 🚀 Server Quick Start

**Einfacher Server-Start ohne Probleme**

## Option 1: Direkt aus dem Root-Verzeichnis

```powershell
# Im Root-Verzeichnis (C:\CODE\GIT\MCP-NCA-TOOLKIT)
.\start-server.ps1
```

## Option 2: Manuell (wenn Skript Probleme macht)

```powershell
# 1. Ins server/ Verzeichnis wechseln
cd server

# 2. Server starten
.\venv\Scripts\python.exe app.py
```

## Option 3: Mit pnpm (empfohlen für Development)

```powershell
# Im Root-Verzeichnis
pnpm run dev
```

## Fehlerbehebung

### Problem: "Cannot find path 'server\server'"

**Ursache:** Skript wird aus falschem Verzeichnis aufgerufen

**Lösung:**
```powershell
# Stelle sicher, dass du im Root-Verzeichnis bist
cd C:\CODE\GIT\MCP-NCA-TOOLKIT

# Dann starte
.\start-server.ps1
```

### Problem: ".env nicht gefunden"

**Lösung:**
```powershell
# Kopiere .env.example zu .env
cp .env.example .env
cp .env.example server\.env

# Oder verwende Standard-Konfiguration (Skript macht das automatisch)
```

### Problem: "Server startet nicht"

**Lösung:**
```powershell
# 1. Prüfe ob Python-Umgebung aktiviert ist
cd server
.\venv\Scripts\Activate.ps1

# 2. Installiere Dependencies
pip install -r requirements.txt

# 3. Starte manuell
python app.py
```

## Server-Status prüfen

```powershell
# Prüfe ob Server läuft
curl http://localhost:5000/api/health

# Prüfe laufende Python-Prozesse
Get-Process python
```

## Server stoppen

```powershell
# Finde Python-Prozesse
Get-Process python | Where-Object { $_.Path -like "*mcp-nca-toolkit*" }

# Stoppe alle
Get-Process python | Where-Object { $_.Path -like "*mcp-nca-toolkit*" } | Stop-Process -Force
```

## Logs ansehen

```powershell
# Production Logs (Warnings & Errors)
tail -f logs/nca-server.log

# Debug Logs (wenn DEBUG=true)
tail -f logs/debug.log

# Oder mit PowerShell
Get-Content logs/nca-server.log -Wait -Tail 50
```

## Konfiguration

### Environment Variables (.env)

```bash
# Logging
LOG_LEVEL=WARNING    # DEBUG, INFO, WARNING, ERROR
DEBUG=false          # true für verbose Logging

# NCA API
NCA_API_URL=http://localhost:8080
NCA_API_KEY=343534sfklsjf343423

# Gemini (optional)
GEMINI_API_KEY=your_key_here
```

## Schnellstart nach Änderungen

```powershell
# 1. Server stoppen (Ctrl+C oder Fenster schließen)

# 2. Neu starten
cd C:\CODE\GIT\MCP-NCA-TOOLKIT
.\start-server.ps1

# Oder manuell:
cd server
python app.py
```

---

**Tipp:** Für Development empfehle ich den manuellen Start (`python app.py`), da Sie dann direkt die Logs sehen und einfacher debuggen können.
