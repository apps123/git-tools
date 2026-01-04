"""Integration tests for dimensional analysis accuracy validation."""

import json
from pathlib import Path
from typing import Dict, List

import pytest  # type: ignore[import-untyped]

from github_tools.summarizers.multi_dimensional_analyzer import MultiDimensionalAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


@pytest.fixture
def ground_truth_data():
    """Load ground truth dataset."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    ground_truth_file = fixtures_dir / "dimensional_ground_truth.json"
    
    if not ground_truth_file.exists():
        # Return empty structure if file doesn't exist yet
        return {
            "test_cases": [],
            "expected_accuracy_threshold": 0.90,
        }
    
    with open(ground_truth_file) as f:
        return json.load(f)


@pytest.fixture
def analyzer():
    """Create multi-dimensional analyzer instance."""
    return MultiDimensionalAnalyzer()


@pytest.mark.integration
class TestDimensionalAccuracy:
    """Integration tests for dimensional analysis accuracy."""
    
    def test_security_impact_accuracy(self, analyzer, ground_truth_data):
        """
        Test security impact detection accuracy meets ≥90% threshold.
        
        Validates against ground truth dataset with manually annotated PRs.
        """
        test_cases = ground_truth_data.get("test_cases", [])
        security_cases = [tc for tc in test_cases if "security" in tc.get("dimensions", {})]
        
        if not security_cases:
            pytest.skip("No security test cases in ground truth dataset")
        
        correct = 0
        total = len(security_cases)
        
        for case in security_cases:
            pr_context = {
                "title": case["pr_title"],
                "body": case.get("pr_body", ""),
                "repository": case.get("repository", "test/repo"),
            }
            
            files = [
                PRFile(
                    filename=f["filename"],
                    status=f.get("status", "modified"),
                    additions=f.get("additions", 0),
                    deletions=f.get("deletions", 0),
                    patch=f.get("patch"),
                )
                for f in case.get("files", [])
            ]
            
            results = analyzer.analyze(pr_context, files)
            actual_security_level = results["security"].level
            
            expected = case["dimensions"]["security"]["level"]
            
            # Allow flexible matching (High matches "High", case-insensitive)
            if actual_security_level.lower() == expected.lower():
                correct += 1
        
        accuracy = correct / total if total > 0 else 0.0
        
        assert accuracy >= 0.90, (
            f"Security impact accuracy {accuracy:.2%} below threshold of 90%. "
            f"Correct: {correct}/{total}"
        )
    
    def test_cost_impact_accuracy(self, analyzer, ground_truth_data):
        """Test cost/FinOps impact detection accuracy."""
        test_cases = ground_truth_data.get("test_cases", [])
        cost_cases = [tc for tc in test_cases if "cost" in tc.get("dimensions", {})]
        
        if not cost_cases:
            pytest.skip("No cost test cases in ground truth dataset")
        
        correct = 0
        total = len(cost_cases)
        
        for case in cost_cases:
            pr_context = {
                "title": case["pr_title"],
                "body": case.get("pr_body", ""),
            }
            
            files = [
                PRFile(f["filename"], f.get("status", "modified"), f.get("additions", 0), f.get("deletions", 0))
                for f in case.get("files", [])
            ]
            
            results = analyzer.analyze(pr_context, files)
            actual_cost_level = results["cost"].level
            
            expected = case["dimensions"]["cost"]["level"]
            
            if actual_cost_level.lower() == expected.lower() or (
                expected.lower() == "neutral" and actual_cost_level.lower() in ["neutral", "n/a"]
            ):
                correct += 1
        
        accuracy = correct / total if total > 0 else 0.0
        
        assert accuracy >= 0.90, (
            f"Cost impact accuracy {accuracy:.2%} below threshold of 90%. "
            f"Correct: {correct}/{total}"
        )
    
    def test_false_positive_rate(self, analyzer, ground_truth_data):
        """
        Test false positive rate for security concerns ≤10%.
        
        False positive = PR marked as High/Medium security impact when it should be Low/N/A.
        """
        test_cases = ground_truth_data.get("test_cases", [])
        security_cases = [
            tc for tc in test_cases
            if "security" in tc.get("dimensions", {})
            and tc["dimensions"]["security"]["level"].lower() in ["low", "n/a", "no impact"]
        ]
        
        if not security_cases:
            pytest.skip("No low-security test cases in ground truth dataset")
        
        false_positives = 0
        true_negatives = 0
        
        for case in security_cases:
            pr_context = {
                "title": case["pr_title"],
                "body": case.get("pr_body", ""),
            }
            
            files = [
                PRFile(f["filename"], f.get("status", "modified"), f.get("additions", 0), f.get("deletions", 0))
                for f in case.get("files", [])
            ]
            
            results = analyzer.analyze(pr_context, files)
            actual_level = results["security"].level.lower()
            
            if actual_level in ["high", "medium"]:
                false_positives += 1
            else:
                true_negatives += 1
        
        total_negative = false_positives + true_negatives
        false_positive_rate = false_positives / total_negative if total_negative > 0 else 0.0
        
        assert false_positive_rate <= 0.10, (
            f"Security false positive rate {false_positive_rate:.2%} exceeds threshold of 10%. "
            f"False positives: {false_positives}/{total_negative}"
        )
    
    def test_all_dimensions_analyzed(self, analyzer):
        """Test that all 7 dimensions are analyzed for every PR."""
        pr_context = {
            "title": "Test PR",
            "body": "Test description",
        }
        files = [PRFile("test.py", "modified", 10, 5)]
        
        results = analyzer.analyze(pr_context, files)
        
        assert len(results) == 7
        assert "security" in results
        assert "cost" in results
        assert "operational" in results
        assert "architectural" in results
        assert "mentorship" in results
        assert "data_governance" in results
        assert "ai_governance" in results

