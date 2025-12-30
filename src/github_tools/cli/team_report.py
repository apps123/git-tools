"""CLI command for team and department contribution reports."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from github_tools.analyzers.team_analyzer import TeamAnalyzer
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.collectors.contribution_collector import ContributionCollector
from github_tools.models.team import Team
from github_tools.models.time_period import TimePeriod
from github_tools.reports.generator import ReportGenerator
from github_tools.utils.cache import FileCache
from github_tools.utils.config import AppConfig
from github_tools.utils.filters import filter_by_teams, filter_internal_contributors, apply_contributor_classification
from github_tools.utils.logging import get_logger
from github_tools.cli.developer_report import parse_date

logger = get_logger(__name__)


def load_team_config(config_path: Optional[Path]) -> List[Team]:
    """
    Load team configuration from file.
    
    Args:
        config_path: Path to team configuration file (JSON or YAML)
    
    Returns:
        List of Team objects
    """
    if not config_path or not config_path.exists():
        logger.warning("No team configuration file provided")
        return []
    
    try:
        with open(config_path) as f:
            if config_path.suffix == ".json":
                data = json.load(f)
            else:
                # Try YAML
                import yaml
                data = yaml.safe_load(f)
            
            teams = []
            for team_data in data.get("teams", []):
                team = Team(
                    name=team_data["name"],
                    display_name=team_data.get("display_name", team_data["name"]),
                    department=team_data.get("department", "unknown"),
                    members=team_data.get("members", []),
                )
                teams.append(team)
            
            return teams
    except Exception as e:
        logger.error(f"Failed to load team configuration: {e}")
        raise


@click.command("team-report")
@click.option(
    "--start-date",
    required=True,
    help="Start date (ISO format: YYYY-MM-DD or relative: '30d', '1w', '1m', 'today', 'yesterday')",
)
@click.option(
    "--end-date",
    required=True,
    help="End date (ISO format: YYYY-MM-DD or relative: 'today', 'yesterday')",
)
@click.option(
    "--team-config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to team configuration file (JSON or YAML)",
)
@click.option(
    "--team",
    "-t",
    multiple=True,
    help="Filter by team name (can specify multiple times)",
)
@click.option(
    "--department",
    "-d",
    multiple=True,
    help="Filter by department name (can specify multiple times)",
)
@click.option(
    "--include-external",
    is_flag=True,
    default=False,
    help="Include external contributors (default: false)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "csv"], case_sensitive=False),
    default="markdown",
    help="Output format (default: markdown)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching, force fresh data collection",
)
@click.pass_context
def team_report(
    ctx: click.Context,
    start_date: str,
    end_date: str,
    team_config: Optional[Path],
    team: tuple,
    department: tuple,
    include_external: bool,
    format: str,
    output: Optional[Path],
    no_cache: bool,
) -> None:
    """
    Generate team and department contribution report.
    
    Aggregates individual contributions into team and department-level metrics
    for organizational insights. Requires team configuration file or team
    membership data from GitHub.
    """
    try:
        config: AppConfig = ctx.obj["config"]
        
        # Parse dates
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            click.echo(f"Error: Invalid date format: {e}", err=True)
            sys.exit(1)
        
        if start > end:
            logger.error("Start date must be before end date")
            click.echo("Error: Start date must be before end date", err=True)
            sys.exit(1)
        
        # Create time period
        time_period = TimePeriod(
            start_date=start,
            end_date=end,
            period_type="custom",
        )
        
        # Load team configuration
        teams = load_team_config(team_config)
        if not teams:
            logger.warning("No teams configured. Team report will be empty.")
            click.echo("Warning: No teams configured. Use --team-config to provide team configuration.", err=True)
            sys.exit(0)
        
        # Initialize components
        github_config = config.get_github_config()
        cache_config = config.get_cache_config()
        
        github_client = GitHubClient(github_config)
        rate_limiter = RateLimiter()
        cache = FileCache(cache_config) if not no_cache else None
        
        collector = ContributionCollector(github_client, rate_limiter, cache)
        analyzer = TeamAnalyzer()
        report_generator = ReportGenerator()
        
        # Get organization repositories
        if not github_config.organization:
            logger.error("Organization not configured.")
            click.echo("Error: Organization not configured.", err=True)
            sys.exit(1)
        
        logger.info("Fetching organization repositories...")
        try:
            repo_models = github_client.get_organization_repositories()
            repositories = [r.full_name for r in repo_models]
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            click.echo(f"Error: Failed to fetch repositories: {e}", err=True)
            sys.exit(1)
        
        if not repositories:
            logger.warning("No repositories found")
            click.echo("Warning: No repositories found", err=True)
            sys.exit(0)
        
        # Collect contributions
        logger.info(f"Collecting contributions from {len(repositories)} repositories...")
        all_contributions = []
        
        for repo in repositories:
            try:
                contributions = collector.collect_contributions(
                    repo,
                    time_period,
                    use_cache=not no_cache,
                )
                all_contributions.extend(contributions)
                logger.debug(f"Collected {len(contributions)} contributions from {repo}")
            except Exception as e:
                logger.warning(f"Failed to collect from {repo}: {e}")
                continue
        
        # Get developers and classify
        unique_devs = {c.developer for c in all_contributions}
        developers = []
        for username in unique_devs:
            dev = github_client.get_user(username)
            if dev:
                developers.append(dev)
        
        # Classify contributors
        developers = apply_contributor_classification(
            developers,
            github_client,
            repository=repositories[0] if repositories else None,
        )
        
        # Filter internal/external
        if not include_external:
            all_contributions = filter_internal_contributors(
                all_contributions,
                developers,
                include_external=False,
            )
        
        # Filter by teams if specified
        if team:
            all_contributions = filter_by_teams(
                all_contributions,
                developers,
                list(team),
            )
        
        # Analyze team metrics
        logger.info("Analyzing team contributions...")
        team_metrics = analyzer.analyze_teams(
            all_contributions,
            developers,
            teams,
            time_period,
        )
        
        # Filter by department if specified
        if department:
            # Filter teams by department
            filtered_teams = [
                t for t in teams if t.department in list(department)
            ]
            team_metrics = [
                tm for tm in team_metrics
                if tm.team_name in [t.name for t in filtered_teams]
            ]
        
        # Analyze department metrics
        department_metrics = analyzer.analyze_departments(
            team_metrics,
            teams,
            time_period,
        )
        
        # Filter departments if specified
        if department:
            department_metrics = [
                dm for dm in department_metrics
                if dm.department_name in list(department)
            ]
        
        # Generate report (team report by default, can be extended for department)
        logger.info("Generating report...")
        report = report_generator.generate_team_report(team_metrics, time_period, format)
        
        # Output report
        if output:
            output.write_text(report)
            logger.info(f"Report written to {output}")
            click.echo(f"Report written to {output}", err=True)
        else:
            click.echo(report)
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        click.echo("Interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

