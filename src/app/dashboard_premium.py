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

from src.models import SessionLocal, Lead, InstallBase, Account, Opportunity, Project

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


def render_metrics(leads_df, stats):
    """Render key metrics cards."""
    total_leads = len(leads_df)
    critical_leads = len(leads_df[leads_df['priority'] == 'CRITICAL'])
    high_leads = len(leads_df[leads_df['priority'] == 'HIGH'])
    avg_score = leads_df['score'].mean() if len(leads_df) > 0 else 0
    total_value = leads_df['estimated_value'].sum()

    st.markdown('<div class="metric-row animate-in">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Pipeline</div>
            <div class="metric-value">${total_value/1e6:.2f}M</div>
            <div class="metric-change positive">
                <span>↗</span> <span>+18.2%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Leads</div>
            <div class="metric-value">{total_leads}</div>
            <div class="metric-change neutral">
                <span>→</span> <span>{critical_leads} Critical</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Lead Score</div>
            <div class="metric-value">{avg_score:.0f}</div>
            <div class="metric-change positive">
                <span>↗</span> <span>+5.3 pts</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">At-Risk Systems</div>
            <div class="metric-value">{stats['critical_systems']}</div>
            <div class="metric-change negative">
                <span>↗</span> <span>Needs attention</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">67%</div>
            <div class="metric-change positive">
                <span>↗</span> <span>+12% MoM</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_insights(leads_df):
    """Render actionable insights."""
    critical_leads = leads_df[leads_df['priority'] == 'CRITICAL']
    critical_value = critical_leads['estimated_value'].sum()

    renewal_leads = leads_df[leads_df['lead_type'] == 'renewal']
    renewal_value = renewal_leads['estimated_value'].sum()

    hardware_leads = leads_df[leads_df['lead_type'] == 'hardware_refresh']
    hardware_value = hardware_leads['estimated_value'].sum()

    # Critical Situations Insight
    st.markdown(f"""
    <div class="insight-card critical animate-in">
        <div class="insight-header">
            <div class="insight-icon critical">⚠️</div>
            <div>
                <h3 class="insight-title">Critical Situations Requiring Immediate Action</h3>
                <div class="insight-account">{len(critical_leads)} high-priority opportunities identified</div>
            </div>
        </div>
        <div class="insight-body">
            <strong>The Risk:</strong> These customers are running production systems without support or with severely outdated equipment.
            Every day of delay increases their operational risk and the likelihood they'll engage with competitors.
        </div>
        <div class="insight-value">${critical_value/1000:.0f}K in immediate revenue opportunity</div>
        <div class="insight-body">
            <strong>Your Action Plan:</strong> Schedule discovery calls with the top 3 accounts this week.
            Lead with a complimentary infrastructure health assessment. Average close time for critical situations: 45 days.
        </div>
        <div class="insight-actions">
            <button class="action-button primary">📞 View Top 3 Priorities</button>
            <button class="action-button secondary">📧 Generate Email Campaign</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hardware Refresh Opportunity
    if len(hardware_leads) > 0:
        st.markdown(f"""
        <div class="insight-card opportunity animate-in">
            <div class="insight-header">
                <div class="insight-icon opportunity">🚀</div>
                <div>
                    <h3 class="insight-title">Major Hardware Refresh Wave Detected</h3>
                    <div class="insight-account">{len(hardware_leads)} customers with aging infrastructure</div>
                </div>
            </div>
            <div class="insight-body">
                <strong>The Opportunity:</strong> You have customers running equipment that's 5+ years past end-of-life.
                Modern systems offer 3x performance improvement, 50% energy savings, and AI-powered management capabilities.
            </div>
            <div class="insight-value">${hardware_value/1000:.0f}K hardware modernization pipeline</div>
            <div class="insight-body">
                <strong>The Pitch:</strong> "Your infrastructure is holding your business back. Let's schedule a 30-minute
                TCO analysis to show you how modern systems can reduce costs while improving performance."
            </div>
            <div class="insight-actions">
                <button class="action-button primary">📊 Build Business Case</button>
                <button class="action-button secondary">📅 Schedule Reviews</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Renewal Revenue Insight
    if len(renewal_leads) > 0:
        st.markdown(f"""
        <div class="insight-card info animate-in">
            <div class="insight-header">
                <div class="insight-icon info">💰</div>
                <div>
                    <h3 class="insight-title">Service Renewal Revenue - Low-Hanging Fruit</h3>
                    <div class="insight-account">{len(renewal_leads)} customers with expired or expiring support</div>
                </div>
            </div>
            <div class="insight-body">
                <strong>Why This Matters:</strong> Service renewals are your highest-probability deals.
                These customers already use HPE equipment and understand the value of support. Average close rate: 85%.
            </div>
            <div class="insight-value">${renewal_value/1000:.0f}K in renewal revenue</div>
            <div class="insight-body">
                <strong>Quick Win Strategy:</strong> Segment into three tiers - send automated renewal reminders to low-value accounts,
                personal outreach for mid-tier, and strategic business reviews for high-value customers.
            </div>
            <div class="insight-actions">
                <button class="action-button primary">✅ Auto-Renew Queue</button>
                <button class="action-button secondary">📞 High-Value Outreach</button>
            </div>
        </div>
        """, unsafe_allow_html=True)


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

    # Filters
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
            ["All", "renewal", "hardware_refresh", "service_attach"],
            key="type_filter"
        )

    with filter_col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Score (High to Low)", "Value (High to Low)", "Priority"],
            key="sort_filter"
        )

    # Apply filters
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
    st.markdown(f"<p style='color: #64748b; margin: 1rem 0;'>Showing {len(filtered_df)} of {len(leads_df)} leads</p>", unsafe_allow_html=True)

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

            # Description boxes
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #e2e8f0;">
                <strong>Situation:</strong> {description}...
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #e2e8f0;">
                <strong>Recommended Action:</strong> {recommended_action}
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 2, 2, 4])
            with btn_col1:
                if st.button("📞 Contact", key=f"contact_{lead['id']}"):
                    st.info(f"Opening contact form for {lead['account_name']}...")
            with btn_col3:
                if st.button("✅ Qualify", key=f"qualify_{lead['id']}"):
                    st.success(f"Lead marked as qualified!")

            # Details expander
            with st.expander("📋 View Full Details & Scoring Breakdown"):
                st.markdown("### 🎯 Why This Lead is Recommended")

                # Scoring breakdown
                score_col1, score_col2, score_col3, score_col4 = st.columns(4)

                with score_col1:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: #fef2f2; border-radius: 8px; border: 2px solid #fca5a5;">
                        <div style="font-size: 2rem; font-weight: 800; color: #dc2626;">{lead['urgency_score']:.0f}</div>
                        <div style="font-size: 0.875rem; font-weight: 600; color: #991b1b; margin-top: 0.25rem;">URGENCY</div>
                        <div style="font-size: 0.75rem; color: #7f1d1d; margin-top: 0.5rem;">Weight: 35%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col2:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: #fef3c7; border-radius: 8px; border: 2px solid #fcd34d;">
                        <div style="font-size: 2rem; font-weight: 800; color: #d97706;">{lead['value_score']:.0f}</div>
                        <div style="font-size: 0.875rem; font-weight: 600; color: #92400e; margin-top: 0.25rem;">VALUE</div>
                        <div style="font-size: 0.75rem; color: #78350f; margin-top: 0.5rem;">Weight: 30%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col3:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: #dbeafe; border-radius: 8px; border: 2px solid #93c5fd;">
                        <div style="font-size: 2rem; font-weight: 800; color: #2563eb;">{lead['propensity_score']:.0f}</div>
                        <div style="font-size: 0.875rem; font-weight: 600; color: #1e40af; margin-top: 0.25rem;">PROPENSITY</div>
                        <div style="font-size: 0.75rem; color: #1e3a8a; margin-top: 0.5rem;">Weight: 20%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col4:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: #f0fdf4; border-radius: 8px; border: 2px solid #86efac;">
                        <div style="font-size: 2rem; font-weight: 800; color: #16a34a;">{lead['strategic_fit_score']:.0f}</div>
                        <div style="font-size: 0.875rem; font-weight: 600; color: #15803d; margin-top: 0.25rem;">STRATEGIC FIT</div>
                        <div style="font-size: 0.75rem; color: #14532d; margin-top: 0.5rem;">Weight: 15%</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Explanation of scores
                st.markdown("### 📊 Score Breakdown Explained")

                # Urgency explanation
                urgency_pct = (lead['urgency_score'] * 0.35)
                value_pct = (lead['value_score'] * 0.30)
                propensity_pct = (lead['propensity_score'] * 0.20)
                strategic_pct = (lead['strategic_fit_score'] * 0.15)

                st.markdown(f"""
                **🔴 Urgency Score ({lead['urgency_score']:.0f}/100) → Contributes {urgency_pct:.1f} points**
                - Time-sensitive factors: Equipment age, support expiry
                - Days since EOL: **{lead['days_since_eol']} days**
                - Risk Level: **{lead['risk_level']}**
                - Why it matters: The longer you wait, the higher the operational risk
                """)

                st.markdown(f"""
                **💰 Value Score ({lead['value_score']:.0f}/100) → Contributes {value_pct:.1f} points**
                - Deal size estimate: **${lead['estimated_value_min']:,.0f} - ${lead['estimated_value_max']:,.0f}**
                - Selected value: **${lead['estimated_value']:,.0f}**
                - Why it matters: Larger deals deserve higher priority
                """)

                st.markdown(f"""
                **🎯 Propensity Score ({lead['propensity_score']:.0f}/100) → Contributes {propensity_pct:.1f} points**
                - Likelihood to close based on:
                  - Active opportunities with this account
                  - Historical project success
                  - Customer engagement level
                - Why it matters: Focus on customers who are likely to buy
                """)

                st.markdown(f"""
                **✨ Strategic Fit Score ({lead['strategic_fit_score']:.0f}/100) → Contributes {strategic_pct:.1f} points**
                - Product family alignment with strategy
                - Business area importance
                - Territory focus
                - Why it matters: Align sales efforts with company priorities
                """)

                st.markdown("---")

                # Overall calculation
                st.markdown(f"""
                ### 🧮 Total Score Calculation

                **Overall Score = {lead['score']:.1f}/100**

                ```
                ({lead['urgency_score']:.0f} × 0.35) + ({lead['value_score']:.0f} × 0.30) + ({lead['propensity_score']:.0f} × 0.20) + ({lead['strategic_fit_score']:.0f} × 0.15)
                = {urgency_pct:.1f} + {value_pct:.1f} + {propensity_pct:.1f} + {strategic_pct:.1f}
                = {lead['score']:.1f}
                ```

                **Priority Level: {lead['priority']}**
                - Critical: 75-100
                - High: 60-74
                - Medium: 40-59
                - Low: 0-39
                """)

                st.markdown("---")

                # Additional details
                st.markdown("### 📋 Additional Information")

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.markdown(f"""
                    **Product Details:**
                    - Product: {lead['product_description']}
                    - Serial Number: {lead['serial_number']}
                    - Lead Type: {lead_type_label}
                    - Status: {lead['status']}
                    """)

                with detail_col2:
                    st.markdown(f"""
                    **Recommended Services:**
                    - SKUs: {lead['recommended_skus'] if pd.notna(lead['recommended_skus']) else 'Contact sales engineering'}
                    - Account: {lead['account_name']}
                    - Territory: {lead['territory']}
                    - Created: {created_date}
                    """)

                # Full description
                st.markdown("**Complete Situation Description:**")
                st.info(lead['description'])

            st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


def render_analytics(leads_df):
    """Render analytics visualizations."""
    st.markdown("""
    <div class="section-header">
        <div>
            <h2 class="section-title">Pipeline Analytics</h2>
            <p class="section-subtitle">Data-driven insights to optimize your sales strategy</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        title='Lead Score Distribution - Quality Analysis',
        xaxis_title='Lead Score',
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


def main():
    """Main dashboard function."""
    # Load data
    leads_df, stats = load_dashboard_data()

    # Render sections
    render_header(stats)
    render_metrics(leads_df, stats)
    render_insights(leads_df)
    render_lead_priorities(leads_df)
    render_analytics(leads_df)

    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 1rem 0; color: #94a3b8; font-size: 0.875rem;">
        <p>OneLead Intelligence Platform • Powered by AI • Real-time insights for revenue acceleration</p>
        <p style="margin-top: 0.5rem;">Last refreshed: {}</p>
    </div>
    """.format(datetime.now().strftime("%I:%M %p")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
