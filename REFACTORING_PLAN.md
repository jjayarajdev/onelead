# OneLead - Refactoring Plan: Remove Estimated Values, Use Actual Data Only

**Created**: October 29, 2025
**Priority**: HIGH
**Status**: Planning

---

## 🎯 Objective

**Remove all estimated/generated financial values and use ONLY actual data from Excel files.**

---

## 📊 Current State Analysis

### What We Have (Actual Data)

| Data Source | Field | Type | Values |
|-------------|-------|------|--------|
| **A&PS Projects** | PRJ Size | Categorical | '<$50k', '$50k-$500k', '$500k-$1M', '$1M-$5M', '>$5M' |
| **A&PS Projects** | PRJ Size Sort | Integer | 1, 2, 3, 4, 5 (ranking) |
| **A&PS Projects** | PRJ Days | Integer | Actual project duration in days |
| **A&PS Projects** | PRJ Start Date | Date | Actual start dates |
| **A&PS Projects** | PRJ End Date | Date | Actual end dates |
| **Install Base** | Support_Status | Categorical | Active/Expired status |
| **Install Base** | Product_End_of_Life_Date | Date | Actual EOL dates |
| **Service Credits** | PurchasedCredits | Integer | 650 total credits |
| **Service Credits** | ActiveCredits | Integer | 320 available credits |
| **LS_SKU** | Service mappings | List | Product → Service → SKU |

### What We DON'T Have (Currently Estimated)

❌ Install Base asset values
❌ Opportunity deal amounts
❌ Service contract pricing
❌ Exact project revenue/costs
❌ Win rates / close probabilities

---

## 🔧 Refactoring Changes Required

### 1. Lead Generator (`src/engines/lead_generator.py`)

#### Current Issues:
```python
# Lines 59-82: Generates estimated values
def _estimate_renewal_value(self, product_name: str) -> Tuple[float, float]:
    """PROBLEM: Creates fake financial estimates"""
    # Returns made-up values like ($3000, $8000)
```

#### Required Changes:

**Option A: Remove Value Estimation Completely**
```python
# Remove _estimate_renewal_value() function entirely
# Set estimated_value_min and estimated_value_max to None

lead_data = {
    'estimated_value_min': None,  # Don't estimate
    'estimated_value_max': None,  # Don't estimate
    'priority_reason': 'Expired warranty'  # Keep non-financial reasons
}
```

**Option B: Use Project Size Categories (Recommended)**
```python
def _get_project_size_category(self, account_id: int) -> str:
    """
    Get typical project size for this account based on historical data
    Returns: '<$50k', '$50k-$500k', '$500k-$1M', '$1M-$5M', '>$5M', or None
    """
    # Query A&PS projects for this account
    projects = self.session.query(APSProject).filter(
        APSProject.account_st_name.contains(account_name)
    ).all()

    if not projects:
        return None

    # Get most common project size for this account
    sizes = [p.prj_size for p in projects if p.prj_size and p.prj_size != '-']
    if sizes:
        return max(set(sizes), key=sizes.count)  # Most frequent

    return None

lead_data = {
    'estimated_value_min': None,
    'estimated_value_max': None,
    'project_size_category': self._get_project_size_category(account_id),
    'priority_reason': 'Expired warranty'
}
```

---

### 2. Lead Scorer (`src/engines/lead_scorer.py`)

#### Current Issues:
```python
# Uses estimated_value_min/max for value scoring
value_score = self._calculate_value_score(lead)

def _calculate_value_score(self, lead) -> float:
    """PROBLEM: Depends on fake estimated values"""
    if lead.estimated_value_min:
        # Scores based on non-existent data
```

#### Required Changes:

