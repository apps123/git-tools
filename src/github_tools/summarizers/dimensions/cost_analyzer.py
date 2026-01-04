"""Cost/FinOps impact analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class CostAnalyzer(DimensionAnalyzer):
    """Analyzes cost/FinOps impact of PR changes."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze cost/FinOps impact.
        
        Checks for:
        - IAC resource changes (compute, storage, network)
        - Resource scaling/optimization
        - Cost optimization opportunities
        """
        # Check for IAC files (infrastructure changes)
        has_iac = "iac" in file_patterns
        
        # Analyze resource changes from IAC files
        iac_files = [f for f in file_analysis if f.filename.endswith((".tf", ".yaml", ".yml", ".json"))]
        
        # Simple heuristics for cost impact
        total_additions = sum(f.additions for f in iac_files)
        total_deletions = sum(f.deletions for f in iac_files)
        
        # Check for resource-related keywords
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        text = f"{title_lower} {body_lower}"
        
        has_cost_increase_keywords = any(
            keyword in text
            for keyword in ["scale up", "increase", "add instance", "new resource", "provision"]
        )
        
        has_cost_decrease_keywords = any(
            keyword in text
            for keyword in ["optimize", "reduce", "downsize", "remove", "delete resource"]
        )
        
        # Determine impact level
        if has_iac and (total_additions > total_deletions):
            if has_cost_increase_keywords:
                level = "Negative"
                description = "Infrastructure changes likely increase costs; new resources detected"
            else:
                level = "Neutral"
                description = "Infrastructure changes detected; review resource costs"
        elif has_iac and (total_deletions > total_additions):
            if has_cost_decrease_keywords:
                level = "Positive"
                description = "Infrastructure changes likely reduce costs; resources removed/optimized"
            else:
                level = "Neutral"
                description = "Infrastructure changes detected; may reduce costs"
        elif has_iac:
            level = "Neutral"
            description = "Infrastructure changes detected; cost impact neutral"
        else:
            # Check for compute/storage related changes in other files
            has_compute_changes = any(
                keyword in text
                for keyword in ["performance", "optimization", "cache", "memory", "cpu"]
            )
            
            if has_compute_changes and has_cost_decrease_keywords:
                level = "Positive"
                description = "Performance optimizations may reduce compute costs"
            elif has_compute_changes:
                level = "Neutral"
                description = "Performance-related changes; minimal cost impact"
            else:
                level = "N/A"
                description = "No significant cost impact identified"
        
        return DimensionResult(
            level=level,
            description=description,
            is_applicable=(level != "N/A"),
            metadata={"iac_files": file_patterns.get("iac", [])}
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "cost"

