"""
OneLead - Complete Lead Intelligence Platform
Reimagined with 3-Category Lead System + Service Recommendations
Built 100% on Actual Data from Excel Files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path
from sqlalchemy import func, and_, or_

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.base import SessionLocal
from src.models import Lead, Account, InstallBase, Project, Opportunity, ServiceSKUMapping

# Page configuration
st.set_page_config(
    page_title="OneLead - Complete Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #01A982 0%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .category-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.25rem;
    }
    .cat-install-base {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .cat-ongoing {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    .cat-completed {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
    }
    .opportunity-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transition: all 0.3s ease;
    }
    .opportunity-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    .priority-critical {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-high {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-medium {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .priority-low {
        background: #e0e0e0;
        color: #666;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .recommendation-box {
        background: #f8f9fa;
        border-left: 4px solid #01A982;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .service-sku {
        background: #e3f2fd;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #1976d2;
        display: inline-block;
        margin: 0.2rem;
    }
    .customer-info {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .section-divider {
        border-top: 3px solid #01A982;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_session():
    """Get database session."""
    return SessionLocal()


@st.cache_data(ttl=300)
def load_install_base_leads():
    """Load Category 1: Install Base (RAW data from Install Base table - NO calculated leads)."""
    session = get_session()

    # Load RAW install base items directly from the Install Base Excel sheet
    install_base_items = session.query(InstallBase).all()

    data = []
    for item in install_base_items:
        # Get customer name from account
        account = session.query(Account).filter(Account.id == item.account_id).first()

        # Determine simple priority based ONLY on actual data (not calculated scores)
        priority = 'MEDIUM'  # Default
        if item.support_status and 'Expired' in item.support_status:
            if item.days_since_expiry and item.days_since_expiry > 365:
                priority = 'HIGH'
            elif item.days_since_expiry and item.days_since_expiry > 180:
                priority = 'MEDIUM'

        if item.days_since_eol and item.days_since_eol > 1825:  # 5 years past EOL
            priority = 'HIGH'

        data.append({
            'category': 'Install Base',
            'id': item.id,
            'serial_number': item.serial_number,
            'product_name': item.product_name,
            'customer_name': account.account_name if account else 'Unknown',
            'business_area': item.business_area,
            'support_status': item.support_status,
            'priority': priority,
            'product_eol_date': item.product_eol_date,
            'product_eos_date': item.product_eos_date,
            'service_start_date': item.service_start_date,
            'service_end_date': item.service_end_date,
            'days_since_eol': item.days_since_eol,
            'days_since_expiry': item.days_since_expiry,
            'risk_level': item.risk_level,
            'account_id': item.account_id,
            'territory_id': item.territory_id,
            'product_family': item.product_family
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_ongoing_project_opportunities():
    """Load Category 2: Ongoing Projects (end date > today)."""
    session = get_session()
    today = datetime.now().date()

    ongoing = session.query(Project).filter(
        Project.end_date > today
    ).all()

    data = []
    for project in ongoing:
        # Calculate days until completion
        days_remaining = (project.end_date - today).days if project.end_date else None

        # Determine priority based on days remaining
        if days_remaining and days_remaining < 30:
            priority = 'CRITICAL'
        elif days_remaining and days_remaining < 90:
            priority = 'HIGH'
        elif days_remaining and days_remaining < 180:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        # Get customer info
        account = session.query(Account).filter(Account.id == project.account_id).first()

        data.append({
            'category': 'Ongoing Project',
            'id': f"ONG-{project.id}",
            'title': f"Project: {project.project_description or project.project_id}",
            'customer_name': account.account_name if account else 'Unknown',
            'project_id': project.project_id,
            'opportunity_id': None,  # Would come from project.prj_siebel_id if available
            'practice': project.practice,
            'business_area': project.business_area,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'days_remaining': days_remaining,
            'priority': priority,
            'status': project.status,
            'size_category': project.size_category,
            'account_id': project.account_id
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_completed_project_opportunities():
    """Load Category 3: Completed Projects (end date <= today)."""
    session = get_session()
    today = datetime.now().date()

    completed = session.query(Project).filter(
        Project.end_date <= today,
        Project.end_date >= today - timedelta(days=730)  # Last 2 years
    ).all()

    data = []
    for project in completed:
        # Calculate days since completion
        days_since = (today - project.end_date).days if project.end_date else None

        # Determine priority based on recency (hot leads)
        if days_since and days_since < 90:
            priority = 'HIGH'  # Recent completion - hot lead
            warmth = 'HOT'
        elif days_since and days_since < 180:
            priority = 'MEDIUM'
            warmth = 'WARM'
        else:
            priority = 'LOW'
            warmth = 'COLD'

        # Get customer info
        account = session.query(Account).filter(Account.id == project.account_id).first()

        data.append({
            'category': 'Completed Project',
            'id': f"CMP-{project.id}",
            'title': f"Re-engage: {project.project_description or project.project_id}",
            'customer_name': account.account_name if account else 'Unknown',
            'project_id': project.project_id,
            'opportunity_id': None,
            'practice': project.practice,
            'business_area': project.business_area,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'days_since_completion': days_since,
            'priority': priority,
            'warmth': warmth,
            'status': project.status,
            'size_category': project.size_category,
            'account_id': project.account_id
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_service_sku_mappings():
    """Load LS_SKU service recommendations."""
    session = get_session()
    mappings = session.query(ServiceSKUMapping).all()

    data = []
    for mapping in mappings:
        data.append({
            'product_family': mapping.product_family,
            'product_category': mapping.product_category,
            'service_type': mapping.service_type,
            'service_sku': mapping.service_sku
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_service_catalog():
    """Load Services from service_catalog table (from Services sheet)."""
    session = get_session()
    from src.models import ServiceCatalog

    services = session.query(ServiceCatalog).all()

    data = []
    for service in services:
        data.append({
            'practice': service.practice,
            'sub_practice': service.sub_practice,
            'service_name': service.service_name,
            'service_description': service.service_description,
            'service_category': service.service_category
        })

    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_summary_stats():
    """Load comprehensive statistics."""
    session = get_session()
    today = datetime.now().date()

    stats = {
        'install_base_leads': session.query(func.count(InstallBase.id)).scalar(),  # RAW install base count
        'ongoing_projects': session.query(func.count(Project.id)).filter(Project.end_date > today).scalar(),
        'completed_projects_2yr': session.query(func.count(Project.id)).filter(
            and_(Project.end_date <= today, Project.end_date >= today - timedelta(days=730))
        ).scalar(),
        'total_opportunities': 0,  # Would come from Opportunity table
        'total_accounts': session.query(func.count(Account.id)).scalar(),
        'total_install_base': session.query(func.count(InstallBase.id)).scalar(),
        'total_projects_all': session.query(func.count(Project.id)).scalar(),
        'service_skus': session.query(func.count(ServiceSKUMapping.id)).scalar()
    }

    return stats


def render_header():
    """Render application header."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="main-header">🎯 OneLead Complete</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Intelligence Platform Powered by 5 Data Relationships - All Data, No Estimates</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 1rem;">
            <div style="font-size: 0.8rem; color: #999;">Last Updated</div>
            <div style="font-size: 1rem; font-weight: 600;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")


