"""Pydantic schemas for Document"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base schema for Document"""
    filename: str = Field(..., min_length=1, max_length=255, description="Display filename")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Original uploaded filename")


class DocumentCreate(BaseModel):
    """Schema for creating a new document (internal use)"""
    filename: str
    original_filename: str
    content_type: str = "application/pdf"
    file_size: int
    blob_name: str
    uploaded_by: Optional[str] = None


class DocumentRead(BaseModel):
    """Schema for reading document data"""
    id: int
    client_id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime
    uploaded_by: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentWithDownloadUrl(DocumentRead):
    """Schema for document with download URL"""
    download_url: str
