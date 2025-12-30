"""File-based caching utilities for GitHub contribution analytics tools."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar
from github_tools.utils.config import CacheConfig

T = TypeVar("T")


class FileCache:
    """
    File-based cache using JSON files with optional SQLite support.
    
    Supports:
    - JSON file caching for small to medium datasets
    - SQLite database for large datasets (optional)
    - TTL-based cache invalidation
    - Cache key generation from repository/time period
    """
    
    def __init__(self, config: CacheConfig):
        """
        Initialize file cache.
        
        Args:
            config: Cache configuration
        """
        self.config = config
        self.cache_dir = config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if config.use_sqlite:
            self.db_path = self.cache_dir / "cache.db"
            self._init_sqlite()
    
    def _init_sqlite(self) -> None:
        """Initialize SQLite database if enabled."""
        if not self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            conn.commit()
            conn.close()
    
    def _get_cache_key(
        self,
        prefix: str,
        repository: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate cache key from parameters.
        
        Args:
            prefix: Cache key prefix (e.g., "contributions", "developer_metrics")
            repository: Repository full name (optional)
            start_date: Start date (optional)
            end_date: End date (optional)
            **kwargs: Additional key components
        
        Returns:
            Cache key string
        """
        parts = [prefix]
        if repository:
            parts.append(repository.replace("/", "_"))
        if start_date:
            parts.append(start_date.strftime("%Y%m%d"))
        if end_date:
            parts.append(end_date.strftime("%Y%m%d"))
        for key, value in sorted(kwargs.items()):
            if value is not None:
                parts.append(f"{key}_{value}")
        return "_".join(parts)
    
    def _get_json_path(self, key: str) -> Path:
        """Get JSON file path for cache key."""
        return self.cache_dir / f"{key}.json"
    
    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for cache key."""
        return self.cache_dir / f"{key}.meta.json"
    
    def get(
        self,
        key: str,
        default: Optional[T] = None,
    ) -> Optional[T]:
        """
        Get cached value by key.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
        
        Returns:
            Cached value or default
        """
        if self.config.use_sqlite:
            return self._get_sqlite(key, default)
        return self._get_json(key, default)
    
    def _get_json(self, key: str, default: Optional[T]) -> Optional[T]:
        """Get value from JSON cache."""
        json_path = self._get_json_path(key)
        metadata_path = self._get_metadata_path(key)
        
        if not json_path.exists() or not metadata_path.exists():
            return default
        
        # Check expiration
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if datetime.now() > expires_at:
                # Expired, delete cache files
                json_path.unlink(missing_ok=True)
                metadata_path.unlink(missing_ok=True)
                return default
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid metadata, delete cache files
            json_path.unlink(missing_ok=True)
            metadata_path.unlink(missing_ok=True)
            return default
        
        # Load cached data
        try:
            with open(json_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    
    def _get_sqlite(self, key: str, default: Optional[T]) -> Optional[T]:
        """Get value from SQLite cache."""
        if not self.db_path.exists():
            return default
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT value, expires_at FROM cache_entries WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            
            if not row:
                return default
            
            value_json, expires_at_str = row
            expires_at = datetime.fromisoformat(expires_at_str)
            
            if datetime.now() > expires_at:
                # Expired, delete entry
                cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                return default
            
            return json.loads(value_json)
        except (json.JSONDecodeError, ValueError, sqlite3.Error):
            return default
        finally:
            conn.close()
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None,
    ) -> None:
        """
        Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl_hours: Time to live in hours (uses config default if None)
        """
        if ttl_hours is None:
            ttl_hours = self.config.cache_ttl_hours
        
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        if self.config.use_sqlite:
            self._set_sqlite(key, value, expires_at)
        else:
            self._set_json(key, value, expires_at)
    
    def _set_json(self, key: str, value: Any, expires_at: datetime) -> None:
        """Set value in JSON cache."""
        json_path = self._get_json_path(key)
        metadata_path = self._get_metadata_path(key)
        
        # Write data
        with open(json_path, "w") as f:
            json.dump(value, f, default=str)
        
        # Write metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
    
    def _set_sqlite(self, key: str, value: Any, expires_at: datetime) -> None:
        """Set value in SQLite cache."""
        if not self.db_path.exists():
            self._init_sqlite()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            value_json = json.dumps(value, default=str)
            cursor.execute(
                """
                INSERT OR REPLACE INTO cache_entries (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    key,
                    value_json,
                    datetime.now().isoformat(),
                    expires_at.isoformat(),
                ),
            )
            conn.commit()
        except (json.JSONEncodeError, sqlite3.Error):
            # Fallback to JSON file if SQLite fails
            self._set_json(key, value, expires_at)
        finally:
            conn.close()
    
    def delete(self, key: str) -> None:
        """
        Delete cached value by key.
        
        Args:
            key: Cache key
        """
        if self.config.use_sqlite:
            self._delete_sqlite(key)
        else:
            self._delete_json(key)
    
    def _delete_json(self, key: str) -> None:
        """Delete value from JSON cache."""
        self._get_json_path(key).unlink(missing_ok=True)
        self._get_metadata_path(key).unlink(missing_ok=True)
    
    def _delete_sqlite(self, key: str) -> None:
        """Delete value from SQLite cache."""
        if not self.db_path.exists():
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            conn.commit()
        finally:
            conn.close()
    
    def clear(self, prefix: Optional[str] = None) -> None:
        """
        Clear cache entries.
        
        Args:
            prefix: Optional prefix to clear only matching keys
        """
        if self.config.use_sqlite:
            self._clear_sqlite(prefix)
        else:
            self._clear_json(prefix)
    
    def _clear_json(self, prefix: Optional[str]) -> None:
        """Clear JSON cache entries."""
        if prefix:
            for path in self.cache_dir.glob(f"{prefix}_*.json"):
                path.unlink(missing_ok=True)
            for path in self.cache_dir.glob(f"{prefix}_*.meta.json"):
                path.unlink(missing_ok=True)
        else:
            for path in self.cache_dir.glob("*.json"):
                if path.name != "cache.db":
                    path.unlink(missing_ok=True)
    
    def _clear_sqlite(self, prefix: Optional[str]) -> None:
        """Clear SQLite cache entries."""
        if not self.db_path.exists():
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if prefix:
                cursor.execute(
                    "DELETE FROM cache_entries WHERE key LIKE ?",
                    (f"{prefix}_%",),
                )
            else:
                cursor.execute("DELETE FROM cache_entries")
            conn.commit()
        finally:
            conn.close()

