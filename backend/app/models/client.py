"""Client database model"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Client(Base):
    """Client model for storing client information"""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    business_type = Column(String(100), nullable=False)
    organization_size = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.getutcdate())
    updated_at = Column(DateTime(timezone=True), server_default=func.getutcdate(), onupdate=func.getutcdate())
    created_by = Column(String(255), nullable=True)

    # Relationship to sites
    sites = relationship("Site", back_populates="client", cascade="all, delete-orphan")

    # Relationship to documents
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_client_name', 'name'),
        Index('idx_client_country', 'country'),
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', country='{self.country}')>"
