# Fuzzy Logic Usage in OneLead

**Last Updated**: October 31, 2025
**Status**: ✅ Active Implementation

---

## 📋 Executive Summary

Fuzzy logic is currently used in OneLead for **account name normalization and matching**. The implementation uses the `fuzzywuzzy` library (Levenshtein distance algorithm) to handle variations in customer account names across different data sources.

---

## 🎯 Primary Use Case: Account Name Normalization

### Problem Being Solved

When loading data from multiple sources (Install Base, Opportunity, A&PS Projects), the same customer account may be named differently:

**Examples of Variations:**
```
Source 1: "Apple Inc"
Source 2: "APPLE INC."
Source 3: "Apple Computer Inc"
Source 4: "apple inc"
```

Without fuzzy matching, these would be treated as **4 different accounts** instead of 1.

### Solution: Fuzzy String Matching

The system uses **Levenshtein distance** (edit distance) to calculate similarity between account names and normalize them to a canonical form.

---

## 🔧 Implementation Details

### 1. Location: `src/utils/account_normalizer.py`

**Class**: `AccountNormalizer`

**Key Methods**:

#### `__init__(patterns, fuzzy_threshold=85)`
- **Purpose**: Initialize with known account name patterns and similarity threshold
- **fuzzy_threshold**: Minimum similarity score (0-100) to consider a match
- **Default**: 85% similarity required

#### `normalize(account_name)`
- **Purpose**: Convert any account name variation to its canonical form
- **Process**:
  1. Clean the name (lowercase, remove suffixes like Inc/Corp/Ltd, remove punctuation)
  2. Check for exact match in known patterns
  3. If no exact match, use fuzzy matching (Levenshtein distance)
  4. Return best match if score ≥ threshold, otherwise return cleaned name

#### `are_same_account(name1, name2)`
- **Purpose**: Check if two names refer to the same account
- **Returns**: True if normalized forms match

#### `find_canonical(account_name, existing_accounts)`
- **Purpose**: Find the best matching account from a list of existing accounts
- **Used for**: Deduplication during data loading

---

### 2. Configuration: `config/config.yaml`

```yaml
account_normalization:
  patterns:
    - ["Apple Inc", "APPLE INC.", "Apple Computer Inc", "APPLE COMPUTER INC"]
    - ["Applied Materials, Inc.", "APPLIED MATERIALS, INC."]
  fuzzy_threshold: 85  # Levenshtein ratio threshold (0-100)
```

**Configurable Parameters**:
- **patterns**: Pre-defined account name variations (first in list is canonical)
- **fuzzy_threshold**: Minimum similarity percentage (default: 85%)

---

### 3. Usage in Data Loading: `src/etl/loader.py`

**Context**: When loading Excel data into the database

```python
class DataLoader:
    def __init__(self):
        self.normalizer = AccountNormalizer(
            patterns=config.get('account_normalization.patterns', []),
            fuzzy_threshold=config.get('account_normalization.fuzzy_threshold', 85)
        )
        self.account_cache = {}  # Cache for performance

    def _get_or_create_account(self, session, account_name, territory_id, **kwargs):
        # Normalize account name using fuzzy logic
        normalized_name = self.normalizer.normalize(account_name)

        # Check if account exists with this normalized name
        account = session.query(Account).filter(
            Account.normalized_name == normalized_name
        ).first()

        if not account:
            # Create new account
            account = Account(
                account_name=account_name,
                normalized_name=normalized_name,  # Stored for future matching
                territory_id=territory_id,
                **kwargs
            )
```

**Flow**:
1. Load Install Base data → Normalize account names → Create/find accounts
2. Load Opportunity data → Normalize account names → Link to same accounts
3. Load Projects data → Normalize customer names → Link to same accounts

**Result**: All data sources point to the **same Account record** despite name variations

---

### 4. Database Storage: `src/models/account.py`

```python
class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    account_name = Column(String)           # Original name from source
    normalized_name = Column(String, index=True)  # Fuzzy-matched canonical form
    territory_id = Column(String)

    # Relationships
    install_base_items = relationship("InstallBase")
    opportunities = relationship("Opportunity")
    projects = relationship("Project")
```

