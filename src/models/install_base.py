"""Install Base model."""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class InstallBase(Base):
    """Install Base hardware inventory entity."""

    __tablename__ = 'install_base'

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True, index=True, nullable=False)
    product_id = Column(String, index=True)
    product_name = Column(String)
    product_platform = Column(String)
    product_family = Column(String, index=True)  # Computed: Compute, Storage, etc.
    line_description = Column(String)
    business_area = Column(String)
    legacy_gbu = Column(String)

    # Dates
    product_eol_date = Column(Date)
    product_eos_date = Column(Date)
    service_start_date = Column(Date)
    service_end_date = Column(Date)

    # Support information
    support_status = Column(String, index=True)
    service_agreement_id = Column(String)
    service_source = Column(String)

    # Foreign keys
    account_id = Column(Integer, ForeignKey('accounts.id'), index=True)

    # Metadata
    territory_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Calculated fields
    days_since_eol = Column(Integer)
    days_since_expiry = Column(Integer)
    risk_level = Column(String, index=True)  # CRITICAL, HIGH, MEDIUM, LOW

    # Relationships
    account = relationship("Account", back_populates="install_base_items")

    def __repr__(self):
        return f"<InstallBase(sn='{self.serial_number}', product='{self.product_name}', status='{self.support_status}')>"
