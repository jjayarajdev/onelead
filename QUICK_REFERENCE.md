# OneLead Quick Reference Card

## 🚀 Launch Commands

```bash
# Easiest way - Interactive launcher
./run_dashboard.sh

# Or launch specific dashboard directly:
streamlit run src/app/dashboard_premium.py    # Premium (Recommended)
streamlit run src/app/dashboard_business.py   # Business Story
streamlit run src/app/dashboard_v2.py         # Enhanced
streamlit run src/app/dashboard.py            # Basic
```

---

## 📊 Dashboard Versions at a Glance

| Version | Command | Best For | Key Feature |
|---------|---------|----------|-------------|
| **Premium** ⭐ | `dashboard_premium.py` | Executives, Presentations | World-class design |
| Business | `dashboard_business.py` | Sales Teams | Narrative storytelling |
| Enhanced | `dashboard_v2.py` | Analysts | Advanced filters |
| Basic | `dashboard.py` | Quick access | Simple tables |

---

## 🔄 Data Management

```bash
# Reload data from Excel files
python load_data.py

# Regenerate and rescore all leads
python generate_leads.py

# Full refresh (nuclear option)
rm database/onelead.db
python load_data.py
python generate_leads.py
```

---

## 📁 File Locations

```
Data Files:          data/*.xlsx
Database:            database/onelead.db
Config:              config/config.yaml
Dashboards:          src/app/dashboard_*.py
Documentation:       *.md (root directory)
```

---

## 🎯 Priority Levels

| Priority | Score Range | Color | Action Required |
|----------|-------------|-------|-----------------|
| CRITICAL | 75-100 | 🔴 Red | Immediate (Today) |
| HIGH | 60-74 | 🟠 Orange | This Week |
| MEDIUM | 40-59 | 🔵 Blue | This Month |
| LOW | 0-39 | ⚪ Gray | Backlog |

---

## 💰 Lead Types

| Type | Icon | Description | Avg Deal Size |
|------|------|-------------|---------------|
| Renewal | 🔄 | Expired/expiring support | $25-75K |
| Hardware Refresh | 🔧 | EOL equipment (5+ years) | $50-300K |
| Service Attach | 📦 | Uncovered equipment | $15-95K |

---

## 📈 Lead Scoring Formula

```
Total Score (0-100) =
  Urgency (35%)       +
  Value (30%)         +
  Propensity (20%)    +
  Strategic Fit (15%)
```

**Urgency:** Days since EOL/expiry
**Value:** Deal size + install base size
**Propensity:** Open opportunities + historical projects
**Strategic Fit:** Product family + business alignment

---

## 🎨 Premium Dashboard Sections

1. **Hero Header** - Context and metadata
2. **Metrics (5 cards)** - Pipeline, leads, score, risk, win rate
3. **Insights (3 cards)** - Critical, opportunity, strategic
4. **Lead Priorities** - Top 10 with filters
5. **Analytics** - Priority pipeline, type distribution, score histogram

---

## 🔍 Filtering Options

**By Priority:**
- All, CRITICAL, HIGH, MEDIUM, LOW

**By Type:**
- All, renewal, hardware_refresh, service_attach

**By Score:**
- Minimum score threshold (0-100)

**Sort By:**
- Score (High to Low)
- Value (High to Low)
- Priority Level

---

## 🎯 Action Buttons (Premium)

| Button | Purpose | Status |
|--------|---------|--------|
| 📞 Contact Customer | Call with script | Simulated |
| 📋 View Full Details | Account 360° view | Simulated |
| ✅ Mark as Qualified | Update lead status | Simulated |
| 📧 Generate Email | Automated outreach | Simulated |
| 📊 Build Business Case | TCO analysis | Simulated |

_Note: Buttons are UI placeholders in v2.0. Will be functional in v2.1._

---

## 📚 Documentation Map

| File | Purpose | Length |
|------|---------|--------|
| README.md | Main overview | 2 pages |
| LAUNCH_PREMIUM.md | Premium dashboard guide | 10 pages |
| PREMIUM_DASHBOARD.md | Design philosophy | 40 pages |
| BUSINESS_DASHBOARD.md | Storytelling approach | 15 pages |
| QUICKSTART.md | Getting started | 5 pages |
| DATA_MAPPING.md | Excel → DB mapping | 50 pages |
| DESIGN_DECISIONS.md | Architecture | 20 pages |
| WHATS_NEW.md | Release notes | 12 pages |
| QUICK_REFERENCE.md | This file | 4 pages |

---

## ⚙️ Configuration (config/config.yaml)

```yaml
# Adjust scoring weights
scoring_weights:
  urgency: 0.35
  value: 0.30
  propensity: 0.20
  strategic_fit: 0.15

# Adjust priority thresholds
priority_thresholds:
  critical: 75
  high: 60
  medium: 40
  low: 0

# Add territory mappings
territory_mapping:
  "56088": "Apple Inc"
  "56180": "APPLIED MATERIALS, INC."
```

---

