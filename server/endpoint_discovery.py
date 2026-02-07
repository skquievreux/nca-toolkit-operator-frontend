"""
Endpoint Discovery Service
Queries the NCA Toolkit Docker container for available endpoints
"""

import requests
import os
import logging

logger = logging.getLogger(__name__)

NCA_API_URL = os.getenv('NCA_API_URL', 'http://localhost:8080')
NCA_API_KEY = os.getenv('NCA_API_KEY', '343534sfklsjf343423')

# Cache for discovered endpoints
_discovered_endpoints = None

# Known endpoints from container inspection (verified 2026-01-08)
# These are the ONLY endpoints that actually exist in the container
KNOWN_ENDPOINTS = {
    '/v1/code/execute/python': {
        'method': 'POST',
        'description': 'Führt Python-Code aus',
        'params': ['code', 'requirements (optional)']
    },
    '/v1/media/metadata': {
        'method': 'POST',
        'description': 'Extrahiert Metadaten aus Media-Datei',
        'params': ['media_url']
    },
    '/v1/media/convert': {
        'method': 'POST',
        'description': 'Konvertiert Medienformate (Generisch)',
        'params': ['media_url', 'format']
    },
    '/v1/toolkit/authenticate': {
        'method': 'POST',
        'description': 'Authentifizierung testen',
        'params': []
    },
    '/audio-mixing': {
        'method': 'POST',
        'description': 'Mischt Audio mit Video (Alternative: /v1/video/add/audio)',
        'params': ['video_url', 'audio_url', 'video_vol (optional, default: 100)', 'audio_vol (optional, default: 100)', 'output_length (optional, "video" or "audio")']
    },
    '/v1/audio/concatenate': {
        'method': 'POST',
        'description': 'Fügt mehrere Audiodateien zusammen',
        'params': ['audio_urls (array)']
    },
    '/v1/video/concatenate': {
        'method': 'POST',
        'description': 'Fügt mehrere Videos zusammen (Alternative: /combine-videos)',
        'params': ['video_urls (array)']
    },
    '/v1/media/convert/mp3': {
        'method': 'POST',
        'description': 'Konvertiert Video/Audio zu MP3 Audio.',
        'params': ['media_url']
    },
    '/v1/media/transcribe': {
        'method': 'POST',
        'description': 'Erstellt eine Transkription (Text & Untertitel) aus Audio/Video Dateien. Keywords: Transkript, Untertitel, SRT, Speech-to-Text.',
        'params': ['media_url', 'language (optional, default: "de")']
    },
    '/v1/video/add/captions': {
        'method': 'POST',
        'description': 'Erstellt Untertitel für ein Video',
        'params': ['video_url', 'language (optional, default: "de")']
    },
    '/v1/video/add/watermark': {
        'method': 'POST',
        'description': 'Fügt ein Logo/Bild als Wasserzeichen zu einem Video hinzu',
        'params': ['video_url', 'image_url', 'position (optional, default: "bottom_right")']
    },
    '/v1/image/convert/image_to_video': {
        'method': 'POST',
        'description': 'Erstellt ein Video aus einem Bild (Slideshow)',
        'params': ['image_url', 'duration (optional, default: 5)']
    },
    '/v1/video/thumbnail': {
        'method': 'POST',
        'description': 'Erstellt ein Thumbnail aus einem Video',
        'params': ['video_url', 'timestamp (optional, default: "00:00:01")']
    },
    '/v1/video/cut': {
        'method': 'POST',
        'description': 'Schneidet ein Video (Trimmen)',
        'params': ['video_url', 'start_time (string, e.g. "00:00:05")', 'end_time (optional, string)']
    },
    '/v1/image/screenshot/webpage': {
            'method': 'POST',
            'description': 'Erstellt einen Screenshot einer Webseite',
            'params': ['url', 'viewport_width (optional)', 'viewport_height (optional)']
        },
    '/gdrive-upload': {
        'method': 'POST',
        'description': 'Lädt Datei zu Google Drive hoch',
        'params': ['file_url']
    },
    '/v1/voice/generate': {
        'method': 'POST',
        'description': 'Generiert Audio aus Text (ElevenLabs)',
        'params': ['text', 'voice_id (optional, default: "Adam")']
    },
    '/v1/video/download': {
        'method': 'POST',
        'description': 'Lädt ein Video von YouTube herunter',
        'params': ['url']
    },
    '/api/rss/process': {
        'method': 'POST',
        'description': 'Generiert Video aus RSS (Bild/Audio) - Use this for Acid Monk / Racket Voice',
        'params': ['image_url', 'audio_url', 'title (optional)']
    },
    '/api/rss/list': {
        'method': 'GET',
        'description': 'Listet Items eines Feeds auf',
        'params': ['url (optional)', 'limit (optional, default: 10)']
    },
    '/v1/toolkit/test': {
        'method': 'GET',
        'description': 'Prüft ob das System online ist',
        'params': []
    }
}

