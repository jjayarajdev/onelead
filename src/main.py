"""
HPE OneLead Business Intelligence Dashboard
Streamlit application for opportunity identification and consultant enablement
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from data_processing.data_loader_v2 import OneleadDataLoaderV2
from data_processing.feature_engineering_v2 import OneleadFeatureEngineerV2
from models.opportunity_predictor import OpportunityPredictor

# Page configuration
st.set_page_config(
    page_title="HPE OneLead Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .high-priority {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .medium-priority {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .low-priority {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the HPE OneLead data"""
    # Use the new data file
    data_path = "data/DataExportAug29th.xlsx"
    
    # Load data with new loader
    loader = OneleadDataLoaderV2(data_path)
    processed_data = loader.process_all_data()
    
    # Engineer features with new feature engineer
    feature_engineer = OneleadFeatureEngineerV2(processed_data)
    features = feature_engineer.build_feature_set()
    
    return processed_data, features, feature_engineer

@st.cache_resource
def train_model(features):
    """Train the opportunity prediction model"""
    predictor = OpportunityPredictor()
    training_results = predictor.train_model(features)
    return predictor, training_results

def main():
    st.title("🎯 HPE OneLead Business Intelligence Dashboard")
    st.markdown("**Predictive Opportunity Intelligence for HPE Consultants**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select View",
        ["Executive Dashboard", "Opportunity Pipeline", "Customer Deep Dive", 
         "Predictive Analytics", "Consultant Enablement", "Data Insights", "Raw Data Analysis"]
    )
    
    # Load data
    try:
        with st.spinner("Loading HPE OneLead data..."):
            processed_data, features, feature_engineer = load_and_process_data()
            
        with st.spinner("Training predictive models..."):
            predictor, training_results = train_model(features)
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure the data file 'DataExportAug29th.xlsx' is in the data/ directory")
        return
    
    # Route to different pages
    if page == "Executive Dashboard":
        show_executive_dashboard(features, predictor, processed_data)
    elif page == "Opportunity Pipeline":
        show_opportunity_pipeline(features, predictor)
    elif page == "Customer Deep Dive":
        show_customer_deep_dive(features, predictor, processed_data)
    elif page == "Predictive Analytics":
        show_predictive_analytics(features, predictor, training_results)
    elif page == "Consultant Enablement":
        show_consultant_enablement(features, predictor)
    elif page == "Data Insights":
        show_data_insights(processed_data, features)
    elif page == "Raw Data Analysis":
        show_raw_data_analysis(processed_data, features)

