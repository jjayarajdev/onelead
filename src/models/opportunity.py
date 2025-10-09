"""Opportunity model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Opportunity(Base):
    """Sales Opportunity entity."""

    __tablename__ = 'opportunities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(String, unique=True, index=True, nullable=False)
    opportunity_name = Column(String)
    product_line = Column(String, index=True)

    # Foreign keys
    account_id = Column(Integer, ForeignKey('accounts.id'), index=True)

    # Metadata
    territory_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="opportunities")

    def __repr__(self):
        return f"<Opportunity(id='{self.opportunity_id}', name='{self.opportunity_name}')>"
