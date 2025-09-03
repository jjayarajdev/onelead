# HPE OneLead Business Intelligence System

A predictive analytics platform that leverages internal HPE data to surface high-propensity "OneLead" opportunities, enabling HPE consultants to proactively engage customers with relevant solutions that have strong likelihood of conversion.

## 🎯 Objectives

- **Data-Driven Opportunity Identification**: Analyze historical and real-time HPE data to identify patterns and signals that indicate strong buying intent or solution fit
- **Customer Account-Level Insights**: Generate opportunity insights at the account level, enabling targeted outreach and personalized engagement strategies
- **Proactive Consultant Enablement**: Equip consultants with actionable intelligence to initiate meaningful conversations with customers
- **OneLead Strategy Alignment**: Support HPE's vision of driving consultative, value-led engagements that lead to measurable business outcomes

## 🏗️ System Architecture

### Data Processing Layer
- **Data Loader**: Ingests multi-sheet Excel data with comprehensive preprocessing
- **Feature Engineering**: Creates RFM scoring, urgency indicators, and customer engagement metrics
- **Data Quality**: Handles missing data, data type conversions, and validation

### Machine Learning Layer
- **Opportunity Predictor**: Gradient Boosting model for customer propensity scoring
- **Feature Importance**: Identifies key drivers of opportunity conversion
- **Synthetic Label Generation**: Creates training labels based on business rules

### Business Intelligence Layer
- **Streamlit Dashboard**: Interactive web interface for opportunity exploration
- **Consultant Recommendations**: Actionable recommendations with conversation starters
- **Executive Reporting**: High-level metrics and KPIs for leadership

## 📊 Key Features

### Opportunity Scoring
- **Propensity Levels**: High/Medium/Low classification with confidence scores
- **Urgency Scoring**: Product lifecycle and contract renewal urgency
- **RFM Analysis**: Recency, Frequency, Monetary customer segmentation

### Business Intelligence
- **Renewal Opportunities**: Product end-of-life and contract renewal tracking
- **Cross-sell Identification**: Platform diversity analysis for expansion opportunities
- **Service Expansion**: Credit utilization analysis for service growth
- **Customer Health**: Project success rates and engagement patterns

### Consultant Enablement
- **Prioritized Pipeline**: Ranked opportunities with actionable insights
- **Conversation Starters**: Personalized outreach templates
- **Action Categories**: Organized by renewal, cross-sell, service expansion
- **Risk Flags**: Early warning indicators for account risk

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure data file is in place
# Place onelead_consolidated_data_new.xlsx in data/ directory
```

### 2. Run Complete Analysis
```bash
# Execute full pipeline analysis
python run_analysis.py
```

This will:
- Load and process all data sheets
- Engineer predictive features
- Train the ML model
- Generate customer predictions
- Create consultant recommendations
- Save results to data/outputs/

### 3. Launch Interactive Dashboard
```bash
# Start Streamlit application
streamlit run src/main.py
```

Navigate to the provided URL to access the interactive dashboard.

## 📋 Dashboard Views

### Executive Dashboard
- High-level opportunity metrics
- Propensity distribution analysis
- Key performance indicators
- Top priority opportunities

### Opportunity Pipeline
- Filtered and ranked opportunities
- Confidence scoring
- Export capabilities
- Customizable views

### Customer Deep Dive
- Individual customer analysis
- Radar charts and profiling
- Personalized recommendations
- Historical engagement patterns

### Raw Data Analysis
- Comprehensive analysis of all 5 Excel data sources
- Interactive data source exploration
- Missing data analysis and quality assessment
- Business insights by data category (Install Base, Opportunities, Service Credits, Projects, Services)
- Data quality scoring and recommendations
- Export capabilities for raw data reports

### Predictive Analytics
- Model performance metrics
- Feature importance analysis
- Prediction distributions
- Cross-validation results

### Consultant Enablement
- Action-oriented opportunity lists
- Conversation starter templates
- Categorized by urgency and type
- Export for CRM integration

### Data Insights
- Data quality metrics
- Feature distributions
- Correlation analysis
- System health monitoring

## 📈 Business Impact

### For HPE Consultants
- **Prioritized Outreach**: Focus on highest-propensity opportunities
- **Personalized Engagement**: Tailored conversation starters and recommendations
- **Timing Optimization**: Proactive outreach based on urgency indicators
- **Success Tracking**: Monitor engagement outcomes and model performance

### For HPE Leadership
- **Pipeline Visibility**: Clear view of opportunity landscape
- **Resource Allocation**: Data-driven consultant assignment
- **Performance Metrics**: Track conversion rates and revenue impact
- **Strategic Planning**: Identify market trends and customer patterns

### Key Metrics Tracked
- **Opportunity Propensity**: Likelihood of customer engagement
- **Renewal Risk**: Product and contract lifecycle management
- **Cross-sell Potential**: Revenue expansion opportunities
- **Customer Health**: Engagement quality and satisfaction
- **Consultant Effectiveness**: Outreach success rates

## 🔧 Technical Architecture

### Data Sources (5 sheets, 8,838 records)
- **Install Base**: Hardware lifecycle and support tracking
- **Opportunities**: Active sales pipeline
- **Service Credits**: Service utilization and contracts
- **Projects**: Historical delivery and engagement
- **Services**: Service catalog and capabilities

### Feature Engineering (80+ features)
- **Temporal Features**: Days to expiration, engagement recency
- **Aggregation Features**: Customer totals, averages, counts
- **Risk Indicators**: EOL urgency, underutilization flags
- **Behavioral Patterns**: Success rates, diversity metrics

### ML Pipeline
- **Model**: Gradient Boosting Classifier
- **Features**: 20+ key predictive variables
- **Labels**: Business rule-based synthetic targets
- **Validation**: 5-fold cross-validation
- **Monitoring**: Feature importance tracking

## 🛡️ Security & Privacy

- **Data Protection**: Sensitive customer data handled securely
- **Access Control**: Role-based dashboard access
- **Audit Trail**: Model predictions and consultant actions logged
- **Compliance**: Follows HPE data governance standards

## 📊 Sample Outputs

### Top Opportunity Identification
```
Customer ABC123: High propensity (95% confidence)
- Action: Critical Product Renewal (30 days to EOL)
- Cross-sell: Platform expansion opportunity
- Conversation: "Your critical systems need upgrade planning..."
```

### Business Insights
```
Total Customers: 5,678
High Priority Opportunities: 234 (4.1%)
Urgent Renewals: 89 customers
Cross-sell Potential: 456 customers
Service Expansion: 123 underutilized accounts
```

This system transforms HPE's customer data into actionable intelligence, enabling consultants to deliver timely, relevant solutions that accelerate pipeline conversion and deepen customer relationships.