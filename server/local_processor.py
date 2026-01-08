import os
import subprocess
import uuid
import logging
from file_handler import UPLOAD_FOLDER
from youtube_service import download_youtube_video
from utils import get_lan_ip

HOST_IP = get_lan_ip()

logger = logging.getLogger(__name__)

def check_local_ffmpeg():
    """Checks if FFmpeg is installed and returns True/False"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# ------------------------------
# LOCAL WEBSITE SCREENSHOT
# ------------------------------
def create_website_screenshot(url, width=1920, height=1080):
    """
    Erstellt einen Screenshot einer Webseite mit Selenium
    """
    logger.info(f"📸 Generating website screenshot for: {url}")
    
    output_filename = f"screenshot_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--window-size={width},{height}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Setup WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            import time
            time.sleep(2) 
            driver.save_screenshot(output_path)
            logger.info(f"✅ Screenshot saved to {output_path}")
        finally:
            driver.quit()

        return {
            'filename': output_filename,
            'url': f"http://{HOST_IP}:5000/uploads/{output_filename}",
            'type': 'png',
            'size': os.path.getsize(output_path),
            'source': 'local_selenium',
            'stored_filename': output_filename
            # NO job_id for sync tasks!
        }

    except Exception as e:
        logger.error(f"❌ Screenshot failed: {e}")
        raise Exception(f"Failed to create screenshot: {str(e)}")

def url_to_path(url):
    """Converts a localhost/upload URL to a local filesystem path"""
    if not url:
        return None
    # Extract filename from URL (assuming .../uploads/filename.ext)
    filename = url.split('/')[-1]
    return os.path.join(UPLOAD_FOLDER, filename)

def local_audio_mixing(video_url, audio_url):
    """
    Mixes video and audio locally using FFmpeg.
    Accepts URLs, converts to paths, processes, returns result dict.
    """
    video_path = url_to_path(video_url)
    audio_path = url_to_path(audio_url)
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_filename = f"{uuid.uuid4()}_local_mixed.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    # Command: ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest output.mp4
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ]
    
    logger.debug(f"🎬 Running Local FFmpeg: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"FFmpeg fehlgeschlagen: {result.stderr[:200]}")
            
        logger.info(f"✅ Local FFmpeg success: {output_path}")
        
        file_size = os.path.getsize(output_path)
        
        # Always use HOST_IP for container compatibility
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"
        
        return {
             'filename': output_filename,
             'stored_filename': output_filename,
             'url': file_url,
             'type': 'mp4',
             'size': file_size,
             'source': 'local_ffmpeg',
             'source': 'local_ffmpeg'
             # 'job_id': str(uuid.uuid4()) # REMOVED: Sync tasks should not trigger polling
        }
        
    except Exception as e:
        logger.exception("Local processing failed")
        raise e

def create_thumbnail(video_url, time_offset="00:00:01"):
    """
    Creates a thumbnail from a video file using local FFmpeg.
    """
    video_path = url_to_path(video_url)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Output filename
    output_filename = f"{uuid.uuid4()}_thumbnail.jpg"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 output.jpg
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-ss', time_offset,
        '-vframes', '1',
        output_path
    ]

    logger.debug(f"📸 Generating Thumbnail: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"Thumbnail generation failed: {result.stderr[:200]}")

        file_size = os.path.getsize(output_path)
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"

        return {
             'filename': output_filename,
             'stored_filename': output_filename,
             'url': file_url,
             'type': 'jpg',
             'size': file_size,
             'source': 'local_ffmpeg',
             'source': 'local_ffmpeg'
             # 'job_id': str(uuid.uuid4()) # REMOVED: Sync tasks should not trigger polling
        }
    except Exception as e:
        logger.exception("Thumbnail generation failed")
        raise e
def local_audio_concat(audio_urls):
    """
    Concatenates multiple audio files locally using FFmpeg.
    """
    audio_paths = [url_to_path(url) for url in audio_urls]
    for p in audio_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Audio file not found: {p}")

    output_filename = f"concat_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Use concat demuxer if many files, or simple concat filter
    # For now, let's use the complex filter or simple concat protocol
    # Simple approach for a few files:
    # ffmpeg -i i1.mp3 -i i2.mp3 -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" out.mp3
    
    inputs = []
    for p in audio_paths:
        inputs.extend(['-i', p])
    
    filter_complex = "".join([f"[{i}:a]" for i in range(len(audio_paths))])
    filter_complex += f"concat=n={len(audio_paths)}:v=0:a=1[out]"
    
    cmd = ['ffmpeg', '-y'] + inputs + ['-filter_complex', filter_complex, '-map', '[out]', output_path]

    logger.debug(f"🎤 Concatenating Audio: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"Audio concatenation failed: {result.stderr[:200]}")

        file_size = os.path.getsize(output_path)
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"

        return {
             'filename': output_filename,
             'stored_filename': output_filename,
             'url': file_url,
             'type': 'mp3',
             'size': file_size,
             'source': 'local_ffmpeg'
        }
    except Exception as e:
        logger.exception("Audio concatenation failed")
        raise e

def create_video_from_image_and_audio(image_url, audio_url):
    """
    Erstellt ein Video aus einem Standbild und einer Audiodatei.
    Perfekt für Zusammenfassungen oder Podcasts mit Thumbnail.
    """
    image_path = url_to_path(image_url)
    audio_path = url_to_path(audio_url)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_filename = f"recap_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    # ffmpeg -loop 1 -i image.jpg -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest out.mp4
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]
    
    logger.debug(f"🎬 Creating video from image+audio: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"Video-Erstellung fehlgeschlagen: {result.stderr[:200]}")
            
        file_size = os.path.getsize(output_path)
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"
        
        return {
             'filename': output_filename,
             'url': file_url,
             'type': 'mp4',
             'size': file_size,
             'source': 'local_ffmpeg_recap'
        }
    except Exception as e:
        logger.exception("Recap video creation failed")
        raise e