**Key Fields**:
- **account_name**: Original name as it appears in source data
- **normalized_name**: Cleaned, canonical form used for matching (indexed for performance)

---

## 📊 Algorithm: Levenshtein Distance

### What is Levenshtein Distance?

The minimum number of single-character edits (insertions, deletions, substitutions) needed to transform one string into another.

### Example Calculation

```
String 1: "Apple Inc"
String 2: "APPLE INC."

Steps:
1. Lowercase both: "apple inc" vs "apple inc."
2. Remove punctuation: "apple inc" vs "apple inc"
3. Levenshtein distance: 0 (exact match)
4. Similarity ratio: 100%
```

### Similarity Threshold

**Current Setting**: 85%

```
"Apple Inc"        vs "Apple Computer Inc"     → ~75% similarity → NO MATCH
"Applied Materials" vs "Applied Material"      → ~95% similarity → MATCH
"APPLE INC."       vs "apple inc"              → 100% similarity → MATCH
```

---

## 🔍 Where Fuzzy Logic is NOT Used (But Could Be)

### ❌ Current Gap: Product Name Matching

**Problem**: Install Base → LS_SKU mapping currently uses **keyword matching**

```python
# Current approach (in DATA_RELATIONSHIPS_ANALYSIS.md)
if "DL360" in product_name:
    product_family = "Servers"
```

**Could be improved with fuzzy logic**:
```python
# Potential fuzzy approach
similarity = fuzz.ratio("HP DL360p Gen8", "DL360 Server")
if similarity >= 80:
    product_family = "Servers"
```

### ❌ Current Gap: Service Name Matching

**Problem**: When recommending services, exact text matching is used

**Could benefit from fuzzy matching**:
- "Health Check" vs "Health Assessment"
- "Migration Service" vs "Data Migration"
- "Firmware Upgrade" vs "Firmware Update"

---

## 📈 Performance Considerations

### Current Optimization

1. **Pattern Pre-matching**
   - Known patterns checked first (O(1) lookup)
   - Fuzzy matching only if no exact pattern match

2. **Caching**
   - Account lookups cached during data loading
   - Prevents redundant fuzzy calculations

3. **Database Indexing**
   - `normalized_name` field is indexed
   - Fast lookups after initial normalization

### Performance Metrics

```python
# Typical performance (from fuzzywuzzy)
Simple comparison: ~0.0001 seconds
100 comparisons: ~0.01 seconds
1000 comparisons: ~0.1 seconds

# With caching (OneLead implementation)
First lookup: ~0.0001 seconds (fuzzy match)
Subsequent lookups: ~0.00001 seconds (cache hit)
```

---

## 🎛️ Configuration Guide

### Adjusting Fuzzy Threshold

**Location**: `config/config.yaml`

```yaml
account_normalization:
  fuzzy_threshold: 85  # Adjust this value
```

**Threshold Guidelines**:

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| **95-100** | Very strict - almost exact match only | High data quality, few variations |
| **85-94** | **Current setting** - moderate flexibility | Typical business names with variations |
| **70-84** | Loose - allows significant differences | Poor data quality, many typos |
| **<70** | Very loose - risk of false positives | Not recommended |

### Adding Known Patterns

**Location**: `config/config.yaml`

```yaml
account_normalization:
  patterns:
    - ["Canonical Name", "Variation 1", "Variation 2"]
    - ["Apple Inc", "APPLE INC.", "Apple Computer Inc"]
    - ["Microsoft Corporation", "MICROSOFT CORP", "MS Corp"]
```

**Best Practice**: First name in each list is the **canonical form**

---

## 🔬 Testing Fuzzy Logic

### Manual Test Script

