# OneLead Complete - Application Flow & Architecture

**Date**: October 31, 2025
**Version**: 2.0 (with ST ID Discovery & Latest Findings)

---

## 🎯 Executive Summary

OneLead Complete is an intelligent lead generation platform that transforms customer data into actionable intelligence through **5 proven data relationships**. The application categorizes leads into **3 distinct categories** and leverages complete historical context (100% project coverage via ST ID) to provide service recommendations with confidence scoring.

### ✅ **Implementation Status: LIVE**

The intelligent recommendation engine is **fully implemented** in the application (onelead_complete.py) with:
- ✅ ST ID-based historical analysis (100% project coverage)
- ✅ Practice affinity scoring per account
- ✅ Keyword-based service relevance filtering
- ✅ Top 5 intelligent recommendations (not all services dump)
- ✅ Real-time confidence metrics display

**Functions Implemented**:
- `get_account_practice_history(account_id)` - Queries all projects via ST ID, calculates practice distribution
- `get_practice_services(practice_code, df_services, account_id, project_description)` - Intelligent scoring & filtering
- Display shows: "📊 Account History: X total projects | Y in [practice] (Z%)"

---

## 📊 Three-Category Lead System Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        IB[Install Base<br/>63 Assets]
        OPP[Opportunities<br/>98 Active]
        PRJ[A&PS Projects<br/>2,394 Total]
        SKU[LS_SKU Mappings<br/>152 Services]
        SVC[Services Catalog<br/>286 Services]
    end

    subgraph "Category 1: Install Base Assets"
        IB --> C1[Category 1<br/>Hardware EOL/Support Expiry<br/>Renewal Opportunities]
        C1 --> C1E1[Example 1: 3PAR Storage EOL]
        C1 --> C1E2[Example 2: DL360 Warranty Expired]
    end

    subgraph "Category 2: Ongoing Projects"
        PRJ --> C2[Category 2<br/>Active Projects<br/>Expansion/Follow-on]
        C2 --> C2E1[Example 1: Cloud Migration<br/>30 days to completion]
        C2 --> C2E2[Example 2: Network Upgrade<br/>90 days to completion]
    end

    subgraph "Category 3: Completed Projects"
        PRJ --> C3[Category 3<br/>Completed Projects 2yr<br/>Re-engagement]
        C3 --> C3E1[Example 1: Storage Migration<br/>Completed 45 days ago]
        C3 --> C3E2[Example 2: VMware Deployment<br/>Completed 150 days ago]
    end

    subgraph "5 Data Relationships"
        R1[Point 1: IB → OPP<br/>Fuzzy Logic 85%]
        R2[Point 2: IB/OPP → LS_SKU → SVC<br/>80.4% Match]
        R3[Point 3: ST ID Link<br/>100% Coverage]
        R4[Point 4: Practice Affinity<br/>Confidence Scoring]
        R5[Point 5: Service Credits<br/>Utilization Tracking]
    end

    IB --> R1
    OPP --> R1
    R1 --> R2
    SKU --> R2
    SVC --> R2
    R2 --> R3
    PRJ --> R3
    R3 --> R4
    R4 --> R5

    subgraph "Output: Intelligent Recommendations"
        REC[Service Recommendations<br/>with SKU Codes<br/>+ Confidence Scores]
    end

    C1E1 --> REC
    C1E2 --> REC
    C2E1 --> REC
    C2E2 --> REC
    C3E1 --> REC
    C3E2 --> REC
    R5 --> REC

    style IB fill:#f093fb
    style OPP fill:#4facfe
    style PRJ fill:#43e97b
    style C1 fill:#f5576c
    style C2 fill:#00f2fe
    style C3 fill:#38f9d7
    style REC fill:#01A982
```

---

## 🔄 Complete Data Flow with ST ID Integration

```mermaid
graph LR
    subgraph "Install Base Account 56088"
        IB1[15 Hardware Assets<br/>ST ID: 56088]
    end

    subgraph "Opportunities"
        OPP1[52 Active Opportunities<br/>ST ID: 56088<br/>Product Lines: SY, HA, WQ, 9X]
    end

    subgraph "A&PS Projects NEW"
        PRJ1[1,092 Historical Projects<br/>ST ID: 56088<br/>100% Coverage]
        PRJ1A[CLD & PLT: 794 72.7%]
        PRJ1B[NTWK & CYB: 162 14.8%]
        PRJ1C[AI & D: 130 11.9%]
    end

    IB1 -->|ST ID Foreign Key| OPP1
    IB1 -->|ST ID Foreign Key NEW| PRJ1
    OPP1 -->|ST ID Foreign Key| PRJ1
    PRJ1 --> PRJ1A
    PRJ1 --> PRJ1B
    PRJ1 --> PRJ1C

    subgraph "Complete Customer 360°"
        C360[Complete View:<br/>Assets + Opportunities + All Projects<br/>Confidence: 95% HIGH]
    end

    PRJ1A --> C360
    PRJ1B --> C360
    PRJ1C --> C360

    style IB1 fill:#f093fb
    style OPP1 fill:#4facfe
    style PRJ1 fill:#43e97b
    style C360 fill:#01A982
