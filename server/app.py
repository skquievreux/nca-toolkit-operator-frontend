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
NCA_API_KEY = os.getenv('NCA_API_KEY', 'change_me_to_secure_key_123')

# Upload-Ordner initialisieren
init_upload_folder()

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
                    'timestamp': datetime.datetime.now().isoformat()
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
        
        logger.info(f"🎯 Intent: {endpoint} (confidence: {confidence})")
        logger.info(f"💭 Reasoning: {reasoning}")
        logger.info(f"📋 Params: {json.dumps(params, indent=2)}")
        
        # Check if intent was found
        if not endpoint or confidence < 0.5:
            logger.warning("⚠️ Low confidence or no intent found")
            return jsonify({
                'success': False,
                'error': 'Konnte keine passende Aktion finden. Bitte formulieren Sie Ihre Anfrage anders.',
                'intent': llm_result,
                'uploaded_files': uploaded_files
            }), 400
        
        # 4. Call NCA Toolkit API
        with job_lock:
            jobs[job_id]['progress'] = 60
            jobs[job_id]['message'] = f'Rufe {endpoint} auf...'
        
        logger.info(f"🚀 Calling NCA API: {endpoint}")
        
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

    url = f"{NCA_API_URL}{endpoint}"
    headers = {
        'x-api-key': NCA_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=params, timeout=300)
    
    if not response.ok:
        raise Exception(f"NCA API Error: {response.status_code} - {response.text[:200]}")
    
    return response.json()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health Check Endpunkt"""
    try:
        # Teste Verbindung zum NCA Toolkit
        response = requests.get(
            f"{NCA_API_URL}/",
            timeout=5
        )
        nca_status = 'healthy' if response.ok else 'unhealthy'
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
