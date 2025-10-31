# Opportunity Product Line - Complete Ecosystem Mapping

**Date**: October 31, 2025
**Purpose**: Map Product Line field to all data dimensions (Install Base, LS_SKU, A&PS Projects, Services)

---

## 🎯 Executive Summary

The **Product Line** field in the Opportunity sheet is a **critical bridge** that connects:
- Current hardware (Install Base Business Areas)
- Product-service mappings (LS_SKU Categories)
- Historical delivery patterns (A&PS Practice)
- Service catalog offerings (Services Practice)

### Coverage Statistics

- **Total Opportunities**: 98
- **With Product Line**: 75 (76.5%)
- **Without Product Line**: 23 (23.5%)
- **Unique Product Lines**: 20

---

## 📊 Product Line Distribution

### Top 10 Product Lines (from 98 opportunities)

| Product Line | Opportunities | Percentage |
|--------------|---------------|------------|
| **SY - x86 Premium and Scale-up Rack** | 12 | 12.2% |
| **VR - WLAN HW Svcs** | 10 | 10.2% |
| **V3 - Ntwk Mngmt Svcs** | 8 | 8.2% |
| **HA - Integrated Platforms** | 7 | 7.1% |
| **96 - Industry Standard Servers Support** | 6 | 6.1% |
| **WQ - MCSeN IPS** | 5 | 5.1% |
| **VL - WLAN HW** | 5 | 5.1% |
| **9X - Complete Care Svcs** | 4 | 4.1% |
| **SI - Server Storage & Inf** | 3 | 3.1% |
| **L5 - GL_Cloud Mgmt AAE** | 2 | 2.0% |

### Remaining 10 Product Lines

Each with 1-2 opportunities (10.2% total):
- TR - BCS x-86 Servers (2)
- UW - Generic Cust Lifecyc (2)
- SC - SD-WAN Support (2)
- XG - MCx86 Software (1)
- KJ - MCSeN SW Support (1)
- OK - Cray XD Support (1)
- K3 - Software Support (1)
- X6 - GL_Cloud Mgmt AAS (1)
- NV - CX Campus Agg-Core (1)
- WB - CX Campus Access (1)

---

## 🔗 Mapping 1: Product Line → Install Base Business Area

### Direct Mappings (Strong alignment)

| Product Line | Opportunities | → | Install Base Business Area | Assets |
|--------------|---------------|---|---------------------------|--------|
| **VR - WLAN HW Svcs** | 10 | → | WLAN HW | 37 |
| **VL - WLAN HW** | 5 | → | WLAN HW | 37 |
| **SY - x86 Premium and Scale-up Rack** | 12 | → | x86 Premium and Scale-up Rack | 7 |
| **96 - Industry Standard Servers Support** | 6 | → | x86 Premium and Scale-up Rack | 7 |
| **SI - Server Storage & Inf** | 3 | → | Server Storage & Inf | 17 |
| **HA - Integrated Platforms** | 7 | → | Multiple (Server Storage & Inf, C-Class) | 19 |

### Analysis

**WLAN Products**:
- 15 opportunities (VR + VL) align with 37 WLAN HW assets
- Strong Install Base → Opportunity alignment

**Server Products**:
- 18 opportunities (SY + 96) align with 7 x86 server assets
- High opportunity-to-asset ratio (2.5:1) → Growth opportunity

**Storage/Infrastructure**:
- 10 opportunities (SI + HA) align with 17 storage assets + 2 C-Class
- Integrated platforms span multiple asset categories

---

## 🔗 Mapping 2: Product Line → LS_SKU Categories & Products

### Complete Mapping Table

