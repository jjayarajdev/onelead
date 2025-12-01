"""Service Credit model."""

from sqlalchemy import Column, Integer, String, DateTime, Date
from datetime import datetime
from .base import Base


class ServiceCredit(Base):
    """Service Credit entity."""

    __tablename__ = 'service_credits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, index=True)
    project_name = Column(String)
    practice_name = Column(String, index=True)

    # Credit counts
    purchased_credits = Column(Integer)
    converted_credits = Column(Integer)
    delivered_credits = Column(Integer)
    converted_not_delivered_credits = Column(Integer)
    active_credits = Column(Integer, index=True)

    # Expiry
    expiry_in_days = Column(String)
    contract_end_date = Column(Date)

    # Link to account via territory
    territory_id = Column(String, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServiceCredit(project='{self.project_id}', active={self.active_credits}, territory='{self.territory_id}')>"
