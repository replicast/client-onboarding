"""Document database model"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Document(Base):
    """Document model for storing document metadata"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), default="application/pdf")
    file_size = Column(BigInteger, nullable=False)
    blob_name = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.getutcdate())
    uploaded_by = Column(String(255), nullable=True)

    # Relationship to client
    client = relationship("Client", back_populates="documents")

    # Indexes
    __table_args__ = (
        Index('idx_document_client_id', 'client_id'),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', client_id={self.client_id})>"
