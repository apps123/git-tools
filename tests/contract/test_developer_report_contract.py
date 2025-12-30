"""Contract tests for developer activity report output schema."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest

from github_tools.models.time_period import TimePeriod


def validate_developer_report_json(report: Dict[str, Any]) -> None:
    """
    Validate developer report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "developers" in report, "Report must have developers"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata, "Metadata must have generated_at"
    assert "tool_version" in metadata, "Metadata must have tool_version"
    assert "period" in metadata, "Metadata must have period"
    
    period = metadata["period"]
    assert "start_date" in period, "Period must have start_date"
    assert "end_date" in period, "Period must have end_date"
    
    # Validate summary
    summary = report["summary"]
    assert "total_developers" in summary, "Summary must have total_developers"
    assert "total_contributions" in summary, "Summary must have total_contributions"
    assert isinstance(summary["total_developers"], int)
    assert isinstance(summary["total_contributions"], int)
    
    # Validate developers array
    developers = report["developers"]
    assert isinstance(developers, list), "developers must be a list"
    
    for dev in developers:
        assert "username" in dev, "Developer must have username"
        assert "total_commits" in dev, "Developer must have total_commits"
        assert "pull_requests_created" in dev, "Developer must have pull_requests_created"
        assert "pull_requests_reviewed" in dev, "Developer must have pull_requests_reviewed"
        assert "pull_requests_merged" in dev, "Developer must have pull_requests_merged"
        assert "issues_created" in dev, "Developer must have issues_created"
        assert "issues_resolved" in dev, "Developer must have issues_resolved"
        assert "code_review_participation" in dev, "Developer must have code_review_participation"
        assert "repositories_contributed" in dev, "Developer must have repositories_contributed"
        
        # Validate types
        assert isinstance(dev["username"], str)
        assert isinstance(dev["total_commits"], int)
        assert isinstance(dev["pull_requests_created"], int)
        assert isinstance(dev["pull_requests_reviewed"], int)
        assert isinstance(dev["pull_requests_merged"], int)
        assert isinstance(dev["issues_created"], int)
        assert isinstance(dev["issues_resolved"], int)
        assert isinstance(dev["code_review_participation"], int)
        assert isinstance(dev["repositories_contributed"], list)
        
        # Validate per_repository_breakdown if present
        if "per_repository_breakdown" in dev:
            breakdown = dev["per_repository_breakdown"]
            assert isinstance(breakdown, dict)
            for repo, metrics in breakdown.items():
                assert isinstance(repo, str)
                assert isinstance(metrics, dict)
                if "commits" in metrics:
                    assert isinstance(metrics["commits"], int)
                if "pull_requests_created" in metrics:
                    assert isinstance(metrics["pull_requests_created"], int)


class TestDeveloperReportContract:
    """Contract tests for developer report output format."""
    
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
                "total_developers": 2,
                "total_contributions": 100,
            },
            "developers": [
                {
                    "username": "alice",
                    "total_commits": 50,
                    "pull_requests_created": 10,
                    "pull_requests_reviewed": 20,
                    "pull_requests_merged": 8,
                    "issues_created": 5,
                    "issues_resolved": 4,
                    "code_review_participation": 20,
                    "repositories_contributed": ["myorg/repo1"],
                },
            ],
        }
        
        validate_developer_report_json(report)
    
    def test_report_with_per_repository_breakdown(self):
        """Test that report can include per-repository breakdown."""
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
                "total_developers": 1,
                "total_contributions": 50,
            },
            "developers": [
                {
                    "username": "alice",
                    "total_commits": 30,
                    "pull_requests_created": 5,
                    "pull_requests_reviewed": 10,
                    "pull_requests_merged": 4,
                    "issues_created": 2,
                    "issues_resolved": 1,
                    "code_review_participation": 10,
                    "repositories_contributed": ["myorg/repo1", "myorg/repo2"],
                    "per_repository_breakdown": {
                        "myorg/repo1": {
                            "commits": 20,
                            "pull_requests_created": 3,
                            "pull_requests_reviewed": 5,
                        },
                        "myorg/repo2": {
                            "commits": 10,
                            "pull_requests_created": 2,
                            "pull_requests_reviewed": 5,
                        },
                    },
                },
            ],
        }
        
        validate_developer_report_json(report)
    
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
                "total_developers": 1,
                "total_contributions": 10,
            },
            "developers": [
                {
                    "username": "alice",
                    "total_commits": 5,
                    "pull_requests_created": 2,
                    "pull_requests_reviewed": 3,
                    "pull_requests_merged": 1,
                    "issues_created": 1,
                    "issues_resolved": 1,
                    "code_review_participation": 3,
                    "repositories_contributed": ["myorg/repo1"],
                },
            ],
        }
        
        # Should serialize without errors
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_developer_report_json(parsed)

