"""
File Handler - Upload und Storage Management
"""

import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import url_for

logger = logging.getLogger(__name__)

# Konfiguration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 500 * 1024 * 1024))  # 500MB default

ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'},
    'audio': {'mp3', 'wav', 'aac', 'm4a', 'ogg', 'flac'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'},
    'document': {'pdf', 'doc', 'docx', 'txt'}
}

ALL_ALLOWED = set().union(*ALLOWED_EXTENSIONS.values())


def init_upload_folder():
    """Erstellt Upload-Ordner falls nicht vorhanden"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logger.info(f"Created upload folder: {UPLOAD_FOLDER}")


def get_file_type(filename):
    """Bestimmt Dateityp anhand Extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    
    return 'unknown'


def allowed_file(filename):
    """Prüft ob Datei erlaubt ist"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED


def get_file_size_mb(size_bytes):
    """Konvertiert Bytes zu MB"""
    return round(size_bytes / (1024 * 1024), 2)


def handle_upload(file):
    """
    Verarbeitet File-Upload
    
    Args:
        file: Werkzeug FileStorage object
    
    Returns:
        {
            'filename': 'original.mp4',
            'stored_filename': 'abc123.mp4',
            'url': 'http://localhost:5000/uploads/abc123.mp4',
            'type': 'mp4',
            'file_type': 'video',
            'size': 1024000,
            'size_mb': 1.02
        }
    """
    
    if not file:
        raise ValueError("Keine Datei übergeben")
    
    if not allowed_file(file.filename):
        raise ValueError(f"Dateityp nicht erlaubt: {file.filename}")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        max_mb = get_file_size_mb(MAX_FILE_SIZE)
        actual_mb = get_file_size_mb(file_size)
        raise ValueError(f"Datei zu groß: {actual_mb}MB (max: {max_mb}MB)")
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower()
    stored_filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)
    
    # Save file
    init_upload_folder()
    file.save(filepath)
    
    logger.info(f"File uploaded: {original_filename} → {stored_filename} ({get_file_size_mb(file_size)}MB)")
    
    # Generate URL
    file_url = url_for('uploaded_file', filename=stored_filename, _external=True)
    
    return {
        'filename': original_filename,
        'stored_filename': stored_filename,
        'url': file_url,
        'type': ext,
        'file_type': get_file_type(original_filename),
        'size': file_size,
        'size_mb': get_file_size_mb(file_size)
    }


def cleanup_old_files(max_age_hours=24):
    """
    Löscht alte Dateien aus dem Upload-Ordner
    
    Args:
        max_age_hours: Maximales Alter in Stunden
    """
    import time
    
    if not os.path.exists(UPLOAD_FOLDER):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleanup: {deleted_count} files deleted")


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Max file size: {get_file_size_mb(MAX_FILE_SIZE)}MB")
    print(f"Allowed extensions: {ALL_ALLOWED}")
    
    init_upload_folder()
