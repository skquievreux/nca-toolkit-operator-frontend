import os
import requests
import logging

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')

def text_to_speech(text, voice_id="Adam", output_filename="speech.mp3"):
    """
    Converts text to speech using ElevenLabs API.
    """
    if not ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY not set. Returning mock success.")
        return {"status": "mock", "message": "TTS simulated because API key is missing"}

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Save audio file
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        filepath = os.path.join(upload_dir, output_filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # Determine URL
        from utils import get_lan_ip
        host_ip = get_lan_ip()
        file_url = f"http://{host_ip}:5000/uploads/{output_filename}"
        
        return {
            "status": "success",
            "file_url": file_url,
            "filename": output_filename
        }
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {e}")
        return {"status": "error", "message": str(e)}
