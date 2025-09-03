"""
HPE OneLead Business Intelligence Dashboard
A business-focused dashboard with actionable insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from data_processing.data_loader_v2 import OneleadDataLoaderV2
from data_processing.feature_engineering_v2 import OneleadFeatureEngineerV2
from data_processing.service_opportunity_mapper import ServiceOpportunityMapper
from models.opportunity_predictor import OpportunityPredictor
from utils.customer_name_mapper import CustomerNameMapper

# Page configuration
st.set_page_config(
    page_title="HPE Customer Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for business-focused design
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Tab styling to make them look like real tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0f0f0;
        padding: 4px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding-left: 25px;
        padding-right: 25px;
        background-color: white;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #01A982;
        color: white;
        font-weight: 600;
    }
    
    /* Alert boxes */
    .critical-alert {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-alert {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .success-alert {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 0.8rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(90deg, #01A982 0%, #00805F 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the HPE OneLead data"""
    data_path = "data/DataExportAug29th.xlsx"
    loader = OneleadDataLoaderV2(data_path)
    processed_data = loader.process_all_data()
    feature_engineer = OneleadFeatureEngineerV2(processed_data)
    features = feature_engineer.build_feature_set()
    return processed_data, features, feature_engineer

@st.cache_resource
def train_model(features):
    """Train the opportunity prediction model"""
    predictor = OpportunityPredictor()
    training_results = predictor.train_model(features)
    return predictor, training_results

def calculate_business_metrics(processed_data):
    """Calculate real business metrics that matter"""
    metrics = {}
    
    # Install base analysis
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        
        # Products at risk
        expired_products = ib[ib['days_to_eol'] < 0] if 'days_to_eol' in ib.columns else pd.DataFrame()
        products_6mo = ib[(ib['days_to_eol'] >= 0) & (ib['days_to_eol'] < 180)] if 'days_to_eol' in ib.columns else pd.DataFrame()
        
        metrics['expired_products'] = len(expired_products)
        metrics['products_6mo_risk'] = len(products_6mo)
        metrics['customers_with_expired'] = expired_products['account_sales_territory_id'].nunique() if not expired_products.empty else 0
        
        # Support coverage
        if 'support_status' in ib.columns:
            support = ib['support_status'].value_counts()
            metrics['unsupported_products'] = support.get('Warranty Expired - Uncovered Box', 0) + \
                                             support.get('Expired Flex Support', 0) + \
                                             support.get('Expired Fixed Support', 0)
            metrics['supported_products'] = support.get('Active Warranty', 0)
    
    # Opportunity analysis
    if 'opportunities' in processed_data:
        opp = processed_data['opportunities']
        metrics['total_opportunities'] = len(opp)
        metrics['opportunity_customers'] = opp['account_st_id'].nunique()
        
        # Key account identification
        opp_by_customer = opp.groupby('account_st_id').size()
        metrics['key_account'] = opp_by_customer.idxmax() if not opp_by_customer.empty else None
        metrics['key_account_opps'] = opp_by_customer.max() if not opp_by_customer.empty else 0
    
    # Service credits
    if 'service_credits' in processed_data:
        sc = processed_data['service_credits']
        if 'purchased_credits' in sc.columns and 'delivered_credits' in sc.columns:
            metrics['unused_credits'] = sc['purchased_credits'].sum() - sc['delivered_credits'].sum()
            metrics['credit_utilization'] = (sc['delivered_credits'].sum() / sc['purchased_credits'].sum() * 100) if sc['purchased_credits'].sum() > 0 else 0
    
    return metrics

def main():
    # Load data
    try:
        processed_data, features, feature_engineer = load_and_process_data()
        predictor, training_results = train_model(features)
        metrics = calculate_business_metrics(processed_data)
        # Create customer name mapper
        name_mapper = CustomerNameMapper(processed_data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Header
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("# 🎯 HPE Customer Intelligence Center")
        st.markdown("**Focus on what matters: Revenue, Risk, and Relationships**")
    with col2:
        st.markdown(f"### {datetime.now().strftime('%B %d, %Y')}")
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main navigation - actual tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚨 ACTION REQUIRED",
        "💰 REVENUE FOCUS", 
        "👥 CUSTOMER HEALTH",
        "🎯 SERVICE RECOMMENDATIONS",
        "📊 BUSINESS METRICS",
        "🔍 DEEP DIVE"
    ])
    
    with tab1:
        show_action_required(processed_data, metrics, name_mapper)
    
    with tab2:
        show_revenue_focus(processed_data, metrics, name_mapper)
    
    with tab3:
        show_customer_health(processed_data, metrics, features, name_mapper)
    
    with tab4:
        show_service_recommendations(processed_data, metrics, name_mapper)
    
    with tab5:
        show_business_metrics(processed_data, metrics, name_mapper)
    
    with tab6:
        show_deep_dive(processed_data, features, name_mapper)

