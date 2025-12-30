"""CLI command for anomaly detection reports."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click

from github_tools.analyzers.anomaly_detector import AnomalyDetector
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.collectors.contribution_collector import ContributionCollector
from github_tools.models.time_period import TimePeriod
from github_tools.reports.generator import ReportGenerator
from github_tools.utils.cache import FileCache
from github_tools.utils.config import AppConfig
from github_tools.utils.filters import filter_by_repositories
from github_tools.utils.logging import get_logger
from github_tools.cli.developer_report import parse_date

logger = get_logger(__name__)


@click.command("anomaly-report")
@click.option(
    "--current-start-date",
    required=True,
    help="Current period start date (ISO format: YYYY-MM-DD or relative: '30d', '1w', '1m', 'today', 'yesterday')",
)
@click.option(
    "--current-end-date",
    required=True,
    help="Current period end date (ISO format: YYYY-MM-DD or relative: 'today', 'yesterday')",
)
@click.option(
    "--previous-start-date",
    help="Previous period start date (default: same duration before current start)",
)
@click.option(
    "--previous-end-date",
    help="Previous period end date (default: same as current start date)",
)
@click.option(
    "--repository",
    "-r",
    multiple=True,
    help="Filter by repository (can specify multiple times)",
)
@click.option(
    "--entity-type",
    type=click.Choice(["developer", "repository", "team"], case_sensitive=False),
    default="developer",
    help="Entity type to analyze (default: developer)",
)
@click.option(
    "--threshold",
    type=float,
    default=50.0,
    help="Anomaly detection threshold percentage (default: 50.0)",
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
def anomaly_report(
    ctx: click.Context,
    current_start_date: str,
    current_end_date: str,
    previous_start_date: Optional[str],
    previous_end_date: Optional[str],
    repository: tuple,
    entity_type: str,
    threshold: float,
    format: str,
    output: Optional[Path],
    no_cache: bool,
) -> None:
    """
    Generate anomaly detection report.
    
    Detects significant changes (drops/spikes >threshold%) in contribution
    patterns by comparing current period against previous period.
    """
    try:
        config: AppConfig = ctx.obj["config"]
        
        # Parse current period dates
        try:
            current_start = parse_date(current_start_date)
            current_end = parse_date(current_end_date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            click.echo(f"Error: Invalid date format: {e}", err=True)
            sys.exit(1)
        
        if current_start > current_end:
            logger.error("Current start date must be before end date")
            click.echo("Error: Current start date must be before end date", err=True)
            sys.exit(1)
        
        # Calculate previous period if not provided
        if previous_start_date and previous_end_date:
            try:
                previous_start = parse_date(previous_start_date)
                previous_end = parse_date(previous_end_date)
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                click.echo(f"Error: Invalid date format: {e}", err=True)
                sys.exit(1)
        else:
            # Default: previous period is same duration before current period
            duration = current_end - current_start
            previous_end = current_start
            previous_start = previous_end - duration
        
        if previous_start > previous_end:
            logger.error("Previous start date must be before end date")
            click.echo("Error: Previous start date must be before end date", err=True)
            sys.exit(1)
        
        # Create time periods
        current_period = TimePeriod(
            start_date=current_start,
            end_date=current_end,
            period_type="custom",
        )
        
        previous_period = TimePeriod(
            start_date=previous_start,
            end_date=previous_end,
            period_type="custom",
        )
        
        # Initialize components
        github_config = config.get_github_config()
        cache_config = config.get_cache_config()
        
        github_client = GitHubClient(github_config)
        rate_limiter = RateLimiter()
        cache = FileCache(cache_config) if not no_cache else None
        
        collector = ContributionCollector(github_client, rate_limiter, cache)
        detector = AnomalyDetector(threshold_percent=threshold)
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
        
        # Collect current period contributions
        logger.info(f"Collecting current period contributions from {len(repositories)} repositories...")
        current_contributions = []
        
        for repo in repositories:
            try:
                contributions = collector.collect_contributions(
                    repo,
                    current_period,
                    use_cache=not no_cache,
                )
                current_contributions.extend(contributions)
                logger.debug(f"Collected {len(contributions)} contributions from {repo} (current period)")
            except Exception as e:
                logger.warning(f"Failed to collect from {repo}: {e}")
                continue
        
        # Collect previous period contributions
        logger.info(f"Collecting previous period contributions...")
        previous_contributions = []
        
        for repo in repositories:
            try:
                contributions = collector.collect_contributions(
                    repo,
                    previous_period,
                    use_cache=not no_cache,
                )
                previous_contributions.extend(contributions)
                logger.debug(f"Collected {len(contributions)} contributions from {repo} (previous period)")
            except Exception as e:
                logger.warning(f"Failed to collect from {repo}: {e}")
                continue
        
        # Apply repository filter if specified
        if repository:
            current_contributions = filter_by_repositories(current_contributions, list(repository))
            previous_contributions = filter_by_repositories(previous_contributions, list(repository))
        
        # Detect anomalies
        logger.info(f"Detecting anomalies (threshold: {threshold}%)...")
        anomalies = detector.detect_anomalies(
            current_contributions,
            previous_contributions,
            current_period,
            entity_type=entity_type,
        )
        
        if not anomalies:
            logger.info("No anomalies detected")
            click.echo("No anomalies detected for the specified periods and threshold.", err=True)
            sys.exit(0)
        
        # Generate report
        logger.info(f"Generating report for {len(anomalies)} anomalies...")
        report = report_generator.generate_anomaly_report(anomalies, current_period, format)
        
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