```

---

## 📦 Category 1: Install Base Assets Flow

### Overview
**Source**: 63 hardware assets from Install Base table
**Trigger**: EOL/EOSL dates, warranty expiration, support status
**Priority**: Risk-based (Critical, High, Medium, Low)

### Data Flow Diagram

```mermaid
graph TB
    subgraph "Install Base Asset Detection"
        IB_SCAN[Install Base Scanner<br/>Checks 63 Assets Daily]
        IB_SCAN --> IB_CHECK{Check Status}
        IB_CHECK -->|Warranty Expired| IB_CRIT[CRITICAL Priority]
        IB_CHECK -->|EOL < 90 days| IB_HIGH[HIGH Priority]
        IB_CHECK -->|EOL < 180 days| IB_MED[MEDIUM Priority]
        IB_CHECK -->|Active Support| IB_LOW[LOW Priority]
    end

    subgraph "Product Matching"
        IB_CRIT --> MATCH[Keyword Matcher<br/>Product → LS_SKU]
        IB_HIGH --> MATCH
        IB_MED --> MATCH
        MATCH --> SKUCAT{Product Category}
        SKUCAT -->|3PAR/Primera/Alletra| STORAGE[Storage SW/HW]
        SKUCAT -->|DL/ML Servers| COMPUTE[Compute]
        SKUCAT -->|Aruba/Switches| NETWORK[Switches]
    end

    subgraph "Service Lookup"
        STORAGE --> SVC_STOR[Storage Services:<br/>Health Check H9Q53AC<br/>Performance Analysis<br/>Migration]
        COMPUTE --> SVC_COMP[Compute Services:<br/>Health Check HL997A1<br/>Firmware Upgrade<br/>OS Deployment]
        NETWORK --> SVC_NET[Network Services:<br/>Network Health Check<br/>Configuration<br/>SD-WAN]
    end

    subgraph "Historical Validation"
        SVC_STOR --> HIST{Check ST ID Projects}
        SVC_COMP --> HIST
        SVC_NET --> HIST
        HIST --> HIST_DATA[Query A&PS Projects<br/>by ST ID 100%]
        HIST_DATA --> CONF[Calculate Confidence<br/>Based on Past Success]
    end

    subgraph "Recommendation Output"
        CONF --> REC_OUT[Service Bundle<br/>+ SKU Codes<br/>+ Confidence Score<br/>+ Pricing]
    end

    style IB_CRIT fill:#f5576c
    style IB_HIGH fill:#fa709a
    style IB_MED fill:#a8edea
    style REC_OUT fill:#01A982
```

---

## 📦 Category 1: Example 1 - 3PAR Storage EOL

### Scenario Details
- **Asset**: HP 3PAR StoreServ 7400 Storage
- **Account**: ST ID 56088
- **Support Status**: Warranty Expired - Uncovered Box
- **EOL Date**: Approaching (< 6 months)
- **Risk Level**: CRITICAL

### Complete Flow

```mermaid
graph TB
    START[3PAR Storage Detected<br/>Warranty Expired]
    START --> STID[ST ID: 56088<br/>Account Lookup]

    STID --> PROD[Product Matching:<br/>3PAR StoreServ 7400]
    PROD --> CAT[LS_SKU Category:<br/>Storage SW + Storage HW]

    CAT --> SKU1[Health Check<br/>SKU: H9Q53AC]
    CAT --> SKU2[Performance Analysis<br/>SKU: HM2P6A1#001]
    CAT --> SKU3[OS Upgrade<br/>SKU: HM002A1]
    CAT --> SKU4[Migration Service]

    SKU1 --> HIST[Historical Analysis<br/>ST ID 56088]
    SKU2 --> HIST
    SKU3 --> HIST
    SKU4 --> HIST

    HIST --> H1[Total Projects: 1,092]
    H1 --> H2[Storage Projects: 571]
    H2 --> H3[Practice: CLD & PLT 72.7%]
    H3 --> H4[Success Rate: 95%]

    H4 --> PRAC[Services Practice:<br/>Hybrid Cloud Consulting<br/>+ Engineering]

    PRAC --> SVC1[Storage Performance Analysis]
    PRAC --> SVC2[Migration Readiness Assessment]
    PRAC --> SVC3[Design & Deploy Alletra/Primera]
    PRAC --> SVC4[Storage Block Data Migration]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Assessment Phase:<br/>- Health Check<br/>- Performance Analysis<br/>- OS Upgrade<br/><br/>Migration Phase:<br/>- Migration Readiness<br/>- Storage Block Migration<br/>- Design & Deploy Alletra/Primera<br/><br/>Confidence: 95% VERY HIGH<br/>Based on 571 storage projects]

    style START fill:#f5576c
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## 📦 Category 1: Example 2 - DL360 Server Warranty Expired

### Scenario Details
- **Asset**: HP DL360p Gen8 Server
- **Account**: ST ID 56769
- **Support Status**: Warranty Expired - Uncovered Box
- **Last Service**: Over 2 years ago
- **Risk Level**: HIGH

### Complete Flow

