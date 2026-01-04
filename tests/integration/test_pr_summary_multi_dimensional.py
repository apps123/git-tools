"""Integration tests for multi-dimensional PR summary generation."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from github_tools.collectors.pr_summary_collector import PRSummaryCollector
from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer
from github_tools.summarizers.file_pattern_detector import PRFile


@pytest.fixture
def sample_pr_contribution():
    """Sample PR contribution for testing."""
    return Contribution(
        id="pr-1024",
        type="pull_request",
        timestamp=datetime.now() - timedelta(days=1),
        repository="test/repo",
        developer="alice",
        title="Migration to New Caching Layer",
        state="merged",
        metadata={
            "body": "Refactors the primary data-retrieval service to use a distributed Redis cache instead of local in-memory storage.",
            "base_branch": "main",
            "head_branch": "feature-cache",
            "number": 1024,
        },
    )


@pytest.fixture
def sample_pr_files():
    """Sample PR files for testing."""
    return [
        PRFile("terraform/redis.tf", "added", 50, 0),
        PRFile("infra/cache.go", "modified", 100, 20),
    ]


@pytest.fixture
def sample_time_period():
    """Sample time period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return TimePeriod(start_date=start_date, end_date=end_date, period_type="custom")


@pytest.mark.integration
class TestPRSummaryMultiDimensional:
    """Integration tests for multi-dimensional PR summary generation."""
    
    def test_dimensional_analysis_all_dimensions(self, sample_pr_contribution, sample_pr_files):
        """Test that dimensional analysis includes all 7 dimensions."""
        mock_provider = Mock()
        mock_provider.summarize.return_value = "Test summary"
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "test-provider"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        
        result = summarizer.summarize_dimensional(
            sample_pr_contribution,
            sample_pr_files,
            use_llm=False,  # Use rule-based for this test
        )
        
        assert "summary" in result
        assert "dimensions" in result
        assert len(result["dimensions"]) == 7
        
        # Verify all dimensions are present
        assert "security" in result["dimensions"]
        assert "cost" in result["dimensions"]
        assert "operational" in result["dimensions"]
        assert "architectural" in result["dimensions"]
        assert "mentorship" in result["dimensions"]
        assert "data_governance" in result["dimensions"]
        assert "ai_governance" in result["dimensions"]
    
    def test_dimensional_analysis_with_iac_files(self, sample_pr_contribution):
        """Test dimensional analysis with IAC files."""
        iac_files = [
            PRFile("terraform/redis.tf", "added", 50, 0),
            PRFile("terraform/variables.tf", "modified", 10, 5),
        ]
        
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "test-provider"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        
        result = summarizer.summarize_dimensional(
            sample_pr_contribution,
            iac_files,
            use_llm=False,
        )
        
        # Should detect infrastructure changes
        assert result["dimensions"]["cost"]["is_applicable"] is True
        assert result["dimensions"]["architectural"]["is_applicable"] is True
    
    def test_formatted_output_structure(self, sample_pr_contribution, sample_pr_files):
        """Test that formatted output follows expected structure."""
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.get_metadata.return_value = {"name": "test-provider"}
        
        summarizer = LLMSummarizer(provider=mock_provider, auto_detect=False)
        
        result = summarizer.summarize_dimensional(
            sample_pr_contribution,
            sample_pr_files,
            use_llm=False,
        )
        
        assert "formatted" in result
        formatted = result["formatted"]
        
        # Check format includes key elements
        assert "PR:" in formatted or "Migration" in formatted
        assert "Summary:" in formatted or "* Summary:" in formatted
        # Should include dimension indicators
        assert "Security" in formatted or "⚠️" in formatted
        assert "Cost" in formatted or "💰" in formatted

