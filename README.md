# OneLead - Lead Generation & Sales Intelligence System

A comprehensive system for identifying renewal opportunities, service upsells, and cross-sell opportunities based on install base analysis, active opportunities, and service catalog mapping.

## ✨ NEW: Premium Intelligence Dashboard

We've launched a **world-class Premium Dashboard** that combines:
- 🎨 Professional design (inspired by Tableau, Looker, Stripe)
- 📊 Business storytelling with actionable insights
- 🚀 Executive-ready presentation quality
- ⚡ Real-time filtering and analytics

**[See LAUNCH_PREMIUM.md for details →](LAUNCH_PREMIUM.md)**

## Features

- **Install Base Analysis**: Track hardware inventory, warranty status, and EOL/EOS dates
- **Lead Identification**: Automatically detect renewal, upsell, and cross-sell opportunities
- **Service Recommendations**: Match products with relevant service SKUs
- **Lead Scoring**: Prioritize opportunities based on urgency, value, and propensity
- **Territory Management**: Account 360° views and territory analytics
- **Multiple Dashboard Options**: Choose from Premium, Business Story, Enhanced, or Basic views

## Quick Start

### Option 1: Use the Launcher (Recommended) ⭐
```bash
./run_dashboard.sh
```
Select from 4 dashboard versions:
1. **Premium Intelligence** (NEW - Recommended for executives)
2. **Business Story** (Narrative-driven for sales teams)
3. **Enhanced Data** (Analytics for power users)
4. **Basic** (Simple tables and charts)

### Option 2: Direct Launch
```bash
# Premium Dashboard (Recommended)
streamlit run src/app/dashboard_premium.py

# Or Business Story Dashboard
streamlit run src/app/dashboard_business.py

# Or Enhanced Dashboard
streamlit run src/app/dashboard_v2.py

# Or Basic Dashboard
streamlit run src/app/dashboard.py
```

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Load data from Excel files
python load_data.py

# 3. Generate and score leads
python generate_leads.py

# 4. Launch dashboard
./run_dashboard.sh
```

## Project Structure

```
onelead/
├── data/               # Excel source files
├── src/
│   ├── etl/           # Data extraction and loading
│   ├── models/        # Database models
│   ├── engines/       # Business logic (lead gen, scoring)
│   ├── app/           # Streamlit dashboard
│   └── utils/         # Helper functions
├── config/            # Configuration files
└── database/          # SQLite database storage
```

## Data Sources

- **Install Base**: Hardware inventory with warranty/support status
- **Opportunities**: Active sales pipeline
- **Projects**: Historical A&PS project data
- **Services**: Available service catalog with SKUs
- **Service SKU Mapping**: Product-to-service mapping matrix

## Lead Types

1. **Renewal Leads**: Expired/expiring support contracts
2. **Hardware Refresh**: EOL/aging equipment requiring upgrades
3. **Service Attach**: Install base without corresponding services
4. **Cross-sell**: Single product line customers needing complementary solutions

## Scoring Algorithm

Leads scored 0-100 based on:
- **Urgency (35%)**: Days since expiry, EOL proximity
- **Value (30%)**: Install base size, historical spend
- **Propensity (20%)**: Open opportunities, engagement
- **Strategic Fit (15%)**: Product alignment, industry

## Documentation

Comprehensive documentation is available:
- **[LAUNCH_PREMIUM.md](LAUNCH_PREMIUM.md)** - Premium Dashboard launch guide
- **[PREMIUM_DASHBOARD.md](PREMIUM_DASHBOARD.md)** - Complete design philosophy and technical details
- **[BUSINESS_DASHBOARD.md](BUSINESS_DASHBOARD.md)** - Business storytelling approach
- **[QUICKSTART.md](QUICKSTART.md)** - Getting started guide
- **[DATA_MAPPING.md](DATA_MAPPING.md)** - Excel to Database mapping (17,000+ words)
- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Architecture and trade-offs

## Dashboard Comparison

| Dashboard | Best For | Visual Design | Business Story | Data Depth |
|-----------|----------|---------------|----------------|------------|
| **Premium** ⭐ | Executives, Presentations | ★★★★★ | ★★★★★ | ★★★★★ |
| **Business Story** | Sales Teams, Daily Use | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| **Enhanced** | Analysts, Power Users | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| **Basic** | Quick Access, Testing | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ |

## Current Data Stats

- ✅ 63 install base records analyzed
- ✅ 98 active opportunities tracked
- ✅ 2,394 historical projects loaded
- ✅ 286 services cataloged
- ✅ **77 scored leads generated** (30 renewal + 27 hardware refresh + 20 service attach)
- ✅ **$1.15M+ pipeline identified**

## License

Proprietary - HPE Internal Use Only