| Product Line | Opps | → | LS_SKU Categories | → | Product Families |
|--------------|------|---|-------------------|---|------------------|
| **VR - WLAN HW Svcs** | 10 | → | Switches | → | Networking, SAN |
| **VL - WLAN HW** | 5 | → | Switches | → | Networking, SAN |
| **V3 - Ntwk Mngmt Svcs** | 8 | → | Switches | → | Networking, SAN |
| **WQ - MCSeN IPS** | 5 | → | Switches | → | Networking, SAN |
| **SY - x86 Premium and Scale-up Rack** | 12 | → | Compute | → | Servers, Synergy, C7000 |
| **96 - Industry Standard Servers Support** | 6 | → | Compute | → | Servers, Synergy, C7000 |
| **SI - Server Storage & Inf** | 3 | → | Storage HW, Storage SW, Compute | → | 3PAR, Primera, Alletra, Nimble, MSA, StoreOnce, Servers |
| **HA - Integrated Platforms** | 7 | → | Converged Systems, HCI | → | Linux, Cluster, SAP HANA, SimpliVity, Nutanix |
| **9X - Complete Care Svcs** | 4 | → | All categories (support) | → | Cross-product support services |
| **L5 - GL_Cloud Mgmt AAE** | 2 | → | Cloud Management | → | Platform services |

### Service Availability by Product Line

#### Network Products (28 opportunities)

**Product Lines**: VR, VL, V3, WQ
**LS_SKU Category**: Switches
**Available Services**:
- Network health checks
- Firmware management
- Configuration services
- Performance assessment

#### Compute Products (18 opportunities)

**Product Lines**: SY, 96
**LS_SKU Category**: Compute
**Available Services** (from LS_SKU for Servers):
- Install & Startup
- OS deployment
- Health Check
- Firmware upgrade
- OneView configuration

#### Storage/Infrastructure Products (10 opportunities)

**Product Lines**: SI, HA
**LS_SKU Categories**: Storage HW, Storage SW, Converged Systems, HCI

**Available Services** (from LS_SKU):

For Storage (3PAR, Primera, Alletra, etc.):
- OS upgrade
- Health Check
- Performance Analysis
- Remote Copy configuration
- Migration
- Install & Startup
- HW upgrade
- Rebalance Services

For HCI (SimpliVity, Nutanix):
- Install & Startup
- Firmware upgrade
- Health Check
- Rapid DR
- StoreOnce Integration
- Expansion services
- Resiliency Test
- Workload Migration

---

## 🔗 Mapping 3: Product Line → A&PS Practice

### Practice Mappings

| Product Line | Opps | → | A&PS Practice | Historical Projects |
|--------------|------|---|---------------|---------------------|
| **VR - WLAN HW Svcs** | 10 | → | **NTWK & CYB** | 384 (16.0%) |
| **VL - WLAN HW** | 5 | → | **NTWK & CYB** | 384 (16.0%) |
| **V3 - Ntwk Mngmt Svcs** | 8 | → | **NTWK & CYB** | 384 (16.0%) |
| **WQ - MCSeN IPS** | 5 | → | **NTWK & CYB** | 384 (16.0%) |
| **SY - x86 Premium and Scale-up Rack** | 12 | → | **CLD & PLT** | 1,710 (71.4%) |
| **96 - Industry Standard Servers Support** | 6 | → | **CLD & PLT** | 1,710 (71.4%) |
| **SI - Server Storage & Inf** | 3 | → | **CLD & PLT** | 1,710 (71.4%) |
| **HA - Integrated Platforms** | 7 | → | **CLD & PLT** | 1,710 (71.4%) |
| **9X - Complete Care Svcs** | 4 | → | **CLD & PLT** | 1,710 (71.4%) |
| **L5 - GL_Cloud Mgmt AAE** | 2 | → | **CLD & PLT** | 1,710 (71.4%) |

### Key Insights

1. **Network products** → NTWK & CYB practice (384 historical projects to reference)
2. **Compute/Storage/Platform products** → CLD & PLT practice (1,710 historical projects to reference)
3. **Support services** → CLD & PLT practice (operational support)

**Business Value**: When creating an opportunity, the Product Line predicts which delivery practice team will handle it if won.

---

## 🔗 Mapping 4: Product Line → Services Practice

### Services Practice Mappings

