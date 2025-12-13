"""Site database model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from ..database import Base


class Site(Base):
    """Site model for storing site information with geolocation polygons"""

    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    site_type = Column(String(100), nullable=False)

    # Store geolocation as GEOGRAPHY (polygon) - Azure SQL supports this
    # GeoJSON will be converted to WKT (Well-Known Text) format for storage
    geolocation_polygon = Column(Geography('POLYGON', srid=4326), nullable=True)

    # Alternative: Store as JSON text if GEOGRAPHY doesn't work with Azure SQL
    # geolocation_polygon_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.getutcdate())
    updated_at = Column(DateTime(timezone=True), server_default=func.getutcdate(), onupdate=func.getutcdate())
    created_by = Column(String(255), nullable=True)

    # Relationship to client
    client = relationship("Client", back_populates="sites")

    # Indexes
    __table_args__ = (
        Index('idx_site_client_id', 'client_id'),
    )

    def __repr__(self):
        return f"<Site(id={self.id}, name='{self.name}', client_id={self.client_id})>"
