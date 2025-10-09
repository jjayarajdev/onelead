## OneLead - Quick Start Guide

### Overview
OneLead is a sales intelligence system that identifies renewal opportunities, hardware refresh needs, and service gaps from your install base data.

### What We Built

**Data Loaded:**
- ✅ 63 install base records
- ✅ 98 opportunities
- ✅ 2,394 projects (historical)
- ✅ 286 services
- ✅ Service SKU mappings

**Leads Generated:**
- ✅ 30 renewal leads (expired support)
- ✅ 27 hardware refresh leads (EOL equipment)
- ✅ 20 service attach leads (coverage gaps)
- ✅ **77 total leads scored and prioritized**

---

### Quick Start

#### 1. Run the Dashboard (Enhanced Version)
```bash
streamlit run src/app/dashboard_v2.py
```

Or run the basic version:
```bash
streamlit run src/app/dashboard.py
```

The dashboard will open in your browser with these views:
- **Dashboard**: Overview metrics and top leads
- **Lead Queue**: Filterable list of all leads with scores
- **Account 360°**: Complete view of any account
- **Territory View**: Territory-based lead management
- **Analytics**: Performance metrics and insights

#### 2. Refresh Data (Optional)
To reload data from Excel files:
```bash
python load_data.py
```

#### 3. Regenerate Leads (Optional)
To regenerate leads after data changes:
```bash
python generate_leads.py
```

---

### How It Works

#### Lead Identification
The system automatically scans install base for:
1. **Expired Support** → Generates renewal leads
2. **EOL Equipment** (5+ years past end-of-life) → Hardware refresh leads
3. **Uncovered Assets** (no service agreement) → Service attach leads

#### Lead Scoring (0-100)
Each lead is scored based on:
- **Urgency (35%)**: How critical is the timing?
  - Days since EOL/support expiry
- **Value (30%)**: How valuable is the deal?
  - Estimated deal size + account install base size
- **Propensity (20%)**: How likely to close?
  - Open opportunities + historical projects
- **Strategic Fit (15%)**: How aligned with strategy?
  - Product family + business area

#### Priority Levels
- **CRITICAL**: Score ≥ 75
- **HIGH**: Score 60-74
- **MEDIUM**: Score 40-59
- **LOW**: Score < 40

---

### Key Features

#### Dashboard Page
- Total leads, high priority count, average score
- Lead distribution by type and priority (charts)
- Top 10 leads table

#### Lead Queue
- Filter by type, priority, minimum score
- Expandable lead cards with full details
- Score breakdown for each lead

#### Account 360° View
- Complete install base inventory
- All active leads for the account
- Open opportunities
- Historical project history

#### Territory View
- Territory-level metrics
- All leads by territory
- Pipeline value by territory

#### Analytics
- Lead score distribution histogram
- Territory leaderboard
- Product family distribution

---

### Understanding the Data

#### Install Base Risk Levels
- **CRITICAL**: 5+ years past EOL with expired support
- **HIGH**: Expired support or 3+ years past EOL
- **MEDIUM**: All other statuses

#### Sample High-Priority Leads
Look for leads with:
- HP DL360p Gen8 servers (Gen8 = 2012, very old!)
- "Warranty Expired - Uncovered Box" status
- No service agreement IDs

These are prime candidates for:
1. Hardware refresh to Gen11
2. Support contract renewal
3. Migration services

---

### Next Steps

1. **Review Top Leads**: Start with the Dashboard's "Top Priority Leads"
2. **Filter by Territory**: Use Territory View to focus on your accounts
3. **Dive into Accounts**: Use Account 360° for complete customer intelligence
4. **Export Data**: (Future) Add CSV export functionality
5. **Create Opportunities**: (Future) One-click opportunity creation in CRM

---

### Configuration

Edit `config/config.yaml` to customize:
- Scoring weights (urgency, value, propensity, strategic fit)
- Urgency thresholds (days past EOL, etc.)
- Lead type definitions
- Product family mappings
- Service bundle templates

---

### Troubleshooting

**Database is empty?**
Run: `python load_data.py`

**No leads showing?**
Run: `python generate_leads.py`

**Dashboard won't start?**
Check that Streamlit is installed: `pip install streamlit plotly`

**Want to start fresh?**
```bash
rm database/onelead.db
python load_data.py
python generate_leads.py
streamlit run src/app/dashboard.py
```

---

### Technical Details

**Architecture:**
```
data/ (Excel files)
  ↓
ETL Pipeline (loader.py)
  ↓
Database (SQLite)
  ↓
Business Logic Engines
  - LeadGenerator
  - ServiceRecommender
  - LeadScorer
  ↓
Streamlit Dashboard
```

**Tech Stack:**
- Python 3.11+
- SQLAlchemy (ORM)
- pandas (data processing)
- Streamlit (UI)
- Plotly (charts)

**Database Schema:**
- `accounts`: Customer accounts
- `install_base`: Hardware inventory
- `opportunities`: Sales pipeline
- `projects`: Historical A&PS projects
- `service_catalog`: Available services
- `service_sku_mappings`: Product→Service mappings
- `leads`: Generated leads (the gold!)

---

### Support

For questions or issues:
1. Check the main README.md
2. Review code comments in `src/` modules
3. Examine config in `config/config.yaml`

Happy selling! 🎯
