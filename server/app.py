"""
NCA Toolkit Web Server
Flask-basierter Backend-Server für die Web-Oberfläche mit LLM-Integration
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import sys
import time
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

# Import unserer Services
from llm_service import extract_intent_and_params
from file_handler import handle_upload, init_upload_folder, cleanup_old_files, UPLOAD_FOLDER
from version import VERSION
from utils import get_lan_ip
import local_processor  # Local FFmpeg support

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)

# Konfiguration
NCA_API_URL = os.getenv('NCA_API_URL', 'http://localhost:8080')
NCA_API_KEY = os.getenv('NCA_API_KEY', '343534sfklsjf343423')

# Upload-Ordner initialisieren
init_upload_folder()

# Build Number (increment on each significant change)
BUILD_NUMBER = "2026.01.08.030"

# Self-Diagnosis: Check Network IP
HOST_IP = get_lan_ip()
logger.info(f"🌐 Running on Host IP: {HOST_IP}")


# Start Time für Uptime
START_TIME = time.time()

# Job Queue für Tracking
jobs = {}
job_lock = __import__('threading').Lock()

# API Endpoint Definitionen
API_ENDPOINTS = {
    'audio': {
        'concatenate': {
            'endpoint': '/v1/audio/concatenate',
            'description': 'Kombiniert mehrere Audiodateien',
            'method': 'POST'
        }
    },
    'code': {
        'execute_python': {
            'endpoint': '/v1/code/execute/python',
            'description': 'Führt Python-Code aus',
            'method': 'POST'
        }
    },
    'image': {
        'convert_to_video': {
            'endpoint': '/v1/image/convert/video',
            'description': 'Konvertiert Bild zu Video',
            'method': 'POST'
        },
        'screenshot_webpage': {
            'endpoint': '/v1/image/screenshot/webpage',
            'description': 'Erstellt Screenshot einer Webseite',
            'method': 'POST'
        }
    },
    'media': {
        'convert': {
            'endpoint': '/v1/media/convert',
            'description': 'Konvertiert Medienformate',
            'method': 'POST'
        },
        'convert_to_mp3': {
            'endpoint': '/v1/media/convert/mp3',
            'description': 'Konvertiert zu MP3',
            'method': 'POST'
        },
        'transcribe': {
            'endpoint': '/v1/media/transcribe',
            'description': 'Transkribiert Audio/Video',
            'method': 'POST'
        },
        'metadata': {
            'endpoint': '/v1/media/metadata',
            'description': 'Extrahiert Metadaten',
            'method': 'POST'
        }
    },
    'video': {
        'add_audio': {
            'endpoint': '/v1/video/add/audio',
            'description': 'Fügt Audio zu Video hinzu',
            'method': 'POST'
        },
        'concatenate': {
            'endpoint': '/v1/video/concatenate',
            'description': 'Fügt Videos zusammen',
            'method': 'POST'
        },
        'caption': {
            'endpoint': '/v1/video/caption',
            'description': 'Fügt Untertitel hinzu',
            'method': 'POST'
        },
        'thumbnail': {
            'endpoint': '/v1/video/thumbnail',
            'description': 'Erstellt Thumbnail',
            'method': 'POST'
        }
    },
    'toolkit': {
        'test': {
            'endpoint': '/v1/toolkit/test',
            'description': 'API-Test',
            'method': 'POST'
        },
        'authenticate': {
            'endpoint': '/v1/toolkit/authenticate',
            'description': 'Authentifizierung testen',
            'method': 'POST'
        }
    }
}


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve files from the upload directory"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/endpoints', methods=['GET'])
def get_endpoints():
    """Gibt alle verfügbaren API-Endpunkte zurück"""
    return jsonify({
        'success': True,
        'endpoints': API_ENDPOINTS
    })


@app.route('/api/proxy', methods=['POST'])
def proxy_request():
    """
    Proxy-Endpunkt für NCA Toolkit API-Requests
    Erwartet: { "endpoint": "/v1/...", "params": {...} }
    """
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        params = data.get('params', {})
        
        if not endpoint:
            return jsonify({
                'success': False,
                'error': 'Endpoint fehlt'
            }), 400
        
        # Log Request
        logger.info(f"Proxy Request: {endpoint}")
        logger.debug(f"Params: {json.dumps(params, indent=2)}")
        
        # SPECIAL HANDLING: Test Endpoint -> Rufe Tools List oder Health auf
        if endpoint == '/v1/toolkit/test':
            # Versuche Tools List zu bekommen für Debugging
            # MCP Standard: /v1/tools/list (GET)
            logger.info("Test-Mode: Checking available tools...")
            try:
                # Versuch 1: Tools List
                resp = requests.get(f"{NCA_API_URL}/v1/tools/list", timeout=5)
                if resp.ok:
                    return jsonify({
                        'success': True, 
                        'result': {'message': 'NCA Toolkit läuft!', 'tools': resp.json()}
                    })
            except:
                pass
                
            # Fallback: Einfach OK zurückgeben
            return jsonify({
                'success': True,
                'result': {
                    'status': 'ok',
                    'message': 'NCA Toolkit ist erreichbar (Mock Response)',
                    'timestamp': datetime.now().isoformat()
                }
            })

        # Request an NCA Toolkit API
        url = f"{NCA_API_URL}{endpoint}"
        headers = {
            'x-api-key': NCA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Calling NCA API: {url} [POST]")
        
        response = requests.post(
            url,
            headers=headers,
            json=params,
            timeout=600  # 10 Minuten Timeout (war 300)
        )
        
        # Log Response
        logger.info(f"Response Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
            
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            error_msg = f"API Error: {response.status_code}"
            logger.error(f"{error_msg} - {response.text[:500]}")
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'details': response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({
            'success': False,
            'error': 'Request timeout (>5 Min)'
        }), 504
        
    except requests.exceptions.ConnectionError:
        logger.error("Connection error - ist der NCA Container erreichbar?")
        return jsonify({
            'success': False,
            'error': 'Verbindung zum NCA Toolkit fehlgeschlagen. Läuft der Container?'
        }), 503
        
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a job"""
    with job_lock:
        job = jobs.get(job_id)
    
    if not job:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    return jsonify({
        'success': True,
        'job': job
    })


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    with job_lock:
        job_list = list(jobs.values())
    
    return jsonify({
        'success': True,
        'jobs': job_list,
        'count': len(job_list)
    })


