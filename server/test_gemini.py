import os
import google.generativeai as genai
import time
import requests

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
AUDIO_URL = "https://cdn.unlock-your-song.de/acid-monk/hooks/1768577804222-RV_Badminton--federball_1.2.0_hook-001.mp3"

def test_gemini_transcription():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    
    # Download file for Gemini
    filename = "test_audio.mp3"
    print(f"Downloading {AUDIO_URL}...")
    try:
        response = requests.get(AUDIO_URL)
        with open(filename, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Download error: {e}")
        return
    
    print("Uploading to Gemini...")
    try:
        audio_file = genai.upload_file(filename, mime_type="audio/mpeg")
        print(f"Uploaded file: {audio_file.name}, URI: {audio_file.uri}")
    except Exception as e:
        print(f"Upload error: {e}")
        return
    
    # Wait for processing
    print("Waiting for processing", end="")
    while audio_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        audio_file = genai.get_file(audio_file.name)
    
    if audio_file.state.name == "FAILED":
        print("\nFile processing FAILED")
        return

    print("\nFile ready. Transcribing...")
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Transcribe this audio. Return ONLY the synchronized SRT content. No talk, no markdown. Start directly with the first subtitle."
        
        # Using explicit Part format for better compatibility
        response = model.generate_content([
            prompt,
            {
                "mime_type": audio_file.mime_type,
                "file_uri": audio_file.uri
            }
        ])
        
        print("SRT Content Sample:")
        print(response.text[:1000])
        
        # Save to file for verification
        with open("test_output.srt", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("\n✅ Full SRT saved to test_output.srt")
        
    except Exception as e:
        print(f"Generation error: {e}")
    
    # Optional cleanup
    # genai.delete_file(audio_file.name)

if __name__ == "__main__":
    test_gemini_transcription()
