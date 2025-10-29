# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HPE OneLead Business Intelligence & Recommendation System - A SQLite-based Streamlit application with SKU-level service recommendations, quote-ready exports, credit optimization, and cross-sell intelligence.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the enhanced dashboard (production)
streamlit run src/main_enhanced.py
```

### Testing & Validation
```bash
# Run all validation tests (8 tests)
python src/test_enhanced_dashboard.py

# Validate Week 1 integration (6 tests)
python src/database/validate_integration.py

# Code formatting
black .

# Linting
flake8

# Type checking
mypy .
```

### Database Operations
```bash
# Create database schema
python src/database/create_sqlite_database.py

# Load LS_SKU data
python src/database/ls_sku_data_loader.py

# Query database
sqlite3 data/onelead.db
```

## Project Architecture

### Current Implementation (v2.0.0)

3-week implementation completed with SQLite backend and SKU-level recommendations:

**Week 1: Data Integration Foundation**
- LS_SKU Excel parser (124 product-service mappings)
- 3-tier product matcher (82.5% match rate, 85% confidence)
- Database schema (6 tables, 5 views)
- ETL pipeline with validation
- Result: 6/6 tests passed

**Week 2: Enhanced Recommendation Engine**
- 3-layer matching strategy (exact → category → fallback)
- SKU code integration
- Expired product recommendations
- Credit optimization logic
- Cross-sell intelligence
- Result: 6/6 tests passed

**Week 3: Dashboard Integration**
- 800-line production-ready Streamlit dashboard
- 5 interactive tabs with visual indicators
- Quote-ready CSV exports
- Credit burn-down widget
- Cross-sell opportunities widget
- Result: 8/8 tests passed

### Directory Structure
```
onelead_system/
├── src/
│   ├── main_enhanced.py                          # Production dashboard (800 lines)
│   ├── test_enhanced_dashboard.py                # Validation suite (8 tests)
│   ├── data_processing/
│   │   ├── enhanced_recommendation_engine.py     # Recommendation engine (650 lines)
│   │   ├── ls_sku_parser.py                      # LS_SKU Excel parser
│   │   ├── product_matcher.py                    # 3-tier product matcher
│   │   └── sqlite_loader.py                      # Data loader
│   └── database/
│       ├── create_sqlite_database.py             # Database schema
│       ├── ls_sku_data_loader.py                 # LS_SKU data loader
│       └── validate_integration.py               # Integration validator
├── data/
│   ├── onelead.db                                # SQLite database
│   ├── DataExportAug29th.xlsx                    # Install Base data
│   └── LS_SKU_for_Onelead.xlsx                   # Service catalog with SKUs
├── docs/
│   ├── WEEK1_COMPLETION_REPORT.md                # Week 1 report
│   ├── WEEK2_COMPLETION_REPORT.md                # Week 2 report
│   ├── WEEK3_COMPLETION_REPORT.md                # Week 3 report
│   ├── DATA_INTEGRATION_ANALYSIS.md              # Integration strategy
│   ├── DATABASE_MODEL.md                         # Database schema
│   ├── HOW_TO_USE_SQLITE.md                      # SQLite guide
│   └── SQLITE_DATABASE_SUMMARY.md                # Database overview
├── WEEK1_QUICK_REFERENCE.md                      # Week 1 quick ref
├── WEEK2_QUICK_REFERENCE.md                      # Week 2 quick ref
├── WEEK3_QUICK_REFERENCE.md                      # Week 3 quick ref
└── IMPLEMENTATION_COMPLETE.md                    # Complete summary
```

## Technology Stack

- **Framework**: Streamlit 1.x for web interface
- **Database**: SQLite 3 (local file-based)
- **Data Processing**: pandas, numpy
- **Visualization**: plotly for interactive charts
- **Text Matching**: fuzzywuzzy for product matching
- **Data I/O**: openpyxl for Excel files

## Core Components

### Database Schema

**Dimension Tables:**
- `dim_customer` - Customer master data
- `dim_product` - Product catalog
- `dim_service` - Service offerings
- `dim_ls_sku_product` - LS_SKU product catalog (22 products)
- `dim_ls_sku_service` - LS_SKU service catalog (53 services)
- `dim_sku_code` - SKU code master (9 codes)

**Mapping Tables:**
- `map_product_service_sku` - Product-to-service-to-SKU mappings (107 mappings)
- `map_service_sku` - Service-to-SKU mappings (14 mappings)
- `map_install_base_to_ls_sku` - Install Base to LS_SKU product matching

**Fact Tables:**
- `fact_install_base` - Customer product inventory
- `fact_opportunities` - Sales opportunities
- `fact_service_credits` - Service credit tracking

**Analytical Views:**
- `v_product_service_recommendations` - Pre-computed recommendations
- `v_customer_service_opportunities` - Customer-level opportunities
- `v_expired_product_service_mapping` - Expired product recommendations
- `v_credit_burndown_opportunities` - Unused credit tracking
- `v_quote_ready_export` - Quote-ready export view

### Key Algorithms

**3-Tier Product Matcher:**
1. Exact keyword match (100% confidence)
2. Alias match (85-95% confidence)
3. Fuzzy match (60-100% confidence)

**3-Layer Recommendation Strategy:**
1. Exact product match (80-95% confidence)
2. Category match (65% confidence)
3. Fallback recommendations (50% confidence)

**Urgency Calculation:**
- Critical: EOL/EOS or unsupported
- High: <180 days to EOL
- Medium: 180-365 days to EOL
- Low: >365 days to EOL

## Data Handling

- **Primary Data**: `data/onelead.db` (SQLite database, ~2MB)
- **Source Files**: Excel files in `data/` directory
- **Git Strategy**: Database and Excel files are git-ignored for security
- **Backup Strategy**: Manual backups recommended monthly

## Security Considerations

- Sensitive data files excluded from version control (.gitignore)
- Database file (`onelead.db`) not committed to git
- Excel files with customer data not committed
- Local-only processing, no external API calls

## Testing Strategy

**3 Validation Suites:**
1. **Week 1**: `src/database/validate_integration.py` (6 tests)
2. **Week 3**: `src/test_enhanced_dashboard.py` (8 tests)
3. **Overall**: 20/20 tests passed (100% success rate)

**Manual Testing:**
```bash
# Quick smoke test
streamlit run src/main_enhanced.py

