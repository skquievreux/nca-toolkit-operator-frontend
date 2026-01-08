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
import datetime
import logging
import threading
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Import unserer Services
from file_handler import handle_upload, init_upload_folder, cleanup_old_files, UPLOAD_FOLDER
from version import VERSION
from utils import get_lan_ip
import db_service
import local_processor  # Local FFmpeg support

# Import LLM/Workflow services AFTER load_dotenv
from llm_service import extract_intent_and_params
from workflow_engine import WorkflowEngine
from api_helpers import safe_api_call, validate_params

# Logging konfigurieren (mit Rotation und konfigurierbaren Levels)
from logging_config import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

# Flask App
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)

# Konfiguration
NCA_API_URL = os.getenv('NCA_API_URL', 'http://localhost:8080')
NCA_API_KEY = os.getenv('NCA_API_KEY', '343534sfklsjf343423')

# Upload-Ordner initialisieren
init_upload_folder()

# Datenbank initialisieren
db_service.init_db()

# Workflow Engine initialisieren
workflow_engine = WorkflowEngine(NCA_API_URL, NCA_API_KEY)

# Build Number (increment on each significant change)
BUILD_NUMBER = "2026.01.08.042"

# Self-Diagnosis: Check Network IP
HOST_IP = get_lan_ip()
logger.info(f"🌐 Running on Host IP: {HOST_IP}")


# Start Time für Uptime
START_TIME = time.time()

