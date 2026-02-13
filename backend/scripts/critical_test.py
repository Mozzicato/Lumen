#!/usr/bin/env python
"""
CRITICAL TEST: Verify each component works independently.
"""
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("CRITICAL COMPONENT TEST")
print("=" * 70)

# Test 1: OCR Service
print("\n[TEST 1] OCR Service Status...")
try:
    from app.services.ocr_service import PADDLE_AVAILABLE
    if PADDLE_AVAILABLE:
        print("✓ PaddleOCR INSTALLED")
    else:
        print("✗ PaddleOCR NOT INSTALLED (using fallback)")
except Exception as e:
    print(f"✗ OCR Import Error: {e}")

# Test 2: API Keys
print("\n[TEST 2] API Keys...")
try:
    from app.core.config import settings
    groq_key = settings.GROQ_API_KEY
    if groq_key and groq_key.startswith('sk_'):
        print(f"✓ GROQ_API_KEY present: {groq_key[:20]}...")
    else:
        print(f"✗ GROQ_API_KEY invalid or missing: {groq_key}")
except Exception as e:
    print(f"✗ Config Error: {e}")

# Test 3: LLM Service
print("\n[TEST 3] LLM Service Connection...")
try:
    import requests
    from app.core.config import settings
    
    test_input = "This is a test. E=mc^2. What is this?"
    
    print(f"  Sending test prompt to OpenRouter...")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/user/note-beautifier",
            "Content-Type": "application/json",
        },
        json={
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": test_input}
            ],
            "temperature": 0.2,
            "max_tokens": 200,
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        output = data["choices"][0]["message"]["content"]
        print(f"✓ LLM API WORKING!")
        print(f"  Input: {test_input}")
        print(f"  Output: {output[:100]}...")
    else:
        print(f"✗ LLM Error {response.status_code}: {response.text[:200]}")
    
except Exception as e:
    print(f"✗ LLM Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Full Pipeline Simulation
print("\n[TEST 4] Full Pipeline with Mock OCR...")
try:
    from app.services.ocr_service import perform_ocr
    from app.services.llm_service import clean_text_with_llm
    
    # Simulate OCR output
    mock_ocr_output = """
    Physics Notes - Lecture 5
    Date: 2024-02-12
    
    Topic: Quantum Mechanics
    
    Key Equation:
    Schrodinger Equation: i*h_bar * dPsi/dt = H_hat * Psi
    
    Where:
    - H_hat is the Hamiltonian operator
    - Psi is the wave function
    - h_bar is reduced Planck constant
    """
    
    print(f"  Simulating OCR output ({len(mock_ocr_output)} chars)...")
    
    print(f"  Sending to LLM for formatting...")
    formatted = clean_text_with_llm(mock_ocr_output)
    
    if formatted != mock_ocr_output:
        print(f"✓ LLM FORMATTING APPLIED!")
        print(f"  Original: {len(mock_ocr_output)} chars")
        print(f"  Formatted: {len(formatted)} chars")
        print(f"\n  Output preview:")
        print("  " + "\n  ".join(formatted.split("\n")[:10]))
    else:
        print(f"✗ LLM RETURNED SAME TEXT (API might have failed silently)")
        
except Exception as e:
    print(f"✗ Pipeline Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
