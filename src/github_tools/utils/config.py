"""Configuration management for GitHub contribution analytics tools."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class GitHubConfig(BaseModel):
    """GitHub API configuration."""
    
    token: str = Field(..., description="GitHub API token")
    base_url: str = Field(default="https://api.github.com", description="GitHub API base URL")
    organization: Optional[str] = Field(None, description="Organization name")
    
    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token is not empty."""
        if not v or not v.strip():
            raise ValueError("GitHub token must be non-empty")
        return v.strip()
    
    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")


class CacheConfig(BaseModel):
    """Cache configuration."""
    
    cache_dir: Path = Field(default=Path.home() / ".github-tools" / "cache", description="Cache directory")
    cache_ttl_hours: int = Field(default=1, description="Cache TTL in hours for recent data")
    cache_ttl_hours_historical: int = Field(default=24, description="Cache TTL in hours for historical data")
    use_sqlite: bool = Field(default=False, description="Use SQLite for large datasets")
    
    @field_validator("cache_dir")
    @classmethod
    def validate_cache_dir(cls, v: Path) -> Path:
        """Ensure cache directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v


class AppConfig(BaseSettings):
    """Application configuration."""
    
    github_token: Optional[str] = Field(None, description="GitHub API token (from env)")
    github_base_url: str = Field(default="https://api.github.com", description="GitHub API base URL")
    github_organization: Optional[str] = Field(None, description="GitHub organization name")
    cache_dir: Optional[Path] = Field(None, description="Cache directory path")
    cache_ttl_hours: int = Field(default=1, description="Cache TTL for recent data")
    cache_ttl_hours_historical: int = Field(default=24, description="Cache TTL for historical data")
    use_sqlite: bool = Field(default=False, description="Use SQLite for caching")
    
    class Config:
        """Pydantic settings configuration."""
        env_prefix = "GITHUB_TOOLS_"
        env_file = ".env"
        case_sensitive = False
    
    def get_github_config(self) -> GitHubConfig:
        """Get GitHub configuration."""
        token = self.github_token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(
                "GitHub token must be provided via GITHUB_TOKEN environment variable "
                "or github_token config setting"
            )
        
        return GitHubConfig(
            token=token,
            base_url=self.github_base_url,
            organization=self.github_organization,
        )
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        cache_dir = self.cache_dir or Path.home() / ".github-tools" / "cache"
        return CacheConfig(
            cache_dir=cache_dir,
            cache_ttl_hours=self.cache_ttl_hours,
            cache_ttl_hours_historical=self.cache_ttl_hours_historical,
            use_sqlite=self.use_sqlite,
        )


def load_config(config_file: Optional[Path] = None) -> AppConfig:
    """
    Load application configuration.
    
    Args:
        config_file: Optional path to configuration file (YAML/TOML)
    
    Returns:
        Application configuration instance
    """
    # For now, load from environment variables
    # TODO: Add support for YAML/TOML config files
    return AppConfig()

