"""Lead model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Lead(Base):
    """Generated Lead entity."""

    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_type = Column(String, index=True, nullable=False)  # Renewal, Hardware Refresh, etc.
    lead_status = Column(String, index=True, default='New')  # New, Qualified, Converted, Rejected
    priority = Column(String, index=True)  # CRITICAL, HIGH, MEDIUM, LOW

    # Scoring
    score = Column(Float, index=True)  # 0-100
    urgency_score = Column(Float)
    value_score = Column(Float)
    propensity_score = Column(Float)
    strategic_fit_score = Column(Float)

    # Lead details
    title = Column(String, nullable=False)
    description = Column(Text)
    recommended_action = Column(Text)
    estimated_value_min = Column(Float)
    estimated_value_max = Column(Float)

    # Foreign keys
    account_id = Column(Integer, ForeignKey('accounts.id'), index=True, nullable=False)
    install_base_id = Column(Integer, ForeignKey('install_base.id'), nullable=True)  # If tied to specific hardware

    # Recommended services (comma-separated SKUs or JSON)
    recommended_skus = Column(Text)

    # Metadata
    territory_id = Column(String, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    converted_opportunity_id = Column(String)  # If converted to opportunity
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    account = relationship("Account", back_populates="leads")
    install_base_item = relationship("InstallBase")

    def __repr__(self):
        return f"<Lead(id={self.id}, type='{self.lead_type}', score={self.score}, priority='{self.priority}')>"
