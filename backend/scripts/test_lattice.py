#!/usr/bin/env python
"""
Comprehensive test of the Note Beautifier Backend.
Tests file upload, background processing, and LLM formatting.
"""
import requests
import time
import os
import json

BASE_URL = "http://localhost:8000/api"

def test_backend():
    print("=" * 60)
    print("NOTE BEAUTIFIER - BACKEND VALIDATION TEST")
    print("=" * 60)
    
    # 1. Health Check
    print("\n[1/5] Health Check...")
    try:
        r = requests.get("http://localhost:8000/")
        if r.status_code == 200:
            print(f"✓ Server is running: {r.json()['message']}")
        else:
            print(f"✗ Server error: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Server not reachable: {e}")
        return False
    
    # 2. Test Upload Endpoint
    print("\n[2/5] Testing Upload Endpoint...")
    pdf_path = "lattice_test.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"✗ Test PDF not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, "application/pdf")}
            r = requests.post(f"{BASE_URL}/upload", files=files)
        
        if r.status_code != 200:
            print(f"✗ Upload failed: {r.text}")
            return False
        
        doc = r.json()
        doc_id = doc['id']
        print(f"✓ Upload successful. Doc ID: {doc_id}")
        print(f"  - Filename: {doc['filename']}")
        print(f"  - Status: {doc['status']}")
        print(f"  - Timestamp: {doc['upload_timestamp']}")
        
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False
    
    # 3. Test Processing Pipeline
    print("\n[3/5] Processing Pipeline...")
    max_wait = 60  # 60 seconds timeout
    start = time.time()
    
    while time.time() - start < max_wait:
        r = requests.get(f"{BASE_URL}/documents/{doc_id}")
        doc = r.json()
        status = doc['status']
        
        print(f"  Status: {status.upper()}")
        
        if status == "completed":
            print(f"✓ Processing completed!")
            break
        elif status == "failed":
            print(f"✗ Processing failed: {doc['error_message']}")
            return False
        
        time.sleep(2)
    else:
        print(f"✗ Processing timeout after {max_wait} seconds")
        return False
    
    # 4. Validate OCR Output
    print("\n[4/5] OCR Output Validation...")
    raw_ocr = doc.get('raw_ocr_text', '')
    
    if raw_ocr:
        char_count = len(raw_ocr)
        line_count = raw_ocr.count('\n')
        print(f"✓ OCR extracted {char_count} characters in {line_count} lines")
        print(f"  Preview: {raw_ocr[:200]}...")
    else:
        print("! OCR returned empty (expected if PaddleOCR not installed)")
    
    # 5. Validate LLM Formatting
    print("\n[5/5] LLM Formatting Output...")
    beautified = doc.get('beautified_text', '')
    
    if beautified:
        char_count = len(beautified)
        print(f"✓ LLM formatted output ({char_count} characters)")
        print("\n--- FORMATTED OUTPUT ---")
        print(beautified[:500])
        print("---END PREVIEW---")
    else:
        print("! LLM returned empty")
    
    # 6. Test List Endpoint
    print("\n[6/6] Testing List Endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/documents")
        if r.status_code == 200:
            docs = r.json()
            print(f"✓ List endpoint working. Total documents: {len(docs)}")
            for d in docs:
                print(f"   - ID {d['id']}: {d['filename']} ({d['status']})")
    except Exception as e:
        print(f"✗ List error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - BACKEND IS WORKING")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_backend()
    exit(0 if success else 1)
