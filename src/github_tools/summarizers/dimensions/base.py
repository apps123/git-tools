"""Base class for dimension analyzers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from github_tools.summarizers.file_pattern_detector import PRFile


@dataclass
class DimensionResult:
    """Result of dimensional analysis."""
    level: str  # Impact level (High/Medium/Low/Positive/Negative/Neutral/Strong/Moderate/Weak/Impact/No Impact/N/A)
    description: str  # Description of impact
    is_applicable: bool = True  # Whether this dimension applies to the PR
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata


class DimensionAnalyzer(ABC):
    """Abstract base class for dimension analyzers."""
    
    @abstractmethod
    def analyze(
        self,
        pr_context: Dict[str, Any],
        file_analysis: List[PRFile],
        file_patterns: Dict[str, List[str]],
    ) -> DimensionResult:
        """
        Analyze PR impact for this dimension.
        
        Args:
            pr_context: PR context (title, body, metadata, repository context)
            file_analysis: List of changed files in PR
            file_patterns: Categorized file patterns from FilePatternDetector
        
        Returns:
            DimensionResult with impact level and description
        """
        pass
    
    @abstractmethod
    def get_dimension_name(self) -> str:
        """Get the name of this dimension."""
        pass

