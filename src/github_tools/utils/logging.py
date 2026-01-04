"""Logging utilities for GitHub contribution analytics tools."""

import logging
import re
import sys
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive data from log messages.
    
    Prevents tokens, API keys, and other sensitive information
    from appearing in log output.
    """
    
    # Patterns to detect and redact sensitive data
    SENSITIVE_PATTERNS = [
        (r'ghp_[a-zA-Z0-9]{36,}', 'ghp_REDACTED'),  # GitHub tokens
        (r'sk-[a-zA-Z0-9]{32,}', 'sk-REDACTED'),  # OpenAI keys
        (r'AIza[0-9A-Za-z-_]{35}', 'AIzaREDACTED'),  # Google API keys
        (r'Bearer\s+[a-zA-Z0-9]{20,}', 'Bearer REDACTED'),  # Bearer tokens
        (r'password[=:]\s*["\']?[^"\'\s]+["\']?', 'password=REDACTED'),
        (r'api_key[=:]\s*["\']?[^"\'\s]+["\']?', 'api_key=REDACTED'),
        (r'token[=:]\s*["\']?[^"\'\s]+["\']?', 'token=REDACTED'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record and redact sensitive data."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = re.sub(pattern, replacement, record.msg, flags=re.IGNORECASE)
        
        if hasattr(record, 'args') and isinstance(record.args, tuple):
            redacted_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        arg = re.sub(pattern, replacement, arg, flags=re.IGNORECASE)
                    redacted_args.append(arg)
                else:
                    redacted_args.append(arg)
            record.args = tuple(redacted_args)
        
        return True


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    redact_sensitive: bool = True,
) -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARN, ERROR)
        format_string: Custom format string (optional)
        redact_sensitive: Enable sensitive data redaction (default: True)
    
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(message)s"
        )
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )
    
    logger = logging.getLogger("github_tools")
    
    # Add sensitive data filter to all handlers
    if redact_sensitive:
        sensitive_filter = SensitiveDataFilter()
        for handler in logger.handlers:
            handler.addFilter(sensitive_filter)
        # Also add to root logger to catch all logs
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(sensitive_filter)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (typically __name__)
    
    Returns:
        Logger instance
    
    Note:
        Sensitive data (tokens, API keys) is automatically redacted
        from log messages when using setup_logging().
    """
    return logging.getLogger(f"github_tools.{name}")