def show_executive_dashboard(features, predictor, processed_data):
    """Executive summary dashboard"""
    st.header("📊 Executive Dashboard")
    
    # Generate insights
    insights = predictor.generate_opportunity_insights(features)
    top_opportunities = predictor.get_top_opportunities(features, n=20)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Customers",
            f"{insights['total_customers']:,}",
            help="Total customers in the database"
        )
    
    with col2:
        st.metric(
            "High Priority Opportunities",
            f"{insights['high_propensity_count']:,}",
            delta=f"+{insights['urgent_opportunities']} urgent",
            help="Customers with high conversion propensity"
        )
    
    with col3:
        st.metric(
            "Renewal Opportunities",
            f"{insights['renewal_opportunities']:,}",
            help="Customers approaching contract/product renewals"
        )
    
    with col4:
        st.metric(
            "Cross-sell Potential",
            f"{insights['cross_sell_opportunities']:,}",
            help="Customers with expansion opportunities"
        )
    
    # Opportunity distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opportunity Distribution")
        propensity_counts = [
            insights['high_propensity_count'],
            insights['medium_propensity_count'],
            insights['low_propensity_count']
        ]
        
        fig = px.pie(
            values=propensity_counts,
            names=['High', 'Medium', 'Low'],
            title="Customer Propensity Distribution",
            color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Opportunity Types")
        opp_types = {
            'Urgent Action': insights['urgent_opportunities'],
            'Renewals': insights['renewal_opportunities'],
            'Cross-sell': insights['cross_sell_opportunities'],
            'Service Expansion': insights['service_expansion_opportunities']
        }
        
        fig = px.bar(
            x=list(opp_types.keys()),
            y=list(opp_types.values()),
            title="Opportunity Categories",
            color=list(opp_types.values()),
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top opportunities table
    st.subheader("🔥 Top 20 Priority Opportunities")
    
    if not top_opportunities.empty:
        # Only include columns that actually exist
        potential_columns = [
            'customer_id', 'predicted_propensity', 'prediction_confidence',
            'urgency_score', 'rfm_score', 'total_projects', 'eol_urgency_score',
            'composite_score', 'opportunity_propensity_score'
        ]
        
        display_columns = [col for col in potential_columns if col in top_opportunities.columns]
        
        # Ensure we have at least the basic columns
        if 'customer_id' not in display_columns:
            display_columns.insert(0, 'customer_id')
        if 'predicted_propensity' not in display_columns and 'predicted_propensity' in top_opportunities.columns:
            display_columns.append('predicted_propensity')
        if 'prediction_confidence' not in display_columns and 'prediction_confidence' in top_opportunities.columns:
            display_columns.append('prediction_confidence')
        
        display_df = top_opportunities[display_columns].copy()
        
        # Format confidence column if it exists
        if 'prediction_confidence' in display_df.columns:
            display_df['prediction_confidence'] = display_df['prediction_confidence'].round(3)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
    else:
        st.info("No high-priority opportunities identified")

def show_opportunity_pipeline(features, predictor):
    """Detailed opportunity pipeline view"""
    st.header("📈 Opportunity Pipeline")
    
    # Filters
    st.sidebar.subheader("Pipeline Filters")
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.6, 0.1)
    propensity_filter = st.sidebar.multiselect(
        "Propensity Level",
        ['High', 'Medium', 'Low'],
        default=['High', 'Medium']
    )
    
    max_results = st.sidebar.slider("Max Results", 10, 200, 50, 10)
    
    # Get filtered opportunities
    all_predictions = predictor.predict_opportunity_propensity(features)
    
    filtered_opps = all_predictions[
        (all_predictions['prediction_confidence'] >= min_confidence) &
        (all_predictions['predicted_propensity'].isin(propensity_filter))
    ].head(max_results)
    
    st.subheader(f"📋 Pipeline ({len(filtered_opps)} opportunities)")
    
    # Pipeline metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_confidence = filtered_opps['prediction_confidence'].mean()
        st.metric("Average Confidence", f"{avg_confidence:.1%}")
    
    with col2:
        if 'urgency_score' in filtered_opps.columns:
            urgent_count = len(filtered_opps[filtered_opps['urgency_score'] >= 3])
        else:
            urgent_count = 0
        st.metric("Urgent Opportunities", urgent_count)
    
    with col3:
        if 'rfm_score' in filtered_opps.columns:
            high_rfm = len(filtered_opps[filtered_opps['rfm_score'] >= 6])
        else:
            high_rfm = 0
        st.metric("High-Value Customers", high_rfm)
    
    # Detailed pipeline table
    if not filtered_opps.empty:
        # Enhanced display columns
        pipeline_columns = [
            'customer_id', 'predicted_propensity', 'prediction_confidence',
            'urgency_score', 'rfm_score', 'eol_urgency_score', 'total_projects',
            'project_success_rate', 'platform_diversity', 'recent_engagement'
        ]
        
        available_columns = [col for col in pipeline_columns if col in filtered_opps.columns]
        display_pipeline = filtered_opps[available_columns].copy()
        
        # Format columns
        if 'prediction_confidence' in display_pipeline.columns:
            display_pipeline['prediction_confidence'] = display_pipeline['prediction_confidence'].apply(lambda x: f"{x:.1%}")
        
        if 'project_success_rate' in display_pipeline.columns:
            display_pipeline['project_success_rate'] = display_pipeline['project_success_rate'].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(
            display_pipeline,
            use_container_width=True,
            height=600
        )
        
        # Export functionality
        csv = display_pipeline.to_csv(index=False)
        st.download_button(
            label="📥 Download Pipeline CSV",
            data=csv,
            file_name=f"hpe_onelead_pipeline_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_customer_deep_dive(features, predictor, processed_data):
    """Individual customer analysis"""
    st.header("🔍 Customer Deep Dive")
    
    # Customer selection
    customer_ids = features['customer_id'].unique()
    selected_customer = st.selectbox("Select Customer ID", customer_ids)
    
    if selected_customer:
        # Get customer data
        customer_data = features[features['customer_id'] == selected_customer].iloc[0]
        customer_prediction = predictor.predict_opportunity_propensity(
            features[features['customer_id'] == selected_customer]
        ).iloc[0]
        
        # Customer overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Propensity Level",
                customer_prediction['predicted_propensity'],
                help="Predicted opportunity propensity"
            )
        
        with col2:
            st.metric(
                "Confidence Score",
                f"{customer_prediction['prediction_confidence']:.1%}",
                help="Model confidence in prediction"
            )
        
        with col3:
            st.metric(
                "RFM Score",
                f"{customer_data.get('rfm_score', 0):.0f}",
                help="Recency, Frequency, Monetary score"
            )
        
        # Customer details
        st.subheader("📊 Customer Profile")
        
        # Create customer profile chart
        profile_metrics = {
            'Urgency Score': customer_data.get('urgency_score', 0),
            'RFM Score': customer_data.get('rfm_score', 0),
            'Total Projects': customer_data.get('total_projects', 0),
            'Platform Diversity': customer_data.get('platform_diversity', 0),
            'Success Rate': customer_data.get('project_success_rate', 0) * 100
        }
        
        fig = go.Figure(data=go.Scatterpolar(
            r=list(profile_metrics.values()),
            theta=list(profile_metrics.keys()),
            fill='toself',
            name='Customer Profile'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(profile_metrics.values()) * 1.1]
                )),
            showlegend=False,
            title="Customer Profile Radar"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        recommendations = []
        
        if customer_data.get('eol_urgency_score', 0) >= 2:
            recommendations.append("🔴 **Product Renewal**: Customer has products approaching end-of-life")
        
        if customer_data.get('low_utilization_risk', 0) == 1:
            recommendations.append("🟡 **Service Expansion**: Customer is under-utilizing service credits")
        
        if customer_data.get('platform_diversity', 0) <= 2:
            recommendations.append("🟢 **Cross-sell Opportunity**: Customer could benefit from additional platforms")
        
        if customer_data.get('project_success_rate', 0) >= 0.8:
            recommendations.append("⭐ **Trusted Partner**: High success rate - good for larger engagements")
        
        if not recommendations:
            recommendations.append("✅ **Stable Customer**: No immediate actions required")
        
        for rec in recommendations:
            st.markdown(rec)

