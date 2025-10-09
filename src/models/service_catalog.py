"""Service Catalog models."""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime
from .base import Base


class ServiceCatalog(Base):
    """Service Catalog entity."""

    __tablename__ = 'service_catalog'

    id = Column(Integer, primary_key=True, autoincrement=True)
    practice = Column(String, index=True)
    sub_practice = Column(String, index=True)
    service_name = Column(String, nullable=False)
    service_description = Column(Text)
    service_category = Column(String, index=True)  # Health Check, Migration, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServiceCatalog(practice='{self.practice}', service='{self.service_name}')>"


class ServiceSKUMapping(Base):
    """Service SKU to Product Family mapping."""

    __tablename__ = 'service_sku_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_family = Column(String, index=True, nullable=False)  # 3PAR, Primera, etc.
    product_category = Column(String, index=True)  # Storage SW, Storage HW
    service_type = Column(String, nullable=False)  # OS upgrade, Health Check, etc.
    service_sku = Column(String)  # HPE SKU code
    estimated_value_min = Column(Float)
    estimated_value_max = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServiceSKUMapping(product='{self.product_family}', service='{self.service_type}', sku='{self.service_sku}')>"
