# 📚 NCA Toolkit - Alle verfügbaren Funktionen

**Version:** 1.0.0  
**Quelle:** [stephengpope/no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit)

---

## 🎵 Audio-Funktionen

### `/v1/audio/concatenate`
**Beschreibung:** Kombiniert mehrere Audiodateien zu einer einzigen  
**Parameter:**
- `audio_urls` (array) - Liste von Audio-URLs

**Beispiel:**
```json
{
  "audio_urls": [
    "https://example.com/audio1.mp3",
    "https://example.com/audio2.mp3"
  ]
}
```

---

## 💻 Code-Ausführung

### `/v1/code/execute/python`
**Beschreibung:** Führt Python-Code in einer sicheren Sandbox aus  
**Parameter:**
- `code` (string) - Python-Code zum Ausführen

**Beispiel:**
```json
{
  "code": "print('Hello World')\nresult = 2 + 2\nprint(result)"
}
```

---

## 🎬 FFmpeg-Operationen

### `/v1/ffmpeg/execute`
**Beschreibung:** Führt benutzerdefinierte FFmpeg-Befehle aus  
**Parameter:**
- `command` (string) - FFmpeg-Befehl
- `input_url` (string) - Input-Datei-URL

---

## 🖼️ Bild-Funktionen

### `/v1/image/convert/video`
**Beschreibung:** Konvertiert ein Bild zu einem Video  
**Parameter:**
- `image_url` (string) - Bild-URL
- `duration` (number) - Video-Dauer in Sekunden
- `zoom` (boolean, optional) - Ken Burns Zoom-Effekt

**Beispiel:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "duration": 5,
  "zoom": true
}
```

### `/v1/image/screenshot/webpage`
**Beschreibung:** Erstellt einen Screenshot einer Webseite  
**Parameter:**
- `url` (string) - Webseiten-URL
- `viewport_width` (number, default: 1920) - Breite
- `viewport_height` (number, default: 1080) - Höhe

**Beispiel:**
```json
{
  "url": "https://github.com",
  "viewport_width": 1920,
  "viewport_height": 1080
}
```

---

## 📁 Media-Funktionen

### `/v1/media/convert`
**Beschreibung:** Konvertiert Medien zwischen verschiedenen Formaten  
**Parameter:**
- `media_url` (string) - Media-URL
- `output_format` (string) - Zielformat (mp4, webm, avi, etc.)

**Beispiel:**
```json
{
  "media_url": "https://example.com/video.avi",
  "output_format": "mp4"
}
```

### `/v1/media/convert/mp3`
**Beschreibung:** Konvertiert Audio/Video zu MP3  
**Parameter:**
- `media_url` (string) - Media-URL

**Beispiel:**
```json
{
  "media_url": "https://example.com/video.mp4"
}
```

### `/v1/media/transcribe`
**Beschreibung:** Transkribiert Audio/Video zu Text (Speech-to-Text)  
**Parameter:**
- `media_url` (string) - Media-URL
- `language` (string, optional) - Sprache (de, en, etc.)

**Beispiel:**
```json
{
  "media_url": "https://example.com/audio.mp3",
  "language": "de"
}
```

### `/v1/media/metadata`
**Beschreibung:** Extrahiert Metadaten aus Media-Dateien  
**Parameter:**
- `media_url` (string) - Media-URL

**Beispiel:**
```json
{
  "media_url": "https://example.com/video.mp4"
}
```

**Response:**
```json
{
  "duration": 120.5,
  "width": 1920,
  "height": 1080,
  "codec": "h264",
  "bitrate": 5000000
}
```

---

## 🎥 Video-Funktionen

### `/v1/video/add/audio`
**Beschreibung:** Fügt Audio zu einem Video hinzu  
**Parameter:**
- `video_url` (string) - Video-URL
- `audio_url` (string) - Audio-URL

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "audio_url": "https://example.com/audio.mp3"
}
```

### `/v1/video/add/captions`
**Beschreibung:** Fügt Untertitel zu einem Video hinzu  
**Parameter:**
- `video_url` (string) - Video-URL
- `captions` (array) - Untertitel-Daten

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "captions": [
    {"start": 0, "end": 5, "text": "Hallo Welt"},
    {"start": 5, "end": 10, "text": "Wie geht es dir?"}
  ]
}
```

### `/v1/video/add/watermark`
**Beschreibung:** Fügt ein Wasserzeichen zu einem Video hinzu  
**Parameter:**
- `video_url` (string) - Video-URL
- `watermark_url` (string) - Wasserzeichen-Bild-URL
- `position` (string) - Position (top-left, top-right, bottom-left, bottom-right, center)
- `opacity` (number, 0-1) - Transparenz

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "watermark_url": "https://example.com/logo.png",
  "position": "bottom-right",
  "opacity": 0.7
}
```

### `/v1/video/concatenate`
**Beschreibung:** Fügt mehrere Videos zusammen  
**Parameter:**
- `video_urls` (array) - Liste von Video-URLs

**Beispiel:**
```json
{
  "video_urls": [
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4",
    "https://example.com/video3.mp4"
  ]
}
```