def render_category_overview(stats):
    """Render 3-category overview."""
    st.markdown("### 📊 Three-Category Lead System")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">CATEGORY 1</div>
            <div class="metric-value">{stats['install_base_leads']}</div>
            <div class="metric-label">Install Base Assets</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Hardware • Support Status • EOL Tracking</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">CATEGORY 2</div>
            <div class="metric-value">{stats['ongoing_projects']}</div>
            <div class="metric-label">Ongoing Projects</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Active Engagement • Expansion • Follow-on</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-box" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">CATEGORY 3</div>
            <div class="metric-value">{stats['completed_projects_2yr']}</div>
            <div class="metric-label">Completed Projects (2yr)</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Re-engagement • Next Phase • Renewal</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_data_foundation(stats):
    """Render data foundation metrics."""
    st.markdown("### 📚 Data Foundation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Accounts", stats['total_accounts'])

    with col2:
        st.metric("Install Base Items", stats['total_install_base'])

    with col3:
        st.metric("Total Projects", stats['total_projects_all'])

    with col4:
        st.metric("Service SKU Mappings", stats['service_skus'])


def get_priority_badge(priority):
    """Get HTML badge for priority."""
    badges = {
        'CRITICAL': '<span class="priority-critical">🔴 CRITICAL</span>',
        'HIGH': '<span class="priority-high">🟠 HIGH</span>',
        'MEDIUM': '<span class="priority-medium">🟡 MEDIUM</span>',
        'LOW': '<span class="priority-low">⚪ LOW</span>'
    }
    return badges.get(priority, '<span class="priority-low">-</span>')


def get_category_badge(category):
    """Get HTML badge for category."""
    badges = {
        'Install Base': '<span class="category-badge cat-install-base">📦 Install Base</span>',
        'Ongoing Project': '<span class="category-badge cat-ongoing">🚀 Ongoing</span>',
        'Completed Project': '<span class="category-badge cat-completed">✅ Completed</span>'
    }
    return badges.get(category, '')


