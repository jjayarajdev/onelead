"""Account model."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Account(Base):
    """Account/Customer entity."""

    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, unique=True, index=True)  # External account ID
    account_name = Column(String, nullable=False, index=True)
    normalized_name = Column(String, index=True)  # For fuzzy matching
    territory_id = Column(String, index=True)
    industry_code = Column(String)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    install_base_items = relationship("InstallBase", back_populates="account")
    opportunities = relationship("Opportunity", back_populates="account")
    projects = relationship("Project", back_populates="account")
    leads = relationship("Lead", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.account_name}', territory='{self.territory_id}')>"