# Verify recommendations
python -c "from src.data_processing.enhanced_recommendation_engine import EnhancedRecommendationEngine; engine = EnhancedRecommendationEngine('data/onelead.db'); print(len(engine.get_product_recommendations('DL360', 'Compute', 'Active', 365)))"
```

## Common Tasks

### Adding New Products
1. Update `data/LS_SKU_for_Onelead.xlsx`
2. Run `python src/database/ls_sku_data_loader.py`
3. Run `python src/database/validate_integration.py`

### Updating Dashboard
1. Edit `src/main_enhanced.py`
2. Test with `streamlit run src/main_enhanced.py`
3. Run validation `python src/test_enhanced_dashboard.py`

### Modifying Recommendation Logic
1. Edit `src/data_processing/enhanced_recommendation_engine.py`
2. Test individual methods
3. Run full test suite

## Performance Considerations

- **Caching**: `@st.cache_data` and `@st.cache_resource` for performance
- **Database**: Indexed tables for fast queries (15-100ms)
- **Views**: Pre-computed analytical views for complex queries
- **Dashboard**: Lazy loading for widgets with empty data

## Documentation

- **Quick Start**: README.md
- **Weekly Guides**: WEEK1_QUICK_REFERENCE.md, WEEK2_QUICK_REFERENCE.md, WEEK3_QUICK_REFERENCE.md
- **Detailed Reports**: docs/WEEK*_COMPLETION_REPORT.md
- **Technical Docs**: docs/DATABASE_MODEL.md, docs/HOW_TO_USE_SQLITE.md
- **Complete Summary**: IMPLEMENTATION_COMPLETE.md