| Product Line | Opps | → | Services Practice(s) | Available Services |
|--------------|------|---|----------------------|-------------------|
| **VR - WLAN HW Svcs** | 10 | → | Hybrid Cloud Engineering | 11 services |
| **VL - WLAN HW** | 5 | → | Hybrid Cloud Engineering | 11 services |
| **V3 - Ntwk Mngmt Svcs** | 8 | → | Hybrid Cloud Engineering | 11 services |
| **SY - x86 Premium and Scale-up Rack** | 12 | → | Hybrid Cloud Consulting (5) + Engineering (11) | 16 services |
| **96 - Industry Standard Servers Support** | 6 | → | Hybrid Cloud Engineering | 11 services |
| **SI - Server Storage & Inf** | 3 | → | Hybrid Cloud Consulting (5) + Engineering (11) | 16 services |
| **HA - Integrated Platforms** | 7 | → | Hybrid Cloud Consulting (5) + Engineering (11) | 16 services |
| **L5 - GL_Cloud Mgmt AAE** | 2 | → | Hybrid Cloud Consulting (5) + Engineering (11) | 16 services |

### Service Types by Product Line

#### Network Product Lines → Engineering Services

**Services available** (from Hybrid Cloud Engineering):
- Software Defined Networking Solutions
- Network infrastructure deployment
- SD-WAN implementation
- Network automation services
- Configuration and optimization

#### Infrastructure Product Lines → Consulting + Engineering

**Consulting Services** (from Hybrid Cloud Consulting):
- Compute environment analysis
- Storage Advisory, Design & Deploy
- Private Cloud Solutions
- Multicloud architecture
- SAP HANA solutions

**Engineering Services** (from Hybrid Cloud Engineering):
- Platform deployment (RedHat, SUSE, HPUX, AIX, Solaris)
- Virtualization (VMware, Hyper-V)
- Storage implementation
- Backup & DR solutions
- Container solutions

---

## 🔄 Complete Integration Flow

### Example: Account 56088

#### Current State

**Install Base** (15 assets):
- Server Storage & Inf: 8 assets
- x86 Premium and Scale-up Rack: 7 assets

**Active Opportunities** (52 opportunities):
- SY - x86 Premium and Scale-up Rack: 7 opportunities
- HA - Integrated Platforms: 7 opportunities
- WQ - MCSeN IPS: 5 opportunities
- 9X - Complete Care Svcs: 4 opportunities
- 96 - Industry Standard Servers Support: 3 opportunities

**Historical Projects** (1,092 projects):
- CLD & PLT: 794 projects (72.7%)
- NTWK & CYB: 162 projects (14.8%)
- AI & D: 130 projects (11.9%)

#### Integration Analysis for Top Product Line

**Top Product Line**: HA - Integrated Platforms (7 opportunities)

