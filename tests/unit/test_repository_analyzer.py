"""Unit tests for repository trend and distribution calculations."""

from datetime import datetime, timedelta

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_contributions_for_trends():
    """Sample contributions for trend analysis."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    # Create contributions over time to show trends
    contributions = []
    
    # Week 1: High activity
    for day in range(7):
        contributions.append(
            Contribution(
                id=f"c_week1_day{day}",
                type="commit",
                timestamp=base_date + timedelta(days=day),
                repository="myorg/repo1",
                developer="alice",
                metadata={"sha": f"abc{day}"},
            )
        )
    
    # Week 2: Medium activity
    for day in range(7, 14):
        if day % 2 == 0:  # Every other day
            contributions.append(
                Contribution(
                    id=f"c_week2_day{day}",
                    type="commit",
                    timestamp=base_date + timedelta(days=day),
                    repository="myorg/repo1",
                    developer="alice",
                    metadata={"sha": f"def{day}"},
                )
            )
    
    # Week 3: Low activity (declining trend)
    for day in range(14, 21):
        if day % 3 == 0:  # Every third day
            contributions.append(
                Contribution(
                    id=f"c_week3_day{day}",
                    type="commit",
                    timestamp=base_date + timedelta(days=day),
                    repository="myorg/repo1",
                    developer="alice",
                    metadata={"sha": f"ghi{day}"},
                )
            )
    
    return contributions


class TestRepositoryTrendAnalysis:
    """Tests for repository trend calculations."""
    
    def test_identify_declining_trend(self, sample_contributions_for_trends):
        """Test that declining activity trend can be identified."""
        # Week 1: 7 contributions
        week1 = [
            c for c in sample_contributions_for_trends
            if 0 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 7
        ]
        
        # Week 2: ~3-4 contributions
        week2 = [
            c for c in sample_contributions_for_trends
            if 7 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 14
        ]
        
        # Week 3: ~2-3 contributions
        week3 = [
            c for c in sample_contributions_for_trends
            if 14 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 21
        ]
        
        assert len(week1) > len(week2)
        assert len(week2) > len(week3)
    
    def test_contribution_distribution_by_developer(self, sample_contributions_for_trends):
        """Test calculating contribution distribution by developer."""
        from collections import Counter
        
        developers = [c.developer for c in sample_contributions_for_trends]
        distribution = Counter(developers)
        
        # All contributions are from alice in this sample
        assert len(distribution) == 1
        assert distribution["alice"] == len(sample_contributions_for_trends)
    
    def test_activity_distribution_over_time(self, sample_contributions_for_trends):
        """Test calculating activity distribution over time periods."""
        # Group by week
        week1_count = len([
            c for c in sample_contributions_for_trends
            if 0 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 7
        ])
        week2_count = len([
            c for c in sample_contributions_for_trends
            if 7 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 14
        ])
        week3_count = len([
            c for c in sample_contributions_for_trends
            if 14 <= (c.timestamp - sample_contributions_for_trends[0].timestamp).days < 21
        ])
        
        # Verify distribution shows declining trend
        assert week1_count >= week2_count
        assert week2_count >= week3_count

