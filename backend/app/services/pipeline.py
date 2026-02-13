from sqlmodel import Session, select
from app.db.models import Document, ProcessingStatus
from app.services.pdf_service import convert_pdf_to_images, extract_text_from_pdf
from app.services.ocr_service import perform_ocr
from app.services.llm_service import clean_text_with_llm
from app.db.database import engine
import os
import logging

def process_document_pipeline(document_id: int):
    """
    Background task that runs the full pipeline:
    1. Try direct text extraction from PDF (fast, works for typed PDFs)
    2. If that fails or returns little text, fall back to OCR
    3. Send to LLM for formatting
    """
    logging.info(f"Starting pipeline for document {document_id}")
    
    # Create a new session for the background task
    with Session(engine) as session:
        doc = session.get(Document, document_id)
        if not doc:
            logging.error(f"Document {document_id} not found")
            return

        try:
            # Update status
            doc.status = ProcessingStatus.PROCESSING
            session.add(doc)
            session.commit()
            session.refresh(doc)
            
            raw_text = ""
            
            # Step 1: Try direct PDF text extraction first (fast & reliable for typed PDFs)
            if doc.content_type == "application/pdf":
                raw_text = extract_text_from_pdf(doc.file_path)
                logging.info(f"PyMuPDF extracted {len(raw_text)} chars directly from PDF")
            
            # Step 2: If direct extraction got very little text, use OCR
            if len(raw_text.strip()) < 50:
                logging.info("Direct extraction insufficient, falling back to OCR...")
                if doc.content_type == "application/pdf":
                    image_paths = convert_pdf_to_images(doc.file_path)
                else:
                    image_paths = [doc.file_path]
                
                raw_text = perform_ocr(image_paths)
                
                # Cleanup temp images
                for p in image_paths:
                    if p != doc.file_path:
                        try:
                            os.remove(p)
                        except OSError:
                            pass
            
            doc.raw_ocr_text = raw_text
            session.add(doc)
            session.commit()

            # Step 3: LLM Cleanup
            final_text = clean_text_with_llm(raw_text)
            doc.beautified_text = final_text
            
            # Finalize
            doc.status = ProcessingStatus.COMPLETED
            session.add(doc)
            session.commit()
            
            logging.info(f"Pipeline completed for document {document_id}")

        except Exception as e:
            logging.error(f"Pipeline failed for document {document_id}: {e}")
            doc.status = ProcessingStatus.FAILED
            doc.error_message = str(e)
            session.add(doc)
            session.commit()
