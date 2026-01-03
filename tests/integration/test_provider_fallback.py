"""Integration tests for provider fallback logic."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from github_tools.collectors.pr_summary_collector import PRSummaryCollector
from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer


@pytest.fixture
def sample_prs():
    """Sample PR contributions."""
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
        for i in range(3)
    ]


@pytest.fixture
def sample_time_period():
    """Sample time period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return TimePeriod(start_date=start_date, end_date=end_date, period_type="custom")


@pytest.mark.integration
class TestProviderFallback:
    """Integration tests for provider fallback."""
    
    def test_summarize_with_fallback(self, sample_prs):
        """Test summarize_with_fallback uses next available provider."""
        # First provider fails
        mock_provider1 = Mock()
        mock_provider1.summarize.side_effect = RuntimeError("Provider 1 failed")
        mock_provider1.is_available.return_value = True
        mock_provider1.get_metadata.return_value = {"name": "provider1"}
        
        # Second provider succeeds
        mock_provider2 = Mock()
        mock_provider2.summarize.return_value = "Summary from provider 2"
        mock_provider2.is_available.return_value = True
        mock_provider2.get_metadata.return_value = {"name": "provider2"}
        
        summarizer = LLMSummarizer(provider=mock_provider1, auto_detect=False)
        summarizer.provider_config = {}
        
        with patch("github_tools.summarizers.llm_summarizer.get_provider") as mock_get:
            mock_get.return_value = mock_provider2
            
            result = summarizer.summarize_with_fallback(
                sample_prs[0],
                fallback_providers=["provider2"],
            )
            
            assert result == "Summary from provider 2"
            mock_provider2.summarize.assert_called_once()
    
    def test_batch_retry_with_fallback(self, sample_prs, sample_time_period):
        """Test batch processing retries with fallback provider."""
        # Primary provider fails for some PRs
        mock_provider1 = Mock()
        mock_provider1.summarize.side_effect = [
            "Summary 1",
            RuntimeError("Failed"),
            RuntimeError("Failed"),
        ]
        mock_provider1.is_available.return_value = True
        mock_provider1.get_metadata.return_value = {"name": "provider1"}
        mock_provider1.provider_name = "provider1"
        
        # Fallback provider succeeds
        mock_provider2 = Mock()
        mock_provider2.summarize.return_value = "Summary from fallback"
        mock_provider2.is_available.return_value = True
        mock_provider2.get_metadata.return_value = {"name": "provider2"}
        
        summarizer = LLMSummarizer(provider=mock_provider1, auto_detect=False)
        summarizer.provider_config = {}
        summarizer.provider_name = "provider1"
        
        collector = PRSummaryCollector(summarizer, auto_retry=True)
        
        with patch("github_tools.collectors.pr_summary_collector.detect_available_providers", return_value=["provider1", "provider2"]):
            with patch("github_tools.summarizers.llm_summarizer.get_provider") as mock_get:
                mock_get.return_value = mock_provider2
                
                summaries = collector.collect_summaries(sample_prs, sample_time_period)
                
                # Should have 3 summaries
                assert len(summaries) == 3
                # First succeeded with provider1
                assert summaries[0]["summary"] == "Summary 1"
                # Others retried with provider2
                assert summaries[1]["summary"] == "Summary from fallback"
                assert summaries[2]["summary"] == "Summary from fallback"
                assert summaries[1]["retried"] is True

