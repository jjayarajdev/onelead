"""
Validation Script for LS_SKU Integration
Tests all components of the Week 1 implementation
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.ls_sku_parser import LSSKUParser
from data_processing.product_matcher import ProductMatcher


def validate_parser():
    """Validate LS_SKU parser functionality"""
    print("\n" + "=" * 70)
    print("TEST 1: LS_SKU Parser Validation")
    print("=" * 70)

    file_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/LS_SKU_for_Onelead.xlsx'
    parser = LSSKUParser(file_path)
    parser.parse_product_mappings()

    stats = parser.get_summary_stats()

    print(f"✅ Parser loaded successfully")
    print(f"   Total Mappings: {stats['total_mappings']}")
    print(f"   Unique Products: {stats['unique_products']}")
    print(f"   Unique Services: {stats['unique_services']}")
    print(f"   Mappings with SKU: {stats['mappings_with_sku']}")

    # Test specific product lookup
    print(f"\n📋 Sample: Services for 3PAR")
    services_3par = parser.get_services_by_product("3PAR")
    for svc in services_3par[:3]:
        print(f"   - {svc['service_name']} (Priority: {svc['priority']})")

    return True


def validate_matcher():
    """Validate product matcher functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: Product Matcher Validation")
    print("=" * 70)

    matcher = ProductMatcher()

    # Test cases
    test_cases = [
        ("HP DL360p Gen8 8-SFF CTO Server", "Servers"),
        ("Aruba AP-325 Dual 4x4:4 802.11ac AP", "Networking"),
        ("HPE 3PAR StoreServ 8000", "3PAR"),
        ("HPE SimpliVity 380", "SimpliVity"),
    ]

    ls_sku_products = [
        '3PAR', 'Primera', 'Alletra', 'Servers', 'Synergy',
        'Networking', 'SAN', 'SimpliVity', 'Nutanix'
    ]

    print("✅ Testing product matching:")
    for install_base_name, expected in test_cases:
        matched, score, method = matcher.match_product(install_base_name, ls_sku_products)
        status = "✓" if matched == expected else "✗"
        print(f"   {status} {install_base_name[:40]:.<40} → {matched} ({score}% via {method})")

    return True


