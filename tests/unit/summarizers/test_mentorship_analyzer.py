"""Unit tests for mentorship insights analyzer."""

import pytest

from github_tools.summarizers.dimensions.mentorship_analyzer import MentorshipAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestMentorshipAnalyzer:
    """Tests for MentorshipAnalyzer."""
    
    def test_analyze_with_documentation(self):
        """Test mentorship analysis with documentation."""
        analyzer = MentorshipAnalyzer()
        pr_context = {
            "title": "Add API documentation",
            "body": "Comprehensive documentation explaining API design patterns and rationale",
        }
        files = [
            PRFile("docs/api.md", "added", 200, 0),
        ]
        file_patterns = {"documentation": ["docs/api.md"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert "documentation" in result.description.lower() or "knowledge" in result.description.lower()
    
    def test_analyze_with_detailed_description(self):
        """Test mentorship analysis with detailed PR description."""
        analyzer = MentorshipAnalyzer()
        pr_context = {
            "title": "Refactor authentication",
            "body": "This PR refactors the authentication system to use JWT tokens. The rationale for this change is to improve security and scalability. We chose JWT because it allows stateless authentication which aligns with our microservices architecture. The implementation follows the OAuth 2.0 specification and includes comprehensive error handling.",
        }
        files = [
            PRFile("auth/jwt.py", "added", 150, 0),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert "educational" in result.description.lower() or "explanation" in result.description.lower() or "collaborative" in result.description.lower()

