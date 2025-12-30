"""JSON formatter for reports."""

import json
from typing import Any, Dict


class JSONFormatter:
    """Formatter for JSON output format."""
    
    def format_developer_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format developer report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    def format_repository_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format repository report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    def format_team_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format team report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    def format_department_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format department report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    def format_pr_summary_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format PR summary report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    def format_anomaly_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format anomaly report as JSON.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)

