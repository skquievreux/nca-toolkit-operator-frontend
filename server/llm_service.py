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
def configure_gemini():
    api_key = os.getenv('GEMINI_API_KEY', '')
    if api_key:
        genai.configure(api_key=api_key)
        logger.info("✅ Gemini API configured")
        return True
    logger.warning("❌ No GEMINI_API_KEY found")
    return False

# Initial configuration
configure_gemini()

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
- KEINE halluzinierten Parameter! Wenn ein Parameter fehlt, gib `endpoint: null` zurück.
- Erfinde KEINE Endpoints. Nutze NUR die oben gelisteten.
- Gib confidence zwischen 0 und 1 an.

Antwort-Format (JSON):
{
  "endpoint": "/v1/...",
  "params": {
    "param1": "value1"
  },
  "confidence": 0.95,
  "reasoning": "Kurze Erklärung oder FEHLERGRUND wenn endpoint null"
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
    
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        logger.warning("Kein GEMINI_API_KEY - nutze Fallback")
        return fallback_extraction(user_message, uploaded_files)
    
    # Ensure genai is configured (in case it wasn't at module load)
    configure_gemini()
    
    try:
        # Build context
        context = f"User-Nachricht: {user_message}\n"
        
        if uploaded_files:
            context += f"\nHochgeladene Dateien:\n"
            for i, file in enumerate(uploaded_files):
                context += f"  {i}. {file['filename']} ({file['type']}, {file['size']} bytes)\n"
                context += f"     URL: {file['url']}\n"
        
        logger.info(f"LLM Context:\n{context}")
        
        # Get dynamic system prompt with discovered endpoints
        from endpoint_discovery import get_dynamic_system_prompt
        dynamic_prompt = get_dynamic_system_prompt()
        
        # Merge with local capabilities (that are NOT in the container)
        local_capabilities = """
Zusätzliche LOKALE Funktionen (Server-seitig verfügbar):

** /v1/image/screenshot/webpage **
   - Beschreibung: Erstellt einen Screenshot einer Webseite
   - Parameter: url (string), viewport_width (int, default: 1920), viewport_height (int, default: 1080)
   - Beispiel: "Screenshot von google.de" -> endpoint: /v1/image/screenshot/webpage

** /v1/video/thumbnail **
   - Beschreibung: Erstellt ein Thumbnail aus einem Video
   - Parameter: url (string - file url)
   - Beispiel: "Mache ein Thumbnail" -> endpoint: /v1/video/thumbnail
"""
        system_prompt = dynamic_prompt + "\n" + local_capabilities
        
        # Call Gemini
        model = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        
        response = model.generate_content(system_prompt + "\n\n" + context)
        
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


import time

# ... (restliche imports bleiben gleich, ich ersetze nur den oberen teil und die fallback funktion)

def fallback_extraction(user_message, uploaded_files=None):
    """
    Fallback wenn LLM nicht verfügbar ist
    Nutzt einfache Keyword-Matching
    """
    import re
    
    message_lower = user_message.lower()
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', user_message)
    
    # Test Endpoint (HÖCHSTE PRIORITÄT!)
    if any(kw in message_lower for kw in ['test', 'teste', 'check', 'prüf']):
        return {
            'endpoint': '/v1/toolkit/test',
            'params': {},
            'confidence': 0.9,
            'reasoning': 'Fallback: Test-Endpunkt erkannt'
        }
    
    # Thumbnail (Video)
    if any(kw in message_lower for kw in ['thumbnail', 'vorschaubild', 'cover']):
        video_url = None
        if uploaded_files:
            video_url = uploaded_files[0]['url']
        elif urls:
            video_url = urls[0]
            
        return {
            'endpoint': '/v1/video/thumbnail',
            'params': {'url': video_url or ''},
            'confidence': 0.8,
            'reasoning': 'Fallback: Keyword-Matching für Thumbnail'
        }

    # Video + Audio zusammenfügen
    if any(kw in message_lower for kw in ['zusammen', 'füge', 'merge', 'combine']) and \
       (any(kw in message_lower for kw in ['audio', 'ton', 'mp3']) and any(kw in message_lower for kw in ['video', 'film', 'mp4'])):
        
        video_url = None
        audio_url = None
        
        if uploaded_files and len(uploaded_files) >= 2:
            # Versuch intelligent zu guessen anhand extension
            for f in uploaded_files:
                ext = f.get('filename', '').lower().split('.')[-1]
                if ext in ['mp4', 'mov', 'avi', 'mkv'] and not video_url:
                    video_url = f['url']
                elif ext in ['mp3', 'wav', 'aac', 'm4a'] and not audio_url:
                    audio_url = f['url']
            
            # Fallback wenn extensions nicht klar
            if not video_url and len(uploaded_files) > 0: video_url = uploaded_files[0]['url']
            if not audio_url and len(uploaded_files) > 1: audio_url = uploaded_files[1]['url']
        
        elif urls and len(urls) >= 2:
            video_url = urls[0]
            audio_url = urls[1]
        # Helper: Get Host IP for webhook
        def get_lan_ip():
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                return 'host.docker.internal' # Fallback
        
        host_ip_addr = get_lan_ip()

        return {
            'endpoint': '/audio-mixing',
            'params': {
                'video_url': video_url,
                'audio_url': audio_url,
                'video_vol': 100,
                'audio_vol': 100,
                'output_length': 'video',
                'webhook_url': f"http://{host_ip_addr}:5000/api/upload"
            },
            'confidence': 0.9,
            'reasoning': 'Fallback: Video+Audio Mixing (legacy endpoint checked)'
        }

    # Audio/Video Concatenation (Loop/Join)
    if any(kw in message_lower for kw in ['hintereinander', 'loop', 'wiederhole', 'concat', 'concatenate', 'reihe']):
        
        media_files = []
        if uploaded_files:
            media_files = [f['url'] for f in uploaded_files]
        elif urls:
            media_files = urls

        if not media_files:
             # No files uploaded and no URLs in message
             # Check if user mentioned specific test files
             if 'audio1' in message_lower:
                  host_ip = get_lan_ip()
                  media_files = [f'http://{host_ip}:5000/uploads/audio-1.mp3']
             elif 'video1' in message_lower:
                  host_ip = get_lan_ip()
                  media_files = [f'http://{host_ip}:5000/uploads/video-1.mp4']


        if media_files:
            # Check for repetition
            count = 1
            if any(kw in message_lower for kw in ['dreimal', '3x', '3 mal', '3 times']):
                count = 3
            elif any(kw in message_lower for kw in ['zweimal', '2x', '2 mal', '2 times']):
                count = 2
            


            final_files = []
            if len(media_files) == 1 and count > 1:
                final_files = media_files * count # Repeat the same file
            else:
                final_files = media_files # Just join different files

            return {
                'endpoint': '/combine-videos', # Correct endpoint per container source
                'params': {
                    'media_urls': final_files # Correct param name
                },
                'confidence': 0.85,
                'reasoning': f'Fallback: Concatenation of {len(final_files)} files requested'
            }
    
    # Transkription
    elif any(kw in message_lower for kw in ['transkript', 'transcrib', 'untertitel', 'text', 'transkrib']):
        media_url = None
        
        if uploaded_files:
            media_url = uploaded_files[0]['url']
        elif urls:
            media_url = urls[0]
        
        language = 'de'
        if any(kw in message_lower for kw in ['englisch', 'english']):
            language = 'en'
        
        return {
            'endpoint': '/transcribe',
            'params': {
                'media_url': media_url or '',
                'language': language,
                # Parameteranpassung laut Doku v1/media/transcribe
                'task': 'transcribe',
                'include_text': True,
                'include_srt': True,
                'response_type': 'cloud'
            },
            'confidence': 0.8,
            'reasoning': 'Fallback: Keyword-Matching für Transkription'
        }
    
    # Screenshot
    elif any(kw in message_lower for kw in ['screenshot', 'capture', 'bild']):
        url = urls[0] if urls else ''
        return {
            'endpoint': '/v1/image/screenshot/webpage',
            'params': {
                'url': url or 'https://google.com',
                'viewport_width': 1920,
                'viewport_height': 1080
            },
            'confidence': 0.8,
            'reasoning': 'Fallback: Keyword-Matching für Screenshot'
        }
    
    # MP3 Konvertierung
    elif any(kw in message_lower for kw in ['mp3', 'audio', 'konvertier']):
        media_url = None
        if uploaded_files: media_url = uploaded_files[0]['url']
        elif urls: media_url = urls[0]
        
        return {
            'endpoint': '/media-to-mp3',
            'params': {'url': media_url or ''},
            'confidence': 0.8,
            'reasoning': 'Fallback: Keyword-Matching für MP3-Konvertierung'
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
