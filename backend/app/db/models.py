from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    content_type: str
    file_path: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    
    # Content storage
    raw_ocr_text: Optional[str] = Field(default=None) # Text extracted by OCR
    beautified_text: Optional[str] = Field(default=None) # Markdown/LaTeX from LLM
    
    error_message: Optional[str] = Field(default=None)
