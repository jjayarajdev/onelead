"""OneLead Streamlit Dashboard."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import SessionLocal, Lead, InstallBase, Account, Opportunity, Project


# Page configuration
st.set_page_config(
    page_title="OneLead - Sales Intelligence",
    page_icon=":dart:",
    layout="wide"
)

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

    # Get accounts with real names (from opportunities)
    accounts_with_names = session.query(Account).filter(
        Account.account_name != Account.territory_id
    ).all()

    for acc in accounts_with_names:
        if acc.territory_id and acc.territory_id not in mapping:
            mapping[acc.territory_id] = acc.account_name

    return mapping

def format_territory(territory_id):
    """Format territory ID - just return the ID."""
    if not territory_id:
        return "N/A"
    return territory_id

def format_account(account):
    """Format account name, showing real name if available."""
    if not account:
        return "Unknown"

    # If account name is just a number (territory ID), try to get real name
    if account.account_name and account.account_name.isdigit():
        territory_map = get_territory_mapping()
        if account.account_name in territory_map:
            # Just return the account name without territory ID
            return territory_map[account.account_name]
        else:
            return f"Territory {account.account_name}"
    else:
        return account.account_name


# Sidebar navigation
st.sidebar.title("OneLead")
st.sidebar.markdown("### Sales Intelligence System")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard", "Lead Queue", "Account 360°", "Territory View", "Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Stats**")

# Quick stats in sidebar
total_leads = session.query(func.count(Lead.id)).filter(Lead.is_active == True).scalar()
high_priority = session.query(func.count(Lead.id)).filter(
    Lead.is_active == True,
    Lead.priority.in_(['CRITICAL', 'HIGH'])
).scalar()
total_value = session.query(func.sum(Lead.estimated_value_max)).filter(Lead.is_active == True).scalar() or 0

st.sidebar.metric("Active Leads", total_leads)
st.sidebar.metric("High Priority", high_priority)
st.sidebar.metric("Pipeline Value", f"${total_value/1000:.0f}K")


# ========================================
# PAGE: Dashboard
# ========================================
if page == "Dashboard":
    st.title("OneLead Dashboard")
    st.markdown("Sales Intelligence & Lead Generation System")
    st.markdown("---")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Leads", total_leads, help="Active leads in the system")

    with col2:
        st.metric("High Priority", high_priority, help="CRITICAL and HIGH priority leads")

    with col3:
        avg_score = session.query(func.avg(Lead.score)).filter(Lead.is_active == True).scalar() or 0
        st.metric("Avg Score", f"{avg_score:.1f}", help="Average lead score (0-100)")

    with col4:
        st.metric("Total Pipeline", f"${total_value/1e6:.2f}M", help="Sum of estimated max values")

    st.markdown("---")

    # Lead distribution charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leads by Type")
        lead_type_data = session.query(
            Lead.lead_type,
            func.count(Lead.id).label('count')
        ).filter(Lead.is_active == True).group_by(Lead.lead_type).all()

        if lead_type_data:
            df = pd.DataFrame(lead_type_data, columns=['Lead Type', 'Count'])
            fig = px.pie(df, values='Count', names='Lead Type', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Leads by Priority")
        priority_data = session.query(
            Lead.priority,
            func.count(Lead.id).label('count')
        ).filter(Lead.is_active == True).group_by(Lead.priority).all()

        if priority_data:
            df = pd.DataFrame(priority_data, columns=['Priority', 'Count'])
            color_map = {'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'yellow', 'LOW': 'green'}
            fig = px.bar(df, x='Priority', y='Count', color='Priority',
                        color_discrete_map=color_map)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top leads table
    st.subheader("Top Priority Leads")

    top_leads = session.query(Lead).filter(
        Lead.is_active == True
    ).order_by(Lead.score.desc()).limit(10).all()

    if top_leads:
        lead_data = []
        for lead in top_leads:
            account = session.query(Account).filter(Account.id == lead.account_id).first()
            lead_data.append({
                'Score': f"{lead.score:.1f}",
                'Priority': lead.priority,
                'Type': lead.lead_type,
                'Account': format_account(account),
                'Territory': format_territory(lead.territory_id),
                'Title': lead.title,
                'Est. Value': f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else 'N/A'
            })

        df = pd.DataFrame(lead_data)
        st.dataframe(df, use_container_width=True)


# ========================================
# PAGE: Lead Queue
# ========================================
elif page == "Lead Queue":
    st.title("Lead Queue")
    st.markdown("Manage and prioritize leads")
    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_type = st.multiselect(
            "Lead Type",
            options=['Renewal - Expired Support', 'Hardware Refresh - EOL Equipment', 'Service Attach - Coverage Gap'],
            default=['Renewal - Expired Support', 'Hardware Refresh - EOL Equipment', 'Service Attach - Coverage Gap']
        )

    with col2:
        filter_priority = st.multiselect(
            "Priority",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            default=['CRITICAL', 'HIGH']
        )

    with col3:
        min_score = st.slider("Minimum Score", 0, 100, 50)

    # Query leads
    query = session.query(Lead).filter(Lead.is_active == True)

    if filter_type:
        query = query.filter(Lead.lead_type.in_(filter_type))
    if filter_priority:
        query = query.filter(Lead.priority.in_(filter_priority))
    if min_score:
        query = query.filter(Lead.score >= min_score)

    leads = query.order_by(Lead.score.desc()).all()

    st.markdown(f"**Showing {len(leads)} leads**")
    st.markdown("---")

    # Display leads
    for lead in leads:
        with st.expander(f"**[{lead.priority}]** {lead.title} - Score: {lead.score:.1f}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Type:** {lead.lead_type}")
                st.markdown(f"**Description:** {lead.description}")
                st.markdown(f"**Recommended Action:** {lead.recommended_action}")

                if lead.recommended_skus:
                    st.markdown(f"**Recommended SKUs:** {lead.recommended_skus}")

            with col2:
                account = session.query(Account).filter(Account.id == lead.account_id).first()
                st.markdown(f"**Account:** {format_account(account)}")
                st.markdown(f"**Territory:** {format_territory(lead.territory_id)}")
                st.markdown(f"**Status:** {lead.lead_status}")

                if lead.estimated_value_min:
                    st.markdown(f"**Est. Value:** ${lead.estimated_value_min/1000:.0f}K - ${lead.estimated_value_max/1000:.0f}K")

                st.markdown("---")
                st.markdown("**Score Breakdown:**")
                st.markdown(f"- Urgency: {lead.urgency_score:.1f}")
                st.markdown(f"- Value: {lead.value_score:.1f}")
                st.markdown(f"- Propensity: {lead.propensity_score:.1f}")
                st.markdown(f"- Strategic Fit: {lead.strategic_fit_score:.1f}")


# ========================================
# PAGE: Account 360°
# ========================================
elif page == "Account 360°":
    st.title("Account 360° View")
    st.markdown("Complete account intelligence")
    st.markdown("---")

    # Account selector
    accounts = session.query(Account).order_by(Account.account_name).all()

    # Create mapping of formatted names to accounts
    account_display_map = {}
    for acc in accounts:
        formatted_name = format_account(acc)
        account_display_map[formatted_name] = acc

    account_display_names = sorted(account_display_map.keys())

    selected_display_name = st.selectbox("Select Account", account_display_names)

    if selected_display_name:
        account = account_display_map[selected_display_name]

        if account:
            st.subheader(f"{format_account(account)}")
            st.markdown(f"**Territory:** {format_territory(account.territory_id)} | **Country:** {account.country or 'N/A'}")
            st.markdown("---")

            # Metrics
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
                st.metric("Install Base", install_base_count)
            with col2:
                st.metric("Active Opportunities", active_opps)
            with col3:
                st.metric("Active Leads", active_leads)
            with col4:
                st.metric("Historical Projects", projects_count)

            st.markdown("---")

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Install Base", "Leads", "Opportunities", "Projects"])

            with tab1:
                st.subheader("Install Base")
                ib_items = session.query(InstallBase).filter(
                    InstallBase.account_id == account.id
                ).all()

                if ib_items:
                    ib_data = [{
                        'Serial Number': item.serial_number,
                        'Product': item.product_name,
                        'Family': item.product_family,
                        'Support Status': item.support_status,
                        'Risk Level': item.risk_level,
                        'EOL Date': str(item.product_eol_date) if item.product_eol_date else 'N/A'
                    } for item in ib_items]

                    st.dataframe(pd.DataFrame(ib_data), use_container_width=True)

            with tab2:
                st.subheader("Active Leads")
                account_leads = session.query(Lead).filter(
                    Lead.account_id == account.id,
                    Lead.is_active == True
                ).order_by(Lead.score.desc()).all()

                if account_leads:
                    for lead in account_leads:
                        st.markdown(f"**[{lead.priority}]** {lead.title} - Score: {lead.score:.1f}")
                        st.markdown(f"{lead.description}")
                        st.markdown("---")

            with tab3:
                st.subheader("Opportunities")
                opps = session.query(Opportunity).filter(
                    Opportunity.account_id == account.id
                ).all()

                if opps:
                    opp_data = [{
                        'Opportunity ID': opp.opportunity_id,
                        'Name': opp.opportunity_name,
                        'Product Line': opp.product_line
                    } for opp in opps]

                    st.dataframe(pd.DataFrame(opp_data), use_container_width=True)

            with tab4:
                st.subheader("Historical Projects")
                projects = session.query(Project).filter(
                    Project.account_id == account.id
                ).all()

                if projects:
                    proj_data = [{
                        'Project ID': proj.project_id,
                        'Description': proj.project_description,
                        'Practice': proj.practice,
                        'Status': proj.status,
                        'Start Date': str(proj.start_date) if proj.start_date else 'N/A',
                        'End Date': str(proj.end_date) if proj.end_date else 'N/A'
                    } for proj in projects]

                    st.dataframe(pd.DataFrame(proj_data), use_container_width=True)


# ========================================
# PAGE: Territory View
# ========================================
elif page == "Territory View":
    st.title("Territory View")
    st.markdown("Territory performance and coverage")
    st.markdown("---")

    # Get all territories
    territories = session.query(Lead.territory_id, func.count(Lead.id).label('lead_count')).filter(
        Lead.is_active == True,
        Lead.territory_id != None
    ).group_by(Lead.territory_id).order_by(func.count(Lead.id).desc()).all()

    if territories:
        territory_list = [t[0] for t in territories]
        selected_territory = st.selectbox("Select Territory", territory_list)

        if selected_territory:
            # Territory metrics
            col1, col2, col3 = st.columns(3)

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

            with col1:
                st.metric("Active Leads", territory_leads)
            with col2:
                st.metric("Accounts", territory_accounts)
            with col3:
                st.metric("Pipeline Value", f"${territory_value/1e6:.2f}M")

            st.markdown("---")

            # Territory leads
            st.subheader(f"Leads in Territory {selected_territory}")

            territory_lead_list = session.query(Lead).filter(
                Lead.territory_id == selected_territory,
                Lead.is_active == True
            ).order_by(Lead.score.desc()).all()

            if territory_lead_list:
                lead_data = []
                for lead in territory_lead_list:
                    account = session.query(Account).filter(Account.id == lead.account_id).first()
                    lead_data.append({
                        'Score': f"{lead.score:.1f}",
                        'Priority': lead.priority,
                        'Type': lead.lead_type,
                        'Account': format_account(account),
                        'Title': lead.title
                    })

                st.dataframe(pd.DataFrame(lead_data), use_container_width=True)


# ========================================
# PAGE: Analytics
# ========================================
elif page == "Analytics":
    st.title("Analytics & Insights")
    st.markdown("Performance metrics and trends")
    st.markdown("---")

    # Score distribution
    st.subheader("Lead Score Distribution")
    leads_for_dist = session.query(Lead.score).filter(Lead.is_active == True).all()
    if leads_for_dist:
        scores = [l[0] for l in leads_for_dist if l[0]]
        fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=20)])
        fig.update_layout(xaxis_title="Score", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Territory leaderboard
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Territory Leaderboard (by Leads)")
        territory_data = session.query(
            Lead.territory_id,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.is_active == True,
            Lead.territory_id != None
        ).group_by(Lead.territory_id).order_by(func.count(Lead.id).desc()).limit(10).all()

        if territory_data:
            df = pd.DataFrame(territory_data, columns=['Territory', 'Lead Count'])
            fig = px.bar(df, x='Territory', y='Lead Count')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Product Family Distribution")
        product_data = session.query(
            InstallBase.product_family,
            func.count(InstallBase.id).label('count')
        ).filter(
            InstallBase.product_family != None
        ).group_by(InstallBase.product_family).all()

        if product_data:
            df = pd.DataFrame(product_data, columns=['Product Family', 'Count'])
            fig = px.pie(df, values='Count', names='Product Family')
            st.plotly_chart(fig, use_container_width=True)
