import json
import unittest
from unittest.mock import patch, MagicMock
from server.workflow_engine import WorkflowEngine

class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        self.engine = WorkflowEngine("http://mock-api", "mock-key")
        # Injection of mock scenarios
        self.engine.scenarios = {
            "test_scenario": {
                "steps": [
                    {
                        "id": "step1",
                        "type": "nca_api",
                        "endpoint": "/step1",
                        "params": { "input": "{{user_val}}" }
                    },
                    {
                        "id": "step2",
                        "type": "llm_task",
                        "prompt": "Process this: {{step1.output}}"
                    }
                ]
            }
        }

    @patch('server.workflow_engine.requests.post')
    @patch('server.workflow_engine.genai.GenerativeModel')
    def test_variable_resolution_and_execution(self, mock_genai, mock_post):
        # Setup mocks
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"output": "hello from step1"}
        mock_post.return_value = mock_resp
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "Processed hello"
        mock_genai.return_value = mock_model

        # Execute
        results = self.engine.execute_scenario("test_scenario", {"user_val": "start"})

        # Assertions
        self.assertEqual(results['step1']['output'], "hello from step1")
        self.assertEqual(results['step2']['text'], "Processed hello")
        
        # Verify call parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['input'], "start")

if __name__ == '__main__':
    unittest.main()