### `/v1/video/resize`
**Beschreibung:** Ändert die Größe eines Videos  
**Parameter:**
- `video_url` (string) - Video-URL
- `width` (number) - Neue Breite
- `height` (number) - Neue Höhe

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "width": 1280,
  "height": 720
}
```

### `/v1/video/thumbnail`
**Beschreibung:** Erstellt ein Thumbnail aus einem Video  
**Parameter:**
- `video_url` (string) - Video-URL
- `timestamp` (number, optional) - Zeitpunkt in Sekunden

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "timestamp": 5
}
```

### `/v1/video/trim`
**Beschreibung:** Schneidet ein Video zu  
**Parameter:**
- `video_url` (string) - Video-URL
- `start` (number) - Start-Zeit in Sekunden
- `end` (number) - End-Zeit in Sekunden

**Beispiel:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "start": 10,
  "end": 30
}
```

---

## ☁️ S3/Storage-Funktionen

### `/v1/s3/upload`
**Beschreibung:** Lädt eine Datei zu S3/Cloud Storage hoch  
**Parameter:**
- `file_url` (string) - Datei-URL
- `bucket` (string, optional) - Bucket-Name
- `key` (string, optional) - Datei-Pfad

**Beispiel:**
```json
{
  "file_url": "https://example.com/file.mp4",
  "bucket": "my-bucket",
  "key": "videos/output.mp4"
}
```

### `/v1/s3/presigned-url`
**Beschreibung:** Generiert eine Pre-Signed URL für Upload  
**Parameter:**
- `bucket` (string) - Bucket-Name
- `key` (string) - Datei-Pfad
- `expires` (number, optional) - Gültigkeit in Sekunden

---

## 🛠️ Toolkit-Funktionen

### `/v1/toolkit/test`
**Beschreibung:** Testet die API-Verbindung  
**Parameter:** Keine

**Response:**
```json
{
  "status": "ok",
  "message": "NCA Toolkit is running",
  "version": "1.0.0"
}
```

### `/v1/toolkit/authenticate`
**Beschreibung:** Testet die Authentifizierung  
**Parameter:** Keine (API-Key im Header)

---

## 📊 Verwendung in der Web-Oberfläche

### Natürlichsprachliche Befehle:

| Befehl                          | Funktion                       | Beispiel                          |
| ------------------------------- | ------------------------------ | --------------------------------- |
| "Füge Video und Audio zusammen" | `/v1/video/add/audio`          | Drag & Drop: video.mp4, audio.mp3 |
| "Transkribiere dieses Video"    | `/v1/media/transcribe`         | Drag & Drop: video.mp4            |
| "Screenshot von https://..."    | `/v1/image/screenshot/webpage` | Text mit URL                      |
| "Konvertiere zu MP3"            | `/v1/media/convert/mp3`        | Drag & Drop: video.mp4            |
| "Erstelle Thumbnail"            | `/v1/video/thumbnail`          | Drag & Drop: video.mp4            |
| "Füge Wasserzeichen hinzu"      | `/v1/video/add/watermark`      | Drag & Drop: video.mp4, logo.png  |

---

## 🎯 Häufig genutzte Workflows

### 1. Video mit Audio erstellen
```
1. Drag & Drop: video.mp4, audio.mp3
2. "Füge diese zusammen"
3. ✅ Ergebnis: video_with_audio.mp4
```

### 2. Video transkribieren
```
1. Drag & Drop: video.mp4
2. "Transkribiere auf Deutsch"
3. ✅ Ergebnis: Transkript-Text
```

### 3. Webseite als Video
```
1. "Screenshot von https://github.com"
2. ✅ Ergebnis: screenshot.png
3. "Konvertiere zu Video"
4. ✅ Ergebnis: screenshot.mp4
```

### 4. Video-Collage
```
1. Drag & Drop: video1.mp4, video2.mp4, video3.mp4
2. "Füge diese Videos zusammen"
3. ✅ Ergebnis: combined.mp4
```

---

## 🔐 Authentifizierung

Alle Requests benötigen einen API-Key im Header:
```
x-api-key: your_api_key_here
```

**Standard-Key:** `change_me_to_secure_key_123`  
**⚠️ WICHTIG:** Ändern Sie diesen in `.env`!

---

## 📝 Response-Format

### Erfolg:
```json
{
  "output_url": "https://storage.../result.mp4",
  "job_id": "abc-123-def",
  "duration": 45.2,
  "size": 6234567,
  "metadata": {
    "width": 1920,
    "height": 1080,
    "codec": "h264"
  }
}
```

### Fehler:
```json
{
  "error": "Invalid input",
  "details": "Video URL is required",
  "code": 400
}
```

---

## 🚀 Weitere Informationen

- **GitHub:** https://github.com/stephengpope/no-code-architects-toolkit
- **Dokumentation:** `docs/` Ordner im Repository
- **API-Test:** `http://localhost:8080/` (Swagger UI)

---

**Alle Funktionen sind über die Web-Oberfläche nutzbar!** 🎉

Nutzen Sie einfach natürlichsprachliche Befehle oder Drag & Drop.
