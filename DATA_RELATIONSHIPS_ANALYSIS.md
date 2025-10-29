# OneLead - Complete Data Relationships & Integration Analysis

**Document Version**: 1.0
**Last Updated**: October 29, 2025
**Author**: Data Analysis Team
**Status**: ✅ Production Reference

---

## 📋 Executive Summary

This document provides a comprehensive analysis of data relationships within the OneLead system, covering:
- Excel file structure and content analysis
- Database relationships and foreign keys
- Integration patterns and mapping logic
- Practical use cases and workflows

### Key Findings

✅ **Discovered 3 major data relationships:**
1. **Install Base ↔ Opportunity** (Direct FK via Account_Sales_Territory_Id)
2. **Opportunity → A&PS Project** (Direct FK via HPE Opportunity ID → PRJ Siebel ID)
3. **A&PS Project → Services** (Conceptual mapping via Practice codes)

✅ **LS_SKU mapping table** serves as the recommendation engine connecting products to services

✅ **47% of A&PS projects** have direct links to originating opportunities

---

## 📊 Data Sources Overview

### 1. DataExportAug29th.xlsx (628KB)

Comprehensive customer data export with **5 sheets**:

#### Sheet 1: Install Base (63 records)
**Purpose**: Track deployed HPE hardware at customer sites

**Key Fields**:
- `Serial_Number_Id` - Hardware serial number (PK)
- `Product_Id` - Product identifier
- `Product_Name` - Product description
- `Account_Sales_Territory_Id` - Customer account ID (FK)
- `Business_Area_Description_Name` - Product category
- `Support_Status` - Warranty/support status
- `Product_End_of_Life_Date` - EOL date
- `Product_End_of_Service_Life_Date` - EOSL date
- `Final_Service_Start_Date` - Current service contract start
- `Final_Service_End_Date` - Current service contract end

**Business Areas**:
- WLAN HW: 37 assets (Aruba access points)
- Server Storage & Inf: 17 assets
- x86 Premium and Scale-up Rack: 7 assets
- C-Class Units & Enclosures: 2 assets

**Support Status Distribution**:
- Active Warranty: 33 assets
- Warranty Expired - Uncovered Box: 20 assets
- Expired Flex Support: 6 assets
- Expired Fixed Support: 4 assets

#### Sheet 2: Opportunity (98 records)
**Purpose**: Track active sales pipeline

**Key Fields**:
- `HPE Opportunity ID` - Unique opportunity identifier (PK, Format: OPE-XXXXXXXXXX)
- `Opportunity NAme` - Opportunity description
- `Account ST ID` - Customer account ID (FK → Install Base)
- `Account Name` - Customer name
- `Product Line` - Sales product line

**Top Product Lines**:
- SY - x86 Premium and Scale-up Rack: 12 opportunities
- VR - WLAN HW Svcs: 10 opportunities
- V3 - Ntwk Mngmt Svcs: 8 opportunities
- HA - Integrated Platforms: 7 opportunities
- 96 - Industry Standard Servers Support: 6 opportunities

**Account Coverage**:
- 8 unique accounts with opportunities
- 8 of 10 Install Base accounts have active opportunities (80% coverage)

#### Sheet 3: A&PS Project sample (2,394 records)
**Purpose**: Historical Advisory & Professional Services project data

**Key Fields**:
- `Project` - Project ID (PK)
- `PRJ Siebel ID` - Originating opportunity ID (FK, Format: OPE-XXXXXXXXXX)
- `PRJ Customer` - Customer name
- `PRJ Customer ID` - Customer identifier
- `Account ST Name` - Account sales territory name
- `PRJ Practice` - Service practice area
- `PRJ Business Area` - Business area code
- `PRJ Start Date` - Project start date
- `PRJ End Date` - Project end date
- `PRJ Status Description` - Project status
- `PRJ Description` - Project description
- `Health` - Project health indicator

**Practice Distribution**:
- CLD & PLT (Cloud & Platform): 1,710 projects (71%)
- NTWK & CYB (Network & Cyber): 384 projects (16%)
- AI & D (AI & Data): 288 projects (12%)
- Other: 12 projects (1%)

**Opportunity Linkage**:
- **1,117 projects (47%)** have Opportunity IDs in PRJ Siebel ID field
- **1,277 projects (53%)** have no opportunity link (older projects)

**Project Duration**:
- Projects WITH opportunity link: 850 days average
- Projects WITHOUT opportunity link: 162 days average

#### Sheet 4: Services (286 records)
**Purpose**: Service catalog organized by practice area

**Key Fields**:
- `Practice` - Practice category
- `Sub-Practice` - Sub-category
- `Services` - Service name

**Practice Categories**:
- Hybrid Cloud Consulting: 5 sub-practices
- Hybrid Cloud Engineering: 11 sub-practices
- Data, AI & IOT: 7 sub-practices

#### Sheet 5: Service Credits (1,384 records)
**Purpose**: Track prepaid service credit balances

**Key Fields**:
- `ProjectID` - Project identifier
- `ProjectName` - Project name
- `PracticeName` - Practice area
- `PurchasedCredits` - Total credits purchased
- `ConvertedCredits` - Credits converted to projects
- `DeliveredCredits` - Credits consumed by delivery
- `ConvertedNotDeliveredCredits` - Converted but not yet delivered
- `ActiveCredits` - Available unused credits
- `ExpiryInDays` - Days until expiration
- `ContractEndDate` - Contract end date

