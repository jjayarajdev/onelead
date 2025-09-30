"""
Enhanced HPE OneLead Recommendation Engine with LS_SKU Integration
Provides SKU-level service recommendations using 3-layer matching strategy
"""

import pandas as pd
import numpy as np
import sqlite3
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EnhancedRecommendationEngine:
    """
    Enhanced service recommendation engine with LS_SKU integration

    Features:
    - 3-layer recommendation strategy (exact product → category → fallback)
    - SKU-level precision for quote generation
    - Expired product urgency handling
    - Cross-sell intelligence
    - Service credit optimization
    """

    def __init__(self, db_path: str = "data/onelead.db"):
        """
        Initialize enhanced recommendation engine

        Args:
            db_path: Path to SQLite database with LS_SKU data
        """
        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        logger.info(f"Enhanced Recommendation Engine initialized with database: {self.db_path}")

    def _get_connection(self):
        """Get a thread-safe database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def get_product_recommendations(
        self,
        product_name: str,
        product_platform: Optional[str] = None,
        support_status: Optional[str] = None,
        days_to_eol: Optional[int] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Get service recommendations for a specific product

        3-Layer Strategy:
        Layer 1: Exact product match via LS_SKU
        Layer 2: Product category/platform match
        Layer 3: Fallback to generic services

        Args:
            product_name: Product name from Install Base
            product_platform: Product platform (Compute, Storage, Network)
            support_status: Current support status
            days_to_eol: Days until end-of-life
            top_n: Number of recommendations to return

        Returns:
            List of service recommendations with SKU codes
        """
        recommendations = []

        # Layer 1: Try exact product match via LS_SKU mapping
        layer1_recs = self._get_exact_product_recommendations(product_name, top_n)

        if layer1_recs:
            recommendations.extend(layer1_recs)
            logger.info(f"Layer 1 (Exact): Found {len(layer1_recs)} recommendations for {product_name}")

        # Layer 2: Try category/platform match if not enough recommendations
        if len(recommendations) < top_n and product_platform:
            layer2_recs = self._get_category_recommendations(product_platform, top_n - len(recommendations))
            recommendations.extend(layer2_recs)
            logger.info(f"Layer 2 (Category): Added {len(layer2_recs)} recommendations")

        # Layer 3: Fallback to generic services
        if len(recommendations) < top_n:
            layer3_recs = self._get_fallback_recommendations(top_n - len(recommendations))
            recommendations.extend(layer3_recs)
            logger.info(f"Layer 3 (Fallback): Added {len(layer3_recs)} recommendations")

        # Adjust priorities based on urgency
        if support_status or days_to_eol is not None:
            recommendations = self._adjust_for_urgency(
                recommendations,
                support_status,
                days_to_eol
            )

        return recommendations[:top_n]

    def _get_exact_product_recommendations(self, product_name: str, top_n: int) -> List[Dict]:
        """Layer 1: Get recommendations via exact product match"""
        query = """
        SELECT
            s.service_name,
            s.service_type,
            s.service_text,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            lp.product_name as ls_sku_product,
            lp.product_category,
            m.confidence_score as match_confidence,
            m.match_method,
            'exact_product' as recommendation_layer
        FROM dim_product p
        JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
        JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
        JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
        JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE p.product_description LIKE ?
        GROUP BY s.ls_service_key
        ORDER BY s.priority ASC, match_confidence DESC
        LIMIT ?
        """

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (f"%{product_name}%", top_n))

        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'service_name': row['service_name'],
                'service_type': row['service_type'],
                'service_text': row['service_text'],
                'priority': row['priority'],
                'sku_codes': row['sku_codes'] if row['sku_codes'] else 'Contact HPE',
                'ls_sku_product': row['ls_sku_product'],
                'product_category': row['product_category'],
                'match_confidence': row['match_confidence'],
                'match_method': row['match_method'],
                'recommendation_layer': row['recommendation_layer'],
                'confidence_score': 95 if row['match_confidence'] >= 85 else 80
            })

        conn.close()
        return recommendations

    def _get_category_recommendations(self, product_platform: str, top_n: int) -> List[Dict]:
        """Layer 2: Get recommendations by product category/platform"""

        # Map platform to LS_SKU categories
        platform_to_category = {
            'Compute': ['Compute', 'HCI', 'Converged Systems'],
            'Storage': ['Storage SW', 'Storage HW'],
            'Network': ['Switches'],
            'Infrastructure': ['Compute', 'Converged Systems'],
            'x86 Premium and Scale-up Rack': ['Compute'],
            'WLAN HW': ['Switches']
        }

        categories = platform_to_category.get(product_platform, [])

        if not categories:
            return []

        placeholders = ','.join('?' * len(categories))
        query = f"""
        SELECT
            s.service_name,
            s.service_type,
            s.service_text,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            lp.product_name as ls_sku_product,
            lp.product_category,
            'category_match' as recommendation_layer
        FROM dim_ls_sku_product lp
        JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
        JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE lp.product_category IN ({placeholders})
        GROUP BY s.ls_service_key
        ORDER BY s.priority ASC
        LIMIT ?
        """

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (*categories, top_n))

        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'service_name': row['service_name'],
                'service_type': row['service_type'],
                'service_text': row['service_text'],
                'priority': row['priority'],
                'sku_codes': row['sku_codes'] if row['sku_codes'] else 'Contact HPE',
                'ls_sku_product': row['ls_sku_product'],
                'product_category': row['product_category'],
                'match_confidence': None,
                'match_method': 'category',
                'recommendation_layer': row['recommendation_layer'],
                'confidence_score': 65
            })

        conn.close()
        return recommendations

    def _get_fallback_recommendations(self, top_n: int) -> List[Dict]:
        """Layer 3: Fallback to generic high-priority services"""
        query = """
        SELECT
            s.service_name,
            s.service_type,
            s.service_text,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            'fallback' as recommendation_layer
        FROM dim_ls_sku_service s
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE s.priority = 1  -- High priority services only
        AND s.service_type IN ('Installation & Startup', 'Health Check', 'Upgrade')
        GROUP BY s.ls_service_key
        ORDER BY s.priority ASC
        LIMIT ?
        """

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (top_n,))

        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'service_name': row['service_name'],
                'service_type': row['service_type'],
                'service_text': row['service_text'],
                'priority': row['priority'],
                'sku_codes': row['sku_codes'] if row['sku_codes'] else 'Contact HPE',
                'ls_sku_product': 'Generic',
                'product_category': 'General',
                'match_confidence': None,
                'match_method': 'fallback',
                'recommendation_layer': row['recommendation_layer'],
                'confidence_score': 50
            })

        conn.close()
        return recommendations

    def _adjust_for_urgency(
        self,
        recommendations: List[Dict],
        support_status: Optional[str],
        days_to_eol: Optional[int]
    ) -> List[Dict]:
        """Adjust recommendation priorities based on urgency"""

        is_expired = support_status and 'Expired' in support_status
        is_urgent = days_to_eol is not None and days_to_eol < 180

        for rec in recommendations:
            # Boost priority for urgent services
            if is_expired or is_urgent:
                if rec['service_type'] in ['Upgrade', 'Migration', 'Installation & Startup']:
                    rec['priority'] = max(1, rec['priority'] - 1)  # Boost priority
                    rec['urgency'] = 'Critical' if is_expired else 'High'
                else:
                    rec['urgency'] = 'Medium'
            else:
                rec['urgency'] = 'Normal'

        # Re-sort by adjusted priority
        recommendations.sort(key=lambda x: (x['priority'], -x['confidence_score']))

        return recommendations

    def get_expired_product_recommendations(self, customer_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get recommendations for expired products with urgency

        Args:
            customer_id: Optional customer ID filter

        Returns:
            DataFrame with expired product recommendations
        """
        query = """
        SELECT
            c.customer_name,
            c.customer_id_5digit,
            p.product_description,
            p.product_platform,
            ib.support_status,
            ib.days_to_eol,
            lp.product_name as ls_sku_product,
            s.service_name,
            s.service_type,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            CASE
                WHEN ib.days_to_eol < -365 THEN 'Critical'
                WHEN ib.days_to_eol < 0 THEN 'Urgent'
                WHEN ib.days_to_eol < 90 THEN 'High'
                ELSE 'Medium'
            END as urgency_level,
            m.confidence_score as match_quality
        FROM fact_install_base ib
        JOIN dim_customer c ON ib.customer_key = c.customer_key
        JOIN dim_product p ON ib.product_key = p.product_key
        LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
        LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
        LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
        LEFT JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE ib.days_to_eol < 180
          AND s.priority IN (1, 2)  -- High and medium priority services
          AND s.service_type IN ('Upgrade', 'Migration', 'Installation & Startup', 'Health Check')
        """

        if customer_id:
            query += f" AND c.customer_id_5digit = '{customer_id}'"

        query += """
        GROUP BY ib.install_key, s.ls_service_key
        ORDER BY urgency_level, s.priority, c.customer_name
        """

        conn = self._get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def get_cross_sell_opportunities(self, customer_id: str) -> List[Dict]:
        """
        Identify cross-sell opportunities based on customer's product mix

        Args:
            customer_id: Customer ID

        Returns:
            List of cross-sell recommendations
        """
        query = """
        SELECT
            p1.product_description as existing_product,
            p1.product_platform as existing_platform,
            lp1.product_name as existing_ls_sku,
            lp1.product_category as existing_category,
            lp2.product_name as cross_sell_product,
            lp2.product_category as cross_sell_category,
            s.service_name as bridge_service,
            s.service_type,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            'cross_sell' as recommendation_type
        FROM fact_install_base ib
        JOIN dim_customer c ON ib.customer_key = c.customer_key
        JOIN dim_product p1 ON ib.product_key = p1.product_key
        LEFT JOIN map_install_base_to_ls_sku m1 ON p1.product_key = m1.product_key
        LEFT JOIN dim_ls_sku_product lp1 ON m1.ls_product_key = lp1.ls_product_key
        -- Find complementary products in different categories
        CROSS JOIN dim_ls_sku_product lp2
        LEFT JOIN map_product_service_sku ps ON lp2.ls_product_key = ps.ls_product_key
        LEFT JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE c.customer_id_5digit = ?
          AND lp1.product_category != lp2.product_category
          AND s.service_type IN ('Integration', 'Configuration', 'Migration')
          AND s.service_name IS NOT NULL
        GROUP BY existing_ls_sku, cross_sell_product, s.ls_service_key
        ORDER BY s.priority ASC
        LIMIT 10
        """

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (customer_id,))

        opportunities = []
        for row in cursor.fetchall():
            opportunities.append({
                'existing_product': row['existing_product'],
                'existing_platform': row['existing_platform'],
                'existing_ls_sku': row['existing_ls_sku'],
                'cross_sell_product': row['cross_sell_product'],
                'cross_sell_category': row['cross_sell_category'],
                'bridge_service': row['bridge_service'],
                'service_type': row['service_type'],
                'priority': row['priority'],
                'sku_codes': row['sku_codes'] if row['sku_codes'] else 'Contact HPE',
                'recommendation_type': row['recommendation_type'],
                'rationale': f"Customer has {row['existing_ls_sku']}, can integrate with {row['cross_sell_product']}"
            })

        conn.close()
        return opportunities

    def get_credit_optimization_recommendations(self, min_unused_credits: int = 20) -> pd.DataFrame:
        """
        Get recommendations for utilizing unused service credits

        Args:
            min_unused_credits: Minimum unused credits threshold

        Returns:
            DataFrame with credit utilization recommendations
        """
        query = """
        SELECT
            c.customer_name,
            c.customer_id_5digit,
            sc.contract_id,
            sc.purchased_credits,
            sc.delivered_credits,
            sc.active_credits,
            sc.utilization_rate,
            sc.contract_end_date,
            CAST(JULIANDAY(sc.contract_end_date) - JULIANDAY('now') as INTEGER) as days_to_expiry,
            s.service_name,
            s.service_type,
            s.priority,
            k.service_credits as credits_required,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            CASE
                WHEN JULIANDAY(sc.contract_end_date) - JULIANDAY('now') < 30 THEN 'Urgent'
                WHEN JULIANDAY(sc.contract_end_date) - JULIANDAY('now') < 90 THEN 'High'
                ELSE 'Medium'
            END as urgency
        FROM fact_service_credit sc
        LEFT JOIN dim_customer c ON sc.customer_key = c.customer_key
        LEFT JOIN fact_install_base ib ON c.customer_key = ib.customer_key
        LEFT JOIN dim_product p ON ib.product_key = p.product_key
        LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
        LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
        LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
        LEFT JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE sc.active_credits >= ?
          AND k.service_credits IS NOT NULL
          AND k.service_credits <= sc.active_credits
        GROUP BY sc.credit_key, s.ls_service_key
        HAVING SUM(k.service_credits) <= sc.active_credits
        ORDER BY urgency, days_to_expiry ASC
        """

        conn = self._get_connection()
        df = pd.read_sql(query, conn, params=(min_unused_credits,))
        conn.close()
        return df

    def generate_quote_ready_export(
        self,
        customer_id: Optional[str] = None,
        urgency_filter: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generate quote-ready export with SKU codes

        Args:
            customer_id: Optional customer filter
            urgency_filter: Optional urgency levels (Critical, High, Medium, Low)

        Returns:
            DataFrame ready for quote generation
        """
        query = """
        SELECT
            c.customer_name,
            c.customer_id_5digit as account_st_id,
            p.product_description as current_product,
            p.product_platform,
            ib.support_status,
            ib.days_to_eol,
            lp.product_name as ls_sku_product,
            s.service_name,
            s.service_type,
            s.priority,
            s.service_text as service_description,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes,
            MAX(k.service_credits) as credits_required,
            m.confidence_score as match_confidence,
            CASE
                WHEN ib.days_to_eol < 0 THEN 'Critical'
                WHEN ib.days_to_eol BETWEEN 0 AND 90 THEN 'High'
                WHEN ib.days_to_eol BETWEEN 91 AND 180 THEN 'Medium'
                ELSE 'Low'
            END as urgency
        FROM dim_customer c
        JOIN fact_install_base ib ON c.customer_key = ib.customer_key
        JOIN dim_product p ON ib.product_key = p.product_key
        LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
        LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
        LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
        LEFT JOIN dim_ls_sku_service s ON ps.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        LEFT JOIN dim_sku_code k ON msk.sku_key = k.sku_key
        WHERE s.service_name IS NOT NULL
        """

        if customer_id:
            query += f" AND c.customer_id_5digit = '{customer_id}'"

        query += """
        GROUP BY c.customer_key, p.product_key, s.ls_service_key
        """

        if urgency_filter:
            query += " HAVING urgency IN ('" + "','".join(urgency_filter) + "')"

        query += " ORDER BY urgency DESC, s.priority, c.customer_name"

        conn = self._get_connection()
        df = pd.read_sql(query, conn)
        conn.close()

        # Add quote preparation fields
        df['quote_ready'] = df['sku_codes'].notna() & (df['sku_codes'] != '')
        df['action_required'] = df.apply(
            lambda x: 'Immediate' if x['urgency'] == 'Critical' else 'Standard',
            axis=1
        )

        return df

    def get_recommendation_summary(self, customer_id: str) -> Dict:
        """
        Get comprehensive recommendation summary for a customer

        Args:
            customer_id: Customer ID

        Returns:
            Summary dictionary with counts and priorities
        """
        # Get all recommendation types
        product_recs = self.get_expired_product_recommendations(customer_id)
        cross_sell = self.get_cross_sell_opportunities(customer_id)

        summary = {
            'customer_id': customer_id,
            'total_recommendations': len(product_recs) + len(cross_sell),
            'expired_product_recs': len(product_recs),
            'cross_sell_opportunities': len(cross_sell),
            'critical_actions': len(product_recs[product_recs['urgency_level'] == 'Critical']) if not product_recs.empty else 0,
            'services_with_sku': len(product_recs[product_recs['sku_codes'].notna()]) if not product_recs.empty else 0,
            'avg_match_quality': product_recs['match_quality'].mean() if not product_recs.empty else 0
        }

        return summary

    def close(self):
        """Close database connection (no-op for thread-safe connections)"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    db_path = "/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead.db"

    with EnhancedRecommendationEngine(db_path) as engine:
        print("\n" + "="*70)
        print("ENHANCED RECOMMENDATION ENGINE TEST")
        print("="*70)

        # Test 1: Product recommendations
        print("\n📦 Test 1: Get recommendations for DL360 Server")
        recs = engine.get_product_recommendations(
            product_name="DL360",
            product_platform="Compute",
            support_status="Expired Flex Support",
            days_to_eol=-500,
            top_n=5
        )

        if recs:
            for i, rec in enumerate(recs, 1):
                print(f"\n  {i}. {rec['service_name']}")
                print(f"     Type: {rec['service_type']} | Priority: {rec['priority']} | Layer: {rec['recommendation_layer']}")
                print(f"     SKU: {rec['sku_codes']}")
                print(f"     Confidence: {rec['confidence_score']}% | Urgency: {rec.get('urgency', 'N/A')}")
        else:
            print("  No recommendations found")

        # Test 2: Expired product recommendations
        print("\n\n🚨 Test 2: Expired Product Recommendations")
        expired_df = engine.get_expired_product_recommendations()

        if not expired_df.empty:
            print(f"  Found {len(expired_df)} expired product recommendations")
            print(f"\n  Sample (first 5):")
            print(expired_df[['customer_name', 'product_description', 'service_name',
                             'sku_codes', 'urgency_level']].head().to_string(index=False))
        else:
            print("  No expired products found")

        # Test 3: Quote-ready export
        print("\n\n📄 Test 3: Quote-Ready Export (Critical & High urgency)")
        quote_df = engine.generate_quote_ready_export(urgency_filter=['Critical', 'High'])

        if not quote_df.empty:
            print(f"  Found {len(quote_df)} quote-ready recommendations")
            quote_ready_count = quote_df['quote_ready'].sum()
            print(f"  Quote-ready (with SKUs): {quote_ready_count} ({quote_ready_count/len(quote_df)*100:.1f}%)")

            print(f"\n  Sample (first 5):")
            print(quote_df[['customer_name', 'current_product', 'service_name',
                           'sku_codes', 'urgency', 'quote_ready']].head().to_string(index=False))
        else:
            print("  No quote-ready recommendations found")

        print("\n" + "="*70)
        print("✅ Enhanced Recommendation Engine Test Complete")
        print("="*70)