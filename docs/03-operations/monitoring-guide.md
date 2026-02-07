---
title: "Docker Monitoring & Debugging Guide"
type: "operations"
status: "approved"
last_updated: "2026-02-07"
---

# Docker Monitoring & Debugging Guide

## Übersicht

Dieser Guide zeigt Ihnen, wie Sie die Aktivitäten im NCA Toolkit Container überwachen und Probleme debuggen können.

---

## 📊 Live-Logs anzeigen

### 1. Alle Logs in Echtzeit
```powershell
docker-compose logs -f
```
- `-f` = follow (bleibt offen und zeigt neue Logs)
- `Strg+C` zum Beenden

### 2. Nur die letzten 50 Zeilen
```powershell
docker-compose logs --tail=50
```

### 3. Logs mit Zeitstempel
```powershell
docker-compose logs -f --timestamps
```

### 4. Logs seit bestimmter Zeit
```powershell
# Letzte 5 Minuten
docker-compose logs --since 5m

# Seit heute 9:00
docker-compose logs --since 2026-01-06T09:00:00
```

---

## 🎯 Spezifische Container-Logs

### Nur NCA Toolkit Logs
```powershell
docker-compose logs -f nca-toolkit
```

### Mit Farben und besser lesbar
```powershell
docker logs nca-toolkit-mcp -f --tail=100
```

---

## 🔴 Live-Monitoring während API-Aufrufen

### Terminal 1: Logs beobachten
```powershell
docker-compose logs -f
```

### Terminal 2: API-Request senden
```powershell
$headers = @{"x-api-key" = "change_me_to_secure_key_123"}
Invoke-RestMethod -Uri "http://localhost:8080/v1/toolkit/test" -Method POST -Headers $headers
```

**Sie sehen dann in Terminal 1:**
```
nca-toolkit-mcp  | [2026-01-06 09:00:00] INFO - Request received: POST /v1/toolkit/test
nca-toolkit-mcp  | [2026-01-06 09:00:00] INFO - Processing request...
nca-toolkit-mcp  | [2026-01-06 09:00:01] INFO - Request completed successfully
```

---

## 🐚 Interaktive Shell im Container

### 1. Bash-Shell öffnen
```powershell
docker exec -it nca-toolkit-mcp /bin/bash
```

Dann im Container:
```bash
# Prozesse anzeigen
ps aux

# Speicherplatz prüfen
df -h

# Logs direkt lesen
tail -f /var/log/*.log

# Python-Version prüfen
python --version

# Installierte Pakete
pip list

# Exit
exit
```

### 2. Einzelne Befehle ausführen
```powershell
# Python-Version
docker exec nca-toolkit-mcp python --version

# Prozesse
docker exec nca-toolkit-mcp ps aux

# Speicher
docker exec nca-toolkit-mcp df -h

# Netzwerk-Test
docker exec nca-toolkit-mcp curl http://localhost:8080
```

---

## 📈 Container-Status & Ressourcen

### 1. Container-Status
```powershell
docker-compose ps
```

**Ausgabe:**
```
NAME              STATUS                     PORTS
nca-toolkit-mcp   Up 15 minutes (healthy)    0.0.0.0:8080->8080/tcp
```

### 2. Ressourcen-Nutzung (Live)
```powershell
docker stats nca-toolkit-mcp
```

**Zeigt:**
- CPU-Auslastung
- Speicher-Nutzung
- Netzwerk I/O
- Disk I/O

**Ausgabe-Beispiel:**
```
CONTAINER         CPU %     MEM USAGE / LIMIT     MEM %     NET I/O
nca-toolkit-mcp   2.5%      512MB / 8GB          6.4%      1.2MB / 850KB
```

### 3. Detaillierte Container-Infos
```powershell
docker inspect nca-toolkit-mcp
```

Oder spezifische Infos:
```powershell
# Status
docker inspect nca-toolkit-mcp --format='{{.State.Status}}'

# Health
docker inspect nca-toolkit-mcp --format='{{.State.Health.Status}}'

# IP-Adresse
docker inspect nca-toolkit-mcp --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```

---

## 🔍 Logs nach Fehlern durchsuchen

### 1. Nur Fehler anzeigen
```powershell
docker-compose logs | Select-String "ERROR"
```

### 2. Warnungen finden
```powershell
docker-compose logs | Select-String "WARNING"
```

### 3. Bestimmte Requests finden
```powershell
docker-compose logs | Select-String "POST /v1/media/transcribe"
```

### 4. Logs in Datei speichern
```powershell
docker-compose logs > logs_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt
```

---

## 🎬 Praktisches Beispiel: API-Request überwachen

### Schritt 1: Logs-Terminal öffnen
```powershell
# Terminal 1
docker-compose logs -f --tail=20
```

### Schritt 2: API-Request senden
```powershell
# Terminal 2
$headers = @{
    "x-api-key" = "change_me_to_secure_key_123"
    "Content-Type" = "application/json"
}

$body = @{
    code = "print('Hello from NCA Toolkit!')"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/v1/code/execute/python" -Method POST -Headers $headers -Body $body
```