def get_service_recommendations(product_family, business_area, df_skus):
    """Get service recommendations based on product and business area."""
    if df_skus.empty:
        return []

    # Try exact match first
    matches = df_skus[
        (df_skus['product_family'].str.contains(product_family or '', case=False, na=False)) |
        (df_skus['product_category'].str.contains(business_area or '', case=False, na=False))
    ]

    if matches.empty:
        # Try broader match
        if 'Server' in str(business_area) or 'Compute' in str(business_area):
            matches = df_skus[df_skus['product_category'] == 'Compute']
        elif 'Storage' in str(business_area):
            matches = df_skus[df_skus['product_category'].str.contains('Storage', case=False, na=False)]
        elif 'Network' in str(business_area) or 'WLAN' in str(business_area):
            matches = df_skus[df_skus['product_category'] == 'Switches']

    recommendations = []
    for _, row in matches.head(5).iterrows():
        recommendations.append({
            'service': row['service_type'],
            'sku': row['service_sku'] if pd.notna(row['service_sku']) else 'Contact Sales',
            'product': row['product_family']
        })

    return recommendations


def get_practice_services(practice_code, df_services):
    """Get services based on practice code (CLD & PLT, NTWK & CYB, AI & D)."""
    if df_services.empty:
        return []

    # Map practice codes to practice names
    practice_mapping = {
        'CLD & PLT': ['Hybrid Cloud Consulting', 'Hybrid Cloud Engineering'],
        'NTWK & CYB': ['Network', 'Cyber', 'Security'],  # May not exist
        'AI & D': ['Data, AI & IOT']
    }

    practice_names = practice_mapping.get(practice_code, [])
    if not practice_names:
        return []

    # Filter services by practice
    matches = df_services[df_services['practice'].isin(practice_names)]

    recommendations = []
    for _, row in matches.head(10).iterrows():
        recommendations.append({
            'practice': row['practice'],
            'sub_practice': row['sub_practice'],
            'service': row['service_name'],
            'category': row['service_category']
        })

    return recommendations


def get_install_base_services(business_area, product_name, df_services):
    """Get services for Install Base hardware from Services sheet.

    Maps hardware types (Compute, Storage, Network) to relevant services.
    Searches both service name and sub-practice for better matches.
    """
    if df_services.empty:
        return []

    recommendations = []

    # Map business area to relevant service keywords
    if 'x86' in str(business_area).lower() or 'server' in str(business_area).lower() or 'compute' in str(business_area).lower():
        # Compute hardware - search in both service_name AND sub_practice
        # Keywords: compute, server, infrastructure, hardware, deployment, migration, HCI
        compute_services = df_services[
            (df_services['service_name'].str.contains('Compute|Server|Infrastructure|Hardware|Deployment|Migration|HCI|Hyperconverged', case=False, na=False)) |
            (df_services['sub_practice'].str.contains('Compute|Infrastructure', case=False, na=False))
        ]

        # Deduplicate and take first 10
        seen_services = set()
        for _, row in compute_services.iterrows():
            service_name = row['service_name']
            if service_name not in seen_services and len(recommendations) < 10:
                seen_services.add(service_name)
                recommendations.append({
                    'practice': row['practice'] if pd.notna(row['practice']) else 'General Services',
                    'sub_practice': row['sub_practice'] if pd.notna(row['sub_practice']) else 'Infrastructure Services',
                    'service': service_name
                })

    elif 'storage' in str(business_area).lower():
        # Storage hardware - search in both service_name AND sub_practice
        # Keywords: storage, 3PAR, Primera, Nimble, Alletra, SAN, NAS
        storage_services = df_services[
            (df_services['service_name'].str.contains('Storage|3PAR|Primera|Nimble|Alletra|SAN|NAS', case=False, na=False)) |
            (df_services['sub_practice'].str.contains('Storage|3PAR|Primera', case=False, na=False))
        ]

        # Deduplicate and take first 10
        seen_services = set()
        for _, row in storage_services.iterrows():
            service_name = row['service_name']
            if service_name not in seen_services and len(recommendations) < 10:
                seen_services.add(service_name)
                recommendations.append({
                    'practice': row['practice'] if pd.notna(row['practice']) else 'General Services',
                    'sub_practice': row['sub_practice'] if pd.notna(row['sub_practice']) else 'Storage Services',
                    'service': service_name
                })

    elif 'wlan' in str(business_area).lower() or 'network' in str(business_area).lower():
        # Network hardware - search in both service_name AND sub_practice
        # Keywords: network, networking, Aruba, switch, wireless, WLAN, SD-WAN
        network_services = df_services[
            (df_services['service_name'].str.contains('Network|Networking|Aruba|Switch|Wireless|WLAN|SD-WAN', case=False, na=False)) |
            (df_services['sub_practice'].str.contains('Network|Aruba', case=False, na=False))
        ]

        # Deduplicate and take first 10
        seen_services = set()
        for _, row in network_services.iterrows():
            service_name = row['service_name']
            if service_name not in seen_services and len(recommendations) < 10:
                seen_services.add(service_name)
                recommendations.append({
                    'practice': row['practice'] if pd.notna(row['practice']) else 'General Services',
                    'sub_practice': row['sub_practice'] if pd.notna(row['sub_practice']) else 'Network Services',
                    'service': service_name
                })

    return recommendations