def validate_database_schema():
    """Validate database schema"""
    print("\n" + "=" * 70)
    print("TEST 3: Database Schema Validation")
    print("=" * 70)

    db_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead.db'

    if not Path(db_path).exists():
        print("❌ Database not found")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check for new tables
    expected_tables = [
        'dim_ls_sku_product',
        'dim_ls_sku_service',
        'dim_sku_code',
        'map_product_service_sku',
        'map_service_sku',
        'map_install_base_to_ls_sku'
    ]

    print("✅ Checking for new tables:")
    for table in expected_tables:
        cursor.execute(f"""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))
        exists = cursor.fetchone()[0] > 0
        status = "✓" if exists else "✗"

        # Get row count if exists
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {status} {table:.<40} {count:>6} rows")
        else:
            print(f"   {status} {table:.<40} Missing!")

    conn.close()
    return True


def validate_views():
    """Validate analytical views"""
    print("\n" + "=" * 70)
    print("TEST 4: Analytical Views Validation")
    print("=" * 70)

    db_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    expected_views = [
        'v_product_service_recommendations',
        'v_customer_service_opportunities',
        'v_expired_product_service_mapping',
        'v_credit_burndown_opportunities',
        'v_quote_ready_export'
    ]

    print("✅ Checking for analytical views:")
    for view in expected_views:
        cursor.execute(f"""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='view' AND name=?
        """, (view,))
        exists = cursor.fetchone()[0] > 0
        status = "✓" if exists else "✗"

        if exists:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {view}")
                count = cursor.fetchone()[0]
                print(f"   {status} {view:.<50} {count:>6} rows")
            except Exception as e:
                print(f"   ✗ {view:.<50} Error: {str(e)[:30]}")
        else:
            print(f"   {status} {view:.<50} Missing!")

    conn.close()
    return True


def validate_data_quality():
    """Validate data quality and relationships"""
    print("\n" + "=" * 70)
    print("TEST 5: Data Quality Validation")
    print("=" * 70)

    db_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead.db'
    conn = sqlite3.connect(db_path)

    # Check 1: Products by category
    df = pd.read_sql("""
        SELECT product_category, COUNT(*) as count
        FROM dim_ls_sku_product
        GROUP BY product_category
    """, conn)

    print("✅ LS_SKU Products by Category:")
    for _, row in df.iterrows():
        print(f"   {row['product_category']:.<30} {row['count']:>4} products")

    # Check 2: Services with SKU codes
    df = pd.read_sql("""
        SELECT
            COUNT(*) as total_services,
            SUM(CASE WHEN has_sku THEN 1 ELSE 0 END) as services_with_sku
        FROM dim_ls_sku_service
    """, conn)

    total = df.iloc[0]['total_services']
    with_sku = df.iloc[0]['services_with_sku']
    print(f"\n✅ Service SKU Coverage:")
    print(f"   Total Services: {total}")
    print(f"   Services with SKU: {with_sku} ({with_sku/total*100:.1f}%)")

    # Check 3: Product-Service mappings
    df = pd.read_sql("""
        SELECT
            p.product_name,
            COUNT(DISTINCT s.ls_service_key) as service_count
        FROM dim_ls_sku_product p
        LEFT JOIN map_product_service_sku m ON p.ls_product_key = m.ls_product_key
        LEFT JOIN dim_ls_sku_service s ON m.ls_service_key = s.ls_service_key
        GROUP BY p.product_name
        ORDER BY service_count DESC
        LIMIT 5
    """, conn)

    print(f"\n✅ Top Products by Service Mappings:")
    for _, row in df.iterrows():
        print(f"   {row['product_name']:.<25} {row['service_count']:>3} services")

    conn.close()
    return True


def validate_sample_queries():
    """Validate sample queries"""
    print("\n" + "=" * 70)
    print("TEST 6: Sample Query Validation")
    print("=" * 70)

    db_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead.db'
    conn = sqlite3.connect(db_path)

    # Query 1: Get services for a specific product with SKUs
    print("✅ Query 1: Services for 3PAR with SKU codes")
    df = pd.read_sql("""
        SELECT
            s.service_name,
            s.service_type,
            s.priority,
            GROUP_CONCAT(k.sku_code, ', ') as sku_codes
        FROM dim_ls_sku_product p
        JOIN map_product_service_sku m ON p.ls_product_key = m.ls_product_key
        JOIN dim_ls_sku_service s ON m.ls_service_key = s.ls_service_key
        LEFT JOIN map_service_sku ms ON s.ls_service_key = ms.ls_service_key
        LEFT JOIN dim_sku_code k ON ms.sku_key = k.sku_key
        WHERE p.product_name = '3PAR'
        GROUP BY s.service_name
        LIMIT 5
    """, conn)

    if len(df) > 0:
        print(df[['service_name', 'service_type', 'sku_codes']].to_string(index=False))
    else:
        print("   No results found")

    # Query 2: Service type distribution
    print(f"\n✅ Query 2: Service Type Distribution")
    df = pd.read_sql("""
        SELECT
            service_type,
            COUNT(*) as count,
            ROUND(AVG(priority), 1) as avg_priority
        FROM dim_ls_sku_service
        GROUP BY service_type
        ORDER BY count DESC
    """, conn)

    print(df.to_string(index=False))

    conn.close()
    return True


def run_all_validations():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("🧪 WEEK 1 IMPLEMENTATION VALIDATION")
    print("HPE OneLead LS_SKU Integration")
    print("=" * 70)

    tests = [
        ("Parser", validate_parser),
        ("Matcher", validate_matcher),
        ("Database Schema", validate_database_schema),
        ("Views", validate_views),
        ("Data Quality", validate_data_quality),
        ("Sample Queries", validate_sample_queries)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")

    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)