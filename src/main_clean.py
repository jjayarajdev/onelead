"""
HPE OneLead Service Recommendation Dashboard
Clean, intuitive UI for service recommendations and opportunity management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

# Import data loaders
from data_processing.sqlite_loader import OneleadSQLiteLoader
from data_processing.enhanced_recommendation_engine import EnhancedRecommendationEngine

# Page configuration
st.set_page_config(
    page_title="HPE OneLead - Service Recommendations",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, modern CSS
st.markdown("""
<style>
    /* Main layout */
    .main {
        padding: 1rem 2rem;
        background-color: #F8F9FA;
    }

    /* Header styling */
    h1 {
        color: #01A982;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    h2 {
        color: #333;
        font-weight: 500;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    h3 {
        color: #555;
        font-weight: 500;
        font-size: 1.1rem;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    div[data-testid="metric-container"] label {
        color: white !important;
        font-weight: 500;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700;
    }

    /* Info boxes */
    .info-box {
        background-color: white;
        border-left: 4px solid #01A982;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Filter section */
    .filter-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }

    /* Tables */
    .dataframe {
        border: none !important;
    }

    /* Buttons */
    .stDownloadButton button {
        background-color: #01A982;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }

    .stDownloadButton button:hover {
        background-color: #018f6e;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 10px;
        padding: 0 30px;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #01A982 0%, #018f6e 100%);
        color: white;
        font-weight: 600;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_database_data():
    """Load all data from SQLite database"""
    loader = OneleadSQLiteLoader("data/onelead.db")
    return loader.load_all_data()

@st.cache_resource
def get_recommendation_engine():
    """Get cached recommendation engine instance"""
    return EnhancedRecommendationEngine('data/onelead.db')

def show_overview():
    """Dashboard overview with key metrics"""
    st.title("🎯 HPE OneLead Service Recommendations")
    st.markdown("**AI-powered service recommendations with SKU codes for faster quoting**")
    st.markdown("---")

    # Key metrics
    engine = get_recommendation_engine()
    data = load_database_data()

    col1, col2, col3, col4 = st.columns(4)

    # Get recommendation count
    try:
        recs = engine.generate_quote_ready_export()
        total_recs = len(recs)
        quote_ready = recs['quote_ready'].sum() if 'quote_ready' in recs.columns else 0
    except:
        total_recs = 0
        quote_ready = 0

    with col1:
        st.metric("📋 Total Recommendations", total_recs)

    with col2:
        st.metric("✅ Quote-Ready", quote_ready)

    with col3:
        customers = len(data['customers']) if 'customers' in data and not data['customers'].empty else 0
        st.metric("👥 Customers", customers)

    with col4:
        install_base = len(data['install_base']) if 'install_base' in data and not data['install_base'].empty else 0
        st.metric("💻 Products", install_base)

def show_recommendations():
    """Main recommendations view"""
    st.header("🎯 Service Recommendations")
    st.markdown("Browse SKU-level service recommendations for your customers")

    engine = get_recommendation_engine()
    data = load_database_data()

    # Filter section
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.subheader("🔍 Filters")

        col1, col2, col3 = st.columns(3)

        with col1:
            urgency_filter = st.multiselect(
                "Urgency Level",
                options=['Critical', 'High', 'Medium', 'Low'],
                default=['Critical', 'High'],
                help="Filter recommendations by urgency"
            )

        with col2:
            confidence_min = st.slider(
                "Minimum Confidence",
                min_value=50,
                max_value=100,
                value=65,
                step=5,
                help="Show only recommendations above this confidence level"
            )

        with col3:
            # Get customer list
            customers = data['customers'] if 'customers' in data and not data['customers'].empty else pd.DataFrame()
            if not customers.empty and 'customer_name' in customers.columns:
                customer_options = ['All Customers'] + sorted(customers['customer_name'].unique().tolist())
                selected_customer = st.selectbox(
                    "Customer",
                    options=customer_options,
                    help="Filter by specific customer"
                )
            else:
                selected_customer = 'All Customers'

        st.markdown('</div>', unsafe_allow_html=True)

    # Get recommendations
    try:
        customer_id = None if selected_customer == 'All Customers' else selected_customer
        recs = engine.generate_quote_ready_export(
            customer_id=customer_id,
            urgency_filter=urgency_filter if urgency_filter else None
        )

        # Apply confidence filter
        if not recs.empty and 'confidence' in recs.columns:
            recs = recs[recs['confidence'] >= confidence_min]

        if not recs.empty:
            st.markdown(f"**Showing {len(recs)} recommendations**")

            # Display options
            col1, col2 = st.columns([3, 1])
            with col2:
                view_mode = st.radio(
                    "View",
                    options=["Table", "Cards"],
                    horizontal=True,
                    help="Choose how to display recommendations"
                )

            st.markdown("---")

            if view_mode == "Table":
                # Table view
                display_cols = []
                if 'customer_name' in recs.columns:
                    display_cols.append('customer_name')
                if 'product_name' in recs.columns:
                    display_cols.append('product_name')
                if 'service_name' in recs.columns:
                    display_cols.append('service_name')
                if 'sku_codes' in recs.columns:
                    display_cols.append('sku_codes')
                if 'urgency' in recs.columns:
                    display_cols.append('urgency')
                if 'confidence' in recs.columns:
                    display_cols.append('confidence')
                if 'quote_ready' in recs.columns:
                    display_cols.append('quote_ready')

                display_df = recs[display_cols] if display_cols else recs

                # Rename columns for clarity
                column_config = {
                    'customer_name': 'Customer',
                    'product_name': 'Product',
                    'service_name': 'Service',
                    'sku_codes': 'SKU Code',
                    'urgency': 'Urgency',
                    'confidence': st.column_config.ProgressColumn(
                        'Confidence',
                        format='%d%%',
                        min_value=0,
                        max_value=100
                    ),
                    'quote_ready': st.column_config.CheckboxColumn('Quote Ready')
                }

                st.dataframe(
                    display_df,
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True,
                    height=500
                )
            else:
                # Card view
                for idx, row in recs.iterrows():
                    with st.expander(f"**{row.get('customer_name', 'N/A')}** - {row.get('service_name', 'N/A')}", expanded=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Product:** {row.get('product_name', 'N/A')}")
                            st.markdown(f"**SKU Code:** `{row.get('sku_codes', 'Contact HPE')}`")
                            st.markdown(f"**Urgency:** {row.get('urgency', 'N/A')}")

                        with col2:
                            st.markdown(f"**Service:** {row.get('service_name', 'N/A')}")
                            confidence = row.get('confidence', 0)
                            st.markdown(f"**Confidence:** {confidence}%")
                            quote_ready = "✅ Yes" if row.get('quote_ready', False) else "❌ No"
                            st.markdown(f"**Quote Ready:** {quote_ready}")

            # Export options
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                csv = recs.to_csv(index=False)
                st.download_button(
                    label="📥 Download All",
                    data=csv,
                    file_name=f"recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            with col2:
                if 'quote_ready' in recs.columns:
                    quote_ready_df = recs[recs['quote_ready'] == True]
                    if not quote_ready_df.empty:
                        csv_ready = quote_ready_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Quote-Ready",
                            data=csv_ready,
                            file_name=f"quote_ready_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
        else:
            st.info("📭 No recommendations match your filters. Try adjusting the filter criteria.")

    except Exception as e:
        st.error(f"Error loading recommendations: {str(e)}")
        st.info("💡 Tip: Make sure the database contains Install Base data and LS_SKU mappings")

def show_customers():
    """Customer view with their recommendations"""
    st.header("👥 Customers")
    st.markdown("View recommendations grouped by customer")

    engine = get_recommendation_engine()
    data = load_database_data()

    try:
        recs = engine.generate_quote_ready_export()

        if not recs.empty and 'customer_name' in recs.columns:
            # Group by customer
            customer_summary = recs.groupby('customer_name').agg({
                'service_name': 'count',
                'quote_ready': 'sum' if 'quote_ready' in recs.columns else lambda x: 0
            }).reset_index()

            customer_summary.columns = ['Customer', 'Total Recommendations', 'Quote-Ready']
            customer_summary = customer_summary.sort_values('Total Recommendations', ascending=False)

            st.markdown(f"**{len(customer_summary)} customers with recommendations**")
            st.markdown("---")

            # Display customer cards
            for _, customer_row in customer_summary.iterrows():
                customer_name = customer_row['Customer']
                total_recs = customer_row['Total Recommendations']
                quote_ready_count = customer_row['Quote-Ready']

                with st.expander(f"**{customer_name}** ({total_recs} recommendations)", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Recommendations", total_recs)
                    with col2:
                        st.metric("Quote-Ready", quote_ready_count)
                    with col3:
                        ready_pct = (quote_ready_count / total_recs * 100) if total_recs > 0 else 0
                        st.metric("Ready %", f"{ready_pct:.0f}%")

                    # Show customer's recommendations
                    customer_recs = recs[recs['customer_name'] == customer_name]

                    display_cols = ['service_name', 'sku_codes', 'urgency', 'confidence']
                    display_cols = [c for c in display_cols if c in customer_recs.columns]

                    st.dataframe(
                        customer_recs[display_cols],
                        hide_index=True,
                        use_container_width=True
                    )

                    # Download button for this customer
                    csv = customer_recs.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {customer_name}'s Recommendations",
                        data=csv,
                        file_name=f"{customer_name}_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"download_{customer_name}"
                    )
        else:
            st.info("📭 No customer recommendations available")

    except Exception as e:
        st.error(f"Error loading customer data: {str(e)}")

def show_analytics():
    """Analytics and insights"""
    st.header("📊 Analytics")
    st.markdown("Insights into recommendations and coverage")

    engine = get_recommendation_engine()

    try:
        recs = engine.generate_quote_ready_export()

        if not recs.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Recommendations by Urgency")
                if 'urgency' in recs.columns:
                    urgency_counts = recs['urgency'].value_counts()
                    fig = px.pie(
                        values=urgency_counts.values,
                        names=urgency_counts.index,
                        color=urgency_counts.index,
                        color_discrete_map={
                            'Critical': '#DC143C',
                            'High': '#FF6B35',
                            'Medium': '#FFA500',
                            'Low': '#90EE90'
                        }
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(showlegend=False, height=350)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Confidence Distribution")
                if 'confidence' in recs.columns:
                    fig = px.histogram(
                        recs,
                        x='confidence',
                        nbins=10,
                        color_discrete_sequence=['#01A982']
                    )
                    fig.update_layout(
                        xaxis_title="Confidence Score (%)",
                        yaxis_title="Count",
                        showlegend=False,
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # SKU Coverage
            st.markdown("---")
            st.subheader("SKU Code Coverage")

            col1, col2, col3 = st.columns(3)

            with col1:
                has_sku = recs['sku_codes'].notna().sum() if 'sku_codes' in recs.columns else 0
                st.metric("Services with SKU", has_sku)

            with col2:
                no_sku = recs['sku_codes'].isna().sum() if 'sku_codes' in recs.columns else 0
                st.metric("Needs Follow-up", no_sku)

            with col3:
                coverage = (has_sku / len(recs) * 100) if len(recs) > 0 else 0
                st.metric("SKU Coverage", f"{coverage:.1f}%")

        else:
            st.info("📭 No data available for analytics")

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def show_data_browser():
    """Data browser to explore Excel and database tables"""
    st.header("💾 Data Browser")
    st.markdown("Explore source data and database mappings")

    data = load_database_data()
    conn = sqlite3.connect('data/onelead.db')

    # Data overview
    st.subheader("📊 Data Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cursor = conn.execute("SELECT COUNT(*) FROM dim_customer")
        customer_count = cursor.fetchone()[0]
        st.metric("Customers", customer_count)

    with col2:
        cursor = conn.execute("SELECT COUNT(*) FROM dim_product")
        product_count = cursor.fetchone()[0]
        st.metric("Products", product_count)

    with col3:
        cursor = conn.execute("SELECT COUNT(*) FROM dim_ls_sku_service")
        service_count = cursor.fetchone()[0]
        st.metric("LS_SKU Services", service_count)

    with col4:
        cursor = conn.execute("SELECT COUNT(*) FROM fact_install_base")
        install_count = cursor.fetchone()[0]
        st.metric("Install Base", install_count)

    st.markdown("---")

    # Table selector
    st.subheader("🔍 Browse Tables")

    table_category = st.radio(
        "Select Category",
        options=["Source Data (Excel)", "LS_SKU Catalog", "Mappings & Integration", "Fact Tables"],
        horizontal=True
    )

    if table_category == "Source Data (Excel)":
        table_options = {
            "Customers": "dim_customer",
            "Products": "dim_product",
            "Services": "dim_service",
            "Opportunities": "fact_opportunity",
            "Service Credits": "fact_service_credit"
        }
    elif table_category == "LS_SKU Catalog":
        table_options = {
            "LS_SKU Products": "dim_ls_sku_product",
            "LS_SKU Services": "dim_ls_sku_service",
            "SKU Codes": "dim_sku_code",
            "Product-Service Mappings": "map_product_service_sku",
            "Service-SKU Mappings": "map_service_sku"
        }
    elif table_category == "Mappings & Integration":
        table_options = {
            "Install Base to LS_SKU": "map_install_base_to_ls_sku",
            "Customer Mappings": "map_customer",
            "Practice Mappings": "map_practice"
        }
    else:  # Fact Tables
        table_options = {
            "Install Base": "fact_install_base",
            "Opportunities": "fact_opportunity",
            "Service Credits": "fact_service_credit",
            "A&PS Projects": "fact_aps_project"
        }

    selected_table_name = st.selectbox("Select Table", options=list(table_options.keys()))
    selected_table = table_options[selected_table_name]

    # Load and display table
    try:
        query = f"SELECT * FROM {selected_table} LIMIT 100"
        df = pd.read_sql(query, conn)

        st.markdown(f"**{selected_table_name}** - Showing up to 100 rows")
        st.markdown(f"Total columns: {len(df.columns)}")

        # Display table
        st.dataframe(df, use_container_width=True, height=400)

        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {selected_table_name}",
            data=csv,
            file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error loading table: {str(e)}")

    conn.close()

def show_database_mapping():
    """Show database schema and mapping statistics"""
    st.header("🗄️ Database Schema & Mappings")
    st.markdown("Understanding how data flows through the system")

    conn = sqlite3.connect('data/onelead.db')

    # Mapping Statistics
    st.subheader("🔗 Data Integration Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📦 Product Mappings**")

        # Install Base to LS_SKU mapping
        cursor = conn.execute("""
            SELECT
                COUNT(DISTINCT ib.product_key) as total_products,
                COUNT(DISTINCT m.product_key) as mapped_products,
                ROUND(COUNT(DISTINCT m.product_key) * 100.0 / NULLIF(COUNT(DISTINCT ib.product_key), 0), 1) as match_rate
            FROM fact_install_base ib
            LEFT JOIN map_install_base_to_ls_sku m ON ib.product_key = m.product_key
        """)
        row = cursor.fetchone()

        st.metric("Total Products", row[0])
        st.metric("Mapped to LS_SKU", row[1])
        st.metric("Match Rate", f"{row[2]}%" if row[2] else "0%")

    with col2:
        st.markdown("**🔧 Service Coverage**")

        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_services,
                COUNT(DISTINCT msk.ls_service_key) as services_with_sku
            FROM dim_ls_sku_service s
            LEFT JOIN map_service_sku msk ON s.ls_service_key = msk.ls_service_key
        """)
        row = cursor.fetchone()
        total_services = row[0]
        services_with_sku = row[1]
        coverage = (services_with_sku / total_services * 100) if total_services > 0 else 0

        st.metric("Total Services", total_services)
        st.metric("Services with SKU", services_with_sku)
        st.metric("SKU Coverage", f"{coverage:.1f}%")

    st.markdown("---")

    # Detailed mapping view
    st.subheader("🔍 Product-to-LS_SKU Mappings")

    cursor = conn.execute("""
        SELECT
            p.product_description,
            lp.product_name as ls_sku_product,
            m.confidence_score,
            m.match_method,
            CASE
                WHEN m.confidence_score >= 90 THEN '🟢 High'
                WHEN m.confidence_score >= 75 THEN '🟡 Medium'
                ELSE '🔴 Low'
            END as confidence_level
        FROM map_install_base_to_ls_sku m
        JOIN dim_product p ON m.product_key = p.product_key
        JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
        ORDER BY m.confidence_score DESC
    """)

    mapping_df = pd.DataFrame(
        cursor.fetchall(),
        columns=['Install Base Product', 'LS_SKU Product', 'Confidence', 'Method', 'Quality']
    )

    if not mapping_df.empty:
        st.dataframe(mapping_df, use_container_width=True, height=300)

        # Mapping quality chart
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Mapping Methods Used**")
            method_counts = mapping_df['Method'].value_counts()
            fig = px.pie(values=method_counts.values, names=method_counts.index)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Confidence Distribution**")
            quality_counts = mapping_df['Quality'].value_counts()
            fig = px.bar(x=quality_counts.index, y=quality_counts.values, color=quality_counts.index,
                        color_discrete_map={'🟢 High': '#28a745', '🟡 Medium': '#ffc107', '🔴 Low': '#dc3545'})
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count", height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product mappings found. Run the LS_SKU data loader to create mappings.")

    st.markdown("---")

    # Database schema diagram (text-based)
    st.subheader("📐 Database Schema Overview")

    with st.expander("View Database Structure", expanded=False):
        st.markdown("""
        ### Dimension Tables (Master Data)
        - **dim_customer** - Customer master data
        - **dim_product** - Product catalog from Install Base
        - **dim_service** - HPE service catalog
        - **dim_ls_sku_product** - LS_SKU product catalog (22 products)
        - **dim_ls_sku_service** - LS_SKU service catalog (53 services)
        - **dim_sku_code** - SKU code master (9 codes)

        ### Fact Tables (Transactional Data)
        - **fact_install_base** - Customer product inventory
        - **fact_opportunity** - Sales opportunities
        - **fact_service_credit** - Service credit tracking
        - **fact_aps_project** - A&PS project history

        ### Mapping Tables (Integration Layer)
        - **map_install_base_to_ls_sku** - Links Install Base products to LS_SKU catalog
        - **map_product_service_sku** - Links LS_SKU products to services with SKU codes
        - **map_service_sku** - Links services to SKU codes
        - **map_customer** - Customer name standardization
        - **map_practice** - Practice/portfolio mappings

        ### Data Flow
        1. **Excel Data** → dim_customer, dim_product, fact_install_base
        2. **LS_SKU Excel** → dim_ls_sku_product, dim_ls_sku_service, dim_sku_code
        3. **Product Matcher** → map_install_base_to_ls_sku (82.5% match rate)
        4. **Recommendation Engine** → Joins all tables to generate recommendations
        """)

    conn.close()

def main():
    """Main application"""

    # Show overview at top
    show_overview()

    st.markdown("---")

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Recommendations",
        "👥 Customers",
        "📊 Analytics",
        "💾 Data Browser",
        "🗄️ Database Schema"
    ])

    with tab1:
        show_recommendations()

    with tab2:
        show_customers()

    with tab3:
        show_analytics()

    with tab4:
        show_data_browser()

    with tab5:
        show_database_mapping()

    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()