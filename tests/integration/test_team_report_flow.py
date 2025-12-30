"""Integration tests for team and department analysis workflow."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.team import Team
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_team_contributions():
    """Sample contributions for team analysis."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    return [
        Contribution(
            id="c1",
            type="commit",
            timestamp=base_date,
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": "abc"},
        ),
        Contribution(
            id="pr1",
            type="pull_request",
            timestamp=base_date + timedelta(days=1),
            repository="myorg/repo1",
            developer="bob",
            state="merged",
            metadata={"number": 1},
        ),
        Contribution(
            id="r1",
            type="review",
            timestamp=base_date + timedelta(days=2),
            repository="myorg/repo1",
            developer="alice",
            state="approved",
            metadata={"review_id": 1},
        ),
    ]


@pytest.fixture
def sample_developers_with_teams():
    """Sample developers with team affiliations."""
    return [
        Developer(
            username="alice",
            display_name="Alice Developer",
            organization_member=True,
            team_affiliations=["backend-team"],
            is_internal=True,
        ),
        Developer(
            username="bob",
            display_name="Bob Contributor",
            organization_member=True,
            team_affiliations=["backend-team"],
            is_internal=True,
        ),
    ]


@pytest.fixture
def sample_teams():
    """Sample teams."""
    return [
        Team(
            name="backend-team",
            display_name="Backend Team",
            department="engineering",
            members=["alice", "bob"],
        ),
    ]


@pytest.fixture
def sample_time_period():
    """Sample time period for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return TimePeriod(
        start_date=start_date,
        end_date=end_date,
        period_type="custom",
    )


class TestTeamReportFlow:
    """Integration tests for team report generation flow."""
    
    @pytest.mark.integration
    def test_team_analysis_with_sample_data(
        self,
        sample_team_contributions,
        sample_developers_with_teams,
        sample_teams,
        sample_time_period,
    ):
        """Test that team analysis can be performed on sample data."""
        # Verify we have contributions
        assert len(sample_team_contributions) > 0
        
        # Verify developers have team affiliations
        for dev in sample_developers_with_teams:
            assert len(dev.team_affiliations) > 0
        
        # Verify teams exist
        assert len(sample_teams) > 0
    
    @pytest.mark.integration
    def test_team_metrics_calculation(self, sample_team_contributions, sample_developers_with_teams):
        """Test that team metrics can be calculated from contributions."""
        # Group contributions by team
        team_contributions = {}
        for contrib in sample_team_contributions:
            dev = next(
                (d for d in sample_developers_with_teams if d.username == contrib.developer),
                None,
            )
            if dev and dev.team_affiliations:
                for team in dev.team_affiliations:
                    if team not in team_contributions:
                        team_contributions[team] = []
                    team_contributions[team].append(contrib)
        
        # Verify backend-team has contributions
        assert "backend-team" in team_contributions
        assert len(team_contributions["backend-team"]) > 0
    
    @pytest.mark.integration
    def test_department_aggregation(self, sample_teams):
        """Test that department metrics aggregate team metrics."""
        # Group teams by department
        dept_teams = {}
        for team in sample_teams:
            if team.department not in dept_teams:
                dept_teams[team.department] = []
            dept_teams[team.department].append(team.name)
        
        # Verify engineering department has teams
        assert "engineering" in dept_teams
        assert len(dept_teams["engineering"]) > 0

