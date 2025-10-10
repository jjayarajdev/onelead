# Project Cleanup Plan

## Files to KEEP (Production Essentials)

### Core Application
- ✅ **app.py** - Streamlit Cloud entry point
- ✅ **requirements.txt** - Dependencies
- ✅ **README.md** - Main documentation
- ✅ **run_dashboard.sh** - Dashboard launcher

### Data & Config
- ✅ **config/config.yaml** - Application configuration
- ✅ **data/DataExportAug29th.xlsx** - Source data
- ✅ **data/LS_SKU_for_Onelead.xlsx** - Service catalog
- ✅ **database/onelead.db** - SQLite database

### Source Code (src/)
- ✅ **src/app/dashboard_premium.py** - Premium Dashboard (ONLY ONE)
- ✅ **src/models/*.py** - Database models (all)
- ✅ **src/engines/*.py** - Lead generation (all)
- ✅ **src/etl/*.py** - Data loading (all)
- ✅ **src/utils/*.py** - Utilities (all)

### Scripts
- ✅ **generate_leads.py** - Lead generation
- ✅ **load_data.py** - Data loading

### Key Documentation
- ✅ **LAUNCH_PREMIUM.md** - Launch guide
- ✅ **QUICK_REFERENCE.md** - Quick reference
- ✅ **DEPLOYMENT.md** - Deployment guide
- ✅ **QUICKSTART.md** - Getting started

### Hidden Config
- ✅ **.streamlit/config.toml** - Streamlit configuration
- ✅ **.gitignore** - Git ignore rules

---

## Files to ARCHIVE

### Old Dashboards (4 files) → archives/old_dashboards/
- ❌ src/app/dashboard.py
- ❌ src/app/dashboard_v2.py
- ❌ src/app/dashboard_business.py
- ❌ src/app/dashboard_modern.py
**Reason:** Only dashboard_premium.py is used in production

### Old Main Files (3 files) → archives/old_code/
- ❌ src/main_simple.py
- ❌ src/main_enhanced.py
- ❌ src/main_clean.py
**Reason:** Replaced by app.py

### Old Data Processing (4 files) → archives/old_code/
- ❌ src/data_processing/enhanced_recommendation_engine.py
- ❌ src/data_processing/ls_sku_parser.py
- ❌ src/data_processing/product_matcher.py
- ❌ src/data_processing/sqlite_loader.py
**Reason:** Replaced by src/engines/ and src/etl/

### Database Setup Scripts (4 files) → archives/old_code/
- ❌ src/database/create_sqlite_database.py
- ❌ src/database/ls_sku_data_loader.py
- ❌ src/database/schema_enhancements.sql
- ❌ src/database/validate_integration.py
**Reason:** Database already created, scripts not needed for production

### Analysis Scripts (4 files) → archives/analysis_scripts/
- ❌ analyze_excel_data.py
- ❌ eda_analysis.py
- ❌ run_analysis.py
- ❌ create_visualizations.py
- ❌ data/create_er_diagram.py
**Reason:** One-time analysis, not needed for production

### Visualization Files (9 files) → archives/visualizations/
- ❌ visualizations/*.png
- ❌ visualizations/*.html
- ❌ visualizations/EDA_SUMMARY_REPORT.md
**Reason:** Historical visualizations, not used in dashboard

### Documentation Archive (16 files) → archives/old_docs/
- ❌ docs/CLIENT_PRESENTATION.md
- ❌ docs/DATA_INTEGRATION_ANALYSIS.md
- ❌ docs/DATABASE_MODEL.md
- ❌ docs/DataExportAug29th_Analysis.md
- ❌ docs/ER_DIAGRAM_EXCEL.md
- ❌ docs/HOW_TO_USE_SQLITE.md
- ❌ docs/INTEGRATED_DATABASE_ANALYSIS.md
- ❌ docs/LS_SKU_Analysis.md
- ❌ docs/README.md
- ❌ docs/SQLITE_DATABASE_SUMMARY.md
- ❌ data/ER_Diagram.md
- ❌ tests/test_framework.md
- ❌ WEEK1_QUICK_REFERENCE.md
- ❌ WEEK2_QUICK_REFERENCE.md
- ❌ WEEK3_QUICK_REFERENCE.md
- ❌ CLAUDE.md
**Reason:** Historical documentation, superseded by current docs

### Design Documentation Archive (5 files) → archives/old_docs/
- ❌ BUSINESS_DASHBOARD.md (content preserved in PREMIUM_DASHBOARD.md)
- ❌ DATA_MAPPING.md (historical reference)
- ❌ DESIGN_DECISIONS.md (historical reference)
- ❌ UI_IMPROVEMENTS.md (historical reference)
- ❌ IMPLEMENTATION_COMPLETE.md (historical reference)
- ❌ FIXES.md (historical reference)
- ❌ WHATS_NEW.md (content in README)
**Reason:** Historical design docs, info incorporated into current docs

### Deployment Configs (3 files) → archives/deployment_configs/
- ❌ deployment/docker/Dockerfile
- ❌ deployment/docker/docker-compose.yml
- ❌ deployment/kubernetes/deployment.yaml
**Reason:** Using Streamlit Cloud, not Docker/K8s

### Extra Data File (1 file) → archives/
- ❌ data/onelead_consolidated_data_new.xlsx
**Reason:** Consolidated file not used, source Excel files are sufficient

---

## Summary

### Before Cleanup
- **Total Files:** ~100 files
- **Cluttered:** Multiple dashboards, old scripts, historical docs

### After Cleanup
- **Production Files:** ~35 files
- **Archived Files:** ~65 files
- **Clean:** Single dashboard, essential code, current docs

### Benefits
- ✅ Easier to navigate
- ✅ Faster deployments
- ✅ Clear what's in production vs. historical
- ✅ Reduced repository size
- ✅ Better maintainability

---

## Execution Plan

1. Create archive folders structure
2. Move files to appropriate archive folders
3. Update .gitignore if needed
4. Delete empty folders
5. Commit changes
6. Push to GitHub

**Estimated cleanup:** 65 files moved to archives
