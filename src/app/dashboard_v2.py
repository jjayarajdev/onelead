"""OneLead Streamlit Dashboard - Enhanced Version."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import SessionLocal, Lead, InstallBase, Account, Opportunity, Project


# Page configuration
st.set_page_config(
    page_title="OneLead - Sales Intelligence",
    page_icon=":dart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main content padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
    }

    /* Priority badges */
    .priority-critical {
        background-color: #ff4444;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }

    .priority-high {
        background-color: #ff9933;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }

    .priority-medium {
        background-color: #ffbb33;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }

    .priority-low {
        background-color: #00C851;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }

    /* Lead cards */
    .lead-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .lead-card-critical {
        border-left-color: #ff4444;
    }

    .lead-card-high {
        border-left-color: #ff9933;
    }

    /* Status badge */
    .status-badge {
        background-color: #e7f3ff;
        color: #0066cc;
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 500;
        display: inline-block;
    }

    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Stat card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }

    /* Tables */
    .dataframe {
        font-size: 14px;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Search box */
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid #e5e7eb;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
@st.cache_resource
def get_session():
    return SessionLocal()

session = get_session()


# Helper functions
@st.cache_data
def get_territory_mapping():
    """Build territory ID to account name mapping."""
    mapping = {}
    accounts_with_names = session.query(Account).filter(
        Account.account_name != Account.territory_id
    ).all()

    for acc in accounts_with_names:
        if acc.territory_id and acc.territory_id not in mapping:
            mapping[acc.territory_id] = acc.account_name

    return mapping

def format_territory(territory_id):
    """Format territory ID."""
    if not territory_id:
        return "N/A"
    return territory_id

def format_account(account):
    """Format account name, showing real name if available."""
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

def get_priority_color(priority):
    """Get color for priority level."""
    colors = {
        'CRITICAL': '#ff4444',
        'HIGH': '#ff9933',
        'MEDIUM': '#ffbb33',
        'LOW': '#00C851'
    }
    return colors.get(priority, '#6c757d')

def render_priority_badge(priority):
    """Render a colored priority badge."""
    color = get_priority_color(priority)
    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 12px;">{priority}</span>'

def render_metric_card(title, value, delta=None, icon=None):
    """Render a custom metric card."""
    delta_html = ""
    if delta:
        delta_color = "#00C851" if delta > 0 else "#ff4444"
        delta_html = f'<div style="color: {delta_color}; font-size: 14px; margin-top: 5px;">{delta:+.1%} vs last month</div>'

    icon_html = f'<div style="font-size: 24px; margin-bottom: 10px;">{icon}</div>' if icon else ""

    return f"""
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        {icon_html}
        <div style="color: #6c757d; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
        <div style="font-size: 32px; font-weight: 700; color: #1f2937; margin-top: 8px;">{value}</div>
        {delta_html}
    </div>
    """


# Sidebar navigation with icons
st.sidebar.title("🎯 OneLead")
st.sidebar.markdown("### Sales Intelligence Platform")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "📋 Lead Queue", "👤 Account 360°", "🗺️ Territory View", "📊 Analytics"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Quick stats in sidebar with better formatting
st.sidebar.markdown("### 📈 Quick Stats")

total_leads = session.query(func.count(Lead.id)).filter(Lead.is_active == True).scalar()
high_priority = session.query(func.count(Lead.id)).filter(
    Lead.is_active == True,
    Lead.priority.in_(['CRITICAL', 'HIGH'])
).scalar()
total_value = session.query(func.sum(Lead.estimated_value_max)).filter(Lead.is_active == True).scalar() or 0

st.sidebar.metric("Total Active Leads", f"{total_leads}", help="All active leads in pipeline")
st.sidebar.metric("High Priority", f"{high_priority}", f"{high_priority/total_leads*100:.0f}%" if total_leads > 0 else "0%")
st.sidebar.metric("Pipeline Value", f"${total_value/1e6:.1f}M", help="Sum of estimated max values")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Actions")
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("📥 Export Leads", use_container_width=True):
    st.sidebar.info("Export feature coming soon!")


# ========================================
# PAGE: Dashboard
# ========================================
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard Overview")
    st.markdown("**Welcome to OneLead** - Your intelligent sales acceleration platform")
    st.markdown("---")

    # Top KPI metrics with custom cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_score = session.query(func.avg(Lead.score)).filter(Lead.is_active == True).scalar() or 0
        st.markdown(render_metric_card("Avg Lead Score", f"{avg_score:.1f}", delta=0.05, icon="🎯"), unsafe_allow_html=True)

    with col2:
        conversion_rate = 0.18  # Placeholder - would track actual conversions
        st.markdown(render_metric_card("Conversion Rate", f"{conversion_rate:.0%}", delta=0.03, icon="✅"), unsafe_allow_html=True)

    with col3:
        st.markdown(render_metric_card("Active Leads", str(total_leads), icon="📋"), unsafe_allow_html=True)

    with col4:
        st.markdown(render_metric_card("Pipeline", f"${total_value/1e6:.1f}M", delta=0.12, icon="💰"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Priority distribution and lead types
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Priority Distribution</div>', unsafe_allow_html=True)
        priority_data = session.query(
            Lead.priority,
            func.count(Lead.id).label('count')
        ).filter(Lead.is_active == True).group_by(Lead.priority).all()

        if priority_data:
            df = pd.DataFrame(priority_data, columns=['Priority', 'Count'])

            # Custom color mapping
            color_map = {
                'CRITICAL': '#ff4444',
                'HIGH': '#ff9933',
                'MEDIUM': '#ffbb33',
                'LOW': '#00C851'
            }

            fig = go.Figure(data=[go.Bar(
                x=df['Priority'],
                y=df['Count'],
                marker_color=[color_map.get(p, '#6c757d') for p in df['Priority']],
                text=df['Count'],
                textposition='auto',
            )])

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Number of Leads",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Lead Types</div>', unsafe_allow_html=True)
        lead_type_data = session.query(
            Lead.lead_type,
            func.count(Lead.id).label('count')
        ).filter(Lead.is_active == True).group_by(Lead.lead_type).all()

        if lead_type_data:
            df = pd.DataFrame(lead_type_data, columns=['Lead Type', 'Count'])

            # Shorten names for better display
            df['Lead Type'] = df['Lead Type'].str.replace('Renewal - ', '').str.replace('Hardware Refresh - ', 'HW: ').str.replace('Service Attach - ', 'Svc: ')

            fig = go.Figure(data=[go.Pie(
                labels=df['Lead Type'],
                values=df['Count'],
                hole=0.4,
                marker=dict(colors=['#667eea', '#764ba2', '#f093fb']),
                textinfo='label+percent',
                textposition='auto'
            )])

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top priority leads - Enhanced display
    st.markdown('<div class="section-header">🔥 Top Priority Leads</div>', unsafe_allow_html=True)

    # Add search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search leads", placeholder="Search by title, account...", label_visibility="collapsed")
    with col2:
        priority_filter = st.multiselect("Filter Priority", ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], default=['CRITICAL', 'HIGH'], label_visibility="collapsed")
    with col3:
        sort_by = st.selectbox("Sort By", ['Score (High→Low)', 'Score (Low→High)', 'Value (High→Low)'], label_visibility="collapsed")

    # Query leads
    query = session.query(Lead).filter(Lead.is_active == True)

    if priority_filter:
        query = query.filter(Lead.priority.in_(priority_filter))

    if sort_by == 'Score (High→Low)':
        query = query.order_by(Lead.score.desc())
    elif sort_by == 'Score (Low→High)':
        query = query.order_by(Lead.score.asc())
    elif sort_by == 'Value (High→Low)':
        query = query.order_by(Lead.estimated_value_max.desc())

    top_leads = query.limit(10).all()

    # Display leads as cards
    for lead in top_leads:
        account = session.query(Account).filter(Account.id == lead.account_id).first()
        account_name = format_account(account)

        # Apply search filter
        if search_term and search_term.lower() not in lead.title.lower() and search_term.lower() not in account_name.lower():
            continue

        # Card with color-coded border
        card_class = f"lead-card-{lead.priority.lower()}" if lead.priority in ['CRITICAL', 'HIGH'] else ""

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{lead.title}**")
                st.caption(f"👤 {account_name} • 📍 Territory {lead.territory_id}")

            with col2:
                st.markdown(render_priority_badge(lead.priority), unsafe_allow_html=True)
                st.caption(f"Score: **{lead.score:.1f}**/100")

            with col3:
                value_display = f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else "N/A"
                st.markdown(f"**{value_display}**")
                st.caption(f"Est. Value")

            # Expandable details
            with st.expander("View Details"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Type:** {lead.lead_type}")
                    st.markdown(f"**Description:** {lead.description}")
                    st.markdown(f"**Recommended Action:** {lead.recommended_action}")

                with col2:
                    st.markdown("**Score Breakdown**")

                    # Score breakdown chart
                    scores = {
                        'Urgency': lead.urgency_score or 0,
                        'Value': lead.value_score or 0,
                        'Propensity': lead.propensity_score or 0,
                        'Strategic': lead.strategic_fit_score or 0
                    }

                    fig = go.Figure(data=[go.Bar(
                        x=list(scores.values()),
                        y=list(scores.keys()),
                        orientation='h',
                        marker_color='#667eea',
                        text=[f"{v:.0f}" for v in scores.values()],
                        textposition='auto'
                    )])

                    fig.update_layout(
                        height=200,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis_range=[0, 100],
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Qualify", key=f"qualify_{lead.id}", use_container_width=True):
                        st.success("Lead qualified!")
                with col2:
                    if st.button("📞 Contact", key=f"contact_{lead.id}", use_container_width=True):
                        st.info("Contact logged!")
                with col3:
                    if st.button("❌ Reject", key=f"reject_{lead.id}", use_container_width=True):
                        st.warning("Lead rejected!")

            st.markdown("---")


# ========================================
# PAGE: Lead Queue
# ========================================
elif page == "📋 Lead Queue":
    st.title("📋 Lead Queue")
    st.markdown("Manage and prioritize your sales pipeline")
    st.markdown("---")

    # Advanced filters in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filter_type = st.multiselect(
            "Lead Type",
            options=['Renewal - Expired Support', 'Hardware Refresh - EOL Equipment', 'Service Attach - Coverage Gap'],
            default=['Renewal - Expired Support', 'Hardware Refresh - EOL Equipment']
        )

    with col2:
        filter_priority = st.multiselect(
            "Priority",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            default=['CRITICAL', 'HIGH']
        )

    with col3:
        min_score = st.slider("Minimum Score", 0, 100, 50)

    with col4:
        min_value = st.select_slider(
            "Min Value",
            options=[0, 25000, 50000, 75000, 100000, 150000, 200000],
            value=0,
            format_func=lambda x: f"${x/1000:.0f}K" if x > 0 else "Any"
        )

    # Query leads
    query = session.query(Lead).filter(Lead.is_active == True)

    if filter_type:
        query = query.filter(Lead.lead_type.in_(filter_type))
    if filter_priority:
        query = query.filter(Lead.priority.in_(filter_priority))
    if min_score:
        query = query.filter(Lead.score >= min_score)
    if min_value > 0:
        query = query.filter(Lead.estimated_value_max >= min_value)

    leads = query.order_by(Lead.score.desc()).all()

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Matching Leads", len(leads))
    with col2:
        total_pipeline = sum([l.estimated_value_max or 0 for l in leads])
        st.metric("Total Pipeline", f"${total_pipeline/1e6:.2f}M")
    with col3:
        avg_score = sum([l.score for l in leads]) / len(leads) if leads else 0
        st.metric("Avg Score", f"{avg_score:.1f}")

    st.markdown("---")

    # Leads table view with actions
    if leads:
        # Create DataFrame for display
        lead_data = []
        for lead in leads:
            account = session.query(Account).filter(Account.id == lead.account_id).first()
            lead_data.append({
                'ID': lead.id,
                'Priority': lead.priority,
                'Score': f"{lead.score:.1f}",
                'Title': lead.title[:50] + "..." if len(lead.title) > 50 else lead.title,
                'Account': format_account(account),
                'Type': lead.lead_type.split('-')[0].strip(),
                'Value': f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else "N/A",
                'Territory': lead.territory_id
            })

        df = pd.DataFrame(lead_data)

        # Color code the dataframe
        def highlight_priority(row):
            colors = {
                'CRITICAL': 'background-color: #ffe6e6',
                'HIGH': 'background-color: #fff4e6',
                'MEDIUM': 'background-color: #ffffcc',
                'LOW': 'background-color: #e6ffe6'
            }
            return [colors.get(row['Priority'], '')] * len(row)

        st.dataframe(
            df.style.apply(highlight_priority, axis=1),
            use_container_width=True,
            hide_index=True,
            height=600
        )
    else:
        st.info("No leads match your filters. Try adjusting your criteria.")


# ========================================
# PAGE: Account 360°
# ========================================
elif page == "👤 Account 360°":
    st.title("👤 Account 360° View")
    st.markdown("Complete account intelligence and relationship history")
    st.markdown("---")

    # Account selector with search
    accounts = session.query(Account).order_by(Account.account_name).all()

    account_display_map = {}
    for acc in accounts:
        formatted_name = format_account(acc)
        account_display_map[formatted_name] = acc

    account_display_names = sorted(account_display_map.keys())

    selected_display_name = st.selectbox(
        "🔍 Select Account",
        account_display_names,
        help="Search and select an account to view details"
    )

    if selected_display_name:
        account = account_display_map[selected_display_name]

        if account:
            # Account header
            st.markdown(f"## {format_account(account)}")

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**Territory:** {format_territory(account.territory_id)}")
            with col2:
                st.markdown(f"**Country:** {account.country or 'N/A'}")
            with col3:
                st.markdown(f"**Industry:** {account.industry_code or 'N/A'}")

            st.markdown("---")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            install_base_count = session.query(func.count(InstallBase.id)).filter(
                InstallBase.account_id == account.id
            ).scalar()

            active_opps = session.query(func.count(Opportunity.id)).filter(
                Opportunity.account_id == account.id
            ).scalar()

            active_leads = session.query(func.count(Lead.id)).filter(
                Lead.account_id == account.id,
                Lead.is_active == True
            ).scalar()

            projects_count = session.query(func.count(Project.id)).filter(
                Project.account_id == account.id
            ).scalar()

            with col1:
                st.markdown(render_metric_card("Install Base", str(install_base_count), icon="💻"), unsafe_allow_html=True)
            with col2:
                st.markdown(render_metric_card("Active Opps", str(active_opps), icon="🎯"), unsafe_allow_html=True)
            with col3:
                st.markdown(render_metric_card("Active Leads", str(active_leads), icon="⚡"), unsafe_allow_html=True)
            with col4:
                st.markdown(render_metric_card("Projects", str(projects_count), icon="📦"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📦 Install Base", "⚡ Active Leads", "🎯 Opportunities", "📊 Project History"])

            with tab1:
                st.markdown('<div class="section-header">Hardware Inventory</div>', unsafe_allow_html=True)
                ib_items = session.query(InstallBase).filter(
                    InstallBase.account_id == account.id
                ).all()

                if ib_items:
                    ib_data = []
                    for item in ib_items:
                        ib_data.append({
                            'Serial Number': item.serial_number,
                            'Product': item.product_name[:40] + "..." if len(item.product_name) > 40 else item.product_name,
                            'Family': item.product_family,
                            'Support Status': item.support_status,
                            'Risk': item.risk_level,
                            'EOL Date': str(item.product_eol_date) if item.product_eol_date else 'N/A',
                            'Days Since EOL': item.days_since_eol or 'N/A'
                        })

                    df = pd.DataFrame(ib_data)

                    # Color code by risk
                    def highlight_risk(row):
                        colors = {
                            'CRITICAL': 'background-color: #ffe6e6',
                            'HIGH': 'background-color: #fff4e6',
                            'MEDIUM': 'background-color: #ffffcc',
                            'LOW': 'background-color: #e6ffe6'
                        }
                        return [colors.get(row['Risk'], '')] * len(row)

                    st.dataframe(
                        df.style.apply(highlight_risk, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No install base data available for this account")

            with tab2:
                st.markdown('<div class="section-header">Active Leads</div>', unsafe_allow_html=True)
                account_leads = session.query(Lead).filter(
                    Lead.account_id == account.id,
                    Lead.is_active == True
                ).order_by(Lead.score.desc()).all()

                if account_leads:
                    for lead in account_leads:
                        with st.container():
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.markdown(f"**{lead.title}**")
                                st.caption(lead.lead_type)

                            with col2:
                                st.markdown(render_priority_badge(lead.priority), unsafe_allow_html=True)
                                st.caption(f"Score: {lead.score:.1f}")

                            st.markdown(f"📝 {lead.description}")
                            st.markdown(f"💡 **Action:** {lead.recommended_action}")

                            st.markdown("---")
                else:
                    st.info("No active leads for this account")

            with tab3:
                st.markdown('<div class="section-header">Sales Opportunities</div>', unsafe_allow_html=True)
                opps = session.query(Opportunity).filter(
                    Opportunity.account_id == account.id
                ).all()

                if opps:
                    opp_data = [{
                        'Opportunity ID': opp.opportunity_id,
                        'Name': opp.opportunity_name[:60] + "..." if len(opp.opportunity_name) > 60 else opp.opportunity_name,
                        'Product Line': opp.product_line
                    } for opp in opps]

                    st.dataframe(pd.DataFrame(opp_data), use_container_width=True, hide_index=True)
                else:
                    st.info("No opportunities on record")

            with tab4:
                st.markdown('<div class="section-header">Historical Projects</div>', unsafe_allow_html=True)
                projects = session.query(Project).filter(
                    Project.account_id == account.id
                ).order_by(Project.start_date.desc()).all()

                if projects:
                    proj_data = [{
                        'Project ID': proj.project_id,
                        'Description': proj.project_description[:50] + "..." if proj.project_description and len(proj.project_description) > 50 else proj.project_description,
                        'Practice': proj.practice,
                        'Status': proj.status,
                        'Start': str(proj.start_date) if proj.start_date else 'N/A',
                        'End': str(proj.end_date) if proj.end_date else 'N/A',
                        'Size': proj.size_category
                    } for proj in projects]

                    st.dataframe(pd.DataFrame(proj_data), use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No project history available")


# ========================================
# PAGE: Territory View
# ========================================
elif page == "🗺️ Territory View":
    st.title("🗺️ Territory Management")
    st.markdown("Territory performance and coverage analysis")
    st.markdown("---")

    # Get all territories
    territories = session.query(
        Lead.territory_id,
        func.count(Lead.id).label('lead_count')
    ).filter(
        Lead.is_active == True,
        Lead.territory_id != None
    ).group_by(Lead.territory_id).order_by(func.count(Lead.id).desc()).all()

    if territories:
        territory_list = [t[0] for t in territories]

        # Territory selector
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_territory = st.selectbox("Select Territory", territory_list)
        with col2:
            territory_map = get_territory_mapping()
            territory_name = territory_map.get(selected_territory, f"Territory {selected_territory}")
            st.markdown(f"### {territory_name}")

        if selected_territory:
            st.markdown("---")

            # Territory metrics
            col1, col2, col3, col4 = st.columns(4)

            territory_leads = session.query(func.count(Lead.id)).filter(
                Lead.territory_id == selected_territory,
                Lead.is_active == True
            ).scalar()

            territory_accounts = session.query(func.count(func.distinct(Account.id))).join(
                Lead, Account.id == Lead.account_id
            ).filter(
                Lead.territory_id == selected_territory
            ).scalar()

            territory_value = session.query(func.sum(Lead.estimated_value_max)).filter(
                Lead.territory_id == selected_territory,
                Lead.is_active == True
            ).scalar() or 0

            critical_leads = session.query(func.count(Lead.id)).filter(
                Lead.territory_id == selected_territory,
                Lead.is_active == True,
                Lead.priority == 'CRITICAL'
            ).scalar()

            with col1:
                st.markdown(render_metric_card("Active Leads", str(territory_leads), icon="📋"), unsafe_allow_html=True)
            with col2:
                st.markdown(render_metric_card("Accounts", str(territory_accounts), icon="👥"), unsafe_allow_html=True)
            with col3:
                st.markdown(render_metric_card("Pipeline", f"${territory_value/1e6:.2f}M", icon="💰"), unsafe_allow_html=True)
            with col4:
                st.markdown(render_metric_card("Critical", str(critical_leads), icon="🚨"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Territory lead breakdown
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="section-header">Lead Type Distribution</div>', unsafe_allow_html=True)

                lead_types = session.query(
                    Lead.lead_type,
                    func.count(Lead.id).label('count')
                ).filter(
                    Lead.territory_id == selected_territory,
                    Lead.is_active == True
                ).group_by(Lead.lead_type).all()

                if lead_types:
                    df = pd.DataFrame(lead_types, columns=['Type', 'Count'])
                    df['Type'] = df['Type'].str.replace('Renewal - ', '').str.replace('Hardware Refresh - ', 'HW: ').str.replace('Service Attach - ', 'Svc: ')

                    fig = px.bar(df, x='Type', y='Count', color='Count', color_continuous_scale='Blues')
                    fig.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown('<div class="section-header">Score Distribution</div>', unsafe_allow_html=True)

                scores = session.query(Lead.score).filter(
                    Lead.territory_id == selected_territory,
                    Lead.is_active == True
                ).all()

                if scores:
                    score_values = [s[0] for s in scores if s[0]]

                    fig = go.Figure(data=[go.Histogram(x=score_values, nbinsx=10, marker_color='#667eea')])
                    fig.update_layout(
                        height=300,
                        xaxis_title="Score",
                        yaxis_title="Count",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Territory leads table
            st.markdown('<div class="section-header">All Territory Leads</div>', unsafe_allow_html=True)

            territory_lead_list = session.query(Lead).filter(
                Lead.territory_id == selected_territory,
                Lead.is_active == True
            ).order_by(Lead.score.desc()).all()

            if territory_lead_list:
                lead_data = []
                for lead in territory_lead_list:
                    account = session.query(Account).filter(Account.id == lead.account_id).first()
                    lead_data.append({
                        'Priority': lead.priority,
                        'Score': f"{lead.score:.1f}",
                        'Account': format_account(account),
                        'Type': lead.lead_type.split('-')[0].strip(),
                        'Title': lead.title[:60] + "..." if len(lead.title) > 60 else lead.title,
                        'Value': f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else "N/A"
                    })

                df = pd.DataFrame(lead_data)

                def highlight_priority(row):
                    colors = {
                        'CRITICAL': 'background-color: #ffe6e6',
                        'HIGH': 'background-color: #fff4e6',
                        'MEDIUM': 'background-color: #ffffcc',
                        'LOW': 'background-color: #e6ffe6'
                    }
                    return [colors.get(row['Priority'], '')] * len(row)

                st.dataframe(
                    df.style.apply(highlight_priority, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )


# ========================================
# PAGE: Analytics
# ========================================
elif page == "📊 Analytics":
    st.title("📊 Analytics & Insights")
    st.markdown("Performance metrics and business intelligence")
    st.markdown("---")

    # Top-level metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_pipeline = session.query(func.sum(Lead.estimated_value_max)).filter(
            Lead.is_active == True
        ).scalar() or 0
        st.markdown(render_metric_card("Total Pipeline", f"${total_pipeline/1e6:.2f}M", delta=0.15, icon="💰"), unsafe_allow_html=True)

    with col2:
        avg_deal_size = total_pipeline / total_leads if total_leads > 0 else 0
        st.markdown(render_metric_card("Avg Deal Size", f"${avg_deal_size/1000:.0f}K", delta=0.08, icon="📈"), unsafe_allow_html=True)

    with col3:
        high_value_leads = session.query(func.count(Lead.id)).filter(
            Lead.is_active == True,
            Lead.estimated_value_max >= 100000
        ).scalar()
        st.markdown(render_metric_card("High Value Leads", f"{high_value_leads}", icon="⭐"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Territory Leaderboard</div>', unsafe_allow_html=True)
        territory_data = session.query(
            Lead.territory_id,
            func.count(Lead.id).label('count'),
            func.sum(Lead.estimated_value_max).label('value')
        ).filter(
            Lead.is_active == True,
            Lead.territory_id != None
        ).group_by(Lead.territory_id).order_by(func.count(Lead.id).desc()).limit(10).all()

        if territory_data:
            territory_map = get_territory_mapping()
            df = pd.DataFrame(territory_data, columns=['Territory', 'Leads', 'Pipeline'])
            df['Territory Name'] = df['Territory'].apply(lambda x: territory_map.get(x, f"Territory {x}"))
            df['Pipeline'] = df['Pipeline'].fillna(0) / 1e6

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=df['Territory Name'],
                x=df['Leads'],
                name='Leads',
                orientation='h',
                marker_color='#667eea'
            ))

            fig.update_layout(
                height=400,
                xaxis_title="Number of Leads",
                yaxis_title="",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Product Family Distribution</div>', unsafe_allow_html=True)
        product_data = session.query(
            InstallBase.product_family,
            func.count(InstallBase.id).label('count')
        ).filter(
            InstallBase.product_family != None
        ).group_by(InstallBase.product_family).all()

        if product_data:
            df = pd.DataFrame(product_data, columns=['Family', 'Count'])

            fig = px.pie(
                df,
                values='Count',
                names='Family',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Score distribution
    st.markdown('<div class="section-header">Lead Score Distribution</div>', unsafe_allow_html=True)

    scores = session.query(Lead.score, Lead.priority).filter(Lead.is_active == True).all()

    if scores:
        df = pd.DataFrame(scores, columns=['Score', 'Priority'])

        fig = px.histogram(
            df,
            x='Score',
            color='Priority',
            nbins=20,
            color_discrete_map={
                'CRITICAL': '#ff4444',
                'HIGH': '#ff9933',
                'MEDIUM': '#ffbb33',
                'LOW': '#00C851'
            }
        )

        fig.update_layout(
            height=300,
            xaxis_title="Score",
            yaxis_title="Number of Leads",
            legend_title="Priority"
        )

        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("OneLead Sales Intelligence Platform • Powered by AI & Data")
