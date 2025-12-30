"""CLI command for repository contribution reports."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from github_tools.analyzers.repository_analyzer import RepositoryAnalyzer
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.collectors.contribution_collector import ContributionCollector
from github_tools.models.time_period import TimePeriod
from github_tools.reports.generator import ReportGenerator
from github_tools.utils.cache import FileCache
from github_tools.utils.config import AppConfig
from github_tools.utils.filters import filter_by_repositories, filter_internal_contributors
from github_tools.utils.logging import get_logger
from github_tools.cli.developer_report import parse_date

logger = get_logger(__name__)


@click.command("repository-report")
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
def repository_report(
    ctx: click.Context,
    start_date: str,
    end_date: str,
    repository: tuple,
    include_external: bool,
    format: str,
    output: Optional[Path],
    no_cache: bool,
) -> None:
    """
    Generate repository contribution analysis report.
    
    Provides repository-level metrics including activity levels, contributor
    diversity, trends, and contribution distribution.
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
        analyzer = RepositoryAnalyzer()
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
        
        # Analyze contributions
        logger.info("Analyzing repository patterns...")
        metrics = analyzer.analyze(all_contributions, time_period)
        
        # Generate report
        logger.info("Generating report...")
        report = report_generator.generate_repository_report(metrics, time_period, format)
        
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