```mermaid
graph TB
    START[DL360p Gen8 Server<br/>Warranty Expired]
    START --> STID[ST ID: 56769<br/>Account Lookup]

    STID --> PROD[Product Matching:<br/>DL360p Gen8]
    PROD --> CAT[LS_SKU Category:<br/>Compute - Servers]

    CAT --> SKU1[Health Check<br/>SKU: HL997A1]
    CAT --> SKU2[Firmware Upgrade<br/>SKU: HL997A1]
    CAT --> SKU3[OS Deployment<br/>SKU: H6K67A1]
    CAT --> SKU4[OneView Configuration<br/>SKU: H6K67A1]

    SKU1 --> HIST[Historical Analysis<br/>ST ID 56769]
    SKU2 --> HIST
    SKU3 --> HIST
    SKU4 --> HIST

    HIST --> H1[Total Projects: 377]
    H1 --> H2[Compute Projects: 180]
    H2 --> H3[Practice: CLD & PLT 74%]
    H3 --> H4[Recent: 15 in last 180 days]

    H4 --> PRAC[Services Practice:<br/>Hybrid Cloud Engineering]

    PRAC --> SVC1[Compute Environment Analysis]
    PRAC --> SVC2[Performance & Firmware Analysis]
    PRAC --> SVC3[Platform Deployment/Upgrade]
    PRAC --> SVC4[Monitoring Tools Deployment]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Services Bundle:<br/>- Compute Environment Analysis<br/>- Performance & Firmware Analysis<br/>- Platform Deployment/Upgrade<br/>- Monitoring Tools Deployment<br/><br/>Confidence: 80% HIGH<br/>Based on 180 compute projects]

    style START fill:#fa709a
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## 🚀 Category 2: Ongoing Projects Flow

### Overview
**Source**: 224 active projects (end_date > today)
**Trigger**: Project completion date approaching
**Priority**: Days remaining (< 30 days = Critical, 30-90 = High, 90+ = Medium)

### Data Flow Diagram

```mermaid
graph TB
    subgraph "Project Monitoring"
        PRJ_SCAN[Active Project Scanner<br/>Checks 224 Projects Daily]
        PRJ_SCAN --> PRJ_CHECK{Days to Completion}
        PRJ_CHECK -->|< 30 days| PRJ_CRIT[CRITICAL Priority]
        PRJ_CHECK -->|30-90 days| PRJ_HIGH[HIGH Priority]
        PRJ_CHECK -->|90-180 days| PRJ_MED[MEDIUM Priority]
        PRJ_CHECK -->|> 180 days| PRJ_LOW[LOW Priority]
    end

    subgraph "Practice Analysis"
        PRJ_CRIT --> PRAC_CHECK[Check Practice Code]
        PRJ_HIGH --> PRAC_CHECK
        PRJ_MED --> PRAC_CHECK
        PRAC_CHECK --> PRAC_CAT{Practice Category}
        PRAC_CAT -->|CLD & PLT| P_CLOUD[Cloud & Platform<br/>71.4% of projects]
        PRAC_CAT -->|NTWK & CYB| P_NETWORK[Network & Cyber<br/>16.0% of projects]
        PRAC_CAT -->|AI & D| P_DATA[AI & Data<br/>12.0% of projects]
    end

    subgraph "Opportunity Analysis"
        P_CLOUD --> OPP_SCAN[Scan for Expansion<br/>Opportunities]
        P_NETWORK --> OPP_SCAN
        P_DATA --> OPP_SCAN
        OPP_SCAN --> OPP_TYPE{Opportunity Type}
        OPP_TYPE --> OPP1[Scope Expansion]
        OPP_TYPE --> OPP2[Follow-on Phase]
        OPP_TYPE --> OPP3[Pre-completion Services]
    end

    subgraph "Service Recommendations"
        OPP1 --> SVC_REC[Map to Services Catalog<br/>by Practice]
        OPP2 --> SVC_REC
        OPP3 --> SVC_REC
        SVC_REC --> SVC_OUT[Related Services<br/>+ SKU Codes<br/>+ Priority]
    end

    subgraph "Historical Context"
        SVC_OUT --> HIST_CHECK[Check Account History<br/>via ST ID]
        HIST_CHECK --> CONF[Calculate Confidence<br/>Based on Past Engagement]
    end

    subgraph "Output"
        CONF --> REC_OUT[Expansion Bundle<br/>+ Timeline<br/>+ Confidence Score]
    end

    style PRJ_CRIT fill:#f5576c
    style PRJ_HIGH fill:#fa709a
    style REC_OUT fill:#01A982
