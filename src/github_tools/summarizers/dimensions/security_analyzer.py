"""Security impact analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class SecurityAnalyzer(DimensionAnalyzer):
    """Analyzes security impact of PR changes."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze security impact.
        
        Checks for:
        - Security configuration changes (keys, certificates, secrets)
        - Network/perimeter changes
        - Authentication/authorization changes
        - Dependency vulnerabilities
        - Encryption requirements
        """
        # Check for security config files
        has_security_config = "security_config" in file_patterns
        
        # Check for network/external exposure indicators
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        has_external_exposure = any(
            keyword in title_lower or keyword in body_lower
            for keyword in ["expose", "public", "external", "endpoint", "api"]
        )
        
        # Check for authentication changes
        has_auth_changes = any(
            keyword in title_lower or keyword in body_lower
            for keyword in ["auth", "authentication", "authorization", "login", "token"]
        )
        
        # Determine impact level
        if has_security_config or has_auth_changes:
            level = "High"
            description = "Security configuration or authentication changes detected"
            if has_security_config:
                description += "; review security config files carefully"
            if has_auth_changes:
                description += "; validate authentication mechanisms"
        elif has_external_exposure:
            level = "Medium"
            description = "New external exposure detected; validate network perimeter and access controls"
        else:
            # Analyze file patterns for potential security concerns
            has_network_files = any(
                f.filename.endswith((".py", ".js", ".java")) and "route" in f.filename.lower()
                for f in file_analysis
            )
            
            if has_network_files:
                level = "Medium"
                description = "Network/routing changes detected; review for proper access controls"
            else:
                level = "Low"
                description = "No significant security concerns identified"
        
        return DimensionResult(
            level=level,
            description=description,
            is_applicable=True,
            metadata={"security_config_files": file_patterns.get("security_config", [])}
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "security"

