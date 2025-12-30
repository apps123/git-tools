"""Rate limiting and retry logic for GitHub API calls."""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar

from github import GithubException
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RateLimiter:
    """
    Rate limiter with exponential backoff and resumable checkpoints.
    
    Handles GitHub API rate limits (5000 requests/hour for authenticated users)
    with automatic retry and checkpoint-based resumption for long-running operations.
    """
    
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 300.0,
        max_retries: int = 10,
        checkpoint_dir: Optional[Path] = None,
    ):
        """
        Initialize rate limiter.
        
        Args:
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds
            max_retries: Maximum number of retries
            checkpoint_dir: Directory for storing checkpoints (optional)
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.checkpoint_dir = checkpoint_dir or Path.home() / ".github-tools" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_with_retry(
        self,
        func: Callable[[], T],
        operation_id: str,
        checkpoint_key: Optional[str] = None,
    ) -> T:
        """
        Execute function with rate limit handling and retry logic.
        
        Args:
            func: Function to execute
            operation_id: Unique identifier for this operation
            checkpoint_key: Optional checkpoint key for resumable operations
        
        Returns:
            Function result
        
        Raises:
            GithubException: If rate limit exceeded and retries exhausted
        """
        retry_count = 0
        last_exception: Optional[Exception] = None
        
        while retry_count <= self.max_retries:
            try:
                return func()
            except GithubException as e:
                last_exception = e
                
                if e.status == 403 and "rate limit" in str(e).lower():
                    # Rate limit exceeded
                    reset_time = self._get_rate_limit_reset_time(e)
                    wait_time = self._calculate_wait_time(reset_time, retry_count)
                    
                    logger.warning(
                        f"Rate limit exceeded for {operation_id}. "
                        f"Waiting {wait_time:.1f} seconds (retry {retry_count}/{self.max_retries})"
                    )
                    
                    if checkpoint_key:
                        self._save_checkpoint(checkpoint_key, operation_id, retry_count)
                    
                    time.sleep(wait_time)
                    retry_count += 1
                    
                elif e.status == 429:
                    # Too many requests (secondary rate limit)
                    wait_time = self._calculate_backoff_delay(retry_count)
                    logger.warning(
                        f"Secondary rate limit hit for {operation_id}. "
                        f"Waiting {wait_time:.1f} seconds (retry {retry_count}/{self.max_retries})"
                    )
                    
                    if checkpoint_key:
                        self._save_checkpoint(checkpoint_key, operation_id, retry_count)
                    
                    time.sleep(wait_time)
                    retry_count += 1
                    
                elif e.status >= 500:
                    # Server error, retry with backoff
                    wait_time = self._calculate_backoff_delay(retry_count)
                    logger.warning(
                        f"Server error {e.status} for {operation_id}. "
                        f"Retrying in {wait_time:.1f} seconds (retry {retry_count}/{self.max_retries})"
                    )
                    
                    time.sleep(wait_time)
                    retry_count += 1
                    
                else:
                    # Client error (4xx), don't retry
                    logger.error(f"Client error {e.status} for {operation_id}: {e}")
                    raise
        
        # Exhausted retries
        logger.error(
            f"Max retries ({self.max_retries}) exceeded for {operation_id}"
        )
        if last_exception:
            raise last_exception
        raise RuntimeError(f"Failed to execute {operation_id} after {self.max_retries} retries")
    
    def _get_rate_limit_reset_time(self, exception: GithubException) -> Optional[datetime]:
        """
        Extract rate limit reset time from exception.
        
        Args:
            exception: GitHub API exception
        
        Returns:
            Reset time or None if not available
        """
        # Try to get reset time from headers
        if hasattr(exception, "headers") and exception.headers:
            reset_header = exception.headers.get("X-RateLimit-Reset")
            if reset_header:
                try:
                    return datetime.fromtimestamp(int(reset_header))
                except (ValueError, TypeError):
                    pass
        
        # Default: reset in 1 hour
        return datetime.now() + timedelta(hours=1)
    
    def _calculate_wait_time(
        self,
        reset_time: Optional[datetime],
        retry_count: int,
    ) -> float:
        """
        Calculate wait time until rate limit resets.
        
        Args:
            reset_time: Rate limit reset time
            retry_count: Current retry count
        
        Returns:
            Wait time in seconds
        """
        if reset_time:
            wait_time = (reset_time - datetime.now()).total_seconds()
            # Add small buffer and jitter
            wait_time = max(0, wait_time) + 5 + random.uniform(0, 10)
            return min(wait_time, self.max_delay)
        
        # Fallback to exponential backoff
        return self._calculate_backoff_delay(retry_count)
    
    def _calculate_backoff_delay(self, retry_count: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            retry_count: Current retry count
        
        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (2 ** retry_count)
        jitter = random.uniform(0, delay * 0.1)  # 10% jitter
        return min(delay + jitter, self.max_delay)
    
    def _save_checkpoint(
        self,
        checkpoint_key: str,
        operation_id: str,
        retry_count: int,
    ) -> None:
        """
        Save checkpoint for resumable operations.
        
        Args:
            checkpoint_key: Unique checkpoint key
            operation_id: Operation identifier
            retry_count: Current retry count
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_key}.json"
        checkpoint_data = {
            "operation_id": operation_id,
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint_data, f)
        except IOError as e:
            logger.warning(f"Failed to save checkpoint {checkpoint_key}: {e}")
    
    def load_checkpoint(self, checkpoint_key: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint for resumable operations.
        
        Args:
            checkpoint_key: Unique checkpoint key
        
        Returns:
            Checkpoint data or None if not found
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_key}.json"
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with open(checkpoint_path) as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load checkpoint {checkpoint_key}: {e}")
            return None
    
    def clear_checkpoint(self, checkpoint_key: str) -> None:
        """
        Clear checkpoint after successful completion.
        
        Args:
            checkpoint_key: Unique checkpoint key
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_key}.json"
        checkpoint_path.unlink(missing_ok=True)

