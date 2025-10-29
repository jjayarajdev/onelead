"""
Product Matcher Module
Matches Install Base product names to LS_SKU product names using fuzzy matching and keyword mapping
"""

import re
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductMatcher:
    """
    Matches Install Base products to LS_SKU products using multiple strategies:
    1. Exact keyword matching (fastest, most accurate)
    2. Alias-based matching (handles product variations)
    3. Fuzzy string matching (fallback for unknown products)
    """

    # Product aliases for common variations
    PRODUCT_ALIASES = {
        # Storage Products
        '3PAR': ['3par', '3PAR StoreServ', 'StoreServ', '3par storeserv'],
        'Primera': ['primera', 'Primera Storage', 'primera storage'],
        'Alletra': ['alletra', 'Alletra 9000', 'Alletra 6000', 'alletra 9000', 'alletra 6000'],
        'Alletra MP': ['alletra mp', 'alletraMP', 'alletra-mp', 'greenlake block storage'],
        'Nimble': ['nimble', 'nimble storage', 'nimble dHCI'],
        'MSA': ['msa', 'msa storage', 'modular smart array'],
        'StoreOnce': ['storeonce', 'store once', 'backup'],
        'MSL': ['msl', 'tape', 'tape library'],

        # Compute Products
        'Servers': ['proliant', 'dl360', 'dl380', 'dl580', 'ml', 'server', 'gen8', 'gen9', 'gen10'],
        'Synergy': ['synergy', 'synergy compute', 'composable'],
        'C7000': ['c7000', 'c-7000', 'blade enclosure', 'bladesystem'],

        # Networking
        'Networking': ['aruba', 'switch', 'network', '5400', '5900', '2930'],
        'SAN': ['san', 'san switch', 'fibre channel', 'fc switch', 'brocade'],

        # Converged Systems
        'Linux (All Flavour)': ['linux', 'red hat', 'rhel', 'suse', 'ubuntu', 'centos'],
        'Cluster (SG, SUSE, RHEL)': ['serviceguard', 'cluster', 'ha cluster', 'high availability'],
        'SAP HANA': ['sap hana', 'sap', 'hana', 's4hana'],
        'Converged Systems': ['converged', 'convergedsystem'],

        # HCI
        'SimpliVity': ['simplivity', 'simpli', 'hpe simplivity'],
        'Nimble dHCI': ['nimble dhci', 'dhci', 'nimble hci'],
        'Nutanix': ['nutanix', 'nutanix hci'],
        'Azure HCI': ['azure hci', 'azure stack hci', 'azurestackhci'],
    }

    # Category keywords for broader matching
    CATEGORY_KEYWORDS = {
        'Storage SW': ['storage', 'disk', 'array', 'san', 'nas'],
        'Storage HW': ['storage', 'disk', 'array', 'san', 'nas'],
        'Compute': ['server', 'compute', 'proliant', 'blade', 'rack'],
        'Switches': ['switch', 'network', 'aruba', 'ethernet'],
        'Converged Systems': ['linux', 'unix', 'os', 'sap', 'cluster'],
        'HCI': ['hyperconverged', 'hci', 'simplivity', 'nutanix'],
    }

    def __init__(self):
        """Initialize the product matcher"""
        self.match_cache = {}  # Cache for performance

    def normalize_product_name(self, product_name: str) -> str:
        """
        Normalize product name for better matching

        Args:
            product_name: Raw product name

        Returns:
            Normalized product name
        """
        if not product_name or product_name == '(null)':
            return ''

        # Convert to lowercase
        normalized = product_name.lower()

        # Remove common prefixes/suffixes
        prefixes_to_remove = ['hpe ', 'hp ', 'hewlett packard enterprise ']
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        # Remove version numbers and generation markers
        normalized = re.sub(r'\bgen\d+\b', '', normalized)
        normalized = re.sub(r'\bv\d+\b', '', normalized)

        # Remove CTO, SFF, LFF etc.
        normalized = re.sub(r'\b(cto|sff|lff|sas|sata)\b', '', normalized)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def extract_keywords(self, product_name: str) -> List[str]:
        """
        Extract important keywords from product name

        Args:
            product_name: Product name

        Returns:
            List of keywords
        """
        normalized = self.normalize_product_name(product_name)
        # Split into words and filter out common words
        stopwords = {'the', 'and', 'with', 'for', 'server', 'kit', 'option'}
        words = [w for w in normalized.split() if w not in stopwords and len(w) > 2]
        return words

    def match_by_exact_keyword(self, install_base_product: str, ls_sku_product: str) -> Optional[int]:
        """
        Match using exact keyword presence

        Args:
            install_base_product: Product name from Install Base
            ls_sku_product: Product name from LS_SKU

        Returns:
            Confidence score (0-100) or None if no match
        """
        normalized_ib = self.normalize_product_name(install_base_product)
        ls_sku_lower = ls_sku_product.lower()

        # Check if LS_SKU product name appears in Install Base product
        if ls_sku_lower in normalized_ib:
            return 100

        # Check keywords
        ib_keywords = self.extract_keywords(install_base_product)
        if ls_sku_lower in ib_keywords:
            return 95

        return None

    def match_by_alias(self, install_base_product: str, ls_sku_product: str) -> Optional[int]:
        """
        Match using product aliases

        Args:
            install_base_product: Product name from Install Base
            ls_sku_product: Product name from LS_SKU

        Returns:
            Confidence score (0-100) or None if no match
        """
        normalized_ib = self.normalize_product_name(install_base_product)

        # Check if ls_sku_product has aliases
        if ls_sku_product in self.PRODUCT_ALIASES:
            aliases = self.PRODUCT_ALIASES[ls_sku_product]

            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in normalized_ib:
                    # Higher confidence for longer matches
                    if len(alias_lower) > 6:
                        return 90
                    else:
                        return 85

        return None

    def match_by_fuzzy(self, install_base_product: str, ls_sku_product: str) -> int:
        """
        Match using fuzzy string similarity

        Args:
            install_base_product: Product name from Install Base
            ls_sku_product: Product name from LS_SKU

        Returns:
            Confidence score (0-100)
        """
        normalized_ib = self.normalize_product_name(install_base_product)
        ls_sku_lower = ls_sku_product.lower()

        # Use partial ratio for substring matching
        score = fuzz.partial_ratio(normalized_ib, ls_sku_lower)

        return score

    def match_product(
        self,
        install_base_product: str,
        ls_sku_products: List[str],
        min_confidence: int = 70
    ) -> Tuple[Optional[str], int, str]:
        """
        Match Install Base product to best LS_SKU product

        Args:
            install_base_product: Product name from Install Base
            ls_sku_products: List of LS_SKU product names
            min_confidence: Minimum confidence threshold (0-100)

        Returns:
            Tuple of (matched_product, confidence_score, match_method)
        """
        # Check cache first
        cache_key = f"{install_base_product}:{','.join(ls_sku_products)}"
        if cache_key in self.match_cache:
            return self.match_cache[cache_key]

        if not install_base_product or install_base_product == '(null)':
            return (None, 0, 'no_input')

        best_match = None
        best_score = 0
        best_method = 'none'

        for ls_sku_product in ls_sku_products:
            # Try exact keyword match first (highest priority)
            score = self.match_by_exact_keyword(install_base_product, ls_sku_product)
            if score and score > best_score:
                best_match = ls_sku_product
                best_score = score
                best_method = 'exact_keyword'

            # Try alias match
            score = self.match_by_alias(install_base_product, ls_sku_product)
            if score and score > best_score:
                best_match = ls_sku_product
                best_score = score
                best_method = 'alias'

            # Try fuzzy match as fallback
            score = self.match_by_fuzzy(install_base_product, ls_sku_product)
            if score > best_score:
                best_match = ls_sku_product
                best_score = score
                best_method = 'fuzzy'

        # Only return if confidence meets threshold
        if best_score >= min_confidence:
            result = (best_match, best_score, best_method)
        else:
            result = (None, best_score, 'below_threshold')

        # Cache the result
        self.match_cache[cache_key] = result

        return result

    def match_by_category(
        self,
        install_base_product: str,
        product_platform: str,
        business_area: str
    ) -> Optional[str]:
        """
        Match to LS_SKU category based on Install Base metadata

        Args:
            install_base_product: Product name from Install Base
            product_platform: Platform description
            business_area: Business area description

        Returns:
            LS_SKU category or None
        """
        # Combine all fields for matching
        combined_text = f"{install_base_product} {product_platform} {business_area}".lower()

        # Try to match to a category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                return category

        return None

    def get_match_confidence_level(self, score: int) -> str:
        """
        Convert numeric confidence score to descriptive level

        Args:
            score: Confidence score (0-100)

        Returns:
            Confidence level description
        """
        if score >= 90:
            return 'High'
        elif score >= 75:
            return 'Medium'
        elif score >= 60:
            return 'Low'
        else:
            return 'Very Low'

    def batch_match(
        self,
        install_base_products: List[Dict],
        ls_sku_products: List[str],
        min_confidence: int = 70
    ) -> List[Dict]:
        """
        Match multiple Install Base products to LS_SKU products

        Args:
            install_base_products: List of dicts with Install Base product info
            ls_sku_products: List of LS_SKU product names
            min_confidence: Minimum confidence threshold

        Returns:
            List of match results with metadata
        """
        results = []

        for ib_product in install_base_products:
            product_name = ib_product.get('Product_Name', '')
            matched_product, score, method = self.match_product(
                product_name,
                ls_sku_products,
                min_confidence
            )

            result = {
                'install_base_product': product_name,
                'install_base_platform': ib_product.get('Product_Platform_Description_Name', ''),
                'install_base_business_area': ib_product.get('Business_Area_Description_Name', ''),
                'matched_ls_sku_product': matched_product,
                'confidence_score': score,
                'confidence_level': self.get_match_confidence_level(score),
                'match_method': method,
                'serial_number': ib_product.get('Serial_Number_Id', ''),
                'support_status': ib_product.get('Support_Status', ''),
            }

            # If no direct match, try category match
            if not matched_product:
                category = self.match_by_category(
                    product_name,
                    ib_product.get('Product_Platform_Description_Name', ''),
                    ib_product.get('Business_Area_Description_Name', '')
                )
                result['matched_category'] = category
            else:
                result['matched_category'] = None

            results.append(result)

        return results


