"""
Endpoint Test Script
Tests NCA Toolkit endpoints to verify functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_endpoint(name, endpoint, data):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"Response: {json.dumps(result, indent=2)[:500]}")
            return True
        else:
            print(f"❌ FAILED")
            print(f"Error: {response.text[:500]}")
            return False
            
    except requests.Timeout:
        print(f"❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("NCA TOOLKIT ENDPOINT TESTS")
    print("="*60)
    
    results = {}
    
    # Test 1: Toolkit Test (should always work)
    results['toolkit_test'] = test_endpoint(
        "Toolkit Test",
        "/api/process",
        {
            "message": "Teste die API",
            "conversation_id": None
        }
    )
    
    time.sleep(2)
    
    # Test 2: Job Status (check if job was created)
    print("\n" + "="*60)
    print("Checking Jobs...")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/jobs", timeout=10)
        if response.ok:
            jobs = response.json().get('jobs', [])
            print(f"✅ Found {len(jobs)} jobs")
            if jobs:
                latest_job = jobs[0]
                print(f"\nLatest Job:")
                print(f"  ID: {latest_job.get('id')}")
                print(f"  Status: {latest_job.get('status')}")
                print(f"  Endpoint: {latest_job.get('endpoint')}")
                print(f"  Progress: {latest_job.get('progress')}%")
                results['job_creation'] = True
            else:
                print("⚠️  No jobs found")
                results['job_creation'] = False
        else:
            print(f"❌ Failed to get jobs: {response.status_code}")
            results['job_creation'] = False
    except Exception as e:
        print(f"❌ Error getting jobs: {e}")
        results['job_creation'] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
