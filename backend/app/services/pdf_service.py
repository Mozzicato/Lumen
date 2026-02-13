import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts embedded text directly from a PDF using PyMuPDF.
    Fast and reliable for typed/digital PDFs. Returns empty for scanned/handwritten.
    """
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            full_text.append(text)
    
    doc.close()
    return "\n\n".join(full_text)


def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """
    Converts a PDF file into a list of image paths (one per page).
    Returns a list of temp image file paths.
    """
    doc = fitz.open(pdf_path)
    output_folder = Path(pdf_path).parent
    base_filename = Path(pdf_path).stem
    
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Zoom = 2 implies 2x resolution (good for OCR)
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        
        image_filename = f"{base_filename}_page_{page_num + 1}.png"
        image_path = output_folder / image_filename
        
        pix.save(str(image_path))
        image_paths.append(str(image_path))
        
    doc.close()
    return image_paths
