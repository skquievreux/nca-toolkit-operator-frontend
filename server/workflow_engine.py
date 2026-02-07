import json
import logging
import re
import requests
from llm_service import extract_intent_and_params, configure_gemini
import google.generativeai as genai
import api_helpers
from api_helpers import normalize_endpoint

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self, nca_api_url, nca_api_key):
        self.nca_api_url = nca_api_url
        self.nca_api_key = nca_api_key
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self):
        try:
            import os
            base_dir = os.path.dirname(__file__)
            scenarios_path = os.path.join(base_dir, 'scenarios.json')
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")
            return {}

    def resolve_variables(self, template, context):
        """Resolves {{var}} placeholders in strings or nested dicts"""
        if isinstance(template, str):
            # Simple regex to find {{step_id.key}} or {{input_param}}
            def replacer(match):
                path = match.group(1).split('.')
                val = context
                for part in path:
                    if isinstance(val, dict):
                        val = val.get(part)
                    else:
                        return match.group(0)
                return str(val) if val is not None else ""
            
            return re.sub(r'\{\{(.*?)\}\}', replacer, template)
        
        elif isinstance(template, dict):
            return {k: self.resolve_variables(v, context) for k, v in template.items()}
        
        elif isinstance(template, list):
            return [self.resolve_variables(i, context) for i in template]
        
        return template

    def execute_scenario(self, scenario_id, inputs):
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        context = inputs.copy()
        results = {}

        for step in scenario['steps']:
            logger.info(f"📍 Executing step: {step['id']} ({step['type']})")
            
            # Resolve parameters for this step
            resolved_params = self.resolve_variables(step.get('params', {}), context)
            
            step_result = None
            if step['type'] == 'nca_api':
                step_result = self._call_nca(step['endpoint'], resolved_params)
            elif step['type'] == 'llm_task':
                resolved_prompt = self.resolve_variables(step['prompt'], context)
                step_result = self._call_llm(resolved_prompt)
            elif step['type'] == 'voice_api':
                import voice_service
                import uuid
                output_fn = f"tts_{uuid.uuid4().hex[:8]}.mp3"
                step_result = voice_service.text_to_speech(
                    resolved_params.get('text', ''),
                    voice_id=resolved_params.get('voice', 'Adam'),
                    output_filename=output_fn
                )
            elif step['type'] == 'local_task':
                import local_processor
                func_name = step['function']
                func = getattr(local_processor, func_name)
                step_result = func(**resolved_params)
            
            # Save to context for next steps
            context[step['id']] = step_result
            results[step['id']] = step_result
            
            logger.info(f"✅ Step {step['id']} completed")

        return results

    def _call_nca(self, endpoint, params):
        """Robust calling of NCA API with validation and mapping"""
        # 0. Canonical normalization
        endpoint = normalize_endpoint(endpoint)
        
        logger.debug(f"🌐 Workflow step calling NCA: {endpoint}")
        
        # This will resolve aliases like /transcribe -> /v1/media/transcribe
        # and map parameter names automatically
        try:
            params = api_helpers.validate_and_map_params(endpoint, params)
        except ValueError as e:
            logger.error(f"❌ Workflow validation error: {e}")
            raise

        response = api_helpers.safe_api_call(
            endpoint=endpoint,
            params=params,
            nca_api_url=self.nca_api_url,
            nca_api_key=self.nca_api_key
        )
        
        if not response['success']:
            error_msg = response.get('error', 'Unknown error')
            logger.error(f"❌ Workflow step failed: {error_msg}")
            raise Exception(f"API Step failed ({endpoint}): {error_msg}")
            
        return response['data']

    def _call_llm(self, prompt):
        # Ensure Gemini is configured
        configure_gemini()
        
        # Using the latest Gemini model
        # Note: gemini-2.0-flash-exp might need specific scopes if using service accounts, 
        # but with direct API key it should work if configured.
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return {"text": response.text}
        except Exception as e:
            logger.error(f"LLM Step failed: {e}")
            if "insufficient authentication scopes" in str(e).lower():
                logger.error("Auth error detected - retrying with 1.5-flash")
                # Fallback or re-config if necessary
            raise
