"""Unit tests for multi-dimensional analyzer orchestrator."""

import pytest

from github_tools.summarizers.multi_dimensional_analyzer import MultiDimensionalAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestMultiDimensionalAnalyzer:
    """Tests for MultiDimensionalAnalyzer."""
    
    def test_analyze_all_dimensions(self):
        """Test that all dimensions are analyzed."""
        analyzer = MultiDimensionalAnalyzer()
        pr_context = {
            "title": "Migration to New Caching Layer",
            "body": "Refactors the primary data-retrieval service to use a distributed Redis cache",
        }
        files = [
            PRFile("infra/redis.tf", "added", 50, 0),
        ]
        
        results = analyzer.analyze(pr_context, files)
        
        # All 7 dimensions should be analyzed
        assert len(results) == 7
        assert "security" in results
        assert "cost" in results
        assert "operational" in results
        assert "architectural" in results
        assert "mentorship" in results
        assert "data_governance" in results
        assert "ai_governance" in results
    
    def test_format_summary(self):
        """Test summary formatting."""
        from github_tools.summarizers.dimensions.base import DimensionResult
        
        analyzer = MultiDimensionalAnalyzer()
        dimensional_results = {
            "security": DimensionResult("High", "Security concern detected"),
            "cost": DimensionResult("Positive", "Cost optimization"),
            "operational": DimensionResult("Applicable", "Monitoring configured"),
            "architectural": DimensionResult("Strong", "Aligns with principles"),
            "mentorship": DimensionResult("Insight", "Good collaboration"),
            "data_governance": DimensionResult("No Impact", "No data changes"),
            "ai_governance": DimensionResult("N/A", "No AI components"),
        }
        
        summary = analyzer.format_summary(
            "PR #123: Test PR",
            "This is a test PR",
            dimensional_results,
            use_emoji=True,
        )
        
        assert "PR: PR #123: Test PR" in summary
        assert "Summary: This is a test PR" in summary
        assert "⚠️ Security Impact" in summary
        assert "💰 Cost/FinOps Impact" in summary
        assert "High" in summary
        assert "Positive" in summary
    
    def test_format_summary_no_emoji(self):
        """Test summary formatting without emojis."""
        from github_tools.summarizers.dimensions.base import DimensionResult
        
        analyzer = MultiDimensionalAnalyzer()
        dimensional_results = {
            "security": DimensionResult("High", "Security concern"),
        }
        
        summary = analyzer.format_summary(
            "PR #123",
            "Test",
            dimensional_results,
            use_emoji=False,
        )
        
        assert "[Security Impact]" in summary
        assert "⚠️" not in summary

