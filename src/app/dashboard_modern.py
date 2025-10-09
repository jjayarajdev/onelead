"""OneLead Modern Dashboard - Inspired by best-in-class data apps."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func, case
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import SessionLocal, Lead, InstallBase, Account, Opportunity, Project

# Page configuration
st.set_page_config(
    page_title="OneLead - Sales Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS with animations and gradients
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main container */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        animation: fadeIn 0.8s ease-in;
    }

    .hero h1 {
        font-size: 48px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }

    .hero p {
        font-size: 20px;
        opacity: 0.9;
        margin-top: 10px;
    }

    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }

    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }

    .stat-value {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 14px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .stat-change {
        font-size: 14px;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .stat-change.positive {
        color: #10b981;
    }

    .stat-change.negative {
        color: #ef4444;
    }

    /* Priority Badge */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    .badge-high {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .badge-medium {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    }

    .badge-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* Lead Card */
    .lead-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .lead-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateX(4px);
    }

    .lead-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .lead-card-critical {
        border-left-color: #ef4444;
    }

    .lead-card-high {
        border-left-color: #f59e0b;
    }

    .lead-title {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    .lead-meta {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        font-size: 14px;
        color: #6b7280;
        margin: 12px 0;
    }

    .lead-meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Section Header */
    .section-header {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin: 40px 0 20px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .section-header::before {
        content: '';
        width: 4px;
        height: 28px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }

    /* Filter Bar */
    .filter-bar {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        margin: 24px 0;
    }

    /* Action Button */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Chart Container */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        margin: 20px 0;
    }

    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Progress Bar */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin: 12px 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
        transition: width 0.6s ease;
    }

    /* Score Circle */
    .score-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #9ca3af;
    }

    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 16px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3d8c 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
@st.cache_resource
def get_session():
    return SessionLocal()

session = get_session()

# Get territory mapping
@st.cache_data
def get_territory_mapping():
    mapping = {}
    accounts_with_names = session.query(Account).filter(
        Account.account_name != Account.territory_id
    ).all()
    for acc in accounts_with_names:
        if acc.territory_id and acc.territory_id not in mapping:
            mapping[acc.territory_id] = acc.account_name
    return mapping

def format_account(account):
    if not account:
        return "Unknown"
    if account.account_name and account.account_name.isdigit():
        territory_map = get_territory_mapping()
        if account.account_name in territory_map:
            return territory_map[account.account_name]
        else:
            return f"Territory {account.account_name}"
    else:
        return account.account_name

# Fetch data
total_leads = session.query(func.count(Lead.id)).filter(Lead.is_active == True).scalar()
critical_leads = session.query(func.count(Lead.id)).filter(
    Lead.is_active == True, Lead.priority == 'CRITICAL'
).scalar()
high_leads = session.query(func.count(Lead.id)).filter(
    Lead.is_active == True, Lead.priority == 'HIGH'
).scalar()
total_pipeline = session.query(func.sum(Lead.estimated_value_max)).filter(
    Lead.is_active == True
).scalar() or 0
avg_score = session.query(func.avg(Lead.score)).filter(Lead.is_active == True).scalar() or 0

# Hero Section
st.markdown("""
<div class="hero">
    <h1>🎯 Sales Intelligence Dashboard</h1>
    <p>Your AI-powered revenue acceleration platform</p>
