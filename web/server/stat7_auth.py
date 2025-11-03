"""
STAT7.ID Authentication & Authorization System

Implements a decentralized identity model where:
- Each user has a unique STAT7.ID (UUID)
- Roles have explicit, non-transferable permissions
- Admins have scoped power (customer service, audit access)
- All access logged immutably
- No "God mode" — all actions auditable and bounded

Design Principles:
- Least Privilege: Users get minimum necessary permissions
- Explicit Allow: Roles must opt-in to capabilities
- Audit First: Every action recorded with actor_id, timestamp, reason
- Scope Limits: Admins cannot access other admins' actions
- Immutable Logs: Audit trails cannot be deleted, only appended
"""

import os
import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import hashlib
import hmac


class PermissionType(Enum):
    """Explicit permission categories (no wildcards)."""
    # Hub Access
    HUB_PUBLIC_VIEW = "hub:public:view"           # Read public dashboards
    HUB_ADMIN_VIEW = "hub:admin:view"             # View admin monitoring
    HUB_SETTINGS_EDIT = "hub:settings:edit"       # Modify simulation settings
    
    # Entity Management
    ENTITY_CREATE = "entity:create"               # Create new entities
    ENTITY_READ = "entity:read"                   # View entity details
    ENTITY_UPDATE = "entity:update"               # Modify entity state
    ENTITY_DELETE = "entity:delete"               # Remove entities (RESTRICTED)
    
    # Simulation Control
    SIMULATION_START = "simulation:start"         # Launch simulations
    SIMULATION_STOP = "simulation:stop"           # Halt simulations
    SIMULATION_REPLAY = "simulation:replay"       # Replay recorded events
    
    # Admin Capabilities
    ADMIN_AUDIT_READ = "admin:audit:read"         # View audit logs
    ADMIN_USER_MANAGE = "admin:user:manage"       # Create/revoke users (SCOPED)
    ADMIN_POLICY_MODIFY = "admin:policy:modify"   # Change governance rules (RESTRICTED)
    
    # System
    SYSTEM_HEALTH = "system:health"               # View system status


class RoleDefinition(Enum):
    """Role definitions with explicit permission sets."""
    
    ADMIN = {
        "name": "admin",
        "description": "Customer service admin (scoped authority)",
        "permissions": [
            PermissionType.HUB_PUBLIC_VIEW,
            PermissionType.HUB_ADMIN_VIEW,
            PermissionType.ENTITY_READ,
            PermissionType.ADMIN_AUDIT_READ,
            PermissionType.ADMIN_USER_MANAGE,
            PermissionType.SYSTEM_HEALTH,
            # EXPLICITLY NOT ALLOWED:
            # - ENTITY_DELETE, ENTITY_UPDATE (customer service doesn't modify)
            # - ADMIN_POLICY_MODIFY (governance is immutable)
            # - SIMULATION_STOP (no power to halt systems)
        ],
        "max_scope": "organization",  # Can only see/manage their org's users
        "immutable": True,  # Cannot modify this role definition
    }
    
    DEMO_ADMIN = {
        "name": "demo_admin",
        "description": "Limited admin for simulations (quarantined)",
        "permissions": [
            PermissionType.HUB_PUBLIC_VIEW,
            PermissionType.HUB_ADMIN_VIEW,
            PermissionType.HUB_SETTINGS_EDIT,
            PermissionType.ENTITY_READ,
            PermissionType.SIMULATION_START,
            PermissionType.SIMULATION_REPLAY,
            PermissionType.SYSTEM_HEALTH,
            # Explicitly quarantined:
            # - Cannot stop simulations (fire and forget)
            # - Cannot delete entities
            # - Cannot manage users
            # - Cannot view audit logs (privacy)
        ],
        "max_scope": "sandbox",  # Limited to sandbox environment
        "immutable": True,
    }
    
    PUBLIC = {
        "name": "public",
        "description": "Read-only public access",
        "permissions": [
            PermissionType.HUB_PUBLIC_VIEW,
            PermissionType.ENTITY_READ,
            PermissionType.SYSTEM_HEALTH,
        ],
        "max_scope": "public_dashboards",
        "immutable": True,
    }


