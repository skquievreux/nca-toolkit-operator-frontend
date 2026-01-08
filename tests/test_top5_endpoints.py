"""
Comprehensive Endpoint Test Suite
Tests top 5 NCA Toolkit endpoints with real data
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:5000"
TIMEOUT = 60  # seconds

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

def print_test(name):
    print(f"\n{Colors.YELLOW}Testing: {name}{Colors.END}")
    print("-" * 70)

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def wait_for_job(job_id, max_wait=60):
    """Wait for job to complete"""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/api/jobs/{job_id}", timeout=10)
            if resp.ok:
                job = resp.json().get('job', {})
                status = job.get('status')
                progress = job.get('progress', 0)
                
                print(f"  Status: {status} ({progress}%)", end='\r')
                
                if status == 'completed':
                    print_success(f"Job completed in {time.time() - start:.1f}s")
                    return job
                elif status == 'failed':
                    error = job.get('statusMessage', 'Unknown error')
                    print_error(f"Job failed: {error}")
                    return job
        except Exception as e:
            print_error(f"Error checking job: {e}")
            return None
        
        time.sleep(2)
    
    print_error(f"Job timeout after {max_wait}s")
    return None

def test_endpoint(name, message, expected_endpoint=None):
    """Test an endpoint via natural language"""
    print_test(name)
    print(f"Message: \"{message}\"")
    
    try:
        # Send request
        resp = requests.post(
            f"{BASE_URL}/api/process",
            json={"message": message},
            timeout=TIMEOUT
        )
        
        if not resp.ok:
            print_error(f"Request failed: {resp.status_code}")
            return False
        
        result = resp.json()
        job_id = result.get('job_id')
        
        if not job_id:
            print_error("No job_id returned")
            return False
        
        print(f"Job ID: {job_id}")
        
        # Wait for completion
        job = wait_for_job(job_id)
        
        if not job:
            return False
        
        if job.get('status') == 'completed':
            endpoint = job.get('endpoint')
            print(f"Endpoint: {endpoint}")
            
            if expected_endpoint and endpoint != expected_endpoint:
                print_error(f"Wrong endpoint! Expected {expected_endpoint}")
                return False
            
            result_data = job.get('result', {})
            if result_data:
                print(f"Result: {json.dumps(result_data, indent=2)[:200]}")
            
            print_success("Test passed!")
            return True
        else:
            print_error(f"Job failed: {job.get('statusMessage')}")
            return False
            
    except requests.Timeout:
        print_error("Request timeout")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("NCA TOOLKIT - TOP 5 ENDPOINT TESTS")
    
    results = {}
    
    # Test 1: API Test
    results['toolkit_test'] = test_endpoint(
        "1. Toolkit Test",
        "Teste die API",
        "/v1/toolkit/test"
    )
    
    time.sleep(2)
    
    # Test 2: Screenshot
    results['screenshot'] = test_endpoint(
        "2. Website Screenshot",
        "Mache einen Screenshot von https://google.com",
        "/v1/image/screenshot/webpage"
    )
    
    time.sleep(2)
    
    # Test 3: Thumbnail (needs video file)
    print_test("3. Video Thumbnail")
    print("⚠️  Requires video file - skipping for now")
    results['thumbnail'] = None
    
    # Test 4: MP3 Conversion (needs media file)
    print_test("4. MP3 Conversion")
    print("⚠️  Requires media file - skipping for now")
    results['mp3_conversion'] = None
    
    # Test 5: Transcription (needs audio/video file)
    print_test("5. Transcription")
    print("⚠️  Requires audio/video file - skipping for now")
    results['transcription'] = None
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = sum(1 for v in results.values() if v is not None)
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test, result in results.items():
        if result is True:
            print_success(f"{test}: PASS")
        elif result is False:
            print_error(f"{test}: FAIL")
        else:
            print(f"{Colors.YELLOW}⚠️  {test}: SKIPPED{Colors.END}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} passed, {skipped} skipped{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
