# 🔧 NCA Toolkit - Troubleshooting & Doku

## Problem: "Netzwerk-Fehler: Der Container konnte das Ergebnis nicht zurücksenden"

Wenn Sie diese Fehlermeldung sehen, hat die Videobearbeitung im Container funktioniert, aber der Container **kann das Ergebnis nicht an das Backend zurücksenden**.

Dies liegt fast immer an der **Windows Firewall**, die eingehende Verbindungen auf Port 5000 (standardmäßig) blockiert, auch wenn sie vom lokalen Docker-Netzwerk kommen.

### ✅ Lösung: Port 5000 freigeben

Führen Sie folgenden Befehl in einer **PowerShell als Administrator** aus:

```powershell
New-NetFirewallRule -DisplayName "NCA Toolkit Backend" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

Starten Sie danach das Backend neu.

---

## 📚 API Dokumentation

Die vollständige API Dokumentation ist verfügbar unter:
URL: http://localhost:5000/docs.html

Dort finden Sie alle Endpoints, Beispiele und können Logs kopieren.