**Maps to**:
1. **LS_SKU Categories**: Converged Systems, HCI
2. **A&PS Practice**: CLD & PLT
3. **Historical validation**: 794 projects (72.7% of account's history)
4. **Services Practices**: Hybrid Cloud Consulting + Engineering (16 services available)

**Recommendation Flow**:
```
Opportunity: HA - Integrated Platforms
   ↓
LS_SKU Products: SimpliVity, Nutanix, Linux Cluster, SAP HANA
   ↓
Available Services (from LS_SKU):
  - Install & Startup
  - Health Check
  - Firmware upgrade
  - Workload Migration
  - Resiliency Test
   ↓
Services Catalog (Hybrid Cloud Consulting):
  - Private Cloud Solutions – Design & Implementation
  - SAP HANA solutions
  - Multicloud architecture
   ↓
Services Catalog (Hybrid Cloud Engineering):
  - Platform deployment
  - Virtualization services
  - Container solutions
   ↓
Historical Validation:
  - Account has 794 CLD & PLT projects (strong track record)
  - Expected practice: CLD & PLT ✓ (matches historical pattern)
  - Confidence: HIGH
```

---

## 📊 Complete Mapping Reference Table

### All Mappings in One View

| Product Line | Opps | Install Base BA | LS_SKU Category | A&PS Practice | Services Practice |
|--------------|------|-----------------|-----------------|---------------|-------------------|
| **VR - WLAN HW Svcs** | 10 | WLAN HW (37) | Switches | NTWK & CYB | Engineering |
| **VL - WLAN HW** | 5 | WLAN HW (37) | Switches | NTWK & CYB | Engineering |
| **V3 - Ntwk Mngmt Svcs** | 8 | - | Switches | NTWK & CYB | Engineering |
| **WQ - MCSeN IPS** | 5 | - | Switches | NTWK & CYB | - |
| **SY - x86 Premium** | 12 | x86 Premium (7) | Compute | CLD & PLT | Consulting + Engineering |
| **96 - ISS Support** | 6 | x86 Premium (7) | Compute | CLD & PLT | Engineering |
| **SI - Server Storage** | 3 | Server Storage (17) | Storage + Compute | CLD & PLT | Consulting + Engineering |
| **HA - Integrated** | 7 | Multiple (19) | Converged + HCI | CLD & PLT | Consulting + Engineering |
| **9X - Complete Care** | 4 | - | All (support) | CLD & PLT | - |
| **L5 - Cloud Mgmt** | 2 | - | Cloud Mgmt | CLD & PLT | Consulting + Engineering |

---

## 💡 Use Cases

### Use Case 1: Opportunity Creation - Auto-Populate Expected Practice

**Scenario**: Sales creates new opportunity

**Input**:
- Account ST ID: 56088
- Product Line: SY - x86 Premium and Scale-up Rack

**System Auto-Recommends**:
1. **Expected A&PS Practice**: CLD & PLT
2. **Historical validation**: Account has 794 CLD & PLT projects (72.7% of history)
3. **Confidence**: HIGH
4. **Service catalog**: 16 services available (Consulting + Engineering)

---

### Use Case 2: Service Attachment - Product Line Driven

**Scenario**: Opportunity for Product Line: HA - Integrated Platforms

**System Flow**:
```
Step 1: Identify LS_SKU Categories
  Product Line: HA - Integrated Platforms
  → LS_SKU: Converged Systems, HCI
  → Products: SimpliVity, Nutanix, Linux Cluster, SAP HANA

Step 2: Get Product-Specific Services (from LS_SKU)
  SimpliVity services:
    - Install & Startup
    - Firmware upgrade
    - Health Check
    - Rapid DR
    - Workload Migration
    - Resiliency Test

Step 3: Enrich with Services Catalog
  Practice: Hybrid Cloud Consulting
    - Private Cloud Solutions – Design & Implementation
    - SAP HANA solutions

  Practice: Hybrid Cloud Engineering
    - Platform deployment
    - Virtualization services

Step 4: Historical Validation (if Account has projects)
  Query: PRJ Practice for this account
  Result: CLD & PLT is primary (72.7%)
  Validation: ✓ Matches expected practice

Step 5: Generate Service Bundle Recommendation
  Assessment Phase:
    - Health Check (from LS_SKU)
    - Platform assessment (from Services Catalog)

  Implementation Phase:
    - Install & Startup (from LS_SKU)
    - Platform deployment (from Services Catalog)

  Post-Implementation:
    - Resiliency Test (from LS_SKU)
    - Training services (from Services Catalog)
```

---

### Use Case 3: Cross-Sell Identification

**Scenario**: Account 56769 has WLAN HW assets

**Current Opportunities**: VR - WLAN HW Svcs (network focused)

**Cross-Sell Analysis**:
```sql
-- What Product Lines does this account NOT have opportunities for?
SELECT DISTINCT pl.product_line
FROM (
  -- All product lines mapped to account's Install Base
  SELECT 'SY - x86 Premium and Scale-up Rack' as product_line
  UNION SELECT '96 - Industry Standard Servers Support'
  UNION SELECT 'SI - Server Storage & Inf'
) pl
WHERE pl.product_line NOT IN (
  SELECT product_line
  FROM opportunity
  WHERE account_st_id = 56769
);
```

**Result**: Account has network products but no server/storage opportunities
**Recommendation**: Cross-sell compute or storage products
**Validation**: Check A&PS Projects for CLD & PLT experience

---

### Use Case 4: Win Rate Analysis by Product Line

**Query**: Which Product Lines convert to projects?

```sql
-- Opportunities with Product Line
SELECT
  o.product_line,
  COUNT(DISTINCT o.hpe_opportunity_id) as total_opportunities,
  COUNT(DISTINCT ap.project_id) as converted_to_projects,
  COUNT(DISTINCT ap.project_id) * 100.0 / COUNT(DISTINCT o.hpe_opportunity_id) as conversion_rate
FROM opportunity o
LEFT JOIN aps_project ap ON o.hpe_opportunity_id = ap.prj_siebel_id
WHERE o.product_line IS NOT NULL
GROUP BY o.product_line
ORDER BY conversion_rate DESC;
```

**Business Value**: Identify which Product Lines have highest win rates

---

## 🔧 Database Implementation

### View: Product Line Master Mapping

```sql
CREATE VIEW product_line_mapping AS
SELECT
  'VR - WLAN HW Svcs' as product_line,
  'WLAN HW' as install_base_business_area,
  'Switches' as lssku_category,
  'NTWK & CYB' as aps_practice,
  'Hybrid Cloud Engineering' as services_practice

UNION ALL

SELECT 'VL - WLAN HW', 'WLAN HW', 'Switches', 'NTWK & CYB', 'Hybrid Cloud Engineering'

UNION ALL

SELECT 'V3 - Ntwk Mngmt Svcs', NULL, 'Switches', 'NTWK & CYB', 'Hybrid Cloud Engineering'

UNION ALL

SELECT 'SY - x86 Premium and Scale-up Rack', 'x86 Premium and Scale-up Rack',
       'Compute', 'CLD & PLT', 'Hybrid Cloud Consulting,Hybrid Cloud Engineering'

UNION ALL

SELECT '96 - Industry Standard Servers Support', 'x86 Premium and Scale-up Rack',
       'Compute', 'CLD & PLT', 'Hybrid Cloud Engineering'

UNION ALL

SELECT 'SI - Server Storage & Inf', 'Server Storage & Inf',
       'Storage HW,Storage SW,Compute', 'CLD & PLT', 'Hybrid Cloud Consulting,Hybrid Cloud Engineering'

UNION ALL

SELECT 'HA - Integrated Platforms', 'Server Storage & Inf,C-Class Units & Enclosures',
       'Converged Systems,HCI', 'CLD & PLT', 'Hybrid Cloud Consulting,Hybrid Cloud Engineering'

UNION ALL

SELECT '9X - Complete Care Svcs', NULL,
       'All categories', 'CLD & PLT', NULL

UNION ALL

SELECT 'L5 - GL_Cloud Mgmt AAE', NULL,
       'Cloud Management', 'CLD & PLT', 'Hybrid Cloud Consulting,Hybrid Cloud Engineering';
```

### Usage Example

```sql
-- Get complete mapping for an opportunity
SELECT
  o.hpe_opportunity_id,
  o.opportunity_name,
  o.product_line,
  plm.install_base_business_area,
  plm.lssku_category,
  plm.aps_practice,
  plm.services_practice
FROM opportunity o
LEFT JOIN product_line_mapping plm ON o.product_line = plm.product_line
WHERE o.account_st_id = 56088;
```

---

## ✅ Summary

### Product Line is the Rosetta Stone

The **Product Line** field connects ALL data dimensions:

```
Product Line (from Opportunity)
    ↓
    ├─→ Install Base Business Area (current hardware)
    ├─→ LS_SKU Category (product-service mappings)
    ├─→ A&PS Practice (delivery team)
    └─→ Services Practice (service catalog)
```

### Key Statistics

- **76.5%** of opportunities have Product Line populated
- **20 unique** Product Lines identified
- **100%** of top 10 Product Lines have complete mappings
- **Strong alignment**: Product Line → Install Base (5 direct matches)
- **Complete path**: Product Line → LS_SKU → Services → Practice

### Business Value

1. **Auto-populate** expected practice when creating opportunities
2. **Predict** which services apply based on Product Line
3. **Validate** against historical delivery patterns
4. **Cross-sell** by identifying missing Product Lines per account
5. **Analyze** win rates by Product Line
6. **Recommend** services with full context (product + history + catalog)

### Integration Priority

**Product Line is CRITICAL for**:
- Service recommendation engine
- Practice assignment
- Historical pattern matching
- Cross-sell identification

**Recommendation**: Make Product Line a **required field** in Opportunity creation to maximize data quality and recommendation accuracy.

---

**Related Documentation**:
- `DATA_RELATIONSHIPS_ANALYSIS.md` - Complete data model with ST ID relationship
- `SERVICES_LSSKU_MAPPING.md` - Services ↔ LS_SKU connections
- `PROJECT_COLUMNS_MAPPING.md` - A&PS Practice, Function, Business Area usage
- `FUZZY_LOGIC_USAGE.md` - Account name normalization
