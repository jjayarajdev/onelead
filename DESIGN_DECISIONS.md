# OneLead System - Design Decisions & Architecture

## Executive Summary

OneLead is a sales intelligence system designed to automatically identify revenue opportunities from install base data. The system analyzes hardware inventory, support coverage, and customer engagement patterns to generate scored, actionable leads for sales teams.

**Key Metrics:**
- Processes 63 install base records
- Generates 77 prioritized leads (30 renewal + 27 hardware refresh + 20 service attach)
- Scores leads 0-100 using 4-factor algorithm
- Provides 360° account intelligence across 2,394 historical projects

---

## 1. Architecture Decision: Why Python + SQLite + Streamlit

### Decision Rationale

**Chosen Stack:**
- **Backend**: Python 3.11+ with SQLAlchemy ORM
- **Database**: SQLite (file-based)
- **ETL**: pandas for Excel processing
- **UI**: Streamlit for rapid dashboard development
- **Visualization**: Plotly for interactive charts

### Why This Approach?

#### 1.1 Python Ecosystem
**Decision:** Use Python as the primary language

**Rationale:**
- **Data Processing Strength**: pandas excels at Excel/CSV manipulation
- **Rapid Development**: Python's ecosystem enables fast prototyping
- **Maintainability**: Readable code, easy for sales operations teams to understand
- **Library Ecosystem**: Rich set of data science and ML libraries for future enhancements

**Alternative Considered:** JavaScript (Node.js)
- **Rejected Because**: Weaker data processing libraries, less familiar to data analysts

#### 1.2 SQLite vs. PostgreSQL/MySQL
**Decision:** Use SQLite for data storage

**Rationale:**
- **Zero Configuration**: No database server setup required
- **Portability**: Single file database, easy to backup/move
- **Sufficient Scale**: Handles thousands of records efficiently
- **Local Development**: No network latency, works offline
- **Version Control**: Can commit database to Git (for dev/test)

**Trade-offs:**
- **Pro**: Instant setup, no infrastructure costs
- **Con**: Limited to ~1M records (acceptable for current scope)
- **Con**: No concurrent write operations (not needed for this use case)

**Migration Path:** Easy upgrade to PostgreSQL by changing connection string if scale demands it

#### 1.3 Streamlit vs. React/Flask
**Decision:** Use Streamlit for dashboard UI

**Rationale:**
- **Rapid Development**: Dashboard built in ~300 lines vs. thousands for React
- **Built-in Components**: Tables, charts, filters out-of-the-box
- **Python Native**: No context switching between frontend/backend
- **Iteration Speed**: Changes visible in seconds with hot-reload

**Trade-offs:**
- **Pro**: 10x faster development, perfect for MVP
- **Con**: Less customization than React (acceptable for internal tool)
- **Con**: Session state management can be tricky (mitigated with caching)

---

## 2. Data Modeling Strategy

### 2.1 Entity Relationship Design

**Core Entities:**
```
Account (Customer)
  ├── Install Base Items (1:many)
  ├── Opportunities (1:many)
  ├── Projects (1:many)
  └── Leads (1:many)

Service Catalog (Available Services)
Service SKU Mapping (Product → Service)
```

### 2.2 Key Modeling Decisions

#### Decision: Separate Account from Territory
**Problem:** Source data uses territory IDs as account identifiers

**Solution:**
- Created `Account` entity with both `account_name` and `territory_id`
- Implemented account normalization to merge variations
- Built territory mapping from Opportunities data

**Rationale:**
- **Data Quality**: Territory IDs (56088) aren't user-friendly
- **Fuzzy Matching**: Account names vary ("Apple Inc" vs. "APPLE INC.")
- **Consolidation**: Multiple records for same customer need unified view

**Implementation:**
```python
# Account normalization removes suffixes, punctuation, case differences
"Apple Inc" → "apple"
"APPLE INC." → "apple"
"Apple Computer Inc" → "apple computer"
# Then fuzzy match with 85% threshold
```

