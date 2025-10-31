"""
OneLead - Modern Lead Intelligence Platform
Built on ACTUAL data only - no estimates or projections
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.base import SessionLocal
from src.models import Lead, Account, InstallBase, Project
from sqlalchemy import func, and_, desc

# Page configuration
st.set_page_config(
    page_title="OneLead - Lead Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #01A982;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .lead-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .priority-critical {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-high {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-medium {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-low {
        background: #e0e0e0;
        color: #666;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .data-badge {
        background: #f0f0f0;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        margin: 0.25rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .section-divider {
        border-top: 2px solid #01A982;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_session():
    """Get database session."""
    return SessionLocal()


@st.cache_data(ttl=300)
def load_leads_data():
    """Load all leads with related data."""
    session = get_session()

    leads = session.query(Lead).filter(Lead.is_active == True).all()

    data = []
    for lead in leads:
        data.append({
            'id': lead.id,
            'title': lead.title,
            'lead_type': lead.lead_type,
            'priority': lead.priority,
            'score': lead.score,
            'urgency_score': lead.urgency_score,
            'value_score': lead.value_score,
            'propensity_score': lead.propensity_score,
            'strategic_fit_score': lead.strategic_fit_score,
            'description': lead.description,
            'recommended_action': lead.recommended_action,
            'project_size_category': lead.project_size_category,
            'install_base_count': lead.install_base_count,
            'historical_project_count': lead.historical_project_count,
            'active_credits_available': lead.active_credits_available,
            'account_id': lead.account_id,
            'install_base_id': lead.install_base_id,
            'generated_at': lead.generated_at,
            'lead_status': lead.lead_status
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_summary_stats():
    """Load summary statistics."""
    session = get_session()

    stats = {
        'total_leads': session.query(func.count(Lead.id)).filter(Lead.is_active == True).scalar(),
        'critical_leads': session.query(func.count(Lead.id)).filter(
            and_(Lead.is_active == True, Lead.priority == 'CRITICAL')
        ).scalar(),
        'high_leads': session.query(func.count(Lead.id)).filter(
            and_(Lead.is_active == True, Lead.priority == 'HIGH')
        ).scalar(),
        'total_accounts': session.query(func.count(func.distinct(Lead.account_id))).filter(
            Lead.is_active == True
        ).scalar(),
        'total_install_base': session.query(func.count(InstallBase.id)).scalar(),
        'total_projects': session.query(func.count(Project.id)).scalar(),
        'avg_score': session.query(func.avg(Lead.score)).filter(Lead.is_active == True).scalar() or 0,
    }

    # Lead type breakdown
    lead_types = session.query(
        Lead.lead_type,
        func.count(Lead.id).label('count')
    ).filter(Lead.is_active == True).group_by(Lead.lead_type).all()

    stats['lead_types'] = {lt[0]: lt[1] for lt in lead_types}

    return stats


def render_header():
    """Render application header."""
    st.markdown('<div class="main-header">🎯 OneLead</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Lead Intelligence Platform - Built on Actual Data Only</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")


def render_metrics_overview(stats):
    """Render key metrics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Active Leads",
            f"{stats['total_leads']}",
            help="Total number of active leads in the system"
        )

    with col2:
        st.metric(
            "Critical Priority",
            f"{stats['critical_leads']}",
            help="Leads requiring immediate attention"
        )

    with col3:
        st.metric(
            "High Priority",
            f"{stats['high_leads']}",
            help="Important leads for follow-up"
        )

    with col4:
        st.metric(
            "Avg. Lead Score",
            f"{stats['avg_score']:.1f}",
            help="Average score across all active leads"
        )


