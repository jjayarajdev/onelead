# Week 1 Quick Reference Guide

## 🎯 What Was Accomplished

Week 1 implemented the **foundational data integration layer** that enables SKU-level service recommendations by integrating LS_SKU product-service mappings with existing Install Base data.

## 📊 Key Numbers

- **124** product-service mappings extracted
- **22** LS_SKU products cataloged
- **53** services with metadata
- **9** SKU codes registered
- **82.5%** Install Base product match rate
- **100%** validation test pass rate

## 🗂️ New Files Created

### Core Modules
```
src/data_processing/
├── ls_sku_parser.py          # Parses LS_SKU Excel file
└── product_matcher.py         # Matches Install Base to LS_SKU products

src/database/
├── schema_enhancements.sql    # 6 new tables + 5 views
├── ls_sku_data_loader.py      # ETL pipeline
└── validate_integration.py    # Test suite
```

### Documentation
```
docs/
├── DATA_INTEGRATION_ANALYSIS.md    # Integration strategy
└── WEEK1_COMPLETION_REPORT.md      # Detailed completion report
```

## 🚀 Quick Start Commands

### Load LS_SKU Data
```bash
# Load all LS_SKU data into database
python src/database/ls_sku_data_loader.py
```

### Run Validation Tests
```bash
# Run comprehensive validation (6 tests)
python src/database/validate_integration.py
```

### Test Individual Components
```bash
# Test parser
python src/data_processing/ls_sku_parser.py

# Test matcher
python src/data_processing/product_matcher.py
```

## 💾 Database Changes

### New Tables (6)
1. `dim_ls_sku_product` - LS_SKU products (22 rows)
2. `dim_ls_sku_service` - Services catalog (53 rows)
3. `dim_sku_code` - SKU codes (9 rows)
4. `map_product_service_sku` - Product-service mappings (107 rows)
5. `map_service_sku` - Service-SKU mappings (14 rows)
6. `map_install_base_to_ls_sku` - Install Base matches (52 rows)

### New Views (5)
1. `v_product_service_recommendations` - Product recommendations
2. `v_customer_service_opportunities` - Customer analysis
3. `v_expired_product_service_mapping` - Urgent actions
4. `v_credit_burndown_opportunities` - Credit optimization
5. `v_quote_ready_export` - Quote generation

## 🔍 Sample Queries

### Get Services for a Product
```sql
SELECT
    s.service_name,
    s.service_type,
    GROUP_CONCAT(k.sku_code, ', ') as sku_codes
FROM dim_ls_sku_product p
JOIN map_product_service_sku m ON p.ls_product_key = m.ls_product_key
JOIN dim_ls_sku_service s ON m.ls_service_key = s.ls_service_key
LEFT JOIN map_service_sku ms ON s.ls_service_key = ms.ls_service_key
LEFT JOIN dim_sku_code k ON ms.sku_key = k.sku_key
WHERE p.product_name = '3PAR'
GROUP BY s.service_name;
```

### Get Quote-Ready Data
```sql
SELECT * FROM v_quote_ready_export
WHERE urgency IN ('Critical', 'High')
LIMIT 10;
```

### Check Match Quality
```sql
SELECT
    confidence_level,
    COUNT(*) as count
FROM map_install_base_to_ls_sku
GROUP BY confidence_level;
```

## 🐍 Python Usage Examples

### Parse LS_SKU File
```python
from src.data_processing.ls_sku_parser import LSSKUParser

parser = LSSKUParser('data/LS_SKU_for_Onelead.xlsx')
parser.parse_product_mappings()

# Get services for a product
services = parser.get_services_by_product('SimpliVity')
for svc in services:
    print(f"{svc['service_name']} - Priority {svc['priority']}")
```

### Match Products
```python
from src.data_processing.product_matcher import ProductMatcher

matcher = ProductMatcher()
ls_sku_products = ['3PAR', 'Primera', 'Servers', 'SimpliVity']

matched, confidence, method = matcher.match_product(
    "HP DL360p Gen8 Server",
    ls_sku_products
)
print(f"Matched: {matched} ({confidence}% via {method})")
```

### Query Database
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/onelead.db')

df = pd.read_sql("""
    SELECT * FROM v_product_service_recommendations
    WHERE match_confidence >= 80
    LIMIT 10
""", conn)

print(df)
```

## 📈 Data Quality Stats

### Products by Category
- Storage SW: 8 products, 35 services
- HCI: 4 products, 26 services
- Compute: 3 products, 14 services
- Converged Systems: 3 products, 18 services
- Switches: 2 products, 8 services

### Service Types
- Installation & Startup: 9 services (avg priority 1.4)
- Upgrade: 7 services (avg priority 2.0)
- Configuration: 8 services (avg priority 2.3)
- Health Check: 2 services (avg priority 1.0)

### SKU Coverage
- Total Services: 53
- Services with SKU: 7 (13.2%)
- Total SKU Codes: 9 unique

## ✅ Validation Checklist

Run this checklist to verify Week 1 implementation:

```bash
# 1. Database exists
ls -lh data/onelead.db

# 2. Validation tests pass
python src/database/validate_integration.py
# Expected: 6/6 tests passed (100%)

# 3. Tables populated
sqlite3 data/onelead.db "
SELECT
    (SELECT COUNT(*) FROM dim_ls_sku_product) as products,
    (SELECT COUNT(*) FROM dim_ls_sku_service) as services,
    (SELECT COUNT(*) FROM map_product_service_sku) as mappings;
"
# Expected: products=22, services=53, mappings=107
```

## 🔮 Week 2 Preview

Week 2 will use this foundation to:

1. **Enhance Recommendation Engine** (`src/data_processing/service_opportunity_mapper.py`)
   - Replace generic product line mapping with SKU-level precision
   - Add confidence scoring based on match quality

2. **Update Dashboard** (`src/main_business.py`)
   - Add "SKU Code" column to Service Recommendations tab
   - Create "Credit Optimization" widget
   - Add "Quote Ready Export" functionality

3. **Integrate ML Model** (`src/models/opportunity_predictor.py`)
   - Add historical pattern features from A&PS projects
   - Retrain model with LS_SKU service data

## 📞 Need Help?

### Check Logs
```bash
# Data loader logs show detailed progress
python src/database/ls_sku_data_loader.py 2>&1 | tee load.log
```

### Inspect Database
```bash
# View schema
sqlite3 data/onelead.db ".schema dim_ls_sku_product"

# View sample data
sqlite3 data/onelead.db "SELECT * FROM dim_ls_sku_product LIMIT 5;"

# Check table counts
sqlite3 data/onelead.db "
SELECT name, (SELECT COUNT(*) FROM ' || name || ') as count
FROM sqlite_master
WHERE type='table' AND name LIKE 'dim_ls_sku%';
"
```

### Troubleshooting

**Issue**: Validation fails
- **Solution**: Rerun data loader to populate tables

**Issue**: Low match rate for Install Base
- **Solution**: Add product aliases in `product_matcher.py`

**Issue**: Missing SKU codes
- **Solution**: Expected - many services don't have explicit SKUs in source data

## 📚 Key Documentation

- `docs/DATA_INTEGRATION_ANALYSIS.md` - Full integration strategy
- `docs/WEEK1_COMPLETION_REPORT.md` - Detailed completion report
- `src/data_processing/ls_sku_parser.py` - Parser implementation docs
- `src/data_processing/product_matcher.py` - Matcher algorithm docs
- `src/database/schema_enhancements.sql` - Database schema reference

---

**Week 1 Status**: ✅ COMPLETE
**Next Step**: Week 2 - Enhanced Recommendation Engine