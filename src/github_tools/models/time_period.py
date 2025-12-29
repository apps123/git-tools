"""TimePeriod model for GitHub contribution analytics."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


PeriodType = Literal["daily", "weekly", "monthly", "quarterly", "yearly", "custom"]


class TimePeriod(BaseModel):
    """
    Represents a date range for filtering and analyzing contributions.
    
    Attributes:
        start_date: Start of time period (inclusive)
        end_date: End of time period (inclusive)
        period_type: Period type
        timezone: Timezone for date calculations (default: UTC)
    """
    
    start_date: datetime = Field(..., description="Start of time period (inclusive)")
    end_date: datetime = Field(..., description="End of time period (inclusive)")
    period_type: PeriodType = Field(..., description="Period type")
    timezone: str = Field(default="UTC", description="Timezone for date calculations")
    
    @model_validator(mode="after")
    def validate_dates(self) -> "TimePeriod":
        """Validate start_date <= end_date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        return self
    
    class Config:
        """Pydantic configuration."""
        frozen = True  # Immutable model
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "period_type": "yearly",
                "timezone": "UTC",
            }
        }

