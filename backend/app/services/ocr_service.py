import logging

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logging.warning("PaddleOCR not installed.")

# Lazy init - models download on first use (~20MB from paddle servers)
_ocr_engine = None

def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None and PADDLE_AVAILABLE:
        try:
            logging.info("Initializing PaddleOCR engine (first use, downloading models ~20MB)...")
            _ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            logging.info("PaddleOCR engine ready.")
        except Exception as e:
            logging.error(f"Failed to initialize PaddleOCR: {e}")
    return _ocr_engine

def perform_ocr(image_paths: list[str]) -> str:
    """
    Runs OCR on a list of images using PaddleOCR v2 and combines the text.
    """
    engine = _get_ocr_engine()
    
    if engine is None:
        return "OCR ERROR: PaddleOCR engine not available. Check server logs."

    full_text = []
    
    for img_path in image_paths:
        try:
            result = engine.ocr(img_path, cls=True)
            
            page_text = ""
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    page_text += text + "\n"
            
            full_text.append(page_text)
            logging.info(f"OCR extracted {len(page_text)} chars from {img_path}")
        except Exception as e:
            logging.error(f"OCR Error on {img_path}: {e}")
    
    return "\n\n--- PAGE BREAK ---\n\n".join(full_text)
