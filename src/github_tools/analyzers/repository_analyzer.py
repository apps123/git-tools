"""Repository-level contribution pattern analysis."""

from collections import Counter, defaultdict
from typing import Dict, List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class RepositoryMetrics:
    """
    Aggregated metrics for a repository over a time period.
    
    Attributes match the RepositoryMetrics model from data-model.md.
    """
    
    def __init__(
        self,
        repository: str,
        time_period: TimePeriod,
    ):
        """
        Initialize repository metrics.
        
        Args:
            repository: Repository full name
            time_period: Time period for metrics
        """
        self.repository = repository
        self.time_period = time_period
        self.total_contributions = 0
        self.active_contributors = 0
        self.contributor_list: List[str] = []
        self.commits = 0
        self.pull_requests = 0
        self.issues = 0
        self.reviews = 0
        self.trend: Optional[str] = None
        self.contribution_distribution: Dict[str, int] = {}
    
    @property
    def average_contributions_per_contributor(self) -> float:
        """Calculate average contributions per contributor."""
        if self.active_contributors == 0:
            return 0.0
        return self.total_contributions / self.active_contributors
    
    @property
    def health_score(self) -> float:
        """
        Calculate composite health score.
        
        Based on activity, contributor diversity, and trends.
        """
        # Simple scoring: normalize to 0-100
        activity_score = min(self.total_contributions / 100, 1.0) * 50
        diversity_score = min(self.active_contributors / 10, 1.0) * 30
        
        trend_score = 20
        if self.trend == "increasing":
            trend_score = 20
        elif self.trend == "decreasing":
            trend_score = 10
        elif self.trend == "stable":
            trend_score = 15
        
        return round(activity_score + diversity_score + trend_score, 2)
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "repository": self.repository,
            "time_period": {
                "start_date": self.time_period.start_date.isoformat(),
                "end_date": self.time_period.end_date.isoformat(),
                "period_type": self.time_period.period_type,
            },
            "total_contributions": self.total_contributions,
            "active_contributors": self.active_contributors,
            "contributor_list": sorted(self.contributor_list),
            "commits": self.commits,
            "pull_requests": self.pull_requests,
            "issues": self.issues,
            "reviews": self.reviews,
            "trend": self.trend,
            "contribution_distribution": self.contribution_distribution,
            "average_contributions_per_contributor": round(
                self.average_contributions_per_contributor, 2
            ),
            "health_score": self.health_score,
        }


class RepositoryAnalyzer:
    """
    Analyzes contributions to compute repository-level metrics.
    
    Provides insights into repository activity, contributor diversity,
    trends, and health indicators.
    """
    
    def analyze(
        self,
        contributions: List[Contribution],
        time_period: Optional[TimePeriod] = None,
        previous_period_contributions: Optional[List[Contribution]] = None,
    ) -> List[RepositoryMetrics]:
        """
        Analyze contributions and compute repository metrics.
        
        Args:
            contributions: List of contributions to analyze
            time_period: Optional time period (inferred if not provided)
            previous_period_contributions: Optional contributions from previous period for trend analysis
        
        Returns:
            List of RepositoryMetrics instances
        """
        # Infer time period if not provided
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
        
        # Group contributions by repository
        repo_contributions: Dict[str, List[Contribution]] = defaultdict(list)
        for contribution in contributions:
            repo_contributions[contribution.repository].append(contribution)
        
        # Compute metrics for each repository
        metrics_list = []
        for repo_name, repo_contribs in repo_contributions.items():
            metrics = RepositoryMetrics(repo_name, time_period)
            
            # Count by type
            for contrib in repo_contribs:
                metrics.total_contributions += 1
                
                if contrib.type == "commit":
                    metrics.commits += 1
                elif contrib.type == "pull_request":
                    metrics.pull_requests += 1
                elif contrib.type == "issue":
                    metrics.issues += 1
                elif contrib.type == "review":
                    metrics.reviews += 1
            
            # Get unique contributors
            contributors = {c.developer for c in repo_contribs}
            metrics.active_contributors = len(contributors)
            metrics.contributor_list = list(contributors)
            
            # Calculate contribution distribution
            distribution = Counter(c.developer for c in repo_contribs)
            metrics.contribution_distribution = dict(distribution)
            
            # Calculate trend if previous period data available
            if previous_period_contributions:
                prev_repo_contribs = [
                    c for c in previous_period_contributions
                    if c.repository == repo_name
                ]
                metrics.trend = self._calculate_trend(
                    len(repo_contribs),
                    len(prev_repo_contribs),
                )
            
            metrics_list.append(metrics)
        
        return metrics_list
    
    def _calculate_trend(
        self,
        current_count: int,
        previous_count: int,
    ) -> str:
        """
        Calculate trend direction.
        
        Args:
            current_count: Contribution count for current period
            previous_count: Contribution count for previous period
        
        Returns:
            Trend: "increasing", "decreasing", or "stable"
        """
        if previous_count == 0:
            return "increasing" if current_count > 0 else "stable"
        
        change_percent = ((current_count - previous_count) / previous_count) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def identify_declining_repositories(
        self,
        metrics: List[RepositoryMetrics],
        threshold_percent: float = -20.0,
    ) -> List[RepositoryMetrics]:
        """
        Identify repositories with declining activity.
        
        Args:
            metrics: List of repository metrics
            threshold_percent: Percentage threshold for decline detection
        
        Returns:
            List of repositories with declining activity
        """
        declining = []
        for metric in metrics:
            if metric.trend == "decreasing":
                # Check if decline is significant
                declining.append(metric)
        return declining

