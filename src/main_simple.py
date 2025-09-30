"""
HPE OneLead - Simple, Business-Focused Dashboard
Clear and actionable service recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# Import data loaders
from data_processing.sqlite_loader import OneleadSQLiteLoader
from data_processing.enhanced_recommendation_engine import EnhancedRecommendationEngine

# Page configuration
st.set_page_config(
    page_title="HPE OneLead - Service Recommendations",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }

    .big-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #01A982;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    div[data-testid="metric-container"] {
        background: white;
        border: 2px solid #e0e0e0;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .stButton button {
        background-color: #01A982;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1rem;
    }

    .stButton button:hover {
        background-color: #018f6e;
        transform: translateY(-1px);
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

def main():
    # Sidebar for filters
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/01A982/FFFFFF?text=HPE+OneLead", use_container_width=True)
        st.markdown("---")

        st.header("Filter Options")

        # Customer filter
        engine = get_recommendation_engine()
        data = load_database_data()

        customers = data.get('customers', pd.DataFrame())
        if not customers.empty and 'customer_name' in customers.columns:
            customer_list = ['All Customers'] + sorted(customers['customer_name'].unique().tolist())
        else:
            customer_list = ['All Customers']

        selected_customer = st.selectbox(
            "Select Customer",
            options=customer_list,
            help="Choose a specific customer or view all"
        )

        # Urgency filter
        st.markdown("**Urgency Level**")
        show_critical = st.checkbox("Critical", value=True, help="Expired or urgent items")
        show_high = st.checkbox("High", value=True, help="Needs attention soon")
        show_medium = st.checkbox("Medium", value=False, help="Plan ahead")
        show_low = st.checkbox("Low", value=False, help="Future consideration")

        urgency_filter = []
        if show_critical:
            urgency_filter.append('Critical')
        if show_high:
            urgency_filter.append('High')
        if show_medium:
            urgency_filter.append('Medium')
        if show_low:
            urgency_filter.append('Low')

        # Confidence filter
        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=50,
            max_value=100,
            value=60,
            step=5,
            help="Only show recommendations we're confident about"
        )

        st.markdown("---")
        st.markdown("### About")
        st.info("This dashboard shows AI-powered service recommendations with SKU codes to help you create quotes faster.")

    # Main content
    st.markdown('<div class="big-title">🎯 Service Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Find the right HPE services for your customers</div>', unsafe_allow_html=True)

    # Get recommendations based on filters
    try:
        customer_id = None if selected_customer == 'All Customers' else selected_customer
        recs = engine.generate_quote_ready_export(
            customer_id=customer_id,
            urgency_filter=urgency_filter if urgency_filter else None
        )

        # Apply confidence filter
        if not recs.empty and 'confidence' in recs.columns:
            recs = recs[recs['confidence'] >= min_confidence]

        if not recs.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📋 Recommendations", len(recs))

            with col2:
                has_sku = (recs['sku_codes'].notna() & (recs['sku_codes'] != '')).sum() if 'sku_codes' in recs.columns else 0
                st.metric("✅ With SKU Code", has_sku)

            with col3:
                customers_count = recs['customer_name'].nunique() if 'customer_name' in recs.columns else 0
                st.metric("👥 Customers", customers_count)

            with col4:
                avg_conf = int(recs['confidence'].mean()) if 'confidence' in recs.columns else 0
                st.metric("📊 Avg Confidence", f"{avg_conf}%")

            st.markdown("---")

            # Main table
            st.subheader("📋 Recommendations")

            # Prepare display data
            display_df = recs.copy()

            # Select and rename columns
            column_mapping = {
                'customer_name': 'Customer',
                'product_name': 'Product',
                'service_name': 'Service Name',
                'sku_codes': 'SKU Code',
                'urgency': 'Priority',
                'confidence': 'Confidence'
            }

            display_cols = [col for col in column_mapping.keys() if col in display_df.columns]
            display_df = display_df[display_cols]

            # Format data
            if 'confidence' in display_df.columns:
                display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "N/A")

            if 'sku_codes' in display_df.columns:
                display_df['sku_codes'] = display_df['sku_codes'].fillna('📞 Contact HPE')
                display_df['sku_codes'] = display_df['sku_codes'].replace('', '📞 Contact HPE')

            # Rename columns
            display_df = display_df.rename(columns=column_mapping)

            # Add urgency emoji
            if 'Priority' in display_df.columns:
                display_df['Priority'] = display_df['Priority'].apply(lambda x:
                    f"🔴 {x}" if x == 'Critical' else
                    f"🟠 {x}" if x == 'High' else
                    f"🟡 {x}" if x == 'Medium' else
                    f"🟢 {x}" if x == 'Low' else x
                )

            # Show table
            st.dataframe(
                display_df,
                use_container_width=True,
                height=500,
                hide_index=True
            )

            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                csv = recs.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Recommendations",
                    data=csv,
                    file_name=f"hpe_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            with col2:
                # Quote-ready only (has SKU code)
                if 'sku_codes' in recs.columns:
                    quote_ready = recs[recs['sku_codes'].notna() & (recs['sku_codes'] != '')]
                    if not quote_ready.empty:
                        csv_ready = quote_ready.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Quote-Ready Only",
                            data=csv_ready,
                            file_name=f"quote_ready_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

            # Quick insights
            st.markdown("---")
            st.subheader("💡 Quick Insights")

            col1, col2 = st.columns(2)

            with col1:
                if 'urgency' in recs.columns:
                    st.markdown("**Recommendations by Priority**")
                    urgency_counts = recs['urgency'].value_counts()

                    for urgency, count in urgency_counts.items():
                        emoji = "🔴" if urgency == "Critical" else "🟠" if urgency == "High" else "🟡" if urgency == "Medium" else "🟢"
                        st.markdown(f"{emoji} **{urgency}**: {count} recommendations")

            with col2:
                if 'customer_name' in recs.columns:
                    st.markdown("**Top Customers**")
                    customer_counts = recs['customer_name'].value_counts().head(5)

                    for customer, count in customer_counts.items():
                        st.markdown(f"👤 **{customer}**: {count} recommendations")

        else:
            st.warning("📭 No recommendations match your current filters.")
            st.info("💡 **Tip**: Try selecting different urgency levels or lowering the minimum confidence.")

            # Show what filters are active
            st.markdown("### Current Filters:")
            st.markdown(f"- **Customer**: {selected_customer}")
            st.markdown(f"- **Urgency**: {', '.join(urgency_filter) if urgency_filter else 'None selected'}")
            st.markdown(f"- **Minimum Confidence**: {min_confidence}%")

    except Exception as e:
        st.error("⚠️ Unable to load recommendations")
        st.error(f"Error: {str(e)}")

        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            1. Database might not be loaded - Run: `python src/database/create_sqlite_database.py`
            2. LS_SKU data might be missing - Run: `python src/database/ls_sku_data_loader.py`
            3. No Install Base data loaded

            **Need help?** Check the documentation in the `docs/` folder.
            """)

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🎯 HPE OneLead Service Recommendations")

    with col2:
        st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    with col3:
        conn = sqlite3.connect('data/onelead.db')
        cursor = conn.execute("SELECT COUNT(*) FROM dim_ls_sku_service")
        service_count = cursor.fetchone()[0]
        conn.close()
        st.caption(f"📦 {service_count} services in catalog")

if __name__ == "__main__":
    main()