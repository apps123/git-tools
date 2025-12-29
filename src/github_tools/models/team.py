"""Team and Department models for GitHub contribution analytics."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Team(BaseModel):
    """
    Represents a group of developers within the organization.
    
    Attributes:
        name: Team name (unique identifier)
        members: List of developer usernames
        department: Department name this team belongs to (optional)
        description: Team description (optional)
    """
    
    name: str = Field(..., description="Team name (unique identifier)")
    members: List[str] = Field(..., description="List of developer usernames")
    department: Optional[str] = Field(None, description="Department name")
    description: Optional[str] = Field(None, description="Team description")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Team name must be non-empty")
        return v.strip()
    
    @field_validator("members")
    @classmethod
    def validate_members(cls, v: List[str]) -> List[str]:
        """Validate members list is not empty."""
        if not v:
            raise ValueError("Members list must not be empty")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "backend-team",
                "members": ["alice", "bob", "charlie"],
                "department": "engineering",
                "description": "Backend development team",
            }
        }


class Department(BaseModel):
    """
    Represents an organizational unit containing multiple teams.
    
    Attributes:
        name: Department name (unique identifier)
        teams: List of team names
        description: Department description (optional)
    """
    
    name: str = Field(..., description="Department name (unique identifier)")
    teams: List[str] = Field(..., description="List of team names")
    description: Optional[str] = Field(None, description="Department description")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Department name must be non-empty")
        return v.strip()
    
    @field_validator("teams")
    @classmethod
    def validate_teams(cls, v: List[str]) -> List[str]:
        """Validate teams list is not empty."""
        if not v:
            raise ValueError("Teams list must not be empty")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "engineering",
                "teams": ["backend-team", "frontend-team"],
                "description": "Engineering department",
            }
        }

