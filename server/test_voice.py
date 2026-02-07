import os
import requests
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_elevenlabs():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY not found in .env file.")
        print("Please add 'ELEVENLABS_API_KEY=your_key' to your .env file.")
        return

    print(f"✅ Found API key (starts with {api_key[:5]}...)")
    
    server_url = "http://localhost:5000/api/process"
    payload = {
        "message": "Generiere eine Sprachausgabe mit dem Text: 'Badminon ist der geilste Sport der Welt' mit der Stimme Adam",
        "conversation_id": "test-voice-123"
    }
    
    print(f"🚀 Sending request to {server_url}...")
    try:
        response = requests.post(server_url, json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200:
            print("\n✅ Success! Check the 'uploads' folder for the generated mp3.")
        else:
            print("\n❌ Failed. Check server logs for details.")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_elevenlabs()
