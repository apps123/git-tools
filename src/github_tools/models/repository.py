"""Repository model for GitHub contribution analytics."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class Repository(BaseModel):
    """
    Represents a GitHub repository within the organization.
    
    Attributes:
        name: Repository name
        full_name: Full repository name (org/repo)
        owner: Organization or user that owns the repository
        visibility: Repository visibility (public or private)
        created_at: Repository creation timestamp
        updated_at: Last update timestamp
        default_branch: Default branch name (typically "main")
        archived: Whether repository is archived
        description: Repository description (optional)
    """
    
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name (org/repo)")
    owner: str = Field(..., description="Organization or user that owns the repository")
    visibility: Literal["public", "private"] = Field(..., description="Repository visibility")
    created_at: datetime = Field(..., description="Repository creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    default_branch: str = Field(default="main", description="Default branch name")
    archived: bool = Field(default=False, description="Whether repository is archived")
    description: Optional[str] = Field(None, description="Repository description")
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate full_name matches pattern owner/name."""
        if "/" not in v:
            raise ValueError("full_name must match pattern owner/name")
        parts = v.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("full_name must match pattern owner/name")
        return v
    
    @model_validator(mode="after")
    def validate_dates(self) -> "Repository":
        """Validate created_at <= updated_at."""
        if self.created_at > self.updated_at:
            raise ValueError("created_at must be <= updated_at")
        return self
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "my-repo",
                "full_name": "myorg/my-repo",
                "owner": "myorg",
                "visibility": "private",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-12-28T00:00:00Z",
                "default_branch": "main",
                "archived": False,
                "description": "Example repository",
            }
        }

