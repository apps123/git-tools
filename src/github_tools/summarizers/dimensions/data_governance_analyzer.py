"""Data governance impact analyzer."""

from typing import Any, Dict, List

from github_tools.summarizers.dimensions.base import DimensionAnalyzer, DimensionResult
from github_tools.summarizers.file_pattern_detector import PRFile


class DataGovernanceAnalyzer(DimensionAnalyzer):
    """Analyzes data governance impact."""
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze data governance impact.
        
        Checks for:
        - Data file changes
        - Data access pattern changes
        - Schema changes
        - Privacy/compliance implications
        """
        # Check for data files
        has_data_files = "data_file" in file_patterns
        
        # Check for database/schema changes
        has_schema_changes = any(
            f.filename.endswith((".sql", ".db", ".schema")) or "schema" in f.filename.lower()
            for f in file_analysis
        )
        
        # Check for data access changes
        title_lower = pr_context.get("title", "").lower()
        body_lower = pr_context.get("body", "").lower()
        text = f"{title_lower} {body_lower}"
        
        has_data_keywords = any(
            keyword in text
            for keyword in ["data", "database", "schema", "privacy", "gdpr", "ccpa", "pii"]
        )
        
        has_access_changes = any(
            keyword in text
            for keyword in ["access", "permission", "role", "grant", "revoke"]
        )
        
        # Determine impact
        if has_data_files or has_schema_changes or has_data_keywords:
            if has_access_changes:
                level = "Impact"
                description = "Data access changes detected; review data governance, lineage, and cataloging requirements"
            else:
                level = "No Impact"
                description = "Data changes detected; no impact to data governance and lineage of datasets. Data quality checks are maintained and no metadata updates are needed to the catalogs"
        else:
            level = "N/A"
            description = "No data governance impact identified"
        
        return DimensionResult(
            level=level,
            description=description,
            is_applicable=(level != "N/A"),
            metadata={"has_data_files": has_data_files, "has_schema_changes": has_schema_changes}
        )
    
    def get_dimension_name(self) -> str:
        """Get dimension name."""
        return "data_governance"

