"""Lead generation engine."""

from typing import List, Dict, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import InstallBase, Account, Lead, Opportunity
from src.utils.config_loader import config


class LeadGenerator:
    """Generate leads from install base and opportunities."""

    def __init__(self, session: Session):
        """Initialize lead generator with database session."""
        self.session = session
        self.config = config

    def generate_all_leads(self) -> int:
        """Generate all types of leads. Returns count of leads generated."""
        count = 0

        # Generate renewal leads (expired/expiring support)
        count += self.generate_renewal_leads()

        # Generate hardware refresh leads (EOL equipment)
        count += self.generate_hardware_refresh_leads()

        # Generate service attach leads (equipment without support)
        count += self.generate_service_attach_leads()

        self.session.commit()
        return count

    def generate_renewal_leads(self) -> int:
        """Generate leads for expired or expiring support contracts."""
        # Find install base items with expired support
        expired_items = self.session.query(InstallBase).filter(
            InstallBase.risk_level.in_(['CRITICAL', 'HIGH']),
            InstallBase.support_status.like('%Expired%')
        ).all()

        count = 0
        for item in expired_items:
            # Check if lead already exists for this install base item
            existing = self.session.query(Lead).filter(
                Lead.install_base_id == item.id,
                Lead.lead_type == 'Renewal - Expired Support',
                Lead.is_active == True
            ).first()

            if existing:
                continue

            # Estimate renewal value based on product family
            estimated_min, estimated_max = self._estimate_renewal_value(
                item.product_family or '',
                item.product_name or ''
            )

            # Create renewal lead
            lead = Lead(
                lead_type='Renewal - Expired Support',
                priority=item.risk_level,
                title=f"Support Renewal: {item.product_name}",
                description=f"Support expired for {item.product_name} (S/N: {item.serial_number}). "
                           f"Status: {item.support_status}. "
                           f"EOL Date: {item.product_eol_date or 'N/A'}.",
                recommended_action=f"Contact account to renew support contract. "
                                 f"Product has been without support for {item.days_since_expiry or 0} days.",
                estimated_value_min=estimated_min,
                estimated_value_max=estimated_max,
                account_id=item.account_id,
                install_base_id=item.id,
                territory_id=item.territory_id,
                lead_status='New',
                is_active=True
            )

            self.session.add(lead)
            count += 1

        print(f"  → Generated {count} renewal leads")
        return count

    def generate_hardware_refresh_leads(self) -> int:
        """Generate leads for EOL/aging hardware requiring refresh."""
        # Find items past EOL
        critical_eol_days = self.config.get('urgency_thresholds.critical_days_past_eol', 1825)

        old_items = self.session.query(InstallBase).filter(
            InstallBase.days_since_eol != None,
            InstallBase.days_since_eol > critical_eol_days
        ).all()

        count = 0
        for item in old_items:
            # Check if lead already exists
            existing = self.session.query(Lead).filter(
                Lead.install_base_id == item.id,
                Lead.lead_type == 'Hardware Refresh - EOL Equipment',
                Lead.is_active == True
            ).first()

            if existing:
                continue

            # Determine generation upgrade path
            gen_info = self._extract_generation(item.product_name)
            upgrade_msg = f" Consider upgrading to Gen{gen_info['next_gen']}." if gen_info else ""

            lead = Lead(
                lead_type='Hardware Refresh - EOL Equipment',
                priority='CRITICAL',
                title=f"Hardware Refresh: {item.product_name}",
                description=f"{item.product_name} (S/N: {item.serial_number}) reached EOL on "
                           f"{item.product_eol_date}. Equipment is {item.days_since_eol} days past EOL.",
                recommended_action=f"Schedule hardware refresh discussion with account.{upgrade_msg} "
                                 f"Highlight risks of running unsupported hardware.",
                estimated_value_min=75000,
                estimated_value_max=200000,
                account_id=item.account_id,
                install_base_id=item.id,
                territory_id=item.territory_id,
                lead_status='New',
                is_active=True
            )

            self.session.add(lead)
            count += 1

        print(f"  → Generated {count} hardware refresh leads")
        return count

    def generate_service_attach_leads(self) -> int:
        """Generate leads for install base without support coverage."""
        # Find items without service agreements or with uncovered status
        uncovered_items = self.session.query(InstallBase).filter(
            InstallBase.support_status.like('%Uncovered%')
        ).all()

        count = 0
        for item in uncovered_items:
            # Check if lead already exists
            existing = self.session.query(Lead).filter(
                Lead.install_base_id == item.id,
                Lead.lead_type == 'Service Attach - Coverage Gap',
                Lead.is_active == True
            ).first()

            if existing:
                continue

            lead = Lead(
                lead_type='Service Attach - Coverage Gap',
                priority='HIGH',
                title=f"Service Coverage Gap: {item.product_name}",
                description=f"{item.product_name} (S/N: {item.serial_number}) has no support coverage. "
                           f"Status: {item.support_status}.",
                recommended_action=f"Propose service contract to cover this equipment. "
                                 f"Emphasize risk mitigation and uptime benefits.",
                estimated_value_min=10000,
                estimated_value_max=50000,
                account_id=item.account_id,
                install_base_id=item.id,
                territory_id=item.territory_id,
                lead_status='New',
                is_active=True
            )

            self.session.add(lead)
            count += 1

        print(f"  → Generated {count} service attach leads")
        return count

    def _extract_generation(self, product_name: str) -> Optional[Dict]:
        """Extract generation info from product name."""
        import re

        if not product_name:
            return None

        # Match patterns like "Gen8", "Gen 10", etc.
        match = re.search(r'Gen\s?(\d+)', product_name, re.IGNORECASE)
        if match:
            current_gen = int(match.group(1))
            return {
                'current_gen': current_gen,
                'next_gen': current_gen + 3  # Typical upgrade path (Gen8 -> Gen11)
            }

        return None

    def _estimate_renewal_value(self, product_family: str, product_name: str = '') -> tuple:
        """Estimate annual support value for a product based on product family.

        Returns (min_value, max_value) tuple for estimated annual support cost.
        """
        if not product_family:
            return (5000, 15000)  # Conservative default

        # Product family benchmarks based on typical support contract values
        benchmarks = {
            'PROLIANT': (3000, 8000),      # Standard servers
            'DL': (3000, 8000),             # DL series servers
            'ML': (2500, 7000),             # ML series servers
            'BL': (4000, 10000),            # Blade servers (higher complexity)
            '3PAR': (15000, 40000),         # Storage arrays
            'PRIMERA': (25000, 60000),      # High-end storage
            'ALLETRA': (20000, 50000),      # Modern storage platform
            'NIMBLE': (12000, 30000),       # Mid-range storage
            'MSA': (5000, 15000),           # Entry-level storage
            'STOREEASY': (8000, 20000),     # NAS solutions
            'STOREONCE': (10000, 25000),    # Backup appliances
            'SIMPLIVITY': (15000, 35000),   # Hyperconverged
            'SYNERGY': (20000, 50000),      # Composable infrastructure
            'APOLLO': (10000, 25000),       # HPC systems
            'SUPERDOME': (40000, 100000),   # Mission-critical systems
        }

        # Check product family first
        product_family_upper = product_family.upper()
        for family, (min_val, max_val) in benchmarks.items():
            if family in product_family_upper:
                return (min_val, max_val)

        # Check product name as fallback
        if product_name:
            product_name_upper = product_name.upper()
            for family, (min_val, max_val) in benchmarks.items():
                if family in product_name_upper:
                    return (min_val, max_val)

        # Default for unknown products
        return (5000, 15000)
