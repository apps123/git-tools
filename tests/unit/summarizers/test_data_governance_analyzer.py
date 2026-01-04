"""Unit tests for data governance impact analyzer."""

import pytest

from github_tools.summarizers.dimensions.data_governance_analyzer import DataGovernanceAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestDataGovernanceAnalyzer:
    """Tests for DataGovernanceAnalyzer."""
    
    def test_analyze_with_data_files(self):
        """Test data governance analysis with data files."""
        analyzer = DataGovernanceAnalyzer()
        pr_context = {
            "title": "Add training dataset",
            "body": "Adding new CSV dataset",
        }
        files = [
            PRFile("data/training.csv", "added", 1000, 0),
        ]
        file_patterns = {"data_file": ["data/training.csv"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Impact", "No Impact", "N/A"]
        assert "data" in result.description.lower()
    
    def test_analyze_with_schema_changes(self):
        """Test data governance analysis with schema changes."""
        analyzer = DataGovernanceAnalyzer()
        pr_context = {
            "title": "Update database schema",
            "body": "Adding new columns for user preferences",
        }
        files = [
            PRFile("schema.sql", "modified", 50, 10),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True