# Removed legacy in-memory jobs and job_lock
# All jobs are now persisted in SQLite via db_service

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
        
        # Log Request (nur in Debug-Mode)
        logger.debug(f"Proxy Request: {endpoint}")
        logger.debug(f"Params: {json.dumps(params, indent=2)}")
        
        # SPECIAL HANDLING: Test Endpoint -> Rufe Tools List oder Health auf
        if endpoint == '/v1/toolkit/test':
            # Versuche Tools List zu bekommen für Debugging
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
                    'timestamp': datetime.datetime.now().isoformat()
                }
            })

        # Request an NCA Toolkit API
        url = f"{NCA_API_URL}{endpoint}"
        headers = {
            'x-api-key': NCA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        logger.debug(f"Calling NCA API: {url} [POST]")
        
        response = requests.post(
            url,
            headers=headers,
            json=params,
            timeout=600  # 10 Minuten Timeout (war 300)
        )
        
        # Log Response (nur Errors und Debug)
        logger.debug(f"Response Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            logger.debug(f"Response: {json.dumps(result, indent=2)[:500]}")
            
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


@app.route('/api/history', methods=['GET'])
def get_history():
    """Gibt den Nachrichtenverlauf zurück"""
    limit = request.args.get('limit', default=50, type=int)
    try:
        conversations = db_service.get_history(limit=limit)
        
        # Format for frontend
        result = []
        for conv in conversations:
            messages = []
            for msg in conv.messages:
                messages.append({
                    'role': msg.role,
                    'text': msg.text,
                    'data': json.loads(msg.data) if msg.data else None,
                    'createdAt': msg.createdAt.isoformat()
                })
            
            result.append({
                'id': conv.id,
                'title': conv.title,
                'messages': messages,
                'createdAt': conv.createdAt.isoformat()
            })
            
        return jsonify({
            'success': True,
            'conversations': result
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """Returns a list of all active/completed jobs"""
    try:
        # Get from DB
        job_list = db_service.get_all_jobs(limit=100)
        
        # Convert objects to dicts for JSON
        result = []
        for job in job_list:
            j_dict = job.model_dump() if hasattr(job, 'model_dump') else job.dict()
            # Ensure JSON fields are parsed
            try: j_dict['params'] = json.loads(job.params) if isinstance(job.params, str) else job.params
            except: pass
            try: j_dict['result'] = json.loads(job.result) if isinstance(job.result, str) else job.result
            except: pass
            j_dict['created_at'] = job.createdAt.timestamp() if job.createdAt else 0
            result.append(j_dict)
            
        return jsonify({'success': True, 'jobs': result})
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a job"""
    try:
        job = db_service.get_job(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Convert to dict
        j_dict = job.model_dump() if hasattr(job, 'model_dump') else job.dict()
        try: j_dict['params'] = json.loads(job.params) if isinstance(job.params, str) else job.params
        except: pass
        try: j_dict['result'] = json.loads(job.result) if isinstance(job.result, str) else job.result
        except: pass
        j_dict['created_at'] = job.createdAt.timestamp() if job.createdAt else 0
        
        return jsonify({
            'success': True,
            'job': j_dict
        })
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """Listet alle verfügbaren Szenarien auf"""
    return jsonify({
        'success': True,
        'scenarios': workflow_engine.scenarios
    })

@app.route('/api/scenarios/save', methods=['POST'])
def save_scenarios():
    """Speichert die Szenarien-Konfiguration"""
    data = request.get_json()
    if not data or 'scenarios' not in data:
        return jsonify({'success': False, 'error': 'Daten fehlen'}), 400
        
    try:
        # Update in-memory
        workflow_engine.scenarios = data['scenarios']
        
        # Save to file
        with open('scenarios.json', 'w', encoding='utf-8') as f:
            json.dump(data['scenarios'], f, indent=2, ensure_ascii=False)
            
        logger.info("✅ Scenarios saved successfully")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving scenarios: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def process_scenario_async(job_id, scenario_id, inputs, conversation_id):
    """Hintergrund-Thread für Szenarien"""
    try:
        # Update progress
        db_service.update_job(job_id, {
            'progress': 10,
            'statusMessage': 'Initialisiere Szenario...'
        })
            
        # Execute
        results = workflow_engine.execute_scenario(scenario_id, inputs)
        
        # Save result message
        db_service.save_message(conversation_id, 'assistant', f"Szenario {scenario_id} abgeschlossen.", data={'results': results})
        
        # Update job status
        db_service.update_job(job_id, {
            'status': 'completed',
            'progress': 100,
            'statusMessage': 'Szenario erfolgreich!',
            'result': results
        })
            
        logger.info(f"✅ Scenario {scenario_id} completed successfully")
        
    except Exception as e:
        logger.exception(f"💥 Scenario {scenario_id} failed")
        db_service.update_job(job_id, {
            'status': 'failed',
            'statusMessage': str(e)
        })

@app.route('/api/scenarios/execute', methods=['POST'])
def execute_scenario():
    """Führt ein Szenario asynchron aus"""
    data = request.get_json()
    scenario_id = data.get('scenario_id')
    inputs = data.get('inputs', {})
    conversation_id = data.get('conversation_id')
    
    if not scenario_id:
        return jsonify({'success': False, 'error': 'Scenario ID fehlt'}), 400
        
    # Create conversation if missing
    if not conversation_id:
        conv = db_service.save_conversation(title=f"Workflow: {scenario_id}")
        conversation_id = conv.id
        
    # Create job in DB
    job = db_service.create_job(
        title=f"Scenario: {scenario_id}",
        endpoint='scenario',
        params={'scenario_id': scenario_id, 'inputs': inputs},
        status='processing'
    )
    
    # Save trigger message
    db_service.save_message(conversation_id, 'user', f"Starte Szenario: {scenario_id}", data={'inputs': inputs})
    
    # Start thread
    thread = threading.Thread(target=process_scenario_async, args=(job.id, scenario_id, inputs, conversation_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job.id,
        'conversation_id': conversation_id
    })


def process_job_async(job_id, user_message, conversation_id, uploaded_files):
    """Hintergrund-Thread für normale Requests"""
    try:
        # 1. Update Progress
        db_service.update_job(job_id, {
            'progress': 30,
            'statusMessage': 'Erkenne Intent...',
            'status': 'processing'
        })
        
        logger.debug("🤖 Calling LLM for intent extraction...")
        llm_result = extract_intent_and_params(user_message, uploaded_files)
        
        endpoint = llm_result.get('endpoint')
        params = llm_result.get('params', {})
        
        # VALIDATION: Check if endpoint was detected
        if not endpoint:
            error_msg = llm_result.get('reasoning', 'Konnte keine passende Aktion erkennen.')
            db_service.update_job(job_id, {
                'status': 'failed',
                'progress': 100,
                'statusMessage': error_msg
            })
            logger.warning(f"❌ No endpoint detected: {error_msg}")
            return
        
        # Update Job Endpoint if changed
        db_service.update_job(job_id, {'endpoint': endpoint})
        
        logger.debug(f"🧐 DEBUG: uploaded_files in thread: {uploaded_files}")
        logger.debug(f"🧐 DEBUG: Initial params: {params}")

        def resolve_params(parameters, uploads):
            if not parameters: return {}
            resolved = {}
            for k, v in parameters.items():
                if isinstance(v, str) and 'USE_UPLOADED_FILE_' in v:
                    # Clean the value
                    clean_v = v.strip()
                    try:
                        # Extract index assuming format USE_UPLOADED_FILE_0
                        parts = clean_v.split('_')
                        if len(parts) > 0 and parts[-1].isdigit():
                            idx = int(parts[-1])
                            if 0 <= idx < len(uploads):
                                resolved[k] = uploads[idx]['url']
                                logger.debug(f"📎 Resolved param '{k}': {v} -> {resolved[k]}")
                            else:
                                logger.warning(f"⚠️ Index {idx} out of range for uploaded_files (len={len(uploads)})")
                                resolved[k] = v
                        else:
                            resolved[k] = v
                    except Exception as e:
                        logger.error(f"Error resolving param {k}: {e}")
                        resolved[k] = v
                else:
                    resolved[k] = v
            return resolved

        # Resolve params with uploads
        if uploaded_files:
            logger.debug("🔧 Resolving parameters with uploads...")
            params = resolve_params(params, uploaded_files)
            logger.debug(f"✅ Resolved params: {params}")
            
            # Update params in DB (serialize to JSON string)
            db_service.update_job(job_id, {'params': json.dumps(params)})

        # 2. Handle YouTube downloads automatically
        if params:
            from youtube_service import is_youtube_url, download_youtube_video
            for key, value in params.items():
                if isinstance(value, str) and is_youtube_url(value):
                    db_service.update_job(job_id, {
                        'progress': 50,
                        'statusMessage': 'Lade YouTube-Video herunter...'
                    })
                    
                    download_result = download_youtube_video(value)
                    params[key] = download_result['url']
                    
                    db_service.update_job(job_id, {
                        'progress': 60,
                        'statusMessage': f'Video heruntergeladen: {download_result["title"]}'
                    })

        # 3. Special Case: Audio Concatenation (Local Override)
        nca_response = None
        if endpoint == '/combine-videos' and params.get('media_urls'):
            first_url = params['media_urls'][0] if params['media_urls'] else ''
            if first_url.endswith('.mp3') or first_url.endswith('.wav') or first_url.endswith('.aac'):
                logger.info("🎵 Handling audio concatenation locally")
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
            else:
                nca_response = call_nca_api(endpoint, params)
        
        # 4. Special Case: Audio Mixing (Local Override)
        elif (endpoint == '/v1/video/add/audio' or endpoint == '/audio-mixing') and params.get('video_url') and params.get('audio_url'):
            if local_processor.check_local_ffmpeg():
                 logger.info("🎬 Handling video/audio mixing locally")
                 from local_processor import local_audio_mixing
                 mixing_result = local_audio_mixing(params['video_url'], params['audio_url'])
                 nca_response = {
                    'success': True,
                    'output_url': mixing_result['url'],
                    'message': 'Video/Audio mixing completed locally',
                    'result': mixing_result
                 }

        # 5. Regular Case: Call API
        if not nca_response:
            db_service.update_job(job_id, {
                'progress': 70,
                'statusMessage': f'Rufe {endpoint} auf...'
            })
            nca_response = call_nca_api(endpoint, params)
        
        # 6. Complete Job
        db_service.update_job(job_id, {
            'status': 'completed',
            'progress': 100,
            'statusMessage': 'Fertig!',
            'result': nca_response
        })
            
        # Save assistant response
        db_service.save_message(conversation_id, 'assistant', "Erfolg", data={
            'intent': llm_result,
            'result': nca_response
        })
        
        logger.debug(f"✅ Job {job_id} completed successfully")
        
    except Exception as e:
        logger.exception(f"💥 Job {job_id} failed")
        db_service.update_job(job_id, {
            'status': 'failed',
            'statusMessage': str(e)
        })

@app.route('/api/process', methods=['POST'])
def process_request():
    """Haupt-Endpunkt: Asynchron"""
    try:
        # Support both JSON and form-data
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '')
            conversation_id = data.get('conversation_id')
        else:
            user_message = request.form.get('message', '')
            conversation_id = request.form.get('conversation_id')
        
        logger.debug(f"📥 Received request: message='{user_message}', conversation_id={conversation_id}")
        logger.debug(f"📥 Request is_json: {request.is_json}")
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Keine Nachricht vorhanden'
            }), 400
        
        # Create or find conversation
        if not conversation_id:
            conv = db_service.save_conversation(title=user_message[:30] or "Neue Anfrage")
            conversation_id = conv.id
        else:
            try:
                # Check existance via DB service or just try to use it
                exists = db_service.get_history(limit=1) # Minimal check not available, assume valid or create new on error if needed
                if not conversation_id:
                     conv = db_service.save_conversation(title=user_message[:30] or "Neue Anfrage")
                     conversation_id = conv.id
            except:
                 pass
            
        # Save user message
        db_service.save_message(conversation_id, 'user', user_message)
        
        # Handle uploads immediately
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                try:
                    file_info = handle_upload(file)
                    uploaded_files.append(file_info)
                except Exception as e:
                    logger.error(f"Upload handle failed: {e}")
                    raise Exception(f"Datei-Upload fehlgeschlagen: {str(e)}")

        # Create Job in DB
        job = db_service.create_job(
            title=user_message[:50] or 'Request',
            endpoint='detecting...',
            params={'uploaded_files': uploaded_files},
            status='processing'
        )
        
        # Update initial progress
        db_service.update_job(job.id, {
            'progress': 20,
            'statusMessage': 'Anfrage vorbereitet...'
        })
            
        # Start background thread
        thread = threading.Thread(target=process_job_async, args=(job.id, user_message, conversation_id, uploaded_files))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'conversation_id': conversation_id,
            'uploaded_files': uploaded_files
        })
    except Exception as e:
        logger.exception("Error in process_request")
        return jsonify({
            'success': False,
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
            'timestamp': datetime.datetime.now().isoformat()
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

    # ---------------------------------------------------------
    # CALL NCA API WITH SAFE WRAPPER
    # ---------------------------------------------------------
    logger.info(f"🌐 Calling NCA API: {endpoint}")
    
    response = safe_api_call(
        endpoint=endpoint,
        params=params,
        nca_api_url=NCA_API_URL,
        nca_api_key=NCA_API_KEY,
        timeout=600,
        max_retries=3
    )
    
    if response['success']:
        logger.info(f"✅ API Success: {endpoint}")
        return response['data']
    else:
        error_msg = response.get('error', 'Unknown error')
        logger.error(f"❌ API Failed: {endpoint} - {error_msg}")
        raise Exception(error_msg)


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
        'timestamp': datetime.datetime.utcnow().isoformat(),
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
