"""
LLM Service - Gemini Integration
Intelligente Intent-Erkennung und Parameter-Extraktion
"""

import google.generativeai as genai
import json
import os
import logging

logger = logging.getLogger(__name__)

# Konfiguration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# System Prompt
SYSTEM_PROMPT = """Du bist ein API-Parameter-Extractor für das NCA Toolkit.

Verfügbare APIs:

1. /v1/video/add/audio - Fügt Audio zu Video hinzu
   Parameter: video_url (string), audio_url (string)

2. /v1/media/transcribe - Transkribiert Audio/Video
   Parameter: media_url (string), language (string, default: "de")

3. /v1/image/screenshot/webpage - Screenshot einer Webseite
   Parameter: url (string), viewport_width (int, default: 1920), viewport_height (int, default: 1080)

4. /v1/media/convert/mp3 - Konvertiert zu MP3
   Parameter: media_url (string)

5. /v1/video/concatenate - Fügt Videos zusammen
   Parameter: video_urls (array of strings)

6. /v1/toolkit/test - API-Test
   Parameter: keine

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

Antwort-Format (JSON):
{
  "endpoint": "/v1/...",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "confidence": 0.95,
  "reasoning": "Kurze Erklärung"
}

Beispiele:

User: "Füge https://example.com/video.mp4 und https://example.com/audio.mp3 zusammen"
Antwort:
{
  "endpoint": "/v1/video/add/audio",
  "params": {
    "video_url": "https://example.com/video.mp4",
    "audio_url": "https://example.com/audio.mp3"
  },
  "confidence": 0.98,
  "reasoning": "Klare Absicht: Video und Audio zusammenfügen"
}

User: "Transkribiere dieses Video" (mit hochgeladener Datei video.mp4)
Antwort:
{
  "endpoint": "/v1/media/transcribe",
  "params": {
    "media_url": "USE_UPLOADED_FILE_0",
    "language": "de"
  },
  "confidence": 0.95,
  "reasoning": "Transkription gewünscht, deutsche Sprache angenommen"
}

User: "Screenshot von https://github.com"
Antwort:
{
  "endpoint": "/v1/image/screenshot/webpage",
  "params": {
    "url": "https://github.com",
    "viewport_width": 1920,
    "viewport_height": 1080
  },
  "confidence": 0.97,
  "reasoning": "Screenshot-Anfrage mit URL"
}
"""


def extract_intent_and_params(user_message, uploaded_files=None):
    """
    Nutzt Gemini LLM um Intent und Parameter zu extrahieren
    
    Args:
        user_message: User-Nachricht
        uploaded_files: Liste von {filename, url, type, size}
    
    Returns:
        {
            'endpoint': '/v1/...',
            'params': {...},
            'confidence': 0.95,
            'reasoning': '...'
        }
    """
    
    if not GEMINI_API_KEY:
        logger.warning("Kein GEMINI_API_KEY - nutze Fallback")
        return fallback_extraction(user_message, uploaded_files)
    
    try:
        # Build context
        context = f"User-Nachricht: {user_message}\n"
        
        if uploaded_files:
            context += f"\nHochgeladene Dateien:\n"
            for i, file in enumerate(uploaded_files):
                context += f"  {i}. {file['filename']} ({file['type']}, {file['size']} bytes)\n"
                context += f"     URL: {file['url']}\n"
        
        logger.info(f"LLM Context:\n{context}")
        
        # Call Gemini
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        
        response = model.generate_content(SYSTEM_PROMPT + "\n\n" + context)
        
        # Parse response
        result = json.loads(response.text)
        
        logger.info(f"LLM Response: {json.dumps(result, indent=2)}")
        
        # Replace placeholders with actual URLs
        if uploaded_files:
            params = result.get('params', {})
            for key, value in params.items():
                if isinstance(value, str) and value.startswith('USE_UPLOADED_FILE_'):
                    file_index = int(value.split('_')[-1])
                    if file_index < len(uploaded_files):
                        params[key] = uploaded_files[file_index]['url']
        
        return result
        
    except Exception as e:
        logger.exception("LLM extraction failed")
        return fallback_extraction(user_message, uploaded_files)


