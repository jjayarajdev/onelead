"""Data loader for ETL pipeline."""

import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import (
    init_db, SessionLocal, Account, InstallBase, Opportunity,
    Project, ServiceCatalog, ServiceSKUMapping
)
from src.utils.config_loader import config
from src.utils.account_normalizer import AccountNormalizer


class DataLoader:
    """Load data from Excel files into database."""

    def __init__(self):
        """Initialize data loader."""
        self.config = config
        self.normalizer = AccountNormalizer(
            patterns=config.get('account_normalization.patterns', []),
            fuzzy_threshold=config.get('account_normalization.fuzzy_threshold', 85)
        )
        self.account_cache = {}  # Cache account lookups

    def load_all(self):
        """Load all data sources into database."""
        print("Initializing database...")
        init_db()

        session = SessionLocal()
        try:
            print("Loading install base data...")
            self._load_install_base(session)

            print("Loading opportunities data...")
            self._load_opportunities(session)

            print("Loading projects data...")
            self._load_projects(session)

            print("Loading services data...")
            self._load_services(session)

            print("Loading service SKU mappings...")
            self._load_service_sku_mappings(session)

            session.commit()
            print("✓ All data loaded successfully!")

        except Exception as e:
            session.rollback()
            print(f"✗ Error loading data: {e}")
            raise
        finally:
            session.close()

    def _get_or_create_account(self, session, account_name: str, territory_id: str = None,
                                account_id: str = None, **kwargs) -> Account:
        """Get existing account or create new one."""
        if not account_name or str(account_name).lower() in ['nan', 'null', '(null)', 'not available']:
            account_name = "Unknown Account"

        # Normalize account name
        normalized_name = self.normalizer.normalize(account_name)

        # Check cache first
        cache_key = f"{normalized_name}_{territory_id}"
        if cache_key in self.account_cache:
            return self.account_cache[cache_key]

        # Query database
        account = session.query(Account).filter(
            Account.normalized_name == normalized_name
        ).first()

        if not account:
            account = Account(
                account_id=account_id,
                account_name=account_name,
                normalized_name=normalized_name,
                territory_id=territory_id,
                **kwargs
            )
            session.add(account)
            session.flush()  # Get ID without committing

        # Cache it
        self.account_cache[cache_key] = account
        return account

    def _parse_date(self, date_value) -> Optional[date]:
        """Parse date from various formats."""
        if pd.isna(date_value) or str(date_value).lower() in ['(null)', 'null', 'nan']:
            return None

        if isinstance(date_value, pd.Timestamp):
            return date_value.date()

        if isinstance(date_value, datetime):
            return date_value.date()

        if isinstance(date_value, date):
            return date_value

        try:
            return pd.to_datetime(date_value).date()
        except:
            return None

    def _calculate_days_diff(self, target_date: Optional[date]) -> Optional[int]:
        """Calculate days difference from today."""
        if not target_date:
            return None
        today = date.today()
        return (today - target_date).days

    def _parse_float(self, value) -> Optional[float]:
        """Safely parse float value."""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _determine_risk_level(self, support_status: str, days_since_eol: Optional[int],
                               days_since_expiry: Optional[int]) -> str:
        """Determine risk level based on support status and dates."""
        if not support_status:
            return "UNKNOWN"

        support_status = str(support_status).lower()

        # Critical conditions
        if 'expired' in support_status or 'uncovered' in support_status:
            if days_since_eol and days_since_eol > config.get('urgency_thresholds.critical_days_past_eol', 1825):
                return "CRITICAL"
            if days_since_expiry and days_since_expiry > config.get('urgency_thresholds.high_days_past_expiry', 180):
                return "HIGH"
            return "HIGH"

        return "MEDIUM"

    def _extract_product_family(self, product_name: str, product_platform: str) -> Optional[str]:
        """Extract product family from product name and platform."""
        text = f"{product_name} {product_platform}".lower()

        # Check storage products
        storage_families = ['3par', 'primera', 'alletra', 'nimble', 'msa', 'storeonce', 'msl']
        for family in storage_families:
            if family in text:
                return family.upper()

        # Check compute indicators
        compute_indicators = ['dl', 'ml', 'bl', 'gen']
        for indicator in compute_indicators:
            if indicator in text:
                return "COMPUTE"

        return "OTHER"

    def _load_install_base(self, session):
        """Load install base data."""
        file_path = Path(self.config.install_base_path)
        if not file_path.exists():
            print(f"Warning: Install base file not found: {file_path}")
            return

        df = pd.read_excel(file_path, sheet_name='Install Base')

        for idx, row in df.iterrows():
            # Check if serial number already exists
            serial_number = str(row.get('Serial_Number_Id'))
            if session.query(InstallBase).filter(InstallBase.serial_number == serial_number).first():
                continue

            # Get or create account
            account = self._get_or_create_account(
                session,
                account_name=row.get('Account_Sales_Territory_Id'),  # Using territory as account for now
                territory_id=str(row.get('Account_Sales_Territory_Id'))
            )

            # Parse dates
            eol_date = self._parse_date(row.get('Product_End_of_Life_Date'))
            eos_date = self._parse_date(row.get('Product_End_of_Service_Life_Date'))
            service_start = self._parse_date(row.get('Final_Service_Start_Date'))
            service_end = self._parse_date(row.get('Final_Service_End_Date'))

            # Calculate derived fields
            days_since_eol = self._calculate_days_diff(eol_date)
            days_since_expiry = self._calculate_days_diff(service_end)

            support_status = str(row.get('Support_Status', ''))
            risk_level = self._determine_risk_level(support_status, days_since_eol, days_since_expiry)

            # Extract product family
            product_family = self._extract_product_family(
                str(row.get('Product_Name', '')),
                str(row.get('Product_Platform_Description_Name', ''))
            )

            install_base = InstallBase(
                serial_number=str(row.get('Serial_Number_Id')),
                product_id=str(row.get('Product_Id')),
                product_name=str(row.get('Product_Name')),
                product_platform=str(row.get('Product_Platform_Description_Name')),
                product_family=product_family,
                line_description=str(row.get('Line_Description_Name')),
                business_area=str(row.get('Business_Area_Description_Name')),
                legacy_gbu=str(row.get('Legacy_Global_Business_Unit')),
                product_eol_date=eol_date,
                product_eos_date=eos_date,
                service_start_date=service_start,
                service_end_date=service_end,
                support_status=support_status,
                service_agreement_id=str(row.get('Service_Agreement_Id')),
                service_source=str(row.get('Final_Service_Source')),
                account_id=account.id,
                territory_id=str(row.get('Account_Sales_Territory_Id')),
                days_since_eol=days_since_eol,
                days_since_expiry=days_since_expiry,
                risk_level=risk_level
            )
            session.add(install_base)

        print(f"  → Loaded {len(df)} install base records")

    def _load_opportunities(self, session):
        """Load opportunities data."""
        file_path = Path(self.config.install_base_path)
        if not file_path.exists():
            return

        df = pd.read_excel(file_path, sheet_name='Opportunity')

        for idx, row in df.iterrows():
            # Check if opportunity already exists
            opp_id = str(row.get('HPE Opportunity ID'))
            if session.query(Opportunity).filter(Opportunity.opportunity_id == opp_id).first():
                continue

            # Get or create account
            account = self._get_or_create_account(
                session,
                account_name=str(row.get('Account Name')),
                territory_id=str(row.get('Account ST ID'))
            )

            opportunity = Opportunity(
                opportunity_id=str(row.get('HPE Opportunity ID')),
                opportunity_name=str(row.get('Opportunity NAme')),  # Note: typo in source
                product_line=str(row.get('Product Line')),
                account_id=account.id,
                territory_id=str(row.get('Account ST ID'))
            )
            session.add(opportunity)

        print(f"  → Loaded {len(df)} opportunity records")

    def _load_projects(self, session):
        """Load A&PS projects data."""
        file_path = Path(self.config.install_base_path)
        if not file_path.exists():
            return

        df = pd.read_excel(file_path, sheet_name='A&PS Project sample')

        loaded_count = 0
        for idx, row in df.iterrows():
            # Get project ID
            project_id = str(row.get('PRJ Siebel ID'))
            # Check for invalid/placeholder project IDs
            invalid_ids = ['#', 'nan', 'None', '']
            if (not project_id or
                project_id in invalid_ids or
                'NOT AV' in project_id.upper() or  # Catches "NOT AVAILABLE" and typos
                len(project_id) < 3):
                # Generate unique ID for missing/invalid project IDs
                project_id = f"UNKNOWN_PRJ_{idx}"

            # Get or create account
            account = self._get_or_create_account(
                session,
                account_name=str(row.get('PRJ Customer')),
                territory_id=None,
                account_id=str(row.get('PRJ Customer ID'))
            )

            # Parse dates
            start_date = self._parse_date(row.get('PRJ Start Date'))
            end_date = self._parse_date(row.get('PRJ End Date'))

            project = Project(
                project_id=project_id,
                project_description=str(row.get('PRJ Description')),
                practice=str(row.get('PRJ Practice')),
                function=str(row.get('PRJ Function')),
                business_area=str(row.get('PRJ Business Area')),
                status=str(row.get('PRJ Status Description')),
                start_date=start_date,
                end_date=end_date,
                project_length_days=int(row.get('PRJ Days')) if pd.notna(row.get('PRJ Days')) else None,
                size_category=str(row.get('PRJ Size')),
                labor_cost=self._parse_float(row.get('Labor Cost')),
                third_party_service_cost=self._parse_float(row.get('3rd Party Svc Cost')),
                third_party_material_cost=self._parse_float(row.get('3rd Party Mat Cost')),
                account_id=account.id,
                country=str(row.get('Country')),
                region=str(row.get('PRJ Region'))
            )
            session.add(project)
            loaded_count += 1

        print(f"  → Loaded {loaded_count} project records (out of {len(df)} total)")

    def _load_services(self, session):
        """Load services catalog."""
        file_path = Path(self.config.install_base_path)
        if not file_path.exists():
            return

        df = pd.read_excel(file_path, sheet_name='Services')

        for idx, row in df.iterrows():
            practice = row.get('Practice')
            sub_practice = row.get('Sub-Practice')
            service_name = row.get('Services')

            # Skip empty rows
            if pd.isna(service_name):
                continue

            service = ServiceCatalog(
                practice=str(practice) if pd.notna(practice) else None,
                sub_practice=str(sub_practice) if pd.notna(sub_practice) else None,
                service_name=str(service_name),
                service_category=self._categorize_service(str(service_name))
            )
            session.add(service)

        print(f"  → Loaded {len([s for s in df['Services'] if pd.notna(s)])} service records")

    def _categorize_service(self, service_name: str) -> str:
        """Categorize service based on name."""
        service_lower = service_name.lower()

        if 'health' in service_lower or 'assessment' in service_lower:
            return "Health Check"
        elif 'migration' in service_lower:
            return "Migration"
        elif 'design' in service_lower or 'implementation' in service_lower:
            return "Design & Implementation"
        elif 'optimization' in service_lower or 'performance' in service_lower:
            return "Optimization"
        elif 'upgrade' in service_lower:
            return "Upgrade"
        else:
            return "Other"

    def _load_service_sku_mappings(self, session):
        """Load service SKU to product mappings."""
        file_path = Path(self.config.service_sku_path)
        if not file_path.exists():
            print(f"Warning: Service SKU file not found: {file_path}")
            return

        df = pd.read_excel(file_path, sheet_name='Sheet2')

        # Skip header rows (first 3 rows are empty/title)
        df = df.iloc[4:].reset_index(drop=True)

        current_category = None
        current_product = None

        for idx, row in df.iterrows():
            # Check if this is a category row (Storage SW, Storage HW)
            product_col = row.iloc[3] if len(row) > 3 else None

            if pd.notna(product_col):
                product_str = str(product_col).strip()

                # Category markers
                if 'Storage SW' in product_str:
                    current_category = "Storage SW"
                    continue
                elif 'Storage HW' in product_str:
                    current_category = "Storage HW"
                    continue

                # Product family
                if product_str and product_str not in ['Product', 'NaN']:
                    current_product = product_str

            # Parse service columns (starting from column 4)
            if current_product and current_category:
                for col_idx in range(4, len(row)):
                    service_text = row.iloc[col_idx]
                    if pd.notna(service_text) and str(service_text).strip():
                        service_sku_mapping = self._parse_service_sku(
                            current_product,
                            current_category,
                            str(service_text)
                        )
                        if service_sku_mapping:
                            session.add(service_sku_mapping)

        print(f"  → Loaded service SKU mappings")

    def _parse_service_sku(self, product_family: str, category: str, service_text: str) -> Optional[ServiceSKUMapping]:
        """Parse service SKU from text."""
        import re

        # Extract SKU codes in parentheses
        sku_match = re.findall(r'\(([A-Z0-9#]+)\)', service_text)
        skus = ','.join(sku_match) if sku_match else None

        # Extract service type (text before parentheses)
        service_type = re.sub(r'\s*\([^)]+\)', '', service_text).strip()

        if service_type:
            return ServiceSKUMapping(
                product_family=product_family,
                product_category=category,
                service_type=service_type,
                service_sku=skus
            )

        return None


if __name__ == "__main__":
    loader = DataLoader()
    loader.load_all()
