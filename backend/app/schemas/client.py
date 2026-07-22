"""Pydantic schemas for Client"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .site import SiteRead
    from .document import DocumentRead


class ClientBase(BaseModel):
    """Base schema for Client"""
    name: str = Field(..., min_length=1, max_length=255, description="Client name")
    country: str = Field(..., min_length=1, max_length=100, description="Country")
    business_type: str = Field(..., min_length=1, max_length=100, description="Type of business")
    organization_size: str = Field(..., min_length=1, max_length=50, description="Size of organization")


class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating an existing client"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    business_type: Optional[str] = Field(None, min_length=1, max_length=100)
    organization_size: Optional[str] = Field(None, min_length=1, max_length=50)


class ClientRead(ClientBase):
    """Schema for reading client data"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 (formerly orm_mode)


class ClientWithSites(ClientRead):
    """Schema for client with associated sites and documents"""
    sites: List["SiteRead"] = []
    documents: List["DocumentRead"] = []

    class Config:
        from_attributes = True


# Import SiteRead and DocumentRead after class definition to avoid circular import
from .site import SiteRead
from .document import DocumentRead
ClientWithSites.model_rebuild()
