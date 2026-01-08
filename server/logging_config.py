"""
Logging Configuration für NCA Toolkit
Professionelles Log-Management mit Rotation und konfigurierbaren Levels
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

# Logging-Level aus Environment Variable (default: WARNING)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'

# Log-Verzeichnis
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Log-Datei mit Rotation
LOG_FILE = LOG_DIR / 'nca-server.log'

def setup_logging():
    """
    Konfiguriert Logging mit:
    - Rotating File Handler (max 10MB, 5 Backups)
    - Console Handler für Errors
    - Unterschiedliche Levels für Production/Development
    """
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    
    # Level basierend auf Environment
    if DEBUG_MODE:
        root_logger.setLevel(logging.DEBUG)
        console_level = logging.DEBUG
    else:
        root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.WARNING))
        console_level = logging.WARNING
    
    # Entferne existierende Handler
    root_logger.handlers.clear()
    
    # Format
    detailed_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # 1. Rotating File Handler (alle Logs >= WARNING)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(detailed_format)
    root_logger.addHandler(file_handler)
    
    # 2. Console Handler (nur Errors in Production, alles in Debug)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(simple_format if not DEBUG_MODE else detailed_format)
    root_logger.addHandler(console_handler)
    
    # 3. Debug File Handler (nur wenn DEBUG=true)
    if DEBUG_MODE:
        debug_file = LOG_DIR / 'debug.log'
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_file,
            maxBytes=50 * 1024 * 1024,  # 50 MB für Debug
            backupCount=3,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_format)
        root_logger.addHandler(debug_handler)
    
    # Externe Libraries leiser machen
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    # Startup-Meldung
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Logging configured: Level={LOG_LEVEL}, Debug={DEBUG_MODE}")
    logger.info(f"📁 Log file: {LOG_FILE}")
    
    return root_logger


def get_logger(name):
    """
    Erstellt einen Logger mit dem gegebenen Namen
    
    Args:
        name: Logger-Name (normalerweise __name__)
    
    Returns:
        logging.Logger
    """
    return logging.getLogger(name)


# Cleanup alte Logs (älter als 30 Tage)
def cleanup_old_logs(days=30):
    """Löscht Log-Dateien älter als X Tage"""
    import time
    
    if not LOG_DIR.exists():
        return
    
    cutoff = time.time() - (days * 86400)
    deleted = 0
    
    for log_file in LOG_DIR.glob('*.log*'):
        if log_file.stat().st_mtime < cutoff:
            try:
                log_file.unlink()
                deleted += 1
            except Exception:
                pass
    
    if deleted > 0:
        logger = logging.getLogger(__name__)
        logger.info(f"🧹 Cleaned up {deleted} old log files")


if __name__ == '__main__':
    # Test
    setup_logging()
    logger = get_logger(__name__)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print(f"\n✅ Logs written to: {LOG_FILE}")
