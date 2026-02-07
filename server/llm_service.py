"""
LLM Service - Gemini Integration
Intelligente Intent-Erkennung und Parameter-Extraktion
"""

import google.generativeai as genai
import requests
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
# System Prompt is now dynamically generated via endpoint_discovery.py
# This ensures ZOT (Single Source of Truth)


def extract_intent_and_params(user_message, uploaded_files=None, language=None):
    """
    Nutzt Gemini LLM um Intent und Parameter zu extrahieren
    
    Args:
        user_message: User-Nachricht
        uploaded_files: Liste von {filename, url, type, size}
        language: Optionaler Sprach-Hint (z.B. 'de', 'en')
    
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
        if language:
            context += f"Bevorzugte Sprache: {language}\n"
            
        if uploaded_files:
            context += f"\nHochgeladene Dateien:\n"
            for i, file in enumerate(uploaded_files):
                context += f"  {i}. {file['filename']} ({file['type']}, {file['size']} bytes)\n"
                context += f"     URL: {file['url']}\n"
        
        logger.debug(f"LLM Context:\n{context}")
        
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
                "response_mime_type": "application/json",
                "temperature": 0.1,  # Niedrige Temperatur für konsistentere Outputs
            }
        )
        
        response = model.generate_content(system_prompt + "\n\n" + context)
        
        # Parse response
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw response: {response.text[:500]}")
            return fallback_extraction(user_message, uploaded_files)
        
        logger.debug(f"LLM Response: {json.dumps(result, indent=2)}")
        
        # VALIDATION: Ensure result is a dictionary, not a list
        if not isinstance(result, dict):
            logger.warning(f"LLM returned invalid format (expected dict, got {type(result).__name__}). Using fallback.")
            logger.debug(f"Invalid response: {result}")
            return fallback_extraction(user_message, uploaded_files)
        
        # Ensure required fields exist
        if 'endpoint' not in result:
            logger.warning("LLM response missing 'endpoint' field. Using fallback.")
            logger.debug(f"Response: {result}")
            return fallback_extraction(user_message, uploaded_files)
        
        # Ensure params is a dict
        if 'params' in result and not isinstance(result['params'], dict):
            logger.warning(f"LLM params is not a dict (got {type(result['params']).__name__}). Fixing.")
            result['params'] = {}
        
        # Replace placeholders with actual URLs
        if uploaded_files:
            params = result.get('params', {})
            for key, value in params.items():
                if isinstance(value, str) and value.startswith('USE_UPLOADED_FILE_'):
                    try:
                        file_index = int(value.split('_')[-1])
                        if file_index < len(uploaded_files):
                            params[key] = uploaded_files[file_index]['url']
                        else:
                            logger.warning(f"LLM hallucinated upload index {file_index}, but only {len(uploaded_files)} files. Setting {key} to None.")
                            params[key] = None
                    except ValueError:
                        params[key] = None
        
        # Cleanup: Remove any remaining placeholders if uploaded_files was empty/None
        if not uploaded_files:
             params = result.get('params', {})
             for key, value in params.items():
                if isinstance(value, str) and value.startswith('USE_UPLOADED_FILE_'):
                     logger.warning(f"LLM used placeholder {value} but no files uploaded. Clearing {key}.")
                     params[key] = None
        
        return result
        
    except Exception as e:
        logger.exception("LLM extraction failed")
        return fallback_extraction(user_message, uploaded_files)


def transcribe_media(media_url, language='de'):
    """
    Transkribiert Media über die externe NCA Toolkit API.
    
    Args:
        media_url: Erreichbare URL zur Datei (http://...)
        language: Sprachcode
        
    Returns:
        {
            'text': 'Vollständiger Text',
            'srt': 'SRT formatierter Text',
            'language': 'de'
        }
    """
    api_url = os.getenv('NCA_API_URL', 'http://localhost:8080')
    api_key = os.getenv('NCA_API_KEY', '')
    
    endpoint = f"{api_url}/v1/media/transcribe"
    logger.info(f"🎙️ NCA Transcription: {media_url} via {endpoint}")
    
    try:
        # PING/Check before call? No, just call.
        payload = {
            'media_url': media_url,
            'language': language,
            'include_srt': True,
            'include_text': True,
            'response_type': 'direct'
        }
        
        response = requests.post(
            endpoint,
            headers={'x-api-key': api_key, 'Content-Type': 'application/json'},
            json=payload,
            timeout=300 # 5min timeout for long files
        )
        
        if response.status_code != 200:
            logger.error(f"API Error ({response.status_code}): {response.text}")
            raise Exception(f"NCA API failed: {response.text}")
            
        result = response.json()
        # AGGRESSIVE LOGGING (Visible even in non-debug mode)
        logger.warning(f"🎙️ [VER5] NCA Raw Result Keys: {list(result.keys())}")
        
        # Determine where the actual data is (NCA often wraps in 'response')
        data = result.get('response', result)
        
        # Handle cases where 'response' might be a JSON string
        if isinstance(data, str):
            try:
                data = json.loads(data)
                logger.info("🔓 Decoded 'response' string into dict")
            except:
                pass

        # Validate result structure
        if isinstance(data, dict):
            logger.warning(f"📝 NCA Data Keys: {list(data.keys())}")
            srt_val = data.get('srt')
            if srt_val is None:
                 logger.warning("❌ 'srt' field is None in NCA response data")
            elif 'srt' not in data:
                 logger.warning("❌ 'srt' field MISSING in NCA response data")
            else:
                 logger.warning(f"✅ [VER5] 'srt' found, length: {len(str(srt_val))}")
                 logger.warning(f"📝 [VER5] SRT CONTENT:\n{srt_val}")
        else:
            logger.warning(f"❌ NCA Data is not a dict: {type(data)}")

        return {
            'text': (data.get('text') or '') if isinstance(data, dict) else '',
            'srt': (data.get('srt') or '') if isinstance(data, dict) else '',
            'language': language
        }

    except Exception as e:
        logger.error(f"External Transcription failed: {e}")
        raise e


import time

# ... (restliche imports bleiben gleich, ich ersetze nur den oberen teil und die fallback funktion)

def fallback_extraction(user_message, uploaded_files=None):
    """
    Fallback wenn LLM nicht verfügbar ist oder ungültige Antwort gibt.
    Nutzt verbessertes Keyword-Matching mit Prioritäten.
    """
    import re
    
    if not user_message:
        return {
            'endpoint': None,
            'params': {},
            'confidence': 0.0,
            'reasoning': 'Fallback: Keine Nachricht vorhanden'
        }
    
    message_lower = user_message.lower()
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', user_message)
    
    # ============================================================================
    # PRIORITY 1: Test Endpoint (HÖCHSTE PRIORITÄT!)
    # ============================================================================
    if any(kw in message_lower for kw in ['test', 'teste', 'check', 'prüf', 'api']):
        return {
            'endpoint': '/v1/toolkit/test',
            'params': {},
            'confidence': 0.9,
            'reasoning': 'Fallback: Test-Endpunkt erkannt'
        }
    
    # ============================================================================
    # PRIORITY 2: Screenshot (Website oder Video)
    # ============================================================================
    if any(kw in message_lower for kw in ['screenshot', 'capture', 'bild', 'screen']):
        url = urls[0] if urls else None
        
        # Wenn keine URL in Message, prüfe uploaded files
        if not url and uploaded_files:
            url = uploaded_files[0].get('url')
        
        return {
            'endpoint': '/v1/image/screenshot/webpage',
            'params': {
                'url': url or 'https://google.com',
                'viewport_width': 1920,
                'viewport_height': 1080
            },
            'confidence': 0.85,
            'reasoning': 'Fallback: Screenshot-Intent erkannt'
        }
    
    # ============================================================================
    # PRIORITY 3: Thumbnail (Video)
    # ============================================================================
    if any(kw in message_lower for kw in ['thumbnail', 'vorschaubild', 'cover', 'preview']):
        video_url = None
        if uploaded_files:
            video_url = uploaded_files[0]['url']
        elif urls:
            video_url = urls[0]
            
        return {
            'endpoint': '/v1/video/thumbnail',
            'params': {'url': video_url or ''},
            'confidence': 0.8,
            'reasoning': 'Fallback: Thumbnail-Intent erkannt'
        }

    # ============================================================================
    # PRIORITY 4: Video + Audio zusammenfügen
    # ============================================================================
    is_mixing = any(kw in message_lower for kw in ['zusammen', 'füge', 'merge', 'combine', 'mix'])
    has_audio_video = (any(kw in message_lower for kw in ['audio', 'ton', 'mp3']) and 
                       any(kw in message_lower for kw in ['video', 'film', 'mp4']))
    
    if is_mixing and has_audio_video:
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
            if not video_url and len(uploaded_files) > 0: 
                video_url = uploaded_files[0]['url']
            if not audio_url and len(uploaded_files) > 1: 
                audio_url = uploaded_files[1]['url']
        
        elif urls and len(urls) >= 2:
            video_url = urls[0]
            audio_url = urls[1]
        
        if video_url and audio_url:
            return {
                'endpoint': '/v1/video/add/audio',
                'params': {
                    'video_url': video_url,
                    'audio_url': audio_url
                },
                'confidence': 0.85,
                'reasoning': 'Fallback: Video+Audio Mixing erkannt'
            }

    # ============================================================================
    # PRIORITY 5: Audio/Video Concatenation (Loop/Join)
    # ============================================================================
    if any(kw in message_lower for kw in ['hintereinander', 'loop', 'wiederhole', 'concat', 'concatenate', 'reihe', 'aneinander']):
        media_files = []
        if uploaded_files:
            media_files = [f['url'] for f in uploaded_files]
        elif urls:
            media_files = urls

        if media_files:
            # Check for repetition
            count = 1
            if any(kw in message_lower for kw in ['dreimal', '3x', '3 mal', '3 times']):
                count = 3
            elif any(kw in message_lower for kw in ['zweimal', '2x', '2 mal', '2 times']):
                count = 2
            
            final_files = []
            if len(media_files) == 1 and count > 1:
                final_files = media_files * count  # Repeat the same file
            else:
                final_files = media_files  # Just join different files

            return {
                'endpoint': '/v1/video/concatenate',
                'params': {
                    'video_urls': final_files
                },
                'confidence': 0.8,
                'reasoning': f'Fallback: Concatenation von {len(final_files)} Dateien'
            }
    
    # ============================================================================
    # PRIORITY 6: Transkription
    # ============================================================================
    if any(kw in message_lower for kw in ['transkript', 'transcrib', 'untertitel', 'text', 'transkrib', 'stt', 'speech to text']):
        media_url = None
        
        if uploaded_files:
            media_url = uploaded_files[0]['url']
        elif urls:
            media_url = urls[0]
        
        language = 'de'
        if any(kw in message_lower for kw in ['englisch', 'english']):
            language = 'en'
        
        return {
            'endpoint': '/v1/media/transcribe',
            'params': {
                'media_url': media_url or '',
                'language': language
            },
            'confidence': 0.8,
            'reasoning': 'Fallback: Transkriptions-Intent erkannt'
        }
    
    # ============================================================================
    # PRIORITY 7: RSS Automatisierung
    # ============================================================================
    if any(kw in message_lower for kw in ['rss', 'feed', 'item', 'podcast', 'acidmonk']):
        # Wenn nur nach Feed gefragt wird -> List
        if any(kw in message_lower for kw in ['list', 'zeig', 'browse', 'durchsuche', 'themen']):
            return {
                'endpoint': '/api/rss/list',
                'params': {'url': urls[0] if urls else None},
                'confidence': 0.9,
                'reasoning': 'Fallback: RSS Liste angefragt'
            }
        # Sonst -> Process
        # Sonst -> Process
        params = {
            'image_url': None, 
            'audio_url': None
        }
        
        # Check for [PARAMS] block from Frontend
        import re
        if '[PARAMS]' in user_message:
            try:
                param_block = user_message.split('[PARAMS]')[1]
                
                # Extract Width
                w_match = re.search(r'width:\s*(\d+)', param_block)
                if w_match: params['width'] = int(w_match.group(1))
                
                # Extract Height
                h_match = re.search(r'height:\s*(\d+)', param_block)
                if h_match: params['height'] = int(h_match.group(1))
                
                # Extract Music URL
                music_match = re.search(r'background_music_url:\s*([^\s\n]+)', param_block)
                if music_match: params['background_music_url'] = music_match.group(1)
                
                # Extract Subtitles
                sub_match = re.search(r'render_subtitles:\s*true', param_block, re.IGNORECASE)
                if sub_match: params['render_subtitles'] = True
                
            except Exception as e:
                logger.error(f"Failed to parse [PARAMS]: {e}")

        return {
            'endpoint': '/api/rss/process',
            'params': params,
            'confidence': 0.9, # Higher confidence because of explicit params
            'reasoning': 'Fallback: RSS Verarbeitung mit expliziten Parametern'
        }

    # ============================================================================
    # PRIORITY 8: MP3 Konvertierung
    # ============================================================================
    if any(kw in message_lower for kw in ['mp3', 'konvertier', 'convert', 'audio']):
        media_url = None
        if uploaded_files: 
            media_url = uploaded_files[0]['url']
        elif urls: 
            media_url = urls[0]
        
        return {
            'endpoint': '/v1/media/convert/mp3',
            'params': {'media_url': media_url or ''},
            'confidence': 0.75,
            'reasoning': 'Fallback: MP3-Konvertierung erkannt'
        }
    
    # ============================================================================
    # FALLBACK: Unbekannt
    # ============================================================================
    # Wenn wir hier ankommen, versuchen wir zu raten basierend auf uploaded files
    if uploaded_files and len(uploaded_files) > 0:
        first_file = uploaded_files[0]
        ext = first_file.get('filename', '').lower().split('.')[-1]
        
        # Video-Datei -> Thumbnail
        if ext in ['mp4', 'mov', 'avi', 'mkv']:
            return {
                'endpoint': '/v1/video/thumbnail',
                'params': {'url': first_file['url']},
                'confidence': 0.5,
                'reasoning': 'Fallback: Video-Datei hochgeladen, vermute Thumbnail-Wunsch'
            }
        
        # Audio-Datei -> MP3 Konvertierung
        if ext in ['wav', 'aac', 'm4a', 'flac']:
            return {
                'endpoint': '/v1/media/convert/mp3',
                'params': {'media_url': first_file['url']},
                'confidence': 0.5,
                'reasoning': 'Fallback: Audio-Datei hochgeladen, vermute MP3-Konvertierung'
            }
    
    # Wirklich keine Ahnung
    return {
        'endpoint': None,
        'params': {},
        'confidence': 0.0,
        'reasoning': 'Fallback: Keine passende Aktion gefunden. Bitte spezifizieren Sie Ihre Anfrage.'
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