def show_action_required(processed_data, metrics, name_mapper):
    """Show what needs immediate action"""
    st.header("🚨 Immediate Actions Required")
    st.markdown("**These items need your attention TODAY**")
    
    # Critical alerts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.error(f"### ⚠️ {metrics.get('expired_products', 0)} Products EXPIRED")
        st.markdown(f"Affecting **{metrics.get('customers_with_expired', 0)} customers**")
        st.markdown("**Action:** Contact for immediate renewal")
    
    with col2:
        st.warning(f"### 💸 {metrics.get('unused_credits', 0):,.0f} Credits Unused")
        st.markdown(f"Only **{metrics.get('credit_utilization', 0):.0f}%** utilized")
        st.markdown("**Action:** Schedule utilization review")
    
    with col3:
        st.info(f"### 🎯 {metrics.get('unsupported_products', 0)} Products Unsupported")
        st.markdown("No active support coverage")
        st.markdown("**Action:** Propose support renewal")
    
    st.markdown("---")
    
    # Customer action list
    st.subheader("📋 Customer Action Priority List")
    
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        
        # Find customers with expired products
        if 'days_to_eol' in ib.columns:
            expired_by_customer = ib[ib['days_to_eol'] < 0].groupby('account_sales_territory_id').agg({
                'product_name': 'count',
                'days_to_eol': 'min'
            }).reset_index()
            
            expired_by_customer.columns = ['Customer ID', 'Expired Products', 'Days Expired']
            expired_by_customer['Days Expired'] = -expired_by_customer['Days Expired'].astype(int)
            expired_by_customer['Priority'] = '🔴 CRITICAL'
            expired_by_customer['Action'] = 'Schedule immediate renewal discussion'
            
            # Add opportunity count
            if 'opportunities' in processed_data:
                opp = processed_data['opportunities']
                opp_counts = opp.groupby('account_st_id').size().reset_index(name='Open Opportunities')
                expired_by_customer = expired_by_customer.merge(
                    opp_counts, 
                    left_on='Customer ID', 
                    right_on='account_st_id', 
                    how='left'
                )
                expired_by_customer.drop('account_st_id', axis=1, errors='ignore', inplace=True)
                expired_by_customer['Open Opportunities'] = expired_by_customer['Open Opportunities'].fillna(0).astype(int)
            
            # Sort by urgency
            expired_by_customer = expired_by_customer.sort_values('Days Expired', ascending=False)
            
            # Display
            st.dataframe(
                expired_by_customer[['Priority', 'Customer ID', 'Expired Products', 
                                    'Days Expired', 'Open Opportunities', 'Action']],
                use_container_width=True,
                hide_index=True,
                height=300
            )
            
            # Download action list
            csv = expired_by_customer.to_csv(index=False)
            st.download_button(
                "📥 Download Action List",
                csv,
                f"urgent_actions_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

def show_revenue_focus(processed_data, metrics, name_mapper):
    """Focus on revenue opportunities"""
    st.header("💰 Revenue & Opportunity Focus")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Opportunities",
            metrics.get('total_opportunities', 0),
            help="Active sales opportunities"
        )
    
    with col2:
        if metrics.get('key_account'):
            st.metric(
                "Key Account",
                f"Customer {metrics.get('key_account')}",
                delta=f"{metrics.get('key_account_opps')} opportunities"
            )
    
    with col3:
        active_customers = metrics.get('opportunity_customers', 0)
        st.metric(
            "Active Customers",
            f"{active_customers}/10",
            delta=f"{active_customers*10}% engagement"
        )
    
    with col4:
        # Estimate revenue at risk
        expired_revenue = metrics.get('expired_products', 0) * 15000  # Assume $15k per product
        st.metric(
            "Revenue at Risk",
            f"${expired_revenue/1000:.0f}K",
            delta="Renewal opportunity",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Opportunity analysis
    if 'opportunities' in processed_data:
        opp = processed_data['opportunities']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Customer Opportunity Concentration")
            
            # Top customers by opportunities
            top_customers = opp.groupby('account_st_id').size().sort_values(ascending=False).head(5)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=[name_mapper.get_name(x) for x in top_customers.index],
                    x=top_customers.values,
                    orientation='h',
                    marker_color=['#01A982' if i == 0 else '#4ECDC4' for i in range(len(top_customers))],
                    text=top_customers.values,
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Top 5 Customers by Opportunity Count",
                xaxis_title="Number of Opportunities",
                yaxis_title="",
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight
            top_3_pct = (top_customers.head(3).sum() / opp.shape[0] * 100)
            st.info(f"💡 **Insight:** Top 3 customers represent {top_3_pct:.0f}% of all opportunities. Focus here for maximum impact.")
        
        with col2:
            st.subheader("📈 Hot Product Lines")
            
            # Product line demand
            product_demand = opp['product_line'].value_counts().head(5)
            
            fig = px.pie(
                values=product_demand.values,
                names=product_demand.index,
                title="Opportunity Distribution by Product",
                hole=0.4,
                color_discrete_sequence=['#01A982', '#00805F', '#4ECDC4', '#FFA500', '#FF6B6B']
            )
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight
            st.success(f"💡 **Top Seller:** {product_demand.index[0]} with {product_demand.values[0]} opportunities")
    
    # Customer engagement analysis
    st.markdown("---")
    st.subheader("🔍 Customer Engagement Analysis")
    
    # Create engagement matrix
    if 'install_base' in processed_data and 'opportunities' in processed_data:
        ib = processed_data['install_base']
        opp = processed_data['opportunities']
        
        # Customer summary
        customers = ib.groupby('account_sales_territory_id').agg({
            'product_id': 'count'
        }).reset_index()
        customers.columns = ['customer_id', 'installed_products']
        
        # Add opportunity count
        opp_count = opp.groupby('account_st_id').size().reset_index(name='opportunities')
        customers = customers.merge(opp_count, left_on='customer_id', right_on='account_st_id', how='left')
        customers['opportunities'] = customers['opportunities'].fillna(0)
        
        # Add expired products
        if 'days_to_eol' in ib.columns:
            expired_count = ib[ib['days_to_eol'] < 0].groupby('account_sales_territory_id').size().reset_index(name='expired_products')
            customers = customers.merge(expired_count, left_on='customer_id', right_on='account_sales_territory_id', how='left')
            customers['expired_products'] = customers['expired_products'].fillna(0)
        
        # Calculate engagement score
        customers['engagement_score'] = (
            customers['opportunities'] * 2 +  # Weight opportunities higher
            customers['installed_products'] * 0.5 -
            customers.get('expired_products', 0) * 1.5  # Penalize expired products
        )
        
        # Classify customers
        customers['status'] = customers.apply(
            lambda x: '🌟 KEY ACCOUNT' if x['opportunities'] > 10 
            else '💰 HIGH VALUE' if x['opportunities'] > 5 
            else '⚠️ AT RISK' if x.get('expired_products', 0) > 0 
            else '📞 NEEDS ENGAGEMENT', 
            axis=1
        )
        
        # Display
        display_cols = ['status', 'customer_id', 'installed_products', 'opportunities', 'expired_products', 'engagement_score']
        available_cols = [col for col in display_cols if col in customers.columns]
        
        customers_display = customers.sort_values('engagement_score', ascending=False)[available_cols]
        customers_display.columns = ['Status', 'Customer', 'Products', 'Opportunities', 'Expired', 'Score']
        
        st.dataframe(
            customers_display,
            use_container_width=True,
            hide_index=True,
            height=300
        )

def show_customer_health(processed_data, metrics, features, name_mapper):
    """Show customer health dashboard"""
    st.header("👥 Customer Health Dashboard")
    
    # Health overview
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = 10
    
    with col1:
        healthy = total_customers - metrics.get('customers_with_expired', 0)
        st.metric("Healthy Customers", healthy, delta=f"{healthy/total_customers*100:.0f}%")
    
    with col2:
        at_risk = metrics.get('customers_with_expired', 0)
        st.metric("At Risk", at_risk, delta=f"{at_risk/total_customers*100:.0f}%", delta_color="inverse")
    
    with col3:
        engaged = metrics.get('opportunity_customers', 0)
        st.metric("Engaged", engaged, delta=f"{engaged/total_customers*100:.0f}%")
    
    with col4:
        inactive = total_customers - engaged
        st.metric("Inactive", inactive, delta="Need outreach", delta_color="inverse")
    
    st.markdown("---")
    
    # Customer selector for detailed view
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if 'customer_id' in features.columns:
            selected_customer = st.selectbox(
                "Select Customer for Detailed Analysis",
                features['customer_id'].unique(),
                format_func=lambda x: name_mapper.get_name(x)
            )
    
    with col2:
        refresh = st.button("🔄 Refresh Analysis", use_container_width=True)
    
    if selected_customer:
        # Customer details
        st.markdown("---")
        st.subheader(f"{name_mapper.get_name(selected_customer)} Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Product Status")
            
            if 'install_base' in processed_data:
                ib = processed_data['install_base']
                customer_products = ib[ib['account_sales_territory_id'] == selected_customer]
                
                if not customer_products.empty:
                    total_products = len(customer_products)
                    
                    if 'days_to_eol' in customer_products.columns:
                        expired = len(customer_products[customer_products['days_to_eol'] < 0])
                        at_risk = len(customer_products[(customer_products['days_to_eol'] >= 0) & 
                                                        (customer_products['days_to_eol'] < 365)])
                        healthy = total_products - expired - at_risk
                        
                        # Pie chart
                        fig = go.Figure(data=[go.Pie(
                            labels=['Expired', 'At Risk (<1yr)', 'Healthy'],
                            values=[expired, at_risk, healthy],
                            hole=0.3,
                            marker_colors=['#F44336', '#FFA500', '#4CAF50']
                        )])
                        
                        fig.update_layout(height=250, showlegend=True, margin=dict(t=0, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if expired > 0:
                            st.error(f"⚠️ {expired} products need immediate renewal")
        
        with col2:
            st.markdown("### 💼 Opportunities")
            
            if 'opportunities' in processed_data:
                opp = processed_data['opportunities']
                customer_opps = opp[opp['account_st_id'] == selected_customer]
                
                st.metric("Active Opportunities", len(customer_opps))
                
                if not customer_opps.empty:
                    # Top product lines
                    top_products = customer_opps['product_line'].value_counts().head(3)
                    st.markdown("**Top Product Interest:**")
                    for product, count in top_products.items():
                        st.markdown(f"• {product}: {count}")
                else:
                    st.warning("No active opportunities - schedule engagement")
        
        with col3:
            st.markdown("### 🎯 Recommendations")
            
            recommendations = []
            
            # Check for expired products
            if 'install_base' in processed_data:
                ib = processed_data['install_base']
                customer_products = ib[ib['account_sales_territory_id'] == selected_customer]
                
                if 'days_to_eol' in customer_products.columns:
                    expired_count = len(customer_products[customer_products['days_to_eol'] < 0])
                    if expired_count > 0:
                        recommendations.append(f"🔴 Renew {expired_count} expired products immediately")
            
            # Check opportunities
            if 'opportunities' in processed_data:
                opp = processed_data['opportunities']
                customer_opps = opp[opp['account_st_id'] == selected_customer]
                
                if len(customer_opps) > 10:
                    recommendations.append("🟢 Key account - assign dedicated resource")
                elif len(customer_opps) > 0:
                    recommendations.append("🟡 Active engagement - maintain momentum")
                else:
                    recommendations.append("🔴 No opportunities - schedule business review")
            
            # Check support
            if 'support_status' in customer_products.columns:
                unsupported = customer_products['support_status'].str.contains('Expired').sum()
                if unsupported > 0:
                    recommendations.append(f"🟡 Upgrade {unsupported} products to active support")
            
            for rec in recommendations:
                st.markdown(rec)

def show_business_metrics(processed_data, metrics, name_mapper):
    """Show key business metrics and trends"""
    st.header("📊 Business Performance Metrics")
    
    # KPI Dashboard
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        coverage = (10 - metrics.get('customers_with_expired', 0)) / 10 * 100
        st.metric(
            "Support Coverage",
            f"{coverage:.0f}%",
            delta="of customers fully supported",
            help="Percentage of customers with all products under support"
        )
    
    with col2:
        utilization = metrics.get('credit_utilization', 0)
        st.metric(
            "Credit Utilization",
            f"{utilization:.0f}%",
            delta=f"{100-utilization:.0f}% opportunity",
            delta_color="inverse" if utilization < 50 else "normal"
        )
    
    with col3:
        engagement = metrics.get('opportunity_customers', 0) / 10 * 100
        st.metric(
            "Customer Engagement",
            f"{engagement:.0f}%",
            delta="have active opportunities"
        )
    
    with col4:
        # Calculate opportunity velocity
        if 'opportunities' in processed_data:
            opp = processed_data['opportunities']
            avg_opps = len(opp) / metrics.get('opportunity_customers', 1)
            st.metric(
                "Opportunity Velocity",
                f"{avg_opps:.1f}",
                delta="avg per customer"
            )
    
    st.markdown("---")
    
    # Visual metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Support Coverage Analysis")
        
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            if 'support_status' in ib.columns:
                support_dist = ib['support_status'].value_counts()
                
                # Group into supported vs unsupported
                supported = support_dist.get('Active Warranty', 0)
                unsupported = sum([v for k, v in support_dist.items() if 'Expired' in k])
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Supported', 'Unsupported'],
                        y=[supported, unsupported],
                        marker_color=['#4CAF50', '#F44336'],
                        text=[supported, unsupported],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title="Product Support Status",
                    yaxis_title="Number of Products",
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if unsupported > 0:
                    potential_revenue = unsupported * 5000  # Assume $5k per support contract
                    st.success(f"💰 **Revenue Opportunity:** ${potential_revenue/1000:.0f}K from support renewals")
    
    with col2:
        st.subheader("💳 Service Credit Performance")
        
        if 'service_credits' in processed_data:
            sc = processed_data['service_credits']
            
            # Credit utilization by practice
            if 'practice_name' in sc.columns:
                practice_util = sc.groupby('practice_name').agg({
                    'purchased_credits': 'sum',
                    'delivered_credits': 'sum'
                }).head(5)
                
                practice_util['utilization'] = (practice_util['delivered_credits'] / 
                                               practice_util['purchased_credits'] * 100)
                practice_util = practice_util.sort_values('utilization', ascending=True)
                
                fig = go.Figure(data=[
                    go.Bar(
                        y=practice_util.index,
                        x=practice_util['utilization'],
                        orientation='h',
                        marker_color=px.colors.sequential.Viridis,
                        text=[f"{x:.0f}%" for x in practice_util['utilization']],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title="Credit Utilization by Practice",
                    xaxis_title="Utilization %",
                    yaxis_title="",
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                lowest_util = practice_util['utilization'].min()
                if lowest_util < 50:
                    st.warning(f"⚠️ **Action Required:** {practice_util.index[0]} at only {lowest_util:.0f}% utilization")
    
    # Business insights
    st.markdown("---")
    st.subheader("💡 Business Insights & Recommendations")
    
    insights = []
    
    # Generate insights based on metrics
    if metrics.get('expired_products', 0) > 20:
        insights.append({
            "type": "critical",
            "title": "Product Renewal Crisis",
            "message": f"{metrics.get('expired_products')} products expired. Estimated revenue opportunity: ${metrics.get('expired_products', 0) * 15000 / 1000:.0f}K",
            "action": "Launch immediate renewal campaign"
        })
    
    if metrics.get('credit_utilization', 0) < 50:
        unused = metrics.get('unused_credits', 0)
        insights.append({
            "type": "warning",
            "title": "Service Credit Underutilization",
            "message": f"{unused:,.0f} credits unused ({100-metrics.get('credit_utilization', 0):.0f}% of total)",
            "action": "Schedule utilization review with customers"
        })
    
    if metrics.get('key_account_opps', 0) > 40:
        insights.append({
            "type": "success",
            "title": "Key Account Opportunity",
            "message": f"Customer {metrics.get('key_account')} has {metrics.get('key_account_opps')} opportunities",
            "action": "Assign senior sales resource for strategic engagement"
        })
    
    # Display insights
    for insight in insights:
        if insight['type'] == 'critical':
            st.error(f"### 🔴 {insight['title']}\n{insight['message']}\n\n**Action:** {insight['action']}")
        elif insight['type'] == 'warning':
            st.warning(f"### 🟡 {insight['title']}\n{insight['message']}\n\n**Action:** {insight['action']}")
        else:
            st.success(f"### 🟢 {insight['title']}\n{insight['message']}\n\n**Action:** {insight['action']}")

def show_service_recommendations(processed_data, metrics, name_mapper):
    """Show opportunity-service mapping and recommendations"""
    st.header("🎯 Service Recommendations")
    st.markdown("**Map opportunities to relevant HPE services for better customer engagement**")
    
    # Initialize service mapper
    service_mapper = ServiceOpportunityMapper()
    
    if 'opportunities' in processed_data and len(processed_data['opportunities']) > 0:
        opportunities = processed_data['opportunities']
        install_base = processed_data.get('install_base')
        
        # Map opportunities to services
        service_mapping = service_mapper.map_opportunity_to_services(opportunities)
        
        # Get customer recommendations
        customer_recommendations = service_mapper.get_customer_service_recommendations(
            opportunities, install_base
        )
        
        # Service coverage metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Opportunities", len(opportunities))
        
        with col2:
            unique_services = service_mapping['service_type'].nunique()
            st.metric("Service Types", unique_services)
        
        with col3:
            high_priority = len(service_mapping[service_mapping['service_priority'] >= 0.8])
            st.metric("High Priority", high_priority)
        
        with col4:
            avg_priority = service_mapping['service_priority'].mean()
            st.metric("Avg Priority Score", f"{avg_priority:.2f}")
        
        st.markdown("---")
        
        # Customer Service Recommendations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Customer Service Recommendations")
            
            if not customer_recommendations.empty:
                display_df = customer_recommendations[[
                    'customer_id', 'customer_name', 'opportunity_count',
                    'primary_recommendation', 'avg_priority'
                ]].copy()
                
                display_df['customer_id'] = name_mapper.map_series(display_df['customer_id'])
                display_df['avg_priority'] = (display_df['avg_priority'] * 100).round(0).astype(int)
                display_df.columns = ['Customer ID', 'Customer Name', 'Opportunities', 
                                     'Primary Recommendation', 'Priority %']
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
        
        with col2:
            st.subheader("📊 Service Distribution")
            
            # Service type distribution
            service_dist = service_mapping['service_type'].value_counts()
            
            fig = px.pie(
                values=service_dist.values,
                names=service_dist.index,
                title="Service Types by Opportunities",
                hole=0.4
            )
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed Opportunity-Service Mapping
        st.subheader("🔗 Detailed Opportunity-Service Mapping")
        
        # Use standardized lowercase column names
        account_col = 'account_name'
        opp_id_col = 'opportunity_id'
        
        customer_filter = st.selectbox(
            "Filter by Customer",
            ['All'] + sorted(opportunities[account_col].dropna().unique().tolist()) if account_col in opportunities.columns else ['All'],
            key='service_customer_filter'
        )
        
        filtered_mapping = service_mapping.copy()
        if customer_filter != 'All' and account_col in opportunities.columns:
            customer_opps = opportunities[opportunities[account_col] == customer_filter][opp_id_col].tolist()
            filtered_mapping = filtered_mapping[filtered_mapping['opportunity_id'].isin(customer_opps)]
        
        if not filtered_mapping.empty:
            # Prepare display
            display_mapping = filtered_mapping[[
                'opportunity_id', 'account_name', 'product_line', 
                'service_type', 'recommended_services', 'service_priority'
            ]].copy()
            
            display_mapping['service_priority'] = (display_mapping['service_priority'] * 100).round(0).astype(int)
            display_mapping.columns = ['Opportunity ID', 'Account', 'Product Line', 
                                      'Service Type', 'Recommended Services', 'Priority %']
            
            # Color code by priority
            def highlight_priority(val):
                if val >= 80:
                    return 'background-color: #ff4b4b; color: white'
                elif val >= 60:
                    return 'background-color: #ffa500; color: white'
                else:
                    return 'background-color: #4ecdc4'
            
            styled_df = display_mapping.style.applymap(
                highlight_priority, 
                subset=['Priority %']
            )
            
            st.dataframe(
                display_mapping,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Export option
            csv = display_mapping.to_csv(index=False)
            st.download_button(
                "📥 Export Service Recommendations",
                csv,
                f"service_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
        
        # Service Coverage Analysis
        st.markdown("---")
        st.subheader("📈 Service Coverage Analysis")
        
        coverage = service_mapper.calculate_service_coverage(
            opportunities, 
            processed_data.get('service_credits')
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Coverage Metrics")
            metrics_df = pd.DataFrame([
                {'Metric': 'Total Opportunities', 'Value': coverage['total_opportunities']},
                {'Metric': 'Mapped Opportunities', 'Value': coverage['mapped_opportunities']},
                {'Metric': 'Unique Service Types', 'Value': coverage['unique_service_types']},
                {'Metric': 'High Priority Count', 'Value': coverage['high_priority_opportunities']},
                {'Metric': 'Avg Service Priority', 'Value': f"{coverage['avg_service_priority']:.2%}"}
            ])
            
            if 'service_credit_utilization' in coverage:
                metrics_df = pd.concat([metrics_df, pd.DataFrame([
                    {'Metric': 'Credit Utilization', 'Value': f"{coverage['service_credit_utilization']:.1f}%"},
                    {'Metric': 'Unused Credits', 'Value': f"{coverage['unused_credits']:,.0f}"}
                ])])
            
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Practice Distribution")
            practice_dist = pd.DataFrame(
                list(coverage['practice_distribution'].items()),
                columns=['Practice', 'Count']
            ).sort_values('Count', ascending=False)
            
            fig = px.bar(
                practice_dist,
                x='Count',
                y='Practice',
                orientation='h',
                title="Opportunities by Practice Area",
                color='Count',
                color_continuous_scale='tealgrn'
            )
            
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No opportunity data available for service mapping")

def show_deep_dive(processed_data, features, name_mapper):
    """Deep dive analysis tool"""
    st.header("🔍 Deep Dive Analysis")
    
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Product Lifecycle Analysis", "Opportunity Pipeline", "Service Utilization", "Customer Segmentation", "Raw Data Explorer"]
    )
    
    st.markdown("---")
    
    if analysis_type == "Product Lifecycle Analysis":
        st.subheader("📅 Product Lifecycle Management")
        
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                customer_filter = st.selectbox(
                    "Filter by Customer",
                    ["All"] + list(ib['account_sales_territory_id'].unique()),
                    format_func=lambda x: "All Customers" if x == "All" else name_mapper.get_name(x)
                )
            
            with col2:
                platform_filter = st.selectbox(
                    "Filter by Platform",
                    ["All"] + list(ib['product_platform_description_name'].dropna().unique())
                )
            
            # Apply filters
            filtered_ib = ib.copy()
            if customer_filter != "All":
                filtered_ib = filtered_ib[filtered_ib['account_sales_territory_id'] == customer_filter]
            if platform_filter != "All":
                filtered_ib = filtered_ib[filtered_ib['product_platform_description_name'] == platform_filter]
            
            # Display critical products
            if 'days_to_eol' in filtered_ib.columns:
                critical_products = filtered_ib[filtered_ib['days_to_eol'] < 365].sort_values('days_to_eol')
                
                if not critical_products.empty:
                    st.error(f"### ⚠️ {len(critical_products)} Products Need Attention")
                    
                    display_cols = ['account_sales_territory_id', 'product_name', 
                                   'product_platform_description_name', 'days_to_eol', 'support_status']
                    available_cols = [col for col in display_cols if col in critical_products.columns]
                    
                    display_df = critical_products[available_cols].copy()
                    display_df.columns = ['Customer', 'Product', 'Platform', 'Days to EOL', 'Support']
                    display_df['Days to EOL'] = display_df['Days to EOL'].astype(int)
                    
                    # Add priority
                    display_df['Priority'] = display_df['Days to EOL'].apply(
                        lambda x: '🔴 EXPIRED' if x < 0 else '🟡 CRITICAL' if x < 180 else '🟢 MONITOR'
                    )
                    
                    st.dataframe(
                        display_df[['Priority'] + list(display_df.columns[:-1])],
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                else:
                    st.success("✅ No products at immediate risk")
    
    elif analysis_type == "Opportunity Pipeline":
        st.subheader("💼 Opportunity Pipeline Analysis")
        
        if 'opportunities' in processed_data:
            opp = processed_data['opportunities']
            
            # Pipeline funnel
            total_opps = len(opp)
            unique_customers = opp['account_st_id'].nunique()
            unique_products = opp['product_line'].nunique()
            
            # Create funnel
            funnel_data = pd.DataFrame({
                'Stage': ['Total Opportunities', 'Unique Customers', 'Product Lines'],
                'Count': [total_opps, unique_customers, unique_products]
            })
            
            fig = go.Figure(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                textposition="inside",
                textinfo="value+percent initial",
                marker_color=['#01A982', '#00805F', '#4ECDC4']
            ))
            
            fig.update_layout(height=300, title="Opportunity Funnel")
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed pipeline
            st.markdown("### Pipeline Details")
            
            opp_summary = opp.groupby(['account_st_id', 'product_line']).size().reset_index(name='count')
            opp_summary['account_st_id'] = name_mapper.map_series(opp_summary['account_st_id'])
            opp_summary = opp_summary.sort_values('count', ascending=False)
            
            st.dataframe(
                opp_summary.rename(columns={
                    'account_st_id': 'Customer',
                    'product_line': 'Product Line',
                    'count': 'Opportunities'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    elif analysis_type == "Service Utilization":
        st.subheader("💳 Service Utilization Analysis")
        
        if 'service_credits' in processed_data:
            sc = processed_data['service_credits']
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_purchased = sc['purchased_credits'].sum() if 'purchased_credits' in sc.columns else 0
            total_delivered = sc['delivered_credits'].sum() if 'delivered_credits' in sc.columns else 0
            total_active = sc['active_credits'].sum() if 'active_credits' in sc.columns else 0
            utilization = (total_delivered / total_purchased * 100) if total_purchased > 0 else 0
            
            with col1:
                st.metric("Purchased Credits", f"{total_purchased:,.0f}")
            
            with col2:
                st.metric("Delivered Credits", f"{total_delivered:,.0f}")
            
            with col3:
                st.metric("Active Credits", f"{total_active:,.0f}")
            
            with col4:
                st.metric("Utilization Rate", f"{utilization:.1f}%")
            
            st.markdown("---")
            
            # Utilization by practice
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Credits by Practice")
                
                if 'practice_name' in sc.columns:
                    practice_summary = sc.groupby('practice_name').agg({
                        'purchased_credits': 'sum',
                        'delivered_credits': 'sum',
                        'active_credits': 'sum'
                    }).sort_values('purchased_credits', ascending=False)
                    
                    practice_summary['utilization_%'] = (practice_summary['delivered_credits'] / 
                                                         practice_summary['purchased_credits'] * 100).round(1)
                    
                    st.dataframe(
                        practice_summary,
                        use_container_width=True,
                        height=300
                    )
            
            with col2:
                st.markdown("### Contract Urgency")
                
                if 'contract_urgency' in sc.columns:
                    urgency_dist = sc['contract_urgency'].value_counts()
                    
                    fig = px.pie(
                        values=urgency_dist.values,
                        names=urgency_dist.index,
                        title="Contracts by Renewal Urgency",
                        hole=0.4,
                        color_discrete_map={
                            'Critical': '#FF6B6B',
                            'High': '#FFA500',
                            'Medium': '#FFD700',
                            'Low': '#4ECDC4'
                        }
                    )
                    
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Underutilized credits
            st.markdown("---")
            st.markdown("### ⚠️ Underutilized Service Credits")
            
            if 'credit_utilization' in sc.columns:
                underutilized = sc[sc['credit_utilization'] < 0.3].copy()
                
                if not underutilized.empty:
                    underutilized['unused_credits'] = underutilized['purchased_credits'] - underutilized['delivered_credits']
                    underutilized = underutilized.sort_values('unused_credits', ascending=False)
                    
                    display_cols = ['project_name', 'practice_name', 'purchased_credits', 
                                   'delivered_credits', 'unused_credits', 'credit_utilization']
                    available_cols = [col for col in display_cols if col in underutilized.columns]
                    
                    if available_cols:
                        display_df = underutilized[available_cols].head(20)
                        display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True,
                            height=300
                        )
                        
                        total_waste = underutilized['unused_credits'].sum() if 'unused_credits' in underutilized.columns else 0
                        st.error(f"💸 **Total Credits at Risk:** {total_waste:,.0f} credits across {len(underutilized)} projects")
                else:
                    st.success("✅ All service credits are being utilized effectively")
        else:
            st.info("No service credit data available")
    
    elif analysis_type == "Customer Segmentation":
        st.subheader("👥 Customer Segmentation Analysis")
        
        # Build customer segments
        if 'install_base' in processed_data and 'opportunities' in processed_data:
            ib = processed_data['install_base']
            opp = processed_data['opportunities']
            
            # Customer metrics
            customer_metrics = ib.groupby('account_sales_territory_id').agg({
                'product_id': 'count',
                'days_to_eol': lambda x: (x < 0).sum() if 'days_to_eol' in x.name else 0
            }).reset_index()
            customer_metrics.columns = ['customer_id', 'total_products', 'expired_products']
            
            # Add opportunity counts
            opp_counts = opp.groupby('account_st_id').size().reset_index(name='opportunities')
            customer_metrics = customer_metrics.merge(
                opp_counts,
                left_on='customer_id',
                right_on='account_st_id',
                how='left'
            )
            customer_metrics['opportunities'] = customer_metrics['opportunities'].fillna(0)
            
            # Segment customers
            def segment_customer(row):
                if row['opportunities'] > 10:
                    return '🌟 Strategic'
                elif row['opportunities'] > 5 and row['expired_products'] == 0:
                    return '💎 High Value'
                elif row['expired_products'] > 0:
                    return '⚠️ At Risk'
                elif row['opportunities'] == 0:
                    return '😴 Dormant'
                else:
                    return '📈 Growing'
            
            customer_metrics['segment'] = customer_metrics.apply(segment_customer, axis=1)
            
            # Display segments
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Customer Segments")
                
                segment_summary = customer_metrics.groupby('segment').agg({
                    'customer_id': 'count',
                    'total_products': 'sum',
                    'opportunities': 'sum',
                    'expired_products': 'sum'
                }).rename(columns={'customer_id': 'customers'})
                
                st.dataframe(
                    segment_summary,
                    use_container_width=True
                )
                
                # Segment distribution
                fig = px.pie(
                    values=segment_summary['customers'],
                    names=segment_summary.index,
                    title="Customer Distribution by Segment",
                    hole=0.4
                )
                
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Segment Details")
                
                # Customer list by segment
                selected_segment = st.selectbox(
                    "Select Segment",
                    customer_metrics['segment'].unique()
                )
                
                segment_customers = customer_metrics[customer_metrics['segment'] == selected_segment]
                
                if not segment_customers.empty:
                    display_cols = ['customer_id', 'total_products', 'expired_products', 'opportunities']
                    display_df = segment_customers[display_cols].copy()
                    display_df['customer_id'] = name_mapper.map_series(display_df['customer_id'])
                    display_df.columns = ['Customer', 'Products', 'Expired', 'Opportunities']
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Segment-specific recommendations
                    st.markdown("### 💡 Segment Strategy")
                    
                    if '🌟 Strategic' in selected_segment:
                        st.success("**Action:** Assign dedicated account manager, quarterly business reviews")
                    elif '💎 High Value' in selected_segment:
                        st.info("**Action:** Maintain engagement, explore upsell opportunities")
                    elif '⚠️ At Risk' in selected_segment:
                        st.error("**Action:** Immediate renewal campaign, risk mitigation plan")
                    elif '😴 Dormant' in selected_segment:
                        st.warning("**Action:** Re-engagement campaign, identify decision makers")
                    else:
                        st.info("**Action:** Nurture relationships, identify growth opportunities")
        else:
            st.error("Insufficient data for customer segmentation")
    
    elif analysis_type == "Raw Data Explorer":
        st.subheader("📊 Raw Data Explorer")
        
        # Select data source
        data_source = st.selectbox(
            "Select Data Source",
            list(processed_data.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if data_source:
            df = processed_data[data_source]
            
            # Basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Records", f"{len(df):,}")
            
            with col2:
                st.metric("Columns", len(df.columns))
            
            with col3:
                missing = df.isnull().sum().sum()
                st.metric("Missing Values", f"{missing:,}")
            
            # Search and filter
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                search = st.text_input("Search in data", placeholder="Type to filter...")
            
            with col2:
                columns_to_show = st.multiselect(
                    "Select Columns",
                    df.columns.tolist(),
                    default=df.columns.tolist()[:10] if len(df.columns) > 10 else df.columns.tolist()
                )
            
            # Apply search
            display_df = df[columns_to_show] if columns_to_show else df
            
            if search:
                mask = pd.Series(False, index=display_df.index)
                for col in display_df.select_dtypes(include=['object']).columns:
                    mask |= display_df[col].astype(str).str.contains(search, case=False, na=False)
                display_df = display_df[mask]
            
            # Display data
            st.dataframe(
                display_df.head(100),
                use_container_width=True,
                height=400
            )
            
            # Export
            csv = display_df.to_csv(index=False)
            st.download_button(
                "📥 Export to CSV",
                csv,
                f"{data_source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()