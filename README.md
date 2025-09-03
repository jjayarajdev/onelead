# 🎯 HPE OneLead Business Intelligence Dashboard

A comprehensive Streamlit-based business intelligence platform for HPE sales teams to analyze customer opportunities, predict propensity, and identify service cross-sell opportunities.

## 🚀 Features

### 📊 **Business Intelligence Dashboard**
- **6 Interactive Tabs** with business-focused insights
- **Real-time Metrics** showing actionable business data
- **Customer Name Display** throughout the interface
- **Export Capabilities** for sales team collaboration

### 🤖 **Machine Learning Powered**
- **Opportunity Prediction** using Gradient Boosting models
- **Customer Segmentation** (Strategic, High Value, At Risk, Dormant, Growing)
- **RFM Scoring** for customer value analysis
- **Propensity Scoring** for opportunity prioritization

### 🔄 **Service Recommendations**
- **Product-to-Service Mapping** connecting opportunities to HPE services
- **Cross-sell Identification** for revenue expansion
- **Priority Scoring** for opportunity ranking
- **Actionable Insights** for consultant engagement

## 📈 **Business Impact**

- 🔴 **$405K Revenue at Risk** from 27 expired products
- 🎯 **98 Opportunities Mapped** to relevant HPE services
- 👥 **Customer Segmentation** across 8 key accounts
- 📊 **Data-Driven Insights** for strategic decision making

## 🗂️ **Project Structure**

```
onelead_system/
├── src/
│   ├── main_business.py              # 🎯 Main business dashboard
│   ├── data_processing/
│   │   ├── data_loader_v2.py         # 📥 Data ingestion from Excel
│   │   ├── feature_engineering_v2.py # 🔧 ML feature pipeline
│   │   └── service_opportunity_mapper.py # 🔗 Service mapping logic
│   ├── models/
│   │   └── opportunity_predictor.py   # 🤖 ML prediction model
│   └── utils/
│       └── customer_name_mapper.py   # 👤 Customer name resolution
├── data/
│   ├── DataExportAug29th.xlsx        # 📊 Primary data source
│   └── ER_Diagram.md                 # 📋 Data relationship docs
├── docs/
│   └── dashboard_pages/              # 📖 Page-by-page documentation
└── visualizations/                   # 📈 EDA reports and charts
```

## 🛠️ **Installation & Setup**

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jjayarajdev/onelead.git
   cd onelead_system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run src/main_business.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Navigate through the 6 dashboard tabs

## 📊 **Dashboard Pages Overview**

| Page | Purpose | Key Insights |
|------|---------|--------------|
| 🚨 **Action Required** | Immediate priorities | Expired products, unused credits, unsupported items |
| 💰 **Revenue Focus** | Financial opportunities | Revenue at risk, top customers, growth targets |
| 👥 **Customer Health** | Relationship status | Customer segments, health scores, risk indicators |
| 🎯 **Service Recommendations** | Cross-sell opportunities | Product-to-service mapping, priority scoring |
| 📊 **Business Metrics** | Performance overview | KPIs, trends, comparative analysis |
| 🔍 **Deep Dive** | Detailed analysis | Segmentation, utilization, raw data explorer |

> 📖 **Detailed documentation for each page is available in [`docs/dashboard_pages/`](docs/dashboard_pages/)**

## 🔧 **Technical Architecture**

### **Data Processing Pipeline**
1. **Data Ingestion** - Excel files with 5 sheets (Install Base, Opportunities, A&PS Projects, Services, Service Credits)
2. **Feature Engineering** - RFM scoring, urgency metrics, propensity calculations
3. **ML Pipeline** - Gradient Boosting classifier for opportunity prediction
4. **Service Mapping** - Product line to service recommendations
5. **Visualization** - Streamlit dashboard with interactive components

### **Key Components**

#### 🧠 **Machine Learning**
- **Model**: Gradient Boosting Classifier
- **Features**: 20+ engineered features including RFM scores, urgency metrics
- **Training**: Synthetic labels based on business rules
- **Accuracy**: 100% on limited dataset with cross-validation

