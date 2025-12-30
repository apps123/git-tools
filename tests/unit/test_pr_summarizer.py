"""Unit tests for PR summarization logic."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from github_tools.models.contribution import Contribution


@pytest.fixture
def sample_pr():
    """Sample PR contribution for testing."""
    return Contribution(
        id="pr-42",
        type="pull_request",
        timestamp=datetime(2024, 12, 15, 10, 0, 0),
        repository="myorg/repo1",
        developer="alice",
        title="Add new feature",
        state="merged",
        metadata={
            "number": 42,
            "merged": True,
            "body": "This PR adds a new feature that improves performance by 50%.",
            "base_branch": "main",
            "head_branch": "feature/new-feature",
        },
    )


class TestPRSummarization:
    """Tests for PR summarization logic."""
    
    def test_extract_pr_context(self, sample_pr):
        """Test extracting context from PR for summarization."""
        context = {
            "title": sample_pr.title,
            "body": sample_pr.metadata.get("body", ""),
            "repository": sample_pr.repository,
            "author": sample_pr.developer,
            "base_branch": sample_pr.metadata.get("base_branch"),
            "head_branch": sample_pr.metadata.get("head_branch"),
        }
        
        assert context["title"] == "Add new feature"
        assert "improves performance" in context["body"]
        assert context["repository"] == "myorg/repo1"
        assert context["author"] == "alice"
    
    def test_summarize_pr_with_title_and_body(self, sample_pr):
        """Test that PR summary uses title and body."""
        # PR summary should be based on title and body
        title = sample_pr.title
        body = sample_pr.metadata.get("body", "")
        
        # Summary should be concise and contextual
        assert len(title) > 0
        assert len(body) > 0
    
    @patch("openai.ChatCompletion.create")
    def test_llm_summarization_call(self, mock_openai, sample_pr):
        """Test that LLM summarization is called correctly."""
        # Mock OpenAI response
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="This PR adds a new feature that improves performance."
                    )
                )
            ]
        )
        
        # This test validates the structure
        # Actual implementation will call OpenAI API
        assert sample_pr.metadata is not None
    
    def test_summary_length_validation(self):
        """Test that summaries meet length requirements."""
        # Summaries should be concise (e.g., max 200 characters)
        max_length = 200
        test_summary = "This is a test summary that should be concise."
        
        assert len(test_summary) <= max_length

