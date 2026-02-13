import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000/api"

def test_upload_and_process():
    # 1. Check health
    try:
        r = requests.get("http://localhost:8000/")
        print(f"Health Check: {r.status_code}")
    except Exception as e:
        print("Server is not running. Please start it with 'uvicorn app.main:app --reload'")
        return

    # 2. Upload
    pdf_path = "sample_notes.pdf"
    if not os.path.exists(pdf_path):
        print("Plese run create_test_pdf.py first")
        return

    print("Uploading document...")
    with open(pdf_path, 'rb') as f:
        files = {'file': ("sample_notes.pdf", f, "application/pdf")}
        r = requests.post(f"{BASE_URL}/upload", files=files)
    
    if r.status_code != 200:
        print(f"Upload failed: {r.text}")
        return
        
    doc = r.json()
    doc_id = doc['id']
    print(f"Upload successful. Doc ID: {doc_id}. Status: {doc['status']}")
    
    # 3. Poll
    while True:
        time.sleep(2)
        r = requests.get(f"{BASE_URL}/documents/{doc_id}")
        doc = r.json()
        status = doc['status']
        print(f"Status: {status}")
        
        if status == "completed":
            print("\n--- FINAL RESULT ---")
            print(doc['beautified_text'])
            print("--------------------")
            break
        elif status == "failed":
            print(f"Processing failed: {doc['error_message']}")
            break

if __name__ == "__main__":
    test_upload_and_process()
