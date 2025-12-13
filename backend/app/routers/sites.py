"""Site API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
from ..database import get_db
from ..models.site import Site
from ..models.client import Client
from ..schemas.site import SiteCreate, SiteRead, SiteUpdate

router = APIRouter()


def geojson_to_wkt(geojson_polygon):
    """Convert GeoJSON polygon to WKT (Well-Known Text) format"""
    if not geojson_polygon:
        return None
    try:
        # Convert GeoJSON to Shapely geometry
        geometry = shape(geojson_polygon)
        # Convert to WKT using GeoAlchemy2
        return from_shape(geometry, srid=4326)
    except Exception as e:
        raise ValueError(f"Invalid GeoJSON polygon: {str(e)}")


def wkt_to_geojson(wkt_element):
    """Convert WKT to GeoJSON format"""
    if not wkt_element:
        return None
    try:
        # Convert WKT to Shapely geometry
        geometry = to_shape(wkt_element)
        # Convert to GeoJSON
        return mapping(geometry)
    except Exception as e:
        print(f"Error converting WKT to GeoJSON: {str(e)}")
        return None


@router.post("/clients/{client_id}/sites", response_model=SiteRead, status_code=201)
def create_site(
    client_id: int = Path(..., description="ID of the client"),
    site: SiteCreate = ...,
    db: Session = Depends(get_db)
):
    """Create a new site for a client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Convert GeoJSON to WKT
    geolocation_wkt = geojson_to_wkt(site.geolocation_polygon)

    # Create site
    db_site = Site(
        client_id=client_id,
        name=site.name,
        site_type=site.site_type,
        geolocation_polygon=geolocation_wkt
    )

    db.add(db_site)
    db.commit()
    db.refresh(db_site)

    # Convert WKT back to GeoJSON for response
    site_dict = {
        "id": db_site.id,
        "client_id": db_site.client_id,
        "name": db_site.name,
        "site_type": db_site.site_type,
        "geolocation_polygon": wkt_to_geojson(db_site.geolocation_polygon),
        "created_at": db_site.created_at,
        "updated_at": db_site.updated_at,
        "created_by": db_site.created_by
    }

    return site_dict


@router.get("/clients/{client_id}/sites", response_model=List[SiteRead])
def list_sites_for_client(
    client_id: int = Path(..., description="ID of the client"),
    db: Session = Depends(get_db)
):
    """Get all sites for a specific client"""
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    sites = db.query(Site).filter(Site.client_id == client_id).all()

    # Convert WKT to GeoJSON for each site
    sites_list = []
    for site in sites:
        sites_list.append({
            "id": site.id,
            "client_id": site.client_id,
            "name": site.name,
            "site_type": site.site_type,
            "geolocation_polygon": wkt_to_geojson(site.geolocation_polygon),
            "created_at": site.created_at,
            "updated_at": site.updated_at,
            "created_by": site.created_by
        })

    return sites_list


@router.get("/{site_id}", response_model=SiteRead)
def get_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific site by ID"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return {
        "id": site.id,
        "client_id": site.client_id,
        "name": site.name,
        "site_type": site.site_type,
        "geolocation_polygon": wkt_to_geojson(site.geolocation_polygon),
        "created_at": site.created_at,
        "updated_at": site.updated_at,
        "created_by": site.created_by
    }


@router.put("/{site_id}", response_model=SiteRead)
def update_site(
    site_id: int,
    site_update: SiteUpdate,
    db: Session = Depends(get_db)
):
    """Update a site"""
    db_site = db.query(Site).filter(Site.id == site_id).first()
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Update fields
    update_data = site_update.model_dump(exclude_unset=True)

    # Handle geolocation separately
    if "geolocation_polygon" in update_data:
        geojson_polygon = update_data.pop("geolocation_polygon")
        db_site.geolocation_polygon = geojson_to_wkt(geojson_polygon)

    # Update other fields
    for field, value in update_data.items():
        setattr(db_site, field, value)

    db.commit()
    db.refresh(db_site)

    return {
        "id": db_site.id,
        "client_id": db_site.client_id,
        "name": db_site.name,
        "site_type": db_site.site_type,
        "geolocation_polygon": wkt_to_geojson(db_site.geolocation_polygon),
        "created_at": db_site.created_at,
        "updated_at": db_site.updated_at,
        "created_by": db_site.created_by
    }


@router.delete("/{site_id}", status_code=204)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """Delete a site"""
    db_site = db.query(Site).filter(Site.id == site_id).first()
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")

    db.delete(db_site)
    db.commit()
    return None
