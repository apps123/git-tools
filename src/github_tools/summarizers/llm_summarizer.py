"""LLM-based PR summarization using provider abstraction."""

from typing import Any, Dict, List, Optional

from github_tools.models.contribution import Contribution
from github_tools.summarizers.providers import (
    LLMProvider,
    get_provider,
    detect_available_providers,
    get_detection_status,
)
from github_tools.summarizers.providers.registry import ProviderRegistry
from github_tools.summarizers.file_pattern_detector import PRFile
from github_tools.summarizers.multi_dimensional_analyzer import MultiDimensionalAnalyzer
from github_tools.summarizers.prompts.dimensional_prompts import create_dimensional_prompt
from github_tools.summarizers.parsers.dimensional_parser import DimensionalParser
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class LLMSummarizer:
    """
    Summarizes pull requests using LLM providers.
    
    Generates concise, contextual summaries of PRs based on title,
    description, and repository context. Supports multiple LLM providers
    (OpenAI, Claude Desktop, Cursor, Gemini, etc.) through provider abstraction.
    """
    
    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        provider_name: Optional[str] = None,
        # Legacy OpenAI parameters for backward compatibility
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 150,
        # Provider configuration
        provider_config: Optional[dict] = None,
        auto_detect: bool = True,
    ):
        """
        Initialize LLM summarizer.
        
        Args:
            provider: Direct provider instance (overrides provider_name)
            provider_name: Provider name (openai, claude-local, cursor, gemini, etc.)
            api_key: OpenAI API key (legacy, for backward compatibility)
            model: Model name (legacy, for backward compatibility)
            max_tokens: Maximum tokens for summary (legacy, for backward compatibility)
            provider_config: Provider-specific configuration dictionary
            auto_detect: If True and provider_name not specified, auto-detect available provider
        """
        self.provider = provider
        self.provider_name = provider_name
        self.max_tokens = max_tokens
        self.provider_config = provider_config or {}
        self.auto_detect = auto_detect
        
        # Initialize provider if not provided directly
        if self.provider is None:
            if self.provider_name:
                # Use specified provider
                config = self._get_provider_config(self.provider_name)
                self.provider = get_provider(self.provider_name, **config)
                if self.provider is None:
                    raise ValueError(f"Provider '{self.provider_name}' not found or could not be initialized")
            elif api_key:
                # Legacy: Initialize OpenAI provider for backward compatibility
                logger.warning("Using legacy OpenAI API initialization. Consider using provider_name='openai' instead.")
                config = self.provider_config.get("openai", {})
                config.update({"api_key": api_key, "model": model, "max_tokens": max_tokens})
                self.provider = get_provider("openai", **config)
                if self.provider is None:
                    raise ValueError("OpenAI provider not available")
            elif auto_detect:
                # Auto-detect available provider
                available = detect_available_providers(self.provider_config)
                if not available:
                    # No providers available - get detection status for error message
                    status = get_detection_status(self.provider_config)
                    error_lines = ["No LLM providers available. Attempted providers:"]
                    for name, info in status.items():
                        error_lines.append(f"  - {name}: {info['reason']}")
                        if info['hint']:
                            error_lines.append(f"    Hint: {info['hint']}")
                    error_msg = "\n".join(error_lines)
                    raise RuntimeError(error_msg)
                
                # Use first available provider in priority order
                self.provider_name = available[0]
                config = self._get_provider_config(self.provider_name)
                self.provider = get_provider(self.provider_name, **config)
                logger.info(f"Auto-detected provider: {self.provider_name}")
            else:
                raise ValueError(
                    "No provider specified and auto_detect is False. "
                    "Specify provider, provider_name, or set auto_detect=True"
                )
        
        # Validate provider is available
        if not self.provider.is_available():
            metadata = self.provider.get_metadata()
            raise RuntimeError(
                f"Provider '{metadata.get('name', 'unknown')}' is not available. "
                f"Check configuration and ensure the provider is running/configured."
            )
        
        logger.debug(f"Using LLM provider: {self.provider.get_metadata().get('name')}")
    
    def _get_provider_config(self, provider_name: str) -> dict:
        """Get provider-specific configuration."""
        config = {}
        
        # Get provider config from provider_config dict
        if provider_name in self.provider_config:
            config.update(self.provider_config[provider_name])
        elif provider_name == "claude-local" and "claude_local" in self.provider_config:
            config.update(self.provider_config["claude_local"])
        
        # Add max_tokens if not specified
        if "max_tokens" not in config:
            config["max_tokens"] = self.max_tokens
        
        return config
    
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
            # Use provider to generate summary
            summary = self.provider.summarize(prompt)
            return summary
        except Exception as e:
            logger.error(f"Failed to generate PR summary: {e}")
            # Fallback to simple summary
            return self._fallback_summary(title, body)
    
    def summarize_dimensional(
        self,
        contribution: Contribution,
        files: List[PRFile],
        repository_context: Optional[str] = None,
        use_llm: bool = True,
    ) -> Dict[str, any]:
        """
        Generate multi-dimensional analysis summary for a pull request.
        
        Args:
            contribution: PR contribution to analyze
            files: List of PRFile objects representing changed files
            repository_context: Optional repository context/description
            use_llm: If True, use LLM for enhanced analysis; otherwise use rule-based only
        
        Returns:
            Dictionary with 'summary' and 'dimensions' keys
        """
        if contribution.type != "pull_request":
            raise ValueError(f"Expected pull_request, got {contribution.type}")
        
        # Initialize dimensional analyzer if needed
        if self._dimensional_analyzer is None:
            self._dimensional_analyzer = MultiDimensionalAnalyzer()
        
        # Extract PR context
        title = contribution.title or ""
        body = contribution.metadata.get("body", "") if contribution.metadata else ""
        
        pr_context = {
            "title": title,
            "body": body,
            "repository": contribution.repository,
        }
        
        if use_llm:
            try:
                # Use LLM for enhanced dimensional analysis
                return self._llm_dimensional_analysis(
                    pr_context, files, repository_context
                )
            except Exception as e:
                logger.warning(f"LLM dimensional analysis failed, falling back to rule-based: {e}")
                # Fall through to rule-based analysis
        
        # Rule-based dimensional analysis (fallback)
        dimensional_results = self._dimensional_analyzer.analyze(pr_context, files)
        
        # Generate base summary
        base_summary = title
        if body:
            # Use first sentence of body as summary
            first_sentence = body.split('.')[0] if '.' in body else body[:100]
            base_summary = f"{title}: {first_sentence}"
        
        # Format summary using orchestrator
        formatted_summary = self._dimensional_analyzer.format_summary(
            title, base_summary, dimensional_results, use_emoji=True
        )
        
        return {
            "summary": base_summary,
            "dimensions": {
                name: {
                    "level": result.level,
                    "description": result.description,
                    "is_applicable": result.is_applicable,
                }
                for name, result in dimensional_results.items()
            },
            "formatted": formatted_summary,
        }
    
    def _llm_dimensional_analysis(
        self,
        pr_context: Dict[str, str],
        files: List[PRFile],
        repository_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform LLM-based dimensional analysis.
        
        Args:
            pr_context: PR context dictionary
            files: List of changed files
            repository_context: Optional repository context
        
        Returns:
            Parsed dimensional analysis results
        """
        # Get file patterns
        if self._dimensional_analyzer is None:
            self._dimensional_analyzer = MultiDimensionalAnalyzer()
        
        file_patterns = self._dimensional_analyzer.pattern_detector.detect_patterns(files)
        
        # Create prompt
        system_prompt, user_prompt = create_dimensional_prompt(
            pr_context["title"],
            pr_context.get("body"),
            files,
            file_patterns,
            repository_context,
        )
        
        # Call LLM with optimized settings
        try:
            response = self.provider.summarize(
                user_prompt,
                system_prompt=system_prompt,
                max_tokens=800,  # More tokens for structured analysis (covers all 7 dimensions)
                temperature=0.3,  # Lower temperature for consistent structured output
            )
            
            # Parse response
            parser = DimensionalParser()
            parsed = parser.parse_response(response)
            
            # Convert to dimension results for consistency
            dimension_results = parser.to_dimension_results(parsed)
            
            # Format summary
            formatted_summary = self._dimensional_analyzer.format_summary(
                pr_context["title"],
                parsed.get("summary", pr_context["title"]),
                dimension_results,
                use_emoji=True,
            )
            
            return {
                "summary": parsed.get("summary", pr_context["title"]),
                "dimensions": {
                    name: {
                        "level": result.level,
                        "description": result.description,
                        "is_applicable": result.is_applicable,
                    }
                    for name, result in dimension_results.items()
                },
                "formatted": formatted_summary,
            }
        except Exception as e:
            logger.error(f"LLM dimensional analysis failed: {e}")
            raise
    
    def summarize_with_fallback(
        self,
        contribution: Contribution,
        repository_context: Optional[str] = None,
        fallback_providers: Optional[List[str]] = None,
    ) -> str:
        """
        Generate summary with automatic fallback to next available provider.
        
        Args:
            contribution: PR contribution to summarize
            repository_context: Optional repository context/description
            fallback_providers: List of provider names to try in order (auto-detected if None)
        
        Returns:
            Concise summary string
        
        Raises:
            RuntimeError: If all providers fail
        """
        providers_to_try = fallback_providers or detect_available_providers(self.provider_config)
        
        last_exception = None
        for provider_name in providers_to_try:
            try:
                config = self._get_provider_config(provider_name)
                provider = get_provider(provider_name, **config)
                if provider and provider.is_available():
                    # Try this provider
                    prompt = self._build_prompt(
                        title=contribution.title or "",
                        body=contribution.metadata.get("body", "") if contribution.metadata else "",
                        repository=contribution.repository,
                        base_branch=contribution.metadata.get("base_branch", "") if contribution.metadata else "",
                        head_branch=contribution.metadata.get("head_branch", "") if contribution.metadata else "",
                        repository_context=repository_context,
                    )
                    return provider.summarize(prompt)
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_exception = e
                continue
        
        # All providers failed - use fallback summary
        if last_exception:
            logger.error(f"All providers failed. Last error: {last_exception}")
        return self._fallback_summary(
            contribution.title or "",
            contribution.metadata.get("body", "") if contribution.metadata else ""
        )
    
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