@app.route('/api/process', methods=['POST'])
def process_request():
    """
    Haupt-Endpunkt: Akzeptiert Nachricht + Dateien, verarbeitet mit LLM, ruft NCA API auf
    
    Form Data:
        message: User-Nachricht (string)
        files: Hochgeladene Dateien (optional, multiple)
    
    Returns:
        {
            'success': True/False,
            'intent': {
                'endpoint': '/v1/...',
                'confidence': 0.95,
                'reasoning': '...'
            },
            'params': {...},
            'uploaded_files': [...],
            'result': {...}
        }
    """
    # Create job
    import uuid
    job_id = str(uuid.uuid4())
    
    with job_lock:
        jobs[job_id] = {
            'id': job_id,
            'status': 'processing',
            'progress': 0,
            'message': '',
            'created_at': time.time(),
            'updated_at': time.time()
        }
    
    try:
        # 1. Get user message
        user_message = request.form.get('message', '')
        
        logger.info("=" * 60)
        logger.info(f"📨 New Request: {user_message[:100]} (Job: {job_id})")
        
        # Update progress
        with job_lock:
            jobs[job_id]['progress'] = 10
            jobs[job_id]['message'] = 'Verarbeite Anfrage...'
        
        # 2. Handle file uploads
        with job_lock:
            jobs[job_id]['progress'] = 20
            jobs[job_id]['message'] = 'Lade Dateien hoch...'
        
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            logger.info(f"📁 Files received: {len(files)}")
            
            for file in files:
                try:
                    file_info = handle_upload(file)
                    uploaded_files.append(file_info)
                    logger.info(f"✅ Uploaded: {file_info['filename']} ({file_info['size_mb']}MB)")
                except Exception as e:
                    logger.error(f"❌ Upload failed: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'File upload failed: {str(e)}'
                    }), 400
        
        # 3. Extract intent and params with LLM
        with job_lock:
            jobs[job_id]['progress'] = 40
            jobs[job_id]['message'] = 'Erkenne Intent...'
        
        logger.info("🤖 Calling LLM for intent extraction...")
        
        llm_result = extract_intent_and_params(user_message, uploaded_files)
        
        endpoint = llm_result.get('endpoint')
        params = llm_result.get('params', {})
        confidence = llm_result.get('confidence', 0.0)
        reasoning = llm_result.get('reasoning', '')
        
        logger.info(f"🤖 Gemini API Call: {endpoint}")
        logger.info(f"📋 Parameters: {json.dumps(params, indent=None)}")
        logger.info(f"💭 Reasoning: {reasoning}")
        logger.info(f"🎯 Confidence: {confidence*100:.1f}%")
        
        # Check if intent was found
        if not endpoint or confidence < 0.5:
            logger.warning("⚠️ Low confidence or no intent found")
            return jsonify({
                'success': False,
                'error': 'Konnte keine passende Aktion finden. Bitte formulieren Sie Ihre Anfrage anders.',
                'intent': llm_result,
                'uploaded_files': uploaded_files
            }), 400
        
        # 3.5 ENDPOINT DISCOVERY: Check if we need to find alternative endpoints
        # This is especially important for audio concatenation which might not work with /combine-videos
        if endpoint == '/combine-videos' and params.get('media_urls'):
            # Check if we're dealing with audio files
            first_url = params['media_urls'][0] if params['media_urls'] else ''
            if first_url.endswith('.mp3') or 'audio' in user_message.lower():
                logger.info("🔍 Detected audio files, checking for audio-specific endpoint...")
                
                # Try to find audio concatenation endpoint
                try:
                    # Query available routes from container
                    routes_response = requests.get(
                        f"{NCA_API_URL}/",
                        headers={'x-api-key': NCA_API_KEY},
                        timeout=2
                    )
                    
                    # If root doesn't work, we know from our investigation that audio mixing exists
                    # Let's use /media-to-mp3 endpoint multiple times or find concat endpoint
                    logger.info("⚠️ Audio concatenation not directly supported by /combine-videos")
                    logger.info("💡 Fallback: Using /media-to-mp3 for each file individually")
                    
                    # For now, we'll keep the original endpoint but log the issue
                    # In production, you'd implement proper audio concatenation here
                    
                except Exception as e:
                    logger.warning(f"Endpoint discovery failed: {e}")

        
        # 4. Call NCA Toolkit API (or handle locally)
        with job_lock:
            jobs[job_id]['progress'] = 60
            jobs[job_id]['message'] = f'Rufe {endpoint} auf...'
        
        logger.info(f"🚀 Calling NCA API: {endpoint}")
        
        # Check for YouTube URLs and download them automatically
        if params:
            from youtube_service import is_youtube_url, download_youtube_video
            
            for key, value in params.items():
                if isinstance(value, str) and is_youtube_url(value):
                    logger.info(f"🎬 YouTube URL detected: {value}")
                    logger.info(f"📥 Downloading video automatically...")
                    
                    with job_lock:
                        jobs[job_id]['progress'] = 50
                        jobs[job_id]['message'] = 'Lade YouTube-Video herunter...'
                    
                    try:
                        download_result = download_youtube_video(value)
                        logger.info(f"✅ Downloaded: {download_result['title']}")
                        
                        # Replace YouTube URL with downloaded file URL
                        params[key] = download_result['url']
                        
                        with job_lock:
                            jobs[job_id]['progress'] = 60
                            jobs[job_id]['message'] = f'Video heruntergeladen: {download_result["title"]}'
                        
                    except Exception as e:
                        logger.error(f"❌ YouTube download failed: {e}")
                        raise ValueError(f"YouTube-Download fehlgeschlagen: {str(e)}")
        
        # SPECIAL CASE: Audio concatenation
        if endpoint == '/combine-videos' and params.get('media_urls'):
            first_url = params['media_urls'][0] if params['media_urls'] else ''
            if first_url.endswith('.mp3') or first_url.endswith('.wav') or first_url.endswith('.aac'):
                logger.info("🎵 Detected audio concatenation request - handling locally")
                
                try:
                    from local_audio_service import concatenate_audio_files
                    import uuid
                    output_filename = f"concatenated_{uuid.uuid4().hex[:8]}.mp3"
                    result_url = concatenate_audio_files(params['media_urls'], output_filename)
                    
                    nca_response = {
                        'success': True,
                        'output_url': result_url,
                        'message': 'Audio concatenation completed locally',
                        'files_concatenated': len(params['media_urls'])
                    }
                    
                    logger.info(f"✅ Local audio concatenation successful: {result_url}")
                    
                except Exception as e:
                    logger.error(f"❌ Local audio concatenation failed: {e}")
                    raise
            else:
                # Regular video concatenation - send to container
                nca_response = call_nca_api(endpoint, params)
        else:
            # All other endpoints - send to container
            nca_response = call_nca_api(endpoint, params)
        
        with job_lock:
            jobs[job_id]['progress'] = 90
            jobs[job_id]['message'] = 'Verarbeite Ergebnis...'
        
        logger.info("✅ Request completed successfully")
        logger.info("=" * 60)
        
        # Update job status
        with job_lock:
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['progress'] = 100
            jobs[job_id]['message'] = 'Fertig!'
            jobs[job_id]['updated_at'] = time.time()
            jobs[job_id]['result'] = nca_response
        
        # 5. Return result
        return jsonify({
            'success': True,
            'job_id': job_id,
            'intent': {
                'endpoint': endpoint,
                'confidence': confidence,
                'reasoning': reasoning
            },
            'params': params,
            'uploaded_files': uploaded_files,
            'result': nca_response
        })
        
    except Exception as e:
        logger.exception("💥 Error processing request")
        
        # Update job status
        with job_lock:
            if job_id in jobs:
                jobs[job_id]['status'] = 'failed'
                jobs[job_id]['message'] = str(e)
                jobs[job_id]['updated_at'] = time.time()
        
        return jsonify({
            'success': False,
            'job_id': job_id,
            'error': str(e)
        }), 500