def show_predictive_analytics(features, predictor, training_results):
    """Model performance and analytics"""
    st.header("🤖 Predictive Analytics")
    
    # Model performance
    st.subheader("Model Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Training Accuracy",
            f"{training_results['train_accuracy']:.1%}"
        )
    
    with col2:
        st.metric(
            "Test Accuracy", 
            f"{training_results['test_accuracy']:.1%}"
        )
    
    with col3:
        cv_mean = training_results['cv_scores'].mean()
        st.metric(
            "Cross-Validation",
            f"{cv_mean:.1%}"
        )
    
    # Feature importance
    st.subheader("🎯 Feature Importance")
    
    feature_importance = training_results['feature_importance']
    
    if feature_importance:
        # Top 15 features
        top_features = dict(list(feature_importance.items())[:15])
        
        fig = px.bar(
            x=list(top_features.values()),
            y=list(top_features.keys()),
            orientation='h',
            title="Top 15 Most Important Features",
            labels={'x': 'Importance Score', 'y': 'Features'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # Prediction distribution
    st.subheader("📈 Prediction Analysis")
    
    all_predictions = predictor.predict_opportunity_propensity(features)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Confidence distribution
        fig = px.histogram(
            all_predictions,
            x='prediction_confidence',
            title="Prediction Confidence Distribution",
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Propensity vs RFM score
        fig = px.scatter(
            all_predictions,
            x='rfm_score',
            y='prediction_confidence',
            color='predicted_propensity',
            title="Propensity vs RFM Score",
            color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_consultant_enablement(features, predictor):
    """Tools and insights for HPE consultants"""
    st.header("🎓 Consultant Enablement")
    
    st.subheader("🎯 Action-Oriented Opportunities")
    
    # Get categorized opportunities
    all_predictions = predictor.predict_opportunity_propensity(features)
    
    # Define action categories with safe column access
    
    # Urgent renewals
    renewal_filter = pd.Series(False, index=all_predictions.index)
    if 'eol_urgency_score' in all_predictions.columns:
        renewal_filter |= (all_predictions['eol_urgency_score'] >= 2)
    if 'contract_renewal_urgency' in all_predictions.columns:
        renewal_filter |= (all_predictions['contract_renewal_urgency'] == 1)
    urgent_renewals = all_predictions[renewal_filter]
    
    # Cross-sell opportunities  
    cross_sell_filter = all_predictions['predicted_propensity'].isin(['High', 'Medium'])
    
    # Look for any platform-related column
    platform_cols = [col for col in all_predictions.columns if 'platform' in col.lower()]
    if platform_cols:
        platform_col = platform_cols[0]  # Use first available platform column
        cross_sell_filter &= (all_predictions[platform_col] <= 2)
    
    cross_sell_opps = all_predictions[cross_sell_filter]
    
    # Service expansion
    service_filter = all_predictions['predicted_propensity'].isin(['High', 'Medium'])
    if 'low_utilization_risk' in all_predictions.columns:
        service_filter &= (all_predictions['low_utilization_risk'] == 1)
    service_expansion = all_predictions[service_filter]
    
    # Action tabs
    tab1, tab2, tab3 = st.tabs(["🔄 Renewals", "📈 Cross-sell", "🚀 Service Expansion"])
    
    with tab1:
        st.markdown("**Customers approaching renewal deadlines**")
        if not urgent_renewals.empty:
            renewal_cols = ['customer_id', 'predicted_propensity']
            potential_cols = ['eol_urgency_score', 'days_to_contract_end', 'min_days_to_contract_end']
            
            for col in potential_cols:
                if col in urgent_renewals.columns:
                    renewal_cols.append(col)
            
            renewal_display = urgent_renewals[renewal_cols].head(20)
            st.dataframe(renewal_display, use_container_width=True)
        else:
            st.info("No urgent renewals identified")
    
    with tab2:
        st.markdown("**Customers with cross-sell potential**")
        if not cross_sell_opps.empty:
            cross_sell_cols = ['customer_id', 'predicted_propensity']
            potential_cols = ['platform_diversity', 'total_projects', 'product_platform_description_name_nunique']
            
            for col in potential_cols:
                if col in cross_sell_opps.columns:
                    cross_sell_cols.append(col)
            
            cross_sell_display = cross_sell_opps[cross_sell_cols].head(20)
            st.dataframe(cross_sell_display, use_container_width=True)
        else:
            st.info("No cross-sell opportunities identified")
    
    with tab3:
        st.markdown("**Customers under-utilizing services**")
        if not service_expansion.empty:
            service_cols = ['customer_id', 'predicted_propensity']
            potential_cols = ['avg_credit_utilization', 'total_contracts', 'low_utilization_risk']
            
            for col in potential_cols:
                if col in service_expansion.columns:
                    service_cols.append(col)
            
            service_display = service_expansion[service_cols].head(20)
            st.dataframe(service_display, use_container_width=True)
        else:
            st.info("No service expansion opportunities identified")
    
    # Conversation starters
    st.subheader("💬 Conversation Starters")
    
    conversation_starters = {
        "Product Renewal": "Hi [Customer], I noticed you have products approaching end-of-life. Let's discuss upgrade options that could improve your ROI.",
        "Service Expansion": "Based on your current utilization, there might be untapped potential in your service credits. Can we explore additional use cases?",
        "Cross-sell": "Given your success with [current platform], I'd love to show you how [new platform] could complement your existing infrastructure.",
        "Success Story": "Congratulations on the successful completion of your recent projects! Are you ready to tackle the next challenge?"
    }
    
    for scenario, starter in conversation_starters.items():
        st.markdown(f"**{scenario}**: _{starter}_")

def show_data_insights(processed_data, features):
    """Data quality and insights view"""
    st.header("📊 Data Insights")
    st.info("💡 For detailed raw data analysis, check the 'Raw Data Analysis' tab!")
    
    # Data summary
    st.subheader("Dataset Overview")
    
    # Enhanced summary with more metrics
    data_summary = {}
    for name, df in processed_data.items():
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        # Count customer presence
        customer_cols = ['account_sales_territory_id', 'prj_customer_id', 'customer_id']
        customer_count = 0
        for col in customer_cols:
            if col in df.columns:
                customer_count = df[col].nunique()
                break
        
        data_summary[name] = {
            'Records': f"{len(df):,}",
            'Columns': len(df.columns),
            'Missing %': f"{missing_pct:.1f}%",
            'Customers': customer_count if customer_count > 0 else 'N/A',
            'Quality': 'High' if missing_pct < 10 else 'Medium' if missing_pct < 25 else 'Low'
        }
    
    summary_df = pd.DataFrame(data_summary).T
    st.dataframe(summary_df, use_container_width=True)
    
    # Feature distribution
    st.subheader("Key Feature Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'urgency_score' in features.columns:
            fig = px.histogram(features, x='urgency_score', title="Urgency Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'rfm_score' in features.columns:
            fig = px.histogram(features, x='rfm_score', title="RFM Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("Feature Correlations")
    
    numeric_features = features.select_dtypes(include=[np.number]).columns
    correlation_matrix = features[numeric_features].corr()
    
    fig = px.imshow(
        correlation_matrix,
        title="Feature Correlation Heatmap",
        aspect='auto'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_raw_data_analysis(processed_data, features):
    """Comprehensive raw data analysis view"""
    st.header("🔍 Raw Data Analysis")
    st.markdown("**Deep dive into the original HPE OneLead dataset structure and content**")
    
    # Dataset overview
    st.subheader("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_records = sum(len(df) for df in processed_data.values())
    total_columns = sum(len(df.columns) for df in processed_data.values())
    
    with col1:
        st.metric("Total Records", f"{total_records:,}")
    
    with col2:
        st.metric("Data Sources", len(processed_data))
    
    with col3:
        st.metric("Total Columns", total_columns)
    
    with col4:
        st.metric("Unique Customers", len(features))
    
    # Data sources breakdown
    st.subheader("📋 Data Sources Breakdown")
    
    source_data = []
    for name, df in processed_data.items():
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        quality = "Excellent" if missing_pct < 5 else "Good" if missing_pct < 15 else "Needs Attention"
        
        source_data.append({
            'Data Source': name,
            'Records': f"{len(df):,}",
            'Columns': len(df.columns),
            'Missing Data %': f"{missing_pct:.1f}%",
            'Data Quality': quality,
            'Memory (MB)': f"{memory_mb:.1f}"
        })
    
    source_df = pd.DataFrame(source_data)
    st.dataframe(source_df, use_container_width=True)
    
    # Detailed analysis by data source
    st.subheader("🔍 Detailed Source Analysis")
    
    selected_source = st.selectbox("Select Data Source", list(processed_data.keys()))
    
    if selected_source:
        df = processed_data[selected_source]
        
        # Source overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{selected_source} Overview:**")
            st.write(f"• Records: {len(df):,}")
            st.write(f"• Columns: {len(df.columns)}")
            
            # Customer presence
            customer_cols = ['account_sales_territory_id', 'prj_customer_id', 'customer_id']
            customer_col = None
            for col in customer_cols:
                if col in df.columns:
                    customer_col = col
                    break
            
            if customer_col:
                unique_customers = df[customer_col].nunique()
                st.write(f"• Unique Customers: {unique_customers}")
        
        with col2:
            # Missing data analysis
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df)) * 100
            missing_cols = missing_pct[missing_pct > 0].sort_values(ascending=False)
            
            if len(missing_cols) > 0:
                st.markdown("**Top Missing Data Columns:**")
                for col, pct in missing_cols.head(5).items():
                    st.write(f"• {col}: {pct:.1f}%")
            else:
                st.success("✅ No missing data!")
        
        # Data sample
        st.markdown(f"**{selected_source} Sample Data:**")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Column details
        if st.expander(f"📝 {selected_source} Column Details"):
            col_info = []
            for col in df.columns:
                col_info.append({
                    'Column': col,
                    'Data Type': str(df[col].dtype),
                    'Non-Null Count': df[col].count(),
                    'Null Count': df[col].isnull().sum(),
                    'Unique Values': df[col].nunique()
                })
            
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)
    
    # Business insights from raw data
    st.subheader("💡 Key Raw Data Insights")
    
    insights_tabs = st.tabs(["Install Base", "Opportunities", "A&PS Projects", "Service Credits", "Services"])
    
    with insights_tabs[0]:  # Install Base
        if 'install_base' in processed_data:
            ib_df = processed_data['install_base']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Product Platform Distribution:**")
                if 'product_platform_description_name' in ib_df.columns:
                    platform_counts = ib_df['product_platform_description_name'].value_counts().head(10)
                    
                    fig = px.bar(
                        x=platform_counts.values,
                        y=platform_counts.index,
                        orientation='h',
                        title="Top 10 Product Platforms",
                        labels={'x': 'Product Count', 'y': 'Platform'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Support Status:**")
                if 'support_status' in ib_df.columns:
                    support_counts = ib_df['support_status'].value_counts()
                    
                    fig = px.pie(
                        values=support_counts.values,
                        names=support_counts.index,
                        title="Support Status Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with insights_tabs[1]:  # Opportunities
        if 'opportunities' in processed_data:
            opp_df = processed_data['opportunities']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Product Line Analysis:**")
                if 'product_line__c' in opp_df.columns:
                    product_line_counts = opp_df['product_line__c'].value_counts()
                    
                    fig = px.pie(
                        values=product_line_counts.values,
                        names=product_line_counts.index,
                        title="Opportunities by Product Line"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Top Opportunity Owners:**")
                if 'opportunity_owner__r_name' in opp_df.columns:
                    owner_counts = opp_df['opportunity_owner__r_name'].value_counts().head(8)
                    
                    fig = px.bar(
                        x=owner_counts.values,
                        y=owner_counts.index,
                        orientation='h',
                        title="Top 8 Opportunity Owners"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with insights_tabs[3]:  # Service Credits
        if 'service_credits' in processed_data:
            sc_df = processed_data['service_credits']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Service Credit Metrics:**")
                if 'purchasedcredits' in sc_df.columns:
                    total_purchased = sc_df['purchasedcredits'].sum()
                    st.metric("Total Purchased Credits", f"{total_purchased:,}")
                
                if 'activecredits' in sc_df.columns:
                    total_active = sc_df['activecredits'].sum()
                    st.metric("Total Active Credits", f"{total_active:,}")
                    
                    if 'purchasedcredits' in sc_df.columns:
                        utilization_rate = ((total_purchased - total_active) / total_purchased) * 100
                        st.metric("Utilization Rate", f"{utilization_rate:.1f}%")
            
            with col2:
                st.markdown("**Practice Distribution:**")
                if 'practicename' in sc_df.columns:
                    practice_counts = sc_df['practicename'].value_counts()
                    
                    fig = px.pie(
                        values=practice_counts.values,
                        names=practice_counts.index,
                        title="Service Credits by Practice"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with insights_tabs[2]:  # A&PS Projects
        if 'aps_projects' in processed_data:
            proj_df = processed_data['aps_projects']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Project Practice Distribution:**")
                if 'prj_practice' in proj_df.columns:
                    practice_counts = proj_df['prj_practice'].value_counts().head(10)
                    
                    fig = px.bar(
                        x=practice_counts.values,
                        y=practice_counts.index,
                        orientation='h',
                        title="Top 10 Practices by Project Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Geographic Distribution:**")
                if 'country_id' in proj_df.columns:
                    country_counts = proj_df['country_id'].value_counts().head(10)
                    
                    fig = px.bar(
                        x=country_counts.values,
                        y=country_counts.index,
                        orientation='h',
                        title="Top 10 Countries by Project Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with insights_tabs[4]:  # Services
        if 'services' in processed_data:
            serv_df = processed_data['services']
            
            st.markdown("**Services Data Quality:**")
            missing_pct = serv_df.isnull().sum() / len(serv_df) * 100
            
            fig = px.bar(
                x=missing_pct.values,
                y=missing_pct.index,
                orientation='h',
                title="Missing Data by Column (%)",
                labels={'x': 'Missing Percentage', 'y': 'Column'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data quality summary
    st.subheader("✅ Data Quality Summary")
    
    quality_data = []
    for name, df in processed_data.items():
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        # Count completely empty columns
        empty_cols = (df.isnull().sum() == len(df)).sum()
        
        # Data type distribution
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        text_cols = len(df.select_dtypes(include=['object']).columns)
        date_cols = len(df.select_dtypes(include=['datetime']).columns)
        
        quality_data.append({
            'Data Source': name,
            'Overall Missing %': f"{missing_pct:.1f}%",
            'Empty Columns': empty_cols,
            'Numeric Columns': numeric_cols,
            'Text Columns': text_cols,
            'Date Columns': date_cols,
            'Quality Score': "High" if missing_pct < 10 else "Medium" if missing_pct < 25 else "Low"
        })
    
    quality_df = pd.DataFrame(quality_data)
    st.dataframe(quality_df, use_container_width=True)
    
    # Export raw data insights
    st.subheader("📥 Export Options")
    
    if st.button("📊 Generate Raw Data Report"):
        # Create a comprehensive report
        report_content = "# HPE OneLead Raw Data Analysis Report\n\n"
        report_content += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report_content += "## Executive Summary\n\n"
        report_content += f"- **Total Records:** {total_records:,}\n"
        report_content += f"- **Data Sources:** {len(processed_data)}\n"
        report_content += f"- **Total Columns:** {total_columns}\n"
        report_content += f"- **Unique Customers:** {len(features)}\n\n"
        
        for name, df in processed_data.items():
            report_content += f"### {name}\n"
            report_content += f"- Records: {len(df):,}\n"
            report_content += f"- Columns: {len(df.columns)}\n"
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            report_content += f"- Missing Data: {missing_pct:.1f}%\n\n"
        
        st.download_button(
            "📄 Download Raw Data Report",
            data=report_content,
            file_name=f"hpe_onelead_raw_data_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()