def fallback_extraction(user_message, uploaded_files=None):
    """
    Fallback wenn LLM nicht verfügbar ist
    Nutzt einfache Keyword-Matching
    """
    import re
    
    message_lower = user_message.lower()
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', user_message)
    
    # Video + Audio zusammenfügen
    if any(kw in message_lower for kw in ['zusammen', 'füge', 'merge', 'combine', 'audio.*video', 'video.*audio']):
        video_url = None
        audio_url = None
        
        if uploaded_files and len(uploaded_files) >= 2:
            # Erste Datei = Video, Zweite = Audio
            video_files = [f for f in uploaded_files if f['type'] in ['mp4', 'avi', 'mov', 'mkv']]
            audio_files = [f for f in uploaded_files if f['type'] in ['mp3', 'wav', 'aac', 'm4a']]
            
            if video_files:
                video_url = video_files[0]['url']
            if audio_files:
                audio_url = audio_files[0]['url']
        
        elif urls and len(urls) >= 2:
            video_url = urls[0]
            audio_url = urls[1]
        
        return {
            'endpoint': '/v1/video/add/audio',
            'params': {
                'video_url': video_url or '',
                'audio_url': audio_url or ''
            },
            'confidence': 0.7,
            'reasoning': 'Fallback: Keyword-Matching für Video+Audio'
        }
    
    # Transkription
    elif any(kw in message_lower for kw in ['transkript', 'transcribe', 'untertitel', 'text']):
        media_url = None
        
        if uploaded_files:
            media_url = uploaded_files[0]['url']
        elif urls:
            media_url = urls[0]
        
        language = 'de' if any(kw in message_lower for kw in ['deutsch', 'german']) else 'de'
        if any(kw in message_lower for kw in ['englisch', 'english']):
            language = 'en'
        
        return {
            'endpoint': '/v1/media/transcribe',
            'params': {
                'media_url': media_url or '',
                'language': language
            },
            'confidence': 0.7,
            'reasoning': 'Fallback: Keyword-Matching für Transkription'
        }
    
    # Screenshot
    elif any(kw in message_lower for kw in ['screenshot', 'capture', 'bild']):
        url = urls[0] if urls else ''
        
        return {
            'endpoint': '/v1/image/screenshot/webpage',
            'params': {
                'url': url,
                'viewport_width': 1920,
                'viewport_height': 1080
            },
            'confidence': 0.7,
            'reasoning': 'Fallback: Keyword-Matching für Screenshot'
        }
    
    # MP3 Konvertierung
    elif any(kw in message_lower for kw in ['mp3', 'audio', 'konvertier']):
        media_url = None
        
        if uploaded_files:
            media_url = uploaded_files[0]['url']
        elif urls:
            media_url = urls[0]
        
        return {
            'endpoint': '/v1/media/convert/mp3',
            'params': {
                'media_url': media_url or ''
            },
            'confidence': 0.6,
            'reasoning': 'Fallback: Keyword-Matching für MP3-Konvertierung'
        }
    
    # Test
    elif any(kw in message_lower for kw in ['test', 'teste']):
        return {
            'endpoint': '/v1/toolkit/test',
            'params': {},
            'confidence': 0.9,
            'reasoning': 'Fallback: Test-Endpunkt erkannt'
        }
    
    # Unbekannt
    else:
        return {
            'endpoint': None,
            'params': {},
            'confidence': 0.0,
            'reasoning': 'Fallback: Keine passende Aktion gefunden'
        }


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    # Test 1: Mit URLs
    result = extract_intent_and_params(
        "Füge https://example.com/video.mp4 und https://example.com/audio.mp3 zusammen"
    )
    print("Test 1:", json.dumps(result, indent=2))
    
    # Test 2: Mit Dateien
    result = extract_intent_and_params(
        "Transkribiere dieses Video",
        uploaded_files=[{
            'filename': 'video.mp4',
            'url': 'http://localhost:5000/uploads/video.mp4',
            'type': 'mp4',
            'size': 1024000
        }]
    )
    print("Test 2:", json.dumps(result, indent=2))
