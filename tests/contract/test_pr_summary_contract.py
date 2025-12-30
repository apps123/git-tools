"""Contract tests for PR summary report output schema."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest


def validate_pr_summary_json(report: Dict[str, Any]) -> None:
    """
    Validate PR summary report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "pull_requests" in report, "Report must have pull_requests"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata
    assert "tool_version" in metadata
    assert "period" in metadata
    
    # Validate summary
    summary = report["summary"]
    assert "total_prs" in summary
    assert isinstance(summary["total_prs"], int)
    
    # Validate pull_requests array
    prs = report["pull_requests"]
    assert isinstance(prs, list)
    
    for pr in prs:
        assert "id" in pr
        assert "title" in pr
        assert "repository" in pr
        assert "author" in pr
        assert "created_at" in pr
        assert "summary" in pr
        
        assert isinstance(pr["id"], str)
        assert isinstance(pr["title"], str)
        assert isinstance(pr["repository"], str)
        assert isinstance(pr["author"], str)
        assert isinstance(pr["summary"], str)


class TestPRSummaryContract:
    """Contract tests for PR summary report output format."""
    
    def test_report_has_required_structure(self):
        """Test that PR summary report has required top-level structure."""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": "0.1.0",
                "period": {
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                },
            },
            "summary": {
                "total_prs": 2,
            },
            "pull_requests": [
                {
                    "id": "pr-42",
                    "title": "Add new feature",
                    "repository": "myorg/repo1",
                    "author": "alice",
                    "created_at": "2024-12-15T10:00:00Z",
                    "summary": "This PR adds a new feature that improves performance.",
                },
            ],
        }
        
        validate_pr_summary_json(report)
    
    def test_report_is_valid_json(self):
        """Test that PR summary report can be serialized to valid JSON."""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": "0.1.0",
                "period": {
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                },
            },
            "summary": {
                "total_prs": 1,
            },
            "pull_requests": [
                {
                    "id": "pr-1",
                    "title": "Fix bug",
                    "repository": "myorg/repo1",
                    "author": "bob",
                    "created_at": "2024-12-20T14:00:00Z",
                    "summary": "This PR fixes a critical bug in authentication.",
                },
            ],
        }
        
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_pr_summary_json(parsed)

