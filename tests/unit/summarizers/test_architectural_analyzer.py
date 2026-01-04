"""Unit tests for architectural integrity analyzer."""

import pytest

from github_tools.summarizers.dimensions.architectural_analyzer import ArchitecturalAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestArchitecturalAnalyzer:
    """Tests for ArchitecturalAnalyzer."""
    
    def test_analyze_with_iac(self):
        """Test architectural analysis with IAC files."""
        analyzer = ArchitecturalAnalyzer()
        pr_context = {
            "title": "Add stateless services infrastructure",
            "body": "Aligns with stateless services initiative",
        }
        files = [
            PRFile("terraform/ecs.tf", "added", 100, 0),
        ]
        file_patterns = {"iac": ["terraform/ecs.tf"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Strong", "Moderate"]
        if result.level == "Strong":
            assert "stateless" in result.description.lower() or "initiative" in result.description.lower()

