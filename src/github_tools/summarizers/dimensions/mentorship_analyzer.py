"""Mentorship insights analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class MentorshipAnalyzer(DimensionAnalyzer):
    """Analyzes mentorship value and knowledge sharing opportunities."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze mentorship insights.
        
        Checks for:
        - Documentation quality
        - Code review collaboration
        - Educational value
        - Knowledge sharing indicators
        """
        # Check for documentation changes
        has_documentation = "documentation" in file_patterns
        
        # Analyze PR description quality
        body = pr_context.get("body", "")
        body_word_count = len(body.split()) if body else 0
        
        # Check for explanatory content
        has_detailed_description = body_word_count > 100
        
        # Check for educational keywords
        title_lower = pr_context.get("title", "").lower()
        body_lower = body.lower()
        text = f"{title_lower} {body_lower}"
        
        has_educational_keywords = any(
            keyword in text
            for keyword in ["explain", "why", "rationale", "decision", "pattern", "design"]
        )
        
        # Build description
        insights = []
        
        if has_documentation:
            insights.append("Documentation updates demonstrate knowledge sharing")
        
        if has_detailed_description:
            insights.append("Detailed PR description provides educational context")
        
        if has_educational_keywords:
            insights.append("PR includes explanations and design rationale")
        
        # Note: Actual review comments would come from PR metadata, but for now we infer
        # In real implementation, this would check PR review comment count from metadata
        has_collaboration = has_detailed_description or has_documentation
        
        if has_collaboration:
            if len(insights) > 1:
                description = "This PR shows extensive collaborative aspects and effective knowledge sharing: " + "; ".join(insights)
            else:
                description = "This PR demonstrates collaborative development and knowledge sharing opportunities"
        else:
            description = "Limited mentorship indicators; consider adding documentation or explanatory comments"
        
        return DimensionResult(
            level="Insight",
            description=description,
            is_applicable=True,
            metadata={
                "has_documentation": has_documentation,
                "description_quality": "high" if has_detailed_description else "medium",
            }
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "mentorship"

