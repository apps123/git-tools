"""Contribution collection pipeline for GitHub repositories."""

from datetime import datetime
from typing import List, Optional

from github import GithubException
from github.Repository import Repository as GHRepository

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.utils.cache import FileCache
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class ContributionCollector:
    """
    Collects contribution data from GitHub repositories.
    
    Supports collecting:
    - Commits
    - Pull requests
    - Code reviews
    - Issues
    - Comments
    """
    
    def __init__(
        self,
        github_client: GitHubClient,
        rate_limiter: RateLimiter,
        cache: Optional[FileCache] = None,
    ):
        """
        Initialize contribution collector.
        
        Args:
            github_client: GitHub API client
            rate_limiter: Rate limiter for API calls
            cache: Optional cache for collected data
        """
        self.github_client = github_client
        self.rate_limiter = rate_limiter
        self.cache = cache
    
    def collect_contributions(
        self,
        repository: str,
        time_period: TimePeriod,
        use_cache: bool = True,
    ) -> List[Contribution]:
        """
        Collect all contributions from a repository for a time period.
        
        Args:
            repository: Repository full name (owner/repo)
            time_period: Time period for collection
            use_cache: Whether to use cache if available
        
        Returns:
            List of contributions
        """
        cache_key = self._get_cache_key(repository, time_period)
        
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Using cached contributions for {repository}")
                return [Contribution(**c) for c in cached]
        
        # Collect from API
        contributions = []
        contributions.extend(self._collect_commits(repository, time_period))
        contributions.extend(self._collect_pull_requests(repository, time_period))
        contributions.extend(self._collect_reviews(repository, time_period))
        contributions.extend(self._collect_issues(repository, time_period))
        
        # Cache results
        if self.cache:
            self.cache.set(
                cache_key,
                [c.model_dump() for c in contributions],
                ttl_hours=None,  # Use default TTL
            )
        
        return contributions
    
    def _collect_commits(
        self,
        repository: str,
        time_period: TimePeriod,
    ) -> List[Contribution]:
        """Collect commits from repository."""
        contributions = []
        
        def _fetch_commits():
            repo = self.github_client.github.get_repo(repository)
            commits = repo.get_commits(
                since=time_period.start_date,
                until=time_period.end_date,
            )
            return list(commits)
        
        try:
            commits = self.rate_limiter.execute_with_retry(
                _fetch_commits,
                f"collect_commits_{repository}",
                checkpoint_key=f"commits_{repository}_{time_period.start_date.date()}",
            )
            
            for commit in commits:
                try:
                    author = commit.author
                    username = author.login if author else None
                    
                    # Use commit author string as-is if no GitHub user (per FR-023)
                    if not username:
                        username = commit.commit.author.name
                    
                    contribution = Contribution(
                        id=commit.sha,
                        type="commit",
                        timestamp=commit.commit.author.date,
                        repository=repository,
                        developer=username,
                        title=commit.commit.message.split("\n")[0] if commit.commit.message else None,
                        metadata={
                            "sha": commit.sha,
                            "message": commit.commit.message,
                            "files_changed": len(commit.files) if commit.files else 0,
                            "additions": commit.stats.additions if commit.stats else 0,
                            "deletions": commit.stats.deletions if commit.stats else 0,
                        },
                    )
                    contributions.append(contribution)
                except Exception as e:
                    logger.warning(f"Failed to process commit {commit.sha}: {e}")
                    continue
        
        except GithubException as e:
            logger.error(f"Failed to collect commits from {repository}: {e}")
        
        return contributions
    
    def _collect_pull_requests(
        self,
        repository: str,
        time_period: TimePeriod,
    ) -> List[Contribution]:
        """Collect pull requests from repository."""
        contributions = []
        
        def _fetch_prs():
            repo = self.github_client.github.get_repo(repository)
            prs = repo.get_pulls(
                state="all",
                sort="updated",
                direction="desc",
            )
            return list(prs)
        
        try:
            prs = self.rate_limiter.execute_with_retry(
                _fetch_prs,
                f"collect_prs_{repository}",
                checkpoint_key=f"prs_{repository}_{time_period.start_date.date()}",
            )
            
            for pr in prs:
                # Filter by time period
                if not (time_period.start_date <= pr.created_at <= time_period.end_date):
                    continue
                
                try:
                    state = "merged" if pr.merged else ("closed" if pr.closed_at else "open")
                    
                    contribution = Contribution(
                        id=f"pr-{pr.number}",
                        type="pull_request",
                        timestamp=pr.created_at,
                        repository=repository,
                        developer=pr.user.login if pr.user else "unknown",
                        title=pr.title,
                        state=state,
                        metadata={
                            "number": pr.number,
                            "base_branch": pr.base.ref,
                            "head_branch": pr.head.ref,
                            "merged": pr.merged,
                            "review_count": pr.review_comments,
                            "comment_count": pr.comments,
                        },
                    )
                    contributions.append(contribution)
                except Exception as e:
                    logger.warning(f"Failed to process PR #{pr.number}: {e}")
                    continue
        
        except GithubException as e:
            logger.error(f"Failed to collect PRs from {repository}: {e}")
        
        return contributions
    
    def _collect_reviews(
        self,
        repository: str,
        time_period: TimePeriod,
    ) -> List[Contribution]:
        """Collect code reviews from repository."""
        contributions = []
        
        def _fetch_prs_for_reviews():
            repo = self.github_client.github.get_repo(repository)
            prs = repo.get_pulls(state="all")
            return list(prs)
        
        try:
            prs = self.rate_limiter.execute_with_retry(
                _fetch_prs_for_reviews,
                f"collect_reviews_{repository}",
                checkpoint_key=f"reviews_{repository}_{time_period.start_date.date()}",
            )
            
            for pr in prs:
                try:
                    reviews = pr.get_reviews()
                    for review in reviews:
                        # Filter by time period
                        if not (time_period.start_date <= review.submitted_at <= time_period.end_date):
                            continue
                        
                        state_map = {
                            "APPROVED": "approved",
                            "CHANGES_REQUESTED": "changes_requested",
                            "COMMENTED": "commented",
                        }
                        
                        contribution = Contribution(
                            id=f"review-{review.id}",
                            type="review",
                            timestamp=review.submitted_at,
                            repository=repository,
                            developer=review.user.login if review.user else "unknown",
                            title=f"Review PR #{pr.number}",
                            state=state_map.get(review.state, "commented"),
                            metadata={
                                "review_id": review.id,
                                "pr_number": pr.number,
                            },
                        )
                        contributions.append(contribution)
                except Exception as e:
                    logger.warning(f"Failed to process reviews for PR #{pr.number}: {e}")
                    continue
        
        except GithubException as e:
            logger.error(f"Failed to collect reviews from {repository}: {e}")
        
        return contributions
    
    def _collect_issues(
        self,
        repository: str,
        time_period: TimePeriod,
    ) -> List[Contribution]:
        """Collect issues from repository."""
        contributions = []
        
        def _fetch_issues():
            repo = self.github_client.github.get_repo(repository)
            issues = repo.get_issues(state="all", since=time_period.start_date)
            return list(issues)
        
        try:
            issues = self.rate_limiter.execute_with_retry(
                _fetch_issues,
                f"collect_issues_{repository}",
                checkpoint_key=f"issues_{repository}_{time_period.start_date.date()}",
            )
            
            for issue in issues:
                # Skip pull requests (they're issues too in GitHub API)
                if issue.pull_request:
                    continue
                
                # Filter by time period
                if not (time_period.start_date <= issue.created_at <= time_period.end_date):
                    continue
                
                try:
                    state = "closed" if issue.closed_at else "open"
                    
                    contribution = Contribution(
                        id=f"issue-{issue.number}",
                        type="issue",
                        timestamp=issue.created_at,
                        repository=repository,
                        developer=issue.user.login if issue.user else "unknown",
                        title=issue.title,
                        state=state,
                        metadata={
                            "number": issue.number,
                            "labels": [label.name for label in issue.labels],
                            "assignees": [assignee.login for assignee in issue.assignees],
                        },
                    )
                    contributions.append(contribution)
                except Exception as e:
                    logger.warning(f"Failed to process issue #{issue.number}: {e}")
                    continue
        
        except GithubException as e:
            logger.error(f"Failed to collect issues from {repository}: {e}")
        
        return contributions
    
    def _get_cache_key(
        self,
        repository: str,
        time_period: TimePeriod,
    ) -> str:
        """Generate cache key for contributions."""
        if self.cache:
            return self.cache._get_cache_key(
                "contributions",
                repository=repository,
                start_date=time_period.start_date,
                end_date=time_period.end_date,
            )
        # Fallback if no cache
        parts = [
            "contributions",
            repository.replace("/", "_"),
            time_period.start_date.strftime("%Y%m%d"),
            time_period.end_date.strftime("%Y%m%d"),
        ]
        return "_".join(parts)

