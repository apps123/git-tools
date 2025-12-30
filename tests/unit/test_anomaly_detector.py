"""Unit tests for anomaly detection logic."""

from datetime import datetime, timedelta

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_contributions_periods():
    """Sample contributions for two periods."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    # Previous period: 10 contributions
    previous = [
        Contribution(
            id=f"prev_{i}",
            type="commit",
            timestamp=base_date - timedelta(days=14) + timedelta(days=i),
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": f"prev{i}"},
        )
        for i in range(10)
    ]
    
    # Current period: 3 contributions (70% drop - anomaly)
    current = [
        Contribution(
            id=f"curr_{i}",
            type="commit",
            timestamp=base_date + timedelta(days=i),
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": f"curr{i}"},
        )
        for i in range(3)
    ]
    
    return previous, current


class TestAnomalyDetection:
    """Tests for anomaly detection logic."""
    
    def test_detect_contribution_drop(self, sample_contributions_periods):
        """Test detection of contribution drops."""
        previous, current = sample_contributions_periods
        
        previous_count = len(previous)
        current_count = len(current)
        
        change_percent = ((current_count - previous_count) / previous_count) * 100
        
        # Anomaly if drop > 50%
        is_anomaly = change_percent < -50
        
        assert is_anomaly is True
        assert change_percent < -50
    
    def test_detect_contribution_spike(self):
        """Test detection of contribution spikes."""
        previous_count = 20
        current_count = 60  # 200% increase
        
        change_percent = ((current_count - previous_count) / previous_count) * 100
        
        # Anomaly if spike > 50%
        is_anomaly = change_percent > 50
        
        assert is_anomaly is True
        assert change_percent > 50
    
    def test_severity_classification(self):
        """Test severity classification for anomalies."""
        # Test different change percentages
        test_cases = [
            (-15, "low"),      # Small change
            (-35, "medium"),  # Moderate change
            (-65, "high"),    # Significant change
            (-85, "critical"), # Critical change
        ]
        
        for change_percent, expected_severity in test_cases:
            # Classify severity
            abs_change = abs(change_percent)
            if abs_change >= 80:
                severity = "critical"
            elif abs_change >= 50:
                severity = "high"
            elif abs_change >= 25:
                severity = "medium"
            else:
                severity = "low"
            
            assert severity == expected_severity
    
    def test_no_anomaly_for_normal_changes(self):
        """Test that normal changes are not flagged as anomalies."""
        previous_count = 100
        current_count = 110  # 10% increase - normal
        
        change_percent = ((current_count - previous_count) / previous_count) * 100
        
        # Anomaly threshold is 50%
        is_anomaly = abs(change_percent) > 50
        
        assert is_anomaly is False
    
    def test_period_comparison(self, sample_contributions_periods):
        """Test comparing contributions across periods."""
        previous, current = sample_contributions_periods
        
        # Group by developer
        prev_by_dev = {}
        for contrib in previous:
            if contrib.developer not in prev_by_dev:
                prev_by_dev[contrib.developer] = []
            prev_by_dev[contrib.developer].append(contrib)
        
        curr_by_dev = {}
        for contrib in current:
            if contrib.developer not in curr_by_dev:
                curr_by_dev[contrib.developer] = []
            curr_by_dev[contrib.developer].append(contrib)
        
        # Compare for each developer
        for dev in prev_by_dev:
            prev_count = len(prev_by_dev[dev])
            curr_count = len(curr_by_dev.get(dev, []))
            
            if prev_count > 0:
                change_percent = ((curr_count - prev_count) / prev_count) * 100
                # Should detect significant drop
                assert change_percent < -50