**Credit Statistics**:
- Total Purchased: 650 credits
- Total Delivered: 320 credits
- Total Active (unused): 320 credits
- Utilization Rate: 49%

---

### 2. LS_SKU_for_Onelead.xlsx (13KB)

**Purpose**: Product-to-Service mapping reference table (Recommendation Engine)

**Structure**:
- **32 product types** across 6 categories
- **138 product-service combinations**
- **HPE SKU codes** included (e.g., HM002A1, H9Q53AC)

**Categories & Products**:

#### Storage SW (8 products)
- 3PAR (6 services)
- Primera (5 services)
- Alletra (5 services)
- Alletra MP (4 services)
- Nimble (1 service)
- MSA (3 services)
- StoreOnce (6 services)
- MSL (3 services)

#### Storage HW (7 products)
- 3PAR (3 services)
- Primera (3 services)
- Alletra (3 services)
- Alletra MP (3 services)
- Nimble (2 services)
- MSA (1 service)
- StoreOnce (2 services)

#### Compute (3 products)
- Servers (5 services)
- Synergy (6 services)
- C7000 (3 services)

#### Switches (2 products)
- Networking (4 services)
- SAN (4 services)

#### Converged Systems (4 products)
- Linux (All Flavour) (6 services)
- Cluster (SG, SUSE, RHEL) (6 services)
- SAP HANA (6 services)
- Converged Systems (3 services)

#### HCI (8 products)
- SimpliVity (8 services)
- Nimble dHCI (7 services)
- Nutanix (6 services)
- Azure HCI (4 services)
- Plus 4 SKU reference entries

**Sample Service Mappings**:

| Product | Category | Services Available | Example SKUs |
|---------|----------|-------------------|--------------|
| 3PAR | Storage SW | OS upgrade, Health Check, Performance Analysis, Remote Copy config, File Persona, Data Optimization | HM002A1, H9Q53AC, HM2P6A1#001, HA124A1#5QV |
| Servers | Compute | Install & Startup, OS deployment, Health Check, Firmware upgrade, OneView config | HL997A1, H6K67A1 |
| SimpliVity | HCI | Install & Startup, Firmware upgrade, Health Check, Rapid DR, StoreOnce Integration, Expansion, Resiliency Test, Workload Migration | N/A |

---

## 🔗 Complete Relationship Map

### Discovered Relationships

```
┌──────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA INTEGRATION FLOW                    │
└──────────────────────────────────────────────────────────────────────┘

1. INSTALL BASE                         LS_SKU REFERENCE TABLE
   ─────────────────                    ────────────────────────
   Account ST ID (PK)        ┌────────> 32 Products
   Product Name              │          6 Categories
   Business Area             │          138 Service mappings
   Support Status            │          HPE SKU codes
   EOL/EOSL dates           │
                            │
        │                   │ Mapping via:
        │ ① FK Link         │ • Product keywords
        ↓                   │ • Business area
                           │ • Support status
2. OPPORTUNITY              │
   ─────────────────       │          Generates:
   Account ST ID (FK) ─────┘          • Service recommendations
   HPE Opportunity ID (PK)             • SKU codes for quotes
   Product Line                        • Priority suggestions
   Format: OPE-XXXXXXXXXX
                                      Validates against:
        │ ② FK Link                    • Historical delivery
        │ When WON...                  • Customer patterns
        ↓                              • Practice expertise
                                              │
3. A&PS PROJECT                               │
   ─────────────────                          │
   Project ID (PK)                            │
   PRJ Siebel ID (FK) ────────────────────────┘
   = HPE Opportunity ID
   PRJ Practice
   PRJ Customer
   Project dates, status

        │ ③ Practice Mapping
        ↓

4. SERVICES CATALOG
   ─────────────────
   Practice → Sub-Practice → Service
   Reference for recommendations
```

---

## 📊 Detailed Relationship Analysis

### Relationship 1: Install Base ↔ Opportunity

**Type**: One-to-Many (Direct Foreign Key)
**Strength**: ⭐⭐⭐⭐⭐ (Strong, direct database relationship)
**Coverage**: 80% (8 of 10 accounts)

**Linking Fields**:
```
Install_Base.Account_Sales_Territory_Id = Opportunity.Account_ST_ID
```

**Business Logic**:
- Install Base shows **current state** (what customer owns)
- Opportunity shows **future state** (what customer is considering)
- Used for: Renewal campaigns, refresh opportunities, upsell identification

**Example**:
```
Account ST ID: 56088

Install Base (15 assets):
  • 5x HP DL360p Gen8 servers
  • 9 expired warranties
  • 6 expired flex support
  • Business Areas: x86 servers, server storage

Opportunities (52 active):
  • Product Lines: x86 servers, software support, integrated platforms
  • Mix of hardware, software, and service opportunities
  • Alignment: Expired warranties → renewal opportunities
```

**Mapping Table**:

| Install Base Business Area | Opportunity Product Lines | Alignment |
|---------------------------|--------------------------|-----------|
| WLAN HW (37 assets) | VR - WLAN HW Svcs (10 opps), VL - WLAN HW (5 opps) | Strong |
| x86 Premium (7 assets) | SY - x86 Premium (12 opps), 96 - Server Support (6 opps) | Strong |
| Server Storage & Inf (17 assets) | SI - Server Storage & Inf (3 opps) | Moderate |

