"""OneLead Premium Dashboard - World-class sales intelligence interface."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func, case, desc
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import SessionLocal, Lead, InstallBase, Account, Opportunity, Project, ServiceCatalog, ServiceSKUMapping

# Page configuration
st.set_page_config(
    page_title="OneLead Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium CSS - Inspired by top SaaS dashboards
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding: 2rem 3rem 3rem 3rem;
        max-width: 1600px;
    }

    /* Modern Header */
    .premium-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.2);
        position: relative;
        overflow: hidden;
    }

    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40" fill="rgba(255,255,255,0.05)"/></svg>');
        opacity: 0.3;
    }

    .premium-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .premium-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        font-weight: 400;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    .header-meta {
        display: flex;
        gap: 2rem;
        margin-top: 1.5rem;
        position: relative;
        z-index: 1;
    }

    .header-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(255,255,255,0.95);
        font-size: 0.95rem;
        font-weight: 500;
    }

    /* Metric Cards */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6, #06b6d4);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border-color: rgba(59, 130, 246, 0.3);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 0.75rem;
    }

    .metric-change {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
    }

    .metric-change.positive {
        color: #059669;
        background: #d1fae5;
    }

    .metric-change.negative {
        color: #dc2626;
        background: #fee2e2;
    }

    .metric-change.neutral {
        color: #6366f1;
        background: #e0e7ff;
    }

    /* Insight Cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .insight-card.critical {
        border-left: 4px solid #ef4444;
        background: linear-gradient(to right, #fef2f2 0%, white 5%);
    }

    .insight-card.opportunity {
        border-left: 4px solid #10b981;
        background: linear-gradient(to right, #f0fdf4 0%, white 5%);
    }

    .insight-card.info {
        border-left: 4px solid #3b82f6;
        background: linear-gradient(to right, #eff6ff 0%, white 5%);
    }

    .insight-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .insight-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 700;
    }

    .insight-icon.critical {
        background: #fee2e2;
        color: #dc2626;
    }

    .insight-icon.opportunity {
        background: #d1fae5;
        color: #059669;
    }

    .insight-icon.info {
        background: #dbeafe;
        color: #2563eb;
    }

    .insight-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }

    .insight-body {
        font-size: 1rem;
        line-height: 1.6;
        color: #475569;
        margin-bottom: 1.25rem;
    }

    .insight-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1rem 0;
    }

    .insight-actions {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
    }

    /* Lead Cards */
    .lead-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }

    .lead-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: rgba(59, 130, 246, 0.4);
    }

    .lead-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 1rem;
    }

    .lead-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }

    .lead-account {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }

    .score-badge {
        min-width: 60px;
        height: 60px;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
    }

    .score-badge.critical {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    }

    .score-badge.high {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: white;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .score-badge.medium {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    .score-label {
        font-size: 0.625rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    .lead-meta {
        display: flex;
        gap: 1.5rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }

    .lead-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #64748b;
    }

    .lead-meta-item strong {
        color: #0f172a;
        font-weight: 600;
    }

    .lead-description {
        font-size: 0.9375rem;
        color: #475569;
        line-height: 1.6;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 8px;
        border-left: 3px solid #e2e8f0;
    }

    .action-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1.25rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
    }

    .action-button.primary {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }

    .action-button.primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    .action-button.secondary {
        background: white;
        color: #3b82f6;
        border: 1.5px solid #3b82f6;
    }

    .action-button.secondary:hover {
        background: #eff6ff;
    }

    /* Section Headers */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }

    .section-subtitle {
        font-size: 0.9375rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Filter Pills */
    .filter-container {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }

    .filter-pill {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        border: 1.5px solid #e2e8f0;
        background: white;
        color: #64748b;
    }

    .filter-pill.active {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border-color: #3b82f6;
    }

    .filter-pill:hover {
        border-color: #3b82f6;
        transform: translateY(-1px);
    }

    /* Chart Container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
    }

    .chart-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 1rem;
    }

    /* Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: slideInUp 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_dashboard_data():
    """Load all data needed for the dashboard."""
    session = SessionLocal()
    try:
        # Get all leads with related data
        leads = session.query(Lead).all()

        # Convert to DataFrame
        leads_data = []
        for lead in leads:
            leads_data.append({
                'id': lead.id,
                'account_id': lead.account_id,
                'install_base_id': lead.install_base_id,  # CRITICAL: Needed for service lookup!
                'account_name': lead.account.account_name if lead.account else 'Unknown',
                'territory': lead.territory_id or 'Unknown',
                'lead_type': lead.lead_type,
                'priority': lead.priority,
                'score': lead.score,
                'urgency_score': lead.urgency_score or 0,
                'value_score': lead.value_score or 0,
                'propensity_score': lead.propensity_score or 0,
                'strategic_fit_score': lead.strategic_fit_score or 0,
                'title': lead.title,
                'description': lead.description,
                'product_description': lead.install_base_item.product_name if lead.install_base_item else 'N/A',
                'serial_number': lead.install_base_item.serial_number if lead.install_base_item else 'N/A',
                'days_since_eol': lead.install_base_item.days_since_eol if lead.install_base_item else 0,
                'risk_level': lead.install_base_item.risk_level if lead.install_base_item else 'N/A',
                'estimated_value': lead.estimated_value_max or lead.estimated_value_min or 0,
                'estimated_value_min': lead.estimated_value_min or 0,
                'estimated_value_max': lead.estimated_value_max or 0,
                'recommended_action': lead.recommended_action,
                'recommended_skus': lead.recommended_skus,
                'status': lead.lead_status,
                'created_date': lead.generated_at
            })

        leads_df = pd.DataFrame(leads_data)

        # Get additional stats
        stats = {
            'total_accounts': session.query(func.count(Account.id)).scalar(),
            'total_install_base': session.query(func.count(InstallBase.id)).scalar(),
            'critical_systems': session.query(func.count(InstallBase.id)).filter(
                InstallBase.risk_level == 'CRITICAL'
            ).scalar(),
            'active_opportunities': session.query(func.count(Opportunity.id)).scalar(),
            'total_pipeline': session.query(func.sum(Lead.estimated_value_max)).filter(
                Lead.is_active == True
            ).scalar() or 0
        }

        return leads_df, stats
    finally:
        session.close()


def render_header(stats):
    """Render premium header."""
    st.markdown(f"""
    <div class="premium-header animate-in">
        <h1>🎯 OneLead Intelligence</h1>
        <p>AI-powered sales intelligence platform delivering actionable insights</p>
        <div class="header-meta">
            <div class="header-meta-item">
                <span>📅</span>
                <span>{datetime.now().strftime("%B %d, %Y")}</span>
            </div>
            <div class="header-meta-item">
                <span>🏢</span>
                <span>{stats['total_accounts']} Active Accounts</span>
            </div>
            <div class="header-meta-item">
                <span>⚡</span>
                <span>Last updated: Just now</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_account_filter(leads_df):
    """Render the account filter at the top of the page. Returns filtered dataframe."""
    st.markdown("""
    <div style="background: #f8fafc; padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;">
        <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem;">Filter by Account</div>
    </div>
    """, unsafe_allow_html=True)

    # Get unique accounts sorted alphabetically
    account_names = ["All Accounts"] + sorted(leads_df['account_name'].unique().tolist())

    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        selected_account = st.selectbox(
            "Select Account",
            account_names,
            key="main_account_filter",
            label_visibility="collapsed"
        )

    # Apply filter
    if selected_account != "All Accounts":
        filtered_df = leads_df[leads_df['account_name'] == selected_account].copy()
        st.markdown(f"""
        <div style="background: #dbeafe; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0 1rem 0; border-left: 4px solid #3b82f6;">
            <span style="font-weight: 600; color: #1e40af;">Viewing: {selected_account}</span>
            <span style="color: #3b82f6; margin-left: 1rem;">{len(filtered_df)} leads</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        filtered_df = leads_df.copy()

    return filtered_df, selected_account


def render_metrics(leads_df):
    """Render key metrics cards based on filtered data only - no mock data."""
    total_leads = len(leads_df)
    if total_leads == 0:
        st.info("No leads found for the selected filter.")
        return

    critical_leads = len(leads_df[leads_df['priority'] == 'CRITICAL'])
    high_leads = len(leads_df[leads_df['priority'] == 'HIGH'])
    avg_score = leads_df['score'].mean()
    total_value = leads_df['estimated_value'].sum()

    # Calculate real metrics from the data
    high_priority_count = critical_leads + high_leads
    high_priority_value = leads_df[leads_df['priority'].isin(['CRITICAL', 'HIGH'])]['estimated_value'].sum()

    st.markdown('<div class="metric-row animate-in">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Format value appropriately based on size
        if total_value >= 1e6:
            value_display = f"${total_value/1e6:.2f}M"
        elif total_value >= 1e3:
            value_display = f"${total_value/1e3:.0f}K"
        else:
            value_display = f"${total_value:,.0f}"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Pipeline</div>
            <div class="metric-value">{value_display}</div>
            <div class="metric-change neutral">
                <span>📊</span> <span>{total_leads} leads</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High Priority</div>
            <div class="metric-value">{high_priority_count}</div>
            <div class="metric-change {"negative" if critical_leads > 0 else "neutral"}">
                <span>🔴</span> <span>{critical_leads} Critical, {high_leads} High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        score_class = "positive" if avg_score >= 65 else "neutral" if avg_score >= 50 else "negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Lead Score</div>
            <div class="metric-value">{avg_score:.0f}</div>
            <div class="metric-change {score_class}">
                <span>🎯</span> <span>{"Strong" if avg_score >= 65 else "Moderate" if avg_score >= 50 else "Needs focus"}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Count unique product types
        unique_products = leads_df['product_description'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Products at Risk</div>
            <div class="metric-value">{unique_products}</div>
            <div class="metric-change neutral">
                <span>🖥️</span> <span>Unique systems</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_insights(leads_df):
    """Render actionable insights based on REAL data only."""
    # Get actual lead type counts and values - use exact database values
    hardware_leads = leads_df[leads_df['lead_type'] == 'Hardware Refresh - EOL Equipment']
    hardware_value = hardware_leads['estimated_value'].sum()
    hardware_critical = len(hardware_leads[hardware_leads['priority'] == 'CRITICAL'])
    hardware_high = len(hardware_leads[hardware_leads['priority'] == 'HIGH'])

    renewal_leads = leads_df[leads_df['lead_type'] == 'Renewal - Expired Support']
    renewal_value = renewal_leads['estimated_value'].sum()
    renewal_high = len(renewal_leads[renewal_leads['priority'] == 'HIGH'])
    renewal_medium = len(renewal_leads[renewal_leads['priority'] == 'MEDIUM'])

    service_leads = leads_df[leads_df['lead_type'] == 'Service Attach - Coverage Gap']
    service_value = service_leads['estimated_value'].sum()
    service_high = len(service_leads[service_leads['priority'] == 'HIGH'])

    # Show insights in 3 columns
    col1, col2, col3 = st.columns(3)

    # Hardware Refresh - highest value
    with col1:
        st.markdown(f"""
        <div class="insight-card opportunity animate-in">
            <div class="insight-header">
                <div class="insight-icon opportunity">🔧</div>
                <div>
                    <h3 class="insight-title">Hardware Refresh</h3>
                    <div class="insight-account">{len(hardware_leads)} leads • ${hardware_value/1000:.0f}K</div>
                </div>
            </div>
            <div class="insight-body" style="font-size: 0.85rem;">
                EOL equipment replacement<br/>
                <span style="color: #dc2626;">{hardware_critical} Critical</span> •
                <span style="color: #f59e0b;">{hardware_high} High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Service Attach
    with col2:
        st.markdown(f"""
        <div class="insight-card info animate-in">
            <div class="insight-header">
                <div class="insight-icon info">📦</div>
                <div>
                    <h3 class="insight-title">Service Attach</h3>
                    <div class="insight-account">{len(service_leads)} leads • ${service_value/1000:.0f}K</div>
                </div>
            </div>
            <div class="insight-body" style="font-size: 0.85rem;">
                Coverage gap opportunities<br/>
                <span style="color: #f59e0b;">{service_high} High priority</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Renewal
    with col3:
        st.markdown(f"""
        <div class="insight-card critical animate-in">
            <div class="insight-header">
                <div class="insight-icon critical">🔄</div>
                <div>
                    <h3 class="insight-title">Renewals</h3>
                    <div class="insight-account">{len(renewal_leads)} leads • ${renewal_value/1000:.0f}K</div>
                </div>
            </div>
            <div class="insight-body" style="font-size: 0.85rem;">
                Expired support contracts<br/>
                <span style="color: #f59e0b;">{renewal_high} High</span> •
                <span style="color: #0891b2;">{renewal_medium} Medium</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def get_recommended_services_for_lead(lead, session):
    """Get actual HPE services from catalog based on lead details."""
    # Get product family from install base
    if not lead.get('install_base_id'):
        return []

    # Use session.get() instead of query().get()
    install_base = session.get(InstallBase, lead['install_base_id'])
    if not install_base:
        return []

    product_family = (install_base.product_family or '').upper()
    product_name = (install_base.product_name or '').upper()

    # Filter by lead type
    lead_type = lead['lead_type']
    recommended_services = []

    if 'Renewal' in lead_type:
        preferred_categories = ['Health Check', 'Optimization', 'Performance Analysis']
    elif 'Hardware Refresh' in lead_type:
        preferred_categories = ['Migration', 'Design & Implementation', 'Health Check', 'Upgrade']
    elif 'Service Attach' in lead_type:
        preferred_categories = ['Install', 'Configuration', 'Health Check', 'Deployment']
    else:
        preferred_categories = ['Health Check']

    # STRATEGY 1: Try ServiceSKUMapping (has SKUs for Storage products)
    mappings = session.query(ServiceSKUMapping).filter(
        ServiceSKUMapping.product_family.ilike(f'%{product_family}%')
    ).all()

    for mapping in mappings:
        for pref_cat in preferred_categories:
            if pref_cat.lower() in mapping.service_type.lower():
                recommended_services.append({
                    'service_type': mapping.service_type,
                    'service_sku': mapping.service_sku or 'Contact HPE',
                    'product_family': mapping.product_family
                })
                break

    # STRATEGY 2: If no SKU mappings (e.g., COMPUTE products), use ServiceCatalog
    if not recommended_services:
        # Check if this is ACTUALLY a server (not just a component)
        is_actual_server = any(keyword in product_name for keyword in ['DL360', 'DL380', 'DL560', 'DL580', 'ML350', 'ML110', 'BL460', 'BL660', 'PROLIANT', 'SERVER'])

        # Only show relevant services for actual servers, not HDDs/memory/components
        if is_actual_server:
            # Get services relevant to server hardware - broader than just "compute"
            relevant_services = session.query(ServiceCatalog).filter(
                ServiceCatalog.service_category.in_(preferred_categories)
            ).all()

            # Score and filter services by relevance to lead type and product
            scored_services = []
            for svc in relevant_services:
                svc_cat = (svc.service_category or '').lower()
                svc_name = (svc.service_name or '').lower()
                score = 0

                # Match by preferred category (highest priority)
                for pref in [p.lower() for p in preferred_categories]:
                    if pref in svc_cat:
                        score += 10
                        break

                # Bonus for compute/server-specific services
                if any(word in svc_name for word in ['compute', 'server', 'proliant', 'dl', 'ml', 'blade']):
                    score += 7

                # Bonus for specific product mentions (makes it more relevant)
                if 'DL' in product_name or 'PROLIANT' in product_name:
                    if 'dl' in svc_name or 'proliant' in svc_name or 'compute' in svc_name:
                        score += 3
                if 'ML' in product_name:
                    if 'ml' in svc_name and 'mlops' not in svc_name:  # ML servers, not MLOps
                        score += 3
                if 'BLADE' in product_name or 'BL' in product_name:
                    if 'blade' in svc_name:
                        score += 3

                # STRONGLY penalize irrelevant services for hardware refresh
                if 'Hardware Refresh' in lead_type:
                    # These are not relevant for simple server hardware refresh
                    if any(word in svc_name for word in ['mlops', 'middleware', 'database', 'db', 'oracle', 'sql server',
                                                           'storage', 'san', 'backup', 'container', 'kubernetes', 'docker',
                                                           'iot', 'data governance', 'app code']):
                        score -= 15  # Strong penalty

                if score > 0:
                    scored_services.append((score, svc))

            # Sort by score and take top services
            scored_services.sort(key=lambda x: x[0], reverse=True)
            for score, svc in scored_services[:5]:
                recommended_services.append({
                    'service_type': svc.service_name,
                    'service_sku': 'Contact HPE',
                    'product_family': 'Compute/Servers'
                })
        else:
            # For components (HDDs, memory, etc.), show general services by category
            # Don't show compute migration services for individual components
            general_services = session.query(ServiceCatalog).filter(
                ServiceCatalog.service_category.in_(preferred_categories)
            ).limit(5).all()

            if general_services:
                for svc in general_services:
                    recommended_services.append({
                        'service_type': svc.service_name,
                        'service_sku': 'Contact HPE',
                        'product_family': svc.practice or 'General'
                    })
            else:
                # For components without specific services, provide contextual message
                return [{
                    'service_type': f'This component is typically included in system-level services. See server-level recommendations.',
                    'service_sku': 'N/A',
                    'product_family': product_family or 'Component'
                }]

    # If still no services, return a helpful message
    if not recommended_services:
        return [{
            'service_type': 'Contact HPE Partner Connect for service recommendations',
            'service_sku': 'N/A',
            'product_family': product_family or 'Unknown'
        }]

    return recommended_services[:5]  # Return top 5


def generate_lead_recommendations(lead, session):
    """Generate personalized recommendations for a lead with REAL HPE services."""
    recommendations = {
        'why_matters': '',
        'services': [],
        'urgency_reason': ''
    }

    # Get actual services from catalog
    services = get_recommended_services_for_lead(lead, session)
    recommendations['services'] = services

    # Determine urgency reason
    if lead['days_since_eol'] > 1825:
        recommendations['urgency_reason'] = f"Equipment is {lead['days_since_eol']//365} years past end-of-life"
    elif lead['days_since_eol'] > 365:
        recommendations['urgency_reason'] = "Equipment has reached end-of-life"
    else:
        recommendations['urgency_reason'] = "Support contract has expired"

    # Type-specific messaging - plain text (no markdown, will be in HTML)
    if 'Renewal' in lead['lead_type']:
        recommendations['why_matters'] = f"Renewal Opportunity: Customer has {lead['product_description']} without support coverage for {lead.get('days_since_expiry', 0)} days. Risk of downtime and security vulnerabilities. Worth ${lead['estimated_value']:,.0f} annually."
    elif 'Hardware Refresh' in lead['lead_type']:
        recommendations['why_matters'] = f"Hardware Refresh Opportunity: Equipment is {lead['days_since_eol']//365}+ years past end-of-life. Modern systems offer significant performance and cost savings. Worth ${lead['estimated_value']:,.0f}."
    elif 'Service Attach' in lead['lead_type']:
        recommendations['why_matters'] = f"Service Coverage Gap: Equipment without support coverage creates risk. Opportunity to attach services worth ${lead['estimated_value']:,.0f}."

    return recommendations


def render_lead_priorities(leads_df):
    """Render top priority leads."""
    st.markdown("""
    <div class="section-header">
        <div>
            <h2 class="section-title">Your Top Priorities This Week</h2>
            <p class="section-subtitle">Start here for maximum impact - these leads are scored, qualified, and ready for action</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Secondary filters (account filter is already at top of page)
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 3])

    with filter_col1:
        priority_filter = st.selectbox(
            "Priority Level",
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
            key="priority_filter"
        )

    with filter_col2:
        type_filter = st.selectbox(
            "Lead Type",
            ["All", "Renewal - Expired Support", "Hardware Refresh - EOL Equipment", "Service Attach - Coverage Gap"],
            key="type_filter"
        )

    with filter_col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Score (High to Low)", "Value (High to Low)", "Priority"],
            key="sort_filter"
        )

    # Apply filters (leads_df is already filtered by account from main filter)
    filtered_df = leads_df.copy()
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['lead_type'] == type_filter]

    # Apply sorting
    if sort_by == "Score (High to Low)":
        filtered_df = filtered_df.sort_values('score', ascending=False)
    elif sort_by == "Value (High to Low)":
        filtered_df = filtered_df.sort_values('estimated_value', ascending=False)
    else:
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        filtered_df['priority_rank'] = filtered_df['priority'].map(priority_order)
        filtered_df = filtered_df.sort_values(['priority_rank', 'score'], ascending=[True, False])

    # Display leads
    col_info, col_export = st.columns([3, 1])
    with col_info:
        st.markdown(f"<p style='color: #64748b; margin: 1rem 0;'>Showing {len(filtered_df)} of {len(leads_df)} leads</p>", unsafe_allow_html=True)
    with col_export:
        # Export to CSV button
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"onelead_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download filtered leads as CSV for import into CRM or offline analysis"
        )

    for idx, lead in filtered_df.head(10).iterrows():
        priority_class = lead['priority'].lower()
        lead_type_icon = {
            'renewal': '🔄',
            'hardware_refresh': '🔧',
            'service_attach': '📦'
        }.get(lead['lead_type'], '📋')

        lead_type_label = {
            'renewal': 'Support Renewal',
            'hardware_refresh': 'Hardware Refresh',
            'service_attach': 'Service Attach'
        }.get(lead['lead_type'], lead['lead_type'])

        # Clean text to avoid HTML issues
        description = str(lead['description'])[:200].replace('<', '&lt;').replace('>', '&gt;') if pd.notna(lead['description']) else 'No description'
        recommended_action = str(lead['recommended_action']).replace('<', '&lt;').replace('>', '&gt;') if pd.notna(lead['recommended_action']) else 'No action specified'
        created_date = lead['created_date'].strftime('%b %d, %Y') if pd.notna(lead['created_date']) else 'N/A'

        # Use container for better rendering
        with st.container():
            st.markdown(f"""
            <div class="lead-card animate-in">
                <div class="lead-header">
                    <div>
                        <div class="lead-title">{lead_type_icon} {lead['title']}</div>
                        <div class="lead-account">🏢 {lead['account_name']} • Territory {lead['territory']}</div>
                    </div>
                    <div class="score-badge {priority_class}">
                        {int(lead['score'])}
                        <div class="score-label">Score</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Use columns for metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**📊 Type:** {lead_type_label}")
            with col2:
                st.markdown(f"**💰 Value:** ${lead['estimated_value']:,.0f}")
            with col3:
                st.markdown(f"**🎯 Priority:** {lead['priority']}")
            with col4:
                st.markdown(f"**📅 Created:** {created_date}")

            # Get DB session for service lookup
            session = SessionLocal()
            try:
                # Get personalized recommendations with actual services
                recommendations = generate_lead_recommendations(lead, session)

                # Why This Matters section
                st.markdown(f"""
                <div style="background: linear-gradient(to right, #eff6ff, #ffffff); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #3b82f6;">
                    <strong style="color: #1e40af; font-size: 1.05rem;">💡 Why This Matters:</strong><br/>
                    {recommendations['why_matters']}
                </div>
                """, unsafe_allow_html=True)

                # HPE Services Recommendations - improved layout
                if recommendations.get('services') and len(recommendations['services']) > 0:
                    st.markdown("""
                    <div style="margin: 1rem 0 0.5rem 0;">
                        <span style="font-size: 1.1rem; font-weight: 600; color: #1f2937;">🎯 Recommended HPE Services</span>
                        <span style="font-size: 0.875rem; color: #6b7280; margin-left: 0.5rem;">Ready to attach to your quote</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Use 2-column layout for services to save space
                    service_cols = st.columns(2)
                    for idx, service in enumerate(recommendations['services'], 1):
                        col = service_cols[idx % 2]
                        with col:
                            # Shorten service names if too long
                            service_name = service['service_type']
                            if len(service_name) > 60:
                                service_name = service_name[:57] + "..."

                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
                                        padding: 0.875rem;
                                        border-radius: 8px;
                                        margin: 0.5rem 0;
                                        border: 1px solid #d1fae5;
                                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <div style="display: flex; align-items: flex-start; gap: 0.5rem;">
                                    <div style="background: #10b981;
                                                color: white;
                                                min-width: 24px;
                                                height: 24px;
                                                border-radius: 50%;
                                                display: flex;
                                                align-items: center;
                                                justify-content: center;
                                                font-weight: 700;
                                                font-size: 0.75rem;
                                                flex-shrink: 0;">{idx}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: #065f46; font-size: 0.9rem; line-height: 1.3; margin-bottom: 0.5rem;">
                                            {service_name}
                                        </div>
                                        <div style="display: flex; align-items: center; gap: 0.75rem; font-size: 0.8rem;">
                                            <span style="color: #059669;">
                                                <span style="opacity: 0.7;">Family:</span> <strong>{service['product_family']}</strong>
                                            </span>
                                            <span style="color: #0891b2;">
                                                <span style="opacity: 0.7;">SKU:</span> <strong>{service['service_sku']}</strong>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Add summary and quick actions
                    st.markdown(f"""
                    <div style="background: #f9fafb; padding: 0.75rem; border-radius: 6px; margin-top: 1rem; border: 1px dashed #d1d5db;">
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            <strong style="color: #374151;">💡 Next Steps:</strong>
                            Add these {len(recommendations['services'])} services to your quote to increase deal value by 20-40%.
                            Services help ensure successful implementation and customer satisfaction.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💬 Contact HPE Partner Connect for service recommendations specific to this product.")

            except Exception as e:
                st.error(f"Error loading services: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
            finally:
                session.close()

            # Details expander
            with st.expander("📋 View Full Details & Scoring Breakdown"):
                # Scoring breakdown - simplified and more visual
                st.markdown("### 🎯 Score Components")

                # Calculate contributions
                urgency_pct = (lead['urgency_score'] * 0.35)
                value_pct = (lead['value_score'] * 0.30)
                propensity_pct = (lead['propensity_score'] * 0.20)
                strategic_pct = (lead['strategic_fit_score'] * 0.15)

                # Compact 2-column layout for score cards
                score_col1, score_col2 = st.columns(2)

                with score_col1:
                    st.markdown(f"""
                    <div style="padding: 0.75rem; background: #fef2f2; border-radius: 6px; border-left: 4px solid #dc2626; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.75rem; color: #991b1b; font-weight: 600;">🔴 URGENCY (35%)</div>
                                <div style="font-size: 0.875rem; color: #7f1d1d; margin-top: 0.25rem;">
                                    {lead['days_since_eol']:,} days past EOL • {lead['risk_level']} risk
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: 800; color: #dc2626;">{lead['urgency_score']:.0f}</div>
                                <div style="font-size: 0.75rem; color: #991b1b;">= {urgency_pct:.1f} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style="padding: 0.75rem; background: #dbeafe; border-radius: 6px; border-left: 4px solid #2563eb; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.75rem; color: #1e40af; font-weight: 600;">🎯 PROPENSITY (20%)</div>
                                <div style="font-size: 0.875rem; color: #1e3a8a; margin-top: 0.25rem;">
                                    Likelihood to close
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: 800; color: #2563eb;">{lead['propensity_score']:.0f}</div>
                                <div style="font-size: 0.75rem; color: #1e40af;">= {propensity_pct:.1f} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col2:
                    st.markdown(f"""
                    <div style="padding: 0.75rem; background: #fef3c7; border-radius: 6px; border-left: 4px solid #d97706; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.75rem; color: #92400e; font-weight: 600;">💰 VALUE (30%)</div>
                                <div style="font-size: 0.875rem; color: #78350f; margin-top: 0.25rem;">
                                    ${lead['estimated_value']:,.0f} opportunity
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: 800; color: #d97706;">{lead['value_score']:.0f}</div>
                                <div style="font-size: 0.75rem; color: #92400e;">= {value_pct:.1f} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style="padding: 0.75rem; background: #f0fdf4; border-radius: 6px; border-left: 4px solid #16a34a; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.75rem; color: #15803d; font-weight: 600;">✨ STRATEGIC FIT (15%)</div>
                                <div style="font-size: 0.875rem; color: #14532d; margin-top: 0.25rem;">
                                    Alignment with priorities
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: 800; color: #16a34a;">{lead['strategic_fit_score']:.0f}</div>
                                <div style="font-size: 0.75rem; color: #15803d;">= {strategic_pct:.1f} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Total score - prominent display
                st.markdown(f"""
                <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; text-align: center; margin: 1rem 0;">
                    <div style="font-size: 0.875rem; color: #e0e7ff; font-weight: 600; margin-bottom: 0.5rem;">TOTAL SCORE</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff;">{lead['score']:.1f}</div>
                    <div style="font-size: 0.875rem; color: #e0e7ff; margin-top: 0.25rem;">{urgency_pct:.1f} + {value_pct:.1f} + {propensity_pct:.1f} + {strategic_pct:.1f}</div>
                    <div style="font-size: 1rem; color: #ffffff; font-weight: 600; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e0e7ff;">Priority: {lead['priority']}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")

                # Additional details - more compact
                st.markdown("### 📋 Lead Details")

                st.markdown(f"""
                <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; font-size: 0.875rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                        <div>
                            <strong style="color: #475569;">🖥️ Product:</strong> {lead['product_description']}<br/>
                            <strong style="color: #475569;">🔢 Serial:</strong> {lead['serial_number']}<br/>
                            <strong style="color: #475569;">📦 Type:</strong> {lead_type_label}
                        </div>
                        <div>
                            <strong style="color: #475569;">🏢 Account:</strong> {lead['account_name']}<br/>
                            <strong style="color: #475569;">📍 Territory:</strong> {lead['territory']}<br/>
                            <strong style="color: #475569;">📅 Created:</strong> {created_date}
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
                        <strong style="color: #475569;">📄 Situation:</strong><br/>
                        <span style="color: #64748b;">{lead['description']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


def render_analytics(leads_df):
    """Render analytics visualizations."""
    st.markdown("""
    <div class="section-header">
        <div>
            <h2 class="section-title">📊 Understanding Your Pipeline</h2>
            <p class="section-subtitle">See where your revenue opportunities are and how to prioritize your time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate summary stats for context
    total_value = leads_df['estimated_value'].sum()
    critical_value = leads_df[leads_df['priority'] == 'CRITICAL']['estimated_value'].sum()
    critical_pct = (critical_value / total_value * 100) if total_value > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        # Pipeline by Priority
        priority_data = leads_df.groupby('priority')['estimated_value'].sum().reset_index()
        priority_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        priority_data['priority'] = pd.Categorical(priority_data['priority'], categories=priority_order, ordered=True)
        priority_data = priority_data.sort_values('priority')

        fig_priority = go.Figure(data=[
            go.Bar(
                x=priority_data['priority'],
                y=priority_data['estimated_value'],
                marker=dict(
                    color=['#dc2626', '#f59e0b', '#3b82f6', '#64748b'],
                    line=dict(color='white', width=2)
                ),
                text=priority_data['estimated_value'].apply(lambda x: f'${x/1000:.0f}K'),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>'
            )
        ])

        fig_priority.update_layout(
            title='Pipeline Value by Priority',
            xaxis_title='Priority Level',
            yaxis_title='Estimated Value ($)',
            height=350,
            margin=dict(t=40, b=40, l=40, r=40),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', size=12),
            showlegend=False
        )

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_priority, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Add explanation
        st.markdown(f"""
        **💡 What This Means:**
        - **{critical_pct:.0f}%** of your pipeline value is in CRITICAL priority leads
        - Focus on red (CRITICAL) and orange (HIGH) bars first
        - These are time-sensitive opportunities that need immediate attention
        """)

    with col2:
        # Lead Type Distribution
        type_data = leads_df.groupby('lead_type').agg({
            'id': 'count',
            'estimated_value': 'sum'
        }).reset_index()
        type_data.columns = ['lead_type', 'count', 'value']

        type_labels = {
            'renewal': 'Support Renewal',
            'hardware_refresh': 'Hardware Refresh',
            'service_attach': 'Service Attach'
        }
        type_data['label'] = type_data['lead_type'].map(type_labels)

        fig_type = go.Figure(data=[
            go.Pie(
                labels=type_data['label'],
                values=type_data['count'],
                marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b']),
                hole=0.5,
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
            )
        ])

        fig_type.update_layout(
            title='Lead Type Distribution',
            height=350,
            margin=dict(t=40, b=40, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', size=12),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
        )

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_type, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Add explanation
        renewal_count = len(leads_df[leads_df['lead_type'] == 'renewal'])
        hardware_count = len(leads_df[leads_df['lead_type'] == 'hardware_refresh'])
        service_count = len(leads_df[leads_df['lead_type'] == 'service_attach'])

        st.markdown(f"""
        **💡 What This Means:**
        - **Support Renewals ({renewal_count})**: Easiest wins - customers already know they need this
        - **Hardware Refresh ({hardware_count})**: Larger deals - equipment replacement opportunities
        - **Service Attach ({service_count})**: Coverage gaps - quick additions to existing base
        """)

    # Score Distribution Histogram
    fig_score = go.Figure(data=[
        go.Histogram(
            x=leads_df['score'],
            nbinsx=20,
            marker=dict(
                color='#3b82f6',
                line=dict(color='white', width=1)
            ),
            hovertemplate='Score Range: %{x}<br>Count: %{y}<extra></extra>'
        )
    ])

    fig_score.update_layout(
        title='Lead Quality Distribution - Are Your Leads Worth Pursuing?',
        xaxis_title='Lead Score (0-100)',
        yaxis_title='Number of Leads',
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12)
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_score, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Calculate quality metrics
    high_quality = len(leads_df[leads_df['score'] >= 75])
    medium_quality = len(leads_df[(leads_df['score'] >= 60) & (leads_df['score'] < 75)])
    avg_score = leads_df['score'].mean()

    st.markdown(f"""
    **💡 What This Means:**
    - **{high_quality} leads** scored 75+ (CRITICAL priority) - these are your best bets
    - **{medium_quality} leads** scored 60-74 (HIGH priority) - strong opportunities
    - **Average score: {avg_score:.0f}** - {"Good quality pipeline" if avg_score >= 65 else "Consider focusing on higher-scoring leads"}

    **Action:** Prioritize leads on the right side of this chart (higher scores = better opportunities)
    """)


def main():
    """Main dashboard function."""
    # Load data
    leads_df, stats = load_dashboard_data()

    # Render header
    render_header(stats)

    # Account filter at top - filters everything below
    filtered_df, selected_account = render_account_filter(leads_df)

    # All sections now use filtered data
    render_metrics(filtered_df)
    render_insights(filtered_df)
    render_lead_priorities(filtered_df)
    render_analytics(filtered_df)

    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 1rem 0; color: #94a3b8; font-size: 0.875rem;">
        <p>OneLead Intelligence Platform • Powered by AI • Real-time insights for revenue acceleration</p>
        <p style="margin-top: 0.5rem;">Last refreshed: {}</p>
    </div>
    """.format(datetime.now().strftime("%I:%M %p")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
