
import requests
import sys
import os
import time

# Colors for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log(type, message):
    if type == "SUCCESS":
        print(f"{GREEN}[SUCCESS]{RESET} {message}")
    elif type == "ERROR":
        print(f"{RED}[ERROR]{RESET} {message}")
    elif type == "INFO":
        print(f"{YELLOW}[INFO]{RESET} {message}")
    else:
        print(message)

def test_docker_direct():
    """Tries to connect directly to the Docker container port (8080 by default)"""
    base_url = "http://localhost:8080"
    api_key = os.getenv("API_KEY", "change_me_to_secure_key_123")
    headers = {"x-api-key": api_key}
    
    log("INFO", f"Testing connectivity to Docker at {base_url}...")

    endpoints_to_test = [
        ("POST", "/authenticate", headers),
        ("POST", "/v1/toolkit/authenticate", headers),
        ("GET", "/", None)
    ]

    for method, path, headers_to_use in endpoints_to_test:
        url = f"{base_url}{path}"
        try:
            if method == "GET":
                response = requests.get(url, headers=headers_to_use, timeout=2)
            else:
                response = requests.post(url, headers=headers_to_use, timeout=2)
            
            if response.ok:
                log("SUCCESS", f"Docker reachable! {method} {path} returned {response.status_code}")
                return True
            elif response.status_code == 401:
                 log("SUCCESS", f"Docker reachable! {method} {path} returned 401 Unauthorized (Auth works, Key might be wrong)")
                 return True
            elif response.status_code == 404:
                 log("INFO", f"Docker reachable but {method} {path} returned 404 (Not Found)")
            else:
                 log("INFO", f"Docker reachable but {method} {path} returned {response.status_code}")
                 print(f"      Headers: {response.headers}")
                 print(f"      Content: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            pass # Keep trying other endpoints
        except Exception as e:
            log("ERROR", f"Error checking {url}: {e}")

    log("ERROR", "Could not connect to Docker container on any tested endpoint.")
    log("INFO", "Is the Docker container running? (docker ps)")
    return False

def test_flask_server():
    """Tries to connect to the Flask server (5000)"""
    url = "http://localhost:5000/api/health"
    log("INFO", f"Testing connection to Flask Server at {url}...")
    try:
        response = requests.get(url, timeout=2)
        if response.ok:
            data = response.json()
            log("SUCCESS", "Flask server is up and running!")
            
            # Check what Flask thinks about Docker
            nca_status = data.get('nca_toolkit', {}).get('status')
            if nca_status == 'healthy':
                log("SUCCESS", "Flask says Docker is HEALTHY.")
            else:
                log("ERROR", f"Flask says Docker is {nca_status}.")
            return True
        else:
            log("ERROR", f"Flask server returned status {response.status_code}")
            return False
    except Exception as e:
        log("ERROR", f"Could not connect to Flask server: {str(e)}")
        log("INFO", "Is the Flask server running? (python server/app.py)")
        return False

def main():
    print("="*60)
    print(" 🕵️  DIAGNOSTIC TOOL: Data Flow Connectivity")
    print("="*60)
    
    # 1. Check Docker
    docker_ok = test_docker_direct()
    print("-" * 30)
    
    # 2. Check Flask
    flask_ok = test_flask_server()
    print("-" * 30)
    
    print("SUMMARY")
    if docker_ok and flask_ok:
        log("SUCCESS", "Both systems seem reachable. Data flow should work.")
        print("\nNEXT STEP: Open http://localhost:5000/test_flow.html in your browser.")
    elif not docker_ok:
        log("ERROR", "Docker container is NOT reachable. Please run: docker-compose up -d")
    elif not flask_ok:
        log("ERROR", "Flask server is NOT reachable. Please start it: python server/app.py")
    
if __name__ == "__main__":
    main()
