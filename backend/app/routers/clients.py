"""Client API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientRead, ClientUpdate, ClientWithSites
from ..services.blob_storage import blob_storage_service

router = APIRouter()


@router.post("/", response_model=ClientRead, status_code=201)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db)
):
    """Create a new client"""
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/", response_model=List[ClientRead])
def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by client name or country"),
    country: Optional[str] = Query(None, description="Filter by country"),
    business_type: Optional[str] = Query(None, description="Filter by business type"),
    db: Session = Depends(get_db)
):
    """
    List all clients with optional search and filtering.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search by client name or country (case-insensitive)
    - **country**: Filter by exact country match
    - **business_type**: Filter by exact business type match
    """
    query = db.query(Client)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.name.ilike(search_term)) |
            (Client.country.ilike(search_term))
        )

    # Apply country filter
    if country:
        query = query.filter(Client.country == country)

    # Apply business type filter
    if business_type:
        query = query.filter(Client.business_type == business_type)

    # Apply pagination (MS SQL Server requires ORDER BY with OFFSET/LIMIT)
    clients = query.order_by(Client.id).offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientWithSites)
def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific client by ID, including associated sites"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update only provided fields
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)

    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Delete a client (and all associated sites and documents due to CASCADE)"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Delete associated document blobs from storage before removing DB records.
    # DB rows cascade automatically, but blobs must be cleaned up explicitly.
    try:
        await blob_storage_service.delete_client_documents(client_id)
    except Exception as e:
        # Log but don't fail - we still want to delete the client record
        print(f"Warning: Failed to delete blobs for client {client_id}: {str(e)}")

    db.delete(db_client)
    db.commit()
    return None
