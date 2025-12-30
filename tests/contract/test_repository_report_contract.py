"""Contract tests for repository report output schema."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest


def validate_repository_report_json(report: Dict[str, Any]) -> None:
    """
    Validate repository report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "repositories" in report, "Report must have repositories"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata
    assert "tool_version" in metadata
    assert "period" in metadata
    
    # Validate summary
    summary = report["summary"]
    assert "total_repositories" in summary
    assert isinstance(summary["total_repositories"], int)
    
    # Validate repositories array
    repositories = report["repositories"]
    assert isinstance(repositories, list)
    
    for repo in repositories:
        assert "repository" in repo
        assert "total_contributions" in repo
        assert "active_contributors" in repo
        assert "commits" in repo
        assert "pull_requests" in repo
        assert "issues" in repo
        assert "reviews" in repo
        
        assert isinstance(repo["repository"], str)
        assert isinstance(repo["total_contributions"], int)
        assert isinstance(repo["active_contributors"], int)
        assert isinstance(repo["commits"], int)
        assert isinstance(repo["pull_requests"], int)
        assert isinstance(repo["issues"], int)
        assert isinstance(repo["reviews"], int)


class TestRepositoryReportContract:
    """Contract tests for repository report output format."""
    
    def test_report_has_required_structure(self):
        """Test that report has required top-level structure."""
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
                "total_repositories": 2,
            },
            "repositories": [
                {
                    "repository": "myorg/repo1",
                    "total_contributions": 100,
                    "active_contributors": 5,
                    "commits": 50,
                    "pull_requests": 30,
                    "issues": 15,
                    "reviews": 20,
                },
            ],
        }
        
        validate_repository_report_json(report)
    
    def test_report_is_valid_json(self):
        """Test that report can be serialized to valid JSON."""
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
                "total_repositories": 1,
            },
            "repositories": [
                {
                    "repository": "myorg/repo1",
                    "total_contributions": 50,
                    "active_contributors": 3,
                    "commits": 25,
                    "pull_requests": 15,
                    "issues": 8,
                    "reviews": 10,
                },
            ],
        }
        
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_repository_report_json(parsed)