---

### Relationship 2: Opportunity → A&PS Project

**Type**: One-to-Many (Direct Foreign Key)
**Strength**: ⭐⭐⭐⭐⭐ (Strong, confirmed FK relationship)
**Coverage**: 47% (1,117 of 2,394 projects)

**Linking Fields**:
```
Opportunity.HPE_Opportunity_ID = A&PS_Project.PRJ_Siebel_ID
Format: OPE-XXXXXXXXXX (e.g., OPE-0006205063)
```

**Business Logic**:
1. Sales creates **Opportunity** in CRM
2. Opportunity status changes to **WON**
3. A&PS **Project** created to deliver services
4. **PRJ Siebel ID** stores the originating Opportunity ID
5. Project tracks actual delivery vs. promised scope

**Discovery Evidence**:
- 1,117 projects (47%) have OPE-format Siebel IDs
- 991 projects have "NOT AVAILABLE" (no link)
- 186 projects have "#" (missing data)
- Remaining 100 have other formats

**Why 53% Don't Have Links**:
- Older projects before tracking system (pre-2015)
- Internal projects without sales opportunity
- Projects from different tracking systems
- Data quality issues

**Analysis by Time Period**:

| Year Range | Projects WITH Opp Link | Projects WITHOUT Opp Link |
|------------|----------------------|--------------------------|
| 2012-2014 | 31 (17%) | 43 (83%) |
| 2015-2018 | 349 (49%) | 369 (51%) |
| 2019-2022 | 607 (52%) | 554 (48%) |
| 2023-2025 | 130 (42%) | 311 (58%) |

**Characteristics by Link Status**:

| Metric | WITH Opportunity Link | WITHOUT Opportunity Link |
|--------|----------------------|-------------------------|
| Primary Practice | CLD & PLT (75%) | CLD & PLT (68%) |
| Average Duration | 850 days | 162 days |
| Project Complexity | High (long-term) | Lower (short engagements) |

**Example Flow**:
```
Opportunity Created:
  ID: OPE-0006205063
  Customer: Bank of Japan
  Product Line: Cloud & Platform Services
  Value: $500K

       ↓ Status: WON

Project Created:
  Project ID: JP3-SW410
  PRJ Siebel ID: OPE-0006205063  ← LINKS TO OPPORTUNITY
  Customer: 日本銀行 (Bank of Japan)
  Practice: CLD & PLT
  Start: 2017-06-19
  End: 2019-04-26
  Duration: 677 days
  Description: 2017年度区画作成対応
```

---

### Relationship 3: A&PS Project → Services

**Type**: Many-to-Many (Conceptual mapping via Practice codes)
**Strength**: ⭐⭐⭐ (Moderate, requires translation table)

**Linking Fields**:
```
A&PS_Project.PRJ_Practice → Services.Practice (requires mapping)
```

**Practice Code Translation**:

| A&PS Practice Code | Services Practice Name | Service Categories |
|-------------------|----------------------|-------------------|
| CLD & PLT | Hybrid Cloud Consulting | Compute, Storage, SAP, Multicloud |
| CLD & PLT | Hybrid Cloud Engineering | HPC, IaC, DevOps, CNC, Cloud Automation |
| AI & D | Data, AI & IOT | Data Engineering, Analytics, BI, ML, IoT |
| NTWK & CYB | (Not in Services catalog) | Network and Security services |

**Business Logic**:
- A&PS Practice codes are **internal tracking codes**
- Services catalog uses **customer-facing names**
- Mapping required for:
  - Service recommendations based on history
  - Practice expertise identification
  - Resource allocation planning

**Example Mapping**:
```
A&PS Project:
  Practice: CLD & PLT
  Description: "VMware to Azure migration"

       ↓ Maps to Services Catalog

Services Available:
  Practice: Hybrid Cloud Consulting
  Sub-Practice: Multicloud, Private Cloud-VMware, Nutanix
  Services:
    • Cloud Migration Assessment
    • Workload Migration Services
    • Azure Stack Deployment
    • Multicloud Management
```

---

### Relationship 4: Install Base → LS_SKU → Recommendations

**Type**: Indirect (Product keyword and business area matching)
**Strength**: ⭐⭐⭐⭐ (Strong recommendation engine)

**Mapping Logic**:

#### Step 1: Product Keyword Matching
```python
Install Base Product → LS_SKU Product:

# Storage products
"HP 3PAR" → Storage SW/HW → 3PAR
"Primera Storage" → Storage SW/HW → Primera
"Alletra" → Storage SW/HW → Alletra
"Nimble Storage" → Storage SW/HW → Nimble

# Compute products
"DL360p Server" → Compute → Servers
"DL380 Gen9" → Compute → Servers
"BL460c" → Compute → Servers
"Synergy" → Compute → Synergy
"C7000 Enclosure" → Compute → C7000

# Networking products
"Aruba AP-325" → Switches → Networking
"Aruba AP-335" → Switches → Networking
"Switch" → Switches → Networking/SAN
```

#### Step 2: Business Area Mapping
```
Install Base Business Area → LS_SKU Category:

"WLAN HW" → Switches (Networking, SAN)
"Server Storage & Inf" → Storage HW, Storage SW, Compute
"x86 Premium and Scale-up Rack" → Compute
"C-Class Units & Enclosures" → Compute
```

