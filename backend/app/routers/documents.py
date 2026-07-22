"""Document API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.document import Document
from ..models.client import Client
from ..schemas.document import DocumentRead
from ..services.blob_storage import blob_storage_service

router = APIRouter()

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]


@router.post("/clients/{client_id}/documents", response_model=DocumentRead, status_code=201)
async def upload_document(
    client_id: int = Path(..., description="ID of the client"),
    file: UploadFile = File(..., description="PDF file to upload"),
    db: Session = Depends(get_db)
):
    """Upload a PDF document for a client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF files are allowed. Got: {file.content_type}"
        )

    # Read file to check size
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Reset file position for upload
    await file.seek(0)

    # Upload to blob storage
    try:
        blob_name, actual_size = await blob_storage_service.upload_document(
            file=file.file,
            client_id=client_id,
            original_filename=file.filename,
            content_type=file.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Storage configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Create database record
    db_document = Document(
        client_id=client_id,
        filename=file.filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=actual_size,
        blob_name=blob_name
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.get("/clients/{client_id}/documents", response_model=List[DocumentRead])
def list_documents_for_client(
    client_id: int = Path(..., description="ID of the client"),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    documents = db.query(Document).filter(
        Document.client_id == client_id
    ).order_by(Document.created_at.desc()).all()

    return documents


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a secure download URL for a document (redirects to SAS URL)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Generate SAS URL with 1 hour expiry
        download_url = blob_storage_service.generate_sas_url(document.blob_name, expiry_hours=1)
        return RedirectResponse(url=download_url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


@router.get("/{document_id}/url")
def get_document_url(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a secure SAS URL for a document (returns URL as JSON, no redirect)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Generate SAS URL with 1 hour expiry
        download_url = blob_storage_service.generate_sas_url(document.blob_name, expiry_hours=1)
        return {"url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from blob storage
    try:
        await blob_storage_service.delete_document(document.blob_name)
    except Exception as e:
        # Log but don't fail - we still want to delete the DB record
        print(f"Warning: Failed to delete blob {document.blob_name}: {str(e)}")

    # Delete from database
    db.delete(document)
    db.commit()

    return None
