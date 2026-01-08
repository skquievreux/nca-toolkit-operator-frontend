from llm_service import extract_intent_and_params
import json

msg = "Spiele Audio1-Datei dreimal hintereinander ab"
files = [{'filename': 'audio-1.mp3', 'url': 'http://localhost:5000/uploads/audio-1.mp3', 'type': 'audio/mp3', 'size': 123}]

print("Testing message:", msg)
result = extract_intent_and_params(msg, files)
print(json.dumps(result, indent=2))

if result['endpoint'] == '/combine-videos' and len(result['params']['media_urls']) == 3:
    print("SUCCESS: Logic verified!")
else:
    print("FAILURE: Logic failed.")
