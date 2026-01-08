"""
YouTube Download Service
Downloads YouTube videos using yt-dlp
"""

import os
import logging
import uuid
from pathlib import Path
from utils import get_lan_ip

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

def is_youtube_url(url):
    """Check if URL is a YouTube URL"""
    return 'youtube.com' in url or 'youtu.be' in url

def download_youtube_video(url, format='best'):
    """
    Download YouTube video using yt-dlp Python API
    
    Args:
        url: YouTube video URL
        format: Video format (best, worst, bestaudio, etc.)
        
    Returns:
        {
            'filename': 'video.mp4',
            'path': '/path/to/video.mp4',
            'url': 'http://localhost:5000/uploads/video.mp4',
            'title': 'Video Title',
            'duration': 123.45
        }
    """
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
            logger.info(f"📁 Saved to: {filename}")
            
            # Generate URL that Docker container can access
            basename = os.path.basename(filename)
            host_ip = get_lan_ip()
            file_url = f"http://{host_ip}:5000/uploads/{basename}"
            
            return {
                'filename': basename,
                'path': filename,
                'url': file_url,
                'title': title,
                'duration': duration,
                'size': os.path.getsize(filename),
                'size_mb': round(os.path.getsize(filename) / (1024 * 1024), 2)
            }
        
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
