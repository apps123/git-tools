"""Anomaly detection for contribution patterns."""

from datetime import datetime
from typing import Dict, List, Optional

from github_tools.models.contribution import Contribution
from github_tools.models.time_period import TimePeriod
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class Anomaly:
    """
    Represents a detected anomaly in contribution patterns.
    
    Attributes:
        type: Type of anomaly (contribution_drop, contribution_spike, etc.)
        entity: Entity identifier (developer, repository, team, etc.)
        entity_type: Type of entity (developer, repository, team, department)
        severity: Severity level (low, medium, high, critical)
        description: Human-readable description
        detected_at: When anomaly was detected
        previous_value: Previous period value
        current_value: Current period value
        change_percent: Percentage change
    """
    
    def __init__(
        self,
        type: str,
        entity: str,
        entity_type: str,
        severity: str,
        description: str,
        detected_at: datetime,
        previous_value: float,
        current_value: float,
        change_percent: float,
    ):
        """Initialize anomaly."""
        self.type = type
        self.entity = entity
        self.entity_type = entity_type
        self.severity = severity
        self.description = description
        self.detected_at = detected_at
        self.previous_value = previous_value
        self.current_value = current_value
        self.change_percent = change_percent
    
    def to_dict(self) -> Dict:
        """Convert anomaly to dictionary for serialization."""
        return {
            "type": self.type,
            "entity": self.entity,
            "entity_type": self.entity_type,
            "severity": self.severity,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "previous_value": self.previous_value,
            "current_value": self.current_value,
            "change_percent": round(self.change_percent, 2),
        }


class AnomalyDetector:
    """
    Detects anomalies in contribution patterns.
    
    Compares current period metrics against previous period to identify
    significant changes (drops/spikes >50%) in contribution patterns.
    """
    
    def __init__(
        self,
        threshold_percent: float = 50.0,
    ):
        """
        Initialize anomaly detector.
        
        Args:
            threshold_percent: Percentage threshold for anomaly detection (default: 50%)
        """
        self.threshold_percent = threshold_percent
    
    def detect_anomalies(
        self,
        current_contributions: List[Contribution],
        previous_contributions: List[Contribution],
        current_period: TimePeriod,
        entity_type: str = "developer",
    ) -> List[Anomaly]:
        """
        Detect anomalies by comparing current and previous periods.
        
        Args:
            current_contributions: Contributions from current period
            previous_contributions: Contributions from previous period
            current_period: Current time period
            entity_type: Type of entity to analyze (developer, repository, team)
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Group contributions by entity
        current_by_entity = self._group_by_entity(current_contributions, entity_type)
        previous_by_entity = self._group_by_entity(previous_contributions, entity_type)
        
        # Compare each entity
        all_entities = set(current_by_entity.keys()) | set(previous_by_entity.keys())
        
        for entity in all_entities:
            current_count = len(current_by_entity.get(entity, []))
            previous_count = len(previous_by_entity.get(entity, []))
            
            if previous_count == 0:
                # New entity, not an anomaly
                continue
            
            change_percent = ((current_count - previous_count) / previous_count) * 100
            
            # Check if change exceeds threshold
            if abs(change_percent) > self.threshold_percent:
                anomaly_type = "contribution_drop" if change_percent < 0 else "contribution_spike"
                severity = self._classify_severity(abs(change_percent))
                
                description = self._generate_description(
                    entity_type,
                    entity,
                    anomaly_type,
                    change_percent,
                    previous_count,
                    current_count,
                )
                
                anomaly = Anomaly(
                    type=anomaly_type,
                    entity=entity,
                    entity_type=entity_type,
                    severity=severity,
                    description=description,
                    detected_at=current_period.end_date,
                    previous_value=previous_count,
                    current_value=current_count,
                    change_percent=change_percent,
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    def _group_by_entity(
        self,
        contributions: List[Contribution],
        entity_type: str,
    ) -> Dict[str, List[Contribution]]:
        """
        Group contributions by entity type.
        
        Args:
            contributions: List of contributions
            entity_type: Type of entity (developer, repository, team)
        
        Returns:
            Dictionary mapping entity names to contributions
        """
        grouped: Dict[str, List[Contribution]] = {}
        
        for contrib in contributions:
            if entity_type == "developer":
                key = contrib.developer
            elif entity_type == "repository":
                key = contrib.repository
            else:
                # For team, would need developer lookup
                key = contrib.developer  # Placeholder
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(contrib)
        
        return grouped
    
    def _classify_severity(self, change_percent: float) -> str:
        """
        Classify anomaly severity based on change percentage.
        
        Args:
            change_percent: Absolute change percentage
        
        Returns:
            Severity level (low, medium, high, critical)
        """
        if change_percent >= 80:
            return "critical"
        elif change_percent >= 50:
            return "high"
        elif change_percent >= 25:
            return "medium"
        else:
            return "low"
    
    def _generate_description(
        self,
        entity_type: str,
        entity: str,
        anomaly_type: str,
        change_percent: float,
        previous_count: int,
        current_count: int,
    ) -> str:
        """
        Generate human-readable description for anomaly.
        
        Args:
            entity_type: Type of entity
            entity: Entity identifier
            anomaly_type: Type of anomaly
            change_percent: Change percentage
            previous_count: Previous period count
            current_count: Current period count
        
        Returns:
            Description string
        """
        direction = "dropped" if change_percent < 0 else "increased"
        abs_change = abs(change_percent)
        
        return (
            f"{entity_type.capitalize()} '{entity}' contribution count "
            f"{direction} by {abs_change:.1f}% compared to previous period "
            f"({previous_count} -> {current_count} contributions)"
        )