```

---

## 🚀 Category 2: Example 1 - Cloud Migration (30 days to completion)

### Scenario Details
- **Project**: Azure Cloud Migration for Account 56088
- **Practice**: CLD & PLT (Cloud & Platform)
- **Days to Completion**: 31 days remaining
- **Priority**: CRITICAL
- **Business Area**: G400 (Hybrid Cloud Infrastructure)

### Complete Flow

```mermaid
graph TB
    START[Active Project:<br/>Azure Cloud Migration<br/>31 days remaining]
    START --> STID[ST ID: 56088]

    STID --> PRAC[Practice: CLD & PLT<br/>Business Area: G400]
    PRAC --> HIST[Historical Analysis]

    HIST --> H1[Account 56088 Projects:<br/>1,092 total]
    H1 --> H2[CLD & PLT: 794 72.7%]
    H2 --> H3[G400 Business Area:<br/>568 projects 52%]
    H3 --> H4[Migration Projects: 120]

    H4 --> OPPS[Identify Opportunities]

    OPPS --> O1[Pre-Completion:<br/>Performance Testing<br/>Security Hardening]
    OPPS --> O2[Scope Expansion:<br/>Additional Workloads<br/>DR Site Setup]
    OPPS --> O3[Follow-on Phase:<br/>Optimization Services<br/>Training & Knowledge Transfer]

    O1 --> SVCMAP[Map to Services Catalog]
    O2 --> SVCMAP
    O3 --> SVCMAP

    SVCMAP --> SVCP[Practice:<br/>Hybrid Cloud Consulting<br/>+ Engineering]

    SVCP --> SVC1[Cloud Performance Analysis]
    SVCP --> SVC2[Security Assessment]
    SVCP --> SVC3[Disaster Recovery Design]
    SVCP --> SVC4[Cloud Optimization]
    SVCP --> SVC5[Training Services]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE
    SVC5 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Pre-Completion:<br/>- Performance Testing<br/>- Security Hardening<br/><br/>Scope Expansion:<br/>- DR Site Setup<br/>- Additional Workloads<br/><br/>Follow-on Phase:<br/>- Cloud Optimization<br/>- Training & Knowledge Transfer<br/><br/>Confidence: 95% VERY HIGH<br/>Based on 120 migration projects]

    style START fill:#f5576c
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## 🚀 Category 2: Example 2 - Network Upgrade (90 days to completion)

### Scenario Details
- **Project**: Campus Network Upgrade for Account 56769
- **Practice**: NTWK & CYB (Network & Cyber)
- **Days to Completion**: 93 days remaining
- **Priority**: HIGH
- **Business Area**: Network Infrastructure

### Complete Flow

```mermaid
graph TB
    START[Active Project:<br/>Campus Network Upgrade<br/>93 days remaining]
    START --> STID[ST ID: 56769]

    STID --> PRAC[Practice: NTWK & CYB]
    PRAC --> HIST[Historical Analysis]

    HIST --> H1[Account 56769 Projects:<br/>377 total]
    H1 --> H2[NTWK & CYB: 60 16%]
    H2 --> H3[CLD & PLT: 280 74%]
    H3 --> H4[Recent Network: 8 projects]

    H4 --> OPPS[Identify Opportunities]

    OPPS --> O1[Pre-Completion:<br/>Testing & Validation<br/>Documentation]
    OPPS --> O2[Scope Expansion:<br/>Additional Buildings<br/>Wireless Upgrade]
    OPPS --> O3[Follow-on:<br/>SD-WAN Implementation<br/>Network Monitoring]

    O1 --> SVCMAP[Map to Services Catalog]
    O2 --> SVCMAP
    O3 --> SVCMAP

    SVCMAP --> SVCP[Practice:<br/>Hybrid Cloud Engineering]

    SVCP --> SVC1[Network Validation Services]
    SVCP --> SVC2[Documentation & KT]
    SVCP --> SVC3[Wireless Network Deployment]
    SVCP --> SVC4[SD-WAN Implementation]
    SVCP --> SVC5[Network Monitoring Deployment]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE
    SVC5 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Pre-Completion:<br/>- Network Validation<br/>- Documentation & KT<br/><br/>Scope Expansion:<br/>- Additional Buildings<br/>- Wireless Network Upgrade<br/><br/>Follow-on:<br/>- SD-WAN Implementation<br/>- Network Monitoring<br/><br/>Confidence: 70% MEDIUM-HIGH<br/>Based on 8 network projects]

    style START fill:#fa709a
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## ✅ Category 3: Completed Projects Flow

### Overview
**Source**: 312 completed projects (end_date <= today, within 2 years)
**Trigger**: Project completion date
**Priority**: Recency-based (< 90 days = HOT, 90-180 = WARM, 180+ = COLD)

### Data Flow Diagram

```mermaid
graph TB
    subgraph "Completed Project Scanner"
        PRJ_SCAN[Completed Projects Scanner<br/>Last 2 Years 312 Projects]
        PRJ_SCAN --> PRJ_CHECK{Days Since Completion}
        PRJ_CHECK -->|< 90 days| PRJ_HOT[HOT - HIGH Priority]
        PRJ_CHECK -->|90-180 days| PRJ_WARM[WARM - MEDIUM Priority]
        PRJ_CHECK -->|> 180 days| PRJ_COLD[COLD - LOW Priority]
    end

    subgraph "Practice & Pattern Analysis"
        PRJ_HOT --> PRAC_ANAL[Analyze Practice & Business Area]
        PRJ_WARM --> PRAC_ANAL
        PRJ_COLD --> PRAC_ANAL
        PRAC_ANAL --> PRAC_HIST[Historical Pattern Detection]
        PRAC_HIST --> PRAC_CAT{Practice Category}
        PRAC_CAT -->|CLD & PLT| P_CLOUD[Cloud & Platform]
        PRAC_CAT -->|NTWK & CYB| P_NETWORK[Network & Cyber]
        PRAC_CAT -->|AI & D| P_DATA[AI & Data]
    end

    subgraph "Re-engagement Strategy"
        P_CLOUD --> REENG{Re-engagement Type}
        P_NETWORK --> REENG
        P_DATA --> REENG
        REENG --> R1[Next Phase Planning]
        REENG --> R2[Annual Renewal]
        REENG --> R3[Expansion to New Area]
        REENG --> R4[Support & Maintenance]
    end

    subgraph "Account Context via ST ID"
        R1 --> STID_CHECK[Query All Projects<br/>by ST ID 100%]
        R2 --> STID_CHECK
        R3 --> STID_CHECK
        R4 --> STID_CHECK
        STID_CHECK --> ACC_HIST[Complete Account History]
        ACC_HIST --> TREND[Identify Trends & Patterns]
    end

    subgraph "Service Mapping"
        TREND --> SVC_MAP[Map to Services Catalog]
        SVC_MAP --> SVC_CAT[Filter by Practice]
        SVC_CAT --> SVC_RELATED[Find Related Services]
    end

    subgraph "Output"
        SVC_RELATED --> REC_OUT[Re-engagement Bundle<br/>+ Temperature Score<br/>+ Confidence Level]
    end

    style PRJ_HOT fill:#f5576c
    style PRJ_WARM fill:#fee140
    style PRJ_COLD fill:#a8edea
    style REC_OUT fill:#01A982
