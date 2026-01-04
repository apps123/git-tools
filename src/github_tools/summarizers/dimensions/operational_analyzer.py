"""Operational impact analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class OperationalAnalyzer(DimensionAnalyzer):
    """Analyzes operational impact of PR changes."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze operational impact.
        
        Checks for:
        - Monitoring/metrics configuration
        - Deployment/infrastructure changes
        - SLO/SLA implications
        - Alert configuration
        """
        # Check for infrastructure/deployment changes
        has_infrastructure = "infrastructure" in file_patterns or "iac" in file_patterns
        
        # Check for monitoring/alerts configuration
        has_monitoring = any(
            "monitor" in f.filename.lower() or "alert" in f.filename.lower() or "metric" in f.filename.lower()
            for f in file_analysis
        )
        
        # Check deployment-related keywords
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        text = f"{title_lower} {body_lower}"
        
        has_deployment_changes = any(
            keyword in text
            for keyword in ["deploy", "rollout", "release", "infrastructure", "infra"]
        )
        
        has_monitoring_keywords = any(
            keyword in text
            for keyword in ["monitor", "alert", "metric", "slo", "sla", "observability"]
        )
        
        # Build description
        description_parts = []
        
        if has_infrastructure or has_deployment_changes:
            description_parts.append("Infrastructure/deployment changes detected")
        
        if has_monitoring or has_monitoring_keywords:
            description_parts.append("Monitoring/metrics configuration present")
        else:
            description_parts.append("Review monitoring/alert configuration requirements")
        
        # Determine if metrics/alerts are configured
        if has_monitoring or has_monitoring_keywords:
            description = "; ".join(description_parts) + ". All SLOs and metrics have been defined and alerts are configured as required"
        else:
            description = "; ".join(description_parts) + ". Ensure SLOs, metrics, and alerts are configured"
        
        return DimensionResult(
            level="Applicable",
            description=description,
            is_applicable=True,
            metadata={
                "has_infrastructure": has_infrastructure,
                "has_monitoring": has_monitoring,
            }
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "operational"

