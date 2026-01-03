"""Configuration management for GitHub contribution analytics tools."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

# TOML support - Python 3.11+ has tomllib built-in
try:
    import tomllib  # type: ignore
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

# YAML support - optional
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


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


def _load_json_config(config_path: Path) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_toml_config(config_path: Path) -> Dict[str, Any]:
    """Load TOML configuration file."""
    if tomllib is None:
        raise ImportError(
            "TOML support requires Python 3.11+ (tomllib) or 'tomli' package. "
            "Install with: pip install tomli"
        )
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    if yaml is None:
        raise ImportError(
            "YAML support requires 'pyyaml' package. Install with: pip install pyyaml"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _normalize_config_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize configuration data to match AppConfig field names.
    
    Supports both nested and flat structures:
    - Nested: {"github": {"token": "...", "base_url": "..."}, "cache": {...}}
    - Flat: {"github_token": "...", "github_base_url": "...", ...}
    
    Args:
        data: Raw configuration data from file
    
    Returns:
        Normalized dictionary with AppConfig field names
    """
    normalized: Dict[str, Any] = {}
    
    # Handle nested structure
    if "github" in data:
        github = data["github"]
        if "token" in github:
            normalized["github_token"] = github["token"]
        if "base_url" in github:
            normalized["github_base_url"] = github["base_url"]
        if "organization" in github:
            normalized["github_organization"] = github["organization"]
    
    if "cache" in data:
        cache = data["cache"]
        if "directory" in cache or "dir" in cache:
            cache_dir = cache.get("directory") or cache.get("dir")
            if cache_dir:
                normalized["cache_dir"] = Path(cache_dir).expanduser()
        if "ttl_hours" in cache:
            normalized["cache_ttl_hours"] = cache["ttl_hours"]
        if "ttl_hours_historical" in cache:
            normalized["cache_ttl_hours_historical"] = cache["ttl_hours_historical"]
        if "use_sqlite" in cache:
            normalized["use_sqlite"] = cache["use_sqlite"]
    
    # Handle flat structure (also merge any top-level keys that match AppConfig fields)
    field_mapping = {
        "github_token": "github_token",
        "github_base_url": "github_base_url",
        "github_organization": "github_organization",
        "cache_dir": "cache_dir",
        "cache_ttl_hours": "cache_ttl_hours",
        "cache_ttl_hours_historical": "cache_ttl_hours_historical",
        "use_sqlite": "use_sqlite",
    }
    
    for key, field_name in field_mapping.items():
        if key in data and key not in normalized:
            value = data[key]
            # Handle cache_dir as Path
            if key == "cache_dir" and isinstance(value, str):
                value = Path(value).expanduser()
            normalized[field_name] = value
    
    return normalized


def load_config(config_file: Optional[Path] = None) -> AppConfig:
    """
    Load application configuration from file and/or environment variables.
    
    Configuration priority (highest to lowest):
    1. Environment variables (including .env file via pydantic-settings)
    2. Config file (if provided)
    3. Default values
    
    Args:
        config_file: Optional path to configuration file (JSON, TOML, or YAML)
    
    Returns:
        Application configuration instance
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is unsupported or invalid
        ImportError: If required library for file format is missing
    """
    # First, load from environment variables (this has highest priority)
    config = AppConfig()
    
    if config_file:
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine file type and load
        suffix = config_path.suffix.lower()
        if suffix == ".json":
            raw_data = _load_json_config(config_path)
        elif suffix == ".toml":
            raw_data = _load_toml_config(config_path)
        elif suffix in (".yaml", ".yml"):
            raw_data = _load_yaml_config(config_path)
        else:
            raise ValueError(
                f"Unsupported configuration file format: {suffix}. "
                f"Supported formats: .json, .toml, .yaml, .yml"
            )
        
        # Normalize the data structure
        config_data = _normalize_config_data(raw_data)
        
        # Update config with file values as defaults
        # Environment variables (already loaded) will have higher priority
        # We use model_copy with update - this effectively makes config file values
        # available, but env vars (already set) will remain unchanged
        file_updates = {}
        for key, value in config_data.items():
            current_value = getattr(config, key, None)
            # Only update if:
            # 1. Field is None (optional field not set by env)
            # 2. Field has default value that hasn't been customized by env var
            # (Note: This is simplified - in practice, env vars take precedence
            # because AppConfig() was created first and already loaded them)
            if current_value is None:
                file_updates[key] = value
            elif key == "github_base_url" and current_value == "https://api.github.com":
                # Allow config file to set base_url if still at default
                file_updates[key] = value
        
        if file_updates:
            config = config.model_copy(update=file_updates)
    
    return config

