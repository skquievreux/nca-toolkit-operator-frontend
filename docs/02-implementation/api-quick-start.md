# 🚀 NCA Toolkit API - Quick Start Guide

## ✅ Status

**Container läuft!** 🎉
- **URL**: http://localhost:8080
- **API Key**: `change_me_to_secure_key_123` (in `.env` ändern!)

## 📋 Verfügbare API-Endpunkte

### 🔧 Toolkit (Basis-Funktionen)
- `POST /v1/toolkit/test` - API-Test
- `POST /v1/toolkit/authenticate` - API-Key validieren
- `GET /v1/toolkit/job/status` - Job-Status abrufen
- `GET /v1/toolkit/jobs/status` - Alle Jobs abrufen

### 🎵 Audio
- `POST /v1/audio/concatenate` - Mehrere Audiodateien zusammenfügen

### 💻 Code
- `POST /v1/code/execute/python` - Python-Code remote ausführen

### 🎬 FFmpeg
- `POST /v1/ffmpeg/compose` - Komplexe Medienverarbeitung mit FFmpeg

### 🖼️ Image
- `POST /v1/image/convert/video` - Bild zu Video konvertieren
- `POST /v1/image/screenshot/webpage` - Webseiten-Screenshot erstellen

### 📹 Media
- `POST /v1/media/convert` - Medienformate konvertieren
- `POST /v1/media/convert/mp3` - Zu MP3 konvertieren
- `POST /v1/BETA/media/download` - Medien von URLs herunterladen (yt-dlp)
- `POST /v1/media/transcribe` - Audio/Video transkribieren
- `POST /v1/media/silence` - Stille-Intervalle erkennen
- `POST /v1/media/metadata` - Medien-Metadaten extrahieren
- `GET /v1/media/feedback` - Feedback-Interface

### ☁️ S3
- `POST /v1/s3/upload` - Dateien zu S3 hochladen

### 🎥 Video
- `POST /v1/video/add/audio` - Audio zu Video hinzufügen
- `POST /v1/video/add/captions` - Untertitel zu Video hinzufügen
- `POST /v1/video/add/watermark` - Wasserzeichen hinzufügen
- `POST /v1/video/clip` - Video-Clips erstellen
- `POST /v1/video/concatenate` - Videos zusammenfügen
- `POST /v1/video/generate/captions` - Untertitel generieren
- `POST /v1/video/overlay` - Videos überlagern
- `POST /v1/video/resize` - Video-Größe ändern
- `POST /v1/video/reverse` - Video umkehren
- `POST /v1/video/rotate` - Video rotieren
- `POST /v1/video/speed` - Video-Geschwindigkeit ändern
- `POST /v1/video/split/scenes` - Video in Szenen aufteilen
- `POST /v1/video/thumbnail` - Thumbnails generieren

## 🧪 API testen

### 1. Mit PowerShell (einfacher Test)

```powershell
# Test-Endpunkt
$headers = @{
    "x-api-key" = "change_me_to_secure_key_123"
}

Invoke-RestMethod -Uri "http://localhost:8080/v1/toolkit/test" -Method POST -Headers $headers
```

### 2. Mit Postman

1. **Postman Template importieren**: [Download Template](https://bit.ly/49Gkh61)
2. **Environment Variables setzen**:
   - `base_url`: `http://localhost:8080`
   - `x-api-key`: `change_me_to_secure_key_123`
3. **Requests testen**

### 3. Mit cURL

```bash
# Test-Endpunkt
curl -X POST http://localhost:8080/v1/toolkit/test \
  -H "x-api-key: change_me_to_secure_key_123"

# Authentifizierung testen
curl -X POST http://localhost:8080/v1/toolkit/authenticate \
  -H "x-api-key: change_me_to_secure_key_123"
```

### 4. Python-Beispiel

```python
import requests

API_URL = "http://localhost:8080"
API_KEY = "change_me_to_secure_key_123"

headers = {
    "x-api-key": API_KEY
}

# Test-Endpunkt
response = requests.post(f"{API_URL}/v1/toolkit/test", headers=headers)
print(response.json())

# Python-Code ausführen
payload = {
    "code": "print('Hello from NCA Toolkit!')\nresult = 2 + 2\nprint(f'Result: {result}')"
}
response = requests.post(
    f"{API_URL}/v1/code/execute/python",
    headers=headers,
    json=payload
)
print(response.json())
```

## 📚 Detaillierte Dokumentation

Jeder Endpunkt hat eine ausführliche Dokumentation:
- [Audio Concatenate](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/audio/concatenate.md)
- [Python Execute](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/code/execute/execute_python.md)
- [FFmpeg Compose](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/ffmpeg/ffmpeg_compose.md)
- [Weitere Docs...](https://github.com/stephengpope/no-code-architects-toolkit/tree/main/docs)

## 🤖 NCA Toolkit GPT

Nutzen Sie den **[NCA Toolkit API GPT](https://bit.ly/4feDDk4)** für:
- Beispiel-Requests generieren
- API-Features erkunden
- Troubleshooting

## 🔐 Sicherheit

**WICHTIG**: Ändern Sie den API-Key in `.env`:

```env
API_KEY=ihr_sicherer_produktions_key_hier
```

Dann Container neu starten:
```powershell
docker-compose restart
```

## 🛠️ Container-Verwaltung

```powershell
# Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs -f

# Neu starten
docker-compose restart

# Stoppen
docker-compose down

# Starten
docker-compose up -d
```

## 💡 Tipps

1. **Webhook URLs**: Für lange Prozesse (>1 Min) nutzen Sie `webhook_url` im Request
2. **Performance**: Passen Sie `GUNICORN_WORKERS` in `.env` an Ihre CPU an
3. **Storage**: Für Produktion S3 oder GCP Storage konfigurieren
4. **Monitoring**: Logs mit `docker-compose logs -f` überwachen

## 🆘 Troubleshooting

### Container startet nicht
```powershell
docker-compose logs nca-toolkit
```

### API antwortet nicht
```powershell
# Container-Status prüfen
docker-compose ps

# Health-Check
docker inspect nca-toolkit-mcp | Select-String "Health"
```

### Port bereits belegt
In `.env` ändern:
```env
HOST_PORT=8081
```

## 📖 Weitere Ressourcen

- **GitHub**: https://github.com/stephengpope/no-code-architects-toolkit
- **Community**: No-Code Architects Community
- **Issues**: https://github.com/stephengpope/no-code-architects-toolkit/issues
