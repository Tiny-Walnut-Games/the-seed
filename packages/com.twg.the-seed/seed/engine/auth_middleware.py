"""
Authentication & Authorization Middleware for Phase 6B REST API

Provides JWT-based authentication, role-based access control, and audit logging.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Callable
from functools import wraps

from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# Roles
ROLE_VIEWER = "viewer"       # Read-only access
ROLE_ADMIN = "admin"         # Full access
ROLE_SYSTEM = "system"       # Internal system operations


class AuthToken:
    """Manages JWT token creation and validation."""
    
    @staticmethod
    def create_token(
        user_id: str,
        role: str = ROLE_VIEWER,
        expires_in_hours: int = JWT_EXPIRY_HOURS
    ) -> str:
        """Create JWT token for user."""
        payload = {
            "user_id": user_id,
            "role": role,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        }
        
        try:
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            logger.info(f"✅ Token created for user {user_id} with role {role}")
            return token
        except Exception as e:
            logger.error(f"❌ Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed"
            )
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("🚨 Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"🚨 Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


class BearerAuth:
    """HTTP Bearer authentication scheme."""
    
    security = HTTPBearer()
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthCredentials = Depends(HTTPBearer())) -> Dict:
        """Extract and validate bearer token."""
        token = credentials.credentials
        return AuthToken.verify_token(token)


class RBACMiddleware:
    """Role-Based Access Control middleware."""
    
    # Define endpoint access requirements
    ENDPOINT_ROLES: Dict[str, List[str]] = {
        # Public endpoints (no auth required)
        "/api/realms": [ROLE_VIEWER, ROLE_ADMIN],
        "/api/realms/{realm_id}": [ROLE_VIEWER, ROLE_ADMIN],
        "/api/npcs": [ROLE_VIEWER, ROLE_ADMIN],
        
        # Admin-only endpoints
        "/api/universe/snapshot/save": [ROLE_ADMIN, ROLE_SYSTEM],
        "/api/universe/snapshot/replay": [ROLE_ADMIN, ROLE_SYSTEM],
        "/api/admin/audit-log": [ROLE_ADMIN],
    }
    
    @staticmethod
    def require_role(allowed_roles: List[str]) -> Callable:
        """Decorator to require specific roles."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, current_user: Dict = Depends(BearerAuth.get_current_user), **kwargs):
                user_role = current_user.get("role")
                user_id = current_user.get("user_id")
                
                if user_role not in allowed_roles:
                    logger.warning(
                        f"🚨 Unauthorized access attempt by {user_id} (role: {user_role}) "
                        f"to {func.__name__}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                
                # Log authorized access
                logger.info(f"✅ Authorized access by {user_id} to {func.__name__}")
                
                return await func(*args, current_user=current_user, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def require_auth(func):
        """Decorator to require authentication."""
        @wraps(func)
        async def wrapper(*args, current_user: Dict = Depends(BearerAuth.get_current_user), **kwargs):
            logger.info(f"✅ Authenticated user: {current_user.get('user_id')}")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper


class AuditLogger:
    """Logs all critical actions for audit trail."""
    
    @staticmethod
    def log_action(
        user_id: str,
        action: str,
        resource: str,
        result: str,
        metadata: Optional[Dict] = None
    ):
        """Log an action to audit trail."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "metadata": metadata or {}
        }
        
        logger.info(f"📝 AUDIT: {audit_entry}")
        
        # In production, this would write to a secure audit database
        return audit_entry