**Replace Value Scoring with Actual Metrics**
```python
def _calculate_value_score(self, lead) -> float:
    """
    Score based on actual data:
    - Historical project size category
    - Number of assets in install base
    - Active service credits
    - Project history (count and recency)
    """
    score = 50  # Base score

    # Factor 1: Project size category (from historical data)
    if lead.project_size_category:
        size_scores = {
            '<$50k': 60,
            '$50k-$500k': 70,
            '$500k-$1M': 80,
            '$1M-$5M': 90,
            '>$5M': 100
        }
        score = size_scores.get(lead.project_size_category, 50)

    # Factor 2: Install base size (more assets = larger account)
    install_base_count = self._get_install_base_count(lead.account_id)
    if install_base_count > 50:
        score += 20
    elif install_base_count > 20:
        score += 10
    elif install_base_count > 10:
        score += 5

    # Factor 3: Historical project count
    project_count = self._get_historical_project_count(lead.account_id)
    if project_count > 10:
        score += 15
    elif project_count > 5:
        score += 10
    elif project_count > 0:
        score += 5

    # Factor 4: Active service credits (shows commitment)
    active_credits = self._get_active_credits(lead.account_id)
    if active_credits > 100:
        score += 15
    elif active_credits > 50:
        score += 10
    elif active_credits > 0:
        score += 5

    return min(score, 100)  # Cap at 100
```

---

### 3. Database Models (`src/models/lead.py`)

#### Current Issues:
```python
class Lead(Base):
    estimated_value_min = Column(Float, nullable=True)
    estimated_value_max = Column(Float, nullable=True)
    # These fields contain fake data
```

#### Required Changes:

**Option A: Remove Fields (Breaking Change)**
```python
class Lead(Base):
    # Remove these fields entirely
    # estimated_value_min = Column(Float, nullable=True)  # DELETE
    # estimated_value_max = Column(Float, nullable=True)  # DELETE

    # Add new fields for actual data
    project_size_category = Column(String(50), nullable=True)
    install_base_count = Column(Integer, nullable=True)
    historical_project_count = Column(Integer, nullable=True)
    active_credits_available = Column(Integer, nullable=True)
```

**Option B: Keep Fields but Set to None (Non-Breaking)**
```python
class Lead(Base):
    # Keep fields for backward compatibility but always set to None
    estimated_value_min = Column(Float, nullable=True)  # Always None
    estimated_value_max = Column(Float, nullable=True)  # Always None

    # Add new fields
    project_size_category = Column(String(50), nullable=True)
    install_base_count = Column(Integer, nullable=True)
    historical_project_count = Column(Integer, nullable=True)
    active_credits_available = Column(Integer, nullable=True)
```

**Recommended: Option B** (maintains backward compatibility)

---

### 4. Dashboard (`src/app/dashboard_premium.py`)

#### Current Issues:
```python
# Displays fake estimated values
if lead.estimated_value_min and lead.estimated_value_max:
    st.write(f"💰 Estimated Value: ${lead.estimated_value_min:,.0f} - ${lead.estimated_value_max:,.0f}")
```

#### Required Changes:

**Replace with Actual Data Display**
```python
# Show actual data instead of estimates
col1, col2, col3 = st.columns(3)

with col1:
    if lead.project_size_category:
        st.metric("Historical Project Size", lead.project_size_category)
    else:
        st.metric("Historical Project Size", "No history")

with col2:
    if lead.install_base_count:
        st.metric("Assets in Install Base", f"{lead.install_base_count} assets")
    else:
        st.metric("Assets in Install Base", "Unknown")

with col3:
    if lead.active_credits_available:
        st.metric("Active Service Credits", f"{lead.active_credits_available} credits")
    else:
        st.metric("Active Service Credits", "None")

# Show historical project performance
if lead.historical_project_count:
    st.write(f"📊 **Historical Engagement**: {lead.historical_project_count} projects completed")
    st.write(f"💡 **Typical project size for this account**: {lead.project_size_category or 'Unknown'}")
```

---

### 5. Service Recommender (`src/engines/service_recommender.py`)

#### Current State:
```python
# Already good - uses LS_SKU mappings (actual data)
# No changes needed
```

✅ **No changes required** - already using actual service catalog data

---

## 📋 Implementation Steps

### Phase 1: Database Schema Update

```bash
# Step 1: Create migration script
python create_migration.py add_actual_metrics

# Step 2: Add new columns to Lead model
# - project_size_category
# - install_base_count
# - historical_project_count
# - active_credits_available

# Step 3: Run migration
python migrate_database.py
```

### Phase 2: Update Lead Generator

