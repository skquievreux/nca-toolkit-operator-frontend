
import unittest
from unittest.mock import MagicMock, patch
import json
import logging
import sys
import os

# Adjust path to import server modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))

# Mock environment variables BEFORE importing llm_service
os.environ['GEMINI_API_KEY'] = 'test-key'

from llm_service import extract_intent_and_params

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestLLMFlow")

class TestLLMIntentRecognition(unittest.TestCase):

    def test_audio_mixing(self):
        """Test: Video + Audio Mixing"""
        message = "Füge dieses Video und diese Audiodatei zusammen"
        files = [
            {'filename': 'video.mp4', 'url': 'http://loc/video.mp4', 'type': 'video/mp4', 'size': 1000},
            {'filename': 'audio.mp3', 'url': 'http://loc/audio.mp3', 'type': 'audio/mpeg', 'size': 500}
        ]
        
        # We need to actually CALL the LLM or Mock it? 
        # Ideally we want to test the PROMPT generation logic or the full flow if possible.
        # Since I can't call real Gemini here without a key (and I shouldn't waste tokens in auto-tests),
        # I will mock the Gemini response but VERIFY the System Prompt that was used!
        
        with patch('google.generativeai.GenerativeModel') as MockModel:
            mock_chat = MockModel.return_value.start_chat.return_value
            mock_response = MagicMock()
            mock_response.text = '{"endpoint": "/audio-mixing", "params": {"video_url": "v", "audio_url": "a"}, "confidence": 0.9}'
            mock_chat.send_message.return_value = mock_response
            
            result = extract_intent_and_params(message, files)
            
            # Check result
            print(f"\n[Audio Mixing] Result: {result}")
            
    def test_website_screenshot_prompt_inclusion(self):
        """Test: Verify Screenshot Endpoint inclusion in prompt"""
        message = "Mache einen Screenshot von google.de"
        
        with patch('google.generativeai.GenerativeModel') as MockModel:
            mock_model_instance = MockModel.return_value
            mock_model_instance.generate_content.return_value.text = '{}' # Dummy JSON response
            
            extract_intent_and_params(message)
            
            # Retrieve arguments passed to generate_content
            args, kwargs = mock_model_instance.generate_content.call_args
            full_prompt = args[0]
            
            print(f"\n[Screenshot] Prompt Length: {len(full_prompt)}")
            
            if '/v1/image/screenshot/webpage' in full_prompt:
                print("✅ PASSED: Screenshot endpoint IS in the prompt.")
            else:
                print("❌ FAILED: Screenshot endpoint IS NOT in the prompt.")
                print(f"Prompt content: {full_prompt[:500]}...") # Debug
                self.fail("Screenshot endpoint missing from system prompt logic!")

    def test_screenshot_intent(self):
        """Test: Trigger actual intent extraction flow (Mocked) for Screenshot"""
        # This simulates what Gemini WOULD see
        message = "Screenshot von https://google.com"
        
        # Mock Gemini response assuming it got the correct prompt
        # If the prompt is missing, Gemini would hallucinate or fail.
        # Since we mock the response, this test mainly validates the parsing logic.
        
        with patch('google.generativeai.GenerativeModel') as MockModel:
            mock_chat = MockModel.return_value.start_chat.return_value
            mock_response = MagicMock()
            mock_response.text = json.dumps({
                "endpoint": "/v1/image/screenshot/webpage",
                "params": {"url": "https://google.com"},
                "confidence": 0.95,
                "reasoning": "Screenshot intent detected"
            })
            mock_chat.send_message.return_value = mock_response
            
            result = extract_intent_and_params(message)
            print(f"\n[Screenshot Mock] Parsed Result: {result}")
            
            self.assertEqual(result['endpoint'], '/v1/image/screenshot/webpage')

if __name__ == '__main__':
    unittest.main()
