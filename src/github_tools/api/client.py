"""GitHub API client wrapper for contribution analytics."""

from typing import List, Optional
from github import Github, GithubException
from github.Organization import Organization
from github.Repository import Repository as GHRepository
from github.User import User as GHUser
from github.NamedUser import NamedUser

from github_tools.models.repository import Repository
from github_tools.models.developer import Developer
from github_tools.utils.config import GitHubConfig
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """
    GitHub API client wrapper with rate limiting and error handling.
    
    Provides high-level methods for accessing GitHub repositories,
    organizations, and user data.
    """
    
    def __init__(self, config: GitHubConfig):
        """
        Initialize GitHub API client.
        
        Args:
            config: GitHub configuration with token and base URL
        """
        self.config = config
        self.github = Github(
            login_or_token=config.token,
            base_url=config.base_url,
        )
        self._organization: Optional[Organization] = None
    
    @property
    def organization(self) -> Optional[Organization]:
        """
        Get organization instance.
        
        Returns:
            Organization instance or None if not configured
        """
        if self.config.organization and not self._organization:
            try:
                self._organization = self.github.get_organization(
                    self.config.organization
                )
            except GithubException as e:
                logger.error(f"Failed to get organization: {e}")
                raise
        return self._organization
    
    def get_repository(self, full_name: str) -> Repository:
        """
        Get repository information.
        
        Args:
            full_name: Repository full name (owner/repo)
        
        Returns:
            Repository model instance
        """
        try:
            gh_repo = self.github.get_repo(full_name)
            return Repository(
                name=gh_repo.name,
                full_name=gh_repo.full_name,
                owner=gh_repo.owner.login,
                visibility="private" if gh_repo.private else "public",
                created_at=gh_repo.created_at,
                updated_at=gh_repo.updated_at,
                default_branch=gh_repo.default_branch,
                archived=gh_repo.archived,
                description=gh_repo.description,
            )
        except GithubException as e:
            logger.error(f"Failed to get repository {full_name}: {e}")
            raise
    
    def get_organization_repositories(self) -> List[Repository]:
        """
        Get all repositories for the configured organization.
        
        Returns:
            List of Repository model instances
        """
        if not self.organization:
            raise ValueError("Organization not configured")
        
        repositories = []
        try:
            for gh_repo in self.organization.get_repos():
                repositories.append(
                    Repository(
                        name=gh_repo.name,
                        full_name=gh_repo.full_name,
                        owner=gh_repo.owner.login,
                        visibility="private" if gh_repo.private else "public",
                        created_at=gh_repo.created_at,
                        updated_at=gh_repo.updated_at,
                        default_branch=gh_repo.default_branch,
                        archived=gh_repo.archived,
                        description=gh_repo.description,
                    )
                )
        except GithubException as e:
            logger.error(f"Failed to get organization repositories: {e}")
            raise
        
        return repositories
    
    def get_user(self, username: str) -> Optional[Developer]:
        """
        Get user information.
        
        Args:
            username: GitHub username
        
        Returns:
            Developer model instance or None if user not found
        """
        try:
            user = self.github.get_user(username)
            return Developer(
                username=user.login,
                display_name=user.name,
                email=user.email,
                organization_member=False,  # Will be set by membership check
                team_affiliations=[],
                is_internal=False,  # Will be set by membership check
            )
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"User {username} not found")
                return None
            logger.error(f"Failed to get user {username}: {e}")
            raise
    
    def is_organization_member(self, username: str) -> bool:
        """
        Check if user is a member of the organization.
        
        Args:
            username: GitHub username
        
        Returns:
            True if user is an organization member, False otherwise
        """
        if not self.organization:
            return False
        
        try:
            # Check if user is a member of the organization
            user = self.github.get_user(username)
            # Try to get organization membership
            try:
                self.organization.get_membership(user)
                return True
            except GithubException:
                # Not a member
                return False
        except GithubException as e:
            if e.status == 404:
                return False
            logger.error(f"Failed to check organization membership for {username}: {e}")
            return False
    
    def is_repository_collaborator(
        self,
        repository: str,
        username: str,
    ) -> bool:
        """
        Check if user is a collaborator (outside collaborator) on a repository.
        
        Args:
            repository: Repository full name (owner/repo)
            username: GitHub username
        
        Returns:
            True if user is a collaborator, False otherwise
        """
        try:
            repo = self.github.get_repo(repository)
            try:
                repo.get_collaborator(username)
                return True
            except GithubException:
                return False
        except GithubException as e:
            logger.error(
                f"Failed to check collaborator status for {username} on {repository}: {e}"
            )
            return False
    
    def classify_contributor(
        self,
        username: str,
        repository: Optional[str] = None,
    ) -> tuple[bool, bool]:
        """
        Classify contributor as internal or external.
        
        Args:
            username: GitHub username
            repository: Optional repository full name for collaborator check
        
        Returns:
            Tuple of (is_internal, is_organization_member)
        """
        is_org_member = self.is_organization_member(username)
        
        if is_org_member:
            return (True, True)
        
        # Check if outside collaborator
        if repository:
            is_collaborator = self.is_repository_collaborator(repository, username)
            if is_collaborator:
                return (False, False)
        
        # Default: assume external if not org member and not collaborator
        return (False, False)
    
    def get_rate_limit(self) -> dict:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        rate_limit = self.github.get_rate_limit()
        return {
            "core": {
                "limit": rate_limit.core.limit,
                "remaining": rate_limit.core.remaining,
                "reset": rate_limit.core.reset,
            },
            "search": {
                "limit": rate_limit.search.limit,
                "remaining": rate_limit.search.remaining,
                "reset": rate_limit.search.reset,
            },
        }

