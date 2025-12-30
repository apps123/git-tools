"""CSV formatter for reports."""

import csv
import io
from typing import Any, Dict, List


class CSVFormatter:
    """Formatter for CSV output format."""
    
    def format_developer_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format developer report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        developers = report_data["developers"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "username",
            "total_commits",
            "pull_requests_created",
            "pull_requests_reviewed",
            "pull_requests_merged",
            "issues_created",
            "issues_resolved",
            "code_review_participation",
            "repositories_contributed",
        ])
        
        # Data rows
        for dev in developers:
            repos = ",".join(dev["repositories_contributed"])
            writer.writerow([
                dev["username"],
                dev["total_commits"],
                dev["pull_requests_created"],
                dev["pull_requests_reviewed"],
                dev["pull_requests_merged"],
                dev["issues_created"],
                dev["issues_resolved"],
                dev["code_review_participation"],
                repos,
            ])
        
        return output.getvalue()
    
    def format_repository_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format repository report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        repositories = report_data["repositories"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "repository",
            "total_contributions",
            "active_contributors",
            "commits",
            "pull_requests",
            "issues",
            "reviews",
            "trend",
        ])
        
        # Data rows
        for repo in repositories:
            writer.writerow([
                repo["repository"],
                repo["total_contributions"],
                repo["active_contributors"],
                repo["commits"],
                repo["pull_requests"],
                repo["issues"],
                repo["reviews"],
                repo.get("trend", ""),
            ])
        
        return output.getvalue()

