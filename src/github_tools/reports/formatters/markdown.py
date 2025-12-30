"""Markdown formatter for reports."""

from typing import Any, Dict


class MarkdownFormatter:
    """Formatter for Markdown output format."""
    
    def format_developer_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format developer report as Markdown.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            Markdown string
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        developers = report_data["developers"]
        
        lines = []
        
        # Header
        lines.append("# Developer Activity Report")
        lines.append("")
        
        # Metadata
        period = metadata["period"]
        lines.append(f"**Period**: {period['start_date']} to {period['end_date']}")
        lines.append(f"**Generated**: {metadata['generated_at']}")
        lines.append(f"**Tool Version**: {metadata['tool_version']}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Developers: {summary['total_developers']}")
        lines.append(f"- Total Contributions: {summary['total_contributions']}")
        lines.append("")
        
        # Developers table
        lines.append("## Developers")
        lines.append("")
        lines.append(
            "| Username | Commits | PRs Created | PRs Reviewed | "
            "PRs Merged | Issues Created | Issues Resolved | Repositories |"
        )
        lines.append(
            "|----------|---------|-------------|--------------|"
            "------------|----------------|-----------------|--------------|"
        )
        
        for dev in developers:
            repos = ", ".join(dev["repositories_contributed"])
            lines.append(
                f"| {dev['username']} | "
                f"{dev['total_commits']} | "
                f"{dev['pull_requests_created']} | "
                f"{dev['pull_requests_reviewed']} | "
                f"{dev['pull_requests_merged']} | "
                f"{dev['issues_created']} | "
                f"{dev['issues_resolved']} | "
                f"{repos} |"
            )
        
        lines.append("")
        
        # Per-repository breakdown (if available)
        has_breakdown = any("per_repository_breakdown" in dev for dev in developers)
        if has_breakdown:
            lines.append("## Per-Repository Breakdown")
            lines.append("")
            for dev in developers:
                if "per_repository_breakdown" in dev:
                    lines.append(f"### {dev['username']}")
                    lines.append("")
                    for repo, breakdown in dev["per_repository_breakdown"].items():
                        lines.append(f"**{repo}**:")
                        lines.append(f"- Commits: {breakdown.get('commits', 0)}")
                        lines.append(
                            f"- PRs Created: {breakdown.get('pull_requests_created', 0)}"
                        )
                        lines.append(
                            f"- PRs Reviewed: {breakdown.get('pull_requests_reviewed', 0)}"
                        )
                        lines.append("")
        
        return "\n".join(lines)
    
    def format_repository_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format repository report as Markdown.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            Markdown string
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        repositories = report_data["repositories"]
        
        lines = []
        
        # Header
        lines.append("# Repository Contribution Report")
        lines.append("")
        
        # Metadata
        period = metadata["period"]
        lines.append(f"**Period**: {period['start_date']} to {period['end_date']}")
        lines.append(f"**Generated**: {metadata['generated_at']}")
        lines.append(f"**Tool Version**: {metadata['tool_version']}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Repositories: {summary['total_repositories']}")
        lines.append("")
        
        # Repositories table
        lines.append("## Repositories")
        lines.append("")
        lines.append(
            "| Repository | Contributions | Contributors | Commits | "
            "PRs | Issues | Reviews | Trend |"
        )
        lines.append(
            "|-----------|---------------|--------------|---------|"
            "-----|--------|---------|-------|"
        )
        
        for repo in repositories:
            trend = repo.get("trend", "N/A")
            lines.append(
                f"| {repo['repository']} | "
                f"{repo['total_contributions']} | "
                f"{repo['active_contributors']} | "
                f"{repo['commits']} | "
                f"{repo['pull_requests']} | "
                f"{repo['issues']} | "
                f"{repo['reviews']} | "
                f"{trend} |"
            )
        
        lines.append("")
        
        # Contribution distribution (if available)
        has_distribution = any(
            "contribution_distribution" in repo for repo in repositories
        )
        if has_distribution:
            lines.append("## Contribution Distribution")
            lines.append("")
            for repo in repositories:
                if "contribution_distribution" in repo:
                    lines.append(f"### {repo['repository']}")
                    lines.append("")
                    for dev, count in sorted(
                        repo["contribution_distribution"].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:10]:  # Top 10 contributors
                        lines.append(f"- {dev}: {count} contributions")
                    lines.append("")
        
        return "\n".join(lines)
    
    def format_team_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format team report as Markdown.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            Markdown string
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        teams = report_data["teams"]
        
        lines = []
        
        # Header
        lines.append("# Team Contribution Report")
        lines.append("")
        
        # Metadata
        period = metadata["period"]
        lines.append(f"**Period**: {period['start_date']} to {period['end_date']}")
        lines.append(f"**Generated**: {metadata['generated_at']}")
        lines.append(f"**Tool Version**: {metadata['tool_version']}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Teams: {summary['total_teams']}")
        lines.append("")
        
        # Teams table
        lines.append("## Teams")
        lines.append("")
        lines.append(
            "| Team | Contributions | Members | Commits | "
            "PRs | Issues | Reviews | Repositories |"
        )
        lines.append(
            "|------|---------------|---------|---------|"
            "-----|--------|---------|--------------|"
        )
        
        for team in teams:
            repos = ", ".join(team["repositories_contributed"])
            lines.append(
                f"| {team['team_name']} | "
                f"{team['total_contributions']} | "
                f"{team['active_members']} | "
                f"{team['commits']} | "
                f"{team['pull_requests']} | "
                f"{team['issues']} | "
                f"{team['reviews']} | "
                f"{repos} |"
            )
        
        lines.append("")
        
        return "\n".join(lines)
    
    def format_department_report(self, report_data: Dict[str, Any]) -> str:
        """
        Format department report as Markdown.
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            Markdown string
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        departments = report_data["departments"]
        
        lines = []
        
        # Header
        lines.append("# Department Contribution Report")
        lines.append("")
        
        # Metadata
        period = metadata["period"]
        lines.append(f"**Period**: {period['start_date']} to {period['end_date']}")
        lines.append(f"**Generated**: {metadata['generated_at']}")
        lines.append(f"**Tool Version**: {metadata['tool_version']}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Departments: {summary['total_departments']}")
        lines.append("")
        
        # Departments table
        lines.append("## Departments")
        lines.append("")
        lines.append(
            "| Department | Contributions | Members | Teams |"
        )
        lines.append(
            "|------------|---------------|---------|-------|"
        )
        
        for dept in departments:
            teams_str = ", ".join(dept["teams"])
            lines.append(
                f"| {dept['department_name']} | "
                f"{dept['total_contributions']} | "
                f"{dept['active_members']} | "
                f"{teams_str} |"
            )
        
        lines.append("")
        
        return "\n".join(lines)

