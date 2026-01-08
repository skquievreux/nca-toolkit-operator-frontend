import sys
sys.path.insert(0, 'server')

from llm_service import extract_intent_and_params

# Simulate the user's request
message = "Bitte füge das Video und das Audio zu einer Datei zusammen"
uploaded_files = [
    {
        'filename': 'xAupGriFDKmrm3Q7To95U_output.mp4',
        'url': 'http://host.docker.internal:5000/uploads/abc123.mp4',
        'type': 'mp4',
        'size': 3000000
    },
    {
        'filename': 'ElevenLabs_2026-01-06T09_29_28_Arabella_pvc_sp100_s63_sb100_v3.mp3',
        'url': 'http://host.docker.internal:5000/uploads/def456.mp3',
        'type': 'mp3',
        'size': 110000
    }
]

result = extract_intent_and_params(message, uploaded_files)

import json
print(json.dumps(result, indent=2, ensure_ascii=False))
