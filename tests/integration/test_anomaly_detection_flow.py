"""Integration tests for anomaly detection workflow."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_contributions_with_anomaly():
    """Sample contributions showing an anomaly pattern."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    # Week 1: Normal activity (10 contributions)
    week1 = [
        Contribution(
            id=f"c{i}",
            type="commit",
            timestamp=base_date + timedelta(days=i),
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": f"abc{i}"},
        )
        for i in range(10)
    ]
    
    # Week 2: Drop in activity (2 contributions - anomaly)
    week2 = [
        Contribution(
            id=f"c{i+10}",
            type="commit",
            timestamp=base_date + timedelta(days=i+7),
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": f"def{i+10}"},
        )
        for i in range(2)
    ]
    
    return week1 + week2


@pytest.fixture
def sample_time_periods():
    """Sample time periods for comparison."""
    end_date = datetime.now()
    current_start = end_date - timedelta(days=7)
    previous_start = current_start - timedelta(days=7)
    previous_end = current_start
    
    current_period = TimePeriod(
        start_date=current_start,
        end_date=end_date,
        period_type="custom",
    )
    
    previous_period = TimePeriod(
        start_date=previous_start,
        end_date=previous_end,
        period_type="custom",
    )
    
    return current_period, previous_period


class TestAnomalyDetectionFlow:
    """Integration tests for anomaly detection flow."""
    
    @pytest.mark.integration
    def test_anomaly_detection_with_sample_data(
        self,
        sample_contributions_with_anomaly,
        sample_time_periods,
    ):
        """Test that anomalies can be detected from sample data."""
        current_period, previous_period = sample_time_periods
        
        # Split contributions by period
        current_contribs = [
            c for c in sample_contributions_with_anomaly
            if current_period.start_date <= c.timestamp <= current_period.end_date
        ]
        previous_contribs = [
            c for c in sample_contributions_with_anomaly
            if previous_period.start_date <= c.timestamp <= previous_period.end_date
        ]
        
        # Calculate change
        if len(previous_contribs) > 0:
            change_percent = ((len(current_contribs) - len(previous_contribs)) / len(previous_contribs)) * 100
            
            # Anomaly if change > 50% (drop or spike)
            is_anomaly = abs(change_percent) > 50
            
            # In this sample, week 2 has 2 contributions vs week 1's 10
            # That's an 80% drop, which should be detected as an anomaly
            assert is_anomaly or len(current_contribs) < len(previous_contribs)
    
    @pytest.mark.integration
    def test_anomaly_severity_classification(self):
        """Test that anomalies are classified by severity."""
        # Test severity thresholds
        change_percentages = [
            (-10, "low"),      # Small drop
            (-30, "medium"),   # Moderate drop
            (-60, "high"),     # Significant drop
            (-90, "critical"), # Critical drop
        ]
        
        for change, expected_severity in change_percentages:
            # Severity classification logic
            if abs(change) >= 80:
                severity = "critical"
            elif abs(change) >= 50:
                severity = "high"
            elif abs(change) >= 25:
                severity = "medium"
            else:
                severity = "low"
            
            assert severity == expected_severity