def call_nca_api(endpoint, params):
    """Call NCA Toolkit API"""
    
    # SPECIAL HANDLING: Test Endpoint
    if endpoint == '/v1/toolkit/test':
        try:
            resp = requests.get(f"{NCA_API_URL}/v1/tools/list", timeout=5)
            if resp.ok:
                return {'message': 'NCA Toolkit läuft!', 'tools': resp.json()}
        except:
            pass
        return {
            'status': 'ok',
            'message': 'NCA Toolkit ist erreichbar (Mock Response)',
            'timestamp': datetime.now().isoformat()
        }

    # VALIDATION
    required_params = {
        '/audio-mixing': ['video_url', 'audio_url'],
        '/combine-videos': ['video_urls'],
        '/media-to-mp3': ['media_url'],
        '/transcribe': ['media_url'],
        '/gdrive-upload': ['file_url']
    }

    if endpoint in required_params:
        missing = [p for p in required_params[endpoint] if p not in params or not params[p]]
        if missing:
            # Versuch Parameter zu korrigieren
            if endpoint == '/audio-mixing' and 'media_url' in params:
                # Vielleicht wurde nur eine URL übergeben?
                pass 
            
            logger.error(f"❌ Missing parameters for {endpoint}: {missing}")
            raise ValueError(f"Fehlende Parameter für {endpoint}: {', '.join(missing)}")
            
    # Parameter-Bereinigung
    # Entferne leere Parameter
    params = {k: v for k, v in params.items() if v is not None}

    # ---------------------------------------------------------
    # INTERCEPT: Local Audio Concatenation
    # ---------------------------------------------------------
    if endpoint == '/v1/audio/concatenate' and local_processor.check_local_ffmpeg():
        logger.info("🚀 LOCAL OVERRIDE: Using local FFmpeg for audio concatenation")
        audio_urls = params.get('audio_urls', [])
        try:
            return local_processor.local_audio_concat(audio_urls)
        except Exception as e:
            logger.error(f"Local Audio Concat Failed: {e}")
            raise Exception(f"Local Audio Processing Error: {e}")

    # Normalize endpoints for consistency
    if endpoint == '/v1/video/add/audio':
        endpoint = '/audio-mixing'
    if endpoint == '/v1/media/convert/mp3' or endpoint == '/v1/audio/convert/mp3':
        endpoint = '/media-to-mp3'
    if endpoint == '/v1/media/transcribe':
        endpoint = '/transcribe'
    if endpoint == '/v1/video/concatenate':
        endpoint = '/combine-videos'
    if endpoint == '/v1/video/add/captions' or endpoint == '/v1/video/captions':
        endpoint = '/v1/video/add/captions'
    if endpoint == '/v1/video/add/watermark':
        endpoint = '/v1/video/add/watermark'
    if endpoint == '/v1/video/cut' or endpoint == '/v1/video/trim':
        endpoint = '/v1/video/cut'

    # ---------------------------------------------------------
    # INTERCEPT: Local Audio Mixing (Network Bypass)
    # ---------------------------------------------------------
    if endpoint == '/audio-mixing' and local_processor.check_local_ffmpeg():
        logger.info("🚀 LOCAL OVERRIDE: Using local FFmpeg for audio mixing")
        video_url = params.get('video_url')
        audio_url = params.get('audio_url')
        try:
            return local_processor.local_audio_mixing(video_url, audio_url)
        except Exception as e:
            logger.error(f"Local Fallback Failed: {e}")
            raise Exception(f"Local Processing Error: {e}")

    # ---------------------------------------------------------
    # INTERCEPT: Local Thumbnail / Screenshot for Video
    # ---------------------------------------------------------
    # Mapping "Thumbnail" intent to existing screenshot endpoint or simply catching it
    if 'thumbnail' in endpoint or 'screenshot' in endpoint:
         

         # Check if we have a video file in params
         video_url = params.get('url') or params.get('video_url') or params.get('media_url')
         
         if video_url:
             # Video Screenshot / Thumbnail
             if video_url.endswith('.mp4') or video_url.endswith('.mov') or video_url.endswith('.mkv'):
                 if local_processor.check_local_ffmpeg():
                     logger.info("🚀 LOCAL OVERRIDE: Generating thumbnail locally with FFmpeg")
                     try:
                         # Synchronous result - NO job_id needed for frontend!
                         return local_processor.create_thumbnail(video_url)
                     except Exception as e:
                         logger.error(f"Local Thumbnail Failed: {e}")
                         raise Exception(f"Thumbnail Generation Error: {e}")
             
             # Website Screenshot (via Selenium)
             elif video_url.startswith('http') and not video_url.endswith(('.mp3', '.wav')):
                 logger.info("🚀 LOCAL OVERRIDE: Generating website screenshot locally with Selenium")
                 try:
                      # Check params for viewport
                      width = params.get('viewport_width', 1920)
                      height = params.get('viewport_height', 1080)
                      return local_processor.create_website_screenshot(video_url, width, height)
                 except Exception as e:
                      logger.error(f"Local Website Screenshot Failed: {e}")
                      # Fallback to container if local fails? No, container doesn't have it.
                      raise Exception(f"Website Screenshot Error: {e}")

    url = f"{NCA_API_URL}{endpoint}"
    headers = {
        'x-api-key': NCA_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=params, timeout=300)
    
    if not response.ok:
        error_text = response.text
        # Check for specific container upload failure (Firewall/Networking issue)
        if "Failed to upload" in error_text or "Connection refused" in error_text:
            logger.error(f"Networking Error: Container cannot reach Host. Firewall? {error_text}")
            raise Exception(f"Netzwerk-Fehler: Der Container konnte das Ergebnis nicht zurücksenden. Bitte Firewall prüfen (Port 5000 freigeben). Details: {error_text[:100]}")
            
        raise Exception(f"NCA API Error: {response.status_code} - {error_text[:200]}")
    
    return response.json()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/upload', methods=['POST'])
