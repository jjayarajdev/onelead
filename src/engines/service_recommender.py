"""Service recommendation engine."""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import InstallBase, ServiceSKUMapping, Lead
from src.utils.config_loader import config


class ServiceRecommender:
    """Recommend services based on install base and product families."""

    def __init__(self, session: Session):
        """Initialize service recommender with database session."""
        self.session = session
        self.config = config

    def recommend_services_for_lead(self, lead: Lead) -> List[Dict]:
        """Recommend services for a specific lead."""
        if not lead.install_base_id:
            return []

        install_base = self.session.query(InstallBase).get(lead.install_base_id)
        if not install_base:
            return []

        return self.recommend_services_for_product(
            product_family=install_base.product_family,
            lead_type=lead.lead_type
        )

    def recommend_services_for_product(self, product_family: str,
                                      lead_type: Optional[str] = None) -> List[Dict]:
        """
        Recommend services for a product family.

        Args:
            product_family: Product family (3PAR, Primera, COMPUTE, etc.)
            lead_type: Type of lead to tailor recommendations

        Returns:
            List of recommended services with SKUs
        """
        if not product_family:
            return []

        # Query service mappings for this product family
        mappings = self.session.query(ServiceSKUMapping).filter(
            ServiceSKUMapping.product_family == product_family.upper()
        ).all()

        recommendations = []
        for mapping in mappings:
            # Prioritize based on lead type
            priority = self._calculate_service_priority(mapping.service_type, lead_type)

            recommendations.append({
                'product_family': mapping.product_family,
                'service_type': mapping.service_type,
                'service_sku': mapping.service_sku,
                'category': mapping.product_category,
                'priority': priority,
                'estimated_value_min': mapping.estimated_value_min,
                'estimated_value_max': mapping.estimated_value_max
            })

        # Sort by priority (higher first)
        recommendations.sort(key=lambda x: x['priority'], reverse=True)

        return recommendations

    def _calculate_service_priority(self, service_type: str, lead_type: Optional[str]) -> int:
        """Calculate priority score for a service based on lead type."""
        if not service_type:
            return 0

        service_lower = service_type.lower()
        priority = 5  # Base priority

        if not lead_type:
            return priority

        # Boost priority based on lead type and service type match
        if 'renewal' in lead_type.lower():
            if 'health check' in service_lower:
                priority += 10
            elif 'upgrade' in service_lower:
                priority += 8
            elif 'performance' in service_lower:
                priority += 6

        elif 'hardware refresh' in lead_type.lower():
            if 'migration' in service_lower:
                priority += 10
            elif 'install' in service_lower or 'startup' in service_lower:
                priority += 9
            elif 'rebalance' in service_lower:
                priority += 7

        elif 'service attach' in lead_type.lower():
            if 'health check' in service_lower:
                priority += 10
            elif 'upgrade' in service_lower:
                priority += 7

        return priority

    def enrich_leads_with_services(self) -> int:
        """Enrich all active leads with service recommendations."""
        leads = self.session.query(Lead).filter(
            Lead.is_active == True,
            Lead.install_base_id != None
        ).all()

        count = 0
        for lead in leads:
            if lead.recommended_skus:
                # Already enriched
                continue

            recommendations = self.recommend_services_for_lead(lead)
            if recommendations:
                # Store top 3 recommendations as comma-separated SKUs
                top_skus = [r['service_sku'] for r in recommendations[:3] if r['service_sku']]
                lead.recommended_skus = ','.join(top_skus)

                # Update estimated values based on recommendations
                if not lead.estimated_value_min and recommendations:
                    values = [r for r in recommendations if r.get('estimated_value_min')]
                    if values:
                        lead.estimated_value_min = min(v['estimated_value_min'] for v in values)
                        lead.estimated_value_max = max(v.get('estimated_value_max', v['estimated_value_min']) for v in values)

                count += 1

        self.session.commit()
        print(f"  → Enriched {count} leads with service recommendations")
        return count