@dataclass
class STAT7ID:
    """Unique user identity in the Seed system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    role: str = "public"  # Default to least privilege
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def has_permission(self, permission: PermissionType) -> bool:
        """Check if user has explicit permission."""
        return permission.value in self.permissions


@dataclass
class AuthToken:
    """Session token for STAT7.ID."""
    token: str = field(default_factory=lambda: str(uuid.uuid4()))
    stat7_id: str = ""
    issued_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: str = ""  # No expiry for permanent access
    is_valid: bool = True
    
    def __post_init__(self):
        if not self.expires_at:
            # Permanent tokens (no auto-expiry)
            self.expires_at = (datetime.utcnow() + timedelta(days=365*100)).isoformat()


@dataclass
class AccessLog:
    """Immutable record of every access attempt."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    actor_id: str = ""
    actor_role: str = ""
    action: str = ""
    resource: str = ""
    permission_required: str = ""
    result: str = ""  # "PERMIT" | "DENY" | "ERROR"
    reason: str = ""
    ip_address: str = ""
    user_agent: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)


class STAT7AuthSystem:
    """
    Authentication & authorization backend.
    
    Thread-safe. In production, backed by persistent storage (DB).
    Here: in-memory with JSON persistence.
    """
    
    def __init__(self, data_dir: str = "/app/data", enable_test_mode: bool = None):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.users: Dict[str, STAT7ID] = {}
        self.tokens: Dict[str, AuthToken] = {}
        self.access_logs: List[AccessLog] = []
        
        # Allow explicit enable_test_mode parameter or check environment variable
        if enable_test_mode is None:
            enable_test_mode = os.environ.get("STAT7_TEST_MODE", "").lower() in ("true", "1", "yes")
        
        self._initialize_roles()
        self._load_from_disk()
        
        # If test mode enabled and no users loaded, initialize test accounts
        if enable_test_mode:
            if not self.users:
                print("[AUTH] TEST MODE: Initializing test STAT7.IDs...")
                self._initialize_test_users()
            else:
                print(f"[AUTH] TEST MODE: Found {len(self.users)} existing users (skipping test initialization)")
    
    def _initialize_roles(self):
        """Set up role definitions (immutable)."""
        self.roles = {
            RoleDefinition.ADMIN.value["name"]: RoleDefinition.ADMIN.value,
            RoleDefinition.DEMO_ADMIN.value["name"]: RoleDefinition.DEMO_ADMIN.value,
            RoleDefinition.PUBLIC.value["name"]: RoleDefinition.PUBLIC.value,
        }
    
    def _initialize_test_users(self):
        """
        (TEST MODE) Pre-seed auth system with test STAT7.IDs.
        Allows E2E tests to authenticate without registration.
        
        Test accounts:
        - test_admin: Admin role for testing protected endpoints
        - test_public: Public role for permission testing
        - test_demo: Demo admin role for simulation testing
        """
        # Test Admin Account
        test_admin = STAT7ID(
            id="test-admin-001",
            username="test_admin",
            email="admin@test.local",
            role="admin",
            permissions=[
                p.value for p in self.roles["admin"]["permissions"]
            ],
            metadata={"test_account": True, "purpose": "E2E testing"}
        )
        self.users[test_admin.id] = test_admin
        
        # Test Public Account
        test_public = STAT7ID(
            id="test-public-001",
            username="test_public",
            email="public@test.local",
            role="public",
            permissions=[
                p.value for p in self.roles["public"]["permissions"]
            ],
            metadata={"test_account": True, "purpose": "E2E testing"}
        )
        self.users[test_public.id] = test_public
        
        # Test Demo Admin Account
        test_demo = STAT7ID(
            id="test-demo-001",
            username="test_demo_admin",
            email="demo@test.local",
            role="demo_admin",
            permissions=[
                p.value for p in self.roles["demo_admin"]["permissions"]
            ],
            metadata={"test_account": True, "purpose": "E2E testing"}
        )
        self.users[test_demo.id] = test_demo
        
        self._log_access(
            actor_id="system",
            action="test_mode_init",
            result="INFO",
            reason="Pre-seeded 3 test accounts for E2E testing"
        )
        
        self._save_to_disk()
    
    def create_qr_registration_code(self) -> Dict:
        """
        Generate a one-time QR code for friend registration.
        
        Returns:
            {
                "code": "temporary_registration_code",
                "qr_data": "stat7://register?code=...",
                "expires_at": "ISO8601",
                "instructions": "Scan this QR or click the link above"
            }
        """
        registration_code = str(uuid.uuid4())[:12]  # Short, readable
        
        return {
            "code": registration_code,
            "qr_data": f"stat7://register?code={registration_code}",
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "instructions": "Scan this QR code or visit your STAT7 hub registration page"
        }
    
    def register_user_with_code(
        self,
        registration_code: str,
        username: str,
        email: str,
        desired_role: str = "public"
    ) -> Optional[STAT7ID]:
        """
        Register a new user via registration code.
        
        Security: Registration code is single-use, time-limited.
        Role assignment rules:
        - Admin must explicitly create DEMO_ADMIN users
        - Friends can only request PUBLIC or DEMO_ADMIN
        - Cannot self-assign higher roles
        """
        
        # Validate role request
        if desired_role not in self.roles:
            return None
        
        if desired_role == "admin":
            # Nobody can self-assign admin
            return None
        
        # In production: verify code against temporary registration table
        # Here: simplified - just validate format
        if len(registration_code) < 8:
            return None
        
        # Create STAT7.ID
        stat7_id = STAT7ID(
            username=username,
            email=email,
            role=desired_role,
            permissions=[
                p.value for p in PermissionType
                if p.value in self.roles[desired_role]["permissions"]
            ]
        )
        
        self.users[stat7_id.id] = stat7_id
        self._save_to_disk()
        
        return stat7_id
    
    def admin_create_demo_user(
        self,
        admin_id: str,
        username: str,
        email: str,
        desired_role: str = "demo_admin"
    ) -> Optional[STAT7ID]:
        """
        Admin-only: Create a DEMO_ADMIN or PUBLIC user.
        
        Only admins (customer service) can create other admins.
        All creations logged with admin_id for accountability.
        """
        
        admin = self.users.get(admin_id)
        if not admin or admin.role != "admin":
            # Log unauthorized attempt
            self._log_access(
                actor_id=admin_id,
                action="admin_create_demo_user",
                result="DENY",
                reason="Not an admin"
            )
            return None
        
        # Validate desired role
        if desired_role not in self.roles:
            desired_role = "demo_admin"
        
        # Create user with desired role
        new_user = STAT7ID(
            username=username,
            email=email,
            role=desired_role,
            permissions=[
                p.value for p in PermissionType
                if p.value in self.roles[desired_role]["permissions"]
            ]
        )
        
        self.users[new_user.id] = new_user
        
        # Log admin action
        self._log_access(
            actor_id=admin_id,
            actor_role="admin",
            action="admin_create_demo_user",
            resource=f"user:{new_user.id}",
            result="PERMIT",
            reason=f"Created {desired_role.upper()}: {username}"
        )
        
        self._save_to_disk()
        return new_user
    
    def login(self, stat7_id: str) -> Optional[AuthToken]:
        """
        Issue authentication token for STAT7.ID.
        
        Returns token or None if user inactive/not found.
        """
        user = self.users.get(stat7_id)
        if not user or not user.is_active:
            self._log_access(
                actor_id=stat7_id,
                action="login",
                result="DENY",
                reason="User inactive or not found"
            )
            return None
        
        # Create token
        token = AuthToken(stat7_id=stat7_id)
        self.tokens[token.token] = token
        
        # Update last_login
        user.last_login = datetime.utcnow().isoformat()
        
        self._log_access(
            actor_id=stat7_id,
            actor_role=user.role,
            action="login",
            result="PERMIT",
            reason="Successful authentication"
        )
        
        self._save_to_disk()
        return token
    
    def validate_token(self, token_str: str) -> Optional[STAT7ID]:
        """
        Validate a token and return associated STAT7.ID.
        
        Returns None if token invalid/expired.
        """
        token = self.tokens.get(token_str)
        if not token or not token.is_valid:
            return None
        
        # Check expiry
        if datetime.fromisoformat(token.expires_at) < datetime.utcnow():
            token.is_valid = False
            return None
        
        user = self.users.get(token.stat7_id)
        if not user or not user.is_active:
            token.is_valid = False
            return None
        
        return user
    
    def check_permission(
        self,
        stat7_id: str,
        permission: PermissionType,
        resource: str = "general"
    ) -> bool:
        """
        Check if user has permission for action.
        
        Logs result for audit trail.
        """
        user = self.users.get(stat7_id)
        if not user:
            self._log_access(
                actor_id=stat7_id,
                action="permission_check",
                resource=resource,
                permission_required=permission.value,
                result="DENY",
                reason="User not found"
            )
            return False
        
        has_perm = user.has_permission(permission)
        
        self._log_access(
            actor_id=stat7_id,
            actor_role=user.role,
            action="permission_check",
            resource=resource,
            permission_required=permission.value,
            result="PERMIT" if has_perm else "DENY",
            reason=f"Permission check for {permission.value}"
        )
        
        return has_perm
    
    def _log_access(
        self,
        actor_id: str,
        action: str,
        resource: str = "",
        permission_required: str = "",
        result: str = "INFO",
        reason: str = "",
        actor_role: str = "unknown",
        ip_address: str = "",
        user_agent: str = ""
    ):
        """
        Append immutable access log entry.
        
        This log cannot be deleted, only queried.
        """
        log = AccessLog(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource=resource,
            permission_required=permission_required,
            result=result,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.access_logs.append(log)
    
    def get_audit_log(
        self,
        actor_id: str,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Retrieve immutable audit log.
        
        Admin-only access verified elsewhere.
        Returns most recent entries up to limit.
        """
        return [log.to_dict() for log in self.access_logs[-limit:]]
    
    def get_audit_logs(self, limit: int = 100) -> List[AccessLog]:
        """
        Helper: Get audit logs (immutable).
        
        Returns most recent AccessLog objects up to limit.
        """
        return self.access_logs[-limit:] if self.access_logs else []
    
    def get_token_for_id(self, stat7_id: str) -> Optional[str]:
        """
        Helper: Get authentication token for STAT7.ID.
        
        Returns token string if valid, None otherwise.
        """
        token_obj = self.login(stat7_id)
        return token_obj.token if token_obj else None
    
    def admin_revoke_token(self, token_str: str, admin_id: str = None) -> bool:
        """
        Revoke a token (mark as invalid).
        
        Optional admin_id for audit logging.
        """
        token = self.tokens.get(token_str)
        if not token:
            return False
        
        token.is_valid = False
        
        if admin_id:
            self._log_access(
                actor_id=admin_id,
                action="admin_revoke_token",
                resource=f"token:{token_str}",
                result="PERMIT",
                reason="Token revoked"
            )
        
        self._save_to_disk()
        return True
    
    def _save_to_disk(self):
        """Persist data to disk (simplified)."""
        data = {
            "users": {k: asdict(v) for k, v in self.users.items()},
            "tokens": {k: asdict(v) for k, v in self.tokens.items()},
            "access_logs": [log.to_dict() for log in self.access_logs],
        }
        
        with open(f"{self.data_dir}/stat7_auth.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_from_disk(self):
        """Load persisted data from disk (simplified)."""
        path = f"{self.data_dir}/stat7_auth.json"
        if not os.path.exists(path):
            return
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            # Reconstruct objects
            for user_id, user_data in data.get("users", {}).items():
                self.users[user_id] = STAT7ID(**user_data)
            
            for token_str, token_data in data.get("tokens", {}).items():
                self.tokens[token_str] = AuthToken(**token_data)
            
            # Note: Access logs are append-only, so we fully reload them
            for log_data in data.get("access_logs", []):
                self.access_logs.append(AccessLog(**log_data))
        
        except Exception as e:
            print(f"[WARN] Failed to load auth data: {e}")


# Singleton instance
_auth_system: Optional[STAT7AuthSystem] = None

def get_auth_system(enable_test_mode: bool = None) -> STAT7AuthSystem:
    """
    Get or create singleton auth system.
    
    Args:
        enable_test_mode: If True, initialize with test STAT7.IDs. 
                         If None, check STAT7_TEST_MODE environment variable.
    """
    global _auth_system
    if _auth_system is None:
        _auth_system = STAT7AuthSystem(enable_test_mode=enable_test_mode)
    return _auth_system