"""Error handling and logging utilities for Donut AI.

This module provides:
- Custom exception classes
- Error response formatting
- Structured logging
- Error tracking integration hooks
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class DonutError(Exception):
    """Base exception for Donut AI errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()


class ValidationError(DonutError):
    """Validation error for invalid input."""

    def __init__(self, message: str, field: str = "", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, **(details or {})},
        )


class AuthenticationError(DonutError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            status_code=401,
        )


class AuthorizationError(DonutError):
    """Authorization error for insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class NotFoundError(DonutError):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id},
        )


class RateLimitError(DonutError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT",
            status_code=429,
        )


class ExternalServiceError(DonutError):
    """External service error (API calls, etc.)."""

    def __init__(self, service: str, message: str, details: Optional[dict] = None):
        super().__init__(
            message=f"{service} error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service, **(details or {})},
        )


def format_error_response(error: Exception) -> dict[str, Any]:
    """Format an error into a standardized API response.

    Args:
        error: The exception to format

    Returns:
        Standardized error response dict
    """
    if isinstance(error, DonutError):
        return {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "details": error.details,
                "timestamp": error.timestamp,
            }
        }

    # Handle unexpected errors
    logger.error(f"Unexpected error: {error}", exc_info=True)
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """Log an error with context.

    Args:
        error: The exception to log
        context: Additional context information
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        **(context or {}),
    }

    if isinstance(error, DonutError):
        logger.error(
            f"DonutError [{error.error_code}]: {error.message}",
            extra={"error_details": error_info},
        )
    else:
        logger.error(
            f"Unexpected error: {error}",
            extra={"error_details": error_info},
        )


def handle_errors(func):
    """Decorator to handle errors in async functions.

    Usage:
        @handle_errors
        async def my_function():
            ...
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DonutError:
            raise
        except Exception as e:
            log_error(e, {"function": func.__name__})
            raise DonutError(
                message=str(e),
                error_code="INTERNAL_ERROR",
                status_code=500,
            )

    return wrapper