# Main execution for testing
if __name__ == "__main__":
    import pandas as pd

    # Load Install Base data
    install_base_file = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/DataExportAug29th.xlsx'
    df_install = pd.read_excel(install_base_file, sheet_name='Install Base')

    # LS_SKU products (from parser)
    ls_sku_products = [
        '3PAR', 'Primera', 'Alletra', 'Alletra MP', 'Nimble', 'MSA', 'StoreOnce', 'MSL',
        'Servers', 'Synergy', 'C7000',
        'Networking', 'SAN',
        'Linux (All Flavour)', 'Cluster (SG, SUSE, RHEL)', 'SAP HANA', 'Converged Systems',
        'SimpliVity', 'Nimble dHCI', 'Nutanix', 'Azure HCI'
    ]

    # Initialize matcher
    matcher = ProductMatcher()

    # Convert Install Base to list of dicts
    install_products = df_install.to_dict('records')

    # Perform batch matching
    print("=== Product Matching Analysis ===\n")
    results = matcher.batch_match(install_products, ls_sku_products, min_confidence=60)

    # Convert to DataFrame for analysis
    df_results = pd.DataFrame(results)

    # Summary statistics
    print(f"Total Install Base Products: {len(results)}")
    print(f"Matched Products: {df_results['matched_ls_sku_product'].notna().sum()}")
    print(f"Unmatched Products: {df_results['matched_ls_sku_product'].isna().sum()}")
    print(f"\nMatch Methods:")
    print(df_results['match_method'].value_counts())
    print(f"\nConfidence Levels:")
    print(df_results['confidence_level'].value_counts())

    # Show matched products
    print("\n=== Matched Products (High Confidence) ===")
    high_confidence = df_results[df_results['confidence_score'] >= 85]
    print(high_confidence[[
        'install_base_product',
        'matched_ls_sku_product',
        'confidence_score',
        'match_method'
    ]].to_string(index=False))

    # Show unmatched products
    print("\n=== Unmatched Products ===")
    unmatched = df_results[df_results['matched_ls_sku_product'].isna()]
    print(unmatched[[
        'install_base_product',
        'install_base_platform',
        'matched_category',
        'confidence_score'
    ]].head(10).to_string(index=False))

    # Export results
    output_file = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/outputs/product_matching_results.csv'
    df_results.to_csv(output_file, index=False)
    print(f"\n✓ Exported matching results to: {output_file}")