"""Dimension analyzers for multi-dimensional PR impact analysis."""

# Import order matters - base must come first
try:
    from github_tools.summarizers.dimensions.security_analyzer import SecurityAnalyzer
    from github_tools.summarizers.dimensions.cost_analyzer import CostAnalyzer
    from github_tools.summarizers.dimensions.operational_analyzer import OperationalAnalyzer
    from github_tools.summarizers.dimensions.architectural_analyzer import ArchitecturalAnalyzer
    from github_tools.summarizers.dimensions.mentorship_analyzer import MentorshipAnalyzer
    from github_tools.summarizers.dimensions.data_governance_analyzer import DataGovernanceAnalyzer
    from github_tools.summarizers.dimensions.ai_governance_analyzer import AIGovernanceAnalyzer
    
    __all__ = [
        "SecurityAnalyzer",
        "CostAnalyzer",
        "OperationalAnalyzer",
        "ArchitecturalAnalyzer",
        "MentorshipAnalyzer",
        "DataGovernanceAnalyzer",
        "AIGovernanceAnalyzer",
    ]
except ImportError:
    # Allow partial imports during development
    __all__ = []