#### Step 3: Status-Based Logic
```
Support Status → Recommended Service Type:

"Expired Warranty" → HW upgrade services (priority)
"Expired Support" → Renewal services, Health Checks
"Active Warranty" → SW services, optimization
"Approaching EOL" → Migration services, platform refresh
"Recent Purchase" → Configuration services, training
```

**Complete Mapping Example**:

```
┌─────────────────────────────────────────────────────────────────┐
│ INSTALL BASE RECORD                                             │
├─────────────────────────────────────────────────────────────────┤
│ Product: HP DL360p Gen8 8-SFF CTO Server                        │
│ Business Area: x86 Premium and Scale-up Rack                    │
│ Support Status: Expired Flex Support                            │
│ EOL Date: 2018-12-31 (6+ years ago)                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ ① Keyword match: "DL360" → Servers
             │ ② Business area: "x86" → Compute
             │ ③ Status: "Expired" → Prioritize HW/Health services
             ↓
┌─────────────────────────────────────────────────────────────────┐
│ LS_SKU MATCH                                                    │
├─────────────────────────────────────────────────────────────────┤
│ Category: Compute                                               │
│ Product: Servers                                                │
│                                                                 │
│ Available Services:                                             │
│  1. Install & Startup                                          │
│  2. OS deployment                                               │
│  3. Health Check ⭐ (Priority - expired warranty)              │
│  4. Firmware upgrade (SKU: HL997A1) ⭐                         │
│  5. OneView configuration (SKU: H6K67A1)                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ ④ Generate recommendations with context
             ↓
┌─────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION OUTPUT                                           │
├─────────────────────────────────────────────────────────────────┤
│ Priority: 🔴 HIGH (warranty expired 2+ years)                  │
│                                                                 │
│ Recommended Actions:                                            │
│  1. Health Check (HL997A1) - $X,XXX                            │
│     Reason: No health check in 2+ years, risk assessment      │
│                                                                 │
│  2. Firmware upgrade (HL997A1) - $X,XXX                        │
│     Reason: Server reaching EOL, critical updates needed       │
│                                                                 │
│  3. Platform refresh quote                                      │
│     Reason: Gen8 → Gen11 migration path available             │
│                                                                 │
│ Bundle Opportunity: Complete Care + Migration Services          │
│ Estimated Value: $XX,XXX                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Practical Use Cases & Workflows

### Use Case 1: Proactive Warranty Renewal Campaign

**Objective**: Identify and renew expired support contracts

**Workflow**:

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Query Install Base                                     │
└─────────────────────────────────────────────────────────────────┘

SELECT
  Account_Sales_Territory_Id,
  Product_Name,
  Support_Status,
  Final_Service_End_Date
FROM Install_Base
WHERE Support_Status LIKE '%Expired%'
  AND Account_Sales_Territory_Id IN (target_accounts)

Result: 20 expired assets across 8 accounts

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Map to LS_SKU Services                                 │
└─────────────────────────────────────────────────────────────────┘

For each expired asset:
  1. Match Product → LS_SKU Product (keyword matching)
  2. Get Business Area → LS_SKU Category
  3. Retrieve applicable services with SKU codes

Example Output:
  • 5x DL360p Servers → Health Check (HL997A1), Firmware upgrade
  • 10x Aruba APs → Firmware upgrade, Network assessment
  • 5x Storage devices → Health Check, Performance analysis

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Check A&PS History                                     │
└─────────────────────────────────────────────────────────────────┘

SELECT
  PRJ_Practice,
  PRJ_Description,
  Health,
  PRJ_Start_Date
FROM A&PS_Projects
WHERE Account_ST_Name LIKE '%Customer_Name%'
  AND PRJ_Practice IN ('CLD & PLT', 'NTWK & CYB')
ORDER BY PRJ_Start_Date DESC
LIMIT 5

Analysis:
  • Customer has purchased Health Checks before
  • High project health scores (positive history)
  • Prefers CLD & PLT practice team

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Create Opportunity Bundle                              │
└─────────────────────────────────────────────────────────────────┘

Opportunity Details:
  Account ST ID: 56088
  Opportunity Name: "FY26 Infrastructure Renewal - Q1"
  Product Line: 96 - Industry Standard Servers Support

Bundle Components:
  1. Complete Care Support (5 servers) - $XX,XXX
  2. Health Check Services (HL997A1) - $X,XXX
  3. Firmware Update Package (HL997A1) - $X,XXX
  4. Network Assessment (10 Aruba devices) - $X,XXX

Total Value: $XXX,XXX
Sales Strategy: Reference positive past engagement (Project JP3-SW410)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Track Win → Project Creation                           │
└─────────────────────────────────────────────────────────────────┘

When Opportunity Status = WON:

  Create A&PS Project:
    Project ID: (auto-generated)
    PRJ Siebel ID: OPE-0020425XXX ← Links to opportunity
    Practice: CLD & PLT (based on customer history)
    Start Date: (contract start)
    Services: Health Check, Firmware upgrades (from LS_SKU)

  Result: Complete traceability from asset → opportunity → delivery
```

---

### Use Case 2: EOL/EOSL Refresh Campaign

**Objective**: Proactively manage hardware reaching end-of-life

**Workflow**:

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Identify At-Risk Assets                                │
└─────────────────────────────────────────────────────────────────┘

