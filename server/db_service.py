from prisma import Prisma
import logging
import json
import os

logger = logging.getLogger(__name__)

db = Prisma()

# ============================================================================
# CENTRAL SERIALIZATION FUNCTIONS
# ============================================================================

def serialize_job_data(data):
    """
    Serialisiert alle komplexen Datentypen für Prisma.
    
    Prisma erwartet für JSON-Felder (params, result) Strings.
    Diese Funktion konvertiert automatisch Dicts zu JSON-Strings.
    
    Args:
        data: Dictionary mit Job-Update-Daten
        
    Returns:
        Dictionary mit serialisierten Werten
    """
    if not data:
        return data
        
    result = {}
    for key, value in data.items():
        # Spezielle Behandlung für JSON-Felder
        if key in ['params', 'result']:
            if value is None:
                result[key] = None
            elif isinstance(value, str):
                # Bereits ein String, nicht nochmal serialisieren
                result[key] = value
            else:
                # Dict/List -> JSON String
                result[key] = json.dumps(value)
        else:
            # Alle anderen Felder unverändert
            result[key] = value
    
    return result


def safe_update_job(job_id, data):
    """
    Sicherer Wrapper für job.update() mit automatischer Serialisierung.
    
    Verhindert Prisma-Fehler durch falsche Datentypen.
    
    Args:
        job_id: Job-ID
        data: Update-Daten (werden automatisch serialisiert)
        
    Returns:
        Updated Job object
    """
    try:
        serialized_data = serialize_job_data(data)
        return db.job.update(
            where={'id': job_id},
            data=serialized_data
        )
    except Exception as e:
        logger.error(f"Failed to update job {job_id}: {e}")
        logger.error(f"Data: {data}")
        raise

def init_db():
    """Initializes and connects to the database"""
    try:
        db.connect()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

def save_conversation(title=None):
    """Creates a new conversation"""
    return db.conversation.create(data={'title': title})

def save_message(conversation_id, role, text, data=None):
    """Saves a message to a conversation"""
    return db.message.create(data={
        'conversationId': conversation_id,
        'role': role,
        'text': text,
        'data': json.dumps(data) if data else None
    })

def create_job(title, endpoint, params, status='pending', message_id=None):
    """Creates a new job"""
    return db.job.create(data={
        'title': title,
        'endpoint': endpoint,
        'params': json.dumps(params or {}),
        'status': status,
        'messageId': message_id,
        'progress': 0,
        'statusMessage': 'Initialized'
    })

def update_job(job_id, data):
    """
    Updates a job with partial data.
    
    DEPRECATED: Use safe_update_job() instead for automatic serialization.
    This function is kept for backwards compatibility.
    """
    return safe_update_job(job_id, data)

def get_job(job_id):
    """Retrieves a single job"""
    return db.job.find_unique(where={'id': job_id})

def get_all_jobs(limit=100):
    """Retrieves recent jobs"""
    return db.job.find_many(
        order={'createdAt': 'desc'},
        take=limit
    )

def save_asset(file_info):
    """Saves an asset record from handle_upload result"""
    return db.asset.create(data={
        'filename': file_info['stored_filename'],
        'originalName': file_info['filename'],
        'path': os.path.join('uploads', file_info['stored_filename']),
        'url': file_info['url'],
        'fileType': file_info['file_type'],
        'size': file_info['size'],
        'hash': file_info.get('hash')
    })

def get_asset_by_hash(file_hash):
    """Finds an asset by its hash"""
    return db.asset.find_unique(
        where={'hash': file_hash}
    )

def get_history(limit=50):
    """Retrieves recent conversations and messages"""
    return db.conversation.find_many(
        include={'messages': True},
        order={'createdAt': 'desc'},
        take=limit
    )