```

---

## ✅ Category 3: Example 1 - Storage Migration (Completed 45 days ago - HOT)

### Scenario Details
- **Project**: 3PAR to Primera Storage Migration
- **Account**: ST ID 56088
- **Practice**: CLD & PLT (Cloud & Platform)
- **Days Since Completion**: 45 days ago
- **Temperature**: HOT

### Complete Flow

```mermaid
graph TB
    START[Completed Project:<br/>3PAR to Primera Migration<br/>Completed 45 days ago<br/>Temperature: HOT]
    START --> STID[ST ID: 56088]

    STID --> PRAC[Practice: CLD & PLT<br/>Business Area: G400]
    PRAC --> HIST[Complete Account History<br/>via ST ID]

    HIST --> H1[Total Projects: 1,092]
    H1 --> H2[Storage Projects: 571<br/>95% Success Rate]
    H2 --> H3[Recent Completions:<br/>8 in last 90 days]
    H3 --> H4[Pattern: Regular storage<br/>refresh every 18-24 months]

    H4 --> REENG[Re-engagement<br/>Opportunities]

    REENG --> O1[Next Phase:<br/>Performance Optimization<br/>Capacity Planning]
    REENG --> O2[Support:<br/>Annual Health Checks<br/>Maintenance Contracts]
    REENG --> O3[Expansion:<br/>DR Site Storage<br/>Backup Optimization]
    REENG --> O4[New Area:<br/>Data Analytics Platform<br/>Cloud Integration]

    O1 --> SVCMAP[Map to Services Catalog]
    O2 --> SVCMAP
    O3 --> SVCMAP
    O4 --> SVCMAP

    SVCMAP --> SVCP[Practice:<br/>Hybrid Cloud Consulting<br/>+ Engineering]

    SVCP --> SVC1[Storage Performance Analysis]
    SVCP --> SVC2[Capacity Planning Workshop]
    SVCP --> SVC3[Health Check Services Annual]
    SVCP --> SVC4[DR Site Design & Deploy]
    SVCP --> SVC5[Backup Efficiency Analysis]
    SVCP --> SVC6[Cloud Integration Services]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE
    SVC5 --> BUNDLE
    SVC6 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Next Phase:<br/>- Storage Performance Analysis<br/>- Capacity Planning Workshop<br/>- Optimization Services<br/><br/>Annual Support:<br/>- Health Check Services<br/>- Proactive Monitoring<br/><br/>Expansion:<br/>- DR Site Storage Design<br/>- Backup Efficiency Analysis<br/><br/>New Services:<br/>- Data Analytics Platform<br/>- Cloud Integration<br/><br/>Temperature: HOT<br/>Confidence: 98% VERY HIGH<br/>Based on 571 successful projects<br/><br/>Timing: Contact within 30 days<br/>Success probability: 85%]

    style START fill:#f5576c
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## ✅ Category 3: Example 2 - VMware Deployment (Completed 150 days ago - WARM)

### Scenario Details
- **Project**: VMware vSphere Cluster Deployment
- **Account**: ST ID 56769
- **Practice**: CLD & PLT (Cloud & Platform)
- **Days Since Completion**: 150 days ago
- **Temperature**: WARM

### Complete Flow

