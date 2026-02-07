import requests
import os
import json

NCA_API_URL = os.environ.get('NCA_API_URL', 'http://localhost:8080')
NCA_API_KEY = os.environ.get('NCA_API_KEY', '343534sfklsjf343423')
TEST_VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"

def test_add_captions():
    print(f"Testing /v1/video/add/captions with {TEST_VIDEO_URL}...")
    try:
        url = f"{NCA_API_URL}/v1/video/add/captions"
        headers = {'x-api-key': NCA_API_KEY, 'Content-Type': 'application/json'}
        payload = {'video_url': TEST_VIDEO_URL, 'language': 'de'}
        
        resp = requests.post(url, headers=headers, json=payload, timeout=600)
        print(f"Status: {resp.status_code}")
        if resp.ok:
            data = resp.json()
            print("Keys in response:", data.keys())
            if 'video_url' in data:
                print(f"Captioned Video: {data['video_url']}")
            elif 'response' in data:
                print(f"Captioned Video (in response): {data['response'].get('video_url')}")
        else:
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_add_captions()
