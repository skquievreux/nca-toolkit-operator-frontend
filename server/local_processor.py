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

def local_audio_mixing(video_url, audio_url, background_music_url=None, music_volume=0.2):
    """
    Mixes video and audio locally using FFmpeg.
    Supports optional background music.
    """
    video_path = url_to_path(video_url)
    audio_path = url_to_path(audio_url)
    bg_music_path = url_to_path(background_music_url) if background_music_url else None
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if bg_music_path and not os.path.exists(bg_music_path):
         logger.warning(f"Background music not found: {bg_music_path}, skipping.")
         bg_music_path = None

    output_filename = f"{uuid.uuid4()}_local_mixed.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    # Base command inputs
    inputs = ['-i', video_path, '-i', audio_path]
    
    if bg_music_path:
        inputs.extend(['-i', bg_music_path])
        # Mix voice (1:a) and music (2:a)
        # Music volume reduced, Voice clean
        # duration=shortest (cutoff at shortest input, usually voice/video)
        filter_complex = f"[2:a]volume={music_volume}[music];[1:a][music]amix=inputs=2:duration=shortest[aout]"
        maps = ['-map', '0:v:0', '-map', '[aout]']
    else:
        filter_complex = None
        maps = ['-map', '0:v:0', '-map', '1:a:0'] # Simple copy/map

    cmd = ['ffmpeg', '-y'] + inputs
    
    if filter_complex:
        cmd.extend(['-filter_complex', filter_complex])
    else:
        cmd.append('-c:v')
        cmd.append('copy') # Copy video stream if no complex filter on video
        # (If we use filter_complex for audio, we can still copy video usually, 
        # unless filter affects video. Here it doesn't.)
        # BUT: -c:v copy cannot be used with -filter_complex generally if mapping from filter? 
        # Actually it can if we map video from input 0.
        cmd.append('-c:v'); cmd.append('copy')

    cmd.extend(maps)
    cmd.append('-shortest') # Ensure we stop when the shortest stream ends (usually video or voice)
    cmd.append(output_path)
    
    logger.debug(f"🎬 Running Local FFmpeg: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"FFmpeg fehlgeschlagen: {result.stderr[:200]}")
            
        logger.info(f"✅ Local FFmpeg success: {output_path}")
        
        file_size = os.path.getsize(output_path)
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"
        
        return {
             'filename': output_filename,
             'stored_filename': output_filename,
             'url': file_url,
             'type': 'mp4',
             'size': file_size,
             'source': 'local_ffmpeg',
        }
        
    except Exception as e:
        logger.exception("Local processing failed")
        raise e

def create_thumbnail(video_url, timestamp="00:00:01"):
    """
    Erstellt ein Thumbnail aus einem Video an einem bestimmten Timestamp.
    """
    video_path = url_to_path(video_url)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    output_filename = f"thumb_{uuid.uuid4().hex[:8]}.jpg"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    cmd = [
        'ffmpeg', '-y',
        '-ss', timestamp,
        '-i', video_path,
        '-vframes', '1',
        '-q:v', '2',
        output_path
    ]
    
    logger.info(f"📸 Generating thumbnail: {video_path} @ {timestamp}")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        file_size = os.path.getsize(output_path)
        file_url = f"http://{HOST_IP}:5000/uploads/{output_filename}"
        
        return {
            'filename': output_filename,
            'url': file_url,
            'type': 'jpg',
            'size': file_size,
            'source': 'local_ffmpeg_thumbnail'
        }
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        raise Exception(f"Thumbnail generation failed: {e}")

def create_video_from_image(image_url, duration=5, width=1280, height=720, text_overlay=None, srt_path=None, font_name="Arial", zoom_pan=False):
    """
    Erstellt ein Video aus einem Bild (Slideshow/Loop).
    Skaliert das Bild (Cover/Crop).
    Optional: Text-Overlay (drawtext) ODER Subtitles (SRT).
    Optional: Zoom/Pan Effekt (Ken Burns).
    """
    image_path = url_to_path(image_url)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    output_filename = f"slideshow_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    # If zoom_pan is active, we use a different approach (complex filter)
    if zoom_pan:
        # Ken Burns Effect (Zoom slowly)
        # 1. Scale image to twice target resolution for smooth zoom
        # 2. zoompan: increase z by 0.0015 per frame
        # 3. d: duration in frames (duration * fps)
        total_frames = int(duration * 25)
        vf_chain = (
            f"scale=iw*2:-1,zoompan=z='min(zoom+0.0015,1.5)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps=25,"
            f"setpts=PTS-STARTPTS"
        )
        logger.warning(f"🔍 [VER5] ZOOM ACTIVE: {vf_chain}")
    else:
        # Static Scale/Crop Filter
        vf_chain = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1"
    
    # 1. SRT Subtitles (Preferred if available)
    if srt_path and os.path.exists(srt_path):
        # RELATIVE PATH workaround for Windows colon issues in FFmpeg filter
        try:
            rel_srt_path = os.path.relpath(srt_path, os.getcwd())
            safe_srt_path = rel_srt_path.replace("\\", "/")
            logger.info(f"🎞️ Using relative SRT path: {safe_srt_path}")
        except:
             # Fallback to absolute escaped if relative fails
             safe_srt_path = srt_path.replace("\\", "/").replace(":", "\\\\:")
             
        subtitle_filter = f"subtitles='{safe_srt_path}':force_style='Fontname={font_name},FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=1,MarginV=20'"
        vf_chain = vf_chain.rstrip(',') + f",{subtitle_filter}"
        logger.info(f"🎞️ Subtitle filter applied: {subtitle_filter}")

    # 2. Add Drawtext Filter if text is provided (Fallback/Overlay)
    elif text_overlay:
        # Sanitize text for FFmpeg (escape chars)
        sanitized_text = text_overlay.replace(":", "\\:").replace("'", "").replace('"', '').replace(",", "\\,")
        
        # Windows drive letter escaping: C:/Path -> C\:/Path
        font_path = "C\\:/Windows/Fonts/arial.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        if os.name == 'nt' and not os.path.exists("C:/Windows/Fonts/arial.ttf"):
             font_path = "C\\:/Windows/Fonts/seguisb.ttf" 
             if not os.path.exists("C:/Windows/Fonts/seguisb.ttf"):
                 font_path = "arial"

        drawtext = (
            f"drawtext=fontfile='{font_path}':text='{sanitized_text}':"
            f"fontcolor=white:fontsize=h/20:box=1:boxcolor=black@0.5:"
            f"boxborderw=5:x=(w-text_w)/2:y=h-(text_h*2)"
        )
        vf_chain = vf_chain.rstrip(',') + f",{drawtext}"

    logger.warning(f"🎬 [VER5] FINAL VF_CHAIN: {vf_chain}")
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', image_path,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-vf', vf_chain, 
        output_path
    ]
    
    logger.debug(f"🎬 Creating video from image (Overlay={bool(text_overlay)}): {' '.join(cmd)}")
    
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
             'source': 'local_ffmpeg_slideshow'
        }
    except Exception as e:
        logger.exception("Slideshow creation failed")
        raise e
def create_video_from_image_and_audio(image_url, audio_url, width=1280, height=720):
    """
    Kombiniert ein Bild und eine Audio-Datei direkt zu einem Video.
    Besonders nützlich für Recaps/Summaries.
    """
    logger.info(f"🎬 Local production: Image({image_url}) + Audio({audio_url})")
    
    # 1. Erstelle Slideshow aus dem Bild (Dauer wird automatisch an Audio angepasst in step 2)
    # Aber wir brauchen erstmal ein Video-Gerüst.
    # Einfacher: Nutze direkt mixing logic oder einen One-Shot FFmpeg Call.
    
    from rss_service import get_audio_duration
    audio_path = url_to_path(audio_url)
    duration = get_audio_duration(audio_path)
    
    # Nutze vorhandene Funktionen für Workflow-Reaktivität
    video_stage = create_video_from_image(image_url, duration=duration, width=width, height=height)
    return local_audio_mixing(video_stage['url'], audio_url)
