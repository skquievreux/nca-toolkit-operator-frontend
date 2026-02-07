import requests
import os
import json
import feedparser

NCA_API_URL = os.environ.get('NCA_API_URL', 'http://localhost:8080')
NCA_API_KEY = os.environ.get('NCA_API_KEY', '343534sfklsjf343423')
RSS_URL = "https://acidmonk.unlock-your-song.de/api/rss/racket-voice"

def get_real_audio():
    print(f"Fetching latest audio from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        entry = feed.entries[0]
        if hasattr(entry, 'enclosures'):
            for enc in entry.enclosures:
                if 'audio' in enc.type:
                    return enc.url
    return None

def test_transcribe():
    audio_url = get_real_audio()
    if not audio_url:
        print("Could not find audio URL")
        return
        
    print(f"Testing with valid URL: {audio_url}")
    try:
        url = f"{NCA_API_URL}/v1/media/transcribe"
        headers = {'x-api-key': NCA_API_KEY, 'Content-Type': 'application/json'}
        payload = {'media_url': audio_url}
        
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status: {resp.status_code}")
        if resp.ok:
            data = resp.json()
            # print(f"Response: {json.dumps(data, indent=2)}")
            print("Keys in response:", data.keys())
            if 'response' in data and data['response']:
                resp_obj = data['response']
                print("Keys in data['response']:", resp_obj.keys())
                print(f"SRT Content: {resp_obj.get('srt')}")
                print(f"SRT URL: {resp_obj.get('srt_url')}")
                segments = resp_obj.get('segments', [])
                if segments:
                    print("First segment:", segments[0])
                else:
                    print("No segments found")
        else:
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcribe()
