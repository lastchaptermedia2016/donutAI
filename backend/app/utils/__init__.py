"""Utility modules for Donut AI backend.

This package contains:
- error_handler: Error handling and logging utilities
- validators: Input validation utilities
- security: Security-related utilities
"""

from .error_handler import (
    DonutError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ExternalServiceError,
    format_error_response,
    log_error,
    handle_errors,
)

__all__ = [
    "DonutError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "RateLimitError",
    "ExternalServiceError",
    "format_error_response",
    "log_error",
    "handle_errors",
]