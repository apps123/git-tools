"""Developer model for GitHub contribution analytics."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Developer(BaseModel):
    """
    Represents an individual contributor identified by GitHub username.
    
    Attributes:
        username: GitHub username (unique identifier)
        display_name: Display name from GitHub profile (optional)
        email: Email address (optional)
        organization_member: Whether user is a member of the organization
        team_affiliations: List of team names this developer belongs to
        is_internal: Whether contributor is internal (organization/enterprise member)
                    or external (outside collaborator)
    """
    
    username: str = Field(..., description="GitHub username (unique identifier)")
    display_name: Optional[str] = Field(None, description="Display name from GitHub profile")
    email: Optional[str] = Field(None, description="Email address")
    organization_member: bool = Field(..., description="Whether user is a member of the organization")
    team_affiliations: List[str] = Field(default_factory=list, description="List of team names")
    is_internal: bool = Field(..., description="True if organization/enterprise member, False if outside collaborator")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username is non-empty."""
        if not v or not v.strip():
            raise ValueError("Username must be non-empty")
        # Basic GitHub username format: alphanumeric, hyphens, no consecutive hyphens
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Username must match GitHub username format")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        frozen = True  # Immutable model
        json_schema_extra = {
            "example": {
                "username": "alice",
                "display_name": "Alice Developer",
                "email": "alice@example.com",
                "organization_member": True,
                "team_affiliations": ["backend-team", "infrastructure-team"],
                "is_internal": True,
            }
        }

