"""OneLead Business Intelligence Dashboard - Narrative-Driven."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func, case
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
    initial_sidebar_state="collapsed"
)

# Custom CSS for storytelling
st.markdown("""
<style>
    .big-insight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin: 20px 0;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    .story-card {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #667eea;
    }

    .story-card h3 {
        color: #667eea;
        margin-top: 0;
        font-size: 22px;
    }

    .story-card p {
        font-size: 16px;
        line-height: 1.6;
        color: #4a5568;
    }

    .risk-alert {
        background: #fff5f5;
        border-left: 5px solid #ff4444;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .opportunity-highlight {
        background: #f0fff4;
        border-left: 5px solid #00C851;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .action-needed {
        background: #fffbeb;
        border-left: 5px solid #ff9933;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .metric-large {
        font-size: 48px;
        font-weight: 800;
        color: #667eea;
        margin: 10px 0;
    }

    .metric-context {
        font-size: 16px;
        color: #6c757d;
        margin-bottom: 20px;
    }

    .priority-list {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }

    .priority-item {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .insight-number {
        display: inline-block;
        background: #667eea;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: bold;
        margin-right: 10px;
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

# Calculate all metrics
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

# At-risk equipment
at_risk_equipment = session.query(func.count(InstallBase.id)).filter(
    InstallBase.risk_level.in_(['CRITICAL', 'HIGH'])
).scalar()

# Expiring support
expired_support = session.query(func.count(InstallBase.id)).filter(
    InstallBase.support_status.like('%Expired%')
).scalar()

# ========================================
# MAIN PAGE - THE STORY
# ========================================

# Hero section - The Big Picture
st.markdown(f"""
<div class="big-insight">
    💰 ${total_pipeline/1e6:.1f}M in Revenue Opportunity Identified
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Executive Summary
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="metric-large">{critical_leads + high_leads}</div>
        <div class="metric-context">High-Value Opportunities</div>
        <p style="font-size: 14px; color: #6c757d;">Ready to close in 30-90 days</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="metric-large">{expired_support}</div>
        <div class="metric-context">Customers Without Support</div>
        <p style="font-size: 14px; color: #6c757d;">Critical risk & immediate revenue</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="metric-large">{at_risk_equipment}</div>
        <div class="metric-context">End-of-Life Systems</div>
        <p style="font-size: 14px; color: #6c757d;">Hardware refresh opportunities</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# The Story - What's Happening
st.markdown("## 📖 What's Happening in Your Territory")

# Critical insights
critical_leads_list = session.query(Lead).filter(
    Lead.is_active == True,
    Lead.priority == 'CRITICAL'
).order_by(Lead.score.desc()).limit(3).all()

if critical_leads_list:
    st.markdown(f"""
    <div class="risk-alert">
        <h3 style="color: #ff4444; margin-top: 0;">⚠️ {critical_leads} Critical Situations Require Immediate Attention</h3>
        <p><strong>The Risk:</strong> These customers are running production systems without support.
        Every day we wait increases their risk—and the likelihood they'll turn to a competitor.</p>
        <p><strong>The Opportunity:</strong> These are your easiest wins. Customers already know they need help.
        Average close time: 30 days. Estimated value: ${sum([l.estimated_value_max or 0 for l in critical_leads_list])/1000:.0f}K just from top 3.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Your Top 3 Priorities This Week:")

    for idx, lead in enumerate(critical_leads_list, 1):
        account = session.query(Account).filter(Account.id == lead.account_id).first()
        account_name = format_account(account)
        value = f"${lead.estimated_value_max/1000:.0f}K" if lead.estimated_value_max else "TBD"

        st.markdown(f"""
        <div class="priority-item">
            <span class="insight-number">{idx}</span>
            <strong>{account_name}</strong> - {lead.title}
            <br>
            <span style="color: #6c757d; font-size: 14px;">
                💰 Value: {value} | ⏰ Why Now: {lead.description[:100]}...
            </span>
            <br>
            <strong style="color: #667eea;">→ Next Step:</strong> {lead.recommended_action}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Hardware refresh opportunity
hw_refresh_leads = session.query(Lead).filter(
    Lead.is_active == True,
    Lead.lead_type.like('%Hardware Refresh%')
).all()

if hw_refresh_leads:
    hw_value = sum([l.estimated_value_max or 0 for l in hw_refresh_leads])
    avg_age = session.query(func.avg(InstallBase.days_since_eol)).filter(
        InstallBase.days_since_eol != None,
        InstallBase.days_since_eol > 1825
    ).scalar() or 0

    st.markdown(f"""
    <div class="opportunity-highlight">
        <h3 style="color: #00C851; margin-top: 0;">🚀 ${hw_value/1e6:.1f}M Hardware Refresh Pipeline</h3>
        <p><strong>The Situation:</strong> You have {len(hw_refresh_leads)} customers running equipment that's {avg_age/365:.1f} years past end-of-life.
        Their systems are slow, unreliable, and vulnerable.</p>
        <p><strong>The Pitch:</strong> "Your infrastructure is holding your business back. Modern systems are 3x faster, 50% more energy-efficient,
        and come with AI-powered management. Let's schedule a TCO analysis."</p>
        <p><strong>Average Deal Size:</strong> ${hw_value/len(hw_refresh_leads)/1000:.0f}K per customer</p>
    </div>
    """, unsafe_allow_html=True)

# Service attach opportunity
service_leads = session.query(Lead).filter(
    Lead.is_active == True,
    Lead.lead_type.like('%Service Attach%')
).all()

if service_leads:
    service_value = sum([l.estimated_value_max or 0 for l in service_leads])

    st.markdown(f"""
    <div class="action-needed">
        <h3 style="color: #ff9933; margin-top: 0;">💼 ${service_value/1000:.0f}K in Uncovered Service Revenue</h3>
        <p><strong>The Problem:</strong> {len(service_leads)} customers own HPE equipment but have no service contracts.
        When (not if) something breaks, they'll be scrambling—and might look elsewhere.</p>
        <p><strong>The Solution:</strong> Proactive outreach with a risk assessment offer.
        Frame it as "We noticed your equipment isn't covered. Let's do a free health check to identify any issues before they become emergencies."</p>
        <p><strong>Quick Win:</strong> Service contracts are low-friction sales. Average close time: 2-3 weeks.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Territory Breakdown - Where to Focus
st.markdown("## 🗺️ Where Should You Focus?")

territory_data = session.query(
    Lead.territory_id,
    func.count(Lead.id).label('lead_count'),
    func.sum(Lead.estimated_value_max).label('pipeline'),
    func.sum(case((Lead.priority == 'CRITICAL', 1), else_=0)).label('critical_count')
).filter(
    Lead.is_active == True,
    Lead.territory_id != None
).group_by(Lead.territory_id).order_by(func.sum(Lead.estimated_value_max).desc()).all()

if territory_data:
    territory_map = get_territory_mapping()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💰 Highest Value Territories")
        for idx, (territory, leads, pipeline, critical) in enumerate(territory_data[:5], 1):
            territory_name = territory_map.get(territory, f"Territory {territory}")
            st.markdown(f"""
            <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>{idx}. {territory_name}</strong><br>
                <span style="color: #6c757d;">
                    💰 ${(pipeline or 0)/1e6:.2f}M pipeline |
                    🎯 {leads} opportunities |
                    🚨 {critical} critical
                </span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🚨 Most Urgent Territories")
        urgent_territories = sorted(territory_data, key=lambda x: x[3], reverse=True)[:5]
        for idx, (territory, leads, pipeline, critical) in enumerate(urgent_territories, 1):
            territory_name = territory_map.get(territory, f"Territory {territory}")
            if critical > 0:
                st.markdown(f"""
                <div style="background: #fff5f5; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ff4444;">
                    <strong>{idx}. {territory_name}</strong><br>
                    <span style="color: #6c757d;">
                        🚨 {critical} critical situations |
                        💰 ${(pipeline or 0)/1000:.0f}K value
                    </span><br>
                    <strong style="color: #ff4444;">→ Action: Prioritize immediate outreach</strong>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# Account Stories - Deep Dive
st.markdown("## 👥 Account Spotlight: Who Needs Your Help Most?")

# Find accounts with multiple high-value opportunities
account_summary = session.query(
    Lead.account_id,
    func.count(Lead.id).label('lead_count'),
    func.sum(Lead.estimated_value_max).label('total_value'),
    func.max(Lead.priority).label('highest_priority')
).filter(
    Lead.is_active == True
).group_by(Lead.account_id).order_by(func.sum(Lead.estimated_value_max).desc()).limit(5).all()

for account_id, lead_count, total_value, priority in account_summary:
    if not total_value or total_value < 50000:
        continue

    account = session.query(Account).filter(Account.id == account_id).first()
    account_name = format_account(account)

    account_leads = session.query(Lead).filter(
        Lead.account_id == account_id,
        Lead.is_active == True
    ).all()

    install_base_count = session.query(func.count(InstallBase.id)).filter(
        InstallBase.account_id == account_id
    ).scalar()

    at_risk_count = session.query(func.count(InstallBase.id)).filter(
        InstallBase.account_id == account_id,
        InstallBase.risk_level.in_(['CRITICAL', 'HIGH'])
    ).scalar()

    projects_count = session.query(func.count(Project.id)).filter(
        Project.account_id == account_id
    ).scalar()

    st.markdown(f"""
    <div class="story-card">
        <h3>🏢 {account_name}</h3>
        <p><strong>The Situation:</strong> This customer has {install_base_count} pieces of HPE equipment,
        with {at_risk_count} systems at risk. We've delivered {projects_count} projects for them historically—they trust us.</p>

        <p><strong>The Opportunity:</strong> {lead_count} active opportunities worth ${total_value/1000:.0f}K total:</p>
    """, unsafe_allow_html=True)

    for lead in account_leads[:3]:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 3px solid #667eea;">
            <strong>• {lead.lead_type.split('-')[0].strip()}:</strong> {lead.title}<br>
            <span style="color: #6c757d; font-size: 14px;">
                Value: ${(lead.estimated_value_max or 0)/1000:.0f}K |
                Action: {lead.recommended_action[:80]}...
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <p><strong>Why Act Now:</strong> Their equipment is aging, support is expiring, and competitors are circling.
        Strike while we have the relationship advantage.</p>

        <p><strong>Recommended Approach:</strong> Schedule a business review. Lead with a "health check" of their infrastructure.
        Bundle the opportunities into a comprehensive modernization plan.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# The Numbers (for those who want them)
with st.expander("📊 Show Me the Detailed Numbers"):
    st.markdown("### Pipeline Breakdown")

    col1, col2, col3 = st.columns(3)

    with col1:
        renewal_value = session.query(func.sum(Lead.estimated_value_max)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Renewal%')
        ).scalar() or 0
        renewal_count = session.query(func.count(Lead.id)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Renewal%')
        ).scalar()
        st.metric("Renewal Pipeline", f"${renewal_value/1e6:.2f}M", f"{renewal_count} opportunities")

    with col2:
        hw_value = session.query(func.sum(Lead.estimated_value_max)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Hardware%')
        ).scalar() or 0
        hw_count = session.query(func.count(Lead.id)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Hardware%')
        ).scalar()
        st.metric("Hardware Refresh", f"${hw_value/1e6:.2f}M", f"{hw_count} opportunities")

    with col3:
        service_value = session.query(func.sum(Lead.estimated_value_max)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Service%')
        ).scalar() or 0
        service_count = session.query(func.count(Lead.id)).filter(
            Lead.is_active == True,
            Lead.lead_type.like('%Service%')
        ).scalar()
        st.metric("Service Attach", f"${service_value/1e6:.2f}M", f"{service_count} opportunities")

    st.markdown("### Priority Distribution")
    priority_dist = session.query(
        Lead.priority,
        func.count(Lead.id).label('count'),
        func.sum(Lead.estimated_value_max).label('value')
    ).filter(Lead.is_active == True).group_by(Lead.priority).all()

    df = pd.DataFrame(priority_dist, columns=['Priority', 'Count', 'Value'])
    df['Value'] = df['Value'].fillna(0) / 1e6

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Priority'],
        y=df['Count'],
        name='Count',
        yaxis='y',
        marker_color='#667eea'
    ))
    fig.add_trace(go.Bar(
        x=df['Priority'],
        y=df['Value'],
        name='Value ($M)',
        yaxis='y2',
        marker_color='#764ba2'
    ))

    fig.update_layout(
        yaxis=dict(title='Number of Leads'),
        yaxis2=dict(title='Value ($M)', overlaying='y', side='right'),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

# Action Items
st.markdown("---")
st.markdown("## ✅ Your Action Plan for This Week")

st.markdown("""
<div class="priority-list">
    <div class="priority-item">
        <span class="insight-number">1</span>
        <strong>Monday Morning:</strong> Call the top 3 CRITICAL accounts. Use the script:
        "I noticed your [system] is no longer under support. Can we schedule 15 minutes to discuss coverage options?"
    </div>

    <div class="priority-item">
        <span class="insight-number">2</span>
        <strong>Tuesday-Wednesday:</strong> Email all HIGH priority accounts with a "Free Health Check" offer.
        Include a one-pager showing their at-risk equipment.
    </div>

    <div class="priority-item">
        <span class="insight-number">3</span>
        <strong>Thursday:</strong> Schedule business reviews with your top 5 accounts (by pipeline value).
        Come prepared with their complete install base analysis.
    </div>

    <div class="priority-item">
        <span class="insight-number">4</span>
        <strong>Friday:</strong> Review your win rate this week. Update lead statuses.
        Identify which objections you're hearing and prepare counterarguments.
    </div>
</div>
""", unsafe_allow_html=True)

# Call to action
st.markdown(f"""
<div class="big-insight" style="font-size: 20px; padding: 30px;">
    💪 You have everything you need to close ${total_pipeline/1e6:.1f}M this quarter.
    <br>The leads are warm. The data is solid. Now it's time to execute.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("🎯 OneLead Sales Intelligence • Updated in real-time • Questions? Contact your sales ops team")
