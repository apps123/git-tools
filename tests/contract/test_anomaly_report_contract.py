"""Contract tests for anomaly detection report output schema."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest


def validate_anomaly_report_json(report: Dict[str, Any]) -> None:
    """
    Validate anomaly report JSON structure against contract.
    
    Args:
        report: Report dictionary to validate
    
    Raises:
        AssertionError: If report doesn't match contract
    """
    # Check top-level structure
    assert "metadata" in report, "Report must have metadata"
    assert "summary" in report, "Report must have summary"
    assert "anomalies" in report, "Report must have anomalies"
    
    # Validate metadata
    metadata = report["metadata"]
    assert "generated_at" in metadata
    assert "tool_version" in metadata
    assert "period" in metadata
    
    # Validate summary
    summary = report["summary"]
    assert "total_anomalies" in summary
    assert isinstance(summary["total_anomalies"], int)
    
    # Validate anomalies array
    anomalies = report["anomalies"]
    assert isinstance(anomalies, list)
    
    for anomaly in anomalies:
        assert "type" in anomaly
        assert "entity" in anomaly
        assert "severity" in anomaly
        assert "description" in anomaly
        assert "detected_at" in anomaly
        
        assert isinstance(anomaly["type"], str)
        assert isinstance(anomaly["entity"], str)
        assert isinstance(anomaly["severity"], str)
        assert isinstance(anomaly["description"], str)
        assert anomaly["severity"] in ["low", "medium", "high", "critical"]


class TestAnomalyReportContract:
    """Contract tests for anomaly report output format."""
    
    def test_report_has_required_structure(self):
        """Test that anomaly report has required top-level structure."""
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
                "total_anomalies": 2,
            },
            "anomalies": [
                {
                    "type": "contribution_drop",
                    "entity": "alice",
                    "severity": "medium",
                    "description": "Contribution count dropped by 60% compared to previous period",
                    "detected_at": "2024-12-20T10:00:00Z",
                    "previous_value": 100,
                    "current_value": 40,
                    "change_percent": -60.0,
                },
            ],
        }
        
        validate_anomaly_report_json(report)
    
    def test_report_is_valid_json(self):
        """Test that anomaly report can be serialized to valid JSON."""
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
                "total_anomalies": 1,
            },
            "anomalies": [
                {
                    "type": "contribution_spike",
                    "entity": "myorg/repo1",
                    "severity": "high",
                    "description": "Contribution count increased by 150% compared to previous period",
                    "detected_at": "2024-12-25T15:00:00Z",
                    "previous_value": 50,
                    "current_value": 125,
                    "change_percent": 150.0,
                },
            ],
        }
        
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        validate_anomaly_report_json(parsed)

