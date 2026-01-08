from prisma import Prisma
import logging
import json
import os

logger = logging.getLogger(__name__)

db = Prisma()

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

def save_job(endpoint, params, result=None, status='pending', message_id=None):
    """Saves a job record"""
    return db.job.create(data={
        'endpoint': endpoint,
        'params': json.dumps(params),
        'result': json.dumps(result) if result else None,
        'status': status,
        'messageId': message_id
    })

def update_job_result(job_id, result, status='completed'):
    """Updates a job with its result"""
    return db.job.update(
        where={'id': job_id},
        data={
            'result': json.dumps(result),
            'status': status
        }
    )

def save_asset(file_info):
    """Saves an asset record from handle_upload result"""
    return db.asset.create(data={
        'filename': file_info['stored_filename'],
        'originalName': file_info['filename'],
        'path': os.path.join('uploads', file_info['stored_filename']), # Better to use logic or absolute?
        'url': file_info['url'],
        'fileType': file_info['file_type'],
        'size': file_info['size']
    })

def get_history(limit=50):
    """Retrieves recent conversations and messages"""
    return db.conversation.find_many(
        include={'messages': True},
        order={'createdAt': 'desc'},
        take=limit
    )
