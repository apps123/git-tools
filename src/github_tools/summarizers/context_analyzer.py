"""Repository context analysis for PR summarization."""

from typing import Dict, List, Optional

from github_tools.api.client import GitHubClient
from github_tools.models.repository import Repository
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class ContextAnalyzer:
    """
    Analyzes repository context to provide better PR summaries.
    
    Extracts repository metadata, README content, and other context
    that can help generate more accurate PR summaries.
    """
    
    def __init__(self, github_client: GitHubClient):
        """
        Initialize context analyzer.
        
        Args:
            github_client: GitHub API client
        """
        self.github_client = github_client
    
    def get_repository_context(
        self,
        repository: str,
    ) -> Optional[str]:
        """
        Get repository context for PR summarization.
        
        Args:
            repository: Repository full name (owner/repo)
        
        Returns:
            Repository context string or None
        """
        try:
            repo = self.github_client.github.get_repo(repository)
            
            context_parts = []
            
            # Add repository description
            if repo.description:
                context_parts.append(f"Repository: {repo.description}")
            
            # Add primary language
            if repo.language:
                context_parts.append(f"Primary Language: {repo.language}")
            
            # Try to get README content
            try:
                readme = repo.get_readme()
                readme_content = readme.decoded_content.decode("utf-8")
                # Extract first paragraph or summary
                first_paragraph = readme_content.split("\n\n")[0] if "\n\n" in readme_content else readme_content[:200]
                if first_paragraph:
                    context_parts.append(f"README: {first_paragraph}")
            except Exception as e:
                logger.debug(f"Could not fetch README for {repository}: {e}")
            
            return "\n".join(context_parts) if context_parts else None
        
        except Exception as e:
            logger.warning(f"Failed to get repository context for {repository}: {e}")
            return None
    
    def extract_context_tags(
        self,
        repository: str,
        pr_title: str,
        pr_body: Optional[str] = None,
    ) -> List[str]:
        """
        Extract context tags from repository and PR.
        
        Args:
            repository: Repository full name
            pr_title: PR title
            pr_body: Optional PR body
        
        Returns:
            List of context tags
        """
        tags = []
        
        # Extract from repository name
        repo_lower = repository.lower()
        if "api" in repo_lower or "backend" in repo_lower:
            tags.append("api")
        if "frontend" in repo_lower or "ui" in repo_lower or "web" in repo_lower:
            tags.append("frontend")
        if "mobile" in repo_lower or "ios" in repo_lower or "android" in repo_lower:
            tags.append("mobile")
        
        # Extract from PR title/body
        text = f"{pr_title} {pr_body or ''}".lower()
        if "bug" in text or "fix" in text:
            tags.append("bugfix")
        if "feature" in text or "add" in text:
            tags.append("feature")
        if "refactor" in text:
            tags.append("refactor")
        if "test" in text:
            tags.append("testing")
        if "doc" in text or "readme" in text:
            tags.append("documentation")
        
        return list(set(tags))  # Remove duplicates

