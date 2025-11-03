"""
Authentication & Authorization Middleware

Intercepts all HTTP requests and:
1. Validates STAT7.ID tokens from headers/cookies
2. Enforces permission checks on hub access
3. Logs access attempts (audit trail)
4. Returns 401/403 on auth failures

Integration Points:
- FastAPI: Use as middleware
- Simple HTTP Server: Pre-request filter
- WebSocket: Token validation on upgrade
"""

from typing import Optional, Tuple
from enum import Enum
import logging

from stat7_auth import (
    get_auth_system,
    PermissionType,
    STAT7ID,
)

logger = logging.getLogger(__name__)


class HubAccessPolicy(Enum):
    """Which hubs require which permissions."""
    
    STAT7_THREEJS = ("stat7threejs.html", PermissionType.HUB_PUBLIC_VIEW)
    ADMIN_VIEWER = ("admin-entity-viewer.html", PermissionType.HUB_ADMIN_VIEW)
    DASHBOARD = ("phase6c_dashboard.html", PermissionType.HUB_PUBLIC_VIEW)
    PROJECT_INDEX = ("stat7_project_index.html", PermissionType.HUB_PUBLIC_VIEW)
    SETTINGS = ("/api/settings", PermissionType.HUB_SETTINGS_EDIT)


class AuthMiddleware:
    """
    Validates tokens and enforces permissions.
    
    Usage (FastAPI):
        app.add_middleware(AuthMiddleware)
    
    Usage (Simple HTTP):
        auth = AuthMiddleware()
        if not auth.check_request(path, token):
            return 403
    """
    
    def __init__(self):
        self.auth_system = get_auth_system()
        self.protected_paths = {
            "/admin-entity-viewer.html": PermissionType.HUB_ADMIN_VIEW,
            "/phase6c_dashboard.html": PermissionType.HUB_PUBLIC_VIEW,
            "/stat7threejs.html": PermissionType.HUB_PUBLIC_VIEW,
            "/stat7_project_index.html": PermissionType.HUB_PUBLIC_VIEW,
            "/api/": PermissionType.HUB_PUBLIC_VIEW,  # Default for APIs
        }
        # Public paths (no auth required)
        self.public_paths = {
            "/",
            "/index.html",
            "/health",
            "/api/health",
            "/stat7_auth.html",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/generate-qr",
        }
    
    def extract_token(
        self,
        headers: dict = None,
        cookies: dict = None,
        query_params: dict = None
    ) -> Optional[str]:
        """
        Extract STAT7 token from multiple sources (in order):
        1. Authorization: Bearer <token>
        2. Cookie: stat7_token=<token>
        3. Query: ?token=<token> (for WebSocket fallback)
        
        Returns token string or None.
        """
        
        # Try Authorization header first (most secure)
        if headers:
            auth_header = headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                return auth_header[7:]  # Remove "Bearer " prefix
        
        # Try cookie (for browser SPA)
        if cookies:
            if "stat7_token" in cookies:
                return cookies["stat7_token"]
        
        # Try query param (WebSocket fallback only)
        if query_params:
            if "token" in query_params:
                return query_params["token"]
        
        return None
    
    def check_request(
        self,
        path: str,
        token: str = None,
        headers: dict = None,
        cookies: dict = None,
        query_params: dict = None,
        ip_address: str = "",
        user_agent: str = ""
    ) -> Tuple[bool, Optional[STAT7ID], str]:
        """
        Main entry point: Check if request is authorized.
        
        Returns:
            (is_permitted, user, reason)
        """
        
        # Extract token if not provided
        if not token:
            token = self.extract_token(headers, cookies, query_params)
        
        # Public paths (no auth required)
        if path in self.public_paths:
            return True, None, "Public path"
        
        # Missing token
        if not token:
            logger.warning(f"[AUTH] Missing token for {path}")
            return False, None, "Missing STAT7 token"
        
        # Validate token
        user = self.auth_system.validate_token(token)
        if not user:
            logger.warning(f"[AUTH] Invalid token for {path}")
            self.auth_system._log_access(
                actor_id="unknown",
                action="invalid_token",
                resource=path,
                result="DENY",
                reason="Token validation failed",
                ip_address=ip_address,
                user_agent=user_agent
            )
            return False, None, "Invalid or expired token"
        
        # Find required permission for this path
        required_permission = self._get_required_permission(path)
        if not required_permission:
            # No permission requirement (shouldn't happen for protected paths)
            return True, user, "No permission required"
        
        # Check permission
        has_permission = user.has_permission(required_permission)
        
        if not has_permission:
            logger.warning(
                f"[AUTH] Permission denied: {user.id} ({user.role}) "
                f"tried to access {path}, required {required_permission.value}"
            )
            self.auth_system._log_access(
                actor_id=user.id,
                actor_role=user.role,
                action="permission_denied",
                resource=path,
                permission_required=required_permission.value,
                result="DENY",
                reason=f"Role '{user.role}' lacks permission '{required_permission.value}'",
                ip_address=ip_address,
                user_agent=user_agent
            )
            return False, user, f"Permission denied: {required_permission.value}"
        
        # Success
        logger.info(
            f"[AUTH] Access granted: {user.id} ({user.role}) -> {path}"
        )
        self.auth_system._log_access(
            actor_id=user.id,
            actor_role=user.role,
            action="access_granted",
            resource=path,
            permission_required=required_permission.value,
            result="PERMIT",
            reason="Permission check passed",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return True, user, "Access granted"
    
    def _get_required_permission(self, path: str) -> Optional[PermissionType]:
        """Map path to required permission."""
        
        # Exact matches
        for protected_path, permission in self.protected_paths.items():
            if path == protected_path:
                return permission
        
        # Prefix matches (APIs)
        if path.startswith("/api/"):
            # Default API permission (can be refined per endpoint)
            return PermissionType.HUB_PUBLIC_VIEW
        
        # Not protected
        return None
    
    def fastapi_middleware(self, app):
        """
        Attach to FastAPI as middleware.
        
        Usage:
            from fastapi import FastAPI
            from auth_middleware import AuthMiddleware
            
            app = FastAPI()
            middleware = AuthMiddleware()
            middleware.fastapi_middleware(app)
        """
        from fastapi import Request, Response
        from starlette.middleware.base import BaseHTTPMiddleware
        
        class FastAPIAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Extract request info
                path = request.url.path
                headers = dict(request.headers)
                cookies = dict(request.cookies)
                query_params = dict(request.query_params)
                ip_address = request.client.host if request.client else ""
                user_agent = headers.get("user-agent", "")
                
                # Check auth
                is_permitted, user, reason = self.check_request(
                    path=path,
                    headers=headers,
                    cookies=cookies,
                    query_params=query_params,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                if not is_permitted:
                    return Response(
                        content=f'{{"error": "Unauthorized", "reason": "{reason}"}}',
                        status_code=401 if not user else 403,
                        media_type="application/json"
                    )
                
                # Attach user to request for downstream handlers
                request.state.user = user
                
                response = await call_next(request)
                return response
        
        app.add_middleware(FastAPIAuthMiddleware)
    
    def simple_http_check(
        self,
        path: str,
        authorization_header: str = "",
        cookies_header: str = "",
        ip_address: str = ""
    ) -> Tuple[bool, Optional[STAT7ID], str]:
        """
        Quick check for Simple HTTP Server.
        
        Usage in custom handler:
            auth = AuthMiddleware()
            is_ok, user, msg = auth.simple_http_check(
                path=self.path,
                authorization_header=self.headers.get("Authorization"),
                cookies_header=self.headers.get("Cookie"),
                ip_address=self.client_address[0]
            )
            if not is_ok:
                self.send_error(401 if not user else 403)
                return
        """
        
        # Parse cookies
        cookies = {}
        if cookies_header:
            for cookie in cookies_header.split(";"):
                if "=" in cookie:
                    key, val = cookie.split("=", 1)
                    cookies[key.strip()] = val.strip()
        
        # Extract token from Authorization
        token = None
        if authorization_header.startswith("Bearer "):
            token = authorization_header[7:]
        elif "stat7_token" in cookies:
            token = cookies["stat7_token"]
        
        return self.check_request(
            path=path,
            token=token,
            ip_address=ip_address
        )


# Singleton instance
_auth_middleware: Optional[AuthMiddleware] = None

def get_auth_middleware() -> AuthMiddleware:
    """Get or create singleton auth middleware."""
    global _auth_middleware
    if _auth_middleware is None:
        _auth_middleware = AuthMiddleware()
    return _auth_middleware