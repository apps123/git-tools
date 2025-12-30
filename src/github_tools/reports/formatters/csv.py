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
    
    def format_team_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format team report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        teams = report_data["teams"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "team_name",
            "total_contributions",
            "active_members",
            "commits",
            "pull_requests",
            "issues",
            "reviews",
            "repositories_contributed",
        ])
        
        # Data rows
        for team in teams:
            repos = ",".join(team["repositories_contributed"])
            writer.writerow([
                team["team_name"],
                team["total_contributions"],
                team["active_members"],
                team["commits"],
                team["pull_requests"],
                team["issues"],
                team["reviews"],
                repos,
            ])
        
        return output.getvalue()
    
    def format_department_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format department report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        departments = report_data["departments"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "department_name",
            "total_contributions",
            "active_members",
            "teams",
        ])
        
        # Data rows
        for dept in departments:
            teams_str = ",".join(dept["teams"])
            writer.writerow([
                dept["department_name"],
                dept["total_contributions"],
                dept["active_members"],
                teams_str,
            ])
        
        return output.getvalue()
    
    def format_pr_summary_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format PR summary report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        prs = report_data["pull_requests"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "id",
            "title",
            "repository",
            "author",
            "created_at",
            "state",
            "summary",
        ])
        
        # Data rows
        for pr in prs:
            writer.writerow([
                pr["id"],
                pr["title"],
                pr["repository"],
                pr["author"],
                pr["created_at"],
                pr.get("state", ""),
                pr["summary"],
            ])
        
        return output.getvalue()
    
    def format_anomaly_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format anomaly report as CSV.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        anomalies = report_data["anomalies"]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "type",
            "entity",
            "entity_type",
            "severity",
            "description",
            "detected_at",
            "previous_value",
            "current_value",
            "change_percent",
        ])
        
        # Data rows
        for anomaly in anomalies:
            writer.writerow([
                anomaly["type"],
                anomaly["entity"],
                anomaly["entity_type"],
                anomaly["severity"],
                anomaly["description"],
                anomaly["detected_at"],
                anomaly["previous_value"],
                anomaly["current_value"],
                anomaly["change_percent"],
            ])
        
        return output.getvalue()

