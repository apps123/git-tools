"""Report generation library for GitHub contribution analytics."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from github_tools import __version__
from github_tools.analyzers.developer_analyzer import DeveloperMetrics
from github_tools.analyzers.repository_analyzer import RepositoryMetrics
from github_tools.analyzers.team_analyzer import TeamMetrics, DepartmentMetrics
from github_tools.models.time_period import TimePeriod
from github_tools.reports.formatters.json import JSONFormatter
from github_tools.reports.formatters.markdown import MarkdownFormatter
from github_tools.reports.formatters.csv import CSVFormatter
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Generates reports in multiple formats (JSON, Markdown, CSV).
    
    Supports developer activity reports, repository reports, team reports, etc.
    """
    
    def __init__(self):
        """Initialize report generator."""
        self.json_formatter = JSONFormatter()
        self.markdown_formatter = MarkdownFormatter()
        self.csv_formatter = CSVFormatter()
    
    def generate_developer_report(
        self,
        metrics: List[DeveloperMetrics],
        time_period: TimePeriod,
        format: str = "markdown",
    ) -> str:
        """
        Generate developer activity report.
        
        Args:
            metrics: List of developer metrics
            time_period: Time period for the report
            format: Output format (json, markdown, csv)
        
        Returns:
            Formatted report string
        """
        report_data = self._build_developer_report_data(metrics, time_period)
        
        if format == "json":
            return self.json_formatter.format_developer_report(report_data)
        elif format == "csv":
            return self.csv_formatter.format_developer_report(report_data)
        elif format == "markdown":
            return self.markdown_formatter.format_developer_report(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _build_developer_report_data(
        self,
        metrics: List[DeveloperMetrics],
        time_period: TimePeriod,
    ) -> Dict[str, Any]:
        """
        Build developer report data structure.
        
        Args:
            metrics: List of developer metrics
            time_period: Time period for the report
        
        Returns:
            Report data dictionary
        """
        # Calculate summary
        total_contributions = sum(m.total_contributions for m in metrics)
        
        # Build developers array
        developers = []
        for metric in metrics:
            dev_data = {
                "username": metric.developer,
                "total_commits": metric.total_commits,
                "pull_requests_created": metric.pull_requests_created,
                "pull_requests_reviewed": metric.pull_requests_reviewed,
                "pull_requests_merged": metric.pull_requests_merged,
                "issues_created": metric.issues_created,
                "issues_resolved": metric.issues_resolved,
                "code_review_participation": metric.code_review_participation,
                "repositories_contributed": sorted(set(metric.repositories_contributed)),
            }
            
            # Add per-repository breakdown if available
            if metric.per_repository_breakdown:
                dev_data["per_repository_breakdown"] = {
                    repo: {
                        "commits": breakdown.get("commits", 0),
                        "pull_requests_created": breakdown.get("pull_requests_created", 0),
                        "pull_requests_reviewed": breakdown.get("pull_requests_reviewed", 0),
                    }
                    for repo, breakdown in metric.per_repository_breakdown.items()
                }
            
            developers.append(dev_data)
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": __version__,
                "period": {
                    "start_date": time_period.start_date.isoformat(),
                    "end_date": time_period.end_date.isoformat(),
                },
            },
            "summary": {
                "total_developers": len(metrics),
                "total_contributions": total_contributions,
            },
            "developers": developers,
        }
    
    def generate_repository_report(
        self,
        metrics: List[RepositoryMetrics],
        time_period: TimePeriod,
        format: str = "markdown",
    ) -> str:
        """
        Generate repository contribution report.
        
        Args:
            metrics: List of repository metrics
            time_period: Time period for the report
            format: Output format (json, markdown, csv)
        
        Returns:
            Formatted report string
        """
        report_data = self._build_repository_report_data(metrics, time_period)
        
        if format == "json":
            return self.json_formatter.format_repository_report(report_data)
        elif format == "csv":
            return self.csv_formatter.format_repository_report(report_data)
        elif format == "markdown":
            return self.markdown_formatter.format_repository_report(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _build_repository_report_data(
        self,
        metrics: List[RepositoryMetrics],
        time_period: TimePeriod,
    ) -> Dict[str, Any]:
        """
        Build repository report data structure.
        
        Args:
            metrics: List of repository metrics
            time_period: Time period for the report
        
        Returns:
            Report data dictionary
        """
        repositories = []
        for metric in metrics:
            repo_data = {
                "repository": metric.repository,
                "total_contributions": metric.total_contributions,
                "active_contributors": metric.active_contributors,
                "contributor_list": sorted(metric.contributor_list),
                "commits": metric.commits,
                "pull_requests": metric.pull_requests,
                "issues": metric.issues,
                "reviews": metric.reviews,
            }
            
            if metric.trend:
                repo_data["trend"] = metric.trend
            
            if metric.contribution_distribution:
                repo_data["contribution_distribution"] = metric.contribution_distribution
            
            repositories.append(repo_data)
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": __version__,
                "period": {
                    "start_date": time_period.start_date.isoformat(),
                    "end_date": time_period.end_date.isoformat(),
                },
            },
            "summary": {
                "total_repositories": len(metrics),
            },
            "repositories": repositories,
        }
    
    def generate_team_report(
        self,
        metrics: List[TeamMetrics],
        time_period: TimePeriod,
        format: str = "markdown",
    ) -> str:
        """
        Generate team contribution report.
        
        Args:
            metrics: List of team metrics
            time_period: Time period for the report
            format: Output format (json, markdown, csv)
        
        Returns:
            Formatted report string
        """
        report_data = self._build_team_report_data(metrics, time_period)
        
        if format == "json":
            return self.json_formatter.format_team_report(report_data)
        elif format == "csv":
            return self.csv_formatter.format_team_report(report_data)
        elif format == "markdown":
            return self.markdown_formatter.format_team_report(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _build_team_report_data(
        self,
        metrics: List[TeamMetrics],
        time_period: TimePeriod,
    ) -> Dict[str, Any]:
        """
        Build team report data structure.
        
        Args:
            metrics: List of team metrics
            time_period: Time period for the report
        
        Returns:
            Report data dictionary
        """
        teams = []
        for metric in metrics:
            team_data = {
                "team_name": metric.team_name,
                "total_contributions": metric.total_contributions,
                "active_members": metric.active_members,
                "member_list": sorted(metric.member_list),
                "commits": metric.commits,
                "pull_requests": metric.pull_requests,
                "issues": metric.issues,
                "reviews": metric.reviews,
                "repositories_contributed": sorted(set(metric.repositories_contributed)),
            }
            teams.append(team_data)
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": __version__,
                "period": {
                    "start_date": time_period.start_date.isoformat(),
                    "end_date": time_period.end_date.isoformat(),
                },
            },
            "summary": {
                "total_teams": len(metrics),
            },
            "teams": teams,
        }
    
    def generate_department_report(
        self,
        metrics: List[DepartmentMetrics],
        time_period: TimePeriod,
        format: str = "markdown",
    ) -> str:
        """
        Generate department contribution report.
        
        Args:
            metrics: List of department metrics
            time_period: Time period for the report
            format: Output format (json, markdown, csv)
        
        Returns:
            Formatted report string
        """
        report_data = self._build_department_report_data(metrics, time_period)
        
        if format == "json":
            return self.json_formatter.format_department_report(report_data)
        elif format == "csv":
            return self.csv_formatter.format_department_report(report_data)
        elif format == "markdown":
            return self.markdown_formatter.format_department_report(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _build_department_report_data(
        self,
        metrics: List[DepartmentMetrics],
        time_period: TimePeriod,
    ) -> Dict[str, Any]:
        """
        Build department report data structure.
        
        Args:
            metrics: List of department metrics
            time_period: Time period for the report
        
        Returns:
            Report data dictionary
        """
        departments = []
        for metric in metrics:
            dept_data = {
                "department_name": metric.department_name,
                "total_contributions": metric.total_contributions,
                "active_members": metric.active_members,
                "member_list": sorted(metric.member_list),
                "teams": sorted(metric.teams),
            }
            departments.append(dept_data)
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": __version__,
                "period": {
                    "start_date": time_period.start_date.isoformat(),
                    "end_date": time_period.end_date.isoformat(),
                },
            },
            "summary": {
                "total_departments": len(metrics),
            },
            "departments": departments,
        }