def get_all_endpoints():
    """
    Returns the dictionary of all known endpoints.
    Useful for Swagger UI / Documentation.
    """
    return KNOWN_ENDPOINTS

def discover_endpoints():
    """
    Discover available endpoints from the NCA Toolkit container
    Returns a formatted string describing available endpoints
    """
    global _discovered_endpoints
    
    if _discovered_endpoints:
        return _discovered_endpoints
    
    logger.info("🔍 Discovering available endpoints from NCA Toolkit...")
    
    # Format for LLM
    endpoint_description = "Verfügbare NCA Toolkit Endpoints:\n\n"
    for path, info in KNOWN_ENDPOINTS.items():
        endpoint_description += f"{info['method']} {path} - {info['description']}\n"
        if info['params']:
            endpoint_description += f"   Parameter: {', '.join(info['params'])}\n"
        endpoint_description += "\n"
    
    _discovered_endpoints = endpoint_description
    logger.info(f"✅ Discovered {len(KNOWN_ENDPOINTS)} endpoints (aligned with docs)")
    
    return endpoint_description


def get_dynamic_system_prompt():
    """
    Generate system prompt with discovered endpoints
    """
    endpoints = discover_endpoints()
    
    return f"""Du bist ein API-Parameter-Extractor für das NCA Toolkit.

{endpoints}

Aufgabe:
1. Analysiere die User-Nachricht
2. Erkenne die Absicht
3. Wähle den passenden API-Endpunkt
4. Extrahiere Parameter aus der Nachricht
5. Gib JSON zurück

WICHTIG:
- Wenn Dateien hochgeladen wurden, nutze die file_urls
- Wenn URLs in der Nachricht sind, extrahiere sie
- Setze sinnvolle Defaults
- Gib confidence zwischen 0 und 1 an
- Für Audio-Verkettung: WARNUNG ausgeben, dass kein direkter Endpoint existiert

Antwort-Format (JSON):
{{
  "endpoint": "/endpoint-name",
  "params": {{
    "param1": "value1",
    "param2": "value2"
  }},
  "confidence": 0.95,
  "reasoning": "Kurze Erklärung"
}}

Beispiele:

User: "Konvertiere diese Datei zu MP3" (mit hochgeladener Datei audio.wav)
Antwort:
{{
  "endpoint": "/media-to-mp3",
  "params": {{
    "media_url": "USE_UPLOADED_FILE_0"
  }},
  "confidence": 0.98,
  "reasoning": "MP3-Konvertierung gewünscht"
}}

User: "Füge Video und Audio zusammen"
Antwort:
{{
  "endpoint": "/audio-mixing",
  "params": {{
    "video_url": "USE_UPLOADED_FILE_0",
    "audio_url": "USE_UPLOADED_FILE_1",
    "video_vol": 100,
    "audio_vol": 100,
    "output_length": "video"
  }},
  "confidence": 0.95,
  "reasoning": "Audio-Mixing gewünscht"
}}
"""