## 🐛 Troubleshooting

**Dashboard won't start:**
```bash
pip install streamlit plotly
streamlit run src/app/dashboard_premium.py
```

**No data showing:**
```bash
python load_data.py
python generate_leads.py
```

**Database errors:**
```bash
rm database/onelead.db
python load_data.py
python generate_leads.py
```

**Styling looks broken:**
- Clear browser cache
- Use Chrome/Firefox/Safari (not IE)
- Check internet connection (Google Fonts)

**Port 8501 already in use:**
```bash
streamlit run src/app/dashboard_premium.py --server.port 8502
```

---

## 📊 Current Data Stats

- 63 install base records
- 98 active opportunities
- 2,394 historical projects
- 286 services cataloged
- **77 scored leads** (30 renewal + 27 hardware refresh + 20 service attach)
- **$1.15M+ pipeline identified**

---

## 🔐 Database Schema Quick Reference

**Main Tables:**
- `accounts` - Customer accounts
- `install_base` - Hardware inventory
- `opportunities` - Sales pipeline
- `projects` - Historical projects
- `service_catalog` - Available services
- `service_sku_mappings` - Product→Service mappings
- `leads` - Generated leads (the gold!)

**Key Relationships:**
```
leads → accounts (account_id)
leads → install_base (install_base_id)
install_base → accounts (account_id)
opportunities → accounts (account_id)
projects → accounts (account_id)
```

---

## 🎨 Color Palette (Premium)

**Primary:**
- Dark Blue: `#1e3a8a`
- Blue: `#3b82f6`
- Light Blue: `#06b6d4`

**Semantic:**
- Critical/Red: `#dc2626`
- Success/Green: `#059669`
- Warning/Orange: `#f59e0b`

**Neutrals:**
- Text Dark: `#0f172a`
- Text Medium: `#475569`
- Text Light: `#64748b`
- Border: `#e2e8f0`
- Background: `#f8fafc`

---

## 🎯 Keyboard Shortcuts (Streamlit)

| Key | Action |
|-----|--------|
| `R` | Rerun dashboard |
| `C` | Clear cache |
| `?` | Show keyboard shortcuts |
| `Ctrl/Cmd + /` | Focus search |
| `Ctrl/Cmd + K` | Command palette |

---

## 📱 Browser Requirements

**Supported:**
- ✅ Chrome 90+ (Recommended)
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Not Supported:**
- ❌ Internet Explorer (any version)
- ❌ Chrome < 90
- ❌ Mobile browsers (responsive but not optimized)

---

## 🚀 Performance Tips

1. **Use caching** - Don't modify `@st.cache_data` decorators
2. **Close unused tabs** - Each tab runs full app
3. **Clear cache periodically** - Press `C` in dashboard
4. **Use Chrome** - Best Streamlit performance
5. **Local database** - SQLite is fast for <100K records

---

## 📞 Support

**For Issues:**
- Check documentation first
- Review error messages carefully
- Try data refresh: `python load_data.py`

**For Feature Requests:**
- Document your use case
- Explain expected behavior
- Provide examples if possible

---

## 🎓 Learning Resources

**Understanding the System:**
1. Start with README.md (5 min read)
2. Try QUICKSTART.md (10 min tutorial)
3. Explore LAUNCH_PREMIUM.md (20 min deep dive)

**For Technical Details:**
1. DATA_MAPPING.md - How data flows
2. DESIGN_DECISIONS.md - Why we built it this way
3. PREMIUM_DASHBOARD.md - Design deep dive

**For Business Context:**
1. BUSINESS_DASHBOARD.md - Storytelling approach
2. WHATS_NEW.md - Latest features
3. Config files - Customization options

---

## 💡 Pro Tips

**Sales Reps:**
- Open Premium Dashboard every Monday morning
- Focus on top 5 leads, ignore the rest
- Use "Sort by Priority" for daily queue
- Take notes in CRM as you call

**Sales Managers:**
- Use Premium Dashboard in team meetings
- Screenshot insights for weekly reports
- Filter by territory to assign leads
- Track team progress on critical situations

**Executives:**
- Review metrics weekly
- Screenshot hero + metrics for QBRs
- Focus on insight cards for strategy
- Use analytics to identify trends

**Analysts:**
- Use Enhanced Dashboard for deep dives
- Export data for custom analysis
- Adjust scoring in config.yaml
- Monitor score distribution histogram

---

## ✅ Daily Workflow

**Morning Routine (5 minutes):**
1. Open Premium Dashboard
2. Check metrics - any surprises?
3. Read critical insight card
4. Review top 3-5 priorities
5. Plan your day

**End of Day (2 minutes):**
1. Update lead statuses in CRM
2. Note any completed actions
3. Preview tomorrow's priorities

**Weekly Review (15 minutes):**
1. Review all metrics - trends?
2. Check analytics - any patterns?
3. Filter by territory - team alignment
4. Plan next week's focus

---

**Last Updated:** October 9, 2025
**Version:** 2.0
**Print this for quick reference!** 📄