#### Decision: Denormalize Risk Metrics in Install Base
**Problem:** Need to frequently query by urgency (days since EOL, expiry status)

**Solution:** Calculate and store derived fields:
- `days_since_eol`: Pre-calculated at ETL time
- `days_since_expiry`: Pre-calculated at ETL time
- `risk_level`: CRITICAL, HIGH, MEDIUM, LOW (computed from above)

**Rationale:**
- **Performance**: Avoid recalculating dates on every query
- **Consistent Logic**: Risk calculation centralized in ETL
- **Fast Filtering**: Dashboard can filter by risk_level directly

**Trade-off:** Data becomes stale if dates change (acceptable - EOL dates don't change)

#### Decision: Non-Unique Project IDs
**Problem:** Source data contains duplicate/invalid project IDs ("#", "NOT AVAILABLE")

**Solution:**
- Made `project_id` non-unique in database
- Generate synthetic IDs (`UNKNOWN_PRJ_123`) for invalid entries
- Keep all records for historical analysis

**Rationale:**
- **Data Preservation**: Don't lose historical project data
- **Audit Trail**: Maintain complete record of source data
- **Future Cleanup**: Can deduplicate later with business logic

**Alternative Rejected:** Skip duplicates
- Would lose valuable historical spending patterns

---

## 3. ETL Pipeline Design

### 3.1 Data Quality Challenges

**Challenge 1: Inconsistent Date Formats**
```
Source Data:
- "2015-07-01" (string)
- Timestamp objects
- "(null)" strings
- NaN values
```

**Solution:**
```python
def _parse_date(self, date_value) -> Optional[date]:
    if pd.isna(date_value) or str(date_value).lower() in ['(null)', 'null', 'nan']:
        return None
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    # ... handle datetime, date, string formats
```

**Challenge 2: Non-Numeric Financial Data**
```
Source: Labor Cost = "Yes" (should be float)
```

**Solution:**
```python
def _parse_float(self, value) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None  # Graceful degradation
```

### 3.2 Product Family Classification

**Challenge:** Install base has free-text product names, need to categorize

**Solution:** Pattern-based classification
```python
def _extract_product_family(self, product_name: str, product_platform: str) -> str:
    text = f"{product_name} {product_platform}".lower()

    # Storage products
    if '3par' in text: return '3PAR'
    if 'primera' in text: return 'PRIMERA'
    if 'alletra' in text: return 'ALLETRA'

    # Compute products
    if any(x in text for x in ['dl', 'ml', 'bl', 'gen']):
        return 'COMPUTE'
```

**Rationale:**
- **Service Matching**: Services are product-family specific
- **Strategic Segmentation**: Different sales plays per family
- **Reporting**: Territory performance by product line

---

## 4. Lead Generation Logic

### 4.1 Three Lead Types - Why These?

#### Type 1: Renewal Leads (Expired Support)
**Trigger:** `support_status LIKE '%Expired%' AND risk_level IN ('CRITICAL', 'HIGH')`

**Business Rationale:**
- **Immediate Revenue**: Support renewals close quickly (30-60 days)
- **Risk Mitigation**: Customer running without support = high urgency
- **Retention**: Prevent customer from switching vendors

**Example:**
```
Input: HP DL360p Gen8, Support Status: "Warranty Expired - Uncovered Box"
Output: Lead with CRITICAL priority, score 75-90
Action: "Contact account to renew support contract"
```

#### Type 2: Hardware Refresh Leads (EOL Equipment)
**Trigger:** `days_since_eol > 1825` (5 years past end-of-life)

**Business Rationale:**
- **High Value**: Hardware deals are $75K-$200K+
- **Strategic**: Opportunity to modernize customer infrastructure
- **Competitive Defense**: Old equipment = vulnerable to competitors

**Example:**
```
Input: Gen8 server (2012 vintage), EOL 2015, currently 2025
Output: Lead suggesting Gen11 upgrade
Value: $75K-$200K
```

**Why 5 Years?**
- Industry standard: Hardware typically refreshed every 3-5 years
- 5+ years = well beyond normal lifecycle
- High likelihood customer is already planning refresh

#### Type 3: Service Attach Leads (Coverage Gaps)
**Trigger:** `support_status LIKE '%Uncovered%'`

**Business Rationale:**
- **Incremental Revenue**: Add services to existing hardware
- **Customer Success**: Improve uptime and satisfaction
- **Annuity Revenue**: Service contracts provide recurring revenue

---

## 5. Scoring Algorithm Design

### 5.1 Four-Factor Model

**Formula:**
```
Score = (Urgency × 0.35) + (Value × 0.30) + (Propensity × 0.20) + (Strategic Fit × 0.15)
```

### 5.2 Weight Rationale

#### Why Urgency = 35% (Highest Weight)
**Rationale:**
- **Time Sensitivity**: Expired support = immediate risk
- **Customer Pain**: The longer without support, the higher the pain
- **Close Rate**: Urgent needs close faster

**Calculation:**
```python
score = 50  # baseline

# Days since EOL
if days_since_eol > 1825:  # 5 years
    score += 30  # Maximum urgency
elif days_since_eol > 1095:  # 3 years
    score += 20

# Days since support expired
if days_since_expiry > 365:  # 1 year
    score += 20
```

#### Why Value = 30% (Second Highest)
**Rationale:**
- **Revenue Focus**: Sales teams prioritize large deals
- **Resource Allocation**: High-value deals get more attention
- **Account Strategic Value**: Large install base = larger wallet share

**Calculation:**
```python
# Deal size
if estimated_value_max >= 200000:
    score += 40
elif estimated_value_max >= 100000:
    score += 30

# Account install base size (proxy for account value)
if account_hardware_count > 50:
    score += 20  # Large account = more opportunity
```

#### Why Propensity = 20%
**Rationale:**
- **Buying Signals**: Open opportunities = active buying mode
- **Historical Behavior**: Past purchases = likely to buy again
- **Warm vs. Cold**: Engaged accounts close faster

**Calculation:**
```python
# Open opportunities
if open_opportunities > 5:
    score += 30  # Very active account

# Closed projects (historical buying behavior)
if closed_projects > 10:
    score += 30  # Frequent buyer
```

#### Why Strategic Fit = 15% (Lowest Weight)
**Rationale:**
- **Company Priorities**: Certain products are strategic priorities
- **Margin**: Some product families have better margins
- **Lower Weight**: Less important than urgency or value

**Calculation:**
```python
strategic_families = ['3PAR', 'PRIMERA', 'ALLETRA', 'COMPUTE']
if product_family in strategic_families:
    score += 25

if lead_type == 'Hardware Refresh':
    score += 10  # Strategic priority
```

### 5.3 Priority Thresholds

```python
if score >= 75:  priority = 'CRITICAL'  # Top 10% - immediate action
elif score >= 60: priority = 'HIGH'     # Top 25% - this week
elif score >= 40: priority = 'MEDIUM'   # Top 50% - this month
else:             priority = 'LOW'      # Long-term nurture
```

**Rationale:**
- **Action-Oriented**: Clear prioritization for sales teams
- **Resource Allocation**: Focus on CRITICAL/HIGH first
- **Balanced Distribution**: Avoids marking everything "high priority"

---

## 6. Service Recommendation Engine

### 6.1 Product-to-Service Mapping Strategy

**Challenge:** Different products require different services

**Solution:** Service SKU mapping table
```
Product Family | Category    | Service Type        | SKU
3PAR          | Storage SW  | OS Upgrade          | HM002A1
3PAR          | Storage SW  | Health Check        | H9Q53AC
Primera       | Storage SW  | Migration           | HA124A1#5Q3
```

**Source:** Extracted from `LS_SKU_for_Onelead.xlsx`

### 6.2 Priority-Based Recommendation

**Logic:** Service recommendations change based on lead type

```python
if lead_type == 'Renewal':
    priority_boost = {
        'health_check': +10,    # Assess current state
        'upgrade': +8,          # Get to supported version
        'performance': +6       # Optimize existing
    }
elif lead_type == 'Hardware Refresh':
    priority_boost = {
        'migration': +10,       # Move data to new hardware
        'install_startup': +9,  # Deploy new equipment
        'rebalance': +7         # Optimize new config
    }
```

**Rationale:**
- **Context-Aware**: Match services to customer need
- **Attach Rate**: Increase service revenue per hardware sale
- **Customer Value**: Recommend truly helpful services

---

## 7. Data Mapping & Integration Decisions

### 7.1 Account Normalization Strategy

**Problem:** Multiple data sources use different account identifiers

```
Install Base:    Territory ID (56088)
Opportunities:   Account Name ("Apple Inc")
Projects:        Account Name ("日本ヒューレット・パッカード合同会社")
```

**Solution: Multi-Stage Reconciliation**

**Stage 1: Exact Match on Territory ID**
```python
# All records with same territory_id → same account
territory_id = "56088"
→ Consolidate all install base items
```

**Stage 2: Fuzzy Name Matching**
```python
# Normalize names
"Apple Inc" → "apple"
"APPLE INC." → "apple"
"Apple Computer Inc" → "apple computer"

# Levenshtein distance matching (85% threshold)
fuzz.ratio("apple", "apple computer") = 75% → No match
fuzz.ratio("apple inc", "apple computer inc") = 85% → Match!
```

**Stage 3: Manual Mapping (Config)**
```yaml
territory_mapping:
  "56088": "Apple Inc"
  "56180": "APPLIED MATERIALS, INC."
```

**Why This Approach?**
- **Automatic**: Most accounts matched automatically
- **Configurable**: Override with manual mappings
- **Auditable**: Can trace why accounts were merged

### 7.2 Territory vs. Account Decision

**Original Design (Rejected):**
```
Account = Territory (1:1 relationship)
```

**Final Design (Chosen):**
```
Territory (56088) → Multiple Accounts possible
Account stores both account_name AND territory_id
```

**Rationale:**
- **Flexibility**: One territory can have multiple named accounts
- **Real Names**: Show "Apple Inc" not "56088" in dashboard
- **Source Fidelity**: Preserve original territory IDs for reporting

### 7.3 Missing Data Handling

**Philosophy: Graceful Degradation**

```python
# Date fields
if missing: return None  # Don't block record

# Financial fields
if "Yes" instead of number: return None  # Don't crash

# Account names
if missing or "#": use "Territory {id}"  # Always have a name

# Project IDs
if duplicate or "#": generate synthetic ID  # Keep all data
```

**Rationale:**
- **Data Preservation**: Never lose records due to quality issues
- **Progressive Enhancement**: Works with partial data, better with complete data
- **Future Cleanup**: Can fix data quality issues later without code changes

---

## 8. Dashboard UX Decisions

### 8.1 Five-Page Structure

**Page 1: Dashboard (Overview)**
- **Purpose**: Executive summary, top 10 leads
- **Rationale**: Quick snapshot for sales managers
- **Metrics**: Total leads, high priority count, pipeline value

**Page 2: Lead Queue (Work List)**
- **Purpose**: Daily work queue for sales reps
- **Rationale**: Filterable, sortable, action-oriented
- **Features**: Filter by type, priority, score threshold

**Page 3: Account 360° (Deep Dive)**
- **Purpose**: Complete account intelligence
- **Rationale**: Prepare for customer meetings
- **Data**: Install base, leads, opportunities, projects

**Page 4: Territory View (Management)**
- **Purpose**: Territory performance tracking
- **Rationale**: Sales managers need territory rollup
- **Metrics**: Lead count, pipeline value by territory

**Page 5: Analytics (Insights)**
- **Purpose**: Performance metrics, trends
- **Rationale**: Data-driven decision making
- **Visualizations**: Score distribution, territory leaderboard

### 8.2 Filtering Strategy

**Decision:** Client-side filtering (load all data, filter in browser)

**Rationale:**
- **Simplicity**: No complex database queries
- **Responsiveness**: Instant filter updates
- **Acceptable Scale**: 77 leads load instantly

**Trade-off:**
- **Pro**: Fast development, instant UX
- **Con**: Won't scale to 100K+ leads (not needed now)
- **Migration Path**: Easy to add server-side pagination later

---

## 9. Configuration-Driven Design

### 9.1 Why config/config.yaml?

**Decision:** Externalize business rules to YAML config

**Rationale:**
- **Business User Control**: Sales ops can adjust without code changes
- **Rapid Tuning**: Change scoring weights, test impact
- **Environment-Specific**: Different configs for dev/prod
- **Documentation**: Config file is self-documenting

**What's Configurable:**
```yaml
scoring_weights:
  urgency: 0.35        # ← Adjust scoring importance
  value: 0.30

urgency_thresholds:
  critical_days_past_eol: 1825  # ← Tune lead triggers

territory_mapping:
  "56088": "Apple Inc"  # ← Add/update account names
```

**What's NOT Configurable (Hard-Coded):**
- Lead generation logic (requires code understanding)
- Database schema (requires migration)
- Service recommendation algorithm (business logic)

---

## 10. Trade-offs & Future Enhancements

### 10.1 Current Limitations

**1. Service Recommendations Not Fully Populated**
- **Issue**: 0 leads enriched with SKUs
- **Cause**: Service SKU mapping table incomplete
- **Fix Needed**: Parse more service SKUs from Excel, expand mapping table

**2. No ML-Based Scoring**
- **Current**: Rule-based scoring algorithm
- **Future**: Train model on historical win/loss data
- **Benefit**: Improve score accuracy over time

**3. Static Data**
- **Current**: Manual refresh via `load_data.py`
- **Future**: Scheduled ETL jobs, real-time sync with CRM
- **Benefit**: Always up-to-date lead queue

**4. No Lead Status Tracking**
- **Current**: Leads are "New" forever
- **Future**: Update status (Qualified, Converted, Rejected)
- **Benefit**: Track conversion rates, ROI

### 10.2 Recommended Next Steps

**Phase 2 Enhancements (Next 2-3 Weeks):**
1. **Complete Service SKU Mapping**
   - Manually enter all service SKUs from Excel
   - Enrich leads with service recommendations
   - Add estimated service value to pipeline

2. **Lead State Management**
   - Add "Qualify", "Reject", "Convert to Opportunity" buttons
   - Track conversion rates by lead type
   - Build funnel analytics

3. **CSV Export**
   - Export filtered lead lists
   - Share with field sales teams
   - Import into CRM

**Phase 3 Enhancements (Next 1-2 Months):**
1. **CRM Integration**
   - One-click opportunity creation in Salesforce/Dynamics
   - Bi-directional sync (lead status updates)
   - Automatic lead assignment by territory

2. **Email Alerts**
   - Daily digest of new CRITICAL leads
   - Weekly territory performance summary
   - Lead aging alerts (>30 days old)

3. **Predictive Scoring**
   - Train ML model on historical close rates
   - Feature engineering: account industry, size, product mix
   - A/B test rule-based vs. ML scoring

---

## 11. Success Metrics & Validation

### 11.1 How to Measure Success

**Leading Indicators:**
- Lead acceptance rate (sales team agrees lead is valid)
- Average time to contact (speed of follow-up)
- Lead queue velocity (how fast leads move through pipeline)

**Lagging Indicators:**
- Conversion rate (leads → closed opportunities)
- Revenue from OneLead-generated opportunities
- Time to close (OneLead leads vs. manual leads)

### 11.2 Expected Outcomes

**Conservative Estimates (First 90 Days):**
- 20% of leads convert to qualified opportunities
- Average deal size: $75K
- Expected revenue: 77 leads × 20% × $75K = **$1.15M pipeline**

**Success Criteria:**
- ✅ Conversion rate ≥ 15% (better than cold outreach ~5%)
- ✅ Sales team uses dashboard weekly
- ✅ Identified opportunities sales team missed manually

---

## 12. Conclusion

### Key Design Principles Applied

1. **Pragmatism Over Perfection**
   - SQLite instead of PostgreSQL (good enough for scale)
   - Streamlit instead of React (10x faster development)
   - Rule-based scoring instead of ML (MVP first)

2. **Configuration Over Code**
   - Business rules in YAML
   - Easy to tune without developer
   - Self-documenting

3. **Data Quality Over Purity**
   - Graceful degradation for missing data
   - Preserve all records, even duplicates
   - Progressive enhancement

4. **Insight Over Perfection**
   - 77 actionable leads > 0 perfect leads
   - Fast iteration > complete feature set
   - Working dashboard > architectural purity

### Why This Approach Works

**For Sales Teams:**
- Actionable leads with clear next steps
- Prioritization built-in (score + priority)
- 360° account context for meetings

**For Sales Operations:**
- No-code configuration (adjust weights, thresholds)
- Rapid deployment (no infrastructure)
- Easy to extend (add new lead types)

**For Development:**
- Fast iteration (Streamlit hot-reload)
- Maintainable codebase (Python, clear structure)
- Easy to migrate (SQLAlchemy abstracts DB)

### Final Thought

This system prioritizes **time to value** over architectural perfection. It delivers 77 scored leads today, not a perfect system in 6 months. The modular design allows incremental improvement while providing immediate business value.

---

## Appendix: Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   DATA SOURCES                          │
│  - DataExportAug29th.xlsx (Install Base, Opps, Projects)│
│  - LS_SKU_for_Onelead.xlsx (Service Mappings)          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  ETL PIPELINE                           │
│  - Parse Excel files                                    │
│  - Normalize account names (fuzzy matching)            │
│  - Calculate risk levels (days since EOL/expiry)       │
│  - Extract product families (pattern matching)         │
│  - Handle missing/invalid data (graceful degradation)  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              SQLITE DATABASE                            │
│  - accounts (unified customer view)                     │
│  - install_base (hardware inventory + risk)            │
│  - opportunities (sales pipeline)                       │
│  - projects (historical delivery)                       │
│  - service_catalog (available services)                 │
│  - service_sku_mappings (product → service)            │
│  - leads (generated opportunities)                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           BUSINESS LOGIC ENGINES                        │
│                                                         │
│  LeadGenerator:                                         │
│    - Scan install base for triggers                    │
│    - Generate renewal leads (expired support)          │
│    - Generate hardware refresh leads (EOL equipment)   │
│    - Generate service attach leads (coverage gaps)     │
│                                                         │
│  ServiceRecommender:                                    │
│    - Match product families to services                │
│    - Prioritize by lead type                           │
│    - Attach SKUs to leads                              │
│                                                         │
│  LeadScorer:                                            │
│    - Calculate urgency score (35%)                     │
│    - Calculate value score (30%)                       │
│    - Calculate propensity score (20%)                  │
│    - Calculate strategic fit score (15%)               │
│    - Assign priority (CRITICAL/HIGH/MEDIUM/LOW)        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            STREAMLIT DASHBOARD                          │
│                                                         │
│  Pages:                                                 │
│    1. Dashboard - Overview + top 10 leads              │
│    2. Lead Queue - Filterable work list               │
│    3. Account 360° - Complete account intelligence     │
│    4. Territory View - Territory performance          │
│    5. Analytics - Metrics and trends                   │
│                                                         │
│  Interactions:                                          │
│    - Filter by type, priority, score                   │
│    - Sort by any column                                │
│    - Drill down to account details                     │
│    - View score breakdowns                             │
└─────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-09
**Author:** OneLead System Architecture Team
