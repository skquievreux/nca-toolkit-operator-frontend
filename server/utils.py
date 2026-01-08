import socket
import logging

logger = logging.getLogger(__name__)

def get_lan_ip():
    """
    Detects the local LAN IP address of the host.
    Falls back to 'host.docker.internal' if detection fails.
    """
    try:
        # Connect to an external DB (doesn't send data) to get the preferred interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"LAN IP detection failed: {e}. Falling back to host.docker.internal")
        return 'host.docker.internal'
