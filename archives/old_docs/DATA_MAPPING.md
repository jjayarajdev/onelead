# OneLead Data Mapping Documentation

## Overview

This document provides a comprehensive field-by-field mapping between Excel source files and the OneLead database schema. It details all transformations, data quality handling, and business logic applied during the ETL process.

---

## Table of Contents

1. [Source Files](#source-files)
2. [Database Schema](#database-schema)
3. [Mapping Details](#mapping-details)
   - [Install Base Mapping](#install-base-mapping)
   - [Opportunity Mapping](#opportunity-mapping)
   - [Project Mapping](#project-mapping)
   - [Services Mapping](#services-mapping)
   - [Service SKU Mapping](#service-sku-mapping)
   - [Account Consolidation](#account-consolidation)
4. [Data Transformations](#data-transformations)
5. [Derived Fields](#derived-fields)
6. [Data Quality Rules](#data-quality-rules)

---

## Source Files

### File 1: DataExportAug29th.xlsx
**Location:** `data/DataExportAug29th.xlsx`

**Sheets:**
- **Install Base** (63 records) - Hardware inventory with warranty/support status
- **Opportunity** (98 records) - Active sales opportunities
- **A&PS Project sample** (2,394 records) - Historical Advisory & Professional Services projects
- **Services** (286 records) - Available service catalog
- **Service Credits** - Not used in current implementation

### File 2: LS_SKU_for_Onelead.xlsx
**Location:** `data/LS_SKU_for_Onelead.xlsx`

**Sheets:**
- **Sheet2** - Product family to service SKU mappings

---

## Database Schema

### Tables Created

```
accounts                 - Customer/account master data
install_base            - Hardware inventory items
opportunities           - Sales pipeline
projects                - Historical project delivery
service_catalog         - Available services
service_sku_mappings    - Product-to-service mappings
leads                   - Generated sales leads (derived)
```

### Entity Relationships

```
Account (1) ──────── (M) InstallBase
   │
   ├──────────────── (M) Opportunity
   │
   ├──────────────── (M) Project
   │
   └──────────────── (M) Lead
```

---

## Mapping Details

### Install Base Mapping

#### Source: DataExportAug29th.xlsx → Sheet: "Install Base"

#### Field Mapping Table

| Excel Column Name                        | Database Field          | Type    | Transformation                           | Notes                                    |
|------------------------------------------|------------------------|---------|------------------------------------------|------------------------------------------|
| Serial_Number_Id                         | serial_number          | String  | `str(value)`                            | Unique identifier, indexed               |
| Product_Id                               | product_id             | String  | `str(value)`                            | HPE product SKU                          |
| Product_Name                             | product_name           | String  | `str(value)`                            | Full product name                        |
| Product_Platform_Description_Name        | product_platform       | String  | `str(value)`                            | Platform description                     |
| Line_Description_Name                    | line_description       | String  | `str(value)`                            | Product line                             |
| Business_Area_Description_Name           | business_area          | String  | `str(value)`                            | Business area (Compute, Storage, etc.)   |
| Legacy_Global_Business_Unit              | legacy_gbu             | String  | `str(value)`                            | Historical GBU code                      |
| Product_End_of_Life_Date                 | product_eol_date       | Date    | `_parse_date(value)`                    | See date parsing logic                   |
| Product_End_of_Service_Life_Date         | product_eos_date       | Date    | `_parse_date(value)`                    | See date parsing logic                   |
| Final_Service_Start_Date                 | service_start_date     | Date    | `_parse_date(value)`                    | See date parsing logic                   |
| Final_Service_End_Date                   | service_end_date       | Date    | `_parse_date(value)`                    | See date parsing logic                   |
| Support_Status                           | support_status         | String  | `str(value)`                            | Indexed for lead generation              |
| Service_Agreement_Id                     | service_agreement_id   | String  | `str(value)`                            | Contract reference                       |
| Final_Service_Source                     | service_source         | String  | `str(value)`                            | Source of service data                   |
| Account_Sales_Territory_Id               | territory_id           | String  | `str(value)`                            | Used for account lookup                  |
| Account_Sales_Territory_Id               | account_id (FK)        | Integer | `_get_or_create_account(value)`         | Creates/links to Account table           |
| *(Derived)*                              | product_family         | String  | `_extract_product_family()`             | Calculated: 3PAR, COMPUTE, etc.          |
| *(Derived)*                              | days_since_eol         | Integer | `_calculate_days_diff(eol_date)`        | Calculated: (today - eol_date).days      |
| *(Derived)*                              | days_since_expiry      | Integer | `_calculate_days_diff(service_end)`     | Calculated: (today - service_end).days   |
| *(Derived)*                              | risk_level             | String  | `_determine_risk_level()`               | Calculated: CRITICAL/HIGH/MEDIUM/LOW     |

#### Sample Data Flow

**Excel Input:**
```
Serial_Number_Id: USE3267F8N
Product_Id: 654081-B21
Product_Name: HP DL360p Gen8 8-SFF CTO Server
Product_Platform_Description_Name: Compute
Product_End_of_Life_Date: 2015-07-01
Support_Status: Expired Flex Support
Account_Sales_Territory_Id: 56088
```

**Database Output:**
```sql
INSERT INTO install_base (
    serial_number,
    product_id,
    product_name,
    product_platform,
    product_eol_date,
    support_status,
    territory_id,
    account_id,
    product_family,        -- DERIVED: "COMPUTE" (extracted from name)
    days_since_eol,        -- DERIVED: 3,748 days (as of 2025-10-09)
    days_since_expiry,     -- DERIVED: NULL (no service_end_date)
    risk_level            -- DERIVED: "HIGH" (expired + old)
) VALUES (
    'USE3267F8N',
    '654081-B21',
    'HP DL360p Gen8 8-SFF CTO Server',
    'Compute',
    '2015-07-01',
    'Expired Flex Support',
    '56088',
    1,                    -- FK to accounts table
    'COMPUTE',
    3748,
    NULL,
    'HIGH'
);
```

#### Transformation Functions

##### _parse_date(date_value)
**Purpose:** Handle multiple date formats from Excel

**Input Types Handled:**
- `pd.Timestamp` objects
- Python `datetime` objects
- Python `date` objects
- String dates (ISO format)
- `"(null)"`, `"null"`, `NaN` → `None`

**Logic:**
```python
def _parse_date(self, date_value) -> Optional[date]:
    # Handle nulls
    if pd.isna(date_value) or str(date_value).lower() in ['(null)', 'null', 'nan']:
        return None

    # Handle pandas Timestamp
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()

    # Handle datetime
    if isinstance(date_value, datetime):
        return date_value.date()

    # Handle date
    if isinstance(date_value, date):
        return date_value

    # Try to parse string
    try:
        return pd.to_datetime(date_value).date()
    except:
        return None
```

##### _extract_product_family(product_name, product_platform)
**Purpose:** Classify products into strategic families

**Logic:**
```python
def _extract_product_family(self, product_name: str, product_platform: str) -> str:
    text = f"{product_name} {product_platform}".lower()

    # Storage products (high priority)
    if '3par' in text: return '3PAR'
    if 'primera' in text: return 'PRIMERA'
    if 'alletra' in text: return 'ALLETRA'
    if 'nimble' in text: return 'NIMBLE'
    if 'msa' in text: return 'MSA'
    if 'storeonce' in text: return 'STOREONCE'
    if 'msl' in text: return 'MSL'

    # Compute products
    compute_indicators = ['dl', 'ml', 'bl', 'gen']
    for indicator in compute_indicators:
        if indicator in text:
            return 'COMPUTE'

    return 'OTHER'
```

**Examples:**
```
Input: "HP DL360p Gen8 8-SFF CTO Server", "Compute"
Output: "COMPUTE"  (contains 'dl' and 'gen')

Input: "HP 3PAR 7400 Storage Base", "Storage"
Output: "3PAR"  (contains '3par')

Input: "HP 8GB 2Rx4 PC3-10600R-9 Kit", "Server Storage & Inf"
Output: "OTHER"  (no matching indicators)
```

##### _determine_risk_level(support_status, days_since_eol, days_since_expiry)
**Purpose:** Assign urgency level to install base items

**Logic:**
```python
def _determine_risk_level(self, support_status: str, days_since_eol: Optional[int],
                          days_since_expiry: Optional[int]) -> str:
    if not support_status:
        return "UNKNOWN"

    support_status = str(support_status).lower()

    # CRITICAL: Very old equipment with expired support
    if 'expired' in support_status or 'uncovered' in support_status:
        if days_since_eol and days_since_eol > 1825:  # 5 years
            return "CRITICAL"
        if days_since_expiry and days_since_expiry > 180:  # 6 months
            return "HIGH"
        return "HIGH"

    return "MEDIUM"
```

**Examples:**
```
Input: support_status="Warranty Expired - Uncovered Box", days_since_eol=3748, days_since_expiry=NULL
Output: "CRITICAL"  (expired + >5 years past EOL)

Input: support_status="Expired Flex Support", days_since_eol=NULL, days_since_expiry=200
Output: "HIGH"  (expired + >180 days past service end)

Input: support_status="Active", days_since_eol=100, days_since_expiry=NULL
Output: "MEDIUM"  (not expired)
```

---

### Opportunity Mapping

#### Source: DataExportAug29th.xlsx → Sheet: "Opportunity"

#### Field Mapping Table

| Excel Column Name     | Database Field     | Type    | Transformation                  | Notes                          |
|-----------------------|-------------------|---------|----------------------------------|--------------------------------|
| HPE Opportunity ID    | opportunity_id    | String  | `str(value)`                    | Unique identifier, indexed     |
| Opportunity NAme      | opportunity_name  | String  | `str(value)`                    | Note: Typo in source column    |
| Product Line          | product_line      | String  | `str(value)`                    | Product line classification    |
| Account ST ID         | territory_id      | String  | `str(value)`                    | Territory identifier           |
| Account Name          | account_id (FK)   | Integer | `_get_or_create_account(name)`  | Creates/links to Account       |

#### Sample Data Flow

**Excel Input:**
```
HPE Opportunity ID: OPE-0016694761
Opportunity NAme: FY24Q3-RENEWAL ARUBA-Applied Materials, Inc.
Product Line: L5 - GL_Cloud Mgmt AAE
Account ST ID: 56180
Account Name: APPLIED MATERIALS, INC.
```

**Database Output:**
```sql
-- First, account is created/retrieved
INSERT INTO accounts (account_name, normalized_name, territory_id)
VALUES ('APPLIED MATERIALS, INC.', 'applied materials', '56180')
ON CONFLICT DO NOTHING;

-- Then opportunity is inserted
INSERT INTO opportunities (
    opportunity_id,
    opportunity_name,
    product_line,
    territory_id,
    account_id
) VALUES (
    'OPE-0016694761',
    'FY24Q3-RENEWAL ARUBA-Applied Materials, Inc.',
    'L5 - GL_Cloud Mgmt AAE',
    '56180',
    4  -- FK to accounts table
);
```

#### Account Consolidation Logic

**Function:** `_get_or_create_account(account_name, territory_id, ...)`

**Purpose:** Ensure one account record per customer, despite name variations

**Logic:**
```python
def _get_or_create_account(self, session, account_name: str, territory_id: str = None, **kwargs):
    # Handle missing/invalid names
    if not account_name or str(account_name).lower() in ['nan', 'null', '(null)', 'not available']:
        account_name = "Unknown Account"

    # Normalize account name
    normalized_name = self.normalizer.normalize(account_name)

    # Check cache (for performance)
    cache_key = f"{normalized_name}_{territory_id}"
    if cache_key in self.account_cache:
        return self.account_cache[cache_key]

    # Query database for existing account
    account = session.query(Account).filter(
        Account.normalized_name == normalized_name
    ).first()

    # Create if not exists
    if not account:
        account = Account(
            account_name=account_name,
            normalized_name=normalized_name,
            territory_id=territory_id,
            **kwargs
        )
        session.add(account)
        session.flush()  # Get ID without committing

    # Cache for future lookups
    self.account_cache[cache_key] = account
    return account
```

**Account Normalization Examples:**

```python
# Example 1: Case and punctuation differences
normalize("Apple Inc")          → "apple"
normalize("APPLE INC.")         → "apple"
normalize("Apple Computer Inc") → "apple computer"

# Example 2: Suffix removal
normalize("Applied Materials, Inc.")     → "applied materials"
normalize("APPLIED MATERIALS, INC.")     → "applied materials"
normalize("Applied Materials Corporation") → "applied materials"

# Example 3: Fuzzy matching
fuzz.ratio("apple", "apple computer") = 75%  → No match (< 85% threshold)
fuzz.ratio("apple inc", "apple inc.") = 97%  → Match (>= 85% threshold)
```

---

### Project Mapping

#### Source: DataExportAug29th.xlsx → Sheet: "A&PS Project sample"

#### Field Mapping Table

| Excel Column Name          | Database Field              | Type    | Transformation               | Notes                                  |
|----------------------------|----------------------------|---------|------------------------------|----------------------------------------|
| PRJ Siebel ID              | project_id                 | String  | `str(value)` or synthetic   | Handles duplicates/invalid IDs         |
| PRJ Description            | project_description        | String  | `str(value)`                | Project name/description               |
| PRJ Practice               | practice                   | String  | `str(value)`                | CLD & PLT, NTWK & CYB, AI & D          |
| PRJ Function               | function                   | String  | `str(value)`                | Project function code                  |
| PRJ Business Area          | business_area              | String  | `str(value)`                | Business area code                     |
| PRJ Status Description     | status                     | String  | `str(value)`                | CLSD, OPEN, etc.                       |
| PRJ Start Date             | start_date                 | Date    | `_parse_date(value)`        | Project start date                     |
| PRJ End Date               | end_date                   | Date    | `_parse_date(value)`        | Project end date                       |
| PRJ Days                   | project_length_days        | Integer | `int(value)` or None        | Project duration in days               |
| PRJ Size                   | size_category              | String  | `str(value)`                | <$50k, $50k-$100k, etc.                |
| Labor Cost                 | labor_cost                 | Float   | `_parse_float(value)`       | Handles "Yes"/"No" → None              |
| 3rd Party Svc Cost         | third_party_service_cost   | Float   | `_parse_float(value)`       | Safe float conversion                  |
| 3rd Party Mat Cost         | third_party_material_cost  | Float   | `_parse_float(value)`       | Safe float conversion                  |
| PRJ Customer               | account_id (FK)            | Integer | `_get_or_create_account()`  | Creates/links to Account               |
| PRJ Customer ID            | *used for account lookup*  | String  | Passed to account creation  | External customer ID                   |
| Country                    | country                    | String  | `str(value)`                | Project country                        |
| PRJ Region                 | region                     | String  | `str(value)`                | Geographic region                      |

#### Special Handling: Invalid Project IDs

**Problem:** Source data contains duplicate and placeholder project IDs:
- `"#"` (appears multiple times)
- `"NOT AVAILABLE"` (appears multiple times)
- `"NOT AUAILABLE"` (typo, appears multiple times)

**Solution:**
```python
# Get project ID and validate
project_id = str(row.get('PRJ Siebel ID'))

# Check for invalid/placeholder project IDs
invalid_ids = ['#', 'nan', 'None', '']
if (not project_id or
    project_id in invalid_ids or
    'NOT AV' in project_id.upper() or  # Catches "NOT AVAILABLE" and typos
    len(project_id) < 3):
    # Generate unique synthetic ID
    project_id = f"UNKNOWN_PRJ_{idx}"  # idx = row index from DataFrame
```

**Examples:**
```
Input: PRJ Siebel ID = "#"
Output: project_id = "UNKNOWN_PRJ_123"

Input: PRJ Siebel ID = "NOT AVAILABLE"
Output: project_id = "UNKNOWN_PRJ_456"

Input: PRJ Siebel ID = "JP3-K1447"
Output: project_id = "JP3-K1447"  (valid, kept as-is)
```

**Rationale:**
- **Data Preservation:** Keep all historical project records
- **Uniqueness:** Ensure database integrity (no duplicate IDs)
- **Traceability:** Can trace back to source row via index

#### Financial Data Handling

**Function:** `_parse_float(value)`

**Purpose:** Safely convert financial fields that may contain non-numeric values

**Logic:**
```python
def _parse_float(self, value) -> Optional[float]:
    """Safely parse float value."""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None  # Graceful degradation
```

**Examples:**
```
Input: Labor Cost = 150000.50
Output: 150000.50

Input: Labor Cost = "Yes"
Output: None  (invalid, set to NULL)

Input: Labor Cost = NaN
Output: None

Input: Labor Cost = ""
Output: None
```

#### Sample Data Flow

**Excel Input:**
```
PRJ Siebel ID: JP3-K1447
PRJ Description: FY18 Q3 FSIP-3 認証案件少額セリング活動
PRJ Practice: CLD & PLT
PRJ Business Area: G400
PRJ Status Description: CLSD
PRJ Start Date: 2018-06-05
PRJ End Date: 2018-09-03
PRJ Days: 90
PRJ Size: <$50k
Labor Cost: Yes  (invalid)
PRJ Customer: 東京海上日動火災保険(株)
Country: Japan
```

**Database Output:**
```sql
-- Account created/retrieved (Japanese name preserved)
INSERT INTO accounts (account_name, normalized_name, territory_id)
VALUES ('東京海上日動火災保険(株)', '東京海上日動火災保険', NULL);

-- Project inserted
INSERT INTO projects (
    project_id,
    project_description,
    practice,
    business_area,
    status,
    start_date,
    end_date,
    project_length_days,
    size_category,
    labor_cost,          -- NULL (invalid "Yes")
    account_id,
    country,
    region
) VALUES (
    'JP3-K1447',
    'FY18 Q3 FSIP-3 認証案件少額セリング活動',
    'CLD & PLT',
    'G400',
    'CLSD',
    '2018-06-05',
    '2018-09-03',
    90,
    '<$50k',
    NULL,               -- Converted from "Yes"
    31,
    'Japan',
    'Japan'
);
```

---

### Services Mapping

#### Source: DataExportAug29th.xlsx → Sheet: "Services"

#### Field Mapping Table

| Excel Column Name | Database Field       | Type   | Transformation           | Notes                               |
|-------------------|---------------------|--------|--------------------------|-------------------------------------|
| Practice          | practice            | String | `str(value)` or None    | May be None (inherited from above)  |
| Sub-Practice      | sub_practice        | String | `str(value)` or None    | May be None (inherited from above)  |
| Services          | service_name        | String | `str(value)`            | Required, skipped if None           |
| *(Derived)*       | service_category    | String | `_categorize_service()` | Calculated category                 |

#### Service Categorization Logic

**Function:** `_categorize_service(service_name)`

**Purpose:** Classify services into standard categories

**Logic:**
```python
def _categorize_service(self, service_name: str) -> str:
    service_lower = service_name.lower()

    if 'health' in service_lower or 'assessment' in service_lower:
        return "Health Check"
    elif 'migration' in service_lower:
        return "Migration"
    elif 'design' in service_lower or 'implementation' in service_lower:
        return "Design & Implementation"
    elif 'optimization' in service_lower or 'performance' in service_lower:
        return "Optimization"
    elif 'upgrade' in service_lower:
        return "Upgrade"
    else:
        return "Other"
```

**Examples:**
```
Input: "Compute environment analysis services"
Output: "Other"

Input: "Performance and Firmware Analysis of the existing environment"
Output: "Optimization"  (contains 'performance')

Input: "Migration to HPE Compute Readiness Assessment Service"
Output: "Migration"  (contains 'migration')

Input: "Deploy and Configure HPE Compute Hardware"
Output: "Design & Implementation"  (contains 'implementation')
```

#### Special Handling: Hierarchical Data

**Problem:** Excel data has hierarchical structure where Practice/Sub-Practice span multiple rows:

```
Practice          | Sub-Practice                    | Services
------------------------------------------------------------------
Hybrid Cloud      | Compute, CS, HCI, OneView       | Compute environment analysis
                  |                                  | Performance and Firmware Analysis
                  |                                  | HPE Compute Transformation
                  | Storage (3PAR, Primera, etc.)   | Storage Health Check
                  |                                  | Storage Migration Services
```

**Solution:**
```python
for idx, row in df.iterrows():
    practice = row.get('Practice')
    sub_practice = row.get('Sub-Practice')
    service_name = row.get('Services')

    # Skip empty rows
    if pd.isna(service_name):
        continue

    # Use last non-null practice/sub-practice (inherited from above)
    service = ServiceCatalog(
        practice=str(practice) if pd.notna(practice) else None,
        sub_practice=str(sub_practice) if pd.notna(sub_practice) else None,
        service_name=str(service_name),
        service_category=self._categorize_service(str(service_name))
    )
```

---

### Service SKU Mapping

#### Source: LS_SKU_for_Onelead.xlsx → Sheet: "Sheet2"

#### Field Mapping Table

| Excel Column Position | Database Field      | Type   | Transformation                 | Notes                                  |
|----------------------|---------------------|--------|--------------------------------|----------------------------------------|
| Column D (index 3)   | product_family      | String | `str(value)`                  | 3PAR, Primera, Alletra, etc.           |
| Column D (index 3)   | product_category    | String | Context from category row     | "Storage SW" or "Storage HW"           |
| Columns E+ (index 4+)| service_type        | String | `_parse_service_sku()[type]`  | Text before parentheses                |
| Columns E+ (index 4+)| service_sku         | String | `_parse_service_sku()[sku]`   | SKU codes in parentheses               |

#### Data Structure in Excel

**Excel Layout:**
```
Row 1-3: Headers (skipped)
Row 4:   "Product" header
Row 5:   "Storage SW" (category)
Row 6:   "3PAR" | "OS upgrade (HM002A1)" | "Health Check (H9Q53AC)" | ...
Row 7:   "Primera" | "OS upgrade (HM002A1)" | "Migration (HA124A1#5Q3)" | ...
...
Row 15:  "Storage HW" (category)
Row 16:  "3PAR" | "Install & Startup" | "HW upgrade" | ...
```

#### Parsing Logic

**Function:** `_parse_service_sku(product_family, category, service_text)`

**Purpose:** Extract service type and SKU codes from text

**Logic:**
```python
def _parse_service_sku(self, product_family: str, category: str,
                       service_text: str) -> Optional[ServiceSKUMapping]:
    import re

    # Extract SKU codes in parentheses (may be multiple, #-separated)
    sku_match = re.findall(r'\(([A-Z0-9#]+)\)', service_text)
    skus = ','.join(sku_match) if sku_match else None

    # Extract service type (text before parentheses)
    service_type = re.sub(r'\s*\([^)]+\)', '', service_text).strip()

    if service_type:
        return ServiceSKUMapping(
            product_family=product_family,
            product_category=category,
            service_type=service_type,
            service_sku=skus
        )

    return None
```

**Examples:**

```
Input: "OS upgrade (HM002A1/HM002AE/HM002AC)"
Output:
  service_type = "OS upgrade"
  service_sku = "HM002A1,HM002AE,HM002AC"

Input: "Health Check (H9Q53AC)"
Output:
  service_type = "Health Check"
  service_sku = "H9Q53AC"

Input: "Remote Copy configuration (HA124A1#5QV/HA124A1#5Y8/HA124A1#5U2)"
Output:
  service_type = "Remote Copy configuration"
  service_sku = "HA124A1#5QV,HA124A1#5Y8,HA124A1#5U2"

Input: "Install & Startup"  (no SKU)
Output:
  service_type = "Install & Startup"
  service_sku = NULL
```

#### Row Processing Logic

```python
current_category = None
current_product = None

for idx, row in df.iloc[4:].iterrows():  # Skip first 4 rows (headers)
    product_col = row.iloc[3]  # Column D (product family)

    # Check if this is a category row
    if pd.notna(product_col):
        product_str = str(product_col).strip()

        # Category markers
        if 'Storage SW' in product_str:
            current_category = "Storage SW"
            continue
        elif 'Storage HW' in product_str:
            current_category = "Storage HW"
            continue

        # Product family row
        if product_str and product_str not in ['Product', 'NaN']:
            current_product = product_str

    # Parse service columns (starting from column 4)
    if current_product and current_category:
        for col_idx in range(4, len(row)):
            service_text = row.iloc[col_idx]
            if pd.notna(service_text) and str(service_text).strip():
                mapping = self._parse_service_sku(
                    current_product,
                    current_category,
                    str(service_text)
                )
                if mapping:
                    session.add(mapping)
```

#### Sample Data Flow

**Excel Input (Row 6):**
```
Column D: "3PAR"
Column E: "OS upgrade (HM002A1/HM002AE/HM002AC)"
Column F: "Health Check (H9Q53AC)"
Column G: "Performance Analysis (HM2P6A1#001)"
Context: current_category = "Storage SW"
```

**Database Output:**
```sql
INSERT INTO service_sku_mappings (product_family, product_category, service_type, service_sku)
VALUES
    ('3PAR', 'Storage SW', 'OS upgrade', 'HM002A1,HM002AE,HM002AC'),
    ('3PAR', 'Storage SW', 'Health Check', 'H9Q53AC'),
    ('3PAR', 'Storage SW', 'Performance Analysis', 'HM2P6A1#001');
```

---

### Account Consolidation

#### The Account Problem

**Challenge:** Multiple data sources reference accounts differently:
- Install Base uses territory IDs (e.g., "56088")
- Opportunities use account names (e.g., "Apple Inc")
- Projects use various account names (sometimes in Japanese)

**Goal:** Create single unified account record per customer

#### Consolidation Strategy

**Step 1: Territory-Based Grouping**
```
All install base items with territory_id="56088" → Account #1
All install base items with territory_id="56180" → Account #2
```

**Step 2: Name-Based Enrichment**
```
Opportunities with Account Name="Apple Inc" + Territory="56088"
→ Updates Account #1 name from "56088" to "Apple Inc"
```

**Step 3: Normalization**
```
"Apple Inc" → normalized_name = "apple"
"APPLE INC." → normalized_name = "apple"
→ Both map to same account
```

#### Account Table Structure

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id VARCHAR,           -- External ID (if available)
    account_name VARCHAR NOT NULL, -- Display name
    normalized_name VARCHAR,       -- For matching (indexed)
    territory_id VARCHAR,          -- Territory identifier
    industry_code VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_account_normalized ON accounts(normalized_name);
CREATE INDEX idx_account_territory ON accounts(territory_id);
```

#### Account Lookup Flow

**Scenario 1: Install Base Record**
```python
# Input
territory_id = "56088"
account_name = "56088"  # No real name available

# Processing
account = _get_or_create_account(
    session,
    account_name="56088",      # Use territory as name initially
    territory_id="56088"
)

# Database
→ Creates account with:
    account_name = "56088"
    normalized_name = "56088"
    territory_id = "56088"
```

**Scenario 2: Opportunity Record (Same Territory)**
```python
# Input
territory_id = "56088"
account_name = "Apple Inc"

# Processing
normalized = normalize("Apple Inc")  # → "apple"

# Check for existing account
existing = query(Account).filter(
    normalized_name == "apple"
).first()

if not existing:
    # Check by territory
    existing = query(Account).filter(
        territory_id == "56088"
    ).first()

    if existing:
        # Update with real name
        existing.account_name = "Apple Inc"
        existing.normalized_name = "apple"

# Result
→ Account #1 updated:
    account_name = "Apple Inc" (was "56088")
    normalized_name = "apple" (was "56088")
    territory_id = "56088"
```

**Scenario 3: Project Record (Fuzzy Match)**
```python
# Input
account_name = "Apple Computer Inc"
territory_id = None

# Processing
normalized = normalize("Apple Computer Inc")  # → "apple computer"

# Check fuzzy match against existing accounts
for existing_account in all_accounts:
    score = fuzz.ratio("apple computer", existing_account.normalized_name)
    if score >= 85:
        # Match found!
        return existing_account

# If normalized="apple computer" and existing normalized="apple"
# fuzz.ratio("apple computer", "apple") = 75% → No match

# Create new account
→ Creates separate account (not enough similarity)
```

#### Territory to Account Name Mapping

**Discovered Mappings (from Opportunities data):**

```yaml
territory_mapping:
  "56088": "Apple Inc"
  "56160": "Antofagasta Minerals S.A."
  "56166": "Applied Computer Solutions"
  "56180": "APPLIED MATERIALS, INC."
  "56322": "Analog Devices"
  "56396": "ARAMARK SERVICES, INC."
  "56623": "Franklin Baystate Medical Center"
  "56769": "Baltimore City Public School Systems (inc)"
```

**Usage:**
```python
# In dashboard
def format_account(account):
    if account.account_name.isdigit():  # Just a territory ID
        territory_map = config.get('territory_mapping')
        if account.account_name in territory_map:
            return territory_map[account.account_name]
        else:
            return f"Territory {account.account_name}"
    else:
        return account.account_name
```

---

## Data Transformations

### Summary of All Transformations

| Transformation            | Input                          | Output                           | Purpose                                  |
|---------------------------|--------------------------------|----------------------------------|------------------------------------------|
| Date Parsing              | Multiple formats, nulls        | `date` or `None`                | Standardize date fields                  |
| Float Parsing             | Numbers, "Yes", nulls          | `float` or `None`               | Handle invalid financial data            |
| Account Normalization     | "Apple Inc", "APPLE INC."      | "apple"                         | Consolidate account variations           |
| Product Family Extraction | "HP DL360p Gen8..."           | "COMPUTE"                       | Classify products strategically          |
| Risk Level Calculation    | Status + dates                 | CRITICAL/HIGH/MEDIUM/LOW        | Prioritize renewal opportunities         |
| Days Calculation          | Date difference                | Integer (days)                  | Measure urgency                          |
| Service Categorization    | Free text service name         | "Health Check", "Migration"     | Group services                           |
| SKU Extraction            | "OS upgrade (HM002A1)"        | type="OS upgrade", sku="HM002A1"| Parse service SKU data                   |
| Project ID Validation     | "#", "NOT AVAILABLE"           | "UNKNOWN_PRJ_123"               | Handle invalid IDs                       |

---

## Derived Fields

### Fields Calculated at ETL Time

#### Install Base Derived Fields

**1. product_family**
- **Source:** Derived from `product_name` + `product_platform`
- **Logic:** Pattern matching (see _extract_product_family)
- **Values:** 3PAR, PRIMERA, ALLETRA, NIMBLE, MSA, STOREONCE, MSL, COMPUTE, OTHER
- **Purpose:** Service recommendation, strategic segmentation

**2. days_since_eol**
- **Source:** Calculated from `product_eol_date`
- **Logic:** `(today - product_eol_date).days`
- **Type:** Integer
- **Purpose:** Hardware refresh lead generation, urgency scoring

**3. days_since_expiry**
- **Source:** Calculated from `service_end_date`
- **Logic:** `(today - service_end_date).days`
- **Type:** Integer
- **Purpose:** Renewal lead generation, urgency scoring

**4. risk_level**
- **Source:** Derived from `support_status`, `days_since_eol`, `days_since_expiry`
- **Logic:** See _determine_risk_level()
- **Values:** CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN
- **Purpose:** Lead filtering, dashboard KPIs

#### Service Catalog Derived Fields

**1. service_category**
- **Source:** Derived from `service_name`
- **Logic:** Keyword matching (health, migration, design, etc.)
- **Values:** Health Check, Migration, Design & Implementation, Optimization, Upgrade, Other
- **Purpose:** Service classification, reporting

#### Account Derived Fields

**1. normalized_name**
- **Source:** Derived from `account_name`
- **Logic:** Remove punctuation, suffixes, lowercase, trim
- **Type:** String (indexed)
- **Purpose:** Fuzzy matching, duplicate detection

---

## Data Quality Rules

### Null Handling

| Field Type       | Null Strategy           | Example                                    |
|------------------|-------------------------|--------------------------------------------|
| Required String  | Use placeholder         | account_name=NULL → "Unknown Account"      |
| Optional String  | Allow NULL              | service_sku=NULL → NULL                    |
| Date             | Allow NULL              | product_eol_date="(null)" → NULL           |
| Numeric          | Allow NULL              | labor_cost="Yes" → NULL                    |
| Foreign Key      | Create default          | account_id=NULL → Create "Unknown Account" |

### Duplicate Handling

| Entity        | Duplicate Strategy                           | Example                                           |
|---------------|----------------------------------------------|---------------------------------------------------|
| Install Base  | Check serial_number, skip if exists          | S/N "USE3267F8N" already exists → skip            |
| Opportunity   | Check opportunity_id, skip if exists         | "OPE-0016694761" already exists → skip            |
| Project       | Generate synthetic ID for invalid duplicates | project_id="#" (duplicate) → "UNKNOWN_PRJ_123"    |
| Account       | Fuzzy match on normalized_name               | "Apple Inc" matches "APPLE INC." → reuse          |
| Service       | Allow duplicates (different practices)       | Same service name in different practices → both   |

### Invalid Data Handling

| Scenario                  | Handling                                | Rationale                                    |
|---------------------------|-----------------------------------------|----------------------------------------------|
| Invalid date format       | Set to NULL                            | Don't block record for bad date              |
| Non-numeric financial     | Set to NULL                            | Preserve record, lose invalid value          |
| Empty/placeholder ID      | Generate synthetic ID                  | Maintain referential integrity               |
| Missing account name      | Use "Unknown Account"                  | Ensure all records have account              |
| Unicode encoding errors   | Preserve UTF-8 (Japanese, etc.)        | Support international data                   |

### Data Validation Rules

**At Load Time:**
```python
# Serial numbers must be unique
assert install_base.serial_number is not None
assert install_base.serial_number != ""

# Opportunity IDs must be unique
assert opportunity.opportunity_id is not None

# Account must exist or be creatable
assert account_name is not None or territory_id is not None

# Dates must be valid or NULL
assert isinstance(date_field, (date, None))
```

**At Query Time:**
```python
# Only active leads
leads = query(Lead).filter(Lead.is_active == True)

# Only high-risk install base
high_risk = query(InstallBase).filter(
    InstallBase.risk_level.in_(['CRITICAL', 'HIGH'])
)
```

---

## ETL Performance Metrics

### Load Statistics (Actual)

```
Data Source: DataExportAug29th.xlsx + LS_SKU_for_Onelead.xlsx
Load Time: ~15-20 seconds
Database Size: ~800 KB

Records Loaded:
  ✓ 63 install base items
  ✓ 98 opportunities
  ✓ 2,394 projects
  ✓ 286 services
  ✓ Service SKU mappings (variable)
  ✓ ~30 unique accounts (consolidated from variations)

Data Quality:
  - 0 records rejected
  - ~50 invalid financial values converted to NULL
  - ~20 invalid project IDs replaced with synthetic IDs
  - 100% records preserved
```

### Caching Strategy

**Account Lookup Cache:**
```python
self.account_cache = {}  # In-memory cache

# First lookup: Database query
account = query(Account).filter(...)  # 5-10ms

# Cache it
self.account_cache[cache_key] = account

# Subsequent lookups: Cache hit
account = self.account_cache[cache_key]  # <1ms
```

**Impact:**
- Install base loading: 63 records × ~10 cache hits each = ~630 avoided DB queries
- Speed improvement: ~5x faster ETL

---

## Appendix: Complete Data Flow Example

### End-to-End: Install Base Record to Lead

**Step 1: Excel Source**
```
File: DataExportAug29th.xlsx, Sheet: "Install Base", Row: 2
---------------------------------------------------
Serial_Number_Id: USE3267F8N
Product_Id: 654081-B21
Product_Name: HP DL360p Gen8 8-SFF CTO Server
Product_Platform_Description_Name: Compute
Business_Area_Description_Name: x86 Premium and Scale-up Rack
Product_End_of_Life_Date: 2015-07-01
Support_Status: Expired Flex Support
Service_Agreement_Id: 104164014992
Account_Sales_Territory_Id: 56088
```

**Step 2: ETL Processing**
```python
# Parse dates
eol_date = _parse_date("2015-07-01")  # → date(2015, 7, 1)

# Calculate derived fields
days_since_eol = (date.today() - eol_date).days  # → 3,748 days
product_family = _extract_product_family("HP DL360p Gen8...", "Compute")  # → "COMPUTE"
risk_level = _determine_risk_level("Expired Flex Support", 3748, None)  # → "CRITICAL"

# Get/create account
account = _get_or_create_account(session, "56088", "56088")  # → Account #1
```

**Step 3: Database Insert (install_base table)**
```sql
INSERT INTO install_base (
    serial_number, product_id, product_name, product_platform,
    business_area, product_eol_date, support_status, service_agreement_id,
    territory_id, account_id,
    product_family, days_since_eol, risk_level
) VALUES (
    'USE3267F8N', '654081-B21', 'HP DL360p Gen8 8-SFF CTO Server', 'Compute',
    'x86 Premium and Scale-up Rack', '2015-07-01', 'Expired Flex Support', '104164014992',
    '56088', 1,
    'COMPUTE', 3748, 'CRITICAL'
);
```

**Step 4: Lead Generation (generate_leads.py)**
```python
# Lead generator scans install base
generator = LeadGenerator(session)

# Finds this record (CRITICAL risk + expired support)
if item.risk_level in ['CRITICAL', 'HIGH'] and 'Expired' in item.support_status:
    lead = Lead(
        lead_type='Renewal - Expired Support',
        priority='CRITICAL',
        title=f"Support Renewal: {item.product_name}",
        description=f"Support expired for {item.product_name} (S/N: {item.serial_number}). "
                   f"Status: {item.support_status}. EOL Date: {item.product_eol_date}.",
        recommended_action=f"Contact account to renew support contract. "
                         f"Product has been without support for {item.days_since_expiry or 0} days.",
        account_id=item.account_id,
        install_base_id=item.id,
        territory_id=item.territory_id,
        lead_status='New'
    )
    session.add(lead)
```

**Step 5: Lead Scoring (generate_leads.py)**
```python
scorer = LeadScorer(session)

# Calculate scores
urgency = 50 + 30 (>5 years EOL) + 0 (no expiry date) = 80
value = 40 + 0 (no estimated value) + 0 (small install base) = 40
propensity = 30 + 0 (no open opps) + 0 (no projects) = 30
strategic_fit = 50 + 25 (COMPUTE family) + 5 (renewal type) = 80

# Weighted score
score = (80 * 0.35) + (40 * 0.30) + (30 * 0.20) + (80 * 0.15)
      = 28 + 12 + 6 + 12
      = 58

# Assign priority
priority = 'MEDIUM'  # (score 58 is between 40-59)
```

**Step 6: Database Update (leads table)**
```sql
UPDATE leads SET
    urgency_score = 80,
    value_score = 40,
    propensity_score = 30,
    strategic_fit_score = 80,
    score = 58,
    priority = 'MEDIUM'
WHERE id = 123;
```

**Step 7: Dashboard Display**
```
Lead Queue → Filter: Renewal Leads, Priority: MEDIUM

[MEDIUM] Support Renewal: HP DL360p Gen8 8-SFF CTO Server
Score: 58.0

Account: Territory 56088
Territory: 56088
Type: Renewal - Expired Support
Status: New

Description: Support expired for HP DL360p Gen8 8-SFF CTO Server
(S/N: USE3267F8N). Status: Expired Flex Support. EOL Date: 2015-07-01.

Recommended Action: Contact account to renew support contract.
Product has been without support for 0 days.

Score Breakdown:
- Urgency: 80.0
- Value: 40.0
- Propensity: 30.0
- Strategic Fit: 80.0
```

---

## Document Maintenance

**Version:** 1.0
**Last Updated:** 2025-10-09
**Maintained By:** OneLead Development Team

**Change Log:**
- 2025-10-09: Initial documentation created
- Future: Update as schema evolves

**Related Documents:**
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Architecture and design rationale
- [README.md](README.md) - System overview and user guide
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
