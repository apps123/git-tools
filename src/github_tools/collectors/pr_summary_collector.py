"""Collector for PR summaries."""

from typing import List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.summarizers.llm_summarizer import LLMSummarizer
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class PRSummaryCollector:
    """
    Collects and summarizes pull requests.
    
    Filters PRs from contributions and generates summaries using LLM.
    """
    
    def __init__(
        self,
        summarizer: LLMSummarizer,
    ):
        """
        Initialize PR summary collector.
        
        Args:
            summarizer: LLM summarizer instance
        """
        self.summarizer = summarizer
    
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
                # Add PR without summary
                summaries.append({
                    "id": pr.id,
                    "title": pr.title,
                    "repository": pr.repository,
                    "author": pr.developer,
                    "created_at": pr.timestamp.isoformat(),
                    "state": pr.state,
                    "summary": f"Summary unavailable: {str(e)}",
                })
                continue
        
        return summaries

