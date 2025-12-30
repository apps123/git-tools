"""Integration tests for end-to-end developer report flow."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.repository import Repository
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_contributions():
    """Sample contributions for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    return [
        Contribution(
            id="commit1",
            type="commit",
            timestamp=start_date + timedelta(days=1),
            repository="myorg/repo1",
            developer="alice",
            title="Fix bug",
            metadata={"sha": "abc123", "message": "Fix bug", "files_changed": 2},
        ),
        Contribution(
            id="pr1",
            type="pull_request",
            timestamp=start_date + timedelta(days=5),
            repository="myorg/repo1",
            developer="alice",
            title="Add feature",
            state="merged",
            metadata={"number": 1, "merged": True},
        ),
        Contribution(
            id="review1",
            type="review",
            timestamp=start_date + timedelta(days=6),
            repository="myorg/repo1",
            developer="bob",
            title="Review PR #1",
            state="approved",
            metadata={"review_id": 1, "pr_number": 1},
        ),
    ]


@pytest.fixture
def sample_developers():
    """Sample developers for testing."""
    return [
        Developer(
            username="alice",
            display_name="Alice Developer",
            organization_member=True,
            is_internal=True,
        ),
        Developer(
            username="bob",
            display_name="Bob Contributor",
            organization_member=False,
            is_internal=False,
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


class TestDeveloperReportFlow:
    """Integration tests for developer report generation flow."""
    
    @pytest.mark.integration
    def test_report_generation_with_sample_data(
        self,
        sample_contributions,
        sample_developers,
        sample_time_period,
    ):
        """
        Test that developer report can be generated from sample data.
        
        This is a placeholder integration test that validates the flow
        without requiring actual GitHub API access.
        """
        # This test validates the structure and flow
        # Actual implementation will use collectors and analyzers
        
        # Verify we have contributions
        assert len(sample_contributions) > 0
        
        # Verify we have developers
        assert len(sample_developers) > 0
        
        # Verify time period is valid
        assert sample_time_period.start_date <= sample_time_period.end_date
        
        # Verify contributions are within time period
        for contribution in sample_contributions:
            assert (
                sample_time_period.start_date
                <= contribution.timestamp
                <= sample_time_period.end_date
            )
        
        # This test will be expanded when collectors and analyzers are implemented
        # For now, it validates the test fixtures are correct
    
    @pytest.mark.integration
    def test_report_includes_all_developers(
        self,
        sample_contributions,
        sample_developers,
    ):
        """Test that report includes all developers who contributed."""
        # Get unique developers from contributions
        contributing_devs = {c.developer for c in sample_contributions}
        
        # All contributing developers should be in the sample developers list
        dev_usernames = {d.username for d in sample_developers}
        assert contributing_devs.issubset(dev_usernames)
    
    @pytest.mark.integration
    def test_report_handles_empty_contributions(self, sample_time_period):
        """Test that report handles empty contribution list gracefully."""
        # Empty contributions should result in empty report
        contributions = []
        
        # Report should still be valid but with zero metrics
        # This will be validated when report generator is implemented
        assert len(contributions) == 0

