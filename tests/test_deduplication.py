import requests
import os
import hashlib
import time

BASE_URL = "http://localhost:5000/api/process"
TEST_FILE_CONTENT = b"This is a unique test content for deduplication verification." + os.urandom(16)
TEST_FILENAME = "test_dedup.txt"

def create_dummy_file():
    with open(TEST_FILENAME, "wb") as f:
        f.write(TEST_FILE_CONTENT)
    return TEST_FILENAME

def upload_file(filename):
    print(f"Uploading {filename}...")
    with open(filename, 'rb') as f:
        files = {'files': (filename, f, 'text/plain')}
        data = {'message': 'Test Upload', 'conversation_id': 'test_dedup'}
        response = requests.post(BASE_URL, files=files, data=data)
        
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
        return None
        
    return response.json()

def test_deduplication():
    print("--- Starting Deduplication Test ---")
    filename = create_dummy_file()
    
    # 1. First Upload
    print("\n1. First Upload:")
    result1 = upload_file(filename)
    if not result1 or not result1.get('uploaded_files'):
        print("First upload failed.")
        return False
        
    file1_info = result1['uploaded_files'][0]
    print(f"Stored as: {file1_info['stored_filename']}")
    print(f"Hash: {file1_info.get('hash')}")
    
    # 2. Second Upload (Same Content)
    print("\n2. Second Upload (Same Content):")
    result2 = upload_file(filename)
    if not result2 or not result2.get('uploaded_files'):
        print("Second upload failed.")
        return False
        
    file2_info = result2['uploaded_files'][0]
    print(f"Stored as: {file2_info['stored_filename']}")
    print(f"Hash: {file2_info.get('hash')}")
    
    # Verification
    if file1_info['stored_filename'] == file2_info['stored_filename']:
        print("\n✅ SUCCESS: Files are identical (deduplicated).")
        print(f"Both point to: {file1_info['url']}")
        os.remove(filename)
        return True
    else:
        print("\n❌ FAILURE: Files are different (duplication occurred).")
        print(f"File 1: {file1_info['stored_filename']}")
        print(f"File 2: {file2_info['stored_filename']}")
        os.remove(filename)
        return False

if __name__ == "__main__":
    test_deduplication()
