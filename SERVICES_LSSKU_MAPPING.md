# Services Sheet ↔ LS_SKU Sheet Mapping Analysis

**Date**: October 31, 2025
**Connection Rate**: 80.4% (230 of 286 services have potential matches)

---

## 🎯 Executive Summary

Analysis reveals **strong connections** between the **Services catalog** (DataExportSample.xlsx) and **LS_SKU product-service mappings** (LS_SKU_for_Onelead.xlsx Sheet2).

### Key Findings

✅ **71 high-confidence matches** (85%+ similarity) - Direct service name overlaps
✅ **73 medium-confidence matches** (70-84% similarity) - Related services
✅ **86 potential matches** (60-69% similarity) - Conceptual connections
✅ **11 common service keywords** found in both sheets

### Business Impact

This mapping enables:
1. **Product → Service recommendations** (LS_SKU knows which services apply to which products)
2. **Service catalog validation** (Services sheet provides detailed service descriptions)
3. **SKU code enrichment** (LS_SKU provides HPE SKU codes for quoting)
4. **Practice alignment** (Services sheet organizes by practice areas)

---

## 📊 Sheet Comparison

### Services Sheet (DataExportSample.xlsx)
- **Purpose**: Comprehensive service catalog organized by practice
- **Structure**: Practice → Sub-Practice → Service Name
- **Total Services**: 286 services
- **Practices**: 3 (Hybrid Cloud Consulting, Hybrid Cloud Engineering, Data AI & IOT)
- **Sub-Practices**: 23 categories
- **Characteristics**:
  - Detailed, customer-facing service descriptions
  - Organized by business practice
  - Strategic/consulting-oriented
  - No SKU codes included

### LS_SKU Sheet2 (LS_SKU_for_Onelead.xlsx)
- **Purpose**: Product-to-service mapping with SKU codes
- **Structure**: Product Family → Services Available (with SKU codes)
- **Total Services**: 152 service entries (with duplicates across products)
- **Product Categories**: 6 (Storage SW, Storage HW, Compute, Switches, Converged Systems, HCI)
- **Products**: 32 product families
- **Characteristics**:
  - Tactical/operational service names
  - Linked to specific HPE products
  - Includes HPE SKU codes for ordering
  - Implementation-focused

---

## 🔗 Relationship Types

### Type 1: Direct Name Matches (71 services)

**Exact or near-exact service name matches between sheets**

