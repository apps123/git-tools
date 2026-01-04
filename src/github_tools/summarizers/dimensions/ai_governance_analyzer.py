"""AI governance impact analyzer (SAIF framework)."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class AIGovernanceAnalyzer(DimensionAnalyzer):
    """Analyzes AI governance impact using SAIF framework."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze AI governance impact using SAIF framework.
        
        Checks for:
        - AI/ML model files
        - LLM usage
        - Model lifecycle changes
        - Ethical/security concerns
        """
        # Check for AI/ML model files
        has_ai_models = "ai_model" in file_patterns
        
        # Check for LLM/AI usage in code
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        text = f"{title_lower} {body_lower}"
        
        has_ai_keywords = any(
            keyword in text
            for keyword in ["llm", "ai", "ml", "model", "gpt", "claude", "gemini", "openai"]
        )
        
        # Check for model-related files
        has_model_code = any(
            keyword in f.filename.lower()
            for f in file_analysis
            for keyword in ["model", "ai", "ml", "train", "predict"]
        )
        
        # Check for external LLM provider usage (security concern per SAIF)
        has_external_llm = any(
            keyword in text
            for keyword in ["openai", "anthropic", "external api", "third-party"]
        )
        
        # Determine impact
        if has_ai_models or has_ai_keywords or has_model_code:
            if has_external_llm:
                level = "Minor"
                description = "Minor security risks for model exfiltration and supply chain issues from using external LLM providers"
            elif has_ai_models:
                level = "Impact"
                description = "AI/ML model changes detected; review model lifecycle, documentation, and compliance with SAIF framework"
            else:
                level = "Low"
                description = "AI/ML-related code changes; ensure compliance with AI governance policies"
        else:
            level = "N/A"
            description = "No AI governance impact identified"
        
        return DimensionResult(
            level=level,
            description=description,
            is_applicable=(level != "N/A"),
            metadata={
                "has_ai_models": has_ai_models,
                "has_external_llm": has_external_llm,
            }
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "ai_governance"

