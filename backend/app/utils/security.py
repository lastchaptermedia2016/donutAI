"""Security utilities for Donut AI.

This module provides:
- JWT token generation and validation
- Password hashing and verification
- Security headers
- Input sanitization
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional, Any

import jwt
from passlib.context import CryptContext

from ..config import get_settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure secret key.

    Args:
        length: Length of the secret key in bytes

    Returns:
        Hex-encoded secret key
    """
    return secrets.token_hex(length)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm="HS256",
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token data or None if invalid
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        return payload
    except jwt.PyJWTError:
        return None


def generate_csrf_token() -> str:
    """Generate a CSRF token.

    Returns:
        CSRF token string
    """
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify a CSRF token using constant-time comparison.

    Args:
        token: Token to verify
        expected: Expected token value

    Returns:
        True if tokens match, False otherwise
    """
    return hmac.compare_digest(token, expected)


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Limit length
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def get_security_headers() -> dict[str, str]:
    """Get security headers for HTTP responses.

    Returns:
        Dict of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }