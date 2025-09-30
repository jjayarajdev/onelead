"""
HPE OneLead - Step-by-Step Service Recommendation System
Shows the complete data flow from Excel → Database → Recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
from pathlib import Path
import os
import sys
import subprocess

# Auto-setup database if not exists
def setup_database_if_needed():
    """Check if database exists and has required tables"""
    db_path = 'data/onelead.db'

    # Check if database exists and is valid
    needs_setup = False

    if not os.path.exists(db_path):
        needs_setup = True
    else:
        # Check if required tables exist
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dim_ls_sku_product'")
            if cursor.fetchone() is None:
                needs_setup = True
            conn.close()
        except:
            needs_setup = True

    if needs_setup:
        st.warning("🔄 Setting up database for the first time... This will take about 30 seconds.")

        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        try:
            # Run database creation script
            with st.spinner("📊 Creating database schema and loading customer data..."):
                result = subprocess.run(
                    [sys.executable, 'src/database/create_sqlite_database.py'],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=os.getcwd()
                )

                if result.returncode != 0:
                    st.error("❌ Database creation failed!")
                    with st.expander("Show error details"):
                        st.code(result.stderr)
                    st.stop()
                else:
                    st.success("✅ Database created successfully")

            # Load LS_SKU data
            with st.spinner("📦 Loading service catalog (LS_SKU data)..."):
                result = subprocess.run(
                    [sys.executable, 'src/database/ls_sku_data_loader.py'],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=os.getcwd()
                )

                if result.returncode != 0:
                    st.error("❌ LS_SKU loading failed!")
                    with st.expander("Show error details"):
                        st.code(result.stderr)
                    st.stop()
                else:
                    st.success("✅ Service catalog loaded successfully")

            st.success("🎉 Database setup complete! Reloading app...")
            st.balloons()

            # Wait a moment then rerun
            import time
            time.sleep(2)
            st.rerun()

        except subprocess.TimeoutExpired:
            st.error("❌ Database setup timed out. Please try again.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error setting up database: {str(e)}")
            st.exception(e)
            st.stop()

    return True

# Setup database on first run
setup_database_if_needed()

# Import data loaders
from data_processing.sqlite_loader import OneleadSQLiteLoader
from data_processing.enhanced_recommendation_engine import EnhancedRecommendationEngine

# Page configuration
st.set_page_config(
    page_title="HPE OneLead - Data Flow",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }

    .step-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .step-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .step-desc {
        font-size: 1rem;
        opacity: 0.9;
    }

    .data-box {
        background: white;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }

    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    .arrow {
        text-align: center;
        font-size: 2rem;
        color: #667eea;
        margin: 1rem 0;
    }

    div[data-testid="metric-container"] {
        background: white;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
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

def get_db_stats():
    """Get database statistics"""
    conn = sqlite3.connect('data/onelead.db')

    stats = {}

    # LS_SKU data
    stats['ls_products'] = conn.execute("SELECT COUNT(*) FROM dim_ls_sku_product").fetchone()[0]
    stats['ls_services'] = conn.execute("SELECT COUNT(*) FROM dim_ls_sku_service").fetchone()[0]
    stats['sku_codes'] = conn.execute("SELECT COUNT(*) FROM dim_sku_code").fetchone()[0]
    stats['product_service_mappings'] = conn.execute("SELECT COUNT(*) FROM map_product_service_sku").fetchone()[0]

    # Install Base data
    stats['install_base_products'] = conn.execute("SELECT COUNT(*) FROM fact_install_base").fetchone()[0]
    stats['customers'] = conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0]

    # Product matching
    stats['matched_products'] = conn.execute("SELECT COUNT(*) FROM map_install_base_to_ls_sku").fetchone()[0]

    conn.close()
    return stats

def show_step_1_source_data():
    """Step 1: Show source Excel files"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">📥 Step 1: Source Data (Excel Files)</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Two Excel files provide the foundation data</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 DataExportAug29th.xlsx")
        st.markdown("**Customer & Install Base Data**")

        try:
            # Load Install Base sheet
            df_ib = pd.read_excel('data/DataExportAug29th.xlsx', sheet_name='Install Base')

            st.metric("Total Products", len(df_ib))
            st.metric("Unique Product Models", df_ib['Product_Name'].nunique())
            st.metric("Customer Accounts", df_ib['Account_Sales_Territory_Id'].nunique())

            with st.expander("📋 View Sample Install Base Data"):
                st.dataframe(
                    df_ib[['Account_Sales_Territory_Id', 'Product_Name', 'Product_Platform_Description_Name', 'Support_Status']].head(10),
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Error loading Install Base: {str(e)}")

    with col2:
        st.markdown("### 📋 LS_SKU_for_Onelead.xlsx")
        st.markdown("**HPE Service Catalog**")

        try:
            # Load LS_SKU sheet
            df_sku = pd.read_excel('data/LS_SKU_for_Onelead.xlsx', sheet_name='Sheet2', header=4)

            products = df_sku['Product'].dropna().nunique()
            services = df_sku['Services Offered'].dropna().nunique()

            st.metric("HPE Product Categories", products)
            st.metric("Available Services", services)
            st.metric("Service Catalog Rows", len(df_sku))

            with st.expander("📋 View Sample LS_SKU Catalog"):
                st.dataframe(
                    df_sku[['Product', 'Services Offered']].dropna().head(10),
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Error loading LS_SKU: {str(e)}")

def show_step_2_database():
    """Step 2: Show database transformation"""
    st.markdown('<div class="arrow">⬇️</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🗄️ Step 2: Database Transformation (SQLite)</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Excel data is parsed and loaded into structured SQLite tables</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    stats = get_db_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📦 LS_SKU Tables")
        st.metric("Product Categories", stats['ls_products'])
        st.metric("Services", stats['ls_services'])
        st.metric("SKU Codes", stats['sku_codes'])
        st.metric("Product→Service Maps", stats['product_service_mappings'])

    with col2:
        st.markdown("### 🏢 Customer Tables")
        st.metric("Customers", stats['customers'])
        st.metric("Install Base Products", stats['install_base_products'])
        st.metric("Product Matches", stats['matched_products'])

    with col3:
        st.markdown("### 📊 Database Health")

        conn = sqlite3.connect('data/onelead.db')
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        conn.close()

        st.metric("Total Tables", len(tables))
        st.metric("Database Size", f"{Path('data/onelead.db').stat().st_size / 1024 / 1024:.1f} MB")

        with st.expander("📋 View All Tables"):
            for table in tables:
                st.text(f"• {table[0]}")

def show_step_3_matching():
    """Step 3: Show product matching"""
    st.markdown('<div class="arrow">⬇️</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🔗 Step 3: Product Matching Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Install Base products are matched to LS_SKU categories using keyword matching</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    conn = sqlite3.connect('data/onelead.db')

    # Show matching details
    query = """
    SELECT
        p.product_description as install_base_product,
        ls.product_name as ls_sku_category,
        m.confidence_score,
        m.match_method
    FROM dim_product p
    JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
    JOIN dim_ls_sku_product ls ON m.ls_product_key = ls.ls_product_key
    ORDER BY m.confidence_score DESC
    """

    df_matches = pd.read_sql_query(query, conn)
    conn.close()

    if not df_matches.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Product Matching Results")
            st.dataframe(
                df_matches,
                use_container_width=True,
                hide_index=True,
                height=400
            )

        with col2:
            st.markdown("### 📊 Match Quality")

            avg_confidence = df_matches['confidence_score'].mean()
            st.metric("Average Confidence", f"{avg_confidence:.0f}%")
            st.metric("Total Matches", len(df_matches))

            # Confidence distribution
            fig = px.histogram(
                df_matches,
                x='confidence_score',
                title='Confidence Score Distribution',
                labels={'confidence_score': 'Confidence Score', 'count': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No product matches found. Please ensure data is loaded.")

def show_step_4_recommendations():
    """Step 4: Show recommendation generation"""
    st.markdown('<div class="arrow">⬇️</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🎯 Step 4: Recommendation Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Services are recommended based on matched products, with urgency and SKU codes</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    engine = get_recommendation_engine()

    # Generate all recommendations
    recs = engine.generate_quote_ready_export()

    # Rename columns to match expected format
    if not recs.empty:
        if 'match_confidence' in recs.columns:
            recs['confidence'] = recs['match_confidence']
        if 'current_product' in recs.columns:
            recs['product_name'] = recs['current_product']

    if not recs.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(recs)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Recommendations</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            has_sku = (recs['sku_codes'].notna() & (recs['sku_codes'] != '')).sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{has_sku}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">With SKU Codes</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            customers = recs['customer_name'].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{customers}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Customers</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            avg_conf = int(recs['confidence'].mean()) if 'confidence' in recs.columns else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_conf}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Avg Confidence</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Show recommendation breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Recommendations by Priority")
            if 'urgency' in recs.columns:
                urgency_counts = recs['urgency'].value_counts()
                fig = px.pie(
                    values=urgency_counts.values,
                    names=urgency_counts.index,
                    title='Priority Distribution',
                    color_discrete_map={
                        'Critical': '#ff4b4b',
                        'High': '#ffa500',
                        'Medium': '#ffeb3b',
                        'Low': '#4caf50'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 👥 Top Customers")
            if 'customer_name' in recs.columns:
                customer_counts = recs['customer_name'].value_counts().head(5)
                fig = px.bar(
                    x=customer_counts.values,
                    y=customer_counts.index,
                    orientation='h',
                    title='Recommendations per Customer',
                    labels={'x': 'Recommendations', 'y': 'Customer'}
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No recommendations generated. Please check data.")

def show_step_5_dashboard():
    """Step 5: Interactive dashboard with filters"""
    st.markdown('<div class="arrow">⬇️</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">📱 Step 5: Interactive Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Filter and explore recommendations with interactive controls</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Filters
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Customer filter
        engine = get_recommendation_engine()
        data = load_database_data()
        customers = data.get('customers', pd.DataFrame())

        if not customers.empty and 'customer_name' in customers.columns:
            customer_list = ['All Customers'] + sorted(customers['customer_name'].unique().tolist())
        else:
            customer_list = ['All Customers']

        selected_customer = st.selectbox("Select Customer", options=customer_list)

    with col2:
        # Urgency filter
        urgency_options = st.multiselect(
            "Urgency Level",
            options=['Critical', 'High', 'Medium', 'Low'],
            default=['Critical', 'High']
        )

    with col3:
        # Confidence filter
        min_confidence = st.slider("Minimum Confidence", 50, 100, 60, 5)

    # Generate filtered recommendations
    customer_id = None if selected_customer == 'All Customers' else selected_customer
    recs = engine.generate_quote_ready_export(
        customer_id=customer_id,
        urgency_filter=urgency_options if urgency_options else None
    )

    # Rename columns
    if not recs.empty:
        if 'match_confidence' in recs.columns:
            recs['confidence'] = recs['match_confidence']
        if 'current_product' in recs.columns:
            recs['product_name'] = recs['current_product']

        # Apply confidence filter
        if 'confidence' in recs.columns:
            recs = recs[recs['confidence'] >= min_confidence]

    if not recs.empty:
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total Recommendations", len(recs))
        with col2:
            has_sku = (recs['sku_codes'].notna() & (recs['sku_codes'] != '')).sum()
            st.metric("✅ With SKU Codes", has_sku)
        with col3:
            quote_ready_pct = (has_sku / len(recs) * 100) if len(recs) > 0 else 0
            st.metric("📊 Quote-Ready %", f"{quote_ready_pct:.0f}%")

        st.markdown("---")

        # Prepare display data
        display_df = recs.copy()

        display_cols = ['customer_name', 'product_name', 'service_name', 'sku_codes', 'urgency', 'confidence']
        display_cols = [col for col in display_cols if col in display_df.columns]
        display_df = display_df[display_cols]

        # Format data
        if 'confidence' in display_df.columns:
            display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "N/A")

        if 'sku_codes' in display_df.columns:
            display_df['sku_codes'] = display_df['sku_codes'].fillna('📞 Contact HPE')
            display_df['sku_codes'] = display_df['sku_codes'].replace('', '📞 Contact HPE')

        # Rename columns
        column_mapping = {
            'customer_name': 'Customer',
            'product_name': 'Product',
            'service_name': 'Service Name',
            'sku_codes': 'SKU Code',
            'urgency': 'Priority',
            'confidence': 'Confidence'
        }
        display_df = display_df.rename(columns=column_mapping)

        # Add urgency emoji
        if 'Priority' in display_df.columns:
            display_df['Priority'] = display_df['Priority'].apply(lambda x:
                f"🔴 {x}" if x == 'Critical' else
                f"🟠 {x}" if x == 'High' else
                f"🟡 {x}" if x == 'Medium' else
                f"🟢 {x}" if x == 'Low' else x
            )

        # Show recommendations as expandable cards
        st.markdown(f"### 📋 Detailed Recommendations")

        # Group by customer
        if 'Customer' in display_df.columns:
            for customer in display_df['Customer'].unique():
                customer_recs = display_df[display_df['Customer'] == customer]

                # Get original data for this customer to add reasoning
                orig_customer_recs = recs[recs['customer_name'] == customer].copy()

                with st.expander(f"👤 {customer} ({len(customer_recs)} recommendations)", expanded=True):
                    # Show each recommendation with explanation
                    for idx, (_, rec) in enumerate(customer_recs.iterrows(), 1):
                        # Get original data for reasoning
                        orig_rec = orig_customer_recs.iloc[idx-1] if idx <= len(orig_customer_recs) else None

                        # Create a card for each recommendation
                        st.markdown(f"**{idx}. {rec['Service Name']}**")

                        col1, col2 = st.columns([3, 1])

                        with col1:
                            # Recommendation details
                            st.markdown(f"""
                            - **Product**: {rec['Product']}
                            - **SKU Code**: {rec['SKU Code']}
                            - **Priority**: {rec['Priority']}
                            - **Confidence**: {rec['Confidence']}
                            """)

                            # Build reasoning
                            reasons = []

                            # Product-based reasoning
                            if orig_rec is not None:
                                if 'product_platform' in orig_rec:
                                    platform = orig_rec['product_platform']
                                    if pd.notna(platform):
                                        reasons.append(f"Product is in **{platform}** category")

                                # Urgency reasoning
                                urgency = rec['Priority'].split(' ')[-1]  # Remove emoji
                                if urgency == 'Critical':
                                    if 'support_status' in orig_rec and orig_rec['support_status'] == 'Expired':
                                        reasons.append("⚠️ **Support has expired** - service renewal needed immediately")
                                    elif 'days_to_eol' in orig_rec and pd.notna(orig_rec['days_to_eol']):
                                        days = orig_rec['days_to_eol']
                                        if days < 90:
                                            reasons.append(f"⚠️ **Product EOL in {days} days** - urgent service required")
                                elif urgency == 'High':
                                    if 'days_to_eol' in orig_rec and pd.notna(orig_rec['days_to_eol']):
                                        days = orig_rec['days_to_eol']
                                        if days < 180:
                                            reasons.append(f"⏰ **Product EOL in {days} days** - service recommended soon")
                                elif urgency == 'Low':
                                    reasons.append("✅ Product is healthy - proactive maintenance recommended")

                                # Match confidence reasoning
                                if 'match_confidence' in orig_rec:
                                    conf = orig_rec['match_confidence']
                                    if conf == 100:
                                        reasons.append("🎯 **Exact product match** - highly relevant service")
                                    elif conf >= 85:
                                        reasons.append("✅ **Strong product match** - recommended by matching algorithm")
                                    elif conf >= 70:
                                        reasons.append("📊 **Category match** - service fits product type")

                                # Service type reasoning
                                service_name = rec['Service Name'].lower()
                                if 'health check' in service_name:
                                    reasons.append("🏥 Validates system health and identifies issues")
                                elif 'upgrade' in service_name or 'firmware' in service_name:
                                    reasons.append("⬆️ Keeps system up-to-date with latest features and security")
                                elif 'install' in service_name or 'startup' in service_name:
                                    reasons.append("🚀 Ensures proper setup and configuration")
                                elif 'optimization' in service_name:
                                    reasons.append("⚡ Improves performance and efficiency")
                                elif 'migration' in service_name:
                                    reasons.append("🔄 Facilitates smooth transition to new systems")

                        with col2:
                            # Show reasoning box
                            if reasons:
                                st.info("**Why Recommended:**\n\n" + "\n\n".join(f"• {r}" for r in reasons))
                            else:
                                st.info("**Why Recommended:**\n\nStandard service for this product type")

                        st.markdown("---")
        else:
            # Fallback: show all as one table
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600,
                hide_index=True
            )

        # Download section (collapsible)
        st.markdown("---")
        with st.expander("📥 Download Options"):
            col1, col2 = st.columns(2)

            with col1:
                csv = recs.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Recommendations",
                    data=csv,
                    file_name=f"hpe_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                if 'sku_codes' in recs.columns:
                    quote_ready = recs[recs['sku_codes'].notna() & (recs['sku_codes'] != '')]
                    if not quote_ready.empty:
                        csv_ready = quote_ready.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Quote-Ready Only",
                            data=csv_ready,
                            file_name=f"quote_ready_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
    else:
        st.warning("📭 No recommendations match your filters")
        st.info("💡 **Tip**: Try adjusting urgency levels or lowering minimum confidence")

def main():
    # Header
    st.title("🎯 HPE OneLead - Service Recommendation System")
    st.markdown("**Step-by-Step Data Flow: Excel → Database → Recommendations → Dashboard**")
    st.markdown("---")

    # Navigation
    view_mode = st.radio(
        "Choose View",
        options=["📊 Complete Flow", "🎯 Recommendations Only"],
        horizontal=True
    )

    if view_mode == "📊 Complete Flow":
        # Show all steps
        show_step_1_source_data()
        show_step_2_database()
        show_step_3_matching()
        show_step_4_recommendations()
        show_step_5_dashboard()

    else:
        # Show only recommendations dashboard
        show_step_5_dashboard()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🎯 HPE OneLead System")

    with col2:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    with col3:
        conn = sqlite3.connect('data/onelead.db')
        cursor = conn.execute("SELECT COUNT(*) FROM dim_ls_sku_service")
        service_count = cursor.fetchone()[0]
        conn.close()
        st.caption(f"📦 {service_count} services available")

if __name__ == "__main__":
    main()