"""Unit tests for operational impact analyzer."""

import pytest

from github_tools.summarizers.dimensions.operational_analyzer import OperationalAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestOperationalAnalyzer:
    """Tests for OperationalAnalyzer."""
    
    def test_analyze_with_infrastructure(self):
        """Test operational analysis with infrastructure changes."""
        analyzer = OperationalAnalyzer()
        pr_context = {
            "title": "Deploy new infrastructure",
            "body": "Adding new deployment configuration",
        }
        files = [
            PRFile("docker-compose.yml", "added", 50, 0),
        ]
        file_patterns = {"infrastructure": ["docker-compose.yml"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert "infrastructure" in result.description.lower() or "deployment" in result.description.lower()
    
    def test_analyze_with_monitoring(self):
        """Test operational analysis with monitoring configuration."""
        analyzer = OperationalAnalyzer()
        pr_context = {
            "title": "Add monitoring alerts",
            "body": "Configure SLO metrics",
        }
        files = [
            PRFile("monitoring/alerts.yml", "added", 30, 0),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert "monitor" in result.description.lower() or "slo" in result.description.lower()

