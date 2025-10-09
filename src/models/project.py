"""Project (A&PS) model."""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Project(Base):
    """Advisory & Professional Services Project entity."""

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, index=True, nullable=False)  # Not unique - source data has duplicates
    project_description = Column(String)
    practice = Column(String, index=True)
    function = Column(String)
    business_area = Column(String)
    status = Column(String, index=True)

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)
    project_length_days = Column(Integer)

    # Financials
    size_category = Column(String)
    labor_cost = Column(Float)
    third_party_service_cost = Column(Float)
    third_party_material_cost = Column(Float)

    # Foreign keys
    account_id = Column(Integer, ForeignKey('accounts.id'), index=True)

    # Metadata
    country = Column(String)
    region = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="projects")

    def __repr__(self):
        return f"<Project(id='{self.project_id}', practice='{self.practice}', status='{self.status}')>"
