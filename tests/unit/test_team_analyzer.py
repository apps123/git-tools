"""Unit tests for team and department metric aggregation logic."""

from datetime import datetime, timedelta

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
        # Backend team contributions
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
        # Frontend team contributions
        Contribution(
            id="c2",
            type="commit",
            timestamp=base_date + timedelta(days=2),
            repository="myorg/repo2",
            developer="charlie",
            metadata={"sha": "def"},
        ),
    ]


@pytest.fixture
def sample_developers():
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
        Developer(
            username="charlie",
            display_name="Charlie Frontend",
            organization_member=True,
            team_affiliations=["frontend-team"],
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
        Team(
            name="frontend-team",
            display_name="Frontend Team",
            department="engineering",
            members=["charlie"],
        ),
    ]


class TestTeamMetricAggregation:
    """Tests for team metric aggregation logic."""
    
    def test_group_contributions_by_team(
        self,
        sample_team_contributions,
        sample_developers,
    ):
        """Test grouping contributions by team."""
        # Create developer lookup
        dev_lookup = {d.username: d for d in sample_developers}
        
        # Group contributions by team
        team_contributions = {}
        for contrib in sample_team_contributions:
            dev = dev_lookup.get(contrib.developer)
            if dev and dev.team_affiliations:
                for team in dev.team_affiliations:
                    if team not in team_contributions:
                        team_contributions[team] = []
                    team_contributions[team].append(contrib)
        
        assert "backend-team" in team_contributions
        assert "frontend-team" in team_contributions
        assert len(team_contributions["backend-team"]) == 2
        assert len(team_contributions["frontend-team"]) == 1
    
    def test_count_team_members(self, sample_developers, sample_teams):
        """Test counting active team members."""
        # Get unique developers per team
        team_members = {}
        for dev in sample_developers:
            for team_name in dev.team_affiliations:
                if team_name not in team_members:
                    team_members[team_name] = set()
                team_members[team_name].add(dev.username)
        
        assert "backend-team" in team_members
        assert len(team_members["backend-team"]) == 2
        assert "frontend-team" in team_members
        assert len(team_members["frontend-team"]) == 1
    
    def test_aggregate_team_metrics(
        self,
        sample_team_contributions,
        sample_developers,
    ):
        """Test aggregating metrics per team."""
        dev_lookup = {d.username: d for d in sample_developers}
        team_contributions = {}
        
        for contrib in sample_team_contributions:
            dev = dev_lookup.get(contrib.developer)
            if dev and dev.team_affiliations:
                for team in dev.team_affiliations:
                    if team not in team_contributions:
                        team_contributions[team] = []
                    team_contributions[team].append(contrib)
        
        # Count by type per team
        backend_commits = [
            c for c in team_contributions["backend-team"]
            if c.type == "commit"
        ]
        backend_prs = [
            c for c in team_contributions["backend-team"]
            if c.type == "pull_request"
        ]
        
        assert len(backend_commits) == 1
        assert len(backend_prs) == 1


class TestDepartmentMetricAggregation:
    """Tests for department metric aggregation logic."""
    
    def test_group_teams_by_department(self, sample_teams):
        """Test grouping teams by department."""
        dept_teams = {}
        for team in sample_teams:
            if team.department not in dept_teams:
                dept_teams[team.department] = []
            dept_teams[team.department].append(team.name)
        
        assert "engineering" in dept_teams
        assert len(dept_teams["engineering"]) == 2
    
    def test_aggregate_department_metrics(
        self,
        sample_team_contributions,
        sample_developers,
        sample_teams,
    ):
        """Test aggregating metrics per department."""
        # First group by team
        dev_lookup = {d.username: d for d in sample_developers}
        team_contributions = {}
        
        for contrib in sample_team_contributions:
            dev = dev_lookup.get(contrib.developer)
            if dev and dev.team_affiliations:
                for team in dev.team_affiliations:
                    if team not in team_contributions:
                        team_contributions[team] = []
                    team_contributions[team].append(contrib)
        
        # Then aggregate by department
        dept_contributions = {}
        for team in sample_teams:
            if team.department not in dept_contributions:
                dept_contributions[team.department] = []
            dept_contributions[team.department].extend(
                team_contributions.get(team.name, [])
            )
        
        assert "engineering" in dept_contributions
        assert len(dept_contributions["engineering"]) == 3