</div>
""", unsafe_allow_html=True)

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Pipeline Value</div>
        <div class="stat-value">${total_pipeline/1e6:.1f}M</div>
        <div class="stat-change positive">
            <span>↗</span> <span>+15.3% vs last month</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Active Opportunities</div>
        <div class="stat-value">{total_leads}</div>
        <div class="stat-change positive">
            <span>↗</span> <span>+{critical_leads + high_leads} high priority</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Avg Lead Score</div>
        <div class="stat-value">{avg_score:.0f}</div>
        <div class="stat-change positive">
            <span>↗</span> <span>+5.2 points</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    conversion_rate = 0.18
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Conversion Rate</div>
        <div class="stat-value">{conversion_rate:.0%}</div>
        <div class="stat-change positive">
            <span>↗</span> <span>+3.1% improvement</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick Actions
st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📞 Call Critical Leads", use_container_width=True):
        st.toast("Showing critical leads for immediate contact", icon="📞")
with col2:
    if st.button("📧 Send Email Campaign", use_container_width=True):
        st.toast("Email campaign builder opened", icon="📧")
with col3:
    if st.button("📊 Generate Report", use_container_width=True):
        st.toast("Report generation started", icon="📊")
with col4:
    if st.button("🎯 Create Opportunity", use_container_width=True):
        st.toast("New opportunity form opened", icon="🎯")

st.markdown("<br>", unsafe_allow_html=True)

# Filters
st.markdown('<div class="section-header">🔍 Filter Opportunities</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        priority_filter = st.multiselect(
            "Priority Level",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            default=['CRITICAL', 'HIGH'],
            key="priority_filter"
        )

    with col2:
        lead_type_filter = st.multiselect(
            "Opportunity Type",
            options=['Renewal', 'Hardware Refresh', 'Service Attach'],
            default=['Renewal', 'Hardware Refresh', 'Service Attach'],
            key="type_filter"
        )

    with col3:
        score_range = st.slider(
            "Lead Score Range",
            0, 100, (50, 100),
            key="score_filter"
        )

    with col4:
        value_filter = st.selectbox(
            "Min Deal Value",
            options=["All", "$25K+", "$50K+", "$100K+", "$200K+"],
            key="value_filter"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# Build query based on filters
query = session.query(Lead).filter(Lead.is_active == True)

if priority_filter:
    query = query.filter(Lead.priority.in_(priority_filter))

if lead_type_filter:
    type_conditions = []
    for lt in lead_type_filter:
        type_conditions.append(Lead.lead_type.like(f'%{lt}%'))
    from sqlalchemy import or_
    query = query.filter(or_(*type_conditions))

query = query.filter(Lead.score >= score_range[0], Lead.score <= score_range[1])

# Apply value filter
value_map = {
    "$25K+": 25000,
    "$50K+": 50000,
    "$100K+": 100000,
    "$200K+": 200000
}
if value_filter != "All":
    query = query.filter(Lead.estimated_value_max >= value_map[value_filter])

leads = query.order_by(Lead.score.desc()).all()

# Results Summary
st.markdown('<div class="section-header">🎯 Top Opportunities</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Matching Leads", len(leads))
with col2:
    matching_value = sum([l.estimated_value_max or 0 for l in leads])
    st.metric("Total Value", f"${matching_value/1e6:.2f}M")
with col3:
    if leads:
        avg_matching_score = sum([l.score for l in leads]) / len(leads)
        st.metric("Avg Score", f"{avg_matching_score:.1f}")
    else:
        st.metric("Avg Score", "N/A")

st.markdown("<br>", unsafe_allow_html=True)

# Display leads as modern cards
if leads:
    for idx, lead in enumerate(leads[:10], 1):
        account = session.query(Account).filter(Account.id == lead.account_id).first()
        account_name = format_account(account)

        # Determine badge class
        badge_class = f"badge-{lead.priority.lower()}"
        card_class = f"lead-card-{lead.priority.lower()}" if lead.priority in ['CRITICAL', 'HIGH'] else ""

        value_display = f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else "TBD"

        st.markdown(f"""
        <div class="lead-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <span class="badge {badge_class}">{lead.priority}</span>
                    <div class="lead-title" style="margin-top: 8px;">{lead.title}</div>
                </div>
                <div class="score-circle" style="width: 60px; height: 60px; font-size: 18px;">
                    {lead.score:.0f}
                </div>
            </div>

            <div class="lead-meta">
                <div class="lead-meta-item">
                    <span>🏢</span> <strong>{account_name}</strong>
                </div>
                <div class="lead-meta-item">
                    <span>💰</span> <strong>{value_display}</strong>
                </div>
                <div class="lead-meta-item">
                    <span>📍</span> Territory {lead.territory_id}
                </div>
                <div class="lead-meta-item">
                    <span>🏷️</span> {lead.lead_type.split('-')[0].strip()}
                </div>
            </div>

            <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">
                    {lead.description[:150]}{'...' if len(lead.description) > 150 else ''}
                </div>
                <div style="font-size: 13px; color: #667eea; font-weight: 600;">
                    → {lead.recommended_action[:100]}{'...' if len(lead.recommended_action) > 100 else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("✅ Qualify", key=f"qualify_{lead.id}", use_container_width=True):
                st.success("Lead qualified!")
        with col2:
            if st.button("📞 Contact", key=f"contact_{lead.id}", use_container_width=True):
                st.info("Contact logged!")
        with col3:
            if st.button("📊 Details", key=f"details_{lead.id}", use_container_width=True):
                with st.expander("Lead Details", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Score Breakdown**")
                        st.write(f"Urgency: {lead.urgency_score:.1f}")
                        st.write(f"Value: {lead.value_score:.1f}")
                        st.write(f"Propensity: {lead.propensity_score:.1f}")
                        st.write(f"Strategic Fit: {lead.strategic_fit_score:.1f}")
                    with col_b:
                        st.markdown("**Lead Information**")
                        st.write(f"Status: {lead.lead_status}")
                        st.write(f"Type: {lead.lead_type}")
                        if lead.recommended_skus:
                            st.write(f"SKUs: {lead.recommended_skus}")
        with col4:
            if st.button("❌ Dismiss", key=f"dismiss_{lead.id}", use_container_width=True):
                st.warning("Lead dismissed!")

        st.markdown("<br>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <h3>No leads match your filters</h3>
        <p>Try adjusting your filter criteria to see more opportunities</p>
    </div>
    """, unsafe_allow_html=True)

# Analytics Section
st.markdown('<div class="section-header">📊 Performance Analytics</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Priority Distribution**")

    priority_data = session.query(
        Lead.priority,
        func.count(Lead.id).label('count')
    ).filter(Lead.is_active == True).group_by(Lead.priority).all()

    if priority_data:
        df = pd.DataFrame(priority_data, columns=['Priority', 'Count'])

        colors = {'CRITICAL': '#ef4444', 'HIGH': '#f59e0b', 'MEDIUM': '#fbbf24', 'LOW': '#10b981'}
        df['Color'] = df['Priority'].map(colors)

        fig = go.Figure(data=[go.Bar(
            x=df['Priority'],
            y=df['Count'],
            marker_color=df['Color'],
            text=df['Count'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Lead Type Breakdown**")

    type_data = session.query(
        Lead.lead_type,
        func.count(Lead.id).label('count')
    ).filter(Lead.is_active == True).group_by(Lead.lead_type).all()

    if type_data:
        df = pd.DataFrame(type_data, columns=['Type', 'Count'])
        df['Type'] = df['Type'].str.split(' - ').str[0]

        fig = go.Figure(data=[go.Pie(
            labels=df['Type'],
            values=df['Count'],
            hole=0.5,
            marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#c084fc']),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #9ca3af; padding: 20px 0; border-top: 1px solid #e5e7eb;">
    <p style="margin: 0;">🎯 OneLead Sales Intelligence Platform</p>
    <p style="margin: 5px 0 0 0; font-size: 13px;">Powered by AI • Real-time data • Updated every hour</p>
</div>
""", unsafe_allow_html=True)
