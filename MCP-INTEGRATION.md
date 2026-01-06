# MCP-Server-Integration für NCA Toolkit

## Übersicht

Diese Anleitung zeigt, wie Sie das **No-Code Architects Toolkit** als MCP (Model Context Protocol) Server in verschiedenen Clients nutzen können.

## Was ist MCP?

MCP (Model Context Protocol) ist ein offener Standard, der es KI-Assistenten ermöglicht, sicher mit externen Tools und Datenquellen zu kommunizieren. Es funktioniert wie ein "universeller USB-C-Port für KI".

## Voraussetzungen

✅ Docker Desktop läuft  
✅ NCA Toolkit Container ist gestartet (`docker-compose up -d`)  
✅ API ist erreichbar unter `http://localhost:8080`

## Option 1: HTTP-API-Zugriff (Empfohlen)

Die einfachste Methode ist die direkte Nutzung der HTTP-API:

### Für Claude Desktop

Erstellen Sie ein MCP-Server-Wrapper-Skript:

**`nca-mcp-server.ps1`**:
```powershell
# NCA Toolkit MCP Server Wrapper
$API_KEY = "change_me_to_secure_key_123"
$API_BASE = "http://localhost:8080"

# Lese Eingabe von stdin
$input = [Console]::In.ReadToEnd()

# Parse JSON-Request
$request = $input | ConvertFrom-Json

# Forwarde Request an NCA Toolkit API
$headers = @{
    "x-api-key" = $API_KEY
    "Content-Type" = "application/json"
}

$endpoint = $request.endpoint
$body = $request.body | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$API_BASE$endpoint" -Method POST -Headers $headers -Body $body
    $response | ConvertTo-Json -Depth 10
} catch {
    @{
        error = $_.Exception.Message
        status = "failed"
    } | ConvertTo-Json
}
```

### Claude Desktop Konfiguration

Fügen Sie in `%APPDATA%\Claude\claude_desktop_config.json` hinzu:

```json
{
  "mcpServers": {
    "nca-toolkit": {
      "command": "powershell.exe",
      "args": [
        "-ExecutionPolicy", "Bypass",
        "-File", "C:\\CODE\\GIT\\MCP-NCA-TOOLKIT\\nca-mcp-server.ps1"
      ],
      "env": {
        "API_KEY": "change_me_to_secure_key_123"
      }
    }
  }
}
```

## Option 2: Docker Exec (Direkt)

Für direkten Zugriff auf den Container:

```json
{
  "mcpServers": {
    "nca-toolkit": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "nca-toolkit-mcp",
        "python",
        "-m",
        "flask",
        "run",
        "--host=0.0.0.0"
      ],
      "env": {
        "API_KEY": "change_me_to_secure_key_123"
      }
    }
  }
}
```

## Option 3: HTTP-Proxy (Für andere MCP-Clients)

Nutzen Sie die API direkt über HTTP-Requests:

### Python-Beispiel

```python
import requests
import json

class NCAToolkitMCP:
    def __init__(self, api_key, base_url="http://localhost:8080"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"x-api-key": api_key}
    
    def call_endpoint(self, endpoint, payload):
        """Ruft einen NCA Toolkit Endpunkt auf"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()
    
    def execute_python(self, code):
        """Führt Python-Code aus"""
        return self.call_endpoint("/v1/code/execute/python", {"code": code})
    
    def transcribe_media(self, media_url, language="de"):
        """Transkribiert Audio/Video"""
        return self.call_endpoint("/v1/media/transcribe", {
            "media_url": media_url,
            "language": language
        })
    
    def convert_to_mp3(self, media_url):
        """Konvertiert Medien zu MP3"""
        return self.call_endpoint("/v1/media/convert/mp3", {
            "media_url": media_url
        })

# Verwendung
mcp = NCAToolkitMCP(api_key="change_me_to_secure_key_123")
result = mcp.execute_python("print('Hello from MCP!')")
print(result)
```

### Node.js-Beispiel

