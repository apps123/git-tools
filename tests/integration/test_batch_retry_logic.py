"""Integration tests for batch retry logic."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from github_tools.collectors.pr_summary_collector import PRSummaryCollector
from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer


@pytest.fixture
def batch_prs():
    """Batch of PR contributions."""
    base_date = datetime.now() - timedelta(days=1)
    return [
        Contribution(
            id=f"pr{i}",
            type="pull_request",
            timestamp=base_date,
            repository="test/repo",
            developer="alice",
            title=f"PR {i}",
            state="merged",
            metadata={"body": f"Description {i}"},
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_time_period():
    """Sample time period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return TimePeriod(start_date=start_date, end_date=end_date, period_type="custom")


@pytest.mark.integration
class TestBatchRetryLogic:
    """Integration tests for batch retry logic."""
    
    def test_batch_continues_on_individual_failures(self, batch_prs, sample_time_period):
        """Test batch processing continues when individual PRs fail."""
        mock_provider = Mock()
        mock_provider.summarize.side_effect = [
            "Summary 1",
            RuntimeError("Failed"),
            "Summary 3",
            RuntimeError("Failed"),
            "Summary 5",
        ]
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "test-provider"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        collector = PRSummaryCollector(summarizer, auto_retry=False)
        
        summaries = collector.collect_summaries(batch_prs, sample_time_period)
        
        # Should have 5 summaries (some with errors)
        assert len(summaries) == 5
        assert summaries[0]["summary"] == "Summary 1"
        assert summaries[2]["summary"] == "Summary 3"
        assert summaries[4]["summary"] == "Summary 5"
        # Failed ones should have error indicators
        assert summaries[1].get("error") is True
        assert summaries[3].get("error") is True
    
    def test_batch_retry_with_next_provider(self, batch_prs, sample_time_period):
        """Test batch retries failed PRs with next available provider."""
        mock_provider1 = Mock()
        mock_provider1.summarize.side_effect = [
            "Summary 1",
            RuntimeError("Failed"),
            RuntimeError("Failed"),
            "Summary 4",
            RuntimeError("Failed"),
        ]
        mock_provider1.is_available.return_value = True
        mock_provider1.get_metadata.return_value = {"name": "provider1"}
        
        mock_provider2 = Mock()
        mock_provider2.summarize.return_value = "Retry summary"
        mock_provider2.is_available.return_value = True
        mock_provider2.get_metadata.return_value = {"name": "provider2"}
        
        summarizer = LLMSummarizer(provider=mock_provider1, auto_detect=False)
        summarizer.provider_config = {}
        summarizer.provider_name = "provider1"
        
        collector = PRSummaryCollector(summarizer, auto_retry=True)
        
        with patch("github_tools.collectors.pr_summary_collector.detect_available_providers", return_value=["provider1", "provider2"]):
            with patch("github_tools.summarizers.llm_summarizer.get_provider") as mock_get:
                mock_get.return_value = mock_provider2
                
                summaries = collector.collect_summaries(batch_prs, sample_time_period)
                
                # Should have 5 summaries
                assert len(summaries) == 5
                # First succeeded with provider1
                assert summaries[0]["summary"] == "Summary 1"
                assert summaries[0]["provider"] == "provider1"
                # Failed ones retried with provider2
                assert summaries[1]["summary"] == "Retry summary"
                assert summaries[1]["provider"] == "provider2"
                assert summaries[1]["retried"] is True
                assert summaries[2]["provider"] == "provider2"
                assert summaries[2]["retried"] is True
                # Fourth succeeded with provider1
                assert summaries[3]["summary"] == "Summary 4"
                assert summaries[3]["provider"] == "provider1"
                # Fifth retried with provider2
                assert summaries[4]["provider"] == "provider2"
                assert summaries[4]["retried"] is True
    
    def test_batch_no_retry_when_disabled(self, batch_prs, sample_time_period):
        """Test batch processing without retry when disabled."""
        mock_provider = Mock()
        mock_provider.summarize.side_effect = [
            "Summary 1",
            RuntimeError("Failed"),
            "Summary 3",
        ]
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "test-provider"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        collector = PRSummaryCollector(summarizer, auto_retry=False)
        
        summaries = collector.collect_summaries(batch_prs[:3], sample_time_period)
        
        # Should not retry - errors marked immediately
        assert len(summaries) == 3
        assert summaries[1].get("error") is True
        assert "retried" not in summaries[1]

