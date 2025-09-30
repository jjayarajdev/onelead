"""
LS_SKU Data Loader
Loads LS_SKU data into SQLite database with product-service mappings
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.ls_sku_parser import LSSKUParser
from data_processing.product_matcher import ProductMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSSKUDataLoader:
    """Load LS_SKU data into OneLead SQLite database"""

    def __init__(self, db_path: str = "data/onelead.db"):
        """
        Initialize loader

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None

    def load_all_data(
        self,
        ls_sku_file: str,
        excel_data_file: str = None,
        apply_schema: bool = True
    ) -> Dict:
        """
        Load all LS_SKU data into database

        Args:
            ls_sku_file: Path to LS_SKU Excel file
            excel_data_file: Path to DataExport Excel file (for product matching)
            apply_schema: Whether to apply schema enhancements

        Returns:
            Dictionary with load statistics
        """
        try:
            logger.info("=" * 60)
            logger.info("LS_SKU Data Loading Process")
            logger.info("=" * 60)

            # Connect to database
            self._connect()

            # Apply schema if requested
            if apply_schema:
                self._apply_schema_enhancements()

            # Parse LS_SKU file
            logger.info("\n📊 Step 1: Parsing LS_SKU file...")
            parser = LSSKUParser(ls_sku_file)
            parser.parse_product_mappings()
            stats = parser.get_summary_stats()
            logger.info(f"  ✓ Parsed {stats['total_mappings']} mappings")

            # Load LS_SKU products
            logger.info("\n📦 Step 2: Loading LS_SKU products...")
            product_count = self._load_ls_sku_products(parser)
            logger.info(f"  ✓ Loaded {product_count} LS_SKU products")

            # Load LS_SKU services
            logger.info("\n🔧 Step 3: Loading LS_SKU services...")
            service_count = self._load_ls_sku_services(parser)
            logger.info(f"  ✓ Loaded {service_count} LS_SKU services")

            # Load SKU codes
            logger.info("\n🏷️  Step 4: Loading SKU codes...")
            sku_count = self._load_sku_codes(parser)
            logger.info(f"  ✓ Loaded {sku_count} SKU codes")

            # Create product-service mappings
            logger.info("\n🔗 Step 5: Creating product-service mappings...")
            mapping_count = self._create_product_service_mappings(parser)
            logger.info(f"  ✓ Created {mapping_count} product-service mappings")

            # Create service-SKU mappings
            logger.info("\n🔗 Step 6: Creating service-SKU mappings...")
            sku_mapping_count = self._create_service_sku_mappings(parser)
            logger.info(f"  ✓ Created {sku_mapping_count} service-SKU mappings")

            # Match Install Base products to LS_SKU
            if excel_data_file:
                logger.info("\n🎯 Step 7: Matching Install Base products to LS_SKU...")
                match_count = self._match_install_base_products(parser, excel_data_file)
                logger.info(f"  ✓ Matched {match_count} Install Base products")
            else:
                match_count = 0
                logger.info("\n⚠️  Step 7: Skipping Install Base matching (no data file provided)")

            # Commit changes
            self.conn.commit()
            logger.info("\n✅ All data loaded successfully!")

            return {
                'ls_sku_products': product_count,
                'ls_sku_services': service_count,
                'sku_codes': sku_count,
                'product_service_mappings': mapping_count,
                'service_sku_mappings': sku_mapping_count,
                'install_base_matches': match_count
            }

        except Exception as e:
            logger.error(f"❌ Data loading failed: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            if self.conn:
                self.conn.close()

    def _connect(self):
        """Connect to database"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        logger.info(f"📁 Connected to database: {self.db_path}")

    def _apply_schema_enhancements(self):
        """Apply schema enhancements from SQL file"""
        logger.info("\n🏗️  Applying schema enhancements...")

        schema_file = Path(__file__).parent / "schema_enhancements.sql"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        # Execute schema (skip comments and utility queries)
        statements = []
        in_comment_block = False

        for line in schema_sql.split('\n'):
            stripped = line.strip()

            # Skip single-line comments
            if stripped.startswith('--'):
                continue

            # Track multi-line comments
            if '/*' in stripped:
                in_comment_block = True
            if '*/' in stripped:
                in_comment_block = False
                continue

            if not in_comment_block and stripped:
                statements.append(line)

        # Join and split by semicolon
        full_sql = '\n'.join(statements)
        for statement in full_sql.split(';'):
            if statement.strip():
                try:
                    self.cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    # Ignore "table already exists" errors
                    if 'already exists' not in str(e):
                        raise

        self.conn.commit()
        logger.info("  ✓ Schema enhancements applied")

    def _load_ls_sku_products(self, parser: LSSKUParser) -> int:
        """Load LS_SKU products into dim_ls_sku_product"""
        products = {}

        for mapping in parser.parsed_mappings:
            product_key = (mapping['category'], mapping['product'])
            if product_key not in products:
                products[product_key] = {
                    'name': mapping['product'],
                    'category': mapping['category']
                }

        count = 0
        for (category, name), product in products.items():
            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_ls_sku_product
                (product_name, product_category)
                VALUES (?, ?)
            """, (name, category))
            if self.cursor.rowcount > 0:
                count += 1

        return count

    def _load_ls_sku_services(self, parser: LSSKUParser) -> int:
        """Load LS_SKU services into dim_ls_sku_service"""
        services = {}

        for mapping in parser.parsed_mappings:
            service_key = mapping['service_name']
            if service_key not in services:
                services[service_key] = {
                    'name': mapping['service_name'],
                    'text': mapping['service_text'],
                    'type': mapping['service_type'],
                    'priority': mapping['priority'],
                    'has_sku': mapping['has_sku']
                }

        count = 0
        for service_name, service in services.items():
            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_ls_sku_service
                (service_name, service_text, service_type, priority, has_sku)
                VALUES (?, ?, ?, ?, ?)
            """, (service['name'], service['text'], service['type'],
                  service['priority'], service['has_sku']))
            if self.cursor.rowcount > 0:
                count += 1

        return count

    def _load_sku_codes(self, parser: LSSKUParser) -> int:
        """Load SKU codes into dim_sku_code"""
        skus = set()

        for mapping in parser.parsed_mappings:
            for sku in mapping['sku_codes']:
                skus.add(sku)

        count = 0
        for sku in skus:
            # Determine SKU type based on format
            sku_type = 'Standard'
            if '#' in sku:
                sku_type = 'Variant'

            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_sku_code
                (sku_code, sku_type)
                VALUES (?, ?)
            """, (sku, sku_type))
            if self.cursor.rowcount > 0:
                count += 1

        return count

    def _create_product_service_mappings(self, parser: LSSKUParser) -> int:
        """Create product-service mappings in map_product_service_sku"""
        count = 0

        for mapping in parser.parsed_mappings:
            # Get product key
            self.cursor.execute("""
                SELECT ls_product_key FROM dim_ls_sku_product
                WHERE product_name = ? AND product_category = ?
            """, (mapping['product'], mapping['category']))
            product_result = self.cursor.fetchone()

            # Get service key
            self.cursor.execute("""
                SELECT ls_service_key FROM dim_ls_sku_service
                WHERE service_name = ?
            """, (mapping['service_name'],))
            service_result = self.cursor.fetchone()

            if product_result and service_result:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO map_product_service_sku
                    (ls_product_key, ls_service_key, priority, mapping_source)
                    VALUES (?, ?, ?, 'ls_sku')
                """, (product_result[0], service_result[0], mapping['priority']))
                if self.cursor.rowcount > 0:
                    count += 1

        return count

    def _create_service_sku_mappings(self, parser: LSSKUParser) -> int:
        """Create service-SKU mappings in map_service_sku"""
        count = 0

        for mapping in parser.parsed_mappings:
            # Get service key
            self.cursor.execute("""
                SELECT ls_service_key FROM dim_ls_sku_service
                WHERE service_name = ?
            """, (mapping['service_name'],))
            service_result = self.cursor.fetchone()

            if service_result and mapping['sku_codes']:
                for idx, sku in enumerate(mapping['sku_codes']):
                    # Get SKU key
                    self.cursor.execute("""
                        SELECT sku_key FROM dim_sku_code
                        WHERE sku_code = ?
                    """, (sku,))
                    sku_result = self.cursor.fetchone()

                    if sku_result:
                        # First SKU is primary
                        is_primary = (idx == 0)

                        self.cursor.execute("""
                            INSERT OR IGNORE INTO map_service_sku
                            (ls_service_key, sku_key, is_primary)
                            VALUES (?, ?, ?)
                        """, (service_result[0], sku_result[0], is_primary))
                        if self.cursor.rowcount > 0:
                            count += 1

        return count

    def _match_install_base_products(
        self,
        parser: LSSKUParser,
        excel_file: str
    ) -> int:
        """Match Install Base products to LS_SKU products"""
        # Load Install Base data
        df_install = pd.read_excel(excel_file, sheet_name='Install Base')

        # Get LS_SKU product names
        ls_sku_products = parser.get_dataframe()['product'].unique().tolist()

        # Initialize matcher
        matcher = ProductMatcher()

        # Get Install Base products from database
        self.cursor.execute("""
            SELECT
                p.product_key,
                p.product_serial_number,
                p.product_description,
                p.product_platform,
                p.product_business
            FROM dim_product p
        """)

        install_products = []
        for row in self.cursor.fetchall():
            install_products.append({
                'product_key': row[0],
                'Product_Name': row[2] or '',  # product_description
                'Product_Platform_Description_Name': row[3] or '',
                'Business_Area_Description_Name': row[4] or ''
            })

        # Perform matching
        results = matcher.batch_match(install_products, ls_sku_products, min_confidence=60)

        # Insert matches
        count = 0
        for result in results:
            if result['matched_ls_sku_product']:
                # Get LS_SKU product key
                self.cursor.execute("""
                    SELECT ls_product_key FROM dim_ls_sku_product
                    WHERE product_name = ?
                """, (result['matched_ls_sku_product'],))
                ls_product_result = self.cursor.fetchone()

                if ls_product_result:
                    self.cursor.execute("""
                        INSERT OR REPLACE INTO map_install_base_to_ls_sku
                        (product_key, ls_product_key, confidence_score,
                         confidence_level, match_method, matched_category)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        result['product_key'],
                        ls_product_result[0],
                        result['confidence_score'],
                        result['confidence_level'],
                        result['match_method'],
                        result.get('matched_category')
                    ))
                    count += 1
            elif result.get('matched_category'):
                # Store category match even without specific product
                self.cursor.execute("""
                    INSERT OR REPLACE INTO map_install_base_to_ls_sku
                    (product_key, ls_product_key, confidence_score,
                     confidence_level, match_method, matched_category)
                    VALUES (?, NULL, ?, ?, ?, ?)
                """, (
                    result['product_key'],
                    result['confidence_score'],
                    result['confidence_level'],
                    result['match_method'],
                    result['matched_category']
                ))
                count += 1

        return count

    def generate_summary_report(self) -> Dict:
        """Generate summary report of loaded data"""
        self._connect()

        report = {}

        # Count LS_SKU products by category
        self.cursor.execute("""
            SELECT product_category, COUNT(*) as count
            FROM dim_ls_sku_product
            GROUP BY product_category
        """)
        report['products_by_category'] = dict(self.cursor.fetchall())

        # Count services by type
        self.cursor.execute("""
            SELECT service_type, COUNT(*) as count
            FROM dim_ls_sku_service
            GROUP BY service_type
        """)
        report['services_by_type'] = dict(self.cursor.fetchall())

        # Count matched products
        self.cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN ls_product_key IS NOT NULL THEN 1 ELSE 0 END) as matched,
                AVG(confidence_score) as avg_confidence
            FROM map_install_base_to_ls_sku
        """)
        row = self.cursor.fetchone()
        report['install_base_matching'] = {
            'total_products': row[0],
            'matched_products': row[1],
            'match_rate': f"{(row[1]/row[0]*100) if row[0] > 0 else 0:.1f}%",
            'avg_confidence': f"{row[2]:.1f}" if row[2] else "N/A"
        }

        # Count SKU codes
        self.cursor.execute("SELECT COUNT(*) FROM dim_sku_code")
        report['total_sku_codes'] = self.cursor.fetchone()[0]

        # Count mappings
        self.cursor.execute("SELECT COUNT(*) FROM map_product_service_sku")
        report['total_mappings'] = self.cursor.fetchone()[0]

        self.conn.close()

        return report


# Main execution
if __name__ == "__main__":
    # File paths - use relative paths from current working directory
    import os
    from pathlib import Path

    # Work from current directory (handles both local and Streamlit Cloud)
    current_dir = Path(os.getcwd())
    data_dir = current_dir / 'data'

    ls_sku_file = str(data_dir / 'LS_SKU_for_Onelead.xlsx')
    excel_file = str(data_dir / 'DataExportAug29th.xlsx')
    db_file = str(data_dir / 'onelead.db')

    # Initialize loader
    loader = LSSKUDataLoader(db_file)

    # Load all data
    stats = loader.load_all_data(
        ls_sku_file=ls_sku_file,
        excel_data_file=excel_file,
        apply_schema=True
    )

    # Print statistics
    print("\n" + "=" * 60)
    print("DATA LOADING SUMMARY")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title():.<40} {value:>6}")

    # Generate detailed report
    print("\n" + "=" * 60)
    print("DETAILED REPORT")
    print("=" * 60)

    report = loader.generate_summary_report()

    print("\n📦 Products by Category:")
    for category, count in report['products_by_category'].items():
        print(f"  {category:.<35} {count:>4}")

    print("\n🔧 Services by Type:")
    for service_type, count in sorted(report['services_by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {service_type:.<35} {count:>4}")

    print(f"\n🎯 Install Base Matching:")
    print(f"  Total Products:................ {report['install_base_matching']['total_products']}")
    print(f"  Matched Products:.............. {report['install_base_matching']['matched_products']}")
    print(f"  Match Rate:.................... {report['install_base_matching']['match_rate']}")
    print(f"  Average Confidence:............ {report['install_base_matching']['avg_confidence']}")

    print(f"\n🏷️  Total SKU Codes: {report['total_sku_codes']}")
    print(f"🔗 Total Mappings: {report['total_mappings']}")

    print("\n✅ Data loading complete!")
    print(f"📁 Database: {db_file}")