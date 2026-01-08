import os
import logging
import uuid
import json
from pathlib import Path
from utils import get_lan_ip

logger = logging.getLogger(__name__)

from file_handler import UPLOAD_FOLDER

def is_youtube_url(url):
    """Check if URL is a YouTube URL"""
    return 'youtube.com' in url or 'youtu.be' in url

def normalize_youtube_url(url):
    """Simple normalization to handle basic URL variations"""
    if not url: return url
    # Remove tracking params and time offsets for better caching
    if 'youtube.com/watch' in url:
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'v' in params:
            return f"https://www.youtube.com/watch?v={params['v'][0]}"
    elif 'youtu.be/' in url:
        video_id = url.split('/')[-1].split('?')[0]
        return f"https://youtu.be/{video_id}"
    return url

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'youtube_cache.json')

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}
    return {}

def _save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save YouTube cache: {e}")

def download_youtube_video(url, format='best'):
    """
    Download YouTube video using yt-dlp Python API with caching
    """
    url = normalize_youtube_url(url)
    cache = _load_cache()
    
    # Check cache
    if url in cache:
        cached_data = cache[url]
        # Check if file still exists on disk
        if os.path.exists(cached_data.get('path', '')):
            logger.info(f"🚀 Cache hit for YouTube video: {cached_data.get('title', 'Unknown')}")
            # Update Host IP in case it changed
            host_ip = get_lan_ip()
            cached_data['url'] = f"http://{host_ip}:5000/uploads/{cached_data['filename']}"
            return cached_data
        else:
            logger.info(f"⚠️ Cache hit but file missing, re-downloading...")
            del cache[url]
            _save_cache(cache)

    logger.info(f"📥 Downloading YouTube video: {url}")
    
    # Generate unique filename
    video_id = str(uuid.uuid4())
    output_template = os.path.join(UPLOAD_FOLDER, f"{video_id}.%(ext)s")
    
    try:
        import yt_dlp
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format,
            'outtmpl': output_template,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
        }
        
        logger.info(f"🎬 Downloading with yt-dlp...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(url, download=True)
            
            # Get the actual filename
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Downloaded file not found: {filename}")
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            logger.info(f"✅ Downloaded: {title} ({duration}s)")
            
            # Generate URL that Docker container can access
            basename = os.path.basename(filename)
            host_ip = get_lan_ip()
            file_url = f"http://{host_ip}:5000/uploads/{basename}"
            
            result = {
                'filename': basename,
                'path': filename,
                'url': file_url,
                'title': title,
                'duration': duration,
                'size': os.path.getsize(filename),
                'size_mb': round(os.path.getsize(filename) / (1024 * 1024), 2)
            }
            
            # Save to cache
            cache[url] = result
            _save_cache(cache)
            
            return result
        
    except ImportError:
        logger.error("yt-dlp ist nicht installiert")
        raise RuntimeError("yt-dlp ist nicht installiert. Bitte installieren Sie es mit: pip install yt-dlp")
    
    except Exception as e:
        logger.exception("💥 YouTube download failed")
        raise RuntimeError(f"YouTube-Download fehlgeschlagen: {str(e)}")


def download_youtube_audio(url):
    """
    Download YouTube video as audio (best quality)
    
    Args:
        url: YouTube video URL
        
    Returns:
        Same as download_youtube_video()
    """
    logger.info(f"🎵 Downloading YouTube audio: {url}")
    return download_youtube_video(url, format='bestaudio')