### Schritt 3: Logs beobachten
**Sie sehen:**
```
nca-toolkit-mcp  | [2026-01-06 10:00:00] INFO - Request: POST /v1/code/execute/python
nca-toolkit-mcp  | [2026-01-06 10:00:00] INFO - Executing Python code...
nca-toolkit-mcp  | [2026-01-06 10:00:00] INFO - Output: Hello from NCA Toolkit!
nca-toolkit-mcp  | [2026-01-06 10:00:01] INFO - Request completed
```

---

## 🚨 Troubleshooting-Befehle

### Container startet nicht
```powershell
# Fehler beim Start anzeigen
docker-compose up

# Logs vom letzten Start
docker-compose logs --tail=100
```

### Container läuft, aber API antwortet nicht
```powershell
# 1. Container-Status prüfen
docker-compose ps

# 2. Logs prüfen
docker-compose logs --tail=50

# 3. Health-Check
docker inspect nca-toolkit-mcp --format='{{.State.Health.Status}}'

# 4. Port-Binding prüfen
docker port nca-toolkit-mcp
```

### Hohe CPU/Speicher-Nutzung
```powershell
# Ressourcen überwachen
docker stats nca-toolkit-mcp

# Prozesse im Container
docker exec nca-toolkit-mcp ps aux

# Worker-Prozesse prüfen
docker exec nca-toolkit-mcp ps aux | Select-String "gunicorn"
```

### Netzwerk-Probleme
```powershell
# Container-IP
docker inspect nca-toolkit-mcp --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# Netzwerk testen (von außen)
Test-NetConnection localhost -Port 8080

# Netzwerk testen (im Container)
docker exec nca-toolkit-mcp curl http://localhost:8080
```

---

## 📊 Monitoring-Dashboard (Optional)

### PowerShell-Monitoring-Skript erstellen

**`monitor.ps1`**:
```powershell
# NCA Toolkit Monitoring Dashboard
while ($true) {
    Clear-Host
    Write-Host "=== NCA Toolkit Monitoring ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Container Status
    Write-Host "Container Status:" -ForegroundColor Yellow
    docker-compose ps
    Write-Host ""
    
    # Ressourcen
    Write-Host "Ressourcen:" -ForegroundColor Yellow
    docker stats nca-toolkit-mcp --no-stream
    Write-Host ""
    
    # Letzte Logs
    Write-Host "Letzte 5 Log-Einträge:" -ForegroundColor Yellow
    docker-compose logs --tail=5
    Write-Host ""
    
    Write-Host "Aktualisiert: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    Write-Host "Drücken Sie Strg+C zum Beenden"
    
    Start-Sleep -Seconds 5
}
```

**Ausführen:**
```powershell
.\monitor.ps1
```

---

## 🔧 Erweiterte Debugging-Techniken

### 1. Gunicorn Worker-Logs
```powershell
docker exec nca-toolkit-mcp cat /var/log/gunicorn/*.log
```

### 2. Python-Fehler traceback
```powershell
docker-compose logs | Select-String "Traceback" -Context 10
```

### 3. Request-Timing analysieren
```powershell
docker-compose logs | Select-String "Request completed" | Select-String -Pattern "\d+ms"
```

### 4. Aktive Verbindungen
```powershell
docker exec nca-toolkit-mcp netstat -an | Select-String "8080"
```

---

## 📝 Log-Level ändern (Optional)

### Temporär mehr Logs aktivieren

**In `.env` hinzufügen:**
```env
LOG_LEVEL=DEBUG
```

**Container neu starten:**
```powershell
docker-compose restart
```

**Logs werden jetzt detaillierter:**
```
DEBUG - Request headers: {...}
DEBUG - Request body: {...}
DEBUG - Processing step 1...
DEBUG - Processing step 2...
INFO - Request completed
```

---

## 🎯 Quick Reference

| Befehl                                      | Beschreibung       |
| ------------------------------------------- | ------------------ |
| `docker-compose logs -f`                    | Live-Logs anzeigen |
| `docker-compose logs --tail=50`             | Letzte 50 Zeilen   |
| `docker stats nca-toolkit-mcp`              | Ressourcen-Nutzung |
| `docker exec -it nca-toolkit-mcp /bin/bash` | Shell öffnen       |
| `docker-compose ps`                         | Container-Status   |
| `docker inspect nca-toolkit-mcp`            | Detaillierte Infos |

---

## 💡 Best Practices

1. **Immer Logs beobachten** beim Testen neuer Features
2. **Logs regelmäßig speichern** für Debugging
3. **Ressourcen überwachen** bei intensiver Nutzung
4. **Health-Checks prüfen** bei Problemen
5. **Logs durchsuchen** statt alles zu lesen

---

## 🆘 Häufige Log-Meldungen

### ✅ Normale Meldungen
```
INFO - Starting gunicorn
INFO - Listening at: http://0.0.0.0:8080
INFO - Booting worker with pid: 7
INFO - Request completed successfully
```

### ⚠️ Warnungen
```
WARNING - No cloud credentials provided. Using local storage only.
WARNING - Worker timeout (pid:123)
```

### ❌ Fehler
```
ERROR - Worker (pid:123) exited with code 255
ERROR - Exception in worker process
ERROR - API request failed: 401 Unauthorized
```

---

**Viel Erfolg beim Monitoring!** 🚀

Für weitere Fragen siehe `INSTALLATION-ERFOLG.md` oder die Online-Dokumentation.
