import os
import requests
import logging

logger = logging.getLogger(__name__)



# Common Voice IDs
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

def text_to_speech(text, voice_id="Adam", output_filename="speech.mp3"):
    """
    Converts text to speech using ElevenLabs API.
    """
    # Fetch key at runtime to ensure env vars are loaded
    api_key = os.getenv('ELEVENLABS_API_KEY', '')
    
    if not api_key:
        logger.warning(f"ELEVENLABS_API_KEY not found in environment. Keys found: {[k for k in os.environ.keys() if 'API' in k]}")
        return {"status": "mock", "message": "TTS simulated because API key is missing"}

    # Resolve Voice ID if it's a name
    if voice_id in VOICE_MAPPING:
        voice_id = VOICE_MAPPING[voice_id]


    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
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
            "filename": output_filename
        }
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {e}")
        return {"status": "error", "message": str(e)}
