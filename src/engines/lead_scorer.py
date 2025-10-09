"""Lead scoring algorithm."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models import Lead, InstallBase, Account, Opportunity, Project
from src.utils.config_loader import config


class LeadScorer:
    """Score leads based on urgency, value, propensity, and strategic fit."""

    def __init__(self, session: Session):
        """Initialize lead scorer with database session."""
        self.session = session
        self.config = config

        # Get scoring weights from config
        self.weights = {
            'urgency': config.get('scoring_weights.urgency', 0.35),
            'value': config.get('scoring_weights.value', 0.30),
            'propensity': config.get('scoring_weights.propensity', 0.20),
            'strategic_fit': config.get('scoring_weights.strategic_fit', 0.15)
        }

    def score_all_leads(self) -> int:
        """Score all active leads. Returns count of leads scored."""
        leads = self.session.query(Lead).filter(Lead.is_active == True).all()

        count = 0
        for lead in leads:
            self.score_lead(lead)
            count += 1

        self.session.commit()
        print(f"  → Scored {count} leads")
        return count

    def score_lead(self, lead: Lead) -> float:
        """
        Score a single lead (0-100).

        Returns:
            Overall score (0-100)
        """
        # Calculate component scores
        urgency_score = self._calculate_urgency_score(lead)
        value_score = self._calculate_value_score(lead)
        propensity_score = self._calculate_propensity_score(lead)
        strategic_fit_score = self._calculate_strategic_fit_score(lead)

        # Calculate weighted overall score
        overall_score = (
            urgency_score * self.weights['urgency'] +
            value_score * self.weights['value'] +
            propensity_score * self.weights['propensity'] +
            strategic_fit_score * self.weights['strategic_fit']
        )

        # Update lead
        lead.urgency_score = urgency_score
        lead.value_score = value_score
        lead.propensity_score = propensity_score
        lead.strategic_fit_score = strategic_fit_score
        lead.score = overall_score

        # Update priority based on score
        if overall_score >= 75:
            lead.priority = 'CRITICAL'
        elif overall_score >= 60:
            lead.priority = 'HIGH'
        elif overall_score >= 40:
            lead.priority = 'MEDIUM'
        else:
            lead.priority = 'LOW'

        return overall_score

    def _calculate_urgency_score(self, lead: Lead) -> float:
        """Calculate urgency score (0-100) based on time sensitivity."""
        score = 50.0  # Base score

        if not lead.install_base_id:
            return score

        install_base = self.session.query(InstallBase).get(lead.install_base_id)
        if not install_base:
            return score

        # Factor 1: Days since EOL (higher is more urgent)
        if install_base.days_since_eol:
            if install_base.days_since_eol > 1825:  # 5 years
                score += 30
            elif install_base.days_since_eol > 1095:  # 3 years
                score += 20
            elif install_base.days_since_eol > 365:  # 1 year
                score += 10

        # Factor 2: Days since support expiry (higher is more urgent)
        if install_base.days_since_expiry:
            if install_base.days_since_expiry > 365:  # 1 year
                score += 20
            elif install_base.days_since_expiry > 180:  # 6 months
                score += 15
            elif install_base.days_since_expiry > 90:  # 3 months
                score += 10

        # Cap at 100
        return min(score, 100.0)

    def _calculate_value_score(self, lead: Lead) -> float:
        """Calculate value score (0-100) based on deal size and install base."""
        score = 40.0  # Base score

        # Factor 1: Estimated deal value
        if lead.estimated_value_max:
            if lead.estimated_value_max >= 200000:
                score += 40
            elif lead.estimated_value_max >= 100000:
                score += 30
            elif lead.estimated_value_max >= 50000:
                score += 20
            else:
                score += 10

        # Factor 2: Account install base size
        if lead.account_id:
            account_ib_count = self.session.query(func.count(InstallBase.id)).filter(
                InstallBase.account_id == lead.account_id
            ).scalar()

            if account_ib_count > 50:
                score += 20
            elif account_ib_count > 20:
                score += 15
            elif account_ib_count > 5:
                score += 10

        return min(score, 100.0)

    def _calculate_propensity_score(self, lead: Lead) -> float:
        """Calculate propensity score (0-100) based on account engagement."""
        score = 30.0  # Base score

        if not lead.account_id:
            return score

        # Factor 1: Open opportunities (indicates active engagement)
        open_opps = self.session.query(func.count(Opportunity.id)).filter(
            Opportunity.account_id == lead.account_id
        ).scalar()

        if open_opps > 5:
            score += 30
        elif open_opps > 2:
            score += 20
        elif open_opps > 0:
            score += 10

        # Factor 2: Historical projects (indicates past buying behavior)
        closed_projects = self.session.query(func.count(Project.id)).filter(
            Project.account_id == lead.account_id,
            Project.status == 'CLSD'
        ).scalar()

        if closed_projects > 10:
            score += 30
        elif closed_projects > 5:
            score += 20
        elif closed_projects > 0:
            score += 10

        # Factor 3: Recency of last project
        # (Would need project end date for this - placeholder for now)
        score += 10

        return min(score, 100.0)

    def _calculate_strategic_fit_score(self, lead: Lead) -> float:
        """Calculate strategic fit score (0-100) based on product alignment."""
        score = 50.0  # Base score

        if not lead.install_base_id:
            return score

        install_base = self.session.query(InstallBase).get(lead.install_base_id)
        if not install_base:
            return score

        # Factor 1: Strategic product families (prioritize certain products)
        strategic_families = ['3PAR', 'PRIMERA', 'ALLETRA', 'COMPUTE']
        if install_base.product_family and install_base.product_family.upper() in strategic_families:
            score += 25

        # Factor 2: Business area alignment
        if install_base.business_area and 'Compute' in install_base.business_area:
            score += 15

        # Factor 3: Lead type strategic value
        if 'Hardware Refresh' in lead.lead_type:
            score += 10  # Hardware refresh is strategic
        elif 'Renewal' in lead.lead_type:
            score += 5   # Renewals are important but less strategic

        return min(score, 100.0)
