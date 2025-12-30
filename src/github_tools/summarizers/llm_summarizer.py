"""LLM-based PR summarization using OpenAI API."""

from typing import Optional

try:
    import openai
except ImportError:
    openai = None

from github_tools.models.contribution import Contribution
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class LLMSummarizer:
    """
    Summarizes pull requests using LLM (OpenAI API).
    
    Generates concise, contextual summaries of PRs based on title,
    description, and repository context.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 150,
    ):
        """
        Initialize LLM summarizer.
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: Model to use for summarization
            max_tokens: Maximum tokens for summary
        """
        if openai is None:
            raise ImportError(
                "openai package is required for PR summarization. "
                "Install with: pip install openai"
            )
        
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
        elif hasattr(openai, "api_key"):
            # Use environment variable if available
            pass
        else:
            logger.warning("OpenAI API key not provided. Summarization will fail.")
    
    def summarize(
        self,
        contribution: Contribution,
        repository_context: Optional[str] = None,
    ) -> str:
        """
        Generate summary for a pull request.
        
        Args:
            contribution: PR contribution to summarize
            repository_context: Optional repository context/description
        
        Returns:
            Concise summary string
        """
        if contribution.type != "pull_request":
            raise ValueError(f"Expected pull_request, got {contribution.type}")
        
        # Extract PR context
        title = contribution.title or ""
        body = contribution.metadata.get("body", "") if contribution.metadata else ""
        base_branch = contribution.metadata.get("base_branch", "") if contribution.metadata else ""
        head_branch = contribution.metadata.get("head_branch", "") if contribution.metadata else ""
        
        # Build prompt
        prompt = self._build_prompt(
            title=title,
            body=body,
            repository=contribution.repository,
            base_branch=base_branch,
            head_branch=head_branch,
            repository_context=repository_context,
        )
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical writer that creates concise, informative summaries of pull requests. Summaries should be 1-2 sentences and highlight the key changes.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            logger.error(f"Failed to generate PR summary: {e}")
            # Fallback to simple summary
            return self._fallback_summary(title, body)
    
    def _build_prompt(
        self,
        title: str,
        body: str,
        repository: str,
        base_branch: str,
        head_branch: str,
        repository_context: Optional[str] = None,
    ) -> str:
        """
        Build prompt for LLM summarization.
        
        Args:
            title: PR title
            body: PR body/description
            repository: Repository name
            base_branch: Base branch
            head_branch: Head branch
            repository_context: Optional repository context
        
        Returns:
            Prompt string
        """
        prompt_parts = [
            f"Repository: {repository}",
            f"PR Title: {title}",
        ]
        
        if repository_context:
            prompt_parts.append(f"Repository Context: {repository_context}")
        
        if body:
            prompt_parts.append(f"PR Description:\n{body}")
        
        if base_branch and head_branch:
            prompt_parts.append(f"Branch: {head_branch} -> {base_branch}")
        
        prompt_parts.append(
            "\nGenerate a concise 1-2 sentence summary of this pull request."
        )
        
        return "\n".join(prompt_parts)
    
    def _fallback_summary(self, title: str, body: str) -> str:
        """
        Generate fallback summary when LLM fails.
        
        Args:
            title: PR title
            body: PR body
        
        Returns:
            Simple summary string
        """
        if body and len(body) > 50:
            # Use first sentence of body if available
            first_sentence = body.split(".")[0]
            if len(first_sentence) > 20:
                return f"{title}. {first_sentence}."
        
        return title or "No summary available."

