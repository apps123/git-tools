"""Collector for PR summaries."""

from typing import List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer
from github_tools.summarizers.providers import detect_available_providers
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class PRSummaryCollector:
    """
    Collects and summarizes pull requests.
    
    Filters PRs from contributions and generates summaries using LLM.
    Supports batch processing with automatic retry using next available provider.
    """
    
    def __init__(
        self,
        summarizer: LLMSummarizer,
        auto_retry: bool = True,
    ):
        """
        Initialize PR summary collector.
        
        Args:
            summarizer: LLM summarizer instance
            auto_retry: If True, automatically retry failed PRs with next available provider
        """
        self.summarizer = summarizer
        self.auto_retry = auto_retry
    
    def collect_summaries(
        self,
        contributions: List[Contribution],
        time_period: TimePeriod,
        repository_context: Optional[str] = None,
    ) -> List[dict]:
        """
        Collect PR summaries for contributions in time period.
        
        Args:
            contributions: List of contributions
            time_period: Time period filter
            repository_context: Optional repository context for summarization
        
        Returns:
            List of PR summary dictionaries
        """
        # Filter PRs
        prs = [
            c for c in contributions
            if c.type == "pull_request"
            and time_period.start_date <= c.timestamp <= time_period.end_date
        ]
        
        summaries = []
        failed_prs = []  # Track failed PRs for retry
        
        # First pass: try with primary provider
        for pr in prs:
            try:
                summary = self.summarizer.summarize(pr, repository_context)
                
                summary_dict = {
                    "id": pr.id,
                    "title": pr.title,
                    "repository": pr.repository,
                    "author": pr.developer,
                    "created_at": pr.timestamp.isoformat(),
                    "state": pr.state,
                    "summary": summary,
                    "provider": self.summarizer.provider.get_metadata().get("name"),
                }
                
                # Add metadata if available
                if pr.metadata:
                    if "number" in pr.metadata:
                        summary_dict["number"] = pr.metadata["number"]
                    if "merged" in pr.metadata:
                        summary_dict["merged"] = pr.metadata["merged"]
                
                summaries.append(summary_dict)
            
            except Exception as e:
                logger.warning(f"Failed to summarize PR {pr.id}: {e}")
                if self.auto_retry:
                    failed_prs.append((pr, e))
                else:
                    # Add PR without summary immediately
                    summaries.append({
                        "id": pr.id,
                        "title": pr.title,
                        "repository": pr.repository,
                        "author": pr.developer,
                        "created_at": pr.timestamp.isoformat(),
                        "state": pr.state,
                        "summary": f"Summary unavailable: {str(e)}",
                        "error": True,
                    })
        
        # Second pass: retry failed PRs with next available provider
        if failed_prs and self.auto_retry:
            available_providers = detect_available_providers(self.summarizer.provider_config)
            current_provider_name = self.summarizer.provider_name or "unknown"
            
            # Get next provider in priority order
            if current_provider_name in available_providers:
                current_index = available_providers.index(current_provider_name)
                next_providers = available_providers[current_index + 1:]
            else:
                next_providers = available_providers
            
            if next_providers:
                logger.info(f"Retrying {len(failed_prs)} failed PRs with provider: {next_providers[0]}")
                for pr, original_error in failed_prs:
                    try:
                        summary = self.summarizer.summarize_with_fallback(
                            pr,
                            repository_context,
                            fallback_providers=next_providers,
                        )
                        
                        summary_dict = {
                            "id": pr.id,
                            "title": pr.title,
                            "repository": pr.repository,
                            "author": pr.developer,
                            "created_at": pr.timestamp.isoformat(),
                            "state": pr.state,
                            "summary": summary,
                            "provider": next_providers[0],
                            "retried": True,
                        }
                        
                        if pr.metadata:
                            if "number" in pr.metadata:
                                summary_dict["number"] = pr.metadata["number"]
                            if "merged" in pr.metadata:
                                summary_dict["merged"] = pr.metadata["merged"]
                        
                        summaries.append(summary_dict)
                    except Exception as e:
                        logger.warning(f"Failed to summarize PR {pr.id} with fallback provider: {e}")
                        summaries.append({
                            "id": pr.id,
                            "title": pr.title,
                            "repository": pr.repository,
                            "author": pr.developer,
                            "created_at": pr.timestamp.isoformat(),
                            "state": pr.state,
                            "summary": f"Summary unavailable: {str(e)}",
                            "error": True,
                        })
            else:
                # No fallback providers available - mark all as failed
                logger.error("No fallback providers available for failed PRs")
                for pr, original_error in failed_prs:
                    summaries.append({
                        "id": pr.id,
                        "title": pr.title,
                        "repository": pr.repository,
                        "author": pr.developer,
                        "created_at": pr.timestamp.isoformat(),
                        "state": pr.state,
                        "summary": f"Summary unavailable: {str(original_error)}",
                        "error": True,
                    })
        
        return summaries