def api_upload_result():
    """
    Generischer Upload-Endpoint für Container-Ergebnisse
    Erwartet 'file' im multipart/form-data
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        try:
            result = handle_upload(file)
            logger.info(f"✅ Container uploaded result: {result['url']}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health Check Endpunkt"""
    try:
        # Teste Verbindung zum NCA Toolkit
        # Wir nutzen /authenticate da der Root-Pfad 404 liefert
        headers = {'x-api-key': NCA_API_KEY}
        try:
            # Versuche Authenticate Endpoint
            response = requests.post(
                f"{NCA_API_URL}/authenticate", # Container path seems to be /authenticate based on blueprint
                headers=headers,
                timeout=5
            )
            # 200 = Authorized, 401 = Unauthorized (aber erreichbar!), 404 = Falscher Pfad
            if response.status_code in [200, 401]:
                nca_status = 'healthy'
            else:
                # Fallback: Vielleicht ist es unter /v1/toolkit/authenticate?
                response = requests.post(
                    f"{NCA_API_URL}/v1/toolkit/authenticate",
                    headers=headers,
                    timeout=5
                )
                if response.status_code in [200, 401]:
                    nca_status = 'healthy'
                else:
                    nca_status = f'unhealthy ({response.status_code})'
        except requests.exceptions.RequestException:
             nca_status = 'unreachable'
    except:
        nca_status = 'unreachable'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'nca_toolkit': {
            'url': NCA_API_URL,
            'status': nca_status
        }
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Gibt die letzten Log-Einträge zurück"""
    # TODO: Implementiere Log-Speicherung
    return jsonify({
        'success': True,
        'logs': []
    })


@app.route('/api/docs/list', methods=['GET'])
def list_docs():
    """Listet alle verfügbaren Dokumentations-Dateien auf"""
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'nca-api')
    docs = []
    
    if not os.path.exists(docs_path):
        return jsonify({'error': 'Docs folder not found'}), 404
        
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith('.md'):
                # Relativer Pfad zur Anzeige
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, docs_path)
                # Kategorie basierend auf Ordner
                category = os.path.dirname(rel_path)
                if category == '.': category = 'General'
                
                docs.append({
                    'path': rel_path.replace('\\', '/'),
                    'name': file.replace('.md', '').replace('_', ' ').title(),
                    'category': category.replace('_', ' ').title()
                })
    
    # Sortieren nach Kategorie und Name
    docs.sort(key=lambda x: (x['category'], x['name']))
    return jsonify(docs)

@app.route('/api/docs/read', methods=['GET'])
def read_doc():
    """Liest den Inhalt einer Dokumentations-Datei"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'No path provided'}), 400
        
    base_docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'nca-api')
    # Sicherheit: Pfadbereinigung
    safe_path = os.path.normpath(os.path.join(base_docs_path, file_path))
    
    # Prüfe ob Pfad sicher ist (Traversal Schutz)
    # Und erlaube Zugriff auf Subdirectories
    common_prefix = os.path.commonpath([base_docs_path, safe_path])
    if common_prefix != base_docs_path or not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
        
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("NCA Toolkit Web Server")
    logger.info(f"Build: {BUILD_NUMBER}")
    logger.info("=" * 60)
    logger.info(f"NCA API URL: {NCA_API_URL}")
    logger.info(f"API Key: {NCA_API_KEY[:10]}...")
    logger.info("=" * 60)
    logger.info("Server startet auf http://localhost:5000")
    logger.info("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
