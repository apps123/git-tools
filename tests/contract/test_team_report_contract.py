"""Contract tests for team and department report output schema."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest


def validate_team_report_json(report: Dict[str, Any]) -> None:
    """
    Validate team report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "teams" in report, "Report must have teams"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata
    assert "tool_version" in metadata
    assert "period" in metadata
    
    # Validate summary
    summary = report["summary"]
    assert "total_teams" in summary
    assert isinstance(summary["total_teams"], int)
    
    # Validate teams array
    teams = report["teams"]
    assert isinstance(teams, list)
    
    for team in teams:
        assert "team_name" in team
        assert "total_contributions" in team
        assert "active_members" in team
        assert "commits" in team
        assert "pull_requests" in team
        assert "issues" in team
        assert "reviews" in team
        
        assert isinstance(team["team_name"], str)
        assert isinstance(team["total_contributions"], int)
        assert isinstance(team["active_members"], int)


def validate_department_report_json(report: Dict[str, Any]) -> None:
    """
    Validate department report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "departments" in report, "Report must have departments"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata
    assert "tool_version" in metadata
    assert "period" in metadata
    
    # Validate summary
    summary = report["summary"]
    assert "total_departments" in summary
    assert isinstance(summary["total_departments"], int)
    
    # Validate departments array
    departments = report["departments"]
    assert isinstance(departments, list)
    
    for dept in departments:
        assert "department_name" in dept
        assert "total_contributions" in dept
        assert "active_members" in dept
        assert "teams" in dept
        
        assert isinstance(dept["department_name"], str)
        assert isinstance(dept["total_contributions"], int)
        assert isinstance(dept["active_members"], int)
        assert isinstance(dept["teams"], list)


class TestTeamReportContract:
    """Contract tests for team report output format."""
    
    def test_report_has_required_structure(self):
        """Test that team report has required top-level structure."""
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
                "total_teams": 2,
            },
            "teams": [
                {
                    "team_name": "backend-team",
                    "total_contributions": 200,
                    "active_members": 5,
                    "commits": 100,
                    "pull_requests": 60,
                    "issues": 30,
                    "reviews": 40,
                },
            ],
        }
        
        validate_team_report_json(report)
    
    def test_report_is_valid_json(self):
        """Test that team report can be serialized to valid JSON."""
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
                "total_teams": 1,
            },
            "teams": [
                {
                    "team_name": "backend-team",
                    "total_contributions": 100,
                    "active_members": 3,
                    "commits": 50,
                    "pull_requests": 30,
                    "issues": 15,
                    "reviews": 20,
                },
            ],
        }
        
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_team_report_json(parsed)


class TestDepartmentReportContract:
    """Contract tests for department report output format."""
    
    def test_report_has_required_structure(self):
        """Test that department report has required top-level structure."""
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
                "total_departments": 2,
            },
            "departments": [
                {
                    "department_name": "engineering",
                    "total_contributions": 500,
                    "active_members": 15,
                    "teams": ["backend-team", "frontend-team"],
                },
            ],
        }
        
        validate_department_report_json(report)
    
    def test_report_is_valid_json(self):
        """Test that department report can be serialized to valid JSON."""
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
                "total_departments": 1,
            },
            "departments": [
                {
                    "department_name": "engineering",
                    "total_contributions": 300,
                    "active_members": 10,
                    "teams": ["backend-team"],
                },
            ],
        }
        
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_department_report_json(parsed)

