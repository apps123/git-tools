"""Contribution model for GitHub contribution analytics."""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


ContributionType = Literal["commit", "pull_request", "review", "issue", "comment"]


class Contribution(BaseModel):
    """
    Represents a single contribution event (commit, pull request, review, issue).
    
    Attributes:
        id: Unique contribution identifier (GitHub ID or hash)
        type: Contribution type
        timestamp: When contribution occurred
        repository: Repository full name (reference to Repository)
        developer: Developer username (reference to Developer)
        title: Title/description of contribution (optional)
        state: State (e.g., "open", "closed", "merged" for PRs)
        metadata: Type-specific metadata (optional)
    """
    
    id: str = Field(..., description="Unique contribution identifier")
    type: ContributionType = Field(..., description="Contribution type")
    timestamp: datetime = Field(..., description="When contribution occurred")
    repository: str = Field(..., description="Repository full name")
    developer: str = Field(..., description="Developer username")
    title: Optional[str] = Field(None, description="Title/description of contribution")
    state: Optional[str] = Field(None, description="State (open, closed, merged, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Type-specific metadata")
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate contribution type."""
        allowed_types = ["commit", "pull_request", "review", "issue", "comment"]
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v
    
    @model_validator(mode="after")
    def validate_state(self) -> "Contribution":
        """Validate state based on contribution type."""
        if self.type == "pull_request" and self.state:
            allowed_states = ["open", "closed", "merged"]
            if self.state not in allowed_states:
                raise ValueError(f"PR state must be one of {allowed_states}")
        elif self.type == "review" and self.state:
            allowed_states = ["approved", "changes_requested", "commented"]
            if self.state not in allowed_states:
                raise ValueError(f"Review state must be one of {allowed_states}")
        elif self.type == "issue" and self.state:
            allowed_states = ["open", "closed"]
            if self.state not in allowed_states:
                raise ValueError(f"Issue state must be one of {allowed_states}")
        return self
    
    class Config:
        """Pydantic configuration."""
        frozen = True  # Immutable model
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "type": "commit",
                "timestamp": "2024-12-28T10:00:00Z",
                "repository": "myorg/my-repo",
                "developer": "alice",
                "title": "Fix bug in authentication",
                "state": None,
                "metadata": {
                    "sha": "abc123def456",
                    "message": "Fix bug in authentication",
                    "files_changed": 3,
                    "additions": 50,
                    "deletions": 20,
                },
            }
        }