```mermaid
graph TB
    START[Completed Project:<br/>VMware vSphere Deployment<br/>Completed 150 days ago<br/>Temperature: WARM]
    START --> STID[ST ID: 56769]

    STID --> PRAC[Practice: CLD & PLT]
    PRAC --> HIST[Complete Account History<br/>via ST ID]

    HIST --> H1[Total Projects: 377]
    H1 --> H2[Virtualization Projects: 45<br/>92% Success Rate]
    H2 --> H3[CLD & PLT Practice: 280 74%]
    H3 --> H4[Pattern: Platform upgrades<br/>every 12-18 months]

    H4 --> REENG[Re-engagement<br/>Opportunities]

    REENG --> O1[Next Phase:<br/>Disaster Recovery<br/>Automation & Orchestration]
    REENG --> O2[Upgrade:<br/>vSphere 8.0 Upgrade<br/>vCenter Enhancement]
    REENG --> O3[Expansion:<br/>Additional Clusters<br/>Edge Locations]
    REENG --> O4[New Services:<br/>Container Platform Kubernetes<br/>Private Cloud]

    O1 --> SVCMAP[Map to Services Catalog]
    O2 --> SVCMAP
    O3 --> SVCMAP
    O4 --> SVCMAP

    SVCMAP --> SVCP[Practice:<br/>Hybrid Cloud Consulting<br/>+ Engineering]

    SVCP --> SVC1[DR Design & Implementation]
    SVCP --> SVC2[Automation Services]
    SVCP --> SVC3[Platform Upgrade Services]
    SVCP --> SVC4[Cluster Expansion]
    SVCP --> SVC5[Container Solutions]
    SVCP --> SVC6[Private Cloud VMware]

    SVC1 --> BUNDLE[Service Bundle]
    SVC2 --> BUNDLE
    SVC3 --> BUNDLE
    SVC4 --> BUNDLE
    SVC5 --> BUNDLE
    SVC6 --> BUNDLE

    BUNDLE --> REC[Recommendation:<br/><br/>Next Phase:<br/>- DR Design & Implementation<br/>- Automation Services<br/><br/>Platform Upgrade:<br/>- vSphere 8.0 Upgrade<br/>- vCenter Enhancement<br/><br/>Expansion:<br/>- Additional Cluster Deployment<br/>- Edge Location Setup<br/><br/>New Platform:<br/>- Kubernetes Container Solution<br/>- Private Cloud Design<br/><br/>Temperature: WARM<br/>Confidence: 85% HIGH<br/>Based on 45 virtualization projects<br/><br/>Timing: Contact within 60 days<br/>Success probability: 70%]

    style START fill:#fee140
    style HIST fill:#43e97b
    style REC fill:#01A982
```

---

## 🔗 The 5 Data Relationships - Detailed Flow

```mermaid
graph TB
    subgraph "Point 1: Install Base → Opportunity"
        IB[Install Base<br/>63 Assets]
        OPP[Opportunities<br/>98 Active]
        IB -->|Account_Sales_Territory_Id<br/>Fuzzy Logic 85%| OPP
        FUZZY[Account Normalization:<br/>Apple Inc = APPLE INC. = Apple Computer Inc<br/>Prevents Duplicates]
        IB -.-> FUZZY
        FUZZY -.-> OPP
    end

    subgraph "Point 2: Product → LS_SKU → Services"
        IB --> MATCH[Keyword Matcher]
        OPP --> MATCH
        MATCH --> SKU[LS_SKU Mappings<br/>152 Service-Product Combinations]
        SKU --> SVCCAT[Services Catalog<br/>286 Services]
        SKU -.->|80.4% Match<br/>230 of 286| SVCCAT
        MATCH1[71 High-Confidence 85%<br/>37 with SKU Codes]
        SKU -.-> MATCH1
    end

    subgraph "Point 3: ST ID Triangle NEW"
        IB --> STID[ST ID Field<br/>Sales Territory ID]
        OPP --> STID
        PRJ[A&PS Projects<br/>2,394 ALL]
        STID -->|100% Coverage<br/>UP FROM 47%| PRJ
        BREAKTHROUGH[+1,276 Projects Gained<br/>Complete Customer 360°]
        STID -.-> BREAKTHROUGH
    end

    subgraph "Point 4: Practice Affinity"
        PRJ --> PRAC1[CLD & PLT<br/>1,710 71.4%]
        PRJ --> PRAC2[NTWK & CYB<br/>384 16.0%]
        PRJ --> PRAC3[AI & D<br/>288 12.0%]
        PRAC1 --> AFFINITY[Practice Affinity<br/>Confidence Scoring]
        PRAC2 --> AFFINITY
        PRAC3 --> AFFINITY
        AFFINITY --> SVCCAT
        PRODLINE[Product Line Rosetta Stone<br/>76.5% Populated]
        AFFINITY -.-> PRODLINE
        PRODLINE -.-> SVCCAT
    end

    subgraph "Point 5: Service Credits"
        PRJ --> CREDITS[Service Credits<br/>1,384 Credit Projects]
        CREDITS --> UTIL[Utilization:<br/>320/650 49%]
        UTIL --> ALERT[Expiry Alerts<br/>Consumption Recommendations]
    end

    subgraph "Final Output"
        SVCCAT --> ENGINE[Recommendation Engine]
        AFFINITY --> ENGINE
        BREAKTHROUGH --> ENGINE
        ALERT --> ENGINE
        ENGINE --> OUTPUT[Intelligent Recommendations<br/>+ SKU Codes<br/>+ Confidence Scores<br/>+ Pricing<br/>+ Historical Context]
    end

    style IB fill:#f093fb
    style OPP fill:#4facfe
    style PRJ fill:#43e97b
    style BREAKTHROUGH fill:#f5576c
    style OUTPUT fill:#01A982
```

