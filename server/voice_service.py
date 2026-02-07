import os
import requests
import logging

logger = logging.getLogger(__name__)



# Common Voice IDs (Fallback)
VOICE_MAPPING = {
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Sam": "yoZ06aMxZJJ28mfd3POQ"
}

def get_available_voices():
    """
    Fetches the list of available voices from ElevenLabs.
    """
    api_key = os.getenv('ELEVENLABS_API_KEY', '')
    if not api_key:
        # Return fallback mapping if no API key
        return [{"name": name, "voice_id": vid, "category": "fallback"} for name, vid in VOICE_MAPPING.items()]

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        voices_data = response.json().get('voices', [])
        
        # Format for frontend
        return [{
            "name": v.get('name'),
            "voice_id": v.get('voice_id'),
            "category": v.get('category'),
            "preview_url": v.get('preview_url')
        } for v in voices_data]
    except Exception as e:
        logger.error(f"Failed to fetch ElevenLabs voices: {e}")
        # Return fallbacks on error
        return [{"name": name, "voice_id": vid, "category": "fallback"} for name, vid in VOICE_MAPPING.items()]

def text_to_speech(text, voice_id="Adam", output_filename="speech.mp3"):
    """
    Converts text to speech using ElevenLabs API.
    """
    logger.info(f"🎤 Starting TTS for text: {text[:50]}... using voice: {voice_id}")
    
    api_key = os.getenv('ELEVENLABS_API_KEY', '')
    
    if not api_key:
        logger.warning(f"ELEVENLABS_API_KEY not found in environment. Keys found: {[k for k in os.environ.keys() if 'API' in k]}")
        return {"status": "mock", "message": "TTS simulated because API key is missing"}

    # Map voice name to ID if it's a known name, otherwise assume it's already an ID
    voice = VOICE_MAPPING.get(voice_id, voice_id)
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Save audio file
        from file_handler import UPLOAD_FOLDER, init_upload_folder
        if not os.path.exists(UPLOAD_FOLDER):
            init_upload_folder()
            
        filepath = os.path.join(UPLOAD_FOLDER, output_filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # Return relative URL to allow frontend to prepend its backend base URL
        file_url = f"/uploads/{output_filename}"
        
        return {
            "status": "success",
            "file_url": file_url,
            "url": file_url,
            "filename": output_filename
        }
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {e}")
        return {"status": "error", "message": str(e)}
