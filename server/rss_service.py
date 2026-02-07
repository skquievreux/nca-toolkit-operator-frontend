import feedparser
import logging
import re

logger = logging.getLogger(__name__)

# Default Feed if none specified
DEFAULT_RSS_URL = "https://acidmonk.unlock-your-song.de/api/rss/racket-voice"

def get_audio_duration(file_path):
    """Gibt die Dauer einer Audio-Datei in Sekunden zurück (via ffprobe)"""
    try:
        import subprocess
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Could not detect audio duration: {e}. Falling back to 10s.")
        return 10.0

def get_rss_items(url=None, limit=10):
    """
    Parses any RSS feed and returns a list of items with metadata analysis.
    """
    target_url = url if url else DEFAULT_RSS_URL
    try:
        feed = feedparser.parse(target_url)
        if hasattr(feed, 'status') and feed.status >= 400:
             logger.error(f"Error fetching feed: HTTP {feed.status}")
             return []

        items = []
        for entry in feed.entries[:limit]:
            # --- Audio Extraction Heuristics ---
            audio_url = None
            # 1. Standard Enclosures
            if hasattr(entry, 'enclosures'):
                for enc in entry.enclosures:
                    if 'audio' in enc.type or enc.url.endswith(('.mp3', '.m4a', '.wav')):
                        audio_url = enc.url
                        break
            
            # 2. Media Content (MediaRSS)
            if not audio_url and hasattr(entry, 'media_content'):
                for content in entry.media_content:
                    if 'audio' in content.get('type', '') or content.get('url', '').endswith(('.mp3', '.m4a')):
                        audio_url = content['url']
                        break

            # --- Image Extraction Heuristics ---
            image_url = None
            # 1. itunes:image
            if hasattr(entry, 'itunes_image'):
                image_url = entry.itunes_image
            
            # 2. Media Content / Thumbnail
            if not image_url and hasattr(entry, 'media_content'):
                 for content in entry.media_content:
                    if 'image' in content.get('type', '') or content.get('medium') == 'image':
                        image_url = content['url']
                        break
            
            if not image_url and hasattr(entry, 'media_thumbnail'):
                image_url = entry.media_thumbnail[0]['url']

            # 3. Regex from Description/Summary
            if not image_url:
                search_text = entry.get('description', '') + entry.get('summary', '')
                img_match = re.search(r'<img [^>]*src="([^"]+)"', search_text)
                if img_match:
                    image_url = img_match.group(1)

            # Metadata properties for UI
            analysis = {
                "has_audio": audio_url is not None,
                "has_image": image_url is not None,
                "source_format": "atom" if hasattr(feed, 'version') and 'atom' in feed.version else "rss"
            }

            items.append({
                "title": entry.title,
                "description": entry.get('summary', entry.get('description', 'No description')),
                "image_url": image_url,
                "audio_url": audio_url,
                "link": entry.link,
                "id": entry.get('id', entry.link),
                "analysis": analysis
            })
        return items
    except Exception as e:
        logger.error(f"Error parsing RSS {target_url}: {e}")
        return []

def get_latest_rss_item(url=None):
    items = get_rss_items(url, limit=1)
    return items[0] if items else None

    print(get_latest_rss_item())

def generate_rss_video(image_url, audio_url, title="RSS Video", background_music_url=None, 
                       width=1280, height=720, music_volume=0.2, render_subtitles=False, 
                       zoom_pan=False, font_family="Arial", voice_id="Adam", language="de"):
    """
    Orchestriert die Erstellung eines Videos aus Bild und Audio.
    1. Transkribiert Audio zu SRT (wenn subtitles=True)
    2. Erstellt Video aus Bild (mit optionalem Ken Burns & SRT)
    3. Mischt Audio (Stimme + Musik)
    """
    import local_processor
    from file_handler import download_remote_file, UPLOAD_FOLDER
    import os
    import json
    import requests
    import uuid
    
    logger.info(f"🎬 generate_rss_video: {title} (Subtitles={render_subtitles}, Language={language})")
    
    # 1. Transkription (SRT)
    srt_path = None
    if render_subtitles:
        try:
            from llm_service import transcribe_media
            from local_processor import url_to_path
            
            # Audio (Voice)
            if not audio_url:
                 raise ValueError("Audio URL missing for transcription")

            audio_path = url_to_path(audio_url)
            logger.info(f"📝 Transcribing audio for subtitles (Language={language}): {audio_path}")
            
            # Pass language to transcription service
            transcription = transcribe_media(audio_path, language=language)
            
            srt_content = transcription.get('srt')
            
            if srt_content and len(str(srt_content)) > 10:
                srt_filename = f"subs_{uuid.uuid4().hex[:8]}.srt"
                srt_path = os.path.join(UPLOAD_FOLDER, srt_filename)
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                logger.info(f"✅ SRT generated and saved: {srt_path}")
            else:
                logger.warning("Centralized transcription did not return valid SRT content")
                        
        except Exception as e:
            logger.error(f"Error during transcription call: {e}")

    # 2. Download Assets
    try:
        # Image
        if not image_url:
            raise ValueError("Image URL missing")
            
        img_info = download_remote_file(image_url)
        local_image_url = img_info['url']
        local_image_path = img_info['local_path']
        
        # Audio (Voice)
        if not audio_url:
             raise ValueError("Audio URL missing")
             
        audio_info = download_remote_file(audio_url)
        local_audio_url = audio_info['url']
        local_audio_path = audio_info['local_path']
        
        # Background Music (Optional)
        local_bg_music_url = None
        if background_music_url:
            try:
                bg_info = download_remote_file(background_music_url)
                local_bg_music_url = bg_info['url']
            except Exception as e:
                logger.warning(f"Failed to download background music: {e}")
                
    except Exception as e:
        logger.error(f"Asset download failed: {e}")
        raise Exception(f"Asset download failed: {e}")

    # 1.5 Generate SRT if subtitles enabled
    srt_path = None
    if render_subtitles:
        try:
            from llm_service import transcribe_media
            logger.info("🎙️ Requesting high-precision transcription via centralized service...")
            
            # Use URL for container access (NCA Toolkit needs http://...)
            transcription = transcribe_media(local_audio_url, language="de")
            
            srt_content = transcription.get('srt')
            
            if srt_content and len(str(srt_content)) > 10:
                srt_filename = f"subs_{uuid.uuid4().hex[:8]}.srt"
                srt_path = os.path.join(UPLOAD_FOLDER, srt_filename)
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                logger.info(f"✅ SRT generated and saved: {srt_path}")
            else:
                logger.warning("Centralized transcription did not return valid SRT content")
                        
        except Exception as e:
            logger.error(f"Error during transcription call: {e}")

    # 2. Create Video from Image (Loop/Slideshow)
    try:
        # Detect actual duration of voice audio to match video length
        voice_duration = get_audio_duration(local_audio_path)
        logger.info(f"⏱️ Audio duration detected: {voice_duration}s")

        step1 = local_processor.create_video_from_image(
            local_image_url, 
            duration=voice_duration, 
            width=width, 
            height=height,
            text_overlay=title if not srt_path and render_subtitles else None,
            srt_path=srt_path,
            font_name=font_family,
            zoom_pan=zoom_pan
        )
        video_url = step1['url']
    except Exception as e:
        raise Exception(f"Video generation failed: {e}")

    # 3. Mix Audio (Voice + Music)
    try:
        step2 = local_processor.local_audio_mixing(
            video_url, 
            local_audio_url, 
            background_music_url=local_bg_music_url, 
            music_volume=music_volume
        )
        return step2
    except Exception as e:
        raise Exception(f"Audio mixing failed: {e}")
