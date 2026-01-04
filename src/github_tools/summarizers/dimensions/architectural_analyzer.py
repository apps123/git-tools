"""Architectural integrity analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class ArchitecturalAnalyzer(DimensionAnalyzer):
    """Analyzes architectural integrity and alignment."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze architectural integrity.
        
        Checks for:
        - IAC changes (infrastructure patterns)
        - Architectural pattern alignment
        - Structural changes
        """
        # Check for IAC files (architectural/infrastructure changes)
        has_iac = "iac" in file_patterns
        
        # Check for infrastructure patterns
        has_infrastructure = "infrastructure" in file_patterns
        
        # Analyze PR description for architectural keywords
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        text = f"{title_lower} {body_lower}"
        
        # Check for architectural alignment keywords
        has_stateless_patterns = any(
            keyword in text
            for keyword in ["stateless", "microservice", "distributed", "resilient"]
        )
        
        has_architectural_initiatives = any(
            keyword in text
            for keyword in ["initiative", "pattern", "architecture", "design", "principle"]
        )
        
        # Determine assessment
        if has_iac or has_infrastructure:
            if has_stateless_patterns or has_architectural_initiatives:
                level = "Strong"
                description = "Aligns with architectural initiatives and improves system resiliency"
                if has_stateless_patterns:
                    description = "Aligns with the 'Stateless Services' initiative and improves system resiliency"
            else:
                level = "Moderate"
                description = "Infrastructure changes detected; verify alignment with architectural principles"
        else:
            # Check for structural code changes
            has_large_changes = sum(f.additions + f.deletions for f in file_analysis) > 200
            
            if has_large_changes:
                level = "Moderate"
                description = "Significant code changes; review for architectural impact"
            else:
                level = "N/A"
                description = "No significant architectural changes identified"
        
        return DimensionResult(
            level=level,
            description=description,
            is_applicable=(level != "N/A"),
            metadata={"iac_files": file_patterns.get("iac", [])}
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "architectural"

