"""Integration tests for PR summarization with local agents."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from github_tools.collectors.pr_summary_collector import PRSummaryCollector
from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer


@pytest.fixture
def sample_pr_contribution():
    """Sample PR contribution for testing."""
    return Contribution(
        id="pr1",
        type="pull_request",
        timestamp=datetime.now() - timedelta(days=1),
        repository="test/repo",
        developer="alice",
        title="Add feature X",
        state="merged",
        metadata={
            "body": "This PR adds a new feature.",
            "base_branch": "main",
            "head_branch": "feature-x",
        },
    )


@pytest.fixture
def sample_time_period():
    """Sample time period for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return TimePeriod(
        start_date=start_date,
        end_date=end_date,
        period_type="custom",
    )


@pytest.mark.integration
class TestPRSummaryWithProviders:
    """Integration tests for PR summarization with different providers."""
    
    def test_summarize_with_openai_provider(self, sample_pr_contribution):
        """Test PR summarization with OpenAI provider."""
        mock_provider = Mock()
        mock_provider.summarize.return_value = "This PR adds feature X."
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "openai", "type": "cloud"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        result = summarizer.summarize(sample_pr_contribution)
        
        assert result == "This PR adds feature X."
        mock_provider.summarize.assert_called_once()
    
    def test_summarize_with_claude_local_provider(self, sample_pr_contribution):
        """Test PR summarization with Claude local provider."""
        mock_provider = Mock()
        mock_provider.summarize.return_value = "This PR adds feature X using Claude."
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "claude-local", "type": "local"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        result = summarizer.summarize(sample_pr_contribution)
        
        assert result == "This PR adds feature X using Claude."
    
    def test_summarize_with_gemini_provider(self, sample_pr_contribution):
        """Test PR summarization with Gemini provider."""
        mock_provider = Mock()
        mock_provider.summarize.return_value = "This PR adds feature X using Gemini."
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "gemini", "type": "cloud"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        result = summarizer.summarize(sample_pr_contribution)
        
        assert result == "This PR adds feature X using Gemini."
    
    def test_auto_detect_provider(self, sample_pr_contribution):
        """Test automatic provider detection."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            with patch("github_tools.summarizers.llm_summarizer.detect_available_providers", return_value=["openai"]):
                with patch("github_tools.summarizers.llm_summarizer.get_provider") as mock_get:
                    mock_provider = Mock()
                    mock_provider.summarize.return_value = "Summary"
                    mock_provider.is_available.return_value = True
                    mock_provider.get_metadata.return_value = {"name": "openai"}
                    mock_get.return_value = mock_provider
                    
                    summarizer = LLMSummarizer(auto_detect=True)
                    assert summarizer.provider_name == "openai"
    
    def test_collect_summaries_with_provider(self, sample_pr_contribution, sample_time_period):
        """Test collecting PR summaries with provider."""
        mock_provider = Mock()
        mock_provider.summarize.return_value = "Summary"
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "openai"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        collector = PRSummaryCollector(summarizer, auto_retry=False)
        
        summaries = collector.collect_summaries(
            [sample_pr_contribution],
            sample_time_period,
        )
        
        assert len(summaries) == 1
        assert summaries[0]["summary"] == "Summary"
        assert summaries[0]["provider"] == "openai"

