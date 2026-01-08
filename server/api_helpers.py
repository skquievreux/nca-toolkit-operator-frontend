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


def validate_params(endpoint: str, params: Dict[str, Any]) -> Optional[str]:
    """
    Validiert Parameter für einen Endpunkt.
    
    Args:
        endpoint: API-Endpunkt
        params: Parameter-Dictionary
        
    Returns:
        None wenn OK, sonst Fehlermeldung
    """
    
    # Definiere erforderliche Parameter pro Endpunkt
    required_params = {
        '/audio-mixing': ['video_url', 'audio_url'],
        '/v1/video/add/audio': ['video_url', 'audio_url'],
        '/combine-videos': ['media_urls'],
        '/v1/video/concatenate': ['video_urls'],
        '/media-to-mp3': ['media_url'],
        '/v1/media/convert/mp3': ['media_url'],
        '/transcribe': ['media_url'],
        '/v1/media/transcribe': ['media_url'],
        '/gdrive-upload': ['file_url'],
    }
    
    if endpoint not in required_params:
        return None  # Keine Validierung für unbekannte Endpunkte
    
    missing = []
    for param in required_params[endpoint]:
        if param not in params or not params[param]:
            missing.append(param)
    
    if missing:
        return f"Fehlende Parameter: {', '.join(missing)}"
    
    return None


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def is_retriable_error(error_response: Dict[str, Any]) -> bool:
    """Prüft ob ein Fehler retry-bar ist"""
    return error_response.get('retry', False)


def get_error_message(error_response: Dict[str, Any]) -> str:
    """Extrahiert Fehlermeldung aus Response"""
    return error_response.get('error', 'Unknown error')
