"""Lead generation engine."""

from typing import List, Dict, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import InstallBase, Account, Lead, Opportunity, Project
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

            # Get actual data metrics for this account
            project_size = self._get_project_size_category(item.account_id)
            ib_count = self._get_install_base_count(item.account_id)
            project_count = self._get_historical_project_count(item.account_id)
            active_credits = self._get_active_credits(item.account_id)

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
                estimated_value_min=None,  # No longer estimating values
                estimated_value_max=None,  # No longer estimating values
                project_size_category=project_size,
                install_base_count=ib_count,
                historical_project_count=project_count,
                active_credits_available=active_credits,
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

            # Get actual data metrics for this account
            project_size = self._get_project_size_category(item.account_id)
            ib_count = self._get_install_base_count(item.account_id)
            project_count = self._get_historical_project_count(item.account_id)
            active_credits = self._get_active_credits(item.account_id)

            lead = Lead(
                lead_type='Hardware Refresh - EOL Equipment',
                priority='CRITICAL',
                title=f"Hardware Refresh: {item.product_name}",
                description=f"{item.product_name} (S/N: {item.serial_number}) reached EOL on "
                           f"{item.product_eol_date}. Equipment is {item.days_since_eol} days past EOL.",
                recommended_action=f"Schedule hardware refresh discussion with account.{upgrade_msg} "
                                 f"Highlight risks of running unsupported hardware.",
                estimated_value_min=None,  # No longer estimating values
                estimated_value_max=None,  # No longer estimating values
                project_size_category=project_size,
                install_base_count=ib_count,
                historical_project_count=project_count,
                active_credits_available=active_credits,
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

            # Get actual data metrics for this account
            project_size = self._get_project_size_category(item.account_id)
            ib_count = self._get_install_base_count(item.account_id)
            project_count = self._get_historical_project_count(item.account_id)
            active_credits = self._get_active_credits(item.account_id)

            lead = Lead(
                lead_type='Service Attach - Coverage Gap',
                priority='HIGH',
                title=f"Service Coverage Gap: {item.product_name}",
                description=f"{item.product_name} (S/N: {item.serial_number}) has no support coverage. "
                           f"Status: {item.support_status}.",
                recommended_action=f"Propose service contract to cover this equipment. "
                                 f"Emphasize risk mitigation and uptime benefits.",
                estimated_value_min=None,  # No longer estimating values
                estimated_value_max=None,  # No longer estimating values
                project_size_category=project_size,
                install_base_count=ib_count,
                historical_project_count=project_count,
                active_credits_available=active_credits,
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

    def _get_project_size_category(self, account_id: int) -> Optional[str]:
        """Get typical project size for this account based on historical A&PS data.

        Returns project size category from A&PS PRJ Size field:
        '<$50k', '$50k-$500k', '$500k-$1M', '$1M-$5M', '>$5M', or None
        """
        try:
            # Get account to find matching projects
            account = self.session.query(Account).filter(Account.id == account_id).first()
            if not account:
                return None

            # Query A&PS projects for this account
            projects = self.session.query(Project).filter(
                Project.account_id == account_id
            ).all()

            if not projects:
                return None

            # Get most common project size for this account (excluding '-' and None)
            sizes = [p.size_category for p in projects if p.size_category and p.size_category != '-']
            if not sizes:
                return None

            # Return most frequent size
            return max(set(sizes), key=sizes.count)
        except Exception as e:
            print(f"  Warning: Could not get project size category: {e}")
            return None

    def _get_install_base_count(self, account_id: int) -> Optional[int]:
        """Get count of assets in install base for this account."""
        try:
            count = self.session.query(InstallBase).filter(
                InstallBase.account_id == account_id
            ).count()
            return count if count > 0 else None
        except Exception as e:
            print(f"  Warning: Could not get install base count: {e}")
            return None

    def _get_historical_project_count(self, account_id: int) -> Optional[int]:
        """Get count of historical A&PS projects for this account."""
        try:
            count = self.session.query(Project).filter(
                Project.account_id == account_id
            ).count()
            return count if count > 0 else None
        except Exception as e:
            print(f"  Warning: Could not get historical project count: {e}")
            return None

    def _get_active_credits(self, account_id: int) -> Optional[int]:
        """Get available service credits for this account.

        NOTE: Service credits data is not yet loaded in the database.
        This function will return None until the data is imported.
        """
        try:
            # TODO: Implement once service credits data is loaded
            # For now, return None (no credits data available)
            return None
        except Exception as e:
            print(f"  Warning: Could not get active credits: {e}")
            return None
