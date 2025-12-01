"""
OneLead - Account Insights & Service Recommendations
Intelligent cross-sell and up-sell recommendations based on install base, projects, and service credits
"""

import streamlit as st
import sys
from pathlib import Path
from sqlalchemy import func

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.base import SessionLocal
from src.models import Account, InstallBase, Project, Opportunity, ServiceCredit
from src.engines.recommendation_engine import RecommendationEngine

# Page configuration
st.set_page_config(
    page_title="OneLead - Account Insights",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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
</style>
""", unsafe_allow_html=True)


def get_session():
    """Get database session."""
    return SessionLocal()


def main():
    """Main application."""
    # Header
    st.markdown('<p class="main-header">🔍 OneLead Account Insights</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Cross-Sell & Up-Sell Recommendations</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Search interface
    st.markdown("### Search Account")
    st.markdown("Search by **Opportunity ID**, **Account ST ID**, or **Account Name** to get intelligent service recommendations")

    search_col1, search_col2 = st.columns([3, 1])

    with search_col1:
        search_query = st.text_input(
            "🔍 Search Account",
            placeholder="Enter Opportunity ID, ST ID (e.g., 56088), or Account Name",
            key="account_search",
            label_visibility="collapsed"
        )

    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("Search", type="primary", use_container_width=True)

    if search_query and search_button:
        session = get_session()
        engine = RecommendationEngine(session)

        # Try to find account by different search methods
        territory_id = None
        search_results = []

        # Search by ST ID (territory_id)
        if search_query.isdigit():
            account = session.query(Account).filter(Account.territory_id == search_query).first()
            if account:
                territory_id = search_query
                search_results.append({
                    'method': 'ST ID Match',
                    'territory_id': territory_id,
                    'account_name': account.account_name
                })

        # Search by Opportunity ID
        opp = session.query(Opportunity).filter(
            Opportunity.opportunity_id.like(f'%{search_query}%')
        ).first()
        if opp and opp.account:
            territory_id = opp.account.territory_id
            search_results.append({
                'method': 'Opportunity ID Match',
                'territory_id': territory_id,
                'account_name': opp.account.account_name,
                'opp_id': opp.opportunity_id
            })

        # Search by Account Name
        accounts = session.query(Account).filter(
            Account.account_name.like(f'%{search_query}%')
        ).limit(5).all()

        for acc in accounts:
            if acc.territory_id:
                search_results.append({
                    'method': 'Account Name Match',
                    'territory_id': acc.territory_id,
                    'account_name': acc.account_name
                })

        if not search_results:
            st.warning(f"No results found for '{search_query}'. Try different search terms.")
        elif len(search_results) > 1:
            # Multiple results - let user choose
            st.info(f"Found {len(search_results)} matching accounts:")
            for idx, result in enumerate(search_results[:5], 1):
                st.markdown(f"**{idx}. {result['account_name']}** (ST ID: {result['territory_id']}) - {result['method']}")

            selected_st_id = st.selectbox(
                "Select Account:",
                options=[r['territory_id'] for r in search_results[:5]],
                format_func=lambda x: f"{[r['account_name'] for r in search_results if r['territory_id'] == x][0]} (ST ID: {x})"
            )
            territory_id = selected_st_id
        else:
            territory_id = search_results[0]['territory_id']

        # Generate recommendations if we have a territory_id
        if territory_id:
            with st.spinner('Analyzing account data and generating recommendations...'):
                recommendations = engine.generate_recommendations(territory_id)
                account_summary = engine.get_account_summary(territory_id)

            if account_summary:
                # Display Account Summary
                st.markdown("---")
                st.markdown(f"## 📊 Account Overview: {account_summary['account_name']}")

                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("ST ID", territory_id)
                with summary_cols[1]:
                    st.metric("Install Base", f"{account_summary['install_base_count']} items")
                with summary_cols[2]:
                    st.metric("Historical Projects", account_summary['project_count'])
                with summary_cols[3]:
                    st.metric("Active Credits", account_summary['active_credits'])

                st.markdown("---")

                # Display Priority Actions
                if recommendations['priority_actions']:
                    st.markdown("### 🚨 Priority Actions")
                    st.markdown("**Urgent items requiring immediate attention**")

                    for action in recommendations['priority_actions']:
                        urgency_color = {
                            'IMMEDIATE': '#ff4b4b',
                            'HIGH': '#ff8c00',
                            'MEDIUM': '#ffa500'
                        }.get(action['urgency'], '#gray')

                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{action['action']}**")
                                st.markdown(f"_{action['reason']}_")
                                if action.get('risk'):
                                    st.markdown(f"⚠️ **Risk:** {action['risk']}")
                            with col2:
                                st.markdown(f"<span style='color: {urgency_color}; font-weight: bold; font-size: 1.2em;'>{action['urgency']}</span>", unsafe_allow_html=True)
                            st.markdown("---")

                # Display Cross-Sell Recommendations
                if recommendations['cross_sell']:
                    st.markdown("### 🆕 Cross-Sell Opportunities")
                    st.markdown("**New services they haven't used (Gap Analysis)**")

                    for rec in recommendations['cross_sell']:
                        priority_color = {
                            'HIGH': '#ff8c00',
                            'MEDIUM': '#ffa500',
                            'LOW': '#90EE90'
                        }.get(rec['priority'], 'gray')

                        with st.expander(f"**{rec['service']}** - {rec['category']} ({rec['priority']} Priority)"):
                            st.markdown(f"**Reason:** {rec['reason']}")
                            st.markdown(f"**Gap:** {rec['gap_indicator']}")

                            if rec.get('hardware_context'):
                                st.markdown("**Hardware Context:**")
                                for hw in rec['hardware_context']:
                                    st.markdown(f"  • {hw}")

                # Display Up-Sell Recommendations
                if recommendations['up_sell']:
                    st.markdown("### ⬆️ Up-Sell Opportunities")
                    st.markdown("**Enhanced versions of services they already use**")

                    for rec in recommendations['up_sell']:
                        with st.expander(f"**{rec['service']}** - {rec['category']} ({rec['priority']} Priority)"):
                            st.markdown(f"**Current Service:** {rec['current_service']}")
                            st.markdown(f"**Current Usage:** {rec['current_usage']}")
                            st.markdown(f"**Enhancement:** {rec['reason']}")

                # Summary Stats
                st.markdown("---")
                st.markdown("### 📈 Recommendation Summary")
                summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

                with summary_col1:
                    st.metric("Priority Actions", len(recommendations['priority_actions']))
                with summary_col2:
                    st.metric("Cross-Sell", len(recommendations['cross_sell']))
                with summary_col3:
                    st.metric("Up-Sell", len(recommendations['up_sell']))
                with summary_col4:
                    total_recs = len(recommendations['priority_actions']) + len(recommendations['cross_sell']) + len(recommendations['up_sell'])
                    st.metric("Total Opportunities", total_recs)

            else:
                st.error("Could not load account data. Please try again.")

    elif not search_query:
        # Show example searches
        st.info("💡 **Example Searches:**")
        st.markdown("""
        - Search by **ST ID**: `56088`, `56769`, `56322`
        - Search by **Opportunity ID**: `OPE-0020195354`, `OPE-0019668074`
        - Search by **Account Name**: `Apple`, `Baltimore`, `Analog`
        """)

        # Show quick stats
        session = get_session()
        st.markdown("---")
        st.markdown("### 📊 Available Data")

        quick_stats_cols = st.columns(4)
        with quick_stats_cols[0]:
            account_count = session.query(Account).filter(Account.territory_id.isnot(None)).count()
            st.metric("Accounts", account_count)
        with quick_stats_cols[1]:
            total_ib = session.query(InstallBase).count()
            st.metric("Hardware Items", total_ib)
        with quick_stats_cols[2]:
            total_proj = session.query(Project).count()
            st.metric("Projects", f"{total_proj:,}")
        with quick_stats_cols[3]:
            total_credits = session.query(func.sum(ServiceCredit.active_credits)).scalar() or 0
            st.metric("Active Credits", int(total_credits))


if __name__ == "__main__":
    main()
