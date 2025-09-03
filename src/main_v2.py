"""
HPE OneLead Intelligence Dashboard V2
A focused, data-driven approach to customer intelligence
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

# Custom CSS for cleaner design
st.markdown("""
<style>
    /* Main content styling */
    .main {
        padding: 1rem;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Headers */
    h1 {
        color: #01A982;
        border-bottom: 3px solid #01A982;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #333333;
        margin-top: 2rem;
    }
    
    /* Data tables */
    .dataframe {
        font-size: 14px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    
    /* Success box */
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Warning box */
    .warning-box {
        background-color: #FFF3CD;
        border: 1px solid #FFEEBA;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Critical box */
    .critical-box {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the HPE OneLead data"""
    data_path = "data/DataExportAug29th.xlsx"
    
    # Load data
    loader = OneleadDataLoaderV2(data_path)
    processed_data = loader.process_all_data()
    
    # Engineer features
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
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎯 HPE OneLead Intelligence")
        st.markdown("**Unified Customer Intelligence & Opportunity Management**")
    with col2:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Load data
    try:
        with st.spinner("Loading HPE OneLead data..."):
            processed_data, features, feature_engineer = load_and_process_data()
            predictor, training_results = train_model(features)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure the data file 'DataExportAug29th.xlsx' is in the data/ directory")
        return
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    
    # Main navigation with clearer structure
    page = st.sidebar.radio(
        "Select View",
        [
            "🏠 Executive Overview",
            "👥 Customer Intelligence", 
            "💼 Opportunity Analysis",
            "🔧 Service & Support",
            "📈 Predictive Insights",
            "📋 Data Explorer"
        ]
    )
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    
    # Calculate key metrics
    total_customers = len(features[features['id_type'] == '5-digit']) if 'id_type' in features.columns else len(features)
    total_opportunities = processed_data['opportunities']['opportunity_id'].nunique() if 'opportunities' in processed_data else 0
    total_products = processed_data['install_base']['serial_number_id'].nunique() if 'install_base' in processed_data else 0
    
    st.sidebar.metric("Total Customers", f"{total_customers:,}")
    st.sidebar.metric("Active Opportunities", f"{total_opportunities:,}")
    st.sidebar.metric("Installed Products", f"{total_products:,}")
    
    # Route to different pages
    if "Executive Overview" in page:
        show_executive_overview(processed_data, features, predictor)
    elif "Customer Intelligence" in page:
        show_customer_intelligence(processed_data, features, predictor)
    elif "Opportunity Analysis" in page:
        show_opportunity_analysis(processed_data, features, predictor)
    elif "Service & Support" in page:
        show_service_support(processed_data, features)
    elif "Predictive Insights" in page:
        show_predictive_insights(features, predictor, training_results)
    elif "Data Explorer" in page:
        show_data_explorer(processed_data, features)

def show_executive_overview(processed_data, features, predictor):
    """Clean executive overview focused on actionable insights"""
    
    st.header("🏠 Executive Overview")
    st.markdown("Real-time snapshot of customer engagement and opportunities")
    
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    high_priority = len(features[features['propensity_tier'] == 'High']) if 'propensity_tier' in features.columns else 0
    
    # EOL/EOS urgency
    urgent_eol = 0
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        if 'eol_urgency_score' in ib.columns:
            urgent_eol = len(ib[ib['eol_urgency_score'] >= 3])
    
    # Service utilization
    avg_utilization = 0
    if 'service_credits' in processed_data:
        sc = processed_data['service_credits']
        if 'credit_utilization' in sc.columns:
            avg_utilization = sc['credit_utilization'].mean()
    
    with col1:
        st.metric(
            "🔥 High Priority Accounts",
            high_priority,
            help="Accounts with high opportunity propensity"
        )
    
    with col2:
        st.metric(
            "⚠️ EOL/EOS Alerts", 
            urgent_eol,
            help="Products approaching end-of-life"
        )
    
    with col3:
        st.metric(
            "📊 Avg Service Utilization",
            f"{avg_utilization:.0%}",
            help="Average credit utilization across projects"
        )
    
    with col4:
        total_opportunities = len(processed_data['opportunities']) if 'opportunities' in processed_data else 0
        st.metric(
            "💼 Open Opportunities",
            total_opportunities,
            help="Total active opportunities"
        )
    
    # Two main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Customer Prioritization")
        
        if 'propensity_tier' in features.columns:
            # Propensity distribution
            tier_counts = features['propensity_tier'].value_counts()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=tier_counts.index,
                    y=tier_counts.values,
                    marker_color=['#FF6B6B', '#FFA500', '#4ECDC4'],
                    text=tier_counts.values,
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Customer Priority Distribution",
                xaxis_title="Priority Level",
                yaxis_title="Number of Customers",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Opportunity Pipeline")
        
        if 'opportunities' in processed_data:
            opp_df = processed_data['opportunities']
            
            # Group by product line
            if 'product_line' in opp_df.columns:
                product_lines = opp_df['product_line'].value_counts().head(5)
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=product_lines.index,
                        values=product_lines.values,
                        hole=0.4
                    )
                ])
                
                fig.update_layout(
                    title="Opportunities by Product Line",
                    height=300,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Action Items Section
    st.subheader("🎯 Recommended Actions")
    
    actions = []
    
    # Check for urgent EOL/EOS
    if urgent_eol > 0:
        actions.append({
            "priority": "🔴 Critical",
            "action": f"Address {urgent_eol} products approaching EOL/EOS",
            "impact": "Prevent service disruptions"
        })
    
    # Check for low utilization
    if avg_utilization < 0.5:
        actions.append({
            "priority": "🟡 Medium",
            "action": "Review underutilized service credits",
            "impact": "Maximize value from existing contracts"
        })
    
    # High priority accounts
    if high_priority > 0:
        actions.append({
            "priority": "🟢 High",
            "action": f"Engage {high_priority} high-propensity customers",
            "impact": "Accelerate opportunity conversion"
        })
    
    if actions:
        action_df = pd.DataFrame(actions)
        st.dataframe(
            action_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No urgent actions required at this time")

def show_customer_intelligence(processed_data, features, predictor):
    """Unified customer 360 view"""
    
    st.header("👥 Customer Intelligence")
    st.markdown("Comprehensive view of customer engagement and health")
    
    # Customer selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get customer list
        if 'customer_id' in features.columns:
            customer_ids = features['customer_id'].unique()
            selected_customer = st.selectbox(
                "Select Customer",
                customer_ids,
                format_func=lambda x: f"Customer {int(x)}"
            )
        else:
            st.error("No customer data available")
            return
    
    with col2:
        view_mode = st.radio(
            "View Mode",
            ["Summary", "Detailed"]
        )
    
    if selected_customer:
        # Get customer data
        customer_data = features[features['customer_id'] == selected_customer].iloc[0]
        
        # Customer header
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            propensity = customer_data.get('propensity_tier', 'Unknown')
            color = "🔴" if propensity == "High" else "🟡" if propensity == "Medium" else "🟢"
            st.metric("Priority Level", f"{color} {propensity}")
        
        with col2:
            score = customer_data.get('opportunity_propensity_score', 0)
            st.metric("Opportunity Score", f"{score:.2f}")
        
        with col3:
            products = customer_data.get('total_products', 0)
            st.metric("Installed Products", int(products))
        
        with col4:
            opportunities = customer_data.get('total_opportunities', 0)
            st.metric("Active Opportunities", int(opportunities))
        
        if view_mode == "Summary":
            # Summary view with key insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Customer Profile")
                
                # Key metrics
                profile_data = {
                    "Metric": [
                        "Platform Diversity",
                        "Service Engagement",
                        "Renewal Risk",
                        "Utilization Health"
                    ],
                    "Value": [
                        f"{int(customer_data.get('platform_diversity', 0))} platforms",
                        "Active" if customer_data.get('has_active_opportunities', False) else "Inactive",
                        "High" if customer_data.get('has_eol_risk', False) else "Low",
                        "Good" if customer_data.get('org_avg_credit_utilization', 0) > 0.5 else "Low"
                    ],
                    "Status": [
                        "✅" if customer_data.get('platform_diversity', 0) > 1 else "⚠️",
                        "✅" if customer_data.get('has_active_opportunities', False) else "⚠️",
                        "⚠️" if customer_data.get('has_eol_risk', False) else "✅",
                        "✅" if customer_data.get('org_avg_credit_utilization', 0) > 0.5 else "⚠️"
                    ]
                }
                
                profile_df = pd.DataFrame(profile_data)
                st.dataframe(profile_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.subheader("💡 Recommendations")
                
                recommendations = []
                
                # Generate recommendations based on customer data
                if customer_data.get('has_eol_risk', False):
                    recommendations.append("🔴 **Urgent**: Products approaching EOL - Schedule upgrade discussion")
                
                if customer_data.get('platform_diversity', 0) <= 1:
                    recommendations.append("🟡 **Cross-sell**: Limited platform adoption - Explore expansion opportunities")
                
                if not customer_data.get('has_active_opportunities', False):
                    recommendations.append("🟢 **Engage**: No active opportunities - Initiate value assessment")
                
                if customer_data.get('org_avg_credit_utilization', 0) < 0.5:
                    recommendations.append("🟡 **Optimize**: Low credit utilization - Review service usage")
                
                if recommendations:
                    for rec in recommendations:
                        st.markdown(rec)
                else:
                    st.success("Customer is well-engaged with no immediate actions required")
        
        else:  # Detailed view
            # Detailed metrics in tabs
            tab1, tab2, tab3 = st.tabs(["Products", "Opportunities", "Services"])
            
            with tab1:
                st.subheader("Installed Base Details")
                
                if 'install_base' in processed_data:
                    ib = processed_data['install_base']
                    customer_products = ib[ib['account_sales_territory_id'] == selected_customer]
                    
                    if not customer_products.empty:
                        display_cols = ['product_name', 'product_platform_description_name', 
                                      'support_status', 'days_to_eol']
                        available_cols = [col for col in display_cols if col in customer_products.columns]
                        
                        st.dataframe(
                            customer_products[available_cols],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No product data available for this customer")
            
            with tab2:
                st.subheader("Opportunity Details")
                
                if 'opportunities' in processed_data:
                    opp = processed_data['opportunities']
                    customer_opps = opp[opp['account_st_id'] == selected_customer]
                    
                    if not customer_opps.empty:
                        display_cols = ['opportunity_name', 'product_line']
                        available_cols = [col for col in display_cols if col in customer_opps.columns]
                        
                        st.dataframe(
                            customer_opps[available_cols],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No opportunity data available for this customer")
            
            with tab3:
                st.subheader("Service Metrics")
                
                # Show aggregated service metrics
                service_metrics = {
                    "Service Metric": [
                        "Total Service Projects",
                        "Average Credit Utilization",
                        "Active Credits",
                        "Contract Status"
                    ],
                    "Value": [
                        f"{customer_data.get('org_total_service_credit_projects', 0):.0f}",
                        f"{customer_data.get('org_avg_credit_utilization', 0):.0%}",
                        f"{customer_data.get('org_total_active_credits', 0):.0f}",
                        "Active" if customer_data.get('org_critical_contracts', 0) == 0 else "Review Needed"
                    ]
                }
                
                st.dataframe(
                    pd.DataFrame(service_metrics),
                    hide_index=True,
                    use_container_width=True
                )

def show_opportunity_analysis(processed_data, features, predictor):
    """Focused opportunity pipeline and analysis"""
    
    st.header("💼 Opportunity Analysis")
    st.markdown("Pipeline management and opportunity insights")
    
    # Opportunity metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if 'opportunities' in processed_data:
        opp_df = processed_data['opportunities']
        
        with col1:
            total_opps = len(opp_df)
            st.metric("Total Opportunities", total_opps)
        
        with col2:
            unique_accounts = opp_df['account_st_id'].nunique()
            st.metric("Accounts with Opportunities", unique_accounts)
        
        with col3:
            avg_opps_per_account = total_opps / unique_accounts if unique_accounts > 0 else 0
            st.metric("Avg Opportunities/Account", f"{avg_opps_per_account:.1f}")
        
        with col4:
            product_lines = opp_df['product_line'].nunique()
            st.metric("Product Lines", product_lines)
        
        # Opportunity pipeline visualization
        st.subheader("📊 Pipeline Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Opportunities by account
            opps_by_account = opp_df.groupby('account_st_id').size().sort_values(ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"Customer {int(x)}" for x in opps_by_account.index],
                    y=opps_by_account.values,
                    marker_color='#01A982'
                )
            ])
            
            fig.update_layout(
                title="Opportunities by Customer",
                xaxis_title="Customer",
                yaxis_title="Number of Opportunities",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Product line distribution
            product_dist = opp_df['product_line'].value_counts().head(10)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=product_dist.index,
                    x=product_dist.values,
                    orientation='h',
                    marker_color='#FFA500'
                )
            ])
            
            fig.update_layout(
                title="Top 10 Product Lines",
                xaxis_title="Count",
                yaxis_title="Product Line",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Opportunity details table
        st.subheader("📋 Opportunity Details")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_account = st.selectbox(
                "Filter by Customer",
                ["All"] + list(opp_df['account_st_id'].unique()),
                format_func=lambda x: "All Customers" if x == "All" else f"Customer {int(x)}"
            )
        
        with col2:
            selected_product = st.selectbox(
                "Filter by Product Line",
                ["All"] + list(opp_df['product_line'].unique())
            )
        
        # Apply filters
        filtered_df = opp_df.copy()
        
        if selected_account != "All":
            filtered_df = filtered_df[filtered_df['account_st_id'] == selected_account]
        
        if selected_product != "All":
            filtered_df = filtered_df[filtered_df['product_line'] == selected_product]
        
        # Display filtered data
        if not filtered_df.empty:
            display_cols = ['opportunity_id', 'opportunity_name', 'account_name', 'product_line']
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            
            st.dataframe(
                filtered_df[available_cols],
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("No opportunities match the selected filters")
    else:
        st.warning("No opportunity data available")

def show_service_support(processed_data, features):
    """Service and support analytics"""
    
    st.header("🔧 Service & Support Analytics")
    st.markdown("Product lifecycle and service utilization insights")
    
    # Service metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    eol_products = 0
    active_warranties = 0
    expired_support = 0
    
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        
        if 'eol_urgency_score' in ib.columns:
            eol_products = len(ib[ib['eol_urgency_score'] >= 3])
        
        if 'support_status' in ib.columns:
            support_counts = ib['support_status'].value_counts()
            active_warranties = support_counts.get('Active Warranty', 0)
            expired_support = support_counts.get('Warranty Expired - Uncovered Box', 0) + \
                            support_counts.get('Expired Flex Support', 0) + \
                            support_counts.get('Expired Fixed Support', 0)
    
    total_credits = 0
    delivered_credits = 0
    
    if 'service_credits' in processed_data:
        sc = processed_data['service_credits']
        total_credits = sc['purchased_credits'].sum() if 'purchased_credits' in sc.columns else 0
        delivered_credits = sc['delivered_credits'].sum() if 'delivered_credits' in sc.columns else 0
    
    with col1:
        st.metric("⚠️ EOL/EOS Products", eol_products)
    
    with col2:
        st.metric("✅ Active Warranties", active_warranties)
    
    with col3:
        st.metric("❌ Expired Support", expired_support)
    
    with col4:
        utilization = delivered_credits / total_credits if total_credits > 0 else 0
        st.metric("📊 Credit Utilization", f"{utilization:.0%}")
    
    # Detailed analysis in tabs
    tab1, tab2, tab3 = st.tabs(["Product Lifecycle", "Service Credits", "Support Status"])
    
    with tab1:
        st.subheader("📅 Product Lifecycle Management")
        
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            # EOL/EOS timeline
            if 'days_to_eol' in ib.columns:
                eol_categories = pd.cut(
                    ib['days_to_eol'].dropna(),
                    bins=[-np.inf, 0, 180, 365, 730, np.inf],
                    labels=['Expired', '<6 months', '6-12 months', '1-2 years', '>2 years']
                )
                
                eol_dist = eol_categories.value_counts()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=eol_dist.index,
                        y=eol_dist.values,
                        marker_color=['#FF6B6B', '#FFA500', '#FFD700', '#90EE90', '#4ECDC4']
                    )
                ])
                
                fig.update_layout(
                    title="Products by Time to EOL",
                    xaxis_title="Time to EOL",
                    yaxis_title="Number of Products",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Products requiring attention
            st.subheader("🚨 Products Requiring Immediate Attention")
            
            if 'eol_urgency_score' in ib.columns:
                urgent_products = ib[ib['eol_urgency_score'] >= 3]
                
                if not urgent_products.empty:
                    display_cols = ['account_sales_territory_id', 'product_name', 
                                  'days_to_eol', 'support_status']
                    available_cols = [col for col in display_cols if col in urgent_products.columns]
                    
                    urgent_display = urgent_products[available_cols].copy()
                    urgent_display.columns = ['Customer ID', 'Product', 'Days to EOL', 'Support Status']
                    
                    st.dataframe(
                        urgent_display,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("No products require immediate attention")
    
    with tab2:
        st.subheader("💳 Service Credit Analysis")
        
        if 'service_credits' in processed_data:
            sc = processed_data['service_credits']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Credit utilization by practice
                if 'practice_name' in sc.columns:
                    practice_util = sc.groupby('practice_name').agg({
                        'purchased_credits': 'sum',
                        'delivered_credits': 'sum'
                    }).head(10)
                    
                    practice_util['utilization'] = practice_util['delivered_credits'] / practice_util['purchased_credits']
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=practice_util.index,
                            y=practice_util['utilization'] * 100,
                            marker_color='#01A982'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Credit Utilization by Practice",
                        xaxis_title="Practice",
                        yaxis_title="Utilization %",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Contract urgency
                if 'contract_urgency' in sc.columns:
                    urgency_dist = sc['contract_urgency'].value_counts()
                    
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=urgency_dist.index,
                            values=urgency_dist.values,
                            hole=0.4,
                            marker_colors=['#FF6B6B', '#FFA500', '#FFD700', '#4ECDC4']
                        )
                    ])
                    
                    fig.update_layout(
                        title="Contracts by Urgency",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🛡️ Support Coverage Analysis")
        
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            if 'support_status' in ib.columns:
                # Support status by customer
                support_by_customer = pd.crosstab(
                    ib['account_sales_territory_id'],
                    ib['support_status']
                )
                
                # Create stacked bar chart
                fig = go.Figure()
                
                for status in support_by_customer.columns:
                    fig.add_trace(go.Bar(
                        name=status,
                        x=[f"Customer {int(x)}" for x in support_by_customer.index],
                        y=support_by_customer[status]
                    ))
                
                fig.update_layout(
                    title="Support Status by Customer",
                    xaxis_title="Customer",
                    yaxis_title="Number of Products",
                    barmode='stack',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)

def show_predictive_insights(features, predictor, training_results):
    """ML insights and predictions"""
    
    st.header("📈 Predictive Insights")
    st.markdown("Machine learning-driven opportunity predictions")
    
    # Model performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Model Accuracy",
            f"{training_results['test_accuracy']:.1%}",
            help="Prediction accuracy on test data"
        )
    
    with col2:
        cv_mean = training_results['cv_scores'].mean()
        st.metric(
            "Cross-Validation Score",
            f"{cv_mean:.1%}",
            help="Average accuracy across validation folds"
        )
    
    with col3:
        feature_count = len(training_results.get('feature_importance', {}))
        st.metric(
            "Features Used",
            feature_count,
            help="Number of features in the model"
        )
    
    # Predictions overview
    st.subheader("🎯 Opportunity Predictions")
    
    predictions = predictor.predict_opportunity_propensity(features)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Confidence distribution
        fig = px.histogram(
            predictions,
            x='prediction_confidence',
            nbins=20,
            title="Prediction Confidence Distribution",
            labels={'prediction_confidence': 'Confidence Score', 'count': 'Number of Customers'}
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top opportunities
        top_opps = predictions.nlargest(5, 'prediction_confidence')[
            ['customer_id', 'predicted_propensity', 'prediction_confidence']
        ]
        
        st.markdown("**Top 5 Opportunities by Confidence**")
        
        for _, row in top_opps.iterrows():
            confidence_pct = row['prediction_confidence'] * 100
            color = "🔴" if row['predicted_propensity'] == "High" else "🟡" if row['predicted_propensity'] == "Medium" else "🟢"
            st.markdown(f"{color} Customer {int(row['customer_id'])}: {confidence_pct:.1f}% confidence ({row['predicted_propensity']})")
    
    # Feature importance
    st.subheader("🔍 Key Factors Driving Predictions")
    
    if 'feature_importance' in training_results and training_results['feature_importance']:
        importance = training_results['feature_importance']
        
        # Get top 10 features
        top_features = dict(list(importance.items())[:10])
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(top_features.values()),
                y=list(top_features.keys()),
                orientation='h',
                marker_color='#01A982'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Most Important Features",
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Actionable recommendations
    st.subheader("💡 AI-Driven Recommendations")
    
    insights = predictor.generate_opportunity_insights(features)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Opportunity Distribution**")
        
        opp_data = {
            "Priority": ["High", "Medium", "Low"],
            "Count": [
                insights['high_propensity_count'],
                insights['medium_propensity_count'],
                insights['low_propensity_count']
            ],
            "Action": [
                "Immediate engagement",
                "Nurture campaign",
                "Monitor status"
            ]
        }
        
        st.dataframe(
            pd.DataFrame(opp_data),
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.markdown("**Recommended Focus Areas**")
        
        focus_areas = []
        
        if insights['urgent_opportunities'] > 0:
            focus_areas.append(f"🔴 {insights['urgent_opportunities']} urgent opportunities require immediate action")
        
        if insights['renewal_opportunities'] > 0:
            focus_areas.append(f"🟡 {insights['renewal_opportunities']} renewal opportunities approaching")
        
        if insights['cross_sell_opportunities'] > 0:
            focus_areas.append(f"🟢 {insights['cross_sell_opportunities']} cross-sell opportunities identified")
        
        if focus_areas:
            for area in focus_areas:
                st.markdown(area)
        else:
            st.info("No specific focus areas identified")

def show_data_explorer(processed_data, features):
    """Raw data exploration tool"""
    
    st.header("📋 Data Explorer")
    st.markdown("Explore the underlying data sources")
    
    # Data source selector
    data_source = st.selectbox(
        "Select Data Source",
        list(processed_data.keys())
    )
    
    if data_source:
        df = processed_data[data_source]
        
        # Data overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Records", f"{len(df):,}")
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("Missing Data", f"{missing_pct:.1f}%")
        
        with col4:
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("Memory Usage", f"{memory_mb:.1f} MB")
        
        # Data preview and analysis tabs
        tab1, tab2, tab3 = st.tabs(["Data Preview", "Column Analysis", "Data Quality"])
        
        with tab1:
            st.subheader("Data Sample")
            
            # Add search/filter
            search_term = st.text_input("Search in data (leave empty to show all)")
            
            if search_term:
                # Search across all string columns
                mask = pd.Series(False, index=df.index)
                for col in df.select_dtypes(include=['object']).columns:
                    mask |= df[col].astype(str).str.contains(search_term, case=False, na=False)
                filtered_df = df[mask]
            else:
                filtered_df = df
            
            # Display data
            st.dataframe(
                filtered_df.head(100),
                use_container_width=True,
                height=400
            )
            
            # Download option
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"{data_source}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.subheader("Column Statistics")
            
            # Column selector
            selected_column = st.selectbox(
                "Select Column to Analyze",
                df.columns
            )
            
            if selected_column:
                col_data = df[selected_column]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Basic stats
                    st.markdown("**Column Information**")
                    stats = {
                        "Data Type": str(col_data.dtype),
                        "Non-Null Count": col_data.count(),
                        "Null Count": col_data.isnull().sum(),
                        "Unique Values": col_data.nunique(),
                        "Memory Usage": f"{col_data.memory_usage(deep=True) / 1024:.1f} KB"
                    }
                    
                    stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
                    st.dataframe(stats_df, hide_index=True, use_container_width=True)
                
                with col2:
                    # Distribution visualization
                    if pd.api.types.is_numeric_dtype(col_data):
                        st.markdown("**Value Distribution**")
                        fig = px.histogram(
                            col_data.dropna(),
                            nbins=20,
                            title=f"Distribution of {selected_column}"
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.markdown("**Top Values**")
                        top_values = col_data.value_counts().head(10)
                        fig = px.bar(
                            x=top_values.values,
                            y=top_values.index,
                            orientation='h',
                            title=f"Top 10 Values in {selected_column}"
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Data Quality Report")
            
            # Missing data analysis
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df)) * 100
            
            quality_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': missing_pct.values,
                'Data Type': [str(df[col].dtype) for col in missing_data.index]
            })
            
            quality_df = quality_df.sort_values('Missing %', ascending=False)
            
            # Color code based on missing percentage
            def highlight_missing(val):
                if val > 50:
                    return 'background-color: #ffcccc'
                elif val > 20:
                    return 'background-color: #fff3cd'
                else:
                    return ''
            
            styled_df = quality_df.style.applymap(
                highlight_missing,
                subset=['Missing %']
            ).format({'Missing %': '{:.1f}%'})
            
            st.dataframe(
                quality_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )

if __name__ == "__main__":
    main()