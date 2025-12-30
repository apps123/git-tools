"""Developer activity analyzer for computing developer metrics."""

from collections import defaultdict
from typing import Dict, List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.time_period import TimePeriod
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class DeveloperMetrics:
    """
    Aggregated metrics for a developer over a time period.
    
    Attributes match the DeveloperMetrics model from data-model.md.
    """
    
    def __init__(
        self,
        developer: str,
        time_period: TimePeriod,
    ):
        """
        Initialize developer metrics.
        
        Args:
            developer: Developer username
            time_period: Time period for metrics
        """
        self.developer = developer
        self.time_period = time_period
        self.total_commits = 0
        self.pull_requests_created = 0
        self.pull_requests_reviewed = 0
        self.pull_requests_merged = 0
        self.issues_created = 0
        self.issues_resolved = 0
        self.code_review_participation = 0
        self.repositories_contributed: List[str] = []
        self.per_repository_breakdown: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {
                "commits": 0,
                "pull_requests_created": 0,
                "pull_requests_reviewed": 0,
                "issues_created": 0,
                "issues_resolved": 0,
            }
        )
    
    @property
    def total_contributions(self) -> int:
        """Calculate total contributions."""
        return (
            self.total_commits
            + self.pull_requests_created
            + self.pull_requests_reviewed
            + self.issues_created
        )
    
    @property
    def average_contributions_per_day(self) -> float:
        """Calculate average contributions per day."""
        days = (self.time_period.end_date - self.time_period.start_date).days + 1
        if days == 0:
            return 0.0
        return self.total_contributions / days
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "developer": self.developer,
            "time_period": {
                "start_date": self.time_period.start_date.isoformat(),
                "end_date": self.time_period.end_date.isoformat(),
                "period_type": self.time_period.period_type,
            },
            "total_commits": self.total_commits,
            "pull_requests_created": self.pull_requests_created,
            "pull_requests_reviewed": self.pull_requests_reviewed,
            "pull_requests_merged": self.pull_requests_merged,
            "issues_created": self.issues_created,
            "issues_resolved": self.issues_resolved,
            "code_review_participation": self.code_review_participation,
            "repositories_contributed": sorted(set(self.repositories_contributed)),
            "per_repository_breakdown": dict(self.per_repository_breakdown),
            "total_contributions": self.total_contributions,
            "average_contributions_per_day": round(self.average_contributions_per_day, 2),
        }


class DeveloperAnalyzer:
    """
    Analyzes contributions to compute developer-level metrics.
    
    Aggregates contributions by developer and calculates metrics
    such as commits, PRs, reviews, and issues.
    """
    
    def analyze(
        self,
        contributions: List[Contribution],
        developers: Optional[List[Developer]] = None,
        time_period: Optional[TimePeriod] = None,
    ) -> List[DeveloperMetrics]:
        """
        Analyze contributions and compute developer metrics.
        
        Args:
            contributions: List of contributions to analyze
            developers: Optional list of developers (for filtering)
            time_period: Optional time period (for metrics calculation)
        
        Returns:
            List of DeveloperMetrics instances
        """
        # Group contributions by developer
        dev_contributions: Dict[str, List[Contribution]] = defaultdict(list)
        for contribution in contributions:
            dev_contributions[contribution.developer].append(contribution)
        
        # If time period not provided, infer from contributions
        if not time_period and contributions:
            timestamps = [c.timestamp for c in contributions]
            from github_tools.models.time_period import TimePeriod, PeriodType
            time_period = TimePeriod(
                start_date=min(timestamps),
                end_date=max(timestamps),
                period_type="custom",
            )
        
        if not time_period:
            raise ValueError("Time period required for analysis")
        
        # Compute metrics for each developer
        metrics_list = []
        for username, dev_contribs in dev_contributions.items():
            metrics = DeveloperMetrics(username, time_period)
            
            for contrib in dev_contribs:
                repo = contrib.repository
                
                # Track repositories
                if repo not in metrics.repositories_contributed:
                    metrics.repositories_contributed.append(repo)
                
                # Aggregate by type
                if contrib.type == "commit":
                    metrics.total_commits += 1
                    metrics.per_repository_breakdown[repo]["commits"] += 1
                
                elif contrib.type == "pull_request":
                    metrics.pull_requests_created += 1
                    metrics.per_repository_breakdown[repo]["pull_requests_created"] += 1
                    if contrib.state == "merged":
                        metrics.pull_requests_merged += 1
                
                elif contrib.type == "review":
                    metrics.pull_requests_reviewed += 1
                    metrics.code_review_participation += 1
                    metrics.per_repository_breakdown[repo]["pull_requests_reviewed"] += 1
                
                elif contrib.type == "issue":
                    metrics.issues_created += 1
                    metrics.per_repository_breakdown[repo]["issues_created"] += 1
                    if contrib.state == "closed":
                        metrics.issues_resolved += 1
                        metrics.per_repository_breakdown[repo]["issues_resolved"] = (
                            metrics.per_repository_breakdown[repo].get("issues_resolved", 0) + 1
                        )
            
            metrics_list.append(metrics)
        
        return metrics_list
    
    def aggregate_by_repository(
        self,
        metrics: List[DeveloperMetrics],
    ) -> Dict[str, List[DeveloperMetrics]]:
        """
        Group developer metrics by repository.
        
        Args:
            metrics: List of developer metrics
        
        Returns:
            Dictionary mapping repository names to lists of developer metrics
        """
        repo_metrics: Dict[str, List[DeveloperMetrics]] = defaultdict(list)
        
        for metric in metrics:
            for repo in metric.repositories_contributed:
                repo_metrics[repo].append(metric)
        
        return dict(repo_metrics)