SELECT
  Account_Sales_Territory_Id,
  Product_Name,
  Product_End_of_Life_Date,
  Product_End_of_Service_Life_Date,
  DATEDIFF(Product_End_of_Life_Date, CURDATE()) as Days_to_EOL
FROM Install_Base
WHERE Product_End_of_Life_Date <= DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
   OR Product_End_of_Service_Life_Date <= DATE_ADD(CURDATE(), INTERVAL 6 MONTH)

Result: 7 assets approaching EOL in next 12 months

Risk Segments:
  • CRITICAL (0-6 months): 3 assets
  • HIGH (6-12 months): 4 assets

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Match to Refresh Path (LS_SKU)                         │
└─────────────────────────────────────────────────────────────────┘

Example Asset: HP 3PAR Storage (EOL: 2026-03-31)

LS_SKU Lookup:
  Current: 3PAR (Storage SW/HW)
  Recommended Refresh: Primera or Alletra

Migration Services Available:
  • Migration planning assessment
  • Data migration services
  • Install & Startup (new platform)
  • Training and knowledge transfer
  • Parallel run support

Related Services:
  • Storage SW → 3PAR: Migration (listed)
  • Storage HW → Primera: Install & Startup, HW upgrade
  • Storage HW → Alletra: Install & Startup, Migration

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Analyze Similar Migrations (A&PS History)              │
└─────────────────────────────────────────────────────────────────┘

Query historical migration projects:

SELECT
  Project,
  PRJ_Description,
  PRJ_Start_Date,
  PRJ_End_Date,
  DATEDIFF(PRJ_End_Date, PRJ_Start_Date) as Duration_Days,
  Health,
  PRJ_Practice
FROM A&PS_Projects
WHERE PRJ_Description LIKE '%migration%'
   OR PRJ_Description LIKE '%3PAR%'
   OR PRJ_Description LIKE '%Primera%'
ORDER BY PRJ_Start_Date DESC

Analysis Results:
  • Average migration duration: 120 days
  • Success rate: 95% (healthy projects)
  • Practice: CLD & PLT handles storage migrations
  • Common services: Migration + Install + Training bundle

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Build Opportunity with Migration Path                  │
└─────────────────────────────────────────────────────────────────┘

