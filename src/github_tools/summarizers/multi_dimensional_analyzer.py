"""Multi-dimensional analyzer orchestrator."""

from typing import Dict, List, Optional

from github_tools.summarizers.dimensions.base import DimensionResult
from github_tools.summarizers.dimensions.security_analyzer import SecurityAnalyzer
from github_tools.summarizers.dimensions.cost_analyzer import CostAnalyzer
from github_tools.summarizers.dimensions.operational_analyzer import OperationalAnalyzer
from github_tools.summarizers.dimensions.architectural_analyzer import ArchitecturalAnalyzer
from github_tools.summarizers.dimensions.mentorship_analyzer import MentorshipAnalyzer
from github_tools.summarizers.dimensions.data_governance_analyzer import DataGovernanceAnalyzer
from github_tools.summarizers.dimensions.ai_governance_analyzer import AIGovernanceAnalyzer
from github_tools.summarizers.file_pattern_detector import FilePatternDetector, PRFile
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class MultiDimensionalAnalyzer:
    """
    Orchestrates multi-dimensional analysis across all 7 dimensions.
    
    Analyzes PRs across:
    - Security Impact
    - Cost/FinOps Impact
    - Operational Impact
    - Architectural Integrity
    - Mentorship Insights
    - Data Governance Impact
    - AI Governance Impact
    """
    
    def __init__(self):
        """Initialize multi-dimensional analyzer with all dimension analyzers."""
        self.pattern_detector = FilePatternDetector()
        
        # Initialize all dimension analyzers
        self.analyzers = {
            "security": SecurityAnalyzer(),
            "cost": CostAnalyzer(),
            "operational": OperationalAnalyzer(),
            "architectural": ArchitecturalAnalyzer(),
            "mentorship": MentorshipAnalyzer(),
            "data_governance": DataGovernanceAnalyzer(),
            "ai_governance": AIGovernanceAnalyzer(),
        }
    
    def analyze(
        self,
        pr_context: Dict[str, Any],
        files: List[PRFile],
    ) -> Dict[str, DimensionResult]:
        """
        Analyze PR across all dimensions.
        
        Args:
            pr_context: PR context dictionary (title, body, metadata, repository_context)
            files: List of PRFile objects representing changed files
        
        Returns:
            Dictionary mapping dimension names to DimensionResult objects
        """
        # Detect file patterns
        file_patterns = self.pattern_detector.detect_patterns(files)
        
        logger.debug(f"Analyzing PR across 7 dimensions with {len(files)} files")
        
        # Analyze each dimension
        results = {}
        
        for dimension_name, analyzer in self.analyzers.items():
            try:
                result = analyzer.analyze(pr_context, files, file_patterns)
                results[dimension_name] = result
                logger.debug(f"Dimension {dimension_name}: {result.level}")
            except Exception as e:
                logger.error(f"Error analyzing dimension {dimension_name}: {e}")
                # Provide fallback result
                results[dimension_name] = DimensionResult(
                    level="N/A",
                    description=f"Analysis unavailable: {str(e)}",
                    is_applicable=False,
                )
        
        return results
    
    def format_summary(
        self,
        pr_title: str,
        summary: str,
        dimensional_results: Dict[str, DimensionResult],
        use_emoji: bool = True,
    ) -> str:
        """
        Format multi-dimensional PR summary.
        
        Args:
            pr_title: PR title
            summary: Base summary text
            dimensional_results: Dictionary of dimension results
            use_emoji: Whether to use emoji indicators
        
        Returns:
            Formatted summary string
        """
        emoji_map = {
            "security": "⚠️",
            "cost": "💰",
            "operational": "📈",
            "architectural": "🏗️",
            "mentorship": "🤝",
            "data_governance": "🏛️",
            "ai_governance": "🤖",
        }
        
        label_map = {
            "security": "Security Impact",
            "cost": "Cost/FinOps Impact",
            "operational": "Operational Impact",
            "architectural": "Architectural Integrity",
            "mentorship": "Mentorship Insight",
            "data_governance": "Data Governance",
            "ai_governance": "AI Governance",
        }
        
        lines = [f"PR: {pr_title}", f"* Summary: {summary}"]
        
        # Format each dimension
        dimension_order = [
            "security",
            "cost",
            "operational",
            "architectural",
            "mentorship",
            "data_governance",
            "ai_governance",
        ]
        
        for dim in dimension_order:
            if dim in dimensional_results:
                result = dimensional_results[dim]
                emoji = emoji_map.get(dim, "") if use_emoji else ""
                label = label_map.get(dim, dim.replace("_", " ").title())
                
                if use_emoji:
                    lines.append(f"* {emoji} {label}: {result.level}. {result.description}")
                else:
                    lines.append(f"* [{label}]: {result.level}. {result.description}")
        
        return "\n".join(lines)