def render_data_overview(stats):
    """Render data availability overview."""
    st.markdown("### 📊 Data Foundation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="data-badge">
            <strong>{stats['total_accounts']}</strong> Active Accounts
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="data-badge">
            <strong>{stats['total_install_base']}</strong> Install Base Items
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="data-badge">
            <strong>{stats['total_projects']}</strong> Historical Projects
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_lead_type_distribution(stats):
    """Render lead type distribution chart."""
    if not stats['lead_types']:
        return

    st.markdown("### 📈 Lead Distribution by Type")

    df_types = pd.DataFrame([
        {'Lead Type': k, 'Count': v}
        for k, v in stats['lead_types'].items()
    ])

    fig = px.bar(
        df_types,
        x='Lead Type',
        y='Count',
        color='Count',
        color_continuous_scale='Viridis',
        title="Lead Types"
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="Number of Leads"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_score_distribution(df_leads):
    """Render score distribution chart."""
    st.markdown("### 🎯 Lead Score Distribution")

    fig = px.histogram(
        df_leads,
        x='score',
        nbins=20,
        title="Distribution of Lead Scores",
        color_discrete_sequence=['#01A982']
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Lead Score",
        yaxis_title="Number of Leads"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_score_breakdown(df_leads):
    """Render score component breakdown."""
    st.markdown("### 📊 Score Component Analysis")

    avg_scores = {
        'Urgency': df_leads['urgency_score'].mean(),
        'Value': df_leads['value_score'].mean(),
        'Propensity': df_leads['propensity_score'].mean(),
        'Strategic Fit': df_leads['strategic_fit_score'].mean()
    }

    df_components = pd.DataFrame([
        {'Component': k, 'Average Score': v}
        for k, v in avg_scores.items()
    ])

    fig = px.bar(
        df_components,
        x='Component',
        y='Average Score',
        color='Average Score',
        color_continuous_scale='Blues',
        title="Average Scores by Component"
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="Average Score (0-100)"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_priority_filter(df_leads):
    """Render priority filter sidebar."""
    st.sidebar.markdown("### 🎯 Filters")

    # Priority filter
    priorities = ['All'] + sorted(df_leads['priority'].unique().tolist())
    selected_priority = st.sidebar.selectbox("Priority", priorities)

    # Lead type filter
    lead_types = ['All'] + sorted(df_leads['lead_type'].unique().tolist())
    selected_type = st.sidebar.selectbox("Lead Type", lead_types)

    # Score range filter
    min_score = float(df_leads['score'].min())
    max_score = float(df_leads['score'].max())
    score_range = st.sidebar.slider(
        "Score Range",
        min_score,
        max_score,
        (min_score, max_score)
    )

    # Apply filters
    filtered_df = df_leads.copy()

    if selected_priority != 'All':
        filtered_df = filtered_df[filtered_df['priority'] == selected_priority]

    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['lead_type'] == selected_type]

    filtered_df = filtered_df[
        (filtered_df['score'] >= score_range[0]) &
        (filtered_df['score'] <= score_range[1])
    ]

    return filtered_df


def get_priority_badge(priority):
    """Get HTML badge for priority."""
    badges = {
        'CRITICAL': '<span class="priority-critical">CRITICAL</span>',
        'HIGH': '<span class="priority-high">HIGH</span>',
        'MEDIUM': '<span class="priority-medium">MEDIUM</span>',
        'LOW': '<span class="priority-low">LOW</span>'
    }
    return badges.get(priority, '<span class="priority-low">-</span>')


def render_lead_card(lead):
    """Render a single lead card."""
    priority_badge = get_priority_badge(lead['priority'])

    st.markdown(f"""
    <div class="lead-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; color: #333;">{lead['title']}</h4>
            {priority_badge}
        </div>
        <div style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
            <strong>{lead['lead_type']}</strong> | Score: <strong>{lead['score']:.1f}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Actual data metrics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 Actual Data Metrics**")

        if lead['install_base_count']:
            st.write(f"• Install Base: **{lead['install_base_count']} assets**")

        if lead['project_size_category']:
            st.write(f"• Project Size: **{lead['project_size_category']}**")

        if lead['historical_project_count']:
            st.write(f"• Past Projects: **{lead['historical_project_count']}**")

        if lead['active_credits_available']:
            st.write(f"• Service Credits: **{lead['active_credits_available']}**")

        if not any([lead['install_base_count'], lead['project_size_category'],
                    lead['historical_project_count'], lead['active_credits_available']]):
            st.write("_No historical data available_")

    with col2:
        st.markdown("**🎯 Score Breakdown**")
        st.write(f"• Urgency: **{lead['urgency_score']:.1f}**")
        st.write(f"• Value: **{lead['value_score']:.1f}**")
        st.write(f"• Propensity: **{lead['propensity_score']:.1f}**")
        st.write(f"• Strategic Fit: **{lead['strategic_fit_score']:.1f}**")

    # Description and action
    with st.expander("📝 Details & Recommended Action"):
        st.markdown(f"**Situation:**\n{lead['description']}")
        st.markdown(f"**Recommended Action:**\n{lead['recommended_action']}")

    st.markdown("---")


def render_leads_list(df_leads):
    """Render list of leads."""
    st.markdown("### 📋 Lead Details")

    if len(df_leads) == 0:
        st.info("No leads match the selected filters.")
        return

    # Sort by score
    df_leads = df_leads.sort_values('score', ascending=False)

    # Display count
    st.markdown(f"**Showing {len(df_leads)} leads**")

    # Render each lead
    for idx, lead in df_leads.iterrows():
        render_lead_card(lead)


def render_insights_tab():
    """Render insights tab with latest findings."""
    st.markdown("### 💡 Recent Findings & Enhancements")

    st.markdown("""
    Recent analysis has uncovered powerful data relationships that enhance lead intelligence and service recommendations.
    """)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Data Coverage Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Accounts", "10", help="Customer accounts with complete data")

    with col2:
        st.metric("Install Base", "63", help="Hardware assets tracked")

    with col3:
        st.metric("Opportunities", "98", help="Active sales opportunities")

    with col4:
        st.metric("Projects", "2,394", help="Historical A&PS projects")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Key Findings
    st.markdown("### 🔍 Key Discoveries")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **1. Complete Project Coverage (100%)**

        All 2,394 historical projects now linked to accounts via ST ID, providing complete customer history for better recommendations.

        **2. Product Line Mapping**

        Product Line field connects Install Base → LS_SKU → Services → Practice, enabling intelligent service recommendations.
        """)

    with col2:
        st.markdown("""
        **3. Services Integration (80.4%)**

        230 of 286 services mapped between LS_SKU and Services catalog, with 37 SKU codes for quoting.

        **4. Practice Intelligence**

        Historical practice distribution enables confidence scoring based on past delivery patterns.
        """)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Documentation
    st.markdown("### 📚 Documentation")

    st.markdown("""
    Detailed findings documented in:
    - ST_ID_DISCOVERY_SUMMARY.md
    - PRODUCT_LINE_COMPLETE_MAPPING.md
    - SERVICES_LSSKU_MAPPING.md
    - PROJECT_COLUMNS_MAPPING.md
    - FUZZY_LOGIC_USAGE.md
    - DATA_RELATIONSHIPS_ANALYSIS.md
    """)


def main():
    """Main application."""
    # Render header
    render_header()

    # Load data
    with st.spinner("Loading data..."):
        stats = load_summary_stats()
        df_leads = load_leads_data()

    # Sidebar filters
    filtered_df = render_priority_filter(df_leads)

    # Main content
    render_metrics_overview(stats)
    st.markdown("")

    render_data_overview(stats)

    # Analytics section
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "📈 Analytics",
        "📋 Lead List",
        "💡 Insights",
        "ℹ️ About"
    ])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            render_lead_type_distribution(stats)

        with col2:
            render_score_distribution(filtered_df)

    with tab2:
        render_score_breakdown(filtered_df)

        st.markdown("### 📊 Actual Data Coverage")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            coverage_ib = (filtered_df['install_base_count'].notna().sum() / len(filtered_df) * 100)
            st.metric("Install Base Data", f"{coverage_ib:.0f}%")

        with col2:
            coverage_ps = (filtered_df['project_size_category'].notna().sum() / len(filtered_df) * 100)
            st.metric("Project Size Data", f"{coverage_ps:.0f}%")

        with col3:
            coverage_pc = (filtered_df['historical_project_count'].notna().sum() / len(filtered_df) * 100)
            st.metric("Project History Data", f"{coverage_pc:.0f}%")

        with col4:
            coverage_cr = (filtered_df['active_credits_available'].notna().sum() / len(filtered_df) * 100)
            st.metric("Credits Data", f"{coverage_cr:.0f}%")

    with tab3:
        render_leads_list(filtered_df)

    with tab4:
        render_insights_tab()

    with tab5:
        st.markdown("### ℹ️ About OneLead")

        st.markdown("""
        **OneLead** is a lead intelligence platform built entirely on **actual data** from your systems:

        - ✅ **No Estimates**: All metrics are derived from actual Excel data
        - ✅ **Transparent Scoring**: Clear breakdown of urgency, value, propensity, and strategic fit
        - ✅ **Data-Driven**: Based on real install base, projects, and engagement history

        ---

        **Data Sources:**
        - Install Base (63 items)
        - Opportunities (98 items)
        - A&PS Projects (2,394 historical projects)
        - Service Credits tracking

        **Scoring Methodology:**
        - **Urgency** (40%): Based on actual EOL dates, warranty expiry
        - **Value** (30%): Based on historical project sizes, install base count
        - **Propensity** (20%): Based on past engagement and project history
        - **Strategic Fit** (10%): Based on product family and business area

        ---

        **Key Principle**: *If the data isn't in the system, we don't generate it.*
        """)

        st.info("💡 **Tip**: Use the filters in the sidebar to focus on specific priorities or lead types.")


if __name__ == "__main__":
    main()