```python
# File: src/engines/lead_generator.py

# Step 1: Remove _estimate_renewal_value() function
# Step 2: Add _get_project_size_category() function
# Step 3: Add _get_install_base_count() function
# Step 4: Add _get_historical_project_count() function
# Step 5: Add _get_active_credits() function
# Step 6: Update lead_data dict to use actual metrics
```

### Phase 3: Update Lead Scorer

```python
# File: src/engines/lead_scorer.py

# Step 1: Refactor _calculate_value_score() to use actual metrics
# Step 2: Test scoring with real data
# Step 3: Adjust weights if needed
```

### Phase 4: Update Dashboard

```python
# File: src/app/dashboard_premium.py

# Step 1: Replace estimated value display
# Step 2: Add actual metrics display
# Step 3: Update lead card layout
# Step 4: Add historical project performance section
```

### Phase 5: Regenerate Leads

```bash
# Step 1: Delete existing leads with fake data
python -c "from src.models.base import Session; from src.models.lead import Lead; session = Session(); session.query(Lead).delete(); session.commit()"

# Step 2: Regenerate with actual data
python generate_leads.py

# Step 3: Verify in dashboard
streamlit run src/app/dashboard_premium.py
```

---

## 🎯 New Lead Card Example (After Refactoring)

### Before (With Fake Data):
```
Lead: HP DL360p Gen8 Server Renewal
Score: 85
Priority: CRITICAL

💰 Estimated Value: $200,000 - $400,000  ← FAKE
🎯 Recommended Action: Contact for renewal
```

### After (Actual Data Only):
```
Lead: HP DL360p Gen8 Server Renewal
Score: 85
Priority: CRITICAL

📊 Account Metrics (Actual Data):
  • Historical Project Size: $500k-$1M
  • Install Base: 45 assets
  • Completed Projects: 12 projects
  • Active Credits: 75 credits available

💡 Why This Matters:
  This account has a strong history with HPE:
  - 12 successful projects delivered
  - Typical projects in $500k-$1M range
  - Large install base (45 assets) indicates enterprise account
  - 75 active service credits available for immediate use

🎯 Recommended Services (from LS_SKU):
  1. Health Check (SKU: HL997A1)
  2. Firmware Upgrade (SKU: HL997A1)
  3. Complete Care Support (Contact sales for quote)

📞 Next Best Action:
  Contact within 7 days - warranty expired 2+ years ago
```

---

## 📊 New Service Recommendation Categories

### Category 1: Ongoing Projects with Historical Data

**Query A&PS Projects WHERE end_date > today**

**Display**:
- Project ID and description
- Current status and health
- Practice area
- Days until completion
- **Historical project size** (from PRJ Size field)
- Recommended follow-on services (from LS_SKU)
- Available service credits

**Example**:
```
Ongoing Project: JP3-P0314
Customer: Bank of Japan
Practice: Cloud & Platform
End Date: 2035-10-31 (3,654 days remaining)
Historical Size: >$5M (large strategic project)
Status: Active

🎯 Recommended Services:
  → Annual business review (based on project size)
  → Quarterly optimization services
  → Managed services contract (multi-year)

💳 Service Credits Available: 75 credits
```

---

### Category 2: Completed Projects with Size History

**Query A&PS Projects WHERE end_date <= today**

**Display**:
- Project completion date
- Days since completion
- Practice area
- **Actual project size category**
- Project health/success indicator
- Recommended re-engagement services

**Example**:
```
Completed Project: JP3-GS667
Customer: Bank of Japan
Practice: Cloud & Platform
Completed: 2025-10-01 (28 days ago)
Project Size: $500k-$1M
Health: Good

🎯 Re-engagement Opportunity:
  → Post-implementation support (90-day hypercare)
  → Complete Care support contract
  → Health check & optimization

📊 Account Context:
  • 12 total projects completed
  • Average size: $500k-$1M
  • 75 active credits available

⏰ Action Urgency: HIGH (< 30 days post-completion)
```

---

## ✅ Benefits of This Approach

### 1. Data Integrity
✅ All values are **actual** from Excel files
✅ No generated/estimated numbers
✅ Transparent and auditable