```javascript
const axios = require('axios');

class NCAToolkitMCP {
  constructor(apiKey, baseUrl = 'http://localhost:8080') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.headers = { 'x-api-key': apiKey };
  }

  async callEndpoint(endpoint, payload) {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await axios.post(url, payload, { headers: this.headers });
    return response.data;
  }

  async executePython(code) {
    return this.callEndpoint('/v1/code/execute/python', { code });
  }

  async transcribeMedia(mediaUrl, language = 'de') {
    return this.callEndpoint('/v1/media/transcribe', {
      media_url: mediaUrl,
      language
    });
  }
}

// Verwendung
const mcp = new NCAToolkitMCP('change_me_to_secure_key_123');
mcp.executePython("print('Hello from MCP!')").then(console.log);
```

## Verfügbare Funktionen

### 🎵 Audio
- `concatenate` - Audio-Dateien zusammenfügen

### 💻 Code
- `execute/python` - Python-Code ausführen

### 🎬 FFmpeg
- `compose` - Komplexe Medienverarbeitung

### 🖼️ Image
- `convert/video` - Bild zu Video
- `screenshot/webpage` - Webseiten-Screenshot

### 📹 Media
- `convert` - Format-Konvertierung
- `convert/mp3` - MP3-Konvertierung
- `download` - Medien herunterladen
- `transcribe` - Transkription
- `silence` - Stille erkennen
- `metadata` - Metadaten extrahieren

### 🎥 Video
- `add/audio` - Audio hinzufügen
- `add/captions` - Untertitel hinzufügen
- `add/watermark` - Wasserzeichen
- `clip` - Clips erstellen
- `concatenate` - Videos zusammenfügen
- `generate/captions` - Untertitel generieren
- `overlay` - Overlay
- `resize` - Größe ändern
- `reverse` - Umkehren
- `rotate` - Rotieren
- `speed` - Geschwindigkeit
- `split/scenes` - Szenen aufteilen
- `thumbnail` - Thumbnails

### ☁️ S3
- `upload` - S3-Upload

## Verwendungsbeispiele

### 1. Python-Code ausführen

```json
{
  "endpoint": "/v1/code/execute/python",
  "body": {
    "code": "import math\nresult = math.sqrt(16)\nprint(f'Square root: {result}')"
  }
}
```

### 2. Video transkribieren

```json
{
  "endpoint": "/v1/media/transcribe",
  "body": {
    "media_url": "https://example.com/video.mp4",
    "language": "de"
  }
}
```

### 3. Webseiten-Screenshot

```json
{
  "endpoint": "/v1/image/screenshot/webpage",
  "body": {
    "url": "https://example.com",
    "viewport_width": 1920,
    "viewport_height": 1080
  }
}
```

## Sicherheit

⚠️ **WICHTIG**: 
- Ändern Sie `API_KEY` in `.env` vor Produktionsnutzung
- Exponieren Sie den Container NICHT direkt ins Internet
- Nutzen Sie für Produktion einen Reverse Proxy (nginx, Traefik)
- Aktivieren Sie HTTPS für externe Zugriffe

## Troubleshooting

### MCP-Server verbindet nicht

1. **Container läuft?**
   ```powershell
   docker-compose ps
   ```

2. **API erreichbar?**
   ```powershell
   Invoke-WebRequest http://localhost:8080/v1/toolkit/test
   ```

3. **Logs prüfen**
   ```powershell
   docker-compose logs -f
   ```

### API-Key-Fehler

Stellen Sie sicher, dass der API-Key in:
- `.env` Datei
- MCP-Konfiguration
- Request-Headers

identisch ist.

### Timeout-Probleme

Für lange Prozesse (>1 Min):
- Nutzen Sie `webhook_url` im Request-Body
- Erhöhen Sie `GUNICORN_TIMEOUT` in `.env`

## Weiterführende Links

- **API-Dokumentation**: https://github.com/stephengpope/no-code-architects-toolkit/tree/main/docs
- **Postman Collection**: https://bit.ly/49Gkh61
- **NCA Toolkit GPT**: https://bit.ly/4feDDk4
- **MCP Specification**: https://modelcontextprotocol.io

## Support

Bei Fragen:
1. Prüfen Sie die [Dokumentation](https://github.com/stephengpope/no-code-architects-toolkit/tree/main/docs)
2. Erstellen Sie ein [GitHub Issue](https://github.com/stephengpope/no-code-architects-toolkit/issues)
3. Kontaktieren Sie die No-Code Architects Community
