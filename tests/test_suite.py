import requests
import time
import sys
import json

BASE_URL = "http://localhost:5000"

def log(msg, type="INFO"):
    print(f"[{type}] {msg}")

def test_server_health():
    try:
        # Check if root or scenarios is reachable
        response = requests.get(f"{BASE_URL}/api/scenarios")
        if response.status_code == 200:
            log("Server Health Check: PASSED", "SUCCESS")
            return True
        else:
            log(f"Server Health Check: FAILED (Status: {response.status_code})", "ERROR")
            return False
    except Exception as e:
        log(f"Server Health Check: FAILED (Connection Refused)", "ERROR")
        return False

def test_job_creation():
    try:
        data = {
            'message': 'Test Request from Automated Suite',
            'conversation_id': 'test_suite_conv'
        }
        response = requests.post(f"{BASE_URL}/api/process", data=data)
        
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get('success') and json_data.get('job_id'):
                log(f"Job Creation: PASSED (Job ID: {json_data['job_id']})", "SUCCESS")
                return True
            else:
                log(f"Job Creation: FAILED (Invalid Response: {json_data})", "ERROR")
                return False
        else:
            log(f"Job Creation: FAILED (Status: {response.status_code})", "ERROR")
            return False
    except Exception as e:
        log(f"Job Creation: FAILED ({str(e)})", "ERROR")
        return False

def run_suite():
    log("Starting NCA Toolkit Verification Suite...", "INFO")
    
    # 1. Server Reachability
    if not test_server_health():
        log("CRITICAL: Server is not reachable. Aborting.", "ERROR")
        sys.exit(1)
        
    # 2. Job Creation (JSON Response Check)
    if not test_job_creation():
        log("CRITICAL: Job creation failed. JSON/API Error likely.", "ERROR")
        sys.exit(1)
        
    log("========================================", "INFO")
    log("✅ ALL SYSTEMS GO - Backend is Stable", "SUCCESS")
    log("========================================", "INFO")

if __name__ == "__main__":
    run_suite()