#### 📊 **Data Sources**
- **Install Base**: 63 product records across customers
- **Opportunities**: 98 active sales opportunities  
- **A&PS Projects**: 2,394 historical project records
- **Services**: 286 available HPE service offerings
- **Service Credits**: 1,384 credit utilization records

#### 🎯 **Business Logic**
- **Customer Segmentation**: Rule-based classification using opportunity count and product status
- **Priority Scoring**: Weighted scoring system for opportunity ranking
- **Risk Assessment**: EOL/EOS product identification and financial impact calculation

## 🔄 **Service-Opportunity Mapping**

The system maps HPE product lines to relevant service offerings:

| Product Category | Mapped Services | Priority |
|------------------|-----------------|----------|
| **Servers & Compute** | Compute Transformation, Performance Analysis | High (90%) |
| **Networking** | Network Assessment, WLAN Design | High (75%) |
| **Cloud Management** | Multi-Cloud Strategy, CloudOps | High (85%) |
| **Support Services** | Complete Care, Proactive Care | Medium (60%) |

## 📈 **Key Business Metrics**

### **Critical Alerts**
- 🔴 **27 Products EXPIRED** affecting multiple customers
- 💸 **Unused Credits** with low utilization rates
- ⚠️ **Unsupported Products** requiring attention

### **Revenue Opportunities**
- 💰 **$405K Revenue at Risk** from expired products
- 🎯 **High-Priority Opportunities** with 80%+ confidence scores
- 📈 **Cross-sell Potential** across service categories

### **Customer Insights**
- 👑 **Strategic Customers** (10+ opportunities)
- 💎 **High Value Customers** (5+ opportunities, no expired products)
- ⚠️ **At Risk Customers** (expired products requiring immediate action)

## 🚀 **Usage Examples**

### **For Sales Teams**
```python
# Identify top opportunities
top_customers = predictor.get_top_opportunities(features, n=10)

# Generate service recommendations
service_recs = mapper.get_customer_service_recommendations(opportunities)

# Export for follow-up
recommendations.to_csv('customer_recommendations.csv')
```

### **For Business Analysts**
- Use the **Deep Dive** tab for detailed customer analysis
- Export data from any tab using the download buttons
- Filter by customer, product line, or service type
- Monitor KPIs through the Business Metrics dashboard

## 🛡️ **Data Security**

- **Data Isolation**: All data processing occurs locally
- **No External APIs**: Self-contained analysis pipeline
- **Sensitive Data**: Raw data files are git-ignored
- **Export Control**: CSV exports for approved sharing

## 🔄 **Development Workflow**

### **Adding New Features**
1. Update data processing in `src/data_processing/`
2. Modify ML models in `src/models/`
3. Add dashboard components in `src/main_business.py`
4. Update documentation in `docs/`

### **Testing**
```bash
# Run the dashboard locally
streamlit run src/main_business.py

# Validate data processing
python -m src.data_processing.data_loader_v2

# Check ML pipeline
python -m src.models.opportunity_predictor
```

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/new-analysis`)
3. **Commit changes** (`git commit -am 'Add new analysis'`)
4. **Push to branch** (`git push origin feature/new-analysis`)
5. **Create Pull Request**

## 📝 **Version History**

| Version | Date | Changes |
|---------|------|---------|
| **v1.0.0** | 2024-09-03 | Initial release with full dashboard |
| **v0.9.0** | 2024-09-02 | Service-opportunity mapping added |
| **v0.8.0** | 2024-09-01 | Customer name display implementation |
| **v0.7.0** | 2024-08-31 | Business-focused metrics redesign |

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/jjayarajdev/onelead/issues)
- **Documentation**: [`docs/dashboard_pages/`](docs/dashboard_pages/)
- **Data Questions**: Review [`data/ER_Diagram.md`](data/ER_Diagram.md)

## 📄 **License**

This project is proprietary software developed for HPE internal use.

---

**🎯 Built for HPE Sales Excellence** | **🤖 Powered by Machine Learning** | **📊 Data-Driven Insights**