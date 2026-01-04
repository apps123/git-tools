"""Unit tests for security impact analyzer."""

import pytest

from github_tools.summarizers.dimensions.security_analyzer import SecurityAnalyzer
from github_tools.summarizers.dimensions.base import DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile, FileCategory


class TestSecurityAnalyzer:
    """Tests for SecurityAnalyzer."""
    
    def test_analyze_with_security_config_files(self):
        """Test security analysis when security config files are present."""
        analyzer = SecurityAnalyzer()
        pr_context = {
            "title": "Update API keys",
            "body": "Rotating API keys",
            "repository": "test/repo",
        }
        files = [
            PRFile("secrets/api.key", "modified", 1, 1, patch="+API_KEY=new_key"),
            PRFile("cert.pem", "added", 10, 0),
        ]
        file_patterns = {"security_config": ["secrets/api.key", "cert.pem"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert isinstance(result, DimensionResult)
        assert result.is_applicable is True
        assert result.level in ["High", "Medium", "Low"]
        assert "security" in result.description.lower() or "key" in result.description.lower()
    
    def test_analyze_with_network_changes(self):
        """Test security analysis when network configuration changes."""
        analyzer = SecurityAnalyzer()
        pr_context = {
            "title": "Add new API endpoint",
            "body": "Exposing new public endpoint",
        }
        files = [
            PRFile("api/routes.py", "modified", 50, 10, patch="+@app.route('/api/public')"),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["High", "Medium", "Low", "N/A"]
    
    def test_analyze_no_security_impact(self):
        """Test security analysis when no security concerns."""
        analyzer = SecurityAnalyzer()
        pr_context = {
            "title": "Update README",
            "body": "Documentation update",
        }
        files = [
            PRFile("README.md", "modified", 5, 2),
        ]
        file_patterns = {"documentation": ["README.md"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Low", "N/A"] or result.level == "No Impact"
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        analyzer = SecurityAnalyzer()
        assert analyzer.get_dimension_name() == "security"

