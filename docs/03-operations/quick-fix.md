# 🚨 QUICK FIX - Frontend funktioniert nicht

## Problem
Die Logs zeigen:
```
11:32:51 🚀 Rufe Backend auf: http://localhost:8080/api/process
```

**FALSCH!** Es sollte `http://localhost:5000/api/process` sein!

## Lösung

### 1. Browser-Cache leeren
```
1. Drücken Sie F12 (Developer Tools)
2. Rechtsklick auf Reload-Button
3. Wählen Sie "Empty Cache and Hard Reload"
```

### 2. Oder: LocalStorage löschen
```javascript
// In Browser Console (F12):
localStorage.clear();
location.reload();
```

### 3. Oder: Einstellungen ändern
```
1. Klicken Sie auf ⚙️ Icon
2. Ändern Sie API URL zu: http://localhost:5000
3. Speichern
4. Seite neu laden (F5)
```

---

## Was dann passiert:

### Im Frontend (Live-Logs):
```
11:35:00 ℹ️ 📨 Sende Request: "Füge diese zusammen"
11:35:00 ℹ️ 📎 Datei hinzugefügt: video.mp4 (5.66MB)
11:35:00 ℹ️ 📎 Datei hinzugefügt: audio.mp3 (0.11MB)
11:35:00 ℹ️ 🚀 Rufe Backend auf: http://localhost:5000/api/process  ← RICHTIG!
11:35:01 ℹ️ 📡 Response Status: 200
11:35:01 ✅ ✅ Request erfolgreich!
11:35:01 ℹ️ 🎯 Intent: /v1/video/add/audio (Confidence: 0.7)
```

### Im Backend-Terminal:
```
2026-01-06 11:35:00 - INFO - ============================================================
2026-01-06 11:35:00 - INFO - 📨 New Request: Füge diese zusammen
2026-01-06 11:35:00 - INFO - 📁 Files received: 2
2026-01-06 11:35:00 - INFO - ✅ Uploaded: video.mp4 (5.66MB)
2026-01-06 11:35:00 - INFO - ✅ Uploaded: audio.mp4 (0.11MB)
2026-01-06 11:35:00 - INFO - 🤖 Calling LLM for intent extraction...
2026-01-06 11:35:00 - WARNING - Kein GEMINI_API_KEY - nutze Fallback
2026-01-06 11:35:00 - INFO - 🎯 Intent: /v1/video/add/audio (confidence: 0.7)
2026-01-06 11:35:00 - INFO - 💭 Reasoning: Fallback: Keyword-Matching für Video+Audio
2026-01-06 11:35:00 - INFO - 📋 Params: {
  "video_url": "http://localhost:5000/uploads/abc123.mp4",
  "audio_url": "http://localhost:5000/uploads/def456.mp3"
}
2026-01-06 11:35:00 - INFO - 🚀 Calling NCA API: /v1/video/add/audio
2026-01-06 11:35:30 - INFO - ✅ Request completed successfully
2026-01-06 11:35:30 - INFO - ============================================================
```

### Im Frontend (Ergebnis):
```
✅ Anfrage erfolgreich verarbeitet!

🎯 Intent erkannt
   Endpoint: /v1/video/add/audio
   Confidence: 70%
   Reasoning: Fallback: Keyword-Matching für Video+Audio

Parameter:
{
  "video_url": "http://localhost:5000/uploads/abc123.mp4",
  "audio_url": "http://localhost:5000/uploads/def456.mp3"
}

✅ Ergebnis:
{
  "output_url": "https://storage.example.com/result.mp4",
  "job_id": "abc-123-def"
}
```

---

## Wie Sie die fertige Datei erhalten:

### Option 1: Download-Link im Ergebnis
```
Das Ergebnis enthält:
{
  "output_url": "https://..."  ← Klicken Sie hier!
}
```

### Option 2: Job-ID für Webhook
```
Wenn es lange dauert:
{
  "job_id": "abc-123",
  "status": "processing",
  "webhook_url": "..."
}

Dann später:
GET /v1/job/abc-123/status
→ { "status": "completed", "output_url": "..." }
```

### Option 3: Lokaler Download
```
Wenn LOCAL_STORAGE_PATH gesetzt ist:
{
  "output_url": "file:///tmp/result.mp4"
}

Dann im data/ Ordner:
C:\CODE\GIT\MCP-NCA-TOOLKIT\data\result.mp4
```

---

## Schnelltest (ohne Frontend):

```powershell
# 1. Testdateien erstellen
"test" | Out-File test.txt

# 2. Request senden
$form = @{
    message = "Füge diese zusammen"
    files = Get-Item "test.txt"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Form $form
```

---

## Nächste Schritte:

1. **Browser neu laden** (F5 oder Strg+F5)
2. **Dateien erneut hochladen**
3. **Request senden**
4. **Live-Logs beobachten** (📄 Icon)
5. **Ergebnis-URL kopieren**

**Dann haben Sie Ihre fertige Datei!** 🎉