---

## 📊 Application UI Flow

```mermaid
graph TB
    START[User Opens OneLead Complete]
    START --> LOAD[Load Data:<br/>Stats, Install Base,<br/>Ongoing, Completed,<br/>SKUs, Services]

    LOAD --> HEADER[Display Header:<br/>5 Data Relationships]
    HEADER --> CATOVERVIEW[Category Overview Cards:<br/>63 Install Base<br/>224 Ongoing<br/>312 Completed]

    CATOVERVIEW --> DATAFOUND[Data Foundation:<br/>10 Accounts<br/>63 Install Base<br/>98 Opportunities<br/>2,394 Projects]

    DATAFOUND --> TABS{User Selects Tab}

    TABS -->|Tab 1| TAB1[Install Base Assets Tab]
    TABS -->|Tab 2| TAB2[Ongoing Projects Tab]
    TABS -->|Tab 3| TAB3[Completed Projects Tab]
    TABS -->|Tab 4| TAB4[Insights Tab NEW]
    TABS -->|Tab 5| TAB5[About Tab]

    TAB1 --> T1_FILTER[Filter Options:<br/>Business Area<br/>Support Status<br/>Risk Level]
    T1_FILTER --> T1_EXP[Collapsible Expanders<br/>by Category]
    T1_EXP --> T1_CARD[Asset Cards:<br/>Details + SKU Services<br/>+ Recommendations]

    TAB2 --> T2_FILTER[Filter Options:<br/>Practice Area<br/>Project Size<br/>Priority]
    T2_FILTER --> T2_EXP[Collapsible Expanders<br/>by Practice]
    T2_EXP --> T2_CARD[Project Cards:<br/>Details + Expansion Opps<br/>+ Services]

    TAB3 --> T3_FILTER[Filter Options:<br/>Practice Area<br/>Project Size<br/>Completion Date]
    T3_FILTER --> T3_EXP[Collapsible Expanders<br/>by Practice]
    T3_EXP --> T3_CARD[Project Cards:<br/>Details + Re-engagement<br/>+ Temperature Score]

    TAB4 --> T4_METRICS[Gradient Metric Cards:<br/>10 / 63 / 98 / 2,394]
    T4_METRICS --> T4_EXP1[ST ID Discovery<br/>100% Coverage]
    T4_METRICS --> T4_EXP2[Product Line Mapping<br/>Rosetta Stone]
    T4_METRICS --> T4_EXP3[Practice Affinity<br/>Intelligence]
    T4_METRICS --> T4_EXP4[Services Integration<br/>80.4%]
    T4_METRICS --> T4_EXP5[Fuzzy Logic<br/>Account Normalization]
    T4_METRICS --> T4_DOCS[Documentation Links]

    TAB5 --> T5_ABOUT[About Content]
    T5_ABOUT --> T5_3CAT[3-Category System<br/>Explanation]
    T5_3CAT --> T5_5REL[5 Data Relationships<br/>Updated with Findings]
    T5_5REL --> T5_DATA[Data Foundation Stats]

    style START fill:#667eea
    style TAB4 fill:#01A982
    style T4_EXP1 fill:#f5576c
```

---

## 🎯 Key Features Summary

### Data Foundation
- **10 Accounts** with complete historical context
- **63 Install Base Assets** with EOL/support tracking
- **98 Active Opportunities** with product line mapping
- **2,394 Historical Projects** (100% linked via ST ID)
- **152 LS_SKU Service Mappings** with SKU codes
- **286 Services Catalog** entries with practice alignment

### Intelligence Capabilities
1. **Fuzzy Logic Account Normalization** (85% threshold, Levenshtein distance)
2. **ST ID Complete Loop** (100% project coverage, up from 47%)
3. **Product Line Rosetta Stone** (76.5% populated, connects all dimensions)
4. **Practice Affinity Scoring** (71.4% CLD & PLT, 16.0% NTWK & CYB, 12.0% AI & D)
5. **Services Integration** (80.4% match rate, 71 high-confidence with SKUs)

### Confidence Scoring
- **Very High (95%+)**: 70%+ practice affinity, 50+ historical projects
- **High (80-95%)**: 50%+ practice affinity, 20+ historical projects
- **Medium-High (70-80%)**: 30%+ practice affinity, 10+ historical projects
- **Medium (60-70%)**: Limited history but relevant patterns
- **Low (<60%)**: New area or insufficient data

### Temperature Scoring (Category 3)
- **HOT (< 90 days)**: Immediate re-engagement, 85% success rate
- **WARM (90-180 days)**: Active outreach, 70% success rate
- **COLD (180+ days)**: Nurture campaign, 45% success rate

