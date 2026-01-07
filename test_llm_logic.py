import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'server'))

from llm_service import extract_intent_and_params

test_cases = [
    {
        "name": "API Test",
        "message": "Teste die API",
        "files": [],
        "expected_endpoint": "/v1/toolkit/test"
    },
    {
        "name": "Screenshot",
        "message": "Mach einen Screenshot von https://google.com",
        "files": [],
        "expected_endpoint": "/v1/image/screenshot/webpage"
    },
    {
        "name": "Thumbnail",
        "message": "Erstelle ein Thumbnail",
        "files": [{'url': 'http://video.mp4', 'type': 'video/mp4'}],
        "expected_endpoint": "/v1/video/thumbnail"
    },
    {
        "name": "MP3 Convert",
        "message": "Konvertiere zu mp3",
        "files": [{'url': 'http://video.mp4', 'type': 'video/mp4'}],
        "expected_endpoint": "/v1/media/convert/mp3"
    },
    {
        "name": "Transcription",
        "message": "Transkribiere dieses Video",
        "files": [{'url': 'http://video.mp4', 'type': 'video/mp4'}],
        "expected_endpoint": "/v1/media/transcribe"
    },
    {
        "name": "Merge Audio Video",
        "message": "Füge Video und Audio zusammen",
        "files": [
            {'url': 'http://video.mp4', 'type': 'video/mp4'},
            {'url': 'http://audio.mp3', 'type': 'audio/mp3'}
        ],
        "expected_endpoint": "/v1/ffmpeg/compose"
    }
]

print("🔍 STARTING LLM LOGIC TEST\n")
all_passed = True

for case in test_cases:
    print(f"Testing: {case['name']}...")
    result = extract_intent_and_params(case['message'], case['files'])
    
    endpoint = result.get('endpoint')
    confidence = result.get('confidence', 0)
    
    if endpoint == case['expected_endpoint']:
        print(f"✅ PASS: {endpoint} (Conf: {confidence})")
    else:
        print(f"❌ FAIL: Expected {case['expected_endpoint']}, but got {endpoint}")
        print(f"   Reasoning: {result.get('reasoning')}")
        all_passed = False
    print("-" * 30)

if all_passed:
    print("\n🎉 ALL TESTS PASSED!")
else:
    print("\n⚠️ SOME TESTS FAILED.")
