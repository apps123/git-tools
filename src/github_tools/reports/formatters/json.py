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