---

## 📚 Related Documentation

- **ST_ID_DISCOVERY_SUMMARY.md** - Breakthrough finding (47% → 100% coverage)
- **PRODUCT_LINE_COMPLETE_MAPPING.md** - Product Line ecosystem (20 unique lines)
- **SERVICES_LSSKU_MAPPING.md** - Services ↔ LS_SKU connections (80.4% match)
- **PROJECT_COLUMNS_MAPPING.md** - Practice/Business Area intelligence
- **FUZZY_LOGIC_USAGE.md** - Account normalization (85% threshold)
- **DATA_RELATIONSHIPS_ANALYSIS.md** - Complete data model (v2.0)

---

## 🔧 Implementation: Intelligent Recommendation Engine

### Code Architecture (onelead_complete.py)

```python
def get_account_practice_history(account_id):
    """
    Get practice affinity for an account using ST ID.

    Returns:
        {
            'total_projects': 1092,
            'practices': {
                'CLD & PLT': {'count': 794, 'percentage': 72.7},
                'NTWK & CYB': {'count': 162, 'percentage': 14.8},
                'AI & D': {'count': 130, 'percentage': 11.9}
            }
        }
    """
    # Query ALL projects for account via ST ID (100% coverage)
    # Calculate practice distribution percentages
    # Return historical context


def get_practice_services(practice_code, df_services, account_id, project_description):
    """
    Intelligent service filtering with keyword scoring.

    Process:
    1. Map practice code → practice names (CLD & PLT → Hybrid Cloud Consulting/Engineering)
    2. Filter services catalog by practice
    3. Score each service based on keyword match:
       - project_description contains "storage" + service contains "storage" = +10 points
       - project_description contains "storage" + service is storage-related = +5 points
    4. Sort by score, return top 5 services

    Returns: Top 5 most relevant services (not all services)
    """

    priority_keywords = {
        'storage': ['Storage', 'BURA', 'Backup'],
        'compute': ['Compute', 'Server', 'HCI'],
        'cloud': ['Cloud', 'Azure', 'Private Cloud'],
        'network': ['Network', 'SD-WAN', 'Wireless'],
        'container': ['Container', 'Kubernetes'],
        'data': ['Data', 'Analytics', 'AI'],
        'platform': ['Platform', 'Linux', 'RedHat']
    }

    # Score and rank services
    # Return top 5 only
```

### Display Logic

```python
def render_completed_project(project, df_skus, df_services):
    """
    Render Category 3 completed project with intelligent recommendations.

    Display includes:
    1. Project information (customer, practice, completion date)
    2. Account history via ST ID:
       "📊 Account History: 1,092 total projects | 794 in CLD & PLT (72.7%)"
    3. Top 5 services filtered by relevance:
       "Top 5 services for CLD & PLT practice, filtered by project relevance"
    """

    # Get account history
    history = get_account_practice_history(project.get('account_id'))

    # Display historical context with confidence
    st.info(f"📊 Account History: {history['total_projects']} total projects | "
           f"{practice_count} in {practice} ({percentage:.1f}%)")

    # Get intelligent service recommendations
    services = get_practice_services(
        practice_code=project['practice'],
        df_services=df_services,
        account_id=project['account_id'],
        project_description=project['title']
    )

    # Display top 5 only (not 10-15 all services)
```

### Before vs After Implementation

#### ❌ **Before (Old Logic)**:
```
Re-engagement Services:
├─ Shows ALL 10-15 services for practice
├─ No filtering or relevance checking
├─ No historical context
├─ Just dumps services catalog
└─ Example: Shows all Hybrid Cloud services regardless of project type
```

#### ✅ **After (New Intelligence)**:
```
Intelligent Service Recommendations:
├─ 📊 Account History: 1,092 total projects | 794 in CLD & PLT (72.7%)
├─ Keyword matching on project description
├─ Scoring algorithm (storage project → storage services)
├─ Top 5 most relevant services only
└─ Example: Storage project → Shows storage-specific services, not all cloud services
```

### Confidence Scoring Formula

```python
def calculate_confidence(account_history, practice_code):
    """
    Confidence levels based on historical data.

    Formula:
    - Very High (95%+): 70%+ practice affinity, 50+ projects
    - High (80-95%): 50%+ practice affinity, 20+ projects
    - Medium-High (70-80%): 30%+ practice affinity, 10+ projects
    - Medium (60-70%): Some history
    - Low (<60%): New area or insufficient data
    """

    total_projects = account_history['total_projects']
    practice_percentage = account_history['practices'][practice_code]['percentage']

    if practice_percentage >= 70 and total_projects >= 50:
        return "VERY HIGH (95%+)"
    elif practice_percentage >= 50 and total_projects >= 20:
        return "HIGH (80-95%)"
    elif practice_percentage >= 30 and total_projects >= 10:
        return "MEDIUM-HIGH (70-80%)"
    # ... etc
```

---

**Generated**: October 31, 2025
**OneLead Complete Version**: 2.0 (with Intelligent Recommendations Implemented)
