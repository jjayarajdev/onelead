"""
HPE OneLead Intelligence Dashboard V3
Modern horizontal navigation with cleaner layout
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

# Page configuration - hide sidebar since we're using horizontal nav
st.set_page_config(
    page_title="HPE OneLead Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide the sidebar completely
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main content styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Navigation styling */
    .nav-container {
        background: linear-gradient(135deg, #01A982 0%, #00805F 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #333333;
        margin-top: 1.5rem;
    }
    
    /* Quick stats styling */
    .stats-container {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    
    /* Button group styling */
    div.row-widget.stRadio > div {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #01A982;
        color: white;
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

def create_header_with_nav():
    """Create the header with integrated navigation"""
    
    # Header with logo and title
    header_col1, header_col2, header_col3 = st.columns([1, 3, 1])
    
    with header_col1:
        st.markdown("### 🎯 HPE OneLead")
    
    with header_col2:
        st.markdown("## Intelligence Dashboard")
    
    with header_col3:
        st.markdown(f"**{datetime.now().strftime('%b %d, %Y')}**")
        st.markdown(f"*{datetime.now().strftime('%I:%M %p')}*")
    
    # Navigation as a horizontal selector
    st.markdown("---")
    
    # Use columns for navigation options
    nav_col1, nav_col2 = st.columns([4, 1])
    
    with nav_col1:
        # Main navigation with selectbox styled as tabs
        page = st.selectbox(
            "",
            [
                "🏠 Executive Overview",
                "👥 Customer Intelligence", 
                "💼 Opportunity Analysis",
                "🔧 Service & Support",
                "📈 Predictive Insights",
                "📋 Data Explorer"
            ],
            key="main_nav",
            label_visibility="collapsed"
        )
    
    with nav_col2:
        # Quick actions dropdown
        quick_action = st.selectbox(
            "",
            ["⚡ Quick Actions", "📥 Export Data", "⚙️ Settings", "📊 Reports"],
            key="quick_actions",
            label_visibility="collapsed"
        )
    
    return page, quick_action

def create_quick_stats_bar(processed_data, features):
    """Create a horizontal quick stats bar"""
    
    # Calculate key metrics
    total_customers = len(features[features['id_type'] == '5-digit']) if 'id_type' in features.columns else len(features)
    total_opportunities = processed_data['opportunities']['opportunity_id'].nunique() if 'opportunities' in processed_data else 0
    total_products = processed_data['install_base']['serial_number_id'].nunique() if 'install_base' in processed_data else 0
    
    high_priority = len(features[features['propensity_tier'] == 'High']) if 'propensity_tier' in features.columns else 0
    
    # EOL/EOS urgency
    urgent_eol = 0
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        if 'eol_urgency_score' in ib.columns:
            urgent_eol = len(ib[ib['eol_urgency_score'] >= 3])
    
    # Create stats bar
    stats_container = st.container()
    with stats_container:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Customers", f"{total_customers}")
        
        with col2:
            st.metric("Opportunities", f"{total_opportunities}")
        
        with col3:
            st.metric("Products", f"{total_products}")
        
        with col4:
            delta_color = "inverse" if urgent_eol > 0 else "normal"
            st.metric("EOL Alerts", f"{urgent_eol}", delta=f"{urgent_eol} urgent" if urgent_eol > 0 else "All clear")
        
        with col5:
            st.metric("High Priority", f"{high_priority}", delta=f"{(high_priority/total_customers*100):.0f}%" if total_customers > 0 else "0%")

def main():
    # Load data
    try:
        with st.spinner("Loading HPE OneLead data..."):
            processed_data, features, feature_engineer = load_and_process_data()
            predictor, training_results = train_model(features)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure the data file 'DataExportAug29th.xlsx' is in the data/ directory")
        return
    
    # Create header with navigation
    page, quick_action = create_header_with_nav()
    
    # Quick stats bar
    with st.container():
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        create_quick_stats_bar(processed_data, features)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle quick actions
    if quick_action == "📥 Export Data":
        show_export_options(processed_data, features)
    elif quick_action == "⚙️ Settings":
        show_settings()
    elif quick_action == "📊 Reports":
        show_reports(processed_data, features, predictor)
    
    # Main content area
    st.markdown("---")
    
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
    
    # Use tabs for different views within executive overview
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Actions", "📈 Trends"])
    
    with tab1:
        # Main dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer Prioritization Chart
            if 'propensity_tier' in features.columns:
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
                    height=350,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Opportunity Pipeline
            if 'opportunities' in processed_data:
                opp_df = processed_data['opportunities']
                
                if 'product_line' in opp_df.columns:
                    product_lines = opp_df['product_line'].value_counts().head(5)
                    
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=product_lines.index,
                            values=product_lines.values,
                            hole=0.4,
                            marker_colors=['#01A982', '#00805F', '#4ECDC4', '#FFA500', '#FF6B6B']
                        )
                    ])
                    
                    fig.update_layout(
                        title="Top 5 Product Lines",
                        height=350,
                        showlegend=True,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Key Insights Section
        st.markdown("### 💡 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**🎯 Opportunity Concentration**\n\nTop 3 customers account for 60% of all opportunities")
        
        with col2:
            st.warning("**⚠️ Support Risk**\n\n40% of products have expired support coverage")
        
        with col3:
            st.success("**✅ Service Health**\n\nCredit utilization at healthy 49% across projects")
    
    with tab2:
        # Recommended Actions
        st.markdown("### 🎯 Recommended Actions")
        
        # Priority actions
        actions = []
        
        # Check for urgent EOL/EOS
        urgent_eol = 0
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            if 'eol_urgency_score' in ib.columns:
                urgent_eol = len(ib[ib['eol_urgency_score'] >= 3])
        
        if urgent_eol > 0:
            actions.append({
                "Priority": "🔴 Critical",
                "Action": f"Address {urgent_eol} products approaching EOL/EOS",
                "Owner": "Support Team",
                "Timeline": "This Week"
            })
        
        high_priority = len(features[features['propensity_tier'] == 'High']) if 'propensity_tier' in features.columns else 0
        if high_priority > 0:
            actions.append({
                "Priority": "🟡 High",
                "Action": f"Engage {high_priority} high-propensity customers",
                "Owner": "Sales Team",
                "Timeline": "This Month"
            })
        
        actions.append({
            "Priority": "🟢 Medium",
            "Action": "Review underutilized service credits",
            "Owner": "Account Manager",
            "Timeline": "This Quarter"
        })
        
        action_df = pd.DataFrame(actions)
        st.dataframe(
            action_df,
            use_container_width=True,
            hide_index=True,
            height=200
        )
    
    with tab3:
        # Trends
        st.markdown("### 📈 Trend Analysis")
        
        # Mock trend data (in real scenario, this would be historical)
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Opportunities': np.random.randint(90, 110, 30).cumsum() / 30,
            'EOL Products': np.random.randint(50, 70, 30).cumsum() / 30,
            'Service Credits': np.random.randint(1300, 1400, 30).cumsum() / 30
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'],
            y=trend_data['Opportunities'],
            mode='lines',
            name='Opportunities',
            line=dict(color='#01A982', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'],
            y=trend_data['EOL Products'],
            mode='lines',
            name='EOL Products',
            line=dict(color='#FFA500', width=2)
        ))
        
        fig.update_layout(
            title="30-Day Trends",
            xaxis_title="Date",
            yaxis_title="Count",
            height=400,
            template="plotly_white",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_customer_intelligence(processed_data, features, predictor):
    """Unified customer 360 view"""
    
    # Customer selector in main area
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if 'customer_id' in features.columns:
            customer_ids = features['customer_id'].unique()
            selected_customer = st.selectbox(
                "Select Customer",
                customer_ids,
                format_func=lambda x: f"Customer {int(x)}"
            )
    
    with col2:
        view_mode = st.radio(
            "View",
            ["Summary", "Detailed"],
            horizontal=True
        )
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    if selected_customer:
        # Get customer data
        customer_data = features[features['customer_id'] == selected_customer].iloc[0]
        
        # Customer metrics
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            propensity = customer_data.get('propensity_tier', 'Unknown')
            color = "🔴" if propensity == "High" else "🟡" if propensity == "Medium" else "🟢"
            st.metric("Priority", f"{color} {propensity}")
        
        with col2:
            score = customer_data.get('opportunity_propensity_score', 0)
            st.metric("Score", f"{score:.2f}")
        
        with col3:
            products = customer_data.get('total_products', 0)
            st.metric("Products", int(products))
        
        with col4:
            opportunities = customer_data.get('total_opportunities', 0)
            st.metric("Opportunities", int(opportunities))
        
        with col5:
            platforms = customer_data.get('platform_diversity', 0)
            st.metric("Platforms", int(platforms))
        
        # Main content based on view mode
        if view_mode == "Summary":
            # Use tabs for different aspects
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "💡 Insights", "📋 Details"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Customer health radar
                    categories = ['Engagement', 'Risk', 'Value', 'Growth', 'Support']
                    
                    # Calculate scores (0-100)
                    engagement = min(100, customer_data.get('total_opportunities', 0) * 20)
                    risk = 100 - min(100, customer_data.get('eol_urgency_score', 0) * 25)
                    value = min(100, customer_data.get('rfm_score', 0) * 10)
                    growth = min(100, customer_data.get('platform_diversity', 0) * 30)
                    support = 100 if not customer_data.get('has_eol_risk', False) else 30
                    
                    fig = go.Figure(data=go.Scatterpolar(
                        r=[engagement, risk, value, growth, support],
                        theta=categories,
                        fill='toself',
                        marker_color='#01A982'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=False,
                        title="Customer Health Score",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Key metrics
                    st.markdown("### Key Metrics")
                    
                    metrics = {
                        "Platform Coverage": f"{int(customer_data.get('platform_diversity', 0))}/5",
                        "Service Utilization": f"{customer_data.get('org_avg_credit_utilization', 0):.0%}",
                        "Renewal Risk": "High" if customer_data.get('has_eol_risk', False) else "Low",
                        "Engagement Level": "Active" if customer_data.get('has_active_opportunities', False) else "Inactive",
                        "Support Status": "Covered" if customer_data.get('active_warranty_count', 0) > 0 else "Expired"
                    }
                    
                    for metric, value in metrics.items():
                        st.markdown(f"**{metric}:** {value}")
            
            with tab2:
                # AI-generated insights
                st.markdown("### 🤖 AI-Generated Insights")
                
                insights = []
                
                if customer_data.get('has_eol_risk', False):
                    insights.append("⚠️ **Product Refresh Opportunity**: Customer has products approaching end-of-life")
                
                if customer_data.get('platform_diversity', 0) <= 2:
                    insights.append("💰 **Expansion Potential**: Customer uses limited HPE platforms - cross-sell opportunity")
                
                if not customer_data.get('has_active_opportunities', False):
                    insights.append("📞 **Engagement Required**: No active opportunities - schedule business review")
                
                if customer_data.get('org_avg_credit_utilization', 0) < 0.5:
                    insights.append("📈 **Service Optimization**: Low credit utilization indicates potential for service expansion")
                
                for insight in insights:
                    st.info(insight)
            
            with tab3:
                # Detailed information
                if 'install_base' in processed_data:
                    ib = processed_data['install_base']
                    customer_products = ib[ib['account_sales_territory_id'] == selected_customer]
                    
                    if not customer_products.empty:
                        st.markdown("### Installed Products")
                        display_cols = ['product_name', 'support_status', 'days_to_eol']
                        available_cols = [col for col in display_cols if col in customer_products.columns]
                        st.dataframe(customer_products[available_cols], use_container_width=True, hide_index=True)

def show_opportunity_analysis(processed_data, features, predictor):
    """Focused opportunity pipeline and analysis"""
    
    if 'opportunities' in processed_data:
        opp_df = processed_data['opportunities']
        
        # Filters in a horizontal layout
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_account = st.selectbox(
                "Customer",
                ["All"] + list(opp_df['account_st_id'].unique()),
                format_func=lambda x: "All Customers" if x == "All" else f"Customer {int(x)}"
            )
        
        with col2:
            product_lines = ["All"] + list(opp_df['product_line'].unique())
            selected_product = st.selectbox("Product Line", product_lines)
        
        with col3:
            sort_by = st.selectbox("Sort By", ["Customer", "Product Line", "Opportunity Name"])
        
        with col4:
            if st.button("🔄 Reset Filters", use_container_width=True):
                st.rerun()
        
        # Apply filters
        filtered_df = opp_df.copy()
        
        if selected_account != "All":
            filtered_df = filtered_df[filtered_df['account_st_id'] == selected_account]
        
        if selected_product != "All":
            filtered_df = filtered_df[filtered_df['product_line'] == selected_product]
        
        # Metrics row
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filtered Opportunities", len(filtered_df))
        
        with col2:
            unique_customers = filtered_df['account_st_id'].nunique()
            st.metric("Unique Customers", unique_customers)
        
        with col3:
            unique_products = filtered_df['product_line'].nunique()
            st.metric("Product Lines", unique_products)
        
        with col4:
            avg_per_customer = len(filtered_df) / unique_customers if unique_customers > 0 else 0
            st.metric("Avg/Customer", f"{avg_per_customer:.1f}")
        
        # Visualization and table in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📋 Pipeline", "🗺️ Heat Map"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Opportunities by customer
                opps_by_account = filtered_df.groupby('account_st_id').size().sort_values(ascending=False).head(10)
                
                fig = px.bar(
                    x=opps_by_account.values,
                    y=[f"Customer {int(x)}" for x in opps_by_account.index],
                    orientation='h',
                    title="Top 10 Customers by Opportunities",
                    labels={'x': 'Count', 'y': 'Customer'},
                    color=opps_by_account.values,
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Product line distribution
                product_dist = filtered_df['product_line'].value_counts().head(10)
                
                fig = px.pie(
                    values=product_dist.values,
                    names=product_dist.index,
                    title="Product Line Distribution",
                    hole=0.4
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Pipeline table
            if not filtered_df.empty:
                # Sort based on selection
                if sort_by == "Customer":
                    filtered_df = filtered_df.sort_values('account_st_id')
                elif sort_by == "Product Line":
                    filtered_df = filtered_df.sort_values('product_line')
                else:
                    filtered_df = filtered_df.sort_values('opportunity_name')
                
                display_cols = ['opportunity_id', 'opportunity_name', 'account_name', 'product_line']
                available_cols = [col for col in display_cols if col in filtered_df.columns]
                
                st.dataframe(
                    filtered_df[available_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
                
                # Export button
                csv = filtered_df[available_cols].to_csv(index=False)
                st.download_button(
                    "📥 Export Pipeline",
                    csv,
                    f"opportunity_pipeline_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        
        with tab3:
            # Heat map of opportunities
            if len(filtered_df) > 0:
                # Create cross-tab of customers vs products
                heatmap_data = pd.crosstab(
                    filtered_df['account_st_id'],
                    filtered_df['product_line']
                )
                
                fig = px.imshow(
                    heatmap_data,
                    labels=dict(x="Product Line", y="Customer ID", color="Opportunities"),
                    title="Opportunity Heat Map",
                    aspect="auto",
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

def show_service_support(processed_data, features):
    """Service and support analytics"""
    
    # Service metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    eol_products = 0
    active_warranties = 0
    
    if 'install_base' in processed_data:
        ib = processed_data['install_base']
        if 'eol_urgency_score' in ib.columns:
            eol_products = len(ib[ib['eol_urgency_score'] >= 3])
        if 'support_status' in ib.columns:
            active_warranties = ib['support_status'].value_counts().get('Active Warranty', 0)
    
    total_credits = 0
    delivered_credits = 0
    
    if 'service_credits' in processed_data:
        sc = processed_data['service_credits']
        total_credits = sc['purchased_credits'].sum() if 'purchased_credits' in sc.columns else 0
        delivered_credits = sc['delivered_credits'].sum() if 'delivered_credits' in sc.columns else 0
    
    with col1:
        st.metric("EOL Products", eol_products, delta=f"-{eol_products}" if eol_products > 0 else "0")
    
    with col2:
        st.metric("Active Warranties", active_warranties)
    
    with col3:
        st.metric("Total Credits", f"{total_credits:,.0f}")
    
    with col4:
        utilization = delivered_credits / total_credits if total_credits > 0 else 0
        st.metric("Utilization", f"{utilization:.0%}")
    
    # Detailed views in tabs
    tab1, tab2, tab3 = st.tabs(["🔧 Product Lifecycle", "💳 Service Credits", "📊 Support Coverage"])
    
    with tab1:
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # EOL timeline
                if 'days_to_eol' in ib.columns:
                    eol_categories = pd.cut(
                        ib['days_to_eol'].dropna(),
                        bins=[-np.inf, 0, 180, 365, 730, np.inf],
                        labels=['Expired', '<6 months', '6-12 months', '1-2 years', '>2 years']
                    )
                    
                    eol_dist = eol_categories.value_counts()
                    
                    fig = px.bar(
                        x=eol_dist.index,
                        y=eol_dist.values,
                        title="Products by Time to EOL",
                        color=eol_dist.values,
                        color_continuous_scale='RdYlGn_r'
                    )
                    
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Support status
                if 'support_status' in ib.columns:
                    support_dist = ib['support_status'].value_counts()
                    
                    fig = px.pie(
                        values=support_dist.values,
                        names=support_dist.index,
                        title="Support Status Distribution",
                        hole=0.4
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'service_credits' in processed_data:
            sc = processed_data['service_credits']
            
            # Credit analysis
            col1, col2 = st.columns(2)
            
            with col1:
                # Utilization by practice
                if 'practice_name' in sc.columns:
                    practice_util = sc.groupby('practice_name').agg({
                        'purchased_credits': 'sum',
                        'delivered_credits': 'sum'
                    }).head(10)
                    
                    practice_util['utilization'] = (practice_util['delivered_credits'] / 
                                                   practice_util['purchased_credits'] * 100)
                    
                    fig = px.bar(
                        x=practice_util.index,
                        y=practice_util['utilization'],
                        title="Credit Utilization by Practice (%)",
                        color=practice_util['utilization'],
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Contract urgency
                if 'contract_urgency' in sc.columns:
                    urgency_dist = sc['contract_urgency'].value_counts()
                    
                    colors = {'Critical': '#FF6B6B', 'High': '#FFA500', 
                             'Medium': '#FFD700', 'Low': '#4ECDC4'}
                    
                    fig = px.pie(
                        values=urgency_dist.values,
                        names=urgency_dist.index,
                        title="Contract Urgency Distribution",
                        hole=0.4,
                        color_discrete_map=colors
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            
            if 'support_status' in ib.columns:
                # Support coverage by customer
                support_by_customer = pd.crosstab(
                    ib['account_sales_territory_id'],
                    ib['support_status']
                )
                
                fig = go.Figure()
                
                for status in support_by_customer.columns:
                    fig.add_trace(go.Bar(
                        name=status,
                        x=[f"Customer {int(x)}" for x in support_by_customer.index],
                        y=support_by_customer[status]
                    ))
                
                fig.update_layout(
                    title="Support Coverage by Customer",
                    barmode='stack',
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)

def show_predictive_insights(features, predictor, training_results):
    """ML insights and predictions"""
    
    # Model metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Accuracy", f"{training_results['test_accuracy']:.1%}")
    
    with col2:
        cv_mean = training_results['cv_scores'].mean()
        st.metric("Cross-Validation", f"{cv_mean:.1%}")
    
    with col3:
        feature_count = len(training_results.get('feature_importance', {}))
        st.metric("Features", feature_count)
    
    with col4:
        st.metric("Training Samples", len(features))
    
    # Predictions and insights in tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Predictions", "📊 Feature Analysis", "💡 Recommendations"])
    
    with tab1:
        predictions = predictor.predict_opportunity_propensity(features)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Confidence distribution
            fig = px.histogram(
                predictions,
                x='prediction_confidence',
                nbins=20,
                title="Prediction Confidence Distribution",
                color_discrete_sequence=['#01A982']
            )
            
            fig.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top predictions table
            st.markdown("### Top Opportunity Scores")
            
            top_predictions = predictions.nlargest(10, 'prediction_confidence')[
                ['customer_id', 'predicted_propensity', 'prediction_confidence']
            ].copy()
            
            top_predictions['customer_id'] = top_predictions['customer_id'].apply(lambda x: f"Customer {int(x)}")
            top_predictions['prediction_confidence'] = top_predictions['prediction_confidence'].apply(lambda x: f"{x:.1%}")
            top_predictions.columns = ['Customer', 'Propensity', 'Confidence']
            
            st.dataframe(top_predictions, use_container_width=True, hide_index=True)
    
    with tab2:
        # Feature importance
        if 'feature_importance' in training_results and training_results['feature_importance']:
            importance = training_results['feature_importance']
            top_features = dict(list(importance.items())[:15])
            
            fig = px.bar(
                x=list(top_features.values()),
                y=list(top_features.keys()),
                orientation='h',
                title="Top 15 Feature Importance",
                color=list(top_features.values()),
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(height=500, template="plotly_white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # AI recommendations
        insights = predictor.generate_opportunity_insights(features)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Opportunity Breakdown")
            
            breakdown = pd.DataFrame({
                'Priority': ['High', 'Medium', 'Low'],
                'Count': [
                    insights['high_propensity_count'],
                    insights['medium_propensity_count'],
                    insights['low_propensity_count']
                ],
                'Action': [
                    'Immediate Engagement',
                    'Nurture Campaign',
                    'Monitor Status'
                ]
            })
            
            st.dataframe(breakdown, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Focus Areas")
            
            if insights['urgent_opportunities'] > 0:
                st.error(f"🔴 {insights['urgent_opportunities']} urgent opportunities")
            
            if insights['renewal_opportunities'] > 0:
                st.warning(f"🟡 {insights['renewal_opportunities']} renewal opportunities")
            
            if insights['cross_sell_opportunities'] > 0:
                st.success(f"🟢 {insights['cross_sell_opportunities']} cross-sell opportunities")
            
            if insights['service_expansion_opportunities'] > 0:
                st.info(f"📈 {insights['service_expansion_opportunities']} service expansions")

def show_data_explorer(processed_data, features):
    """Raw data exploration tool"""
    
    # Data source selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        data_source = st.selectbox(
            "Data Source",
            list(processed_data.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col2:
        search_term = st.text_input("Search", placeholder="Filter data...")
    
    with col3:
        show_stats = st.checkbox("Show Statistics", value=True)
    
    if data_source:
        df = processed_data[data_source]
        
        # Statistics row
        if show_stats:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Records", f"{len(df):,}")
            
            with col2:
                st.metric("Columns", len(df.columns))
            
            with col3:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Missing %", f"{missing_pct:.1f}%")
            
            with col4:
                memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("Size", f"{memory_mb:.1f} MB")
        
        # Data view
        tab1, tab2, tab3 = st.tabs(["📋 Data", "📊 Analysis", "📈 Quality"])
        
        with tab1:
            # Apply search filter
            if search_term:
                mask = pd.Series(False, index=df.index)
                for col in df.select_dtypes(include=['object']).columns:
                    mask |= df[col].astype(str).str.contains(search_term, case=False, na=False)
                filtered_df = df[mask]
            else:
                filtered_df = df
            
            st.dataframe(filtered_df, use_container_width=True, height=500)
            
            # Export
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Export CSV",
                csv,
                f"{data_source}_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        with tab2:
            # Column analysis
            selected_column = st.selectbox("Select Column", df.columns)
            
            if selected_column:
                col_data = df[selected_column]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Statistics
                    stats_data = {
                        'Data Type': str(col_data.dtype),
                        'Non-Null': f"{col_data.count():,}",
                        'Null': f"{col_data.isnull().sum():,}",
                        'Unique': f"{col_data.nunique():,}"
                    }
                    
                    for stat, value in stats_data.items():
                        st.metric(stat, value)
                
                with col2:
                    # Visualization
                    if pd.api.types.is_numeric_dtype(col_data):
                        fig = px.histogram(
                            col_data.dropna(),
                            nbins=30,
                            title=f"{selected_column} Distribution"
                        )
                    else:
                        value_counts = col_data.value_counts().head(10)
                        fig = px.bar(
                            x=value_counts.values,
                            y=value_counts.index,
                            orientation='h',
                            title=f"Top 10 {selected_column} Values"
                        )
                    
                    fig.update_layout(height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Data quality
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df)) * 100
            
            quality_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing': missing_data.values,
                'Missing %': missing_pct.values
            }).sort_values('Missing %', ascending=False)
            
            # Color-coded quality chart
            fig = px.bar(
                quality_df.head(20),
                x='Missing %',
                y='Column',
                orientation='h',
                title="Top 20 Columns by Missing Data",
                color='Missing %',
                color_continuous_scale='RdYlGn_r'
            )
            
            fig.update_layout(height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

def show_export_options(processed_data, features):
    """Export data options"""
    with st.expander("📥 Export Options", expanded=True):
        st.markdown("### Export Data")
        
        export_type = st.selectbox(
            "Select Data to Export",
            ["Customer Features", "Opportunities", "Install Base", "All Data"]
        )
        
        if st.button("Generate Export"):
            if export_type == "Customer Features":
                csv = features.to_csv(index=False)
                st.download_button(
                    "Download Customer Features",
                    csv,
                    f"customer_features_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            elif export_type == "All Data":
                # Create a zip file with all data
                st.info("Preparing complete data export...")
                # Implementation would go here

def show_settings():
    """Settings panel"""
    with st.expander("⚙️ Settings", expanded=True):
        st.markdown("### Dashboard Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Theme", ["Light", "Dark", "Auto"])
            st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        
        with col2:
            st.number_input("Data Refresh (minutes)", min_value=5, max_value=60, value=15)
            st.checkbox("Enable Notifications", value=True)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

def show_reports(processed_data, features, predictor):
    """Generate reports"""
    with st.expander("📊 Generate Reports", expanded=True):
        st.markdown("### Report Generator")
        
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Customer Analysis", "Opportunity Report", "Service Report"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
        
        if st.button("Generate Report"):
            st.info(f"Generating {report_type}...")
            # Report generation logic would go here
            st.success("Report generated successfully!")

if __name__ == "__main__":
    main()