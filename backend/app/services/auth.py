"""Authentication service for Donut AI.

This module provides:
- Supabase Auth integration
- JWT token verification
- User session management
- Row Level Security (RLS) support
"""

import logging
from typing import Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service using Supabase Auth.
    
    Handles:
    - User registration and login
    - JWT token verification
    - Session management
    - RLS user context
    """
    
    def __init__(self):
        self._supabase = None
        self._initialized = False
    
    async def _initialize(self) -> bool:
        """Initialize Supabase client."""
        if self._initialized:
            return True
        
        try:
            from ..database import get_supabase_client
            self._supabase = get_supabase_client()
            self._initialized = True
            logger.info("Auth service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize auth service: {e}")
            return False
    
    async def sign_up(
        self,
        email: str,
        password: str,
        display_name: str = "",
    ) -> Optional[dict]:
        """Register a new user.
        
        Args:
            email: User email
            password: User password
            display_name: Display name (optional)
            
        Returns:
            User data or None if failed
        """
        if not await self._initialize():
            return None
        
        try:
            response = self._supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": display_name or email.split("@")[0],
                    }
                }
            })
            
            if response.user:
                logger.info(f"User signed up: {email}")
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "display_name": display_name,
                }
            return None
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            return None
    
    async def sign_in(
        self,
        email: str,
        password: str,
    ) -> Optional[dict]:
        """Sign in an existing user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Session data or None if failed
        """
        if not await self._initialize():
            return None
        
        try:
            response = self._supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if response.session:
                logger.info(f"User signed in: {email}")
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
            return None
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            return None
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out a user.
        
        Args:
            access_token: User's access token
            
        Returns:
            True if successful
        """
        if not await self._initialize():
            return False
        
        try:
            self._supabase.auth.sign_out()
            logger.info("User signed out")
            return True
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return False
    
    async def get_user(self, access_token: str) -> Optional[dict]:
        """Get user from access token.
        
        Args:
            access_token: JWT access token
            
        Returns:
            User data or None if invalid
        """
        if not await self._initialize():
            return None
        
        try:
            response = self._supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "display_name": response.user.user_metadata.get("display_name", ""),
                    "created_at": response.user.created_at,
                }
            return None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[dict]:
        """Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New session data or None if failed
        """
        if not await self._initialize():
            return None
        
        try:
            response = self._supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
            return None
        except Exception as e:
            logger.error(f"Refresh token error: {e}")
            return None
    
    async def verify_token(self, access_token: str) -> Optional[str]:
        """Verify a JWT token and return user_id.
        
        Args:
            access_token: JWT access token
            
        Returns:
            User ID or None if invalid
        """
        user = await self.get_user(access_token)
        if user:
            return user["user_id"]
        return None


# ============================================
# Service Singleton
# ============================================

_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get auth service singleton."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


# ============================================
# Convenience Functions
# ============================================

async def sign_up(email: str, password: str, display_name: str = "") -> Optional[dict]:
    """Convenience function for user registration."""
    service = get_auth_service()
    return await service.sign_up(email, password, display_name)


async def sign_in(email: str, password: str) -> Optional[dict]:
    """Convenience function for user login."""
    service = get_auth_service()
    return await service.sign_in(email, password)


async def sign_out(access_token: str) -> bool:
    """Convenience function for user logout."""
    service = get_auth_service()
    return await service.sign_out(access_token)


async def get_user(access_token: str) -> Optional[dict]:
    """Convenience function to get user from token."""
    service = get_auth_service()
    return await service.get_user(access_token)


async def verify_token(access_token: str) -> Optional[str]:
    """Convenience function to verify token and get user_id."""
    service = get_auth_service()
    return await service.verify_token(access_token)


# ============================================
# FastAPI Dependencies
# ============================================

async def get_current_user_id(access_token: str) -> Optional[str]:
    """FastAPI dependency to get current user ID from token.
    
    Usage:
        @app.get("/api/protected")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    return await verify_token(access_token)