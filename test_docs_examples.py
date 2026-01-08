
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Path adjust
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), 'server', '.env'))

from llm_service import extract_intent_and_params

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("DocsTest")

EXAMPLES = [
    {
        "name": "Audio Mix",
        "command": "Füge dieses Video und Audio zusammen",
        "files": [
            {"filename": "holiday.mp4", "url": "http://192.168.1.10/uploads/vid.mp4", "type": "video/mp4", "size": 1000},
            {"filename": "music.mp3", "url": "http://192.168.1.10/uploads/aud.mp3", "type": "audio/mpeg", "size": 500}
        ],
        "expected_endpoint": ["/audio-mixing", "/v1/video/add/audio"]
    },
    {
        "name": "MP3 Conversion",
        "command": "Konvertiere diese Datei zu MP3",
        "files": [{"filename": "podcast.wav", "url": "http://loc/pod.wav", "type": "audio/wav", "size": 1000}],
        "expected_endpoint": ["/media-to-mp3", "/v1/media/convert/mp3"]
    },
    {
        "name": "Audio Concat",
        "command": "Füge diese Audiodateien zusammen",
        "files": [
            {"filename": "i.mp3", "url": "http://loc/i.mp3", "type": "audio/mpeg", "size": 100},
            {"filename": "m.mp3", "url": "http://loc/m.mp3", "type": "audio/mpeg", "size": 100}
        ],
        "expected_endpoint": ["/v1/audio/concatenate"]
    },
    {
        "name": "Audio Loop",
        "command": "Spiele diese Datei dreimal hintereinander ab",
        "files": [{"filename": "beat.mp3", "url": "http://loc/b.mp3", "type": "audio/mpeg", "size": 100}],
        "expected_endpoint": ["/v1/audio/concatenate"]
    },
    {
        "name": "YouTube to MP3",
        "command": "https://youtube.com/watch?v=dQw4w9WgXcQ als MP3",
        "files": [],
        "expected_endpoint": ["/media-to-mp3", "/v1/media/convert/mp3"]
    },
    {
        "name": "Video Concat",
        "command": "Füge diese Videos zusammen",
        "files": [
            {"filename": "1.mp4", "url": "http://loc/1.mp4", "type": "video/mp4", "size": 100},
            {"filename": "2.mp4", "url": "http://loc/2.mp4", "type": "video/mp4", "size": 100}
        ],
        "expected_endpoint": ["/v1/video/concatenate"]
    },
    {
        "name": "Subtitles",
        "command": "Erstelle Untertitel für dieses Video",
        "files": [{"filename": "v.mp4", "url": "http://loc/v.mp4", "type": "video/mp4", "size": 100}],
        "expected_endpoint": ["/v1/video/add/captions"]
    },
    {
        "name": "Tone Swap",
        "command": "Tausche den Ton in diesem Video aus",
        "files": [
            {"filename": "v.mp4", "url": "http://loc/v.mp4", "type": "video/mp4", "size": 100},
            {"filename": "a.mp3", "url": "http://loc/a.mp3", "type": "audio/mpeg", "size": 100}
        ],
        "expected_endpoint": ["/v1/video/add/audio", "/audio-mixing"]
    },
    {
        "name": "Watermark",
        "command": "Füge dieses Logo als Wasserzeichen unten rechts hinzu",
        "files": [
            {"filename": "v.mp4", "url": "http://loc/v.mp4", "type": "video/mp4", "size": 100},
            {"filename": "l.png", "url": "http://loc/l.png", "type": "image/png", "size": 100}
        ],
        "expected_endpoint": ["/v1/video/add/watermark"]
    },
    {
        "name": "Cut / Trim",
        "command": "Schneide die ersten 5 Sekunden ab",
        "files": [{"filename": "v.mp4", "url": "http://loc/v.mp4", "type": "video/mp4", "size": 100}],
        "expected_endpoint": ["/v1/video/cut"]
    },
    {
        "name": "Transcribe",
        "command": "Transkribiere auf Deutsch",
        "files": [{"filename": "m.mp3", "url": "http://loc/m.mp3", "type": "audio/mpeg", "size": 100}],
        "expected_endpoint": ["/transcribe", "/v1/media/transcribe"]
    },
    {
        "name": "Screenshot",
        "command": "Mache einen Screenshot von google.de",
        "files": [],
        "expected_endpoint": ["/v1/image/screenshot/webpage"]
    },
    {
        "name": "Thumbnail",
        "command": "Erstelle ein Thumbnail von diesem Video",
        "files": [{"filename": "v.mp4", "url": "http://loc/v.mp4", "type": "video/mp4", "size": 100}],
        "expected_endpoint": ["/v1/video/thumbnail"]
    },
    {
        "name": "Status Check",
        "command": "Ist das System online?",
        "files": [],
        "expected_endpoint": ["/v1/toolkit/test"]
    }
]

def run_tests():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment or .env file.")
        return

    print(f"\n🚀 Running {len(EXAMPLES)} Examples from Documentation...\n")
    print("-" * 80)
    
    results = []
    
    for ex in EXAMPLES:
        print(f"Testing: {ex['name']} ('{ex['command']}')")
        try:
            result = extract_intent_and_params(ex['command'], ex['files'])
            endpoint = result.get('endpoint')
            confidence = result.get('confidence', 0)
            reasoning = result.get('reasoning', '')
            
            success = endpoint in ex['expected_endpoint']
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {status}")
            print(f"  Endpoint: {endpoint}")
            print(f"  Confidence: {confidence*100:.1f}%")
            print(f"  Reasoning: {reasoning}")
            
            results.append({
                "name": ex['name'],
                "success": success,
                "got": endpoint,
                "expected": ex['expected_endpoint'],
                "confidence": confidence
            })
        except Exception as e:
            print(f"  💥 ERROR: {str(e)}")
            results.append({"name": ex['name'], "success": False, "error": str(e)})
        
        print("-" * 80)

    summary_total = len(results)
    summary_passed = sum(1 for r in results if r['success'])
    print(f"\n🏁 Summary: {summary_passed}/{summary_total} PASSED")
    
    if summary_passed < summary_total:
        print("\n⚠️  Some examples failed! Check optimization options.")

if __name__ == "__main__":
    run_tests()
