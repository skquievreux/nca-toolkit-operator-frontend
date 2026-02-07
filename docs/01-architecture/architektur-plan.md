---
title: "Architektur-Plan und Implementierungsstrategie"
type: "architecture"
status: "approved"
last_updated: "2026-02-07"
---

# Architektur-Plan und Implementierungsstrategie

Dieses Dokument beschreibt die technische Architektur des NCA Toolkits, die LLM-Integration sowie den schrittweisen Implementierungsplan.

## 📋 Inhaltsverzeichnis
1. [Problemanalyse](#problemanalyse)
2. [Architektur-Übersicht](#architektur-übersicht)
3. [Dateiverarbeitung](#dateiverarbeitung)
4. [LLM-Integration](#llm-integration)
5. [Parameter-Extraktion](#parameter-extraktion)
6. [Implementierungsplan](#implementierungsplan)
7. [Technologie-Stack](#technologie-stack)

---

## 1. Problemanalyse

### Aktuelle Situation
- ✅ Docker Container läuft (NCA Toolkit API)
- ✅ Python Flask Server läuft
- ✅ Web-Oberfläche funktioniert
- ❌ Keine Datei-Upload-Funktion
- ❌ Keine URL-Extraktion aus Nachrichten
- ❌ Keine LLM-Integration für intelligente Parameter-Extraktion

### Was wir erreichen wollen
**User sagt:** "Füge dieses Video und diese Audiodatei zusammen"
**System macht:**
1. Erkennt die Absicht (Video + Audio zusammenfügen)
2. Akzeptiert Dateien (Upload oder URLs)
3. Lädt Dateien hoch (zu temporärem Storage oder S3)
4. Ruft NCA Toolkit API auf
5. Gibt Ergebnis zurück

---

## 2. Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                     USER (Browser)                           │
│  "Füge Video.mp4 und Audio.mp3 zusammen"                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Web Frontend (HTML/JS)                          │
│  • Datei-Upload (Drag & Drop)                               │
│  • Natürlichsprachliche Eingabe                             │
│  • Preview & Status-Anzeige                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST /api/process
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Flask Backend (Python)                             │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  1. LLM Service (Gemini/OpenAI)              │          │
│  │     • Intent Recognition                      │          │
│  │     • Parameter Extraction                    │          │
│  │     • API Endpoint Selection                  │          │
│  └──────────────────────────────────────────────┘          │
│                     │                                        │
│  ┌──────────────────▼──────────────────────────┐          │
│  │  2. File Handler                             │          │
│  │     • Upload zu temp storage                 │          │
│  │     • Upload zu S3/Cloudflare R2             │          │
│  │     • URL-Generierung                        │          │
│  └──────────────────────────────────────────────┘          │
│                     │                                        │
│  ┌──────────────────▼──────────────────────────┐          │
│  │  3. API Orchestrator                         │          │
│  │     • Request Building                        │          │
│  │     • Error Handling                          │          │
│  │     • Retry Logic                             │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST /v1/video/add/audio
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         NCA Toolkit API (Docker Container)                   │
│  • Video/Audio Processing                                    │
│  • FFmpeg Operations                                         │
│  • Result Storage                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Storage (S3/Local/R2)                           │
│  • Input Files                                               │
│  • Output Files                                              │
│  • Temporary Files                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Dateiverarbeitung

### Option A: Lokaler Temporary Storage (Einfach)
```python
# Dateien temporär speichern
uploads/
  ├── temp_video_abc123.mp4
  └── temp_audio_abc123.mp3

# Über Flask bereitstellen
http://localhost:5000/uploads/temp_video_abc123.mp4
```

**Vorteile:**
- ✅ Einfach zu implementieren
- ✅ Keine externe Abhängigkeit
- ✅ Schnell für Tests

**Nachteile:**
- ❌ Nicht skalierbar
- ❌ Dateien gehen bei Server-Neustart verloren
- ❌ Speicherplatz-Probleme

### Option B: Cloudflare R2 / S3 (Empfohlen)
```python
# Upload zu R2
r2://nca-toolkit-uploads/user123/video_abc123.mp4

# Öffentliche URL generieren
https://uploads.nca-toolkit.com/user123/video_abc123.mp4
```

**Vorteile:**
- ✅ Skalierbar
- ✅ Persistent
- ✅ CDN-Integration
- ✅ Günstig (R2 = $0.015/GB)

**Nachteile:**
- ⚠️ Externe Abhängigkeit
- ⚠️ Konfiguration nötig

### Option C: Hybrid (Best Practice)
```python
# Kleine Dateien (<100MB): Lokal
# Große Dateien (>100MB): R2/S3
# Temporäre Verarbeitung: Lokal
# Finale Ergebnisse: R2/S3
```

---

## 4. LLM-Integration

### Warum LLM?
**Problem:** User sagt "Füge Video und Audio zusammen"
**Ohne LLM:** Wir müssen manuell Keywords matchen
**Mit LLM:** LLM versteht Kontext und extrahiert Parameter

### LLM-Auswahl

| LLM                         | Kosten           | Latenz  | Qualität | Empfehlung       |
| --------------------------- | ---------------- | ------- | -------- | ---------------- |
| **Google Gemini 2.0 Flash** | $0.075/1M tokens | ~500ms  | ⭐⭐⭐⭐⭐    | ✅ **BESTE WAHL** |
| OpenAI GPT-4o mini          | $0.150/1M tokens | ~800ms  | ⭐⭐⭐⭐     | ✅ Gut            |
| Claude 3.5 Haiku            | $0.25/1M tokens  | ~600ms  | ⭐⭐⭐⭐⭐    | ✅ Sehr gut       |
| Lokales LLM (Ollama)        | Kostenlos        | ~2000ms | ⭐⭐⭐      | ⚠️ Langsam        |

**Empfehlung:** **Gemini 2.0 Flash**
- Günstig
- Schnell
- Exzellente Qualität
- Multimodal (kann Bilder/Videos verstehen)
- Kostenlose Quota: 1500 requests/Tag

### LLM-Prompt-Strategie

```python
SYSTEM_PROMPT = """
Du bist ein API-Parameter-Extractor für das NCA Toolkit.

Verfügbare APIs:
- /v1/video/add/audio: Fügt Audio zu Video hinzu
  Parameter: video_url (string), audio_url (string)
  
- /v1/media/transcribe: Transkribiert Audio/Video
  Parameter: media_url (string), language (string, default: "de")
  
- /v1/image/screenshot/webpage: Screenshot einer Webseite
  Parameter: url (string), viewport_width (int), viewport_height (int)

Aufgabe:
1. Erkenne die User-Absicht
2. Wähle den passenden API-Endpunkt
3. Extrahiere Parameter aus der Nachricht
4. Gib JSON zurück

Beispiel:
User: "Füge https://example.com/video.mp4 und https://example.com/audio.mp3 zusammen"

Antwort:
{
  "endpoint": "/v1/video/add/audio",
  "params": {
    "video_url": "https://example.com/video.mp4",
    "audio_url": "https://example.com/audio.mp3"
  },
  "confidence": 0.95
}
"""
```

---

## 5. Parameter-Extraktion

### Strategie 1: LLM-basiert (Empfohlen)
```python
def extract_parameters(user_message, uploaded_files):
    # 1. LLM-Call
    llm_response = gemini.generate({
        "prompt": SYSTEM_PROMPT + f"\n\nUser: {user_message}",
        "response_format": "json"
    })
    
    # 2. Parse Response
    intent = llm_response['endpoint']
    params = llm_response['params']
    
    # 3. Ergänze mit Upload-URLs
    if uploaded_files:
        params['video_url'] = uploaded_files[0].url
        params['audio_url'] = uploaded_files[1].url if len(uploaded_files) > 1 else None
    
    return intent, params
```

### Strategie 2: Hybrid (LLM + Regex)
```python
def extract_parameters_hybrid(user_message, uploaded_files):
    # 1. Regex für URLs
    urls = re.findall(r'https?://[^\s]+', user_message)
    
    # 2. LLM für Intent
    intent = llm_get_intent(user_message)
    
    # 3. Kombiniere
    params = {}
    if intent == '/v1/video/add/audio':
        params['video_url'] = urls[0] if urls else uploaded_files[0].url
        params['audio_url'] = urls[1] if len(urls) > 1 else uploaded_files[1].url
    
    return intent, params
```

### Strategie 3: Rule-based (Fallback)
```python
RULES = {
    'video.*audio.*zusammen': {
        'endpoint': '/v1/video/add/audio',
        'params': ['video_url', 'audio_url']
    },
    'transkript.*video': {
        'endpoint': '/v1/media/transcribe',
        'params': ['media_url', 'language']
    }
}
```

---

## 6. Implementierungsplan

### Phase 1: File Upload (Tag 1-2)
```
✅ Backend:
  - Flask File Upload Endpoint
  - Temporary Storage
  - URL-Generierung
  
✅ Frontend:
  - Drag & Drop UI
  - File Preview
  - Upload Progress
```

### Phase 2: LLM-Integration (Tag 3-4)
```
✅ Backend:
  - Gemini API Integration
  - Prompt Engineering
  - Parameter Extraction
  
✅ Frontend:
  - Loading States
  - Intent Preview
```

### Phase 3: API Orchestration (Tag 5-6)
```
✅ Backend:
  - Request Building
  - Error Handling
  - Webhook Support
  
✅ Frontend:
  - Status Updates
  - Result Display
```

### Phase 4: Storage Integration (Tag 7-8)
```
✅ Backend:
  - Cloudflare R2 Setup
  - Upload zu R2
  - URL-Generierung
  
✅ Deployment:
  - Environment Variables
  - Testing
```

---

## 7. Technologie-Stack

### Backend
```python
# Core
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0

# File Handling
werkzeug==3.0.0
python-magic==0.4.27  # File type detection

# LLM
google-generativeai==0.3.0  # Gemini
# oder
openai==1.0.0  # OpenAI

# Storage
boto3==1.34.0  # S3/R2
cloudflare==2.11.0  # Cloudflare R2

# Utils
python-dotenv==1.0.0
pydantic==2.5.0  # Validation
```

### Frontend
```javascript
// Core
- Vanilla JavaScript (kein Framework nötig)
- Fetch API für Requests

// File Upload
- Dropzone.js oder native Drag & Drop

// UI
- Bestehende CSS (bereits premium!)
```

---

## 8. Detaillierte Implementierung

### 8.1 File Upload Backend

```python
# server/file_handler.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import request, url_for

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'wav', 'avi', 'mov', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_upload(file):
    """Upload file and return URL"""
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid file")
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save file
    file.save(filepath)
    
    # Generate URL
    file_url = url_for('uploaded_file', filename=filename, _external=True)
    
    return {
        'filename': filename,
        'url': file_url,
        'size': os.path.getsize(filepath),
        'type': ext
    }
```

### 8.2 LLM Service

```python
# server/llm_service.py
import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_PROMPT = """[siehe oben]"""

def extract_intent_and_params(user_message, uploaded_files=[]):
    """Use LLM to extract intent and parameters"""
    
    # Build context
    context = f"User message: {user_message}\n"
    if uploaded_files:
        context += f"Uploaded files: {[f['filename'] for f in uploaded_files]}\n"
    
    # Call Gemini
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(
        SYSTEM_PROMPT + "\n\n" + context,
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    
    # Parse response
    result = json.loads(response.text)
    
    # Inject uploaded file URLs
    if uploaded_files:
        if 'video_url' in result['params'] and not result['params']['video_url']:
            video_files = [f for f in uploaded_files if f['type'] in ['mp4', 'avi', 'mov']]
            if video_files:
                result['params']['video_url'] = video_files[0]['url']
        
        if 'audio_url' in result['params'] and not result['params']['audio_url']:
            audio_files = [f for f in uploaded_files if f['type'] in ['mp3', 'wav']]
            if audio_files:
                result['params']['audio_url'] = audio_files[0]['url']
    
    return result
```

### 8.3 Main API Endpoint

```python
# server/app.py (erweitert)
@app.route('/api/process', methods=['POST'])
def process_request():
    """
    Main endpoint: Accepts message + files, processes with LLM, calls NCA API
    """
    try:
        # 1. Get user message
        user_message = request.form.get('message', '')
        
        # 2. Handle file uploads
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                file_info = handle_upload(file)
                uploaded_files.append(file_info)
        
        logger.info(f"Processing: {user_message}")
        logger.info(f"Files: {[f['filename'] for f in uploaded_files]}")
        
        # 3. Extract intent and params with LLM
        llm_result = extract_intent_and_params(user_message, uploaded_files)
        
        endpoint = llm_result['endpoint']
        params = llm_result['params']
        confidence = llm_result.get('confidence', 0.0)
        
        logger.info(f"Intent: {endpoint} (confidence: {confidence})")
        logger.info(f"Params: {json.dumps(params, indent=2)}")
        
        # 4. Call NCA Toolkit API
        nca_response = call_nca_api(endpoint, params)
        
        # 5. Return result
        return jsonify({
            'success': True,
            'intent': {
                'endpoint': endpoint,
                'confidence': confidence
            },
            'params': params,
            'result': nca_response
        })
        
    except Exception as e:
        logger.exception("Error processing request")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def call_nca_api(endpoint, params):
    """Call NCA Toolkit API"""
    url = f"{NCA_API_URL}{endpoint}"
    headers = {
        'x-api-key': NCA_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=params, timeout=300)
    response.raise_for_status()
    
    return response.json()
```

---

## 9. Frontend-Updates

### 9.1 File Upload UI

```javascript
// web/app.js (erweitert)

// File Upload Handler
const fileInput = document.getElementById('fileInput');
const fileAttachments = document.getElementById('fileAttachments');
let uploadedFiles = [];

fileInput.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    
    for (const file of files) {
        // Add to UI
        uploadedFiles.push(file);
        renderFileAttachments();
    }
});

// Send with files
async function handleSendMessage() {
    const message = elements.userInput.value.trim();
    if (!message && uploadedFiles.length === 0) return;
    
    // Create FormData
    const formData = new FormData();
    formData.append('message', message);
    
    uploadedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    // Send to backend
    const response = await fetch('/api/process', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    // Display result
    displayResult(result);
    
    // Clear
    uploadedFiles = [];
    renderFileAttachments();
}
```

---

## 10. Deployment-Checklist

```yaml
✅ Environment Variables:
  - GEMINI_API_KEY
  - NCA_API_KEY
  - NCA_API_URL
  - UPLOAD_FOLDER
  - MAX_FILE_SIZE

✅ Storage:
  - Create uploads/ directory
  - Set permissions
  - Configure R2 (optional)

✅ Dependencies:
  - pip install -r requirements.txt
  - Test Gemini API

✅ Testing:
  - File upload
  - LLM extraction
  - NCA API call
  - End-to-end flow
```

---

## 11. Kosten-Kalkulation

### Gemini API (Empfohlen)
```
Requests pro Tag: 100
Tokens pro Request: ~500
Kosten: 100 * 500 * $0.075 / 1M = $0.00375/Tag
Monat: ~$0.11

Kostenlose Quota: 1500 requests/Tag = ausreichend!
```

### Storage (Cloudflare R2)
```
Upload: 10 GB/Monat
Storage: 10 GB
Kosten: $0.15/Monat

Vergleich S3: $0.23/Monat
```

**Gesamt: ~$0.26/Monat** (mit R2) oder **$0.11/Monat** (nur lokal)

---

## 12. Nächste Schritte

### Sofort (heute):
1. ✅ Gemini API Key besorgen
2. ✅ File Upload implementieren
3. ✅ LLM-Integration testen

### Diese Woche:
4. ✅ End-to-End Flow testen
5. ✅ Error Handling verbessern
6. ✅ UI Polish

### Nächste Woche:
7. ✅ R2 Storage integrieren
8. ✅ Webhook-Support
9. ✅ Production Deployment

---

## 13. Zusammenfassung

### Architektur-Entscheidungen:
- ✅ **LLM**: Gemini 2.0 Flash (günstig, schnell, gut)
- ✅ **Storage**: Hybrid (lokal + R2 für Produktion)
- ✅ **Backend**: Flask (bereits vorhanden)
- ✅ **Frontend**: Vanilla JS (kein Framework nötig)

### Workflow:
```
User Upload → Flask Backend → LLM Extraction → NCA API → Result
```

### Kosten:
- **Entwicklung**: ~$0/Monat (kostenlose Quotas)
- **Produktion**: ~$0.26/Monat

---

**Bereit zum Start?** Soll ich mit der Implementierung beginnen? 🚀
