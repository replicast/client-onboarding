"""Pydantic schemas for Site"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
import json


class SiteBase(BaseModel):
    """Base schema for Site"""
    name: str = Field(..., min_length=1, max_length=255, description="Site name")
    site_type: str = Field(..., min_length=1, max_length=100, description="Type of site")
    geolocation_polygon: Optional[Dict[str, Any]] = Field(
        None,
        description="GeoJSON polygon representing site location"
    )


class SiteCreate(SiteBase):
    """Schema for creating a new site"""
    pass


class SiteUpdate(BaseModel):
    """Schema for updating an existing site"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    site_type: Optional[str] = Field(None, min_length=1, max_length=100)
    geolocation_polygon: Optional[Dict[str, Any]] = None


class SiteRead(SiteBase):
    """Schema for reading site data"""
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    @field_validator('geolocation_polygon', mode='before')
    @classmethod
    def parse_geolocation(cls, v):
        """Parse JSON string to dict if needed"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

    class Config:
        from_attributes = True  # Pydantic v2 (formerly orm_mode)
