"""Contract tests for multi-dimensional PR summary format."""

import pytest
from typing import Dict, Any


def validate_dimensional_summary(summary: Dict[str, Any]) -> None:
    """
    Validate multi-dimensional PR summary structure against contract.
    
    Args:
        summary: Summary dictionary to validate
    
    Raises:
        AssertionError: If summary doesn't match contract
    """
    # Check top-level structure
    assert "summary" in summary, "Summary must have 'summary' field"
    assert "dimensions" in summary, "Summary must have 'dimensions' field"
    
    # Validate summary text
    assert isinstance(summary["summary"], str), "Summary must be a string"
    assert len(summary["summary"]) > 0, "Summary must not be empty"
    
    # Validate dimensions
    dimensions = summary["dimensions"]
    assert isinstance(dimensions, dict), "Dimensions must be a dictionary"
    
    # All 7 dimensions must be present
    required_dimensions = [
        "security",
        "cost",
        "operational",
        "architectural",
        "mentorship",
        "data_governance",
        "ai_governance",
    ]
    
    for dim_name in required_dimensions:
        assert dim_name in dimensions, f"Dimension '{dim_name}' must be present"
        
        dim = dimensions[dim_name]
        assert isinstance(dim, dict), f"Dimension '{dim_name}' must be a dictionary"
        assert "level" in dim, f"Dimension '{dim_name}' must have 'level' field"
        assert "description" in dim, f"Dimension '{dim_name}' must have 'description' field"
        assert isinstance(dim["description"], str), f"Dimension '{dim_name}' description must be a string"
        
        # Validate level values
        valid_levels = {
            "security": ["High", "Medium", "Low", "N/A"],
            "cost": ["Positive", "Negative", "Neutral", "N/A"],
            "operational": ["Applicable", "N/A"],  # Operational may not have explicit level
            "architectural": ["Strong", "Moderate", "Weak", "N/A"],
            "mentorship": ["Insight", "N/A"],  # Mentorship may not have explicit level
            "data_governance": ["Impact", "No Impact", "N/A"],
            "ai_governance": ["Impact", "Low", "Minor", "N/A"],
        }
        
        level = dim["level"]
        if dim_name in valid_levels:
            # Allow case-insensitive matching
            valid = [l.lower() for l in valid_levels[dim_name]]
            assert level.lower() in valid or level == "N/A", (
                f"Dimension '{dim_name}' level '{level}' not in valid levels: {valid_levels[dim_name]}"
            )
    
    # Optional formatted field
    if "formatted" in summary:
        assert isinstance(summary["formatted"], str), "Formatted summary must be a string"


@pytest.mark.contract
class TestPRSummaryMultidimensionalContract:
    """Contract tests for multi-dimensional PR summary format."""
    
    def test_summary_has_required_structure(self):
        """Test that multi-dimensional summary has required structure."""
        summary = {
            "summary": "Refactors data-retrieval service to use Redis cache",
            "dimensions": {
                "security": {
                    "level": "Medium",
                    "description": "Introduces new network dependencies",
                    "is_applicable": True,
                },
                "cost": {
                    "level": "Neutral",
                    "description": "Infrastructure cost changes",
                    "is_applicable": True,
                },
                "operational": {
                    "level": "Applicable",
                    "description": "SLOs and metrics configured",
                    "is_applicable": True,
                },
                "architectural": {
                    "level": "Strong",
                    "description": "Aligns with stateless services initiative",
                    "is_applicable": True,
                },
                "mentorship": {
                    "level": "Insight",
                    "description": "Good documentation",
                    "is_applicable": True,
                },
                "data_governance": {
                    "level": "No Impact",
                    "description": "No data changes",
                    "is_applicable": True,
                },
                "ai_governance": {
                    "level": "N/A",
                    "description": "No AI components",
                    "is_applicable": False,
                },
            },
            "formatted": "PR: Migration to New Caching Layer\n* Summary: ...",
        }
        
        validate_dimensional_summary(summary)
    
    def test_summary_with_n_a_dimensions(self):
        """Test that summary handles N/A dimensions correctly."""
        summary = {
            "summary": "Documentation update",
            "dimensions": {
                "security": {"level": "Low", "description": "No security concerns"},
                "cost": {"level": "N/A", "description": "No cost impact"},
                "operational": {"level": "Applicable", "description": "Doc changes"},
                "architectural": {"level": "N/A", "description": "No code changes"},
                "mentorship": {"level": "Insight", "description": "Doc improvements"},
                "data_governance": {"level": "N/A", "description": "No data changes"},
                "ai_governance": {"level": "N/A", "description": "No AI components"},
            },
        }
        
        validate_dimensional_summary(summary)
    
    def test_formatted_summary_parseable(self):
        """Test that formatted summary is parseable."""
        formatted = """PR: Migration to New Caching Layer
* Summary: Refactors data-retrieval service
* ⚠️ Security Impact: Medium. Introduces new network dependencies
* 💰 Cost/FinOps Impact: Neutral. Infrastructure cost changes
* 📈 Operational Impact: SLOs configured
* 🏗️ Architectural Integrity: Strong. Aligns with principles
* 🤝 Mentorship Insight: Good documentation
* 🏛️ Data Governance: No Impact. No data changes
* 🤖 AI Governance: N/A. No AI components"""
        
        # Should be able to parse emoji indicators
        assert "⚠️" in formatted
        assert "Security Impact" in formatted
        assert "Medium" in formatted
        
        # Should be able to parse all dimensions
        assert "Security" in formatted
        assert "Cost" in formatted
        assert "Operational" in formatted
        assert "Architectural" in formatted
        assert "Mentorship" in formatted
        assert "Data Governance" in formatted
        assert "AI Governance" in formatted

