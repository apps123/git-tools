"""Structured prompt templates for dimensional analysis."""

from typing import Dict, List, Optional, Tuple

from github_tools.summarizers.file_pattern_detector import PRFile


class DimensionalPrompts:
    """
    Prompt templates for multi-dimensional PR analysis.
    
    Provides structured prompts optimized for LLM token efficiency
    and consistent response format.
    """
    
    SYSTEM_PROMPT = """You are an expert code reviewer and software architect analyzing pull requests across multiple critical dimensions. 
Your task is to provide structured, concise analysis of PR impacts across:
1. Security Impact
2. Cost/FinOps Impact  
3. Operational Impact
4. Architectural Integrity
5. Mentorship Insights
6. Data Governance Impact
7. AI Governance Impact (SAIF framework)

For each dimension, provide:
- Impact level (High/Medium/Low/Positive/Negative/Neutral/Strong/Moderate/Weak/Impact/No Impact/N/A)
- Concise description (1-2 sentences)

Use N/A when a dimension is not applicable to the PR."""

    @staticmethod
    def create_analysis_prompt(
        pr_title: str,
        pr_body: Optional[str],
        files: List[PRFile],
        file_patterns: Dict[str, List[str]],
        repository_context: Optional[str] = None,
    ) -> str:
        """
        Create structured prompt for dimensional analysis.
        
        Args:
            pr_title: PR title
            pr_body: PR description/body
            files: List of changed files
            file_patterns: Categorized file patterns
            repository_context: Optional repository context
        
        Returns:
            Formatted prompt string
        """
        # Summarize file information efficiently
        file_summary = DimensionalPrompts._summarize_files(files, file_patterns)
        
        # Build prompt efficiently
        prompt_parts = [
            "Analyze this pull request across all 7 dimensions:",
            "",
            f"PR Title: {pr_title}",
        ]
        
        if pr_body:
            # Truncate body if too long (token optimization)
            body_text = pr_body[:500] if len(pr_body) > 500 else pr_body
            prompt_parts.append(f"PR Description: {body_text}")
        
        if repository_context:
            context_text = repository_context[:300] if len(repository_context) > 300 else repository_context
            prompt_parts.append(f"Repository Context: {context_text}")
        
        prompt_parts.append("")
        prompt_parts.append("Changed Files:")
        prompt_parts.append(file_summary)
        
        prompt_parts.append("")
        prompt_parts.append("Provide analysis in this exact JSON format:")
        prompt_parts.append(DimensionalPrompts._get_response_format())
        
        prompt_text = "\n".join(prompt_parts)
        
        # Token optimization: Limit total prompt length
        # If prompt is too long, truncate body/context
        max_prompt_length = 4000  # Approximate token limit
        if len(prompt_text) > max_prompt_length:
            # Shorten by truncating body and context if present
            if pr_body and len(pr_body) > 200:
                # Replace with truncated version
                truncated_body = pr_body[:200] + "..."
                prompt_text = prompt_text.replace(f"PR Description: {body_text}", f"PR Description: {truncated_body}")
        
        return prompt_text
    
    @staticmethod
    def _summarize_files(files: List[PRFile], file_patterns: Dict[str, List[str]]) -> str:
        """
        Summarize file changes efficiently.
        
        Optimizes token usage by summarizing large file lists and focusing
        on files most relevant to dimensional analysis.
        
        Args:
            files: List of changed files
            file_patterns: Categorized patterns
        
        Returns:
            Summarized file information
        """
        if not files:
            return "No files changed"
        
        # Limit to top files by change size for token efficiency
        sorted_files = sorted(files, key=lambda f: f.additions + f.deletions, reverse=True)
        top_files = sorted_files[:20]  # Top 20 files by change size
        
        summary_parts = []
        summary_parts.append(f"Total files changed: {len(files)}")
        
        # Add pattern categories (most important for dimensional analysis)
        if file_patterns:
            summary_parts.append("File categories:")
            # Prioritize important categories for dimensional analysis
            priority_categories = ["iac", "ai_model", "security_config", "data_file", "infrastructure"]
            for category in priority_categories:
                if category in file_patterns and file_patterns[category]:
                    summary_parts.append(f"  - {category}: {len(file_patterns[category])} files")
            # Add other categories
            for category, file_list in file_patterns.items():
                if category not in priority_categories and file_list:
                    summary_parts.append(f"  - {category}: {len(file_list)} files")
        
        # List top files (focus on IAC, security, AI models first)
        priority_files = []
        other_files = []
        
        for file in top_files[:15]:  # Top 15 files
            # Prioritize files relevant to dimensional analysis
            if any(
                pattern in file.filename.lower()
                for pattern in [".tf", ".yaml", ".yml", ".pkl", ".h5", ".key", ".pem", "security", "model"]
            ):
                priority_files.append(file)
            else:
                other_files.append(file)
        
        # List priority files first, then others
        if priority_files:
            summary_parts.append("Key changed files:")
            for file in priority_files[:10]:
                summary_parts.append(
                    f"  - {file.filename} ({file.status}): "
                    f"+{file.additions}/-{file.deletions} lines"
                )
        
        if other_files and len(priority_files) < 10:
            remaining_slots = 10 - len(priority_files)
            for file in other_files[:remaining_slots]:
                summary_parts.append(
                    f"  - {file.filename} ({file.status}): "
                    f"+{file.additions}/-{file.deletions} lines"
                )
        
        # If there are many files, mention truncation
        if len(files) > 15:
            summary_parts.append(f"  ... and {len(files) - 15} more files")
        
        return "\n".join(summary_parts)
    
    @staticmethod
    def _get_response_format() -> str:
        """Get JSON response format specification."""
        return """{
  "summary": "One-line summary of what the PR does",
  "dimensions": {
    "security": {
      "level": "High|Medium|Low|N/A",
      "description": "Security impact description"
    },
    "cost": {
      "level": "Positive|Negative|Neutral|N/A",
      "description": "Cost/FinOps impact description"
    },
    "operational": {
      "description": "Operational impact description"
    },
    "architectural": {
      "level": "Strong|Moderate|Weak|N/A",
      "description": "Architectural integrity assessment"
    },
    "mentorship": {
      "description": "Mentorship insights"
    },
    "data_governance": {
      "level": "Impact|No Impact|N/A",
      "description": "Data governance impact"
    },
    "ai_governance": {
      "level": "Impact|Low|Minor|N/A",
      "description": "AI governance impact (SAIF framework)"
    }
  }
}"""


def create_dimensional_prompt(
    pr_title: str,
    pr_body: Optional[str],
    files: List[PRFile],
    file_patterns: Dict[str, List[str]],
    repository_context: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Create system and user prompts for dimensional analysis.
    
    Args:
        pr_title: PR title
        pr_body: PR description
        files: List of changed files
        file_patterns: Categorized file patterns
        repository_context: Optional repository context
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = DimensionalPrompts.SYSTEM_PROMPT
    user_prompt = DimensionalPrompts.create_analysis_prompt(
        pr_title, pr_body, files, file_patterns, repository_context
    )
    
    return system_prompt, user_prompt

