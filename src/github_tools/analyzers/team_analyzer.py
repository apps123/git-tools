"""Team and department-level contribution analysis."""

from collections import defaultdict
from typing import Dict, List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.team import Team
from github_tools.models.time_period import TimePeriod
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class TeamMetrics:
    """
    Aggregated metrics for a team over a time period.
    
    Attributes match the TeamMetrics model from data-model.md.
    """
    
    def __init__(
        self,
        team_name: str,
        time_period: TimePeriod,
    ):
        """
        Initialize team metrics.
        
        Args:
            team_name: Team name
            time_period: Time period for metrics
        """
        self.team_name = team_name
        self.time_period = time_period
        self.total_contributions = 0
        self.active_members = 0
        self.member_list: List[str] = []
        self.commits = 0
        self.pull_requests = 0
        self.issues = 0
        self.reviews = 0
        self.repositories_contributed: List[str] = []
    
    @property
    def average_contributions_per_member(self) -> float:
        """Calculate average contributions per team member."""
        if self.active_members == 0:
            return 0.0
        return self.total_contributions / self.active_members
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "team_name": self.team_name,
            "time_period": {
                "start_date": self.time_period.start_date.isoformat(),
                "end_date": self.time_period.end_date.isoformat(),
                "period_type": self.time_period.period_type,
            },
            "total_contributions": self.total_contributions,
            "active_members": self.active_members,
            "member_list": sorted(self.member_list),
            "commits": self.commits,
            "pull_requests": self.pull_requests,
            "issues": self.issues,
            "reviews": self.reviews,
            "repositories_contributed": sorted(set(self.repositories_contributed)),
            "average_contributions_per_member": round(
                self.average_contributions_per_member, 2
            ),
        }


class DepartmentMetrics:
    """
    Aggregated metrics for a department over a time period.
    
    Attributes match the DepartmentMetrics model from data-model.md.
    """
    
    def __init__(
        self,
        department_name: str,
        time_period: TimePeriod,
    ):
        """
        Initialize department metrics.
        
        Args:
            department_name: Department name
            time_period: Time period for metrics
        """
        self.department_name = department_name
        self.time_period = time_period
        self.total_contributions = 0
        self.active_members = 0
        self.member_list: List[str] = []
        self.teams: List[str] = []
        self.team_metrics: Dict[str, TeamMetrics] = {}
    
    @property
    def average_contributions_per_member(self) -> float:
        """Calculate average contributions per department member."""
        if self.active_members == 0:
            return 0.0
        return self.total_contributions / self.active_members
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "department_name": self.department_name,
            "time_period": {
                "start_date": self.time_period.start_date.isoformat(),
                "end_date": self.time_period.end_date.isoformat(),
                "period_type": self.time_period.period_type,
            },
            "total_contributions": self.total_contributions,
            "active_members": self.active_members,
            "member_list": sorted(self.member_list),
            "teams": sorted(self.teams),
            "average_contributions_per_member": round(
                self.average_contributions_per_member, 2
            ),
        }


class TeamAnalyzer:
    """
    Analyzes contributions to compute team and department-level metrics.
    
    Groups contributions by team membership and aggregates metrics
    at both team and department levels.
    """
    
    def analyze_teams(
        self,
        contributions: List[Contribution],
        developers: List[Developer],
        teams: Optional[List[Team]] = None,
        time_period: Optional[TimePeriod] = None,
    ) -> List[TeamMetrics]:
        """
        Analyze contributions and compute team metrics.
        
        Args:
            contributions: List of contributions to analyze
            developers: List of developers with team affiliations
            teams: Optional list of teams (for validation)
            time_period: Optional time period (inferred if not provided)
        
        Returns:
            List of TeamMetrics instances
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
        
        # Create developer lookup
        dev_lookup = {d.username: d for d in developers}
        
        # Group contributions by team
        team_contributions: Dict[str, List[Contribution]] = defaultdict(list)
        for contribution in contributions:
            dev = dev_lookup.get(contribution.developer)
            if dev and dev.team_affiliations:
                for team_name in dev.team_affiliations:
                    team_contributions[team_name].append(contribution)
        
        # Compute metrics for each team
        metrics_list = []
        for team_name, team_contribs in team_contributions.items():
            metrics = TeamMetrics(team_name, time_period)
            
            # Count by type
            for contrib in team_contribs:
                metrics.total_contributions += 1
                
                if contrib.type == "commit":
                    metrics.commits += 1
                elif contrib.type == "pull_request":
                    metrics.pull_requests += 1
                elif contrib.type == "issue":
                    metrics.issues += 1
                elif contrib.type == "review":
                    metrics.reviews += 1
                
                # Track repositories
                if contrib.repository not in metrics.repositories_contributed:
                    metrics.repositories_contributed.append(contrib.repository)
            
            # Get unique team members
            team_members = set()
            for contrib in team_contribs:
                dev = dev_lookup.get(contrib.developer)
                if dev and team_name in dev.team_affiliations:
                    team_members.add(dev.username)
            
            metrics.active_members = len(team_members)
            metrics.member_list = list(team_members)
            
            metrics_list.append(metrics)
        
        return metrics_list
    
    def analyze_departments(
        self,
        team_metrics: List[TeamMetrics],
        teams: List[Team],
        time_period: Optional[TimePeriod] = None,
    ) -> List[DepartmentMetrics]:
        """
        Analyze team metrics to compute department metrics.
        
        Args:
            team_metrics: List of team metrics
            teams: List of teams with department affiliations
            time_period: Optional time period (inferred from team metrics if not provided)
        
        Returns:
            List of DepartmentMetrics instances
        """
        # Infer time period from team metrics if not provided
        if not time_period and team_metrics:
            time_period = team_metrics[0].time_period
        
        if not time_period:
            raise ValueError("Time period required for analysis")
        
        # Create team lookup
        team_lookup = {t.name: t for t in teams}
        
        # Group teams by department
        dept_teams: Dict[str, List[str]] = defaultdict(list)
        for team in teams:
            dept_teams[team.department].append(team.name)
        
        # Create team metrics lookup
        team_metrics_lookup = {tm.team_name: tm for tm in team_metrics}
        
        # Compute metrics for each department
        metrics_list = []
        for dept_name, team_names in dept_teams.items():
            metrics = DepartmentMetrics(dept_name, time_period)
            metrics.teams = team_names
            
            # Aggregate team metrics
            dept_members = set()
            for team_name in team_names:
                team_metric = team_metrics_lookup.get(team_name)
                if team_metric:
                    metrics.total_contributions += team_metric.total_contributions
                    dept_members.update(team_metric.member_list)
                    metrics.team_metrics[team_name] = team_metric
            
            metrics.active_members = len(dept_members)
            metrics.member_list = list(dept_members)
            
            metrics_list.append(metrics)
        
        return metrics_list

