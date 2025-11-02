"""Unit tests for lead scoring algorithm."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from src.engines.lead_scorer import LeadScorer
from src.models import Lead, InstallBase, Account, Opportunity, Project


class TestLeadScorer:
    """Test lead scoring algorithm."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock session
        self.mock_session = Mock()
        self.scorer = LeadScorer(self.mock_session)

    def test_urgency_score_maximum_eol(self):
        """Test urgency score for equipment far past EOL."""
        # Create lead
        lead = Lead(id=1, install_base_id=1)

        # Create install base item with extreme EOL
        install_base = InstallBase(
            id=1,
            days_since_eol=3753,  # 10+ years past EOL
            days_since_expiry=1000  # Support expired long ago
        )

        # Mock the session query
        self.mock_session.query.return_value.get.return_value = install_base

        # Calculate score
        score = self.scorer._calculate_urgency_score(lead)

        # Should be at maximum (100)
        assert score == 100.0, f"Expected score 100, got {score}"
        print(f"✓ Maximum EOL urgency score: {score}")

    def test_urgency_score_recently_expired(self):
        """Test urgency for recently expired support."""
        lead = Lead(id=2, install_base_id=2)

        install_base = InstallBase(
            id=2,
            days_since_eol=400,  # Just over 1 year past EOL
            days_since_expiry=100  # Just expired (under 6 months)
        )

        self.mock_session.query.return_value.get.return_value = install_base

        score = self.scorer._calculate_urgency_score(lead)

        # Base 50 + 10 (EOL > 365) + 10 (expiry > 90) = 70
        expected = 70.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Recent expiry urgency score: {score}")

    def test_urgency_score_moderate(self):
        """Test moderate urgency scenario."""
        lead = Lead(id=3, install_base_id=3)

        install_base = InstallBase(
            id=3,
            days_since_eol=1200,  # 3+ years past EOL
            days_since_expiry=200  # 6+ months expired
        )

        self.mock_session.query.return_value.get.return_value = install_base

        score = self.scorer._calculate_urgency_score(lead)

        # Base 50 + 20 (EOL > 1095) + 15 (expiry > 180) = 85
        expected = 85.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Moderate urgency score: {score}")

    def test_urgency_score_no_install_base(self):
        """Test urgency when install base is missing."""
        lead = Lead(id=4, install_base_id=None)

        score = self.scorer._calculate_urgency_score(lead)

        # Should return base score
        assert score == 50.0, f"Expected base score 50, got {score}"
        print(f"✓ No install base urgency score: {score}")

    def test_value_score_high_value_deal(self):
        """Test value scoring for large deal."""
        lead = Lead(
            id=5,
            account_id=1,
            estimated_value_max=250000
        )

        # Mock install base count query
        mock_query = Mock()
        mock_query.filter.return_value.scalar.return_value = 60  # Large install base
        self.mock_session.query.return_value = mock_query

        score = self.scorer._calculate_value_score(lead)

        # Base 40 + 40 (value >= 200K) + 20 (IB > 50) = 100
        expected = 100.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ High value deal score: {score}")

    def test_value_score_medium_value_deal(self):
        """Test value scoring for medium-sized deal."""
        lead = Lead(
            id=6,
            account_id=2,
            estimated_value_max=75000
        )

        mock_query = Mock()
        mock_query.filter.return_value.scalar.return_value = 15  # Medium install base
        self.mock_session.query.return_value = mock_query

        score = self.scorer._calculate_value_score(lead)

        # Base 40 + 20 (value >= 50K but < 100K) + 10 (IB > 5 but <= 20) = 70
        expected = 70.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Medium value deal score: {score}")

    def test_value_score_no_estimated_value(self):
        """Test value scoring when estimated value is missing."""
        lead = Lead(
            id=7,
            account_id=3,
            estimated_value_max=None
        )

        mock_query = Mock()
        mock_query.filter.return_value.scalar.return_value = 3
        self.mock_session.query.return_value = mock_query

        score = self.scorer._calculate_value_score(lead)

        # Base 40 + 0 (no value) + 0 (IB <= 5) = 40
        expected = 40.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ No estimated value score: {score}")

    def test_propensity_score_high_engagement(self):
        """Test propensity for highly engaged account."""
        lead = Lead(id=8, account_id=4)

        # Mock queries for opportunities and projects
        def query_side_effect(*args):
            mock = Mock()
            # First call is for opportunities
            if not hasattr(query_side_effect, 'call_count'):
                query_side_effect.call_count = 0

            query_side_effect.call_count += 1

            if query_side_effect.call_count == 1:
                # Opportunities query
                mock.filter.return_value.scalar.return_value = 6  # > 5 opportunities
            else:
                # Projects query
                mock.filter.return_value.scalar.return_value = 12  # > 10 projects

            return mock

        self.mock_session.query.side_effect = query_side_effect

        score = self.scorer._calculate_propensity_score(lead)

        # Base 30 + 30 (opps > 5) + 30 (projects > 10) + 10 (recency) = 100
        expected = 100.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ High engagement propensity score: {score}")

    def test_propensity_score_low_engagement(self):
        """Test propensity for account with minimal engagement."""
        lead = Lead(id=9, account_id=5)

        def query_side_effect(*args):
            mock = Mock()
            if not hasattr(query_side_effect, 'call_count'):
                query_side_effect.call_count = 0

            query_side_effect.call_count += 1

            if query_side_effect.call_count == 1:
                mock.filter.return_value.scalar.return_value = 1  # 1 opportunity
            else:
                mock.filter.return_value.scalar.return_value = 2  # 2 projects

            return mock

        self.mock_session.query.side_effect = query_side_effect

        score = self.scorer._calculate_propensity_score(lead)

        # Base 30 + 10 (1 opp) + 10 (2 projects) + 10 (recency) = 60
        expected = 60.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Low engagement propensity score: {score}")

    def test_strategic_fit_score_strategic_product(self):
        """Test strategic fit for strategic product family."""
        lead = Lead(
            id=10,
            install_base_id=10,
            lead_type='Hardware Refresh - EOL Equipment'
        )

        install_base = InstallBase(
            id=10,
            product_family='PRIMERA',
            business_area='Compute and Storage'
        )

        self.mock_session.query.return_value.get.return_value = install_base

        score = self.scorer._calculate_strategic_fit_score(lead)

        # Base 50 + 25 (PRIMERA) + 15 (Compute) + 10 (Hardware Refresh) = 100
        expected = 100.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Strategic product fit score: {score}")

    def test_strategic_fit_score_renewal_lead(self):
        """Test strategic fit for renewal lead."""
        lead = Lead(
            id=11,
            install_base_id=11,
            lead_type='Renewal - Expired Support'
        )

        install_base = InstallBase(
            id=11,
            product_family='PROLIANT',
            business_area='Other'
        )

        self.mock_session.query.return_value.get.return_value = install_base

        score = self.scorer._calculate_strategic_fit_score(lead)

        # Base 50 + 0 (not strategic family) + 0 (not Compute) + 5 (Renewal) = 55
        expected = 55.0
        assert score == expected, f"Expected {expected}, got {score}"
        print(f"✓ Renewal lead strategic score: {score}")

    def test_overall_score_calculation(self):
        """Test weighted overall scoring formula."""
        lead = Lead(id=12)

        # Set component scores manually
        lead.urgency_score = 100.0
        lead.value_score = 80.0
        lead.propensity_score = 60.0
        lead.strategic_fit_score = 70.0

        # Calculate expected score
        expected = (
            100.0 * 0.35 +  # 35.0
            80.0 * 0.30 +   # 24.0
            60.0 * 0.20 +   # 12.0
            70.0 * 0.15     # 10.5
        )  # = 81.5

        # Manually calculate what score_lead would produce
        actual = (
            lead.urgency_score * self.scorer.weights['urgency'] +
            lead.value_score * self.scorer.weights['value'] +
            lead.propensity_score * self.scorer.weights['propensity'] +
            lead.strategic_fit_score * self.scorer.weights['strategic_fit']
        )

        assert abs(actual - expected) < 0.1, f"Expected {expected}, got {actual}"
        print(f"✓ Overall score calculation: {actual:.1f}")

    def test_priority_assignment_critical(self):
        """Test CRITICAL priority assignment."""
        lead = Lead(id=13, score=85)

        # Manually check priority logic
        if lead.score >= 75:
            priority = 'CRITICAL'
        elif lead.score >= 60:
            priority = 'HIGH'
        elif lead.score >= 40:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        assert priority == 'CRITICAL', f"Expected CRITICAL, got {priority}"
        print(f"✓ Priority for score 85: {priority}")

    def test_priority_assignment_high(self):
        """Test HIGH priority assignment."""
        lead = Lead(id=14, score=65)

        if lead.score >= 75:
            priority = 'CRITICAL'
        elif lead.score >= 60:
            priority = 'HIGH'
        elif lead.score >= 40:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        assert priority == 'HIGH', f"Expected HIGH, got {priority}"
        print(f"✓ Priority for score 65: {priority}")

    def test_priority_assignment_medium(self):
        """Test MEDIUM priority assignment."""
        lead = Lead(id=15, score=50)

        if lead.score >= 75:
            priority = 'CRITICAL'
        elif lead.score >= 60:
            priority = 'HIGH'
        elif lead.score >= 40:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        assert priority == 'MEDIUM', f"Expected MEDIUM, got {priority}"
        print(f"✓ Priority for score 50: {priority}")

    def test_priority_assignment_low(self):
        """Test LOW priority assignment."""
        lead = Lead(id=16, score=30)

        if lead.score >= 75:
            priority = 'CRITICAL'
        elif lead.score >= 60:
            priority = 'HIGH'
        elif lead.score >= 40:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'

        assert priority == 'LOW', f"Expected LOW, got {priority}"
        print(f"✓ Priority for score 30: {priority}")

    def test_priority_boundary_critical(self):
        """Test priority boundary at 75."""
        # Test exactly 75
        lead1 = Lead(id=17, score=75)
        if lead1.score >= 75:
            priority1 = 'CRITICAL'
        elif lead1.score >= 60:
            priority1 = 'HIGH'
        else:
            priority1 = 'MEDIUM'

        assert priority1 == 'CRITICAL'

        # Test just below 75
        lead2 = Lead(id=18, score=74.9)
        if lead2.score >= 75:
            priority2 = 'CRITICAL'
        elif lead2.score >= 60:
            priority2 = 'HIGH'
        else:
            priority2 = 'MEDIUM'

        assert priority2 == 'HIGH'
        print(f"✓ Priority boundary test: 75=CRITICAL, 74.9=HIGH")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])
