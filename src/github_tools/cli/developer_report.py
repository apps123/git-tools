"""CLI command for developer activity reports."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from github_tools.analyzers.developer_analyzer import DeveloperAnalyzer
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.collectors.contribution_collector import ContributionCollector
from github_tools.models.time_period import TimePeriod, PeriodType
from github_tools.reports.generator import ReportGenerator
from github_tools.utils.cache import FileCache
from github_tools.utils.config import AppConfig
from github_tools.utils.filters import (
    filter_by_repositories,
    filter_by_developers,
    filter_internal_contributors,
    apply_contributor_classification,
)
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


def parse_date(date_str: str) -> datetime:
    """
    Parse date string (ISO format or relative).
    
    Args:
        date_str: Date string (ISO format, "today", "yesterday", "30d", "1w", "1m")
    
    Returns:
        Datetime object
    """
    date_str = date_str.lower().strip()
    
    if date_str == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str == "yesterday":
        return (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif date_str.endswith("d"):
        days = int(date_str[:-1])
        return datetime.now() - timedelta(days=days)
    elif date_str.endswith("w"):
        weeks = int(date_str[:-1])
        return datetime.now() - timedelta(weeks=weeks)
    elif date_str.endswith("m"):
        months = int(date_str[:-1])
        return datetime.now() - timedelta(days=months * 30)
    else:
        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {date_str}")


@click.command("developer-report")
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
    "--repository",
    "-r",
    multiple=True,
    help="Filter by repository (can specify multiple times)",
)
@click.option(
    "--developer",
    "-d",
    multiple=True,
    help="Filter by developer (can specify multiple times)",
)
@click.option(
    "--team",
    "-t",
    multiple=True,
    help="Filter by team (can specify multiple times)",
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
def developer_report(
    ctx: click.Context,
    start_date: str,
    end_date: str,
    repository: tuple,
    developer: tuple,
    team: tuple,
    include_external: bool,
    format: str,
    output: Optional[Path],
    no_cache: bool,
) -> None:
    """
    Generate developer activity report.
    
    Generates a report showing developer contributions (commits, PRs, reviews, issues)
    across organization repositories for a specified time period.
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
        
        # Initialize components
        github_config = config.get_github_config()
        cache_config = config.get_cache_config()
        
        github_client = GitHubClient(github_config)
        rate_limiter = RateLimiter()
        cache = FileCache(cache_config) if not no_cache else None
        
        collector = ContributionCollector(github_client, rate_limiter, cache)
        analyzer = DeveloperAnalyzer()
        report_generator = ReportGenerator()
        
        # Get organization repositories (or use specified ones)
        if repository:
            repositories = list(repository)
        else:
            if not github_config.organization:
                logger.error("Organization not configured. Use --repository to specify repositories.")
                click.echo("Error: Organization not configured. Use --repository to specify repositories.", err=True)
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
        
        # Apply filters
        if repository:
            all_contributions = filter_by_repositories(all_contributions, list(repository))
        
        if developer:
            all_contributions = filter_by_developers(all_contributions, list(developer))
        
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
        
        # Analyze contributions
        logger.info("Analyzing contributions...")
        metrics = analyzer.analyze(all_contributions, developers, time_period)
        
        # Generate report
        logger.info("Generating report...")
        report = report_generator.generate_developer_report(metrics, time_period, format)
        
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

