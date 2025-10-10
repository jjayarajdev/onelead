"""
LS_SKU Parser Module
Extracts product-to-service mappings with SKU codes from LS_SKU_for_Onelead.xlsx
"""

import pandas as pd
import re
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSSKUParser:
    """Parser for LS_SKU_for_Onelead.xlsx file"""

    def __init__(self, file_path: str):
        """
        Initialize parser with file path

        Args:
            file_path: Path to LS_SKU_for_Onelead.xlsx
        """
        self.file_path = file_path
        self.raw_data = None
        self.parsed_mappings = []
        self.categories = []

    def load_data(self) -> pd.DataFrame:
        """Load raw Excel data"""
        try:
            self.raw_data = pd.read_excel(
                self.file_path,
                sheet_name='Sheet2',
                header=None
            )
            logger.info(f"Loaded LS_SKU data: {self.raw_data.shape[0]} rows, {self.raw_data.shape[1]} columns")
            return self.raw_data
        except Exception as e:
            logger.error(f"Error loading LS_SKU file: {e}")
            raise

    def extract_sku_from_text(self, text: str) -> List[str]:
        """
        Extract SKU codes from service description text

        Args:
            text: Service description text

        Returns:
            List of SKU codes found
        """
        if pd.isna(text):
            return []

        # Pattern matches SKU formats like: H9Q53AC, HM002A1, HA124A1#5Y8, HL997A1
        sku_pattern = r'([A-Z]{1,2}[0-9]{3,4}[A-Z]{0,2}(?:#[A-Z0-9]+)?)'
        skus = re.findall(sku_pattern, str(text))

        return list(set(skus))  # Remove duplicates

    def parse_service_entry(self, service_text: str) -> Dict:
        """
        Parse a single service entry to extract name and SKU

        Args:
            service_text: Raw service text (e.g., "OS upgrade (HM002A1/HM002AE/HM002AC)")

        Returns:
            Dictionary with service_name and sku_codes
        """
        if pd.isna(service_text):
            return None

        service_text = str(service_text).strip()
        if not service_text:
            return None

        # Extract SKUs
        skus = self.extract_sku_from_text(service_text)

        # Extract service name (text before parentheses or full text if no parentheses)
        service_name_match = re.match(r'^([^(]+)', service_text)
        service_name = service_name_match.group(1).strip() if service_name_match else service_text

        return {
            'service_name': service_name,
            'service_text': service_text,
            'sku_codes': skus,
            'has_sku': len(skus) > 0
        }

    def categorize_service_type(self, service_name: str) -> str:
        """
        Categorize service into type based on name

        Args:
            service_name: Name of the service

        Returns:
            Service type category
        """
        service_name_lower = service_name.lower()

        if any(keyword in service_name_lower for keyword in ['install', 'startup', 'deployment']):
            return 'Installation & Startup'
        elif any(keyword in service_name_lower for keyword in ['upgrade', 'update']):
            return 'Upgrade'
        elif any(keyword in service_name_lower for keyword in ['health check', 'assessment']):
            return 'Health Check'
        elif any(keyword in service_name_lower for keyword in ['migration', 'move']):
            return 'Migration'
        elif any(keyword in service_name_lower for keyword in ['configuration', 'config', 'setup']):
            return 'Configuration'
        elif any(keyword in service_name_lower for keyword in ['analysis', 'performance']):
            return 'Analysis'
        elif any(keyword in service_name_lower for keyword in ['replication', 'remote copy', 'peer persistence']):
            return 'Replication & DR'
        elif any(keyword in service_name_lower for keyword in ['integration']):
            return 'Integration'
        elif any(keyword in service_name_lower for keyword in ['expansion', 'rebalance']):
            return 'Expansion'
        else:
            return 'Other'

    def parse_product_mappings(self) -> List[Dict]:
        """
        Parse the entire LS_SKU file and extract all product-service mappings

        Returns:
            List of dictionaries containing product-service mappings
        """
        if self.raw_data is None:
            self.load_data()

        mappings = []
        current_category = None

        # Iterate through rows starting from row 4 (where actual data begins)
        for idx, row in self.raw_data.iterrows():
            # Column 3 contains product names
            product_cell = row[3]

            if pd.isna(product_cell):
                continue

            product = str(product_cell).strip()

            # Skip empty rows and header-like rows
            if not product or product == 'Product':
                continue

            # Identify category headers (these are usually standalone without services)
            category_keywords = [
                'Storage SW', 'Storage HW', 'Compute', 'Switches',
                'Converged Systems', 'HCI', 'Fixed SKU', 'Fixed Sku'
            ]

            if product in category_keywords:
                current_category = product
                self.categories.append(product)
                continue

            # Extract services from columns 4-10
            services = []
            for col_idx in range(4, 11):
                service_text = row[col_idx]
                service_entry = self.parse_service_entry(service_text)

                if service_entry:
                    services.append(service_entry)

            # Only add if there are services mapped
            if services:
                for service in services:
                    mapping = {
                        'category': current_category,
                        'product': product,
                        'service_name': service['service_name'],
                        'service_text': service['service_text'],
                        'sku_codes': service['sku_codes'],
                        'has_sku': service['has_sku'],
                        'service_type': self.categorize_service_type(service['service_name']),
                        'priority': self._calculate_priority(service['service_name'], current_category)
                    }
                    mappings.append(mapping)

        self.parsed_mappings = mappings
        logger.info(f"Parsed {len(mappings)} product-service mappings")
        logger.info(f"Found {len(self.categories)} categories: {self.categories}")

        return mappings

    def _calculate_priority(self, service_name: str, category: str) -> int:
        """
        Calculate priority score for a service

        Priority levels:
        1 = High (Critical services like Health Check, Install, Upgrade)
        2 = Medium (Configuration, Migration, Analysis)
        3 = Low (Other services)

        Args:
            service_name: Name of the service
            category: Product category

        Returns:
            Priority score (1-3)
        """
        service_lower = service_name.lower()

        # High priority services
        high_priority_keywords = [
            'health check', 'install', 'startup', 'os upgrade',
            'firmware upgrade', 'migration'
        ]

        if any(keyword in service_lower for keyword in high_priority_keywords):
            return 1

        # Medium priority services
        medium_priority_keywords = [
            'configuration', 'analysis', 'performance', 'integration',
            'replication', 'remote copy'
        ]

        if any(keyword in service_lower for keyword in medium_priority_keywords):
            return 2

        # Low priority (everything else)
        return 3

    def get_dataframe(self) -> pd.DataFrame:
        """
        Convert parsed mappings to pandas DataFrame

        Returns:
            DataFrame with all product-service mappings
        """
        if not self.parsed_mappings:
            self.parse_product_mappings()

        df = pd.DataFrame(self.parsed_mappings)

        # Expand SKU codes (one row per SKU)
        expanded_rows = []
        for _, row in df.iterrows():
            if row['sku_codes']:
                for sku in row['sku_codes']:
                    new_row = row.copy()
                    new_row['sku_code'] = sku
                    expanded_rows.append(new_row)
            else:
                new_row = row.copy()
                new_row['sku_code'] = None
                expanded_rows.append(new_row)

        df_expanded = pd.DataFrame(expanded_rows)
        df_expanded = df_expanded.drop(columns=['sku_codes'])

        return df_expanded

    def get_services_by_product(self, product_name: str) -> List[Dict]:
        """
        Get all services for a specific product

        Args:
            product_name: Product name (e.g., "3PAR", "SimpliVity")

        Returns:
            List of services for the product
        """
        if not self.parsed_mappings:
            self.parse_product_mappings()

        return [m for m in self.parsed_mappings if m['product'].lower() == product_name.lower()]

    def get_products_by_category(self, category: str) -> List[str]:
        """
        Get all products in a category

        Args:
            category: Category name (e.g., "Storage SW", "Compute")

        Returns:
            List of unique product names
        """
        if not self.parsed_mappings:
            self.parse_product_mappings()

        products = [m['product'] for m in self.parsed_mappings if m['category'] == category]
        return list(set(products))

    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics of parsed data

        Returns:
            Dictionary with statistics
        """
        if not self.parsed_mappings:
            self.parse_product_mappings()

        df = pd.DataFrame(self.parsed_mappings)

        stats = {
            'total_mappings': len(self.parsed_mappings),
            'unique_products': df['product'].nunique(),
            'unique_services': df['service_name'].nunique(),
            'categories': list(df['category'].unique()),
            'mappings_with_sku': df['has_sku'].sum(),
            'mappings_without_sku': (~df['has_sku']).sum(),
            'services_by_type': df['service_type'].value_counts().to_dict(),
            'services_by_category': df['category'].value_counts().to_dict()
        }

        return stats

    def export_to_csv(self, output_path: str) -> None:
        """
        Export parsed mappings to CSV

        Args:
            output_path: Path for output CSV file
        """
        df = self.get_dataframe()
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} mappings to {output_path}")


# Main execution for testing
if __name__ == "__main__":
    # Test the parser
    file_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/LS_SKU_for_Onelead.xlsx'

    parser = LSSKUParser(file_path)
    parser.load_data()
    mappings = parser.parse_product_mappings()

    # Print summary
    stats = parser.get_summary_stats()
    print("\n=== LS_SKU Parser Summary ===")
    print(f"Total Mappings: {stats['total_mappings']}")
    print(f"Unique Products: {stats['unique_products']}")
    print(f"Unique Services: {stats['unique_services']}")
    print(f"Mappings with SKU: {stats['mappings_with_sku']}")
    print(f"Mappings without SKU: {stats['mappings_without_sku']}")
    print(f"\nCategories: {stats['categories']}")
    print(f"\nServices by Type:")
    for service_type, count in stats['services_by_type'].items():
        print(f"  {service_type}: {count}")

    # Show sample mappings
    print("\n=== Sample Mappings ===")
    df = parser.get_dataframe()
    print(df[['category', 'product', 'service_name', 'sku_code', 'priority']].head(15).to_string(index=False))

    # Test product lookup
    print("\n=== Services for 3PAR ===")
    threeparr_services = parser.get_services_by_product("3PAR")
    for svc in threeparr_services[:5]:
        print(f"  - {svc['service_name']} (SKUs: {svc['sku_codes']}) [Priority: {svc['priority']}]")