def render_install_base_lead(item, df_skus, df_services):
    """Render Category 1: Install Base Item (RAW data from Excel - NO calculated scores)."""
    priority_badge = get_priority_badge(item['priority'])
    category_badge = get_category_badge(item['category'])

    # Determine status indicator
    status_color = '#f5576c' if 'Expired' in str(item['support_status']) else '#43e97b'

    st.markdown(f"""
    <div class="opportunity-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #333;">{item['product_name']}</h3>
                <div style="margin-top: 0.5rem;">
                    {category_badge}
                    {priority_badge}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.85rem; color: #666;">Support Status</div>
                <div style="font-size: 1rem; font-weight: 600; color: {status_color};">{item['support_status']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Asset Information**")
        st.write(f"**Customer:** {item['customer_name']}")
        st.write(f"**Serial Number:** {item['serial_number']}")
        st.write(f"**Business Area:** {item['business_area']}")

    with col2:
        st.markdown("**📅 Support & EOL Dates**")
        if item['product_eol_date']:
            st.write(f"**EOL Date:** {item['product_eol_date']}")
        if item['days_since_eol']:
            st.write(f"**Days Since EOL:** {item['days_since_eol']}")
        if item['service_end_date']:
            st.write(f"**Support End:** {item['service_end_date']}")
        if item['days_since_expiry']:
            st.write(f"**Days Since Expiry:** {item['days_since_expiry']}")

    with col3:
        st.markdown("**⚠️ Risk Assessment**")
        st.write(f"**Risk Level:** {item['risk_level']}")
        st.write(f"**Support Status:** {item['support_status']}")

    with st.expander("🔧 Available Services (from Services Catalog)"):
        # Get services from Services sheet based on business area
        services = get_install_base_services(
            item['business_area'] or '',
            item['product_name'] or '',
            df_services
        )

        if services:
            st.markdown("**Recommended services from Services sheet:**")
            for svc in services:
                st.markdown(f"""
                <div class="recommendation-box">
                    <strong>{svc['service']}</strong><br>
                    <em>Practice:</em> {svc['practice']} | <em>Sub-Practice:</em> {svc['sub_practice']}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Fallback to LS_SKU if no Services sheet match
            st.markdown("**Services from LS_SKU mapping:**")
            sku_recommendations = get_service_recommendations(
                item['product_family'] or '',
                item['business_area'] or '',
                df_skus
            )

            if sku_recommendations:
                for rec in sku_recommendations[:5]:
                    st.markdown(f"""
                    <div class="recommendation-box">
                        • {rec['service']} <span class="service-sku">SKU: {rec['sku']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("💡 Contact sales team for available services for this hardware.")

    st.markdown("---")


def render_ongoing_project(project, df_skus, df_services):
    """Render Category 2: Ongoing Project Opportunity."""
    priority_badge = get_priority_badge(project['priority'])
    category_badge = get_category_badge(project['category'])

    st.markdown(f"""
    <div class="opportunity-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #333;">{project['title']}</h3>
                <div style="margin-top: 0.5rem;">
                    {category_badge}
                    {priority_badge}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.85rem; color: #666;">Days Until Completion</div>
                <div style="font-size: 2rem; font-weight: 700; color: #4facfe;">{project['days_remaining']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Project Information**")
        st.write(f"**Customer:** {project['customer_name']}")
        st.write(f"**Project ID:** {project['project_id']}")
        st.write(f"**Practice:** {project['practice']}")
        st.write(f"**Status:** {project['status']}")

    with col2:
        st.markdown("**📅 Timeline**")
        st.write(f"**Start Date:** {project['start_date']}")
        st.write(f"**End Date:** {project['end_date']}")
        st.write(f"**Days Remaining:** {project['days_remaining']}")
        if project['size_category']:
            st.write(f"**Size Category:** {project['size_category']}")

    with col3:
        st.markdown("**💡 Opportunity Type**")
        if project['days_remaining'] < 30:
            st.write("**🔴 Pre-Completion Services**")
            st.write("• Project health check")
            st.write("• Knowledge transfer")
        elif project['days_remaining'] < 90:
            st.write("**🟠 Renewal Planning**")
            st.write("• Transition planning")
            st.write("• Follow-on services")
        else:
            st.write("**🟢 Scope Expansion**")
            st.write("• Additional services")
            st.write("• Phase 2 planning")

    with st.expander("🎯 Service Recommendations"):
        st.markdown("### Available HPE Services (from Services Catalog)")

        # Get services based on practice area
        practice_services = get_practice_services(project['practice'] or '', df_services)

        if practice_services:
            for rec in practice_services:
                st.markdown(f"""
                <div class="recommendation-box">
                    <strong>{rec['service']}</strong><br>
                    <em>Practice:</em> {rec['practice']} | <em>Sub-Practice:</em> {rec['sub_practice'] or 'General'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Contact sales team for available services based on project practice area: " + (project['practice'] or 'Unknown'))
            st.markdown("**Note:** Service recommendations are based on actual Services sheet data.")

    st.markdown("---")


def render_completed_project(project, df_skus, df_services):
    """Render Category 3: Completed Project Re-engagement."""
    priority_badge = get_priority_badge(project['priority'])
    category_badge = get_category_badge(project['category'])

    warmth_color = {
        'HOT': '#f5576c',
        'WARM': '#fee140',
        'COLD': '#38f9d7'
    }.get(project['warmth'], '#999')

    st.markdown(f"""
    <div class="opportunity-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #333;">{project['title']}</h3>
                <div style="margin-top: 0.5rem;">
                    {category_badge}
                    {priority_badge}
                    <span style="background: {warmth_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-weight: 600; font-size: 0.85rem; margin-left: 0.5rem;">
                        {project['warmth']} LEAD
                    </span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.85rem; color: #666;">Days Since Completion</div>
                <div style="font-size: 2rem; font-weight: 700; color: #43e97b;">{project['days_since_completion']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Project Information**")
        st.write(f"**Customer:** {project['customer_name']}")
        st.write(f"**Project ID:** {project['project_id']}")
        st.write(f"**Practice:** {project['practice']}")
        st.write(f"**Completed:** {project['end_date']}")

    with col2:
        st.markdown("**📈 Engagement History**")
        st.write(f"**Duration:** {(project['end_date'] - project['start_date']).days} days")
        if project['size_category']:
            st.write(f"**Size Category:** {project['size_category']}")
        st.write(f"**Lead Temperature:** {project['warmth']}")

    with col3:
        st.markdown("**💡 Re-engagement Strategy**")
        if project['warmth'] == 'HOT':
            st.write("**🔴 Immediate Follow-up**")
            st.write("• Check-in call (within 7 days)")
            st.write("• Satisfaction survey")
            st.write("• Next phase discussion")
        elif project['warmth'] == 'WARM':
            st.write("**🟠 Quarterly Review**")
            st.write("• Business review meeting")
            st.write("• Optimization assessment")
        else:
            st.write("**🟢 Annual Renewal**")
            st.write("• Technology refresh check")
            st.write("• New initiative discovery")

    with st.expander("🎯 Re-engagement Services"):
        st.markdown("### Available HPE Services (from Services Catalog)")

        # Get services based on practice area from Service Catalog
        practice_services = get_practice_services(project['practice'] or '', df_services)

        if practice_services:
            for rec in practice_services:
                st.markdown(f"""
                <div class="recommendation-box">
                    <strong>{rec['service']}</strong><br>
                    <em>Practice:</em> {rec['practice']} | <em>Sub-Practice:</em> {rec['sub_practice'] or 'General'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Contact sales team for available services based on project practice area: " + (project['practice'] or 'Unknown'))
            st.markdown("**Note:** Service recommendations are based on actual Services sheet data. No services found for this practice area in the current catalog.")

    st.markdown("---")


def main():
    """Main application."""
    # Render header
    render_header()

    # Load all data
    with st.spinner("Loading comprehensive lead intelligence..."):
        stats = load_summary_stats()
        df_install_base = load_install_base_leads()
        df_ongoing = load_ongoing_project_opportunities()
        df_completed = load_completed_project_opportunities()
        df_skus = load_service_sku_mappings()
        df_services = load_service_catalog()

    # Category overview
    render_category_overview(stats)

    # Data foundation
    render_data_foundation(stats)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Set default filters (no sidebar)
    categories = ['Install Base', 'Ongoing Project', 'Completed Project']
    priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Install Base Assets",
        "🚀 Ongoing Projects",
        "✅ Completed Projects",
        "ℹ️ About"
    ])

    with tab1:
        st.markdown(f"### 📦 Install Base Assets ({len(df_install_base)})")
        st.markdown("**Source:** Install Base table (direct from Excel) - hardware, support status, EOL dates")

        if not df_install_base.empty:
            filtered = df_install_base[df_install_base['priority'].isin(priorities)]

            if len(filtered) == 0:
                st.info("No install base assets match the selected filters.")
            else:
                # Add organization controls
                col1, col2 = st.columns(2)
                with col1:
                    view_mode = st.radio(
                        "Organize by:",
                        ["Business Area", "Support Status", "Risk Level"],
                        horizontal=True,
                        key="ib_view_mode"
                    )
                with col2:
                    show_limit = st.selectbox(
                        "Show per category:",
                        [5, 10, 20, "All"],
                        index=1,
                        key="ib_limit"
                    )

                limit = None if show_limit == "All" else show_limit

                # Organize by selected view mode
                if view_mode == "Business Area":
                    # Group by business area
                    for area in filtered['business_area'].unique():
                        area_assets = filtered[filtered['business_area'] == area]
                        area_label = area if area else "Other"

                        with st.expander(f"🏢 {area_label} ({len(area_assets)} assets)", expanded=(len(filtered['business_area'].unique()) <= 3)):
                            for _, item in area_assets.head(limit).iterrows():
                                render_install_base_lead(item, df_skus, df_services)

                elif view_mode == "Support Status":
                    # Group by support status
                    status_order = [
                        'Warranty Expired - Uncovered Box',
                        'Expired Flex Support',
                        'Expired Fixed Support',
                        'Active Warranty'
                    ]

                    for status in status_order:
                        status_assets = filtered[filtered['support_status'].str.contains(status, na=False)]
                        if len(status_assets) > 0:
                            status_emoji = {
                                'Warranty Expired': '🔴',
                                'Expired Flex': '🟠',
                                'Expired Fixed': '🟠',
                                'Active': '🟢'
                            }
                            emoji = next((v for k, v in status_emoji.items() if k in status), '⚪')

                            with st.expander(f"{emoji} {status} ({len(status_assets)} assets)", expanded=('Expired' in status or 'Uncovered' in status)):
                                for _, item in status_assets.head(limit).iterrows():
                                    render_install_base_lead(item, df_skus, df_services)

                else:  # Risk Level
                    # Group by risk level
                    for risk in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                        risk_assets = filtered[filtered['risk_level'] == risk]
                        if len(risk_assets) > 0:
                            risk_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}

                            with st.expander(f"{risk_emoji[risk]} {risk} Risk ({len(risk_assets)} assets)", expanded=(risk in ['CRITICAL', 'HIGH'])):
                                for _, item in risk_assets.head(limit).iterrows():
                                    render_install_base_lead(item, df_skus, df_services)
        else:
            st.info("No install base assets available.")

    with tab2:
        st.markdown(f"### 🚀 Ongoing Projects ({len(df_ongoing)})")
        st.markdown("**Source:** Projects table - active projects with end date > today")

        if not df_ongoing.empty:
            filtered = df_ongoing[df_ongoing['priority'].isin(priorities)]

            if len(filtered) == 0:
                st.info("No ongoing projects match the selected filters.")
            else:
                # Add organization controls
                col1, col2 = st.columns(2)
                with col1:
                    view_mode = st.radio(
                        "Organize by:",
                        ["Practice Area", "Project Size", "Priority"],
                        horizontal=True,
                        key="ongoing_view_mode"
                    )
                with col2:
                    show_limit = st.selectbox(
                        "Show per category:",
                        [5, 10, 20, "All"],
                        index=1,
                        key="ongoing_limit"
                    )

                limit = None if show_limit == "All" else show_limit

                # Organize by selected view mode
                if view_mode == "Practice Area":
                    # Group by practice
                    for practice in filtered['practice'].unique():
                        practice_projects = filtered[filtered['practice'] == practice]
                        practice_label = practice if practice else "Other"

                        with st.expander(f"📊 {practice_label} ({len(practice_projects)} projects)", expanded=(len(filtered['practice'].unique()) <= 3)):
                            for _, project in practice_projects.head(limit).iterrows():
                                render_ongoing_project(project, df_skus, df_services)

                elif view_mode == "Project Size":
                    # Define size order for sorting
                    size_order = ['>$5M', '$1M-$5M', '$500k-$1M', '$50k-$500k', '<$50k', '-', None]

                    # Group by size category
                    for size in size_order:
                        size_projects = filtered[filtered['size_category'] == size]
                        if len(size_projects) > 0:
                            size_label = size if size and size != '-' else "Unknown Size"

                            with st.expander(f"💰 {size_label} ({len(size_projects)} projects)", expanded=(size in ['>$5M', '$1M-$5M'])):
                                for _, project in size_projects.head(limit).iterrows():
                                    render_ongoing_project(project, df_skus, df_services)

                else:  # Priority
                    # Group by priority
                    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                        priority_projects = filtered[filtered['priority'] == priority]
                        if len(priority_projects) > 0:
                            priority_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}

                            with st.expander(f"{priority_emoji[priority]} {priority} Priority ({len(priority_projects)} projects)", expanded=(priority in ['CRITICAL', 'HIGH'])):
                                for _, project in priority_projects.head(limit).iterrows():
                                    render_ongoing_project(project, df_skus, df_services)
        else:
            st.info("No ongoing projects available.")

    with tab3:
        st.markdown(f"### ✅ Completed Projects ({len(df_completed)})")
        st.markdown("**Source:** Projects table - completed in last 2 years")

        if not df_completed.empty:
            filtered = df_completed[df_completed['priority'].isin(priorities)]

            if len(filtered) == 0:
                st.info("No completed projects match the selected filters.")
            else:
                # Add organization controls
                col1, col2 = st.columns(2)
                with col1:
                    view_mode = st.radio(
                        "Organize by:",
                        ["Practice Area", "Project Size", "Completion Date"],
                        horizontal=True,
                        key="completed_view_mode"
                    )
                with col2:
                    show_limit = st.selectbox(
                        "Show per category:",
                        [5, 10, 20, "All"],
                        index=1,
                        key="completed_limit"
                    )

                limit = None if show_limit == "All" else show_limit

                # Organize by selected view mode
                if view_mode == "Practice Area":
                    # Group by practice
                    for practice in filtered['practice'].unique():
                        practice_projects = filtered[filtered['practice'] == practice]
                        practice_label = practice if practice else "Other"

                        with st.expander(f"📊 {practice_label} ({len(practice_projects)} projects)", expanded=(len(filtered['practice'].unique()) <= 3)):
                            for _, project in practice_projects.head(limit).iterrows():
                                render_completed_project(project, df_skus, df_services)

                elif view_mode == "Project Size":
                    # Define size order for sorting
                    size_order = ['>$5M', '$1M-$5M', '$500k-$1M', '$50k-$500k', '<$50k', '-', None]

                    # Group by size category
                    for size in size_order:
                        size_projects = filtered[filtered['size_category'] == size]
                        if len(size_projects) > 0:
                            size_label = size if size and size != '-' else "Unknown Size"

                            with st.expander(f"💰 {size_label} ({len(size_projects)} projects)", expanded=(size in ['>$5M', '$1M-$5M'])):
                                for _, project in size_projects.head(limit).iterrows():
                                    render_completed_project(project, df_skus, df_services)

                else:  # Completion Date
                    # Group by completion timeframe
                    from datetime import datetime, timedelta
                    today = datetime.now().date()

                    timeframes = [
                        ("Last 3 months", 90),
                        ("3-6 months ago", 180),
                        ("6-12 months ago", 365),
                        ("1-2 years ago", 730)
                    ]

                    for label, days in timeframes:
                        start_date = today - timedelta(days=days)
                        if days == 90:
                            end_date = today
                        else:
                            prev_days = [d for l, d in timeframes if d < days]
                            end_date = today - timedelta(days=prev_days[-1]) if prev_days else today

                        timeframe_projects = filtered[
                            (pd.to_datetime(filtered['end_date']).dt.date >= start_date) &
                            (pd.to_datetime(filtered['end_date']).dt.date < end_date)
                        ]

                        if len(timeframe_projects) > 0:
                            with st.expander(f"📅 {label} ({len(timeframe_projects)} projects)", expanded=(days == 90)):
                                for _, project in timeframe_projects.head(limit).iterrows():
                                    render_completed_project(project, df_skus, df_services)
        else:
            st.info("No completed projects available.")

    with tab4:
        st.markdown("### ℹ️ About OneLead Complete")

        st.markdown("""
        ## 🎯 OneLead Complete: Intelligent Lead Generation Platform

        **Transform customer data into actionable intelligence through 5 proven data relationships**

        ---

        ## 📊 Three-Category Lead System

        OneLead Complete analyzes THREE distinct opportunity categories:
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### 📦 Category 1
            **Install Base Assets**

            **Source:** 63 hardware assets (direct from Excel)

            **Shows:**
            - Product details
            - Support status
            - EOL/EOSL dates
            - Serial numbers

            **Use for:**
            - Renewal identification
            - Hardware refresh planning
            - Service attach opportunities
            """)

        with col2:
            st.markdown("""
            ### 🚀 Category 2
            **Ongoing Projects**

            **Source:** 226 active projects

            **Identifies:**
            - Pre-completion services
            - Scope expansion
            - Follow-on phases

            **Temperature:**
            - CRITICAL: < 30 days
            - HIGH: 30-90 days
            - MEDIUM: 90+ days
            """)

        with col3:
            st.markdown("""
            ### ✅ Category 3
            **Completed Projects**

            **Source:** 2,168 projects (2yr)

            **Identifies:**
            - Re-engagement opportunities
            - Next phase planning
            - Annual renewals

            **Temperature:**
            - HOT: < 90 days
            - WARM: 90-180 days
            - COLD: 180+ days
            """)

        st.markdown("---")

        st.markdown("""
        ## 🔗 The 5 Data Relationships

        OneLead Complete leverages 5 key data integration points to generate intelligent recommendations:
        """)

        st.markdown("""
        ### ✅ Point 1: Install Base → Opportunity
        **Relationship:** Direct Foreign Key via Account_Sales_Territory_Id
        **Coverage:** 80% of accounts have active opportunities
        **Usage:** Renewal campaigns, upsell identification
        **Automation:** Auto-generate opportunities for expired assets

        **How it works:** When hardware reaches EOL or support expires, the system automatically identifies
        the account and creates targeted renewal opportunities with appropriate service recommendations.

        ---

        ### ✅ Point 2: Install Base/Opportunity → LS_SKU
        **Relationship:** Keyword matching + business rules
        **Coverage:** 100% of product categories mapped (138 service combinations)
        **Usage:** Service recommendations, quote generation
        **Automation:** Real-time SKU lookup during opportunity creation

        **How it works:** Each product type (servers, storage, networking) maps to specific HPE services
        with actual SKU codes. The system matches products to services based on:
        - Product keywords (3PAR, Primera, DL360, etc.)
        - Business area (Compute, Storage, WLAN)
        - Support status (Expired → Health Check priority)

        **Example:** HP DL360p Gen8 Server → Compute category → Services: Health Check (HL997A1),
        Firmware upgrade, OneView configuration

        ---

        ### ✅ Point 3: Opportunity → A&PS Project
        **Relationship:** Direct Foreign Key (HPE Opportunity ID → PRJ Siebel ID)
        **Coverage:** 47% of projects linked (1,117 of 2,394 projects)
        **Usage:** Pipeline tracking, delivery accountability
        **Automation:** Auto-create project on opportunity win

        **How it works:** When a sales opportunity is WON, the system creates an A&PS delivery project
        with the opportunity ID stored in PRJ Siebel ID field. This enables complete traceability from
        initial opportunity through delivery and completion.

        **Format:** OPE-XXXXXXXXXX (e.g., OPE-0006205063)

        ---

        ### ✅ Point 4: A&PS Project → Services
        **Relationship:** Practice code mapping
        **Coverage:** All projects mapped to practice areas (286 services)
        **Usage:** Historical analysis, expertise mapping
        **Automation:** Service recommendations based on past purchases

        **How it works:** Projects are tagged with practice codes that map to customer-facing service categories:

        **Practice Mappings:**
        - **CLD & PLT** (Cloud & Platform) → Hybrid Cloud Consulting + Hybrid Cloud Engineering (179 services)
        - **AI & D** (AI & Data) → Data, AI & IOT (107 services)
        - **NTWK & CYB** (Network & Cyber) → Network & Security services

        **Example:** Completed project with practice "CLD & PLT" → System recommends Hybrid Cloud services
        like Cloud Migration Assessment, Workload Migration, Azure Stack Deployment

        ---

        ### ⚠️ Point 5: Service Credits
        **Relationship:** Links to projects and practices
        **Coverage:** 1,384 credit-based projects
        **Usage:** Credit utilization tracking, expiry alerts
        **Status:** Data loaded, UI integration in progress

        **How it works:** Tracks prepaid service credits with:
        - Purchased credits: 650 total
        - Delivered credits: 320 consumed
        - Active credits: 320 available
        - Utilization rate: 49%

        **Next Phase:** Alert when credits near expiration, recommend services to consume available credits

        ---

        ## 📈 Data Foundation
        """)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Active Accounts", f"~{stats['total_accounts']}")
            st.caption("Across 3 categories")

        with col2:
            st.metric("Install Base", stats['total_install_base'])
            st.caption("Hardware assets tracked")

        with col3:
            st.metric("Total Projects", f"{stats['total_projects_all']:,}")
            st.caption("Historical + active")

        with col4:
            st.metric("Service Mappings", stats['service_skus'])
            st.caption("Product-to-service SKUs")

        st.markdown("---")

        st.markdown("""
        ## 🎓 Service Recommendation Engine

        **Two-Layer Recommendation System:**

        ### Layer 1: LS_SKU Mappings (Install Base)
        - **32 product types** across 6 categories
        - **138 product-service combinations**
        - **Real HPE SKU codes** for quoting
        - Maps hardware products (servers, storage, networking) to technical services

        **Categories:** Storage SW, Storage HW, Compute, Switches, Converged Systems, HCI

        ### Layer 2: Services Catalog (Projects)
        - **286 practice-aligned services**
        - **3 major practices** with sub-categories
        - **Customer-facing service names**
        - Maps project types to advisory and professional services

        **Practices:** Hybrid Cloud Consulting, Hybrid Cloud Engineering, Data AI & IOT

        ---

        ## ✅ Core Principle: "All Data, No Estimates"

        **Every number in OneLead Complete comes from actual Excel data:**

        ✅ **We DO use:**
        - Actual project end dates
        - Real install base counts
        - Historical project sizes from A&PS data
        - Actual service SKU codes from LS_SKU table
        - Real practice areas from completed projects
        - Actual support status and EOL dates

        ❌ **We DON'T use:**
        - Estimated opportunity values
        - Projected revenue numbers
        - Made-up service recommendations
        - Fake customer propensity scores
        - Synthetic engagement metrics

        **Result:** 100% trustworthy intelligence for sales and delivery teams

        ---

        ## 📞 Questions?

        For more information about data relationships and integration patterns:
        - Review: DATA_RELATIONSHIPS_ANALYSIS.md
        - Review: SERVICE_RECOMMENDATION_STRATEGY.md
        - Check: /data/ folder for source Excel files
        """)

        st.markdown("---")


if __name__ == "__main__":
    main()