Opportunity Structure:

  Primary: Hardware Refresh
    • Primera Storage Array (new)
    • Trade-in credit for 3PAR (if applicable)

  Migration Services (from LS_SKU):
    • Migration planning and assessment
    • Data migration services
    • Install & Startup (LS_SKU: Storage HW → Primera)
    • Health Check (validate migration)
    • Training (2-day session)

  Support Services:
    • 3-year support contract
    • Performance Analysis (LS_SKU: HM2P6A1#001)

Total Package Value: $XXX,XXX
Timeline: 4-6 months (based on historical data)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Post-Win Project Setup                                 │
└─────────────────────────────────────────────────────────────────┘

When Opportunity Status = WON:

  Create Migration Project:
    PRJ Siebel ID: OPE-XXXXXXXXXX
    Practice: CLD & PLT
    Phase 1: Assessment (2 weeks)
    Phase 2: Planning (4 weeks)
    Phase 3: Migration (8 weeks)
    Phase 4: Validation (2 weeks)

  Deliverables tracking:
    ✓ Migration plan document
    ✓ Data integrity validation
    ✓ Performance baseline
    ✓ Training completion
    ✓ Go-live support
```

---

### Use Case 3: Cross-Sell & Service Attach

**Objective**: Identify customers with hardware but no services

**Workflow**:

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Analyze Install Base Coverage Gaps                     │
└─────────────────────────────────────────────────────────────────┘

Query: Find accounts with hardware but minimal services

WITH Account_Product_Mix AS (
  SELECT
    Account_Sales_Territory_Id,
    COUNT(DISTINCT Business_Area_Description_Name) as Product_Areas,
    COUNT(*) as Total_Assets,
    SUM(CASE WHEN Support_Status LIKE '%Active%' THEN 1 ELSE 0 END) as Active_Support,
    SUM(CASE WHEN Support_Status LIKE '%Expired%' THEN 1 ELSE 0 END) as Expired_Support
  FROM Install_Base
  GROUP BY Account_Sales_Territory_Id
)
SELECT *
FROM Account_Product_Mix
WHERE Product_Areas >= 2  -- Multiple product types
  AND Expired_Support > Active_Support  -- More expired than active

Result: Accounts with diverse hardware but poor service coverage

Example Account:
  • 10 servers + 15 Aruba APs + 3 storage devices
  • Only 2 with active support
  • 26 without current services
  • OPPORTUNITY: Complete Care bundle

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Map Full Service Portfolio (LS_SKU)                    │
└─────────────────────────────────────────────────────────────────┘

For each product category owned:

Servers (10 assets):
  LS_SKU Category: Compute → Servers
  Available Services:
    • Complete Care support
    • Health Check services
    • Firmware management
    • OS deployment support
    • OneView configuration

WLAN (15 Aruba APs):
  LS_SKU Category: Switches → Networking
  Available Services:
    • Network health checks
    • Firmware management
    • Configuration optimization
    • Performance assessment

Storage (3 devices):
  LS_SKU Category: Storage HW/SW
  Available Services:
    • Storage health checks
    • Performance analysis
    • Data optimization
    • Replication configuration

Cross-Product Services:
  • Integrated platform assessment
  • End-to-end architecture review
  • Optimization recommendations

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Check Historical Service Purchases                     │
└─────────────────────────────────────────────────────────────────┘

Query past projects to understand buying patterns:

SELECT
  PRJ_Practice,
  COUNT(*) as Project_Count,
  AVG(PRJ_Days) as Avg_Duration,
  MIN(PRJ_Start_Date) as First_Purchase,
  MAX(PRJ_Start_Date) as Last_Purchase
FROM A&PS_Projects
WHERE Account_ST_Name LIKE '%Customer%'
GROUP BY PRJ_Practice

Analysis:
  • Customer HAS purchased services before (positive signal)
  • Last purchase: 18 months ago (time to re-engage)
  • Primary practice: CLD & PLT
  • Average project: 200 days
  • Buying pattern: Annual refresh cycle

Customer is familiar with HPE services → Lower sales friction

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Create Tiered Service Attach Opportunity               │
└─────────────────────────────────────────────────────────────────┘

Build tiered proposal:

TIER 1: Essential Coverage
  • Complete Care for critical assets (5 servers)
  • Basic health checks (quarterly)
  Value: $XX,XXX/year

TIER 2: Comprehensive (Recommended)
  • Complete Care for all assets
  • Health checks (quarterly)
  • Firmware management service
  • 24/7 support hotline
  Value: $XXX,XXX/year

TIER 3: Premium with Proactive Services
  • All Tier 2 services
  • Monthly performance reviews
  • Proactive optimization
  • Dedicated account engineer
  • Architecture advisory (quarterly)
  Value: $XXX,XXX/year

Sales Strategy:
  • Lead with Tier 2 (best value)
  • Reference past successful engagement
  • Highlight risk of unsupported assets
  • Offer first quarter discount

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Ongoing Service Delivery Tracking                      │
└─────────────────────────────────────────────────────────────────┘

When Opportunity Status = WON:

  Create Recurring Service Projects:

    Project Type: Managed Services
    PRJ Siebel ID: OPE-XXXXXXXXXX
    Frequency: Quarterly health checks

    Deliverables per Quarter:
      • Health check reports (all assets)
      • Firmware compliance report
      • Risk assessment
      • Optimization recommendations

    Success Metrics:
      • Service uptime targets
      • Mean time to resolution
      • Customer satisfaction scores
      • Renewal rate

  Track Service Credits:
    • Purchased Credits: Based on tier
    • Consumption rate: Track quarterly
    • Expiry management: Alert 60 days before
```

---

## 🎯 Integration Summary

### Complete Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      ONELEAD DATA ECOSYSTEM                      │
└──────────────────────────────────────────────────────────────────┘

[1] INSTALL BASE                    [LS_SKU REFERENCE]
    ───────────────                 ─────────────────
    • Current assets                • 32 Products
    • 63 records                    • 6 Categories
    • 10 accounts                   • 138 Services
    • 4 business areas              • HPE SKU codes
           │                               │
           │ ① Account ST ID               │ Keyword + Status
           │    (Direct FK)                │ Matching
           ↓                               ↓
    [2] OPPORTUNITY                 Generate Recommendations:
        ───────────────             ────────────────────────
        • Sales pipeline            • Service bundles
        • 98 opportunities          • SKU codes
        • 8 accounts                • Pricing references
        • OPE-XXXXXXXXXX (PK)       • Priority levels
               │                            │
               │ ② HPE Opp ID               │ Validate against
               │    (When WON)              │ history
               ↓                            ↓
    [3] A&PS PROJECT               [4] SERVICES CATALOG
        ────────────────               ─────────────────
        • Delivery tracking            • 286 services
        • 2,394 projects              • 3 practices
        • 47% have Opp link           • Reference catalog
        • PRJ Siebel ID (FK)
               │
               │ ③ Practice code mapping
               ↓
        Practice expertise
        Resource allocation
        Success patterns

                    │
                    │ ④ Feedback Loop
                    ↓

    [5] SERVICE CREDITS
        ───────────────
        • 1,384 projects
        • 650 purchased
        • 320 active
        • Track consumption
```

### Key Integration Points

#### Point 1: Install Base → Opportunity
- **Relationship**: Direct FK (Account_Sales_Territory_Id)
- **Coverage**: 80% of accounts
- **Usage**: Renewal campaigns, upsell identification
- **Automation**: Auto-generate opportunities for expired assets

#### Point 2: Install Base/Opportunity → LS_SKU
- **Relationship**: Keyword matching + business rules
- **Coverage**: 100% of product categories mapped
- **Usage**: Service recommendations, quote generation
- **Automation**: Real-time SKU lookup during opportunity creation

#### Point 3: Opportunity → A&PS Project
- **Relationship**: Direct FK (HPE Opportunity ID → PRJ Siebel ID)
- **Coverage**: 47% of projects linked
- **Usage**: Pipeline tracking, delivery accountability
- **Automation**: Auto-create project on opportunity win

#### Point 4: A&PS Project → Services
- **Relationship**: Practice code mapping
- **Coverage**: All projects mapped to practice areas
- **Usage**: Historical analysis, expertise mapping
- **Automation**: Service recommendations based on past purchases

#### Point 5: Service Credits
- **Relationship**: Links to projects and practices
- **Coverage**: 1,384 credit-based projects
- **Usage**: Credit utilization tracking, expiry alerts
- **Automation**: Alert when credits near expiration

---

## 📈 Data Quality & Coverage Analysis

### Install Base Quality

| Metric | Value | Quality |
|--------|-------|---------|
| Total Records | 63 | ✅ Complete |
| Unique Accounts | 10 | ✅ Good coverage |
| Products with EOL dates | 63 (100%) | ✅ Excellent |
| Products with Support Status | 63 (100%) | ✅ Excellent |
| Active Support Coverage | 33/63 (52%) | ⚠️ Opportunity for renewals |

### Opportunity Quality

| Metric | Value | Quality |
|--------|-------|---------|
| Total Records | 98 | ✅ Complete |
| Unique Accounts | 8 | ✅ Good (80% of IB accounts) |
| With Product Lines | 73/98 (74%) | ⚠️ Some missing classifications |
| Account Name Variations | Multiple per account | ⚠️ Needs normalization |

### A&PS Project Quality

| Metric | Value | Quality |
|--------|-------|---------|
| Total Records | 2,394 | ✅ Excellent historical data |
| With Opportunity Link | 1,117 (47%) | ⚠️ Partial linkage (expected) |
| With Customer Data | 2,394 (100%) | ✅ Complete |
| With Practice Area | 2,394 (100%) | ✅ Complete |
| With Project Dates | 2,394 (100%) | ✅ Complete |

### LS_SKU Coverage

| Metric | Value | Quality |
|--------|-------|---------|
| Product Categories | 6 | ✅ Comprehensive |
| Unique Products | 32 | ✅ Good coverage |
| Service Mappings | 138 | ✅ Detailed |
| SKU Codes Included | ~60% | ⚠️ Some services missing SKUs |

---

## 🔧 Technical Implementation Notes

### Database Schema

```sql
-- Install Base
CREATE TABLE install_base (
  serial_number_id VARCHAR(50) PRIMARY KEY,
  product_id VARCHAR(50),
  product_name VARCHAR(255),
  account_sales_territory_id INTEGER,  -- FK to opportunities
  business_area_description_name VARCHAR(100),
  support_status VARCHAR(50),
  product_end_of_life_date DATE,
  product_end_of_service_life_date DATE,
  -- ... other fields
  FOREIGN KEY (account_sales_territory_id) REFERENCES accounts(account_st_id)
);

-- Opportunity
CREATE TABLE opportunity (
  hpe_opportunity_id VARCHAR(20) PRIMARY KEY,  -- Format: OPE-XXXXXXXXXX
  opportunity_name VARCHAR(255),
  account_st_id INTEGER,  -- FK to install base
  account_name VARCHAR(255),
  product_line VARCHAR(100),
  FOREIGN KEY (account_st_id) REFERENCES accounts(account_st_id)
);

-- A&PS Project
CREATE TABLE aps_project (
  project_id VARCHAR(50) PRIMARY KEY,
  prj_siebel_id VARCHAR(20),  -- FK to opportunity (Format: OPE-XXXXXXXXXX)
  prj_customer VARCHAR(255),
  prj_practice VARCHAR(50),
  prj_start_date DATE,
  prj_end_date DATE,
  -- ... other fields
  FOREIGN KEY (prj_siebel_id) REFERENCES opportunity(hpe_opportunity_id)
);

-- LS_SKU Mapping (reference table, no direct FK)
CREATE TABLE ls_sku_mapping (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category VARCHAR(50),
  product VARCHAR(100),
  service VARCHAR(255),
  sku_code VARCHAR(50)
);
```

### Querying Relationships

#### Query 1: Complete Customer 360
```sql
-- Get complete view of customer with assets, opportunities, and history

SELECT
  ib.account_sales_territory_id,
  COUNT(DISTINCT ib.serial_number_id) as total_assets,
  COUNT(DISTINCT ib.business_area_description_name) as product_categories,
  COUNT(DISTINCT o.hpe_opportunity_id) as active_opportunities,
  COUNT(DISTINCT ap.project_id) as historical_projects,
  SUM(CASE WHEN ib.support_status LIKE '%Expired%' THEN 1 ELSE 0 END) as expired_assets
FROM install_base ib
LEFT JOIN opportunity o ON ib.account_sales_territory_id = o.account_st_id
LEFT JOIN aps_project ap ON o.hpe_opportunity_id = ap.prj_siebel_id
WHERE ib.account_sales_territory_id = 56088
GROUP BY ib.account_sales_territory_id;
```

#### Query 2: Service Recommendations
```sql
-- Get service recommendations for expired assets

SELECT
  ib.product_name,
  ib.business_area_description_name,
  ib.support_status,
  ls.category,
  ls.product,
  ls.service,
  ls.sku_code
FROM install_base ib
LEFT JOIN ls_sku_mapping ls
  ON (
    -- Match by product keywords
    (ib.product_name LIKE CONCAT('%', ls.product, '%'))
    OR
    -- Match by business area
    (ib.business_area_description_name LIKE '%Server%' AND ls.category = 'Compute')
    OR
    (ib.business_area_description_name LIKE '%WLAN%' AND ls.category = 'Switches')
  )
WHERE ib.support_status LIKE '%Expired%'
  AND ib.account_sales_territory_id = 56088;
```

#### Query 3: Opportunity to Project Tracking
```sql
-- Track opportunities that became projects

SELECT
  o.hpe_opportunity_id,
  o.opportunity_name,
  o.product_line,
  ap.project_id,
  ap.prj_description,
  ap.prj_practice,
  ap.prj_start_date,
  ap.prj_end_date,
  DATEDIFF(ap.prj_end_date, ap.prj_start_date) as project_duration_days
FROM opportunity o
INNER JOIN aps_project ap ON o.hpe_opportunity_id = ap.prj_siebel_id
WHERE o.account_st_id = 56088
ORDER BY ap.prj_start_date DESC;
```

---

## 🎓 Best Practices & Recommendations

### Data Integration

1. **Maintain Account ID Consistency**
   - Standardize Account_Sales_Territory_Id across all systems
   - Create account normalization table for name variations
   - Implement data quality checks on imports

2. **Enforce Opportunity → Project Linking**
   - Make PRJ Siebel ID mandatory for new projects
   - Backfill missing links where possible
   - Document exceptions (internal projects, etc.)

3. **Keep LS_SKU Updated**
   - Review quarterly with product teams
   - Add new products/services as launched
   - Validate SKU codes against pricing system
   - Archive discontinued products/services

4. **Automate Data Refresh**
   - Schedule daily imports from source systems
   - Implement change tracking (audit tables)
   - Alert on data quality issues
   - Version control for major schema changes

### Service Recommendations

1. **Priority Scoring**
   - Expired warranties: Highest priority
   - Approaching EOL: High priority
   - Active assets without services: Medium priority
   - Recent purchases: Lower priority (focus on adoption)

2. **Bundle Logic**
   - Always include Health Check with hardware services
   - Pair migrations with training services
   - Offer multi-year contracts for stable environments
   - Suggest Complete Care for mixed environments

3. **Historical Context**
   - Reference past successful projects in proposals
   - Use similar customer case studies
   - Leverage practice expertise from A&PS data
   - Highlight customer-specific buying patterns

### Reporting & Analytics

1. **Executive Dashboards**
   - Pipeline value by account
   - Renewal opportunity forecast
   - EOL/EOSL risk assessment
   - Service attach rate trends

2. **Sales Team Views**
   - Account 360° with complete relationship view
   - Next best actions (prioritized recommendations)
   - Opportunity aging and health scores
   - Win/loss analysis by product line

3. **Operations Tracking**
   - Opportunity → Project conversion rate
   - Average project duration by practice
   - Resource utilization by practice area
   - Customer satisfaction correlation with project health

---

## 📚 Appendix

### A. Field Definitions

#### Install Base Fields
- **Serial_Number_Id**: Unique hardware serial number
- **Account_Sales_Territory_Id**: Customer account identifier
- **Business_Area_Description_Name**: Product category (WLAN, Compute, Storage)
- **Support_Status**: Current warranty/support status
- **Product_End_of_Life_Date**: Date when product reaches EOL
- **Product_End_of_Service_Life_Date**: Date when support ends
- **Final_Service_End_Date**: Current service contract end date

#### Opportunity Fields
- **HPE Opportunity ID**: Unique opportunity identifier (Format: OPE-XXXXXXXXXX)
- **Account ST ID**: Foreign key to Install Base account
- **Product Line**: Sales product line classification
- **Opportunity NAme**: Description of the opportunity

#### A&PS Project Fields
- **Project**: Internal project identifier
- **PRJ Siebel ID**: Originating opportunity ID (FK)
- **PRJ Practice**: Service practice area code (CLD & PLT, NTWK & CYB, AI & D)
- **PRJ Customer**: Customer name
- **PRJ Start Date**: Project start date
- **PRJ End Date**: Project completion date
- **Health**: Project health indicator

#### LS_SKU Fields
- **Category**: High-level product category
- **Product**: Specific product name
- **Service**: Available service offering
- **SKU Code**: HPE service SKU code (where applicable)

### B. Practice Code Mappings

| Code | Full Name | Services Catalog Equivalent |
|------|-----------|----------------------------|
| CLD & PLT | Cloud & Platform | Hybrid Cloud Consulting, Hybrid Cloud Engineering |
| NTWK & CYB | Network & Cyber | (Not in current catalog) |
| AI & D | AI & Data | Data, AI & IOT |
| Other | Miscellaneous | Various |

### C. Support Status Values

| Status | Meaning | Opportunity Type |
|--------|---------|-----------------|
| Active Warranty | Current hardware warranty | Service attach |
| Expired Warranty | Hardware warranty expired | Renewal, Service attach |
| Active Support | Current support contract | Upsell, Cross-sell |
| Expired Flex Support | Flex support expired | Renewal |
| Expired Fixed Support | Fixed support expired | Renewal |
| Warranty Expired - Uncovered Box | No current coverage | High priority renewal |

### D. Business Area Classifications

| Business Area | Description | Primary Category |
|--------------|-------------|-----------------|
| WLAN HW | Wireless LAN hardware | Networking |
| Server Storage & Inf | Servers and storage infrastructure | Compute, Storage |
| x86 Premium and Scale-up Rack | High-end x86 servers | Compute |
| C-Class Units & Enclosures | Blade server enclosures | Compute |

---

## 🔄 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-29 | Data Analysis Team | Initial comprehensive analysis |

---

## 📞 Questions & Support

For questions about data relationships or integration:
- **Technical**: Review this document and DATABASE_MODEL.md
- **Data Quality**: Check source Excel files in /data/
- **Implementation**: See source code in /src/models/ and /src/engines/

---

**End of Document**
