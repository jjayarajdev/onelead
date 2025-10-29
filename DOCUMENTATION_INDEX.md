# OneLead - Documentation Index

**Last Updated:** October 29, 2025
**Status:** ✅ Current and Organized

---

## 📚 Active Documentation (8 files)

### Getting Started

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **[README.md](README.md)** | 4.8KB | Project overview, features, quick start | Everyone |
| **[QUICKSTART.md](QUICKSTART.md)** | 5.0KB | Step-by-step setup guide | New users |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | 8.6KB | Command reference card | Daily users |

### Application & Deployment

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **[LAUNCH_PREMIUM.md](LAUNCH_PREMIUM.md)** | 9.1KB | Premium Dashboard launch guide | Users, Sales teams |
| **[PREMIUM_DASHBOARD.md](PREMIUM_DASHBOARD.md)** | 25KB | Design philosophy, features, technical details | Developers, Designers |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | 7.9KB | Streamlit Cloud deployment guide | DevOps, Admins |

### Technical Reference

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **[DATA_RELATIONSHIPS_ANALYSIS.md](DATA_RELATIONSHIPS_ANALYSIS.md)** | 49KB | **NEW!** Complete data relationships & integration analysis | Developers, Data Analysts, Business Analysts |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | 6.9KB | File organization, production vs. archived files | Developers |

**Total Active Documentation:** 116KB across 8 files

---

## 📖 What Each Document Covers

### 1. README.md
**Purpose:** First stop for anyone discovering the project
- Project features and capabilities
- Quick start options (launcher, direct launch)
- Data sources overview
- Lead types and scoring
- Current statistics (77 leads, $1.15M pipeline)

### 2. QUICKSTART.md
**Purpose:** Get up and running in 5 minutes
- First-time setup instructions
- Data loading steps
- Dashboard launch options
- Troubleshooting basics

### 3. LAUNCH_PREMIUM.md
**Purpose:** Premium Dashboard user guide
- Feature walkthrough
- How to use filters and controls
- Understanding lead cards
- Scoring breakdown explanation
- Tips for sales teams

### 4. PREMIUM_DASHBOARD.md (25KB)
**Purpose:** Complete design and technical documentation
- Design philosophy inspired by Tableau, Looker, Stripe
- Color psychology and visual hierarchy
- Component architecture
- Business storytelling approach
- 40+ pages of detailed documentation

### 5. DATA_RELATIONSHIPS_ANALYSIS.md (49KB) ⭐ NEW
**Purpose:** Comprehensive data integration guide
- **Excel file structure analysis**
  - DataExportAug29th.xlsx (5 sheets analyzed)
  - LS_SKU_for_Onelead.xlsx (product-service mapping)
- **Complete relationship map**
  - Install Base ↔ Opportunity (Direct FK)
  - Opportunity → A&PS Project (Direct FK via PRJ Siebel ID)
  - A&PS Project → Services (Practice mapping)
  - Install Base → LS_SKU → Recommendations (Keyword matching)
- **Practical use cases & workflows**
  - Proactive warranty renewal campaigns
  - EOL/EOSL refresh campaigns
  - Cross-sell & service attach strategies
- **Technical implementation**
  - Database schema and queries
  - Mapping logic and algorithms
  - Best practices and recommendations
- **Data quality analysis**
  - Coverage statistics (47% of projects linked to opportunities)
  - Field definitions and code mappings
  - Historical patterns and trends

**Key Discoveries:**
- ✅ PRJ Siebel ID contains Opportunity IDs (1,117 of 2,394 projects)
- ✅ LS_SKU serves as recommendation engine (32 products, 138 service mappings)
- ✅ Complete customer lifecycle tracking possible

### 6. PROJECT_STRUCTURE.md
**Purpose:** Navigate the codebase effectively
- Production files (37 active files)
- Archived files (65+ historical files)
- Folder structure and organization
- What's deployed to Streamlit Cloud
- How to access archived files

### 7. DEPLOYMENT.md
**Purpose:** Deploy and maintain on Streamlit Cloud
- Pre-deployment checklist
- Streamlit Cloud configuration
- Environment variables setup
- Troubleshooting common issues
- Monitoring and rollback procedures

### 8. QUICK_REFERENCE.md
**Purpose:** Quick command lookup
- Common commands
- File paths
- Configuration references
- Keyboard shortcuts
- Useful snippets

---

## 🗂️ Archived Documentation

Historical documentation preserved for reference:

### Location: `archives/old_docs/project_history/`

| Document | Size | Archived Date | Reason |
|----------|------|--------------|---------|
| GIT_STATUS.md | 4.7KB | 2025-10-29 | Historical git status snapshot (October 9) |
| CLEANUP_PLAN.md | 4.8KB | 2025-10-29 | Project cleanup plan (completed) |
| IMPROVEMENTS_IMPLEMENTED.md | 9.9KB | 2025-10-29 | Phase 1 improvements log (October 28) |
| IMPROVEMENT_RECOMMENDATIONS.md | 50KB | 2025-10-29 | Initial improvement analysis (superseded) |
| SERVICE_RECOMMENDATIONS_FINAL.md | 12KB | 2025-10-29 | Service recommendation implementation notes |
| USER_RECOMMENDATIONS_ADDED.md | 14KB | 2025-10-29 | User recommendation feature notes |

