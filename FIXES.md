# Bug Fixes - Premium Dashboard

## Issue: AttributeError on Dashboard Launch

**Problem:** Premium Dashboard crashed on startup with multiple AttributeError exceptions.

**Root Cause:** Field name mismatches between the Premium Dashboard code and the actual database models.

---

## Fixes Applied

### Fix 1: Lead.territory → Lead.territory_id
```python
# Before:
'territory': lead.territory,

# After:
'territory': lead.territory_id or 'Unknown',
```

**Reason:** Lead model has `territory_id` field, not `territory`.

---

### Fix 2: lead.product_description → lead.install_base_item.product_name
```python
# Before:
'product_description': lead.product_description,

# After:
'product_description': lead.install_base_item.product_name if lead.install_base_item else 'N/A',
```

**Reason:**
- Lead model doesn't have `product_description` field
- Product info is in the related `install_base_item` object
- InstallBase model has `product_name` field (not `product_description`)

---

### Fix 3: lead.estimated_value → lead.estimated_value_max
```python
# Before:
'estimated_value': lead.estimated_value or 0,

# After:
'estimated_value': lead.estimated_value_max or lead.estimated_value_min or 0,
```

**Reason:**
- Lead model doesn't have single `estimated_value` field
- Has `estimated_value_min` and `estimated_value_max` instead
- Use max value, fall back to min if max is null

---

### Fix 4: lead.status → lead.lead_status
```python
# Before:
'status': lead.status,

# After:
'status': lead.lead_status,
```

**Reason:** Lead model has `lead_status` field, not `status`.

---

### Fix 5: lead.created_date → lead.generated_at
```python
# Before:
'created_date': lead.created_date

# After:
'created_date': lead.generated_at
```

**Reason:** Lead model has `generated_at` field, not `created_date`.

---

### Fix 6: Opportunity.amount → Lead.estimated_value_max
```python
# Before:
'total_pipeline': session.query(func.sum(Opportunity.amount)).scalar() or 0

# After:
'total_pipeline': session.query(func.sum(Lead.estimated_value_max)).filter(
    Lead.is_active == True
).scalar() or 0
```

**Reason:**
- Opportunity model doesn't have `amount` field
- Source Excel data doesn't include opportunity amounts
- Use lead estimated values to calculate pipeline instead

---

## Model Field Reference

For future reference, here are the actual model fields:

### Lead Model
```python
- territory_id          # NOT territory
- lead_status          # NOT status
- estimated_value_min  # NOT estimated_value
- estimated_value_max  # NOT estimated_value
- generated_at         # NOT created_date
- (no product_description field - get from install_base_item)
```

### InstallBase Model
```python
- product_name         # NOT product_description
- line_description
- product_id
- serial_number
```

### Opportunity Model
```python
- opportunity_id
- opportunity_name
- product_line
- (no amount field - not in source data)
```

---

## Testing Results

After fixes:
```
✓ Loaded 77 leads successfully
✓ Stats: {
    'total_accounts': 32,
    'total_install_base': 63,
    'critical_systems': 26,
    'active_opportunities': 98,
    'total_pipeline': 6400000.0  # $6.4M
  }
✓ All fields accessible
✓ Dashboard ready to launch
```

---

## Launch Instructions

```bash
# Option 1: Use launcher
./run_dashboard.sh
# Select option 1: Premium Intelligence Dashboard

# Option 2: Direct launch
streamlit run src/app/dashboard_premium.py
```

---

## Lessons Learned

1. **Always check model definitions** before using field names
2. **Use existing dashboards as reference** (e.g., dashboard_business.py)
3. **Test data loading** before full dashboard testing
4. **Handle null values** gracefully (use `or` fallbacks)
5. **Leverage relationships** (e.g., `lead.install_base_item.product_name`)

---

## Files Modified

- `src/app/dashboard_premium.py` - Fixed all field name mismatches

## Files Checked for Reference

- `src/models/lead.py` - Lead model definition
- `src/models/install_base.py` - InstallBase model definition
- `src/models/opportunity.py` - Opportunity model definition
- `src/app/dashboard_business.py` - Reference for correct field usage

---

**Status:** ✅ All issues resolved
**Date:** October 9, 2025
**Version:** 2.0 (Premium Dashboard)
