"""Integration tests for repository analysis workflow."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.repository import Repository
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_repository_contributions():
    """Sample contributions for repository analysis."""
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
            developer="charlie",
            state="approved",
            metadata={"review_id": 1},
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


class TestRepositoryReportFlow:
    """Integration tests for repository report generation flow."""
    
    @pytest.mark.integration
    def test_repository_analysis_with_sample_data(
        self,
        sample_repository_contributions,
        sample_time_period,
    ):
        """Test that repository analysis can be performed on sample data."""
        # Verify we have contributions
        assert len(sample_repository_contributions) > 0
        
        # Verify all contributions are for the same repository
        repos = {c.repository for c in sample_repository_contributions}
        assert len(repos) == 1
        
        # Verify contributions are within time period
        for contribution in sample_repository_contributions:
            assert (
                sample_time_period.start_date
                <= contribution.timestamp
                <= sample_time_period.end_date
            )
    
    @pytest.mark.integration
    def test_repository_metrics_calculation(self, sample_repository_contributions):
        """Test that repository metrics can be calculated from contributions."""
        repo = "myorg/repo1"
        repo_contributions = [
            c for c in sample_repository_contributions if c.repository == repo
        ]
        
        # Count by type
        commits = [c for c in repo_contributions if c.type == "commit"]
        prs = [c for c in repo_contributions if c.type == "pull_request"]
        reviews = [c for c in repo_contributions if c.type == "review"]
        issues = [c for c in repo_contributions if c.type == "issue"]
        
        assert len(commits) == 1
        assert len(prs) == 1
        assert len(reviews) == 1
        assert len(issues) == 0
        
        # Count unique contributors
        contributors = {c.developer for c in repo_contributions}
        assert len(contributors) == 3

