# 🔍 Wo Sie ALLE Details sehen können

## Option 1: Live-Logs im Frontend (EMPFOHLEN!)

**Klicken Sie auf das 📄 Icon** oben rechts im Header!

**Was Sie dort sehen:**
```
12:04:21 ℹ️ 📨 Sende Request: "Teste die API"
12:04:21 ℹ️ 📎 Datei 1: video.mp4 (5.66MB, video/mp4)
12:04:21 ℹ️ 🚀 Rufe Backend auf: http://localhost:5000/api/process
12:04:22 ✅ 📡 Response Status: 200 (1.2s)
12:04:22 ✅ ✅ Request erfolgreich! (1.2s)
12:04:22 ℹ️ 🆔 Job-ID: abc-123-def
12:04:22 ℹ️ 🎯 Intent: /v1/toolkit/test (Confidence: 90%)
12:04:22 ℹ️ 💭 Reasoning: Fallback: Test-Endpunkt erkannt
12:04:22 ℹ️ 📋 Parameter: {
  "test": true
}
12:04:22 ✅ 📁 1 Datei(en) hochgeladen:
12:04:22 ℹ️   • video.mp4 (5.66MB) → http://localhost:5000/uploads/abc123.mp4
12:04:22 ✅ 📦 Ergebnis erhalten:
12:04:22 ℹ️ {
  "status": "ok",
  "message": "NCA Toolkit is running"
}
```

---

## Option 2: Backend-Terminal

**Schauen Sie in das Terminal** wo `pnpm run dev` läuft!

**Was Sie dort sehen:**
```
2026-01-06 12:04:21 - INFO - ============================================================
2026-01-06 12:04:21 - INFO - 📨 New Request: Teste die API (Job: abc-123-def)
2026-01-06 12:04:21 - INFO - 📁 Files received: 1
2026-01-06 12:04:21 - INFO - ✅ Uploaded: video.mp4 (5.66MB)
2026-01-06 12:04:21 - INFO -    Saved as: abc123.mp4
2026-01-06 12:04:21 - INFO -    URL: http://localhost:5000/uploads/abc123.mp4
2026-01-06 12:04:21 - INFO - 🤖 Calling LLM for intent extraction...
2026-01-06 12:04:21 - WARNING - Kein GEMINI_API_KEY - nutze Fallback
2026-01-06 12:04:21 - INFO - 🎯 Intent: /v1/toolkit/test (confidence: 0.9)
2026-01-06 12:04:21 - INFO - 💭 Reasoning: Fallback: Test-Endpunkt erkannt
2026-01-06 12:04:21 - INFO - 📋 Params: {
  "test": true
}
2026-01-06 12:04:21 - INFO - 🚀 Calling NCA API: /v1/toolkit/test
2026-01-06 12:04:22 - INFO - ✅ Request completed successfully
2026-01-06 12:04:22 - INFO - ============================================================
```

---

## Option 3: Browser DevTools Console

**Drücken Sie F12** und öffnen Sie die Console!

**Was Sie dort sehen:**
```javascript
[INFO] 📨 Sende Request: "Teste die API"
[INFO] 📎 Datei 1: video.mp4 (5.66MB, video/mp4)
[INFO] 🚀 Rufe Backend auf: http://localhost:5000/api/process
[SUCCESS] 📡 Response Status: 200 (1.2s)
[SUCCESS] ✅ Request erfolgreich! (1.2s)
[INFO] 🆔 Job-ID: abc-123-def
[INFO] 🎯 Intent: /v1/toolkit/test (Confidence: 90%)
...
```

---

## 🎯 BESTE Option: Live-Logs im Frontend!

**Schritt 1:** Klicken Sie auf **📄 Icon** (oben rechts)  
**Schritt 2:** Sehen Sie ALLE Details in Echtzeit!  
**Schritt 3:** Logs bleiben gespeichert (letzte 100 Einträge)

---

## Was Sie jetzt sehen werden:

### ✅ Erfolgreicher Request:
```
✅ Request erfolgreich! (1.2s)
🆔 Job-ID: abc-123
🎯 Intent: /v1/toolkit/test (90%)
📦 Ergebnis: { "status": "ok" }
```

### ❌ Fehler:
```
❌ Fehler: Connection timeout
📡 Response Status: 500 (300s)
```

### 📁 Datei-Upload:
```
📎 Datei 1: video.mp4 (5.66MB, video/mp4)
📁 1 Datei(en) hochgeladen:
  • video.mp4 (5.66MB) → http://localhost:5000/uploads/abc123.mp4
```

---

**Jetzt haben Sie ALLE Informationen!** 🎉

**Testen Sie es:**
1. Laden Sie die Seite neu (F5)
2. Klicken Sie auf **📄 Icon**
3. Senden Sie einen Request
4. **Sehen Sie ALLE Details!**
