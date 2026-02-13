import requests
from app.core.config import settings
import logging

# Using OpenRouter API (more flexible, supports multiple models)
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
LLM_MODEL = "meta-llama/llama-3.1-8b-instruct"  # Fast and good

SYSTEM_PROMPT = """
You are an expert document formatter and academic assistant. 
Your task is to take raw, messy text extracted from handwritten notes or PDF scans (via OCR) and convert it into a clean, well-structured Markdown document.

Rules:
1. **Layout**: Use proper Markdown headers (#, ##, ###) to structure the notes logicially.
2. **Math**: Detect mathematical expressions and format them using LaTeX. 
   - Use $...$ for inline math.
   - Use $$...$$ for block math/equations.
3. **Corrections**: Fix obvious OCR errors (typos, spacing issues) based on context.
4. **Lists**: Convert bullet points or numbered lists into proper Markdown lists.
5. **Bold/Italic**: Use bold or italics for emphasized text or key terms.
6. **No Chatter**: Return ONLY the formatted Markdown. Do not include introductory or concluding remarks.
"""

def clean_text_with_llm(raw_text: str) -> str:
    """
    Sends raw OCR text to LLM for cleaning and formatting via OpenRouter.
    """
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/user/note-beautifier",
                "Content-Type": "application/json",
            },
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Here is the raw OCR text:\n\n{raw_text}"}
                ],
                "temperature": 0.2,
                "max_tokens": 4096,
            }
        )
        
        if response.status_code != 200:
            logging.error(f"LLM API Error {response.status_code}: {response.text}")
            return raw_text
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
    except Exception as e:
        logging.error(f"LLM Error: {e}")
        return raw_text
