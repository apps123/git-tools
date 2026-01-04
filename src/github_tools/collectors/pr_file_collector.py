"""Collector for PR file changes and diffs."""

from typing import List, Optional

from github import GithubException
from github.PullRequest import PullRequest

from github_tools.summarizers.file_pattern_detector import PRFile
from github_tools.api.client import GitHubClient
from github_tools.api.rate_limiter import RateLimiter
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class PRFileCollector:
    """
    Collects file changes and diffs from pull requests.
    
    Uses GitHub API to fetch PR file information including:
    - File names and paths
    - Additions/deletions counts
    - File status (added/modified/removed)
    - Patch/diff content
    """
    
    def __init__(
        self,
        github_client: GitHubClient,
        rate_limiter: RateLimiter,
        max_files: int = 200,
    ):
        """
        Initialize PR file collector.
        
        Args:
            github_client: GitHub API client
            rate_limiter: Rate limiter for API calls
            max_files: Maximum number of files to process per PR (summarize if exceeded)
        """
        self.github_client = github_client
        self.rate_limiter = rate_limiter
        self.max_files = max_files
    
    def collect_pr_files(
        self,
        repository: str,
        pr_number: int,
    ) -> List[PRFile]:
        """
        Collect file changes for a pull request.
        
        Args:
            repository: Repository full name (owner/repo)
            pr_number: Pull request number
        
        Returns:
            List of PRFile objects
        
        Raises:
            GithubException: If API call fails
        """
        def _fetch_files():
            repo = self.github_client.github.get_repo(repository)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            return list(files)
        
        try:
            files = self.rate_limiter.execute_with_retry(
                _fetch_files,
                f"collect_pr_files_{repository}_{pr_number}",
            )
            
            pr_files = []
            
            for file in files[:self.max_files]:  # Limit to max_files
                pr_file = PRFile(
                    filename=file.filename,
                    status=file.status,  # "added", "modified", "removed"
                    additions=file.additions,
                    deletions=file.deletions,
                    patch=file.patch if hasattr(file, 'patch') else None,
                    sha=file.sha if hasattr(file, 'sha') else None,
                )
                pr_files.append(pr_file)
            
            if len(files) > self.max_files:
                logger.warning(
                    f"PR #{pr_number} has {len(files)} files, "
                    f"processing first {self.max_files} files"
                )
            
            logger.debug(f"Collected {len(pr_files)} files for PR #{pr_number}")
            
            return pr_files
        
        except GithubException as e:
            logger.error(f"Failed to collect files for PR #{pr_number}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error collecting PR files: {e}")
            raise