**Why Archived:**
- Historical project tracking documents
- Implementation notes already incorporated into current docs
- Valuable for project history but not needed for daily use
- Information superseded by DATA_RELATIONSHIPS_ANALYSIS.md

---

## 🎯 Finding What You Need

### I want to...

**...understand what OneLead does**
→ Start with [README.md](README.md)

**...set up OneLead for the first time**
→ Follow [QUICKSTART.md](QUICKSTART.md)

**...use the Premium Dashboard**
→ Read [LAUNCH_PREMIUM.md](LAUNCH_PREMIUM.md)

**...understand the data relationships**
→ Read [DATA_RELATIONSHIPS_ANALYSIS.md](DATA_RELATIONSHIPS_ANALYSIS.md)

**...understand how Excel data maps to the database**
→ See the detailed analysis in [DATA_RELATIONSHIPS_ANALYSIS.md](DATA_RELATIONSHIPS_ANALYSIS.md)

**...deploy to Streamlit Cloud**
→ Follow [DEPLOYMENT.md](DEPLOYMENT.md)

**...understand the design philosophy**
→ Read [PREMIUM_DASHBOARD.md](PREMIUM_DASHBOARD.md)

**...navigate the codebase**
→ Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**...quickly look up a command**
→ Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**...see project history**
→ Check `archives/old_docs/project_history/`

---

## 📊 Documentation Statistics

### Current State
- **Active Files**: 8 documents (116KB total)
- **Archived Files**: 6 documents (95KB total)
- **Total Documentation**: 211KB

### Cleanup Summary
- **Before**: 14 MD files in root (scattered, redundant)
- **After**: 8 MD files in root (organized, current)
- **Archived**: 6 files moved to project_history
- **Improvement**: 43% reduction in root-level files, better organization

### Coverage
- ✅ User guides: Complete
- ✅ Technical references: Complete
- ✅ Deployment guides: Complete
- ✅ Data analysis: **NEW - Complete (49KB comprehensive guide)**
- ✅ Project structure: Complete
- ✅ Quick references: Complete

---

## 🔄 Documentation Maintenance

### When to Update

**README.md** - When features change, new dashboards added, statistics update
**QUICKSTART.md** - When setup process changes
**DATA_RELATIONSHIPS_ANALYSIS.md** - When data sources change, new relationships discovered
**DEPLOYMENT.md** - When deployment process changes
**PROJECT_STRUCTURE.md** - When major file reorganization occurs
**PREMIUM_DASHBOARD.md** - When UI/UX changes significantly

### How to Update

1. Update the relevant document
2. Update "Last Updated" date at top
3. Update this index if document purpose changes
4. Archive old version if major rewrite (git history preserves all versions)

### Adding New Documentation

1. Create document in root directory
2. Add entry to this index
3. Update README.md documentation section
4. Commit with clear message

---

## 🎓 Best Practices

### For Readers

1. **Start with README.md** - Get oriented first
2. **Use this index** - Find the right document quickly
3. **Check "Last Updated"** - Ensure document is current
4. **Reference Quick Reference** - For common commands
5. **Deep dive when needed** - Technical docs provide comprehensive details

### For Writers

1. **Update timestamps** - Always update "Last Updated" date
2. **Be concise in user guides** - Detailed in technical docs
3. **Use examples** - Show, don't just tell
4. **Cross-reference** - Link to related documents
5. **Version major changes** - Archive superseded docs

---

## 📞 Questions?

- **General**: Start with [README.md](README.md)
- **Setup Issues**: Check [QUICKSTART.md](QUICKSTART.md)
- **Data Questions**: See [DATA_RELATIONSHIPS_ANALYSIS.md](DATA_RELATIONSHIPS_ANALYSIS.md)
- **Deployment Issues**: Reference [DEPLOYMENT.md](DEPLOYMENT.md)
- **File Location**: Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 📌 Quick Navigation

### Essential Documents (Must Read)
1. [README.md](README.md) - Start here
2. [QUICKSTART.md](QUICKSTART.md) - Setup guide
3. [DATA_RELATIONSHIPS_ANALYSIS.md](DATA_RELATIONSHIPS_ANALYSIS.md) - **NEW!** Complete data guide

### Application Usage
4. [LAUNCH_PREMIUM.md](LAUNCH_PREMIUM.md) - Dashboard guide
5. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command reference

### Technical Deep Dive
6. [PREMIUM_DASHBOARD.md](PREMIUM_DASHBOARD.md) - Design philosophy
7. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Codebase navigation
8. [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment

---

**Last Review:** October 29, 2025
**Documentation Status:** ✅ Current, Organized, Complete
**Total Pages:** ~116KB of active documentation
