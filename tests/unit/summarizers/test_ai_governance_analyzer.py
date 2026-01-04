"""Unit tests for AI governance impact analyzer."""

import pytest

from github_tools.summarizers.dimensions.ai_governance_analyzer import AIGovernanceAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


class TestAIGovernanceAnalyzer:
    """Tests for AIGovernanceAnalyzer."""
    
    def test_analyze_with_ai_model_files(self):
        """Test AI governance analysis with model files."""
        analyzer = AIGovernanceAnalyzer()
        pr_context = {
            "title": "Add ML model",
            "body": "Training new classification model",
        }
        files = [
            PRFile("models/classifier.pkl", "added", 500, 0),
        ]
        file_patterns = {"ai_model": ["models/classifier.pkl"]}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert result.level in ["Impact", "Low", "Minor", "N/A"]
        assert "model" in result.description.lower() or "ai" in result.description.lower()
    
    def test_analyze_with_external_llm(self):
        """Test AI governance analysis with external LLM usage."""
        analyzer = AIGovernanceAnalyzer()
        pr_context = {
            "title": "Integrate OpenAI API",
            "body": "Using external OpenAI API for text generation",
        }
        files = [
            PRFile("services/llm_client.py", "added", 100, 0),
        ]
        file_patterns = {}
        
        result = analyzer.analyze(pr_context, files, file_patterns)
        
        assert result.is_applicable is True
        assert "external" in result.description.lower() or "exfiltration" in result.description.lower() or "supply chain" in result.description.lower()

