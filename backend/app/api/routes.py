from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlmodel import Session, select
from typing import List

from app.db.database import get_session
from app.db.models import Document, ProcessingStatus
from app.core.config import settings
from app.services.pipeline import process_document_pipeline
import shutil
import os
from pathlib import Path

router = APIRouter()

@router.post("/upload", response_model=Document)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload a PDF file to begin processing.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported for MVP.")
    
    # Save file to disk
    file_location = settings.UPLOAD_DIR / file.filename
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create DB Record
    new_doc = Document(
        filename=file.filename,
        content_type=file.content_type,
        file_path=str(file_location),
        status=ProcessingStatus.PENDING
    )
    session.add(new_doc)
    session.commit()
    session.refresh(new_doc)
    
    # Trigger Background Task
    background_tasks.add_task(process_document_pipeline, new_doc.id)
    
    return new_doc

@router.get("/documents/{doc_id}", response_model=Document)
async def get_document(doc_id: int, session: Session = Depends(get_session)):
    doc = session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/documents", response_model=List[Document])
async def list_documents(session: Session = Depends(get_session)):
    documents = session.exec(select(Document).order_by(Document.upload_timestamp.desc())).all()
    return documents
