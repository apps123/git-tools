"""Unit tests for cost/FinOps impact analyzer."""

import pytest

from github_tools.summarizers.dimensions.cost_analyzer import CostAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestCostAnalyzer:
    """Tests for CostAnalyzer."""
    
    def test_analyze_with_iac_additions(self):
        """Test cost analysis when IAC files add resources."""
        analyzer = CostAnalyzer()
        pr_context = {
            "title": "Add new EC2 instances",
            "body": "Scaling up infrastructure",
        }
        files = [
            PRFile("terraform/ec2.tf", "added", 50, 0),
        ]
        file_patterns = {"iac": ["terraform/ec2.tf"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Negative", "Neutral"]
    
    def test_analyze_with_iac_removals(self):
        """Test cost analysis when IAC files remove resources."""
        analyzer = CostAnalyzer()
        pr_context = {
            "title": "Remove unused resources",
            "body": "Optimizing infrastructure costs",
        }
        files = [
            PRFile("terraform/cleanup.tf", "modified", 0, 30),
        ]
        file_patterns = {"iac": ["terraform/cleanup.tf"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Positive", "Neutral"]
    
    def test_analyze_no_cost_impact(self):
        """Test cost analysis when no cost impact."""
        analyzer = CostAnalyzer()
        pr_context = {
            "title": "Update documentation",
        }
        files = [
            PRFile("README.md", "modified", 5, 2),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.level == "N/A" or result.is_applicable is False

