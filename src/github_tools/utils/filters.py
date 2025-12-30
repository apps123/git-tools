"""Filtering utilities for repositories, developers, and time periods."""

from datetime import datetime
from typing import List, Optional, Set

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.repository import Repository
from github_tools.models.time_period import TimePeriod
from github_tools.api.client import GitHubClient
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


def filter_by_time_period(
    contributions: List[Contribution],
    time_period: TimePeriod,
) -> List[Contribution]:
    """
    Filter contributions by time period.
    
    Args:
        contributions: List of contributions
        time_period: Time period filter
    
    Returns:
        Filtered contributions
    """
    return [
        c
        for c in contributions
        if time_period.start_date <= c.timestamp <= time_period.end_date
    ]


def filter_by_repositories(
    contributions: List[Contribution],
    repository_names: Optional[List[str]] = None,
) -> List[Contribution]:
    """
    Filter contributions by repository names.
    
    Args:
        contributions: List of contributions
        repository_names: List of repository full names (None = all repositories)
    
    Returns:
        Filtered contributions
    """
    if not repository_names:
        return contributions
    
    repo_set = set(repository_names)
    return [c for c in contributions if c.repository in repo_set]


def filter_by_developers(
    contributions: List[Contribution],
    developer_usernames: Optional[List[str]] = None,
) -> List[Contribution]:
    """
    Filter contributions by developer usernames.
    
    Args:
        contributions: List of contributions
        developer_usernames: List of developer usernames (None = all developers)
    
    Returns:
        Filtered contributions
    """
    if not developer_usernames:
        return contributions
    
    dev_set = set(developer_usernames)
    return [c for c in contributions if c.developer in dev_set]


def filter_by_teams(
    contributions: List[Contribution],
    developers: List[Developer],
    team_names: Optional[List[str]] = None,
) -> List[Contribution]:
    """
    Filter contributions by team membership.
    
    Args:
        contributions: List of contributions
        developers: List of developers with team affiliations
        team_names: List of team names (None = all teams)
    
    Returns:
        Filtered contributions
    """
    if not team_names:
        return contributions
    
    team_set = set(team_names)
    dev_set = {
        dev.username
        for dev in developers
        if any(team in team_set for team in dev.team_affiliations)
    }
    
    return [c for c in contributions if c.developer in dev_set]


def filter_internal_contributors(
    contributions: List[Contribution],
    developers: List[Developer],
    include_external: bool = False,
) -> List[Contribution]:
    """
    Filter contributions by internal/external contributor status.
    
    Args:
        contributions: List of contributions
        developers: List of developers with is_internal flag
        include_external: If True, include external contributors; if False, only internal
    
    Returns:
        Filtered contributions
    """
    if include_external:
        return contributions
    
    internal_devs = {dev.username for dev in developers if dev.is_internal}
    return [c for c in contributions if c.developer in internal_devs]


def classify_contributor(
    github_client: GitHubClient,
    username: str,
    repository: Optional[str] = None,
) -> tuple[bool, bool]:
    """
    Classify contributor as internal or external.
    
    Internal: Member of the organization/enterprise that owns the repository.
    External: Not a member, but explicitly granted access to specific repositories
              (outside collaborator with repository-specific access).
    
    Args:
        github_client: GitHub API client
        username: GitHub username
        repository: Optional repository full name for collaborator check
    
    Returns:
        Tuple of (is_internal, is_organization_member)
    """
    # Check if user is organization/enterprise member
    is_org_member = github_client.is_organization_member(username)
    
    if is_org_member:
        # Internal contributor: organization/enterprise member
        return (True, True)
    
    # Check if outside collaborator with repository-specific access
    if repository:
        is_collaborator = github_client.is_repository_collaborator(repository, username)
        if is_collaborator:
            # External contributor: outside collaborator
            return (False, False)
    
    # Default: assume external if not org member and not collaborator
    # (could be a public repository contributor)
    return (False, False)


def apply_contributor_classification(
    developers: List[Developer],
    github_client: GitHubClient,
    repository: Optional[str] = None,
) -> List[Developer]:
    """
    Apply internal/external classification to developers.
    
    Args:
        developers: List of developers to classify
        github_client: GitHub API client
        repository: Optional repository for collaborator checks
    
    Returns:
        Developers with is_internal and organization_member flags set
    """
    classified = []
    
    for dev in developers:
        is_internal, is_org_member = classify_contributor(
            github_client,
            dev.username,
            repository,
        )
        
        # Create new developer instance with classification
        classified_dev = Developer(
            username=dev.username,
            display_name=dev.display_name,
            email=dev.email,
            organization_member=is_org_member,
            team_affiliations=dev.team_affiliations,
            is_internal=is_internal,
        )
        classified.append(classified_dev)
    
    return classified

