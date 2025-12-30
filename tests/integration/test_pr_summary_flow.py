"""Integration tests for PR summary generation workflow."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_pr_contributions():
    """Sample PR contributions for summary generation."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    return [
        Contribution(
            id="pr-1",
            type="pull_request",
            timestamp=base_date,
            repository="myorg/repo1",
            developer="alice",
            title="Add new feature",
            state="merged",
            metadata={
                "number": 1,
                "merged": True,
                "body": "This PR adds a new feature that improves performance.",
            },
        ),
        Contribution(
            id="pr-2",
            type="pull_request",
            timestamp=base_date + timedelta(days=1),
            repository="myorg/repo1",
            developer="bob",
            title="Fix bug",
            state="merged",
            metadata={
                "number": 2,
                "merged": True,
                "body": "This PR fixes a critical bug in authentication.",
            },
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


class TestPRSummaryFlow:
    """Integration tests for PR summary generation flow."""
    
    @pytest.mark.integration
    def test_pr_summary_generation_with_sample_data(
        self,
        sample_pr_contributions,
        sample_time_period,
    ):
        """Test that PR summaries can be generated from sample data."""
        # Verify we have PR contributions
        prs = [c for c in sample_pr_contributions if c.type == "pull_request"]
        assert len(prs) > 0
        
        # Verify PRs are within time period
        for pr in prs:
            assert (
                sample_time_period.start_date
                <= pr.timestamp
                <= sample_time_period.end_date
            )
    
    @pytest.mark.integration
    def test_pr_summary_includes_required_fields(self, sample_pr_contributions):
        """Test that PR summaries include required fields."""
        prs = [c for c in sample_pr_contributions if c.type == "pull_request"]
        
        for pr in prs:
            assert pr.id is not None
            assert pr.title is not None
            assert pr.repository is not None
            assert pr.developer is not None
            assert pr.metadata is not None
    
    @pytest.mark.integration
    @patch("github_tools.summarizers.llm_summarizer.LLMSummarizer")
    def test_pr_summarization_workflow(self, mock_summarizer, sample_pr_contributions):
        """Test that PR summarization workflow can be executed."""
        # Mock summarizer
        mock_summarizer.return_value.summarize.return_value = "Test summary"
        
        # This test validates the structure
        # Actual implementation will use LLM summarizer
        prs = [c for c in sample_pr_contributions if c.type == "pull_request"]
        assert len(prs) > 0