| Services Sheet | LS_SKU Sheet | Match Score | Notes |
|----------------|--------------|-------------|-------|
| Storage Performance Analysis | Performance Analysis (HM2P6A1#001) | 100% | Exact match with SKU |
| HPE Compute Migration Services | Migration | 100% | Generic migration service |
| Storage Block Data Migration | Migration | 100% | Specific migration type |
| HPE StoreOnce Integration Service | StoreOnce Integration | 100% | Product-specific service |
| Private Cloud Upgrade Solutions | Upgrade | 100% | Generic upgrade service |
| Cluster / HA Deployment, Integration and Upgrade | Upgrade | 100% | Specific upgrade type |

**Pattern**: Services sheet has **detailed descriptions**, LS_SKU has **concise names with SKU codes**

### Type 2: Keyword Overlaps (11 common themes)

**Services organized around common operational themes**

| Keyword | Services Sheet Count | LS_SKU Sheet Count | Alignment |
|---------|---------------------|-------------------|-----------|
| **Migration** | 31 | 7 | ✅ Strong - All LS_SKU migrations covered |
| **Install** | 8 | 27 | ✅ Strong - LS_SKU product-specific installs |
| **Upgrade** | 18 | 28 | ✅ Strong - Both cover upgrade services |
| **Health Check** | Embedded in "assessment" (7) | 20 | ✅ Strong - LS_SKU product health checks |
| **Configuration** | 13 | 10 | ✅ Strong - Setup/config services |
| **Performance** | 13 | 3 | ⚠️ Partial - Services broader coverage |
| **Deployment** | 18 | 2 | ⚠️ Partial - Services broader coverage |

### Type 3: Practice-to-Product Mapping

**How Services practices align with LS_SKU product categories**

| Services Practice | Relevant LS_SKU Categories | Connection |
|-------------------|---------------------------|------------|
| **Hybrid Cloud Consulting** | - Compute<br/>- HCI<br/>- Converged Systems | Design, assessment, migration services for compute infrastructure |
| **Hybrid Cloud Engineering** | - Storage SW<br/>- Storage HW<br/>- Switches<br/>- Converged Systems | Implementation services for storage, networking, platform engineering |
| **Data, AI & IOT** | - Storage SW (data platform)<br/>- Compute (ML workloads) | Data platform services, analytics infrastructure |

---

## 💡 Key Connections Discovered

### 1. Migration Services (Strongest Connection)

**Services Sheet** provides 31 different migration services:
- Workload migration (any-to-any)
- Platform migration (Red Hat, SUSE, etc.)
- Storage migration (block, file)
- SAN fabric migration
- Cloud migration (VMware to Azure, etc.)

**LS_SKU Sheet** maps "Migration" to products:
- Primera (migration service available)
- Alletra (migration service available)
- Alletra MP (migration service available)
- StoreOnce (migration service available)
- SimpliVity (workload migration)

**Connection**: Services sheet describes WHAT migrations are offered; LS_SKU shows WHICH products support migration services

### 2. Health Check / Assessment Services

**Services Sheet**:
- Compute environment analysis services
- Storage Performance Analysis
- Backup Efficiency Analysis
- Migration Readiness Assessment

**LS_SKU Sheet** (with SKU codes):
- Health Check (H9Q53AC) - applies to 3PAR, Primera, Alletra, MSA
- Health Check (HM006A1/HM006AE/HM006AC) - for StoreOnce
- Gap Analysis - for MSA, MSL

**Connection**: LS_SKU provides **SKU codes** for health check services described in Services sheet

### 3. Installation & Deployment

**Services Sheet**:
- Design and Deployment of HPE Compute
- Deploy and Configure HPE Compute Hardware
- Design and Deployment of Alletra/Primera/3PAR/Nimble/MSA Storage

**LS_SKU Sheet** (with SKU codes):
- Install & Startup - for all storage products
- Install & Startup (HL997A1) - for servers
- OS deployment (H6K67A1) - for servers

**Connection**: Services catalog describes comprehensive deployment offerings; LS_SKU provides specific product install services with SKUs

### 4. Configuration Services

**Services Sheet**:
- Configuration and Optimization services
- VMware Metro Cluster Configuration
- Remote Copy configuration
- File Persona configuration

**LS_SKU Sheet** (with SKU codes):
- Remote Copy configuration (HA124A1#5QV/HA124A1#5Y8/HA124A1#5U2)
- Replication configuration (HA124A1#58E)
- File Persona configuration
- OneView configuration (H6K67A1)

**Connection**: **Exact match** - Same configuration services appear in both sheets, LS_SKU adds SKU codes

### 5. Upgrade Services

**Services Sheet**:
- Private Cloud Upgrade Solutions
- ESXi / vCenter Upgrade
- MS / Hyper-V Upgrade
- Platform Upgrade (Red Hat, SUSE, etc.)
- ISV version upgrades

**LS_SKU Sheet** (with SKU codes):
- OS upgrade (HM002A1/HM002AE/HM002AC) - for storage
- Firmware upgrade (HL997A1) - for servers
- HW upgrade - for storage platforms

**Connection**: Services describes business-level upgrades; LS_SKU provides product-specific upgrade SKUs

---

## 🔧 Practical Integration Opportunities

### Use Case 1: Enhanced Service Recommendations

**Current State** (from DATA_RELATIONSHIPS_ANALYSIS.md):
```
Install Base: HP DL360p Gen8 Server (expired warranty)
   ↓ Keyword match
LS_SKU: Compute → Servers
   ↓ Available services
Recommendations:
  - Health Check (HL997A1)
  - Firmware upgrade (HL997A1)
  - OS deployment (H6K67A1)
```

**Enhanced with Services Sheet**:
```
Install Base: HP DL360p Gen8 Server (expired warranty)
   ↓ Keyword match
LS_SKU: Compute → Servers
   ↓ Service names + SKU codes
   ↓ Map to Services catalog
Services Sheet Practice: Hybrid Cloud Engineering
   ↓ Find related services
Enhanced Recommendations:
  1. Health Check (HL997A1) - "Compute environment analysis services"
  2. Firmware upgrade (HL997A1) - "Performance and Firmware Analysis"
  3. OS deployment (H6K67A1) - "Platform deployment, upgrade, migration"
  4. PLUS Strategic Services:
     - "HPE Compute Transformation" (from Services sheet)
     - "Monitoring and Management tools deployment" (from Services sheet)
```

### Use Case 2: Practice-Based Service Bundling

**Scenario**: Account 56088 has storage products reaching EOL

**Step 1**: Identify from Install Base
- 3PAR storage devices (EOL approaching)

**Step 2**: Map to LS_SKU
- Product: 3PAR
- Category: Storage SW, Storage HW
- Available services:
  - OS upgrade (HM002A1)
  - Health Check (H9Q53AC)
  - Performance Analysis (HM2P6A1#001)
  - Migration services

**Step 3**: Enrich from Services Sheet
- Practice: Hybrid Cloud Engineering
- Sub-Practice: Storage
- Related services:
  - Storage Performance Analysis
  - HPE Data Migration Readiness Assessment
  - Design and Deployment of Alletra/Primera
  - Storage Block Data Migration

**Step 4**: Build Bundle
```
EOL Migration Package:
  Assessment Phase:
    - Health Check (H9Q53AC) - $X,XXX
    - Storage Performance Analysis - $X,XXX
    - HPE Data Migration Readiness Assessment - $X,XXX

  Migration Phase:
    - Storage Block Data Migration using HPE Tools - $XX,XXX
    - Design and Deployment of Primera - $XX,XXX

  Post-Migration:
    - Performance Analysis (HM2P6A1#001) - $X,XXX
    - Training and knowledge transfer - $X,XXX

Total Package Value: $XXX,XXX
```

### Use Case 3: A&PS Project → Service Catalog Lookup

**Scenario**: Account 56769 has 377 historical projects

**Query**:
```sql
-- Find which services this account has purchased before
SELECT
  ap.prj_description,
  ap.prj_practice,
  ap.project_length_days,
  ap.start_date,
  ap.end_date
FROM aps_project ap
WHERE ap.st_id = 56769
  AND ap.prj_description LIKE '%migration%'
ORDER BY ap.start_date DESC;
```

**Analysis**:
- Account has 15 migration projects historically
- Primary practice: CLD & PLT (Cloud & Platform)
- Average project length: 120 days

**Map to Services Sheet**:
- Practice: Hybrid Cloud Engineering
- Migration services purchased:
  - Workload Migration
  - Platform Migration
  - Storage Migration

**Map to LS_SKU** (for current Install Base):
- Products owned: Aruba APs, DL servers
- Migration services available:
  - Compute migration services
  - Network migration services

**Recommendation**:
"Customer has strong migration experience (15 historical projects). Current refresh opportunity for DL servers. Recommend Migration + Deployment bundle based on past success pattern."

---

## 📋 Mapping Table: Services ↔ LS_SKU

### High-Confidence Direct Mappings

| Service Category | Services Sheet Description | LS_SKU Service Name | LS_SKU SKU Code | Applies to Products |
|-----------------|---------------------------|---------------------|----------------|-------------------|
| **Health Checks** | Storage Performance Analysis | Performance Analysis | HM2P6A1#001 | 3PAR, Primera, Alletra, Alletra MP |
| | Compute environment analysis | Health Check | HL997A1 | Servers |
| | | Health Check | H9Q53AC | Storage products |
| **Migration** | HPE Compute Migration Services | Migration | N/A | Primera, Alletra, SimpliVity |
| | Storage Block Data Migration | Migration | N/A | Storage products |
| | Workload Migration (any-to-any) | Workload Migration | N/A | SimpliVity |
| **Installation** | Design and Deployment of HPE Compute | Install & Startup | HL997A1 | Servers |
| | Design and Deployment of Storage | Install & Startup | N/A | 3PAR, Primera, Alletra, Nimble |
| **Configuration** | VMware Metro Cluster Configuration | Peer Persistence | N/A | 3PAR |
| | | Remote Copy configuration | HA124A1#5QV/5Y8/5U2 | 3PAR, Primera, Alletra |
| | | File Persona configuration | N/A | 3PAR |
| | | OneView configuration | H6K67A1 | Servers |
| **Upgrades** | Platform Upgrade Services | OS upgrade | HM002A1/HM002AE/HM002AC | Storage SW |
| | Firmware Updates | Firmware upgrade | HL997A1 | Servers |
| | | HW upgrade | HA124A1#5Q3/5Q4/5PJ | Primera, Alletra |
| **Integration** | HPE StoreOnce Integration | StoreOnce Integration | N/A | StoreOnce |
| | Backup Solution Integration | Integration services | N/A | Various |
| **Optimization** | Data Optimization | Data Optimization services | HA124A1#5XA | 3PAR |
| | Performance Analysis | Performance Analysis | HM2P6A1#001 | Storage |
| | Storage Rebalance | Rebalance Services | HA124A1#5SV/5WC | 3PAR, Primera, Alletra |

---

## 🎯 Recommendations

### 1. Create Unified Service Catalog

**Combine both sources for complete view**:

```
Unified Service Entry:
  - Service Name: "Storage Health Check"
  - Practice: "Hybrid Cloud Engineering" (from Services sheet)
  - Sub-Practice: "Storage" (from Services sheet)
  - Description: "Storage Performance Analysis" (from Services sheet)
  - SKU Code: "HM2P6A1#001" (from LS_SKU)
  - Applicable Products: "3PAR, Primera, Alletra, Alletra MP" (from LS_SKU)
  - Category: "Storage SW" (from LS_SKU)
```

### 2. Build Service Recommendation Engine

**Logic**:
1. Start with Install Base product
2. Match to LS_SKU category/product
3. Get available services with SKU codes
4. Enrich with Services sheet descriptions
5. Add practice context for bundling
6. Include historical A&PS project data for validation

### 3. Data Integration Approach

**Database Schema**:
```sql
CREATE TABLE unified_service_catalog (
  id INTEGER PRIMARY KEY,
  service_name VARCHAR(255),
  service_description TEXT,  -- From Services sheet
  practice VARCHAR(100),      -- From Services sheet
  sub_practice VARCHAR(100),  -- From Services sheet
  sku_code VARCHAR(50),       -- From LS_SKU
  product_family VARCHAR(100),-- From LS_SKU
  product_category VARCHAR(50),-- From LS_SKU
  service_type VARCHAR(50),   -- Health Check, Migration, etc.
  created_at DATETIME
);

-- Mapping table
CREATE TABLE service_product_mapping (
  service_id INTEGER,
  product_family VARCHAR(100),
  FOREIGN KEY (service_id) REFERENCES unified_service_catalog(id)
);
```

### 4. Fuzzy Matching Configuration

**Recommended approach** (from analysis):
- **High confidence (85%+)**: Automatic mapping
- **Medium confidence (70-84%)**: Manual review required
- **Low confidence (60-69%)**: Flag for expert validation

### 5. Missing Services Identification

**Services in catalog but not in LS_SKU**:
- Data/AI services (analytics, ML, IoT)
- Consulting services (assessment, advisory)
- Cloud-native services (containers, Kubernetes)
- Application development services

**Action**: These may need separate SKU codes or different quoting process

**LS_SKU services not in catalog**:
- Some product-specific technical services
- Niche configuration services

**Action**: May be bundled into larger service offerings

---

## 📊 Summary Statistics

| Metric | Value |
|--------|-------|
| **Services Sheet services** | 286 |
| **LS_SKU service entries** | 152 |
| **High-confidence matches (85%+)** | 71 (24.8%) |
| **Medium-confidence matches (70-84%)** | 73 (25.5%) |
| **Potential matches (60-69%)** | 86 (30.1%) |
| **Total connection rate** | 80.4% |
| **Common keywords** | 11 |
| **Services with SKU codes (LS_SKU)** | 37 |

---

## 🔄 Integration with Existing OneLead Data Model

### Updated Relationship Diagram

```
Install Base (Product owned)
    ↓ Product keyword matching
LS_SKU (Product → Services + SKU codes)
    ↓ Service name fuzzy matching
Services Catalog (Service → Practice + Description)
    ↓ Historical validation
A&PS Projects (Past service delivery)
    ↓ Generate recommendations
Opportunity (Proposed services)
```

### Complete Flow Example

```
Account 56088:

[1] Install Base
  → 3PAR Storage (EOL approaching)
  → Support Status: Expired

[2] LS_SKU Lookup
  → Product: 3PAR
  → Available Services:
     - Health Check (H9Q53AC)
     - Migration
     - Performance Analysis (HM2P6A1#001)

[3] Services Catalog Enrichment
  → Practice: Hybrid Cloud Engineering
  → Related Services:
     - "Storage Performance Analysis"
     - "HPE Data Migration Readiness Assessment"
     - "Design and Deployment of Alletra/Primera"

[4] A&PS Historical Check
  → Query: SELECT * FROM projects WHERE st_id=56088 AND description LIKE '%storage%'
  → Found: 50 storage-related projects
  → Success rate: 95% healthy projects
  → Preferred practice: CLD & PLT

[5] Generate Recommendation
  Recommendation Bundle:
    Assessment:
      - Health Check (H9Q53AC) - $5,000
      - Storage Performance Analysis - $8,000

    Migration Path:
      - Migration Readiness Assessment - $10,000
      - Storage Migration to Alletra - $75,000
      - Install & Startup - $15,000

  Total Value: $113,000
  Confidence: HIGH (based on 50 successful past projects)
  Practice: Hybrid Cloud Engineering
  Estimated Duration: 90 days (based on historical average)
```

---

## ✅ Conclusion

**YES, there are strong connections between the sheets!**

The Services sheet and LS_SKU sheet are **highly complementary**:

- **LS_SKU**: Product-centric, tactical, includes SKU codes for ordering
- **Services Catalog**: Practice-centric, strategic, provides detailed descriptions
- **Together**: Complete service offering mapped to products with SKU codes and practice context

**Connection Rate**: 80.4% of services have mappings

**Business Value**:
1. ✅ Product-driven service recommendations (what services for which products)
2. ✅ SKU codes for quoting (from LS_SKU)
3. ✅ Practice context for bundling (from Services)
4. ✅ Historical validation (from A&PS Projects)

This mapping should be **integrated into the OneLead recommendation engine** to provide comprehensive, SKU-coded service recommendations organized by practice area.

---

**Related Documentation**:
- `DATA_RELATIONSHIPS_ANALYSIS.md` - Overall data model
- `FUZZY_LOGIC_USAGE.md` - Fuzzy matching implementation
- Analysis script: `analyze_services_connection.py`