```python
from src.utils.account_normalizer import AccountNormalizer

# Initialize
normalizer = AccountNormalizer(
    patterns=[
        ["Apple Inc", "APPLE INC.", "Apple Computer Inc"]
    ],
    fuzzy_threshold=85
)

# Test cases
test_names = [
    "Apple Inc",
    "APPLE INC.",
    "Apple Computer Inc",
    "apple inc",
    "Apple  Inc.",  # Extra space
]

for name in test_names:
    normalized = normalizer.normalize(name)
    print(f"{name:30} → {normalized}")

# Expected output:
# Apple Inc                      → apple inc
# APPLE INC.                     → apple inc
# Apple Computer Inc             → apple inc
# apple inc                      → apple inc
# Apple  Inc.                    → apple inc
```

---

## 🚀 Potential Enhancements

### 1. Product Matching (High Priority)

**Current State**: Keyword substring matching
**Proposed**: Fuzzy matching for Install Base → LS_SKU

```python
# Proposed enhancement
class ProductMatcher:
    def match_product_to_sku(self, product_name: str, sku_products: List[str]):
        best_match = None
        best_score = 0

        for sku_product in sku_products:
            score = fuzz.token_set_ratio(product_name, sku_product)
            if score > best_score and score >= 80:
                best_score = score
                best_match = sku_product

        return best_match, best_score
```

### 2. Opportunity Linkage Enhancement

**Use Case**: Match Opportunity names to Project descriptions

```python
# Find projects that might be related to an opportunity
def find_related_projects(opportunity_name: str, projects: List[Project]):
    matches = []
    for project in projects:
        score = fuzz.partial_ratio(opportunity_name, project.description)
        if score >= 75:
            matches.append((project, score))
    return sorted(matches, key=lambda x: x[1], reverse=True)
```

### 3. Customer Name Variants Discovery

**Use Case**: Automatically discover account name variations

```python
# Find all similar account names in dataset
def find_potential_duplicates(accounts: List[str], threshold=85):
    duplicates = []
    for i, acc1 in enumerate(accounts):
        for acc2 in accounts[i+1:]:
            score = fuzz.ratio(acc1, acc2)
            if score >= threshold:
                duplicates.append((acc1, acc2, score))
    return duplicates
```

---

## 📚 References

### Library Documentation
- **fuzzywuzzy**: https://github.com/seatgeek/fuzzywuzzy
- **python-Levenshtein**: https://github.com/ztane/python-Levenshtein

### Current Implementation Files
- `src/utils/account_normalizer.py:4` - Main implementation
- `src/etl/loader.py:16` - Usage in data loading
- `src/models/account.py:17` - Database storage
- `config/config.yaml:29-33` - Configuration

### Algorithm Types Used
- **fuzz.ratio()**: Levenshtein distance ratio (0-100)
- Higher score = more similar
- Case insensitive after normalization

---

## ❓ Common Questions

### Q: Why 85% threshold?
**A**: Balance between catching legitimate variations (Apple Inc vs APPLE INC.) while avoiding false positives (Apple Inc vs Amazon Inc).

### Q: Can I disable fuzzy matching?
**A**: Set `fuzzy_threshold: 100` for exact matching only, but this will create duplicate accounts.

### Q: How do I add a new account pattern?
**A**: Edit `config/config.yaml` and add to the `patterns` list. Restart the data loader.

### Q: What happens if no match is found?
**A**: A new account is created with the cleaned/normalized name as its canonical form.

### Q: Is fuzzy matching used for ST ID relationships?
**A**: **No**. ST ID uses exact integer matching (foreign key). Fuzzy logic only applies to text-based account names.

---

## ✅ Summary

| Aspect | Current Implementation |
|--------|----------------------|
| **Library** | fuzzywuzzy (Levenshtein distance) |
| **Use Case** | Account name normalization |
| **Threshold** | 85% similarity |
| **Location** | `src/utils/account_normalizer.py` |
| **Performance** | Cached for efficiency |
| **Configuration** | `config/config.yaml` |
| **Database Field** | `Account.normalized_name` (indexed) |
| **Status** | ✅ Production-ready |

**Key Benefit**: Prevents duplicate accounts across Install Base, Opportunity, and Project data sources despite naming variations.

---

**Related Documentation**:
- `DATA_RELATIONSHIPS_ANALYSIS.md` - Shows how normalized accounts link data
- `config/config.yaml` - Configuration settings
- `requirements.txt` - fuzzywuzzy dependency