### 2. Actionable Intelligence
✅ Historical project size guides expectations
✅ Install base count shows account size
✅ Project history shows engagement patterns
✅ Service credits show available budget

### 3. Service Recommendations
✅ Based on actual product ownership (Install Base)
✅ Matched to real services (LS_SKU catalog)
✅ Informed by historical patterns (A&PS projects)
✅ Considers available credits (Service Credits)

### 4. Prioritization
✅ Urgency based on actual dates (warranty expiry, EOL)
✅ Account value based on actual metrics (asset count, project history)
✅ Engagement warmth based on recency (days since last project)

---

## 🎯 Scoring Formula (Refactored)

### Old Formula (Used Fake Data):
```
Score = (Urgency × 0.35) + (Estimated_Value × 0.30) + (Propensity × 0.20) + (Strategic × 0.15)
                                     ↑ PROBLEM: Fake numbers
```

### New Formula (Actual Data Only):
```
Score = (Urgency × 0.40) + (Account_Size × 0.30) + (Engagement × 0.20) + (Strategic × 0.10)

Where:
  Urgency (0-100):
    - Days past warranty expiry
    - Days past EOL
    - Days until project end
    - Days since project completion

  Account_Size (0-100):
    - Historical project size category (from PRJ Size)
    - Install base asset count
    - Total historical project count

  Engagement (0-100):
    - Recency of last project (days)
    - Number of recent projects (last 2 years)
    - Active service credits available
    - Opportunity → Project conversion (has links)

  Strategic (0-100):
    - Business area alignment
    - Practice area fit
    - Product family importance
```

---

## 📝 Code Changes Summary

### Files to Modify:

| File | Changes | Lines | Impact |
|------|---------|-------|--------|
| `src/models/lead.py` | Add new columns | ~10 | Database schema |
| `src/engines/lead_generator.py` | Remove estimates, add actual metrics | ~100 | Lead generation |
| `src/engines/lead_scorer.py` | Refactor value scoring | ~50 | Scoring logic |
| `src/app/dashboard_premium.py` | Update display to show actual data | ~30 | UI display |
| `generate_leads.py` | No changes (just regenerate) | 0 | Execution |

**Total**: ~190 lines of code changes

---

## 🚀 Rollout Plan

### Week 1: Development & Testing
- [ ] Day 1-2: Update database schema
- [ ] Day 2-3: Refactor lead generator
- [ ] Day 3-4: Refactor lead scorer
- [ ] Day 4-5: Update dashboard

### Week 2: Data Migration & Validation
- [ ] Day 1: Generate leads with new logic
- [ ] Day 2-3: Validate outputs
- [ ] Day 4: User testing
- [ ] Day 5: Documentation updates

### Week 3: Deployment
- [ ] Day 1: Deploy to test environment
- [ ] Day 2-3: QA testing
- [ ] Day 4: Production deployment
- [ ] Day 5: Monitor and adjust

---

## 📊 Expected Outcomes

### Before Refactoring:
- ❌ Estimated values: $1.15M pipeline (FAKE)
- ❌ No historical context
- ❌ Misleading financial projections

### After Refactoring:
- ✅ 77 leads with ACTUAL metrics
- ✅ Historical project sizes: 5 categories
- ✅ Account size: Asset counts
- ✅ Engagement patterns: Project history
- ✅ Available budget: Service credits
- ✅ Service recommendations: Real SKUs from catalog

---

## 🎓 Key Principles

1. **If it's not in the data, don't create it**
2. **Use actual historical patterns, not estimates**
3. **Show what we know, acknowledge what we don't**
4. **Prioritize by urgency + engagement, not fake money**
5. **Recommend services we can actually deliver (LS_SKU)**

---

## 📞 Next Steps

1. **Review this plan** with stakeholders
2. **Approve approach** (Option A vs B for schema)
3. **Prioritize implementation** (all at once vs. phased)
4. **Assign developers** to each component
5. **Set timeline** (2-3 weeks recommended)

---

**Document Status**: ✅ Ready for Review
**Recommendation**: Implement Option B (backward compatible) in phased approach
**Est. Effort**: 2-3 weeks (1 developer)
