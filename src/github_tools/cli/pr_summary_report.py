"""CLI command for PR summary reports."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from github_tools.analyzers.repository_analyzer import RepositoryAnalyzer
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.collectors.contribution_collector import ContributionCollector
from github_tools.collectors.pr_summary_collector import PRSummaryCollector
from github_tools.models.time_period import TimePeriod
from github_tools.reports.generator import ReportGenerator
from github_tools.summarizers.context_analyzer import ContextAnalyzer
from github_tools.summarizers.llm_summarizer import LLMSummarizer
from github_tools.utils.cache import FileCache
from github_tools.utils.config import AppConfig
from github_tools.utils.filters import filter_by_repositories
from github_tools.utils.logging import get_logger
from github_tools.cli.developer_report import parse_date

logger = get_logger(__name__)


@click.command("pr-summary-report")
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
    "--base-branch",
    default="main",
    help="Base branch to filter PRs (default: main)",
)
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "claude-local", "cursor", "gemini", "generic", "auto"], case_sensitive=False),
    default="auto",
    help="LLM provider to use (default: auto-detect available provider)",
)
@click.option(
    "--openai-api-key",
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY env var) - required if using OpenAI provider",
)
@click.option(
    "--gemini-api-key",
    envvar="GOOGLE_API_KEY",
    help="Google Gemini API key (or set GOOGLE_API_KEY env var) - required if using Gemini provider",
)
@click.option(
    "--claude-endpoint",
    envvar="CLAUDE_ENDPOINT",
    default="http://localhost:11434",
    help="Claude Desktop API endpoint (default: http://localhost:11434)",
)
@click.option(
    "--cursor-endpoint",
    envvar="CURSOR_ENDPOINT",
    default="http://localhost:8080",
    help="Cursor Agent API endpoint (default: http://localhost:8080)",
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
def pr_summary_report(
    ctx: click.Context,
    start_date: str,
    end_date: str,
    repository: tuple,
    base_branch: str,
    llm_provider: str,
    openai_api_key: Optional[str],
    gemini_api_key: Optional[str],
    claude_endpoint: str,
    cursor_endpoint: str,
    format: str,
    output: Optional[Path],
    no_cache: bool,
) -> None:
    """
    Generate pull request summary report.
    
    Produces concise, contextual summaries of PRs merged to main branches
    over a period, grouped by repository. Uses LLM (OpenAI) for summarization.
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
        
        # Build LLM provider configuration
        provider_config = config.get_llm_provider_config()
        
        # Override with CLI options
        if openai_api_key:
            provider_config.setdefault("openai", {})["api_key"] = openai_api_key
        if gemini_api_key:
            provider_config.setdefault("gemini", {})["api_key"] = gemini_api_key
        if claude_endpoint:
            provider_config.setdefault("claude_local", {})["endpoint"] = claude_endpoint
        if cursor_endpoint:
            provider_config.setdefault("cursor", {})["endpoint"] = cursor_endpoint
        
        # Determine provider name
        provider_name = None if llm_provider == "auto" else llm_provider
        
        # Initialize summarizer with provider
        try:
            summarizer = LLMSummarizer(
                provider_name=provider_name,
                provider_config=provider_config,
                auto_detect=(llm_provider == "auto"),
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            click.echo(f"Error: Failed to initialize LLM provider: {e}", err=True)
            sys.exit(1)
        
        collector = ContributionCollector(github_client, rate_limiter, cache)
        context_analyzer = ContextAnalyzer(github_client)
        pr_collector = PRSummaryCollector(summarizer, auto_retry=True)
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
        
        # Collect contributions (PRs only)
        logger.info(f"Collecting PRs from {len(repositories)} repositories...")
        all_contributions = []
        
        for repo in repositories:
            try:
                contributions = collector.collect_contributions(
                    repo,
                    time_period,
                    use_cache=not no_cache,
                )
                # Filter to only PRs merged to base branch
                prs = [
                    c for c in contributions
                    if c.type == "pull_request"
                    and c.state == "merged"
                    and c.metadata.get("base_branch") == base_branch
                ]
                all_contributions.extend(prs)
                logger.debug(f"Collected {len(prs)} merged PRs from {repo}")
            except Exception as e:
                logger.warning(f"Failed to collect from {repo}: {e}")
                continue
        
        # Apply repository filter if specified
        if repository:
            all_contributions = filter_by_repositories(all_contributions, list(repository))
        
        if not all_contributions:
            logger.warning("No PRs found for the specified period")
            click.echo("Warning: No PRs found for the specified period", err=True)
            sys.exit(0)
        
        # Collect PR summaries
        logger.info(f"Generating summaries for {len(all_contributions)} PRs...")
        summaries = []
        
        for repo in repositories:
            repo_prs = [c for c in all_contributions if c.repository == repo]
            if not repo_prs:
                continue
            
            # Get repository context
            context = context_analyzer.get_repository_context(repo)
            
            # Generate summaries
            repo_summaries = pr_collector.collect_summaries(
                repo_prs,
                time_period,
                repository_context=context,
            )
            summaries.extend(repo_summaries)
        
        # Generate report
        logger.info("Generating report...")
        report = report_generator.generate_pr_summary_report(summaries, time_period, format)
        
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

