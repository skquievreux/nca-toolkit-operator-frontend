"""
API Helper Functions
Zentrale Error-Handling und Retry-Logik für NCA API Calls
"""

import requests
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# ERROR HANDLING & RETRY LOGIC
# ============================================================================

class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message, status_code=None, retry=False):
        self.message = message
        self.status_code = status_code
        self.retry = retry
        super().__init__(self.message)


def safe_api_call(
    endpoint: str,
    params: Dict[str, Any],
    nca_api_url: str,
    nca_api_key: str,
    timeout: int = 600,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Sicherer Wrapper für NCA API Calls mit Error Handling und Retry-Logik.
    
    Args:
        endpoint: API-Endpunkt (z.B. '/v1/toolkit/test')
        params: Parameter-Dictionary
        nca_api_url: Basis-URL der NCA API
        nca_api_key: API-Key
        timeout: Timeout in Sekunden (default: 600)
        max_retries: Maximale Anzahl Wiederholungen (default: 3)
        
    Returns:
        Dictionary mit 'success', 'data'/'error', 'retry'
        
    Raises:
        APIError: Bei nicht-retriable Fehlern
    """
    
    url = f"{nca_api_url}{endpoint}"
    headers = {
        'x-api-key': nca_api_key,
        'Content-Type': 'application/json'
    }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"API Call (Attempt {attempt + 1}/{max_retries}): {endpoint}")
            
            response = requests.post(
                url,
                headers=headers,
                json=params,
                timeout=timeout
            )
            
            # Erfolgreiche Response
            if response.ok:
                result = response.json()
                logger.debug(f"API Success: {endpoint}")
                return {
                    'success': True,
                    'data': result,
                    'status_code': response.status_code
                }
            
            # HTTP-Fehler
            error_msg = f"API Error {response.status_code}: {response.text[:200]}"
            logger.warning(error_msg)
            
            # 4xx Fehler -> nicht retry-bar
            if 400 <= response.status_code < 500:
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'retry': False
                }
            
            # 5xx Fehler -> retry-bar
            last_error = error_msg
            
        except requests.Timeout:
            error_msg = f"Timeout after {timeout}s"
            logger.warning(f"{error_msg} (Attempt {attempt + 1}/{max_retries})")
            last_error = error_msg
            
        except requests.ConnectionError as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.warning(f"{error_msg} (Attempt {attempt + 1}/{max_retries})")
            last_error = error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception(f"API call failed: {endpoint}")
            # Unerwartete Fehler -> nicht retry-bar
            return {
                'success': False,
                'error': error_msg,
                'retry': False
            }
        
        # Warte vor nächstem Versuch (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            logger.info(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    # Alle Versuche fehlgeschlagen
    logger.error(f"API call failed after {max_retries} attempts: {endpoint}")
    return {
        'success': False,
        'error': last_error or "Unknown error",
        'retry': True,
        'attempts': max_retries
    }


# ============================================================================
# CENTRALIZED SCHEMA REGISTRY & VALIDATION
# ============================================================================

# Maps various endpoint names to the definitive canonical endpoint
ENDPOINT_MAP = {
    '/transcribe': '/v1/media/transcribe',
    '/v1/media/transcribe': '/v1/media/transcribe',
    '/media-to-mp3': '/v1/media/convert/mp3',
    '/v1/media/convert/mp3': '/v1/media/convert/mp3',
    '/audio-mixing': '/v1/video/add/audio',
    '/v1/video/add/audio': '/v1/video/add/audio',
    '/combine-videos': '/v1/video/concatenate',
    '/v1/video/concatenate': '/v1/video/concatenate',
    '/image-to-video': '/v1/image/convert/image_to_video',
    '/v1/image/convert/image_to_video': '/v1/image/convert/image_to_video',
    '/screenshot': '/v1/image/screenshot/webpage',
    '/v1/image/screenshot/webpage': '/v1/image/screenshot/webpage'
}

NCA_SCHEMA = {
    '/v1/media/transcribe': {
        'required': ['media_url'],
        'aliases': {'url': 'media_url', 'video_url': 'media_url', 'audio_url': 'media_url', 'file_url': 'media_url'}
    },
    '/v1/video/add/audio': {
        'required': ['video_url', 'audio_url'],
        'aliases': {'media_url': 'video_url', 'url': 'video_url'}
    },
    '/v1/video/concatenate': {
        'required': ['video_urls'],
        'aliases': {'media_urls': 'video_urls', 'urls': 'video_urls'}
    },
    '/v1/media/convert/mp3': {
        'required': ['media_url'],
        'aliases': {'url': 'media_url'}
    },
    '/v1/image/convert/image_to_video': {
        'required': ['image_url'],
        'aliases': {'url': 'image_url', 'media_url': 'image_url'}
    },
    '/v1/image/screenshot/webpage': {
        'required': ['url'],
        'aliases': {'site_url': 'url', 'web_url': 'url', 'media_url': 'url'}
    }
}

def normalize_endpoint(endpoint: str) -> str:
    """Mappt beliebige Endpunkt-Strings auf die kanonische Version"""
    return ENDPOINT_MAP.get(endpoint, endpoint)

def validate_and_map_params(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validiert Parameter gegen das Schema und mappt Aliase automatisch.
    Führt zu einem robusten Backend, das LLM-Varianz verzeiht.
    """
    # 1. Endpunkt normalisieren
    canonical_endpoint = normalize_endpoint(endpoint)
    
    if canonical_endpoint not in NCA_SCHEMA:
        logger.debug(f"ℹ️ No schema for canonical endpoint {canonical_endpoint}, passing as-is")
        return params

    schema = NCA_SCHEMA[canonical_endpoint]
    mapped_params = params.copy()

    # 2. Alias-Mapping
    for alias, target in schema.get('aliases', {}).items():
        if alias in mapped_params and target not in mapped_params:
            mapped_params[target] = mapped_params[alias]
            logger.debug(f"🔗 Mapped alias: {alias} -> {target}")

    # 3. Pflichtfeld-Check
    missing = [p for p in schema.get('required', []) if p not in mapped_params or not mapped_params[p]]
    if missing:
        # Letzter Versuch: Falls wir nur EINEN Parameter haben und nur EINEN brauchen, mappen wir ihn einfach
        if len(mapped_params) == 1 and len(schema.get('required', [])) == 1:
            val = next(iter(mapped_params.values()))
            target = schema.get('required', [])[0]
            mapped_params[target] = val
            logger.warning(f"💡 Auto-mapped single parameter to {target}")
        else:
            raise ValueError(f"❌ Missing required parameters for {canonical_endpoint}: {', '.join(missing)}")

    return mapped_params

def validate_params(endpoint: str, params: Dict[str, Any]) -> Optional[str]:
    """Legacy wrapper for compatibility"""
    try:
        validate_and_map_params(endpoint, params)
        return None
    except ValueError as e:
        return str(e)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def is_retriable_error(error_response: Dict[str, Any]) -> bool:
    """Prüft ob ein Fehler retry-bar ist"""
    return error_response.get('retry', False)


def get_error_message(error_response: Dict[str, Any]) -> str:
    """Extrahiert Fehlermeldung aus Response"""
    return error_response.get('error', 'Unknown error')
