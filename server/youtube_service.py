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
        
        # Determine format based on parameter
        # Use robust format strings that prefer mp4/m4a for better compatibility with FFmpeg
        format_spec = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        if format == 'bestaudio':
             format_spec = 'bestaudio[ext=m4a]/bestaudio/best'

        # Configure yt-dlp options for maximum reliability
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            # Use specific clients to bypass some 403 blocks
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'ios', 'mweb', 'android'],
                    'player_skip_unplayable': [True]
                }
            },
            # Common headers to behave like a browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }
        
        # Check if ffmpeg is available and tell yt-dlp where it is if possible
        ffmpeg_path = None
        try:
             import subprocess
             result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
             if result.returncode == 0:
                  logger.info("🎬 FFmpeg detected by yt-dlp")
                  # yt-dlp usually finds it in PATH, but we could explicitly set it if needed
        except:
             logger.warning("⚠️ FFmpeg NOT detected in PATH for yt-dlp")

        logger.info(f"🎬 Downloading with yt-dlp (Format: {format_spec})...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)
            
            # Get the actual filename (extension might change from template)
            filename = ydl.prepare_filename(info)
            
            # If the format selected was a merge (v+a), extension might be .mp4 even if template had none
            if not os.path.exists(filename):
                # Try finding file with any extension if exact match fails
                base_part = os.path.splitext(filename)[0]
                matches = list(Path(UPLOAD_FOLDER).glob(f"{os.path.basename(base_part)}.*"))
                if matches:
                    filename = str(matches[0])
                else:
                    raise FileNotFoundError(f"Downloaded file not found: {filename}")
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            file_size = os.path.getsize(filename)
            
            if file_size == 0:
                 raise RuntimeError("Downloaded file is empty (0 bytes)")

            logger.info(f"✅ Downloaded: {title} ({duration}s, {file_size} bytes)")
            
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
