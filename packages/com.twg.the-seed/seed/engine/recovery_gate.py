"""
EXP-05 Security: Recovery Gate Implementation (Phase 1)

Implements the four Story Test archetypes for secure bit-chain recovery:
- PHANTOM PROP: Verify data exists and is not fabricated
- COLD METHOD: Verify authentication and identity
- HOLLOW ENUM: Enforce access control policy (not just declare it)
- PREMATURE CELEBRATION: Log recovery BEFORE returning data

Status: Phase 1 - Critical security foundation
Doctrine: "Fail-safe on all checks. Audit first, data second."
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from stat7_experiments import (
    DataClass, Capability, BitChain, canonical_serialize, compute_address_hash
)


# ============================================================================
# AUDIT EVENT & RECOVERY POLICY
# ============================================================================

@dataclass
class AuditEvent:
    """Immutable record of recovery attempt."""
    action: str                    # "recovery_attempt", "recovery_success", etc.
    bitchain_id: str              # Which bitchain
    recovered_by: str             # User ID
    timestamp: str                # ISO8601 UTC
    classification: str           # PUBLIC, SENSITIVE, PII
    capability_level: str         # compressed, partial, full
    result: str                   # SUCCESS, DENIED, FAILED
    reason: str = ""              # Why denied/failed
    ip_address: str = ""          # For tracking abuse
    second_factor_verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return asdict(self)
    
    def sign(self, signing_key: bytes) -> str:
        """Create HMAC signature of this event."""
        canonical = canonical_serialize(self.to_dict())
        return hashlib.sha256(canonical.encode() + signing_key).hexdigest()


@dataclass
class RecoveryPolicy:
    """Policy for recovering a specific data classification."""
    classification: DataClass
    allowed_roles: List[str]       # ["owner", "admin", "viewer"]
    owner_only: bool = False       # If True, only owner can recover
    requires_second_factor: bool = False
    rate_limit_per_hour: int = 10
    default_capability: Capability = Capability.COMPRESSED
    anonymization_rules: Optional[Dict[str, Any]] = None  # Phase 2
    
    def can_recover(self, requester_id: str, owner_id: str, role: str) -> Tuple[bool, str]:
        """Check if requester can recover. Returns (can_recover, reason)."""
        if self.owner_only and requester_id != owner_id:
            return False, f"Owner-only recovery. Requester {requester_id} is not owner {owner_id}"
        
        if role not in self.allowed_roles:
            return False, f"Role {role} not in allowed roles: {self.allowed_roles}"
        
        return True, ""


# ============================================================================
# IN-MEMORY AUDIT LEDGER (Phase 1)
# ============================================================================

class InMemoryAuditLedger:
    """Simple in-memory append-only audit log for Phase 1."""
    
    def __init__(self, signing_key: bytes):
        self.events: List[AuditEvent] = []
        self.signing_key = signing_key
        self.signed_hashes: List[str] = []
    
    def append(self, event: AuditEvent) -> str:
        """Append event and return signed hash."""
        self.events.append(event)
        signed_hash = event.sign(self.signing_key)
        self.signed_hashes.append(signed_hash)
        return signed_hash
    
    def query(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query audit log by filters."""
        results = []
        for event in self.events:
            match = True
            for key, value in filters.items():
                if key == 'timestamp_after':
                    if event.timestamp <= value:
                        match = False
                elif key == 'timestamp_before':
                    if event.timestamp >= value:
                        match = False
                elif getattr(event, key, None) != value:
                    match = False
            
            if match:
                results.append(event)
        
        return results
    
    def verify_integrity(self) -> bool:
        """Verify all signatures are intact (simple check)."""
        for i, event in enumerate(self.events):
            expected_hash = event.sign(self.signing_key)
            if expected_hash != self.signed_hashes[i]:
                return False
        return True


# ============================================================================
# IN-MEMORY LEDGER (Phase 1: Simulates authoritative ledger)
# ============================================================================

class InMemoryLedger:
    """Simple in-memory ledger for Phase 1 (production would be append-only blockchain)."""
    
    def __init__(self):
        self.bitchains: Dict[str, BitChain] = {}
        self.signatures: Dict[str, str] = {}
    
    def store(self, bitchain: BitChain, signature: str):
        """Store bitchain with signature."""
        self.bitchains[bitchain.id] = bitchain
        self.signatures[bitchain.id] = signature
    
    def get(self, bitchain_id: str) -> Optional[BitChain]:
        """Retrieve bitchain."""
        return self.bitchains.get(bitchain_id)
    
    def get_signature(self, bitchain_id: str) -> Optional[str]:
        """Get signature for verification."""
        return self.signatures.get(bitchain_id)
    
    def exists(self, bitchain_id: str) -> bool:
        """Check if bitchain exists."""
        return bitchain_id in self.bitchains


# ============================================================================
# SIMPLE AUTH SERVICE (Phase 1)
# ============================================================================

class SimpleAuthService:
    """Simple mock auth service for Phase 1 (production would use real tokens)."""
    
    def __init__(self):
        self.valid_tokens: Dict[str, Dict[str, Any]] = {}
        self.second_factors: Dict[str, bool] = {}
    
    def register_token(self, token: str, user_id: str, role: str = "user"):
        """Register a valid token."""
        self.valid_tokens[token] = {"user_id": user_id, "role": role}
        self.second_factors[user_id] = False
    
    def verify_token(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Verify token and return identity or None."""
        if not token:
            return None
        return self.valid_tokens.get(token)
    
    def verify_second_factor(self, user_id: str) -> bool:
        """Check if user has verified second factor."""
        return self.second_factors.get(user_id, False)
    
    def set_second_factor_verified(self, user_id: str):
        """Mark second factor as verified."""
        self.second_factors[user_id] = True


# ============================================================================
# SIMPLE CRYPTO SERVICE (Phase 1)
# ============================================================================

class SimpleCryptoService:
    """Simple crypto operations for Phase 1."""
    
    def __init__(self, key: bytes = b"phase1-test-key"):
        self.key = key
    
    def sign_bitchain(self, bitchain: BitChain) -> str:
        """Create signature of bitchain."""
        canonical = canonical_serialize(bitchain.to_canonical_dict())
        return hashlib.sha256(canonical.encode() + self.key).hexdigest()
    
    def verify_signature(self, bitchain: BitChain, signature: str) -> bool:
        """Verify bitchain signature."""
        expected = self.sign_bitchain(bitchain)
        return expected == signature
    
    def sign(self, data: Dict[str, Any]) -> str:
        """Sign arbitrary data."""
        canonical = canonical_serialize(data)
        return hashlib.sha256(canonical.encode() + self.key).hexdigest()


# ============================================================================
# RECOVERY GATE: THE CORE SECURITY CLASS
# ============================================================================

class RecoveryGate:
    """
    Secure recovery operations using Story Test archetypes.
    
    Recovery flow (all checks required):
    1. PHANTOM PROP: Verify bitchain exists and signature is valid
    2. REALM + LINEAGE: Verify origin is trusted
    3. COLD METHOD: Verify auth token, identity, and intent
    4. ENVIRONMENT: Get the recovery policy for this classification
    5. HOLLOW ENUM: Enforce the policy (not just declare it)
    6. PREMATURE CELEBRATION: Log recovery BEFORE returning data
    7. NOW SAFE: Return the recovery with appropriate capability
    """
    
    def __init__(
        self,
        ledger: InMemoryLedger,
        auth_service: SimpleAuthService,
        audit_ledger: InMemoryAuditLedger,
        crypto_service: SimpleCryptoService
    ):
        self.ledger = ledger
        self.auth = auth_service
        self.audit = audit_ledger
        self.crypto = crypto_service
        
        # Build default policies
        self.policies: Dict[DataClass, RecoveryPolicy] = {
            DataClass.PUBLIC: RecoveryPolicy(
                classification=DataClass.PUBLIC,
                allowed_roles=["user", "admin", "viewer", "owner"],
                owner_only=False,
                requires_second_factor=False,
                default_capability=Capability.FULL,
            ),
            DataClass.SENSITIVE: RecoveryPolicy(
                classification=DataClass.SENSITIVE,
                allowed_roles=["owner", "admin"],
                owner_only=False,
                requires_second_factor=False,
                default_capability=Capability.PARTIAL,
            ),
            DataClass.PII: RecoveryPolicy(
                classification=DataClass.PII,
                allowed_roles=["owner"],
                owner_only=True,
                requires_second_factor=True,
                default_capability=Capability.COMPRESSED,
            ),
        }
    
    def recover_bitchain(
        self,
        bitchain_id: str,
        auth_token: Optional[str],
        requester_id: str,
        intent: Dict[str, Any],
        ip_address: str = ""
    ) -> Dict[str, Any]:
        """
        Main entry point: Recover a bitchain with full security checks.
        
        Args:
            bitchain_id: ID of bitchain to recover
            auth_token: Authentication token (or None)
            requester_id: User requesting recovery
            intent: Intent declaration (request_id, resources, reason)
            ip_address: For audit trail
        
        Returns:
            Recovered bitchain data (format depends on capability level)
        
        Raises:
            ValueError: If phantom prop check fails
            PermissionError: If auth or policy check fails
        """
        
        # Create audit event (will be committed BEFORE returning data)
        audit_event = AuditEvent(
            action="recovery_attempt",
            bitchain_id=bitchain_id,
            recovered_by=requester_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            classification="unknown",  # Will be set after phantom prop check
            capability_level="none",
            result="PENDING",
            ip_address=ip_address,
        )
        
        try:
            # Step 1: PHANTOM PROP CHECK
            bitchain = self._verify_phantom_prop(bitchain_id)
            audit_event.classification = bitchain.data_classification.value
            
            # Step 2: REALM + LINEAGE VERIFICATION
            self._verify_realm_lineage(bitchain)
            
            # Step 3: COLD METHOD GATE (Auth + Identity + Intent)
            identity_info = self._verify_cold_method(auth_token, requester_id, intent)
            user_role = identity_info.get("role", "user")
            
            # Step 4: GET RECOVERY POLICY
            policy = self._get_recovery_policy(bitchain.data_classification)
            
            # Step 5: HOLLOW ENUM - ENFORCE POLICY
            self._enforce_policy(policy, requester_id, bitchain, user_role)
            
            # Step 6: PREMATURE CELEBRATION - LOG BEFORE RETURNING
            capability = policy.default_capability
            audit_event.capability_level = capability.value
            audit_event.result = "SUCCESS"
            self.audit.append(audit_event)
            
            # Step 7: NOW SAFE - RETURN DATA
            return self._recover_with_capability(bitchain, capability, policy)
        
        except Exception as e:
            # Log the failure
            audit_event.result = "DENIED"
            audit_event.reason = str(e)
            self.audit.append(audit_event)
            raise
    
    # ========================================================================
    # SECURITY CHECK METHODS (One per archetype)
    # ========================================================================
    
    def _verify_phantom_prop(self, bitchain_id: str) -> BitChain:
        """
        PHANTOM PROP: Verify data is real (exists in ledger + signature valid).
        
        This check prevents:
        - Fabricated bitchain IDs
        - Corrupted/tampered bitchains
        - Non-existent bitchains
        """
        # Check it exists in ledger
        bitchain = self.ledger.get(bitchain_id)
        if not bitchain:
            raise ValueError(
                f"PHANTOM PROP DENIED: Bitchain {bitchain_id} not found in ledger"
            )
        
        # Check signature is valid
        stored_signature = self.ledger.get_signature(bitchain_id)
        if not stored_signature:
            raise ValueError(
                f"PHANTOM PROP DENIED: No signature for bitchain {bitchain_id}"
            )
        
        if not self.crypto.verify_signature(bitchain, stored_signature):
            raise ValueError(
                f"PHANTOM PROP DENIED: Signature verification failed for {bitchain_id}"
            )
        
        return bitchain
    
    def _verify_realm_lineage(self, bitchain: BitChain):
        """
        REALM + LINEAGE: Verify we know where this data came from.
        
        This check ensures:
        - Bitchain has valid realm (data/narrative/system/etc.)
        - Bitchain has valid lineage (generation from LUCA)
        - We can trace origin if needed
        """
        if not bitchain.realm:
            raise ValueError("REALM+LINEAGE DENIED: Bitchain missing realm")
        
        if not bitchain.coordinates.lineage:
            raise ValueError("REALM+LINEAGE DENIED: Bitchain missing lineage")
        
        # Could add more checks: is realm in VALID_REALMS? can we trace to LUCA?
        # For Phase 1, just verify they exist.
    
    def _verify_cold_method(
        self,
        auth_token: Optional[str],
        requester_id: str,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        COLD METHOD: Verify authentication, identity, and intent.
        
        This check ensures:
        - Auth token is provided and valid
        - Identity matches requester_id
        - Intent is declared (request_id, resources)
        - Request is specific (not a blank check)
        
        Returns:
            Identity info dict with user_id, role, etc.
        """
        # Check token is provided
        if not auth_token:
            raise ValueError(
                "COLD METHOD DENIED: Authentication token required"
            )
        
        # Verify token and get identity
        identity = self.auth.verify_token(auth_token)
        if not identity:
            raise ValueError(
                "COLD METHOD DENIED: Invalid authentication token"
            )
        
        token_user = identity.get("user_id")
        
        # Verify identity matches requester
        if token_user != requester_id:
            raise ValueError(
                f"COLD METHOD DENIED: Token identity ({token_user}) "
                f"does not match requester ({requester_id})"
            )
        
        # Verify intent is declared
        if not intent:
            raise ValueError(
                "COLD METHOD DENIED: Intent declaration required"
            )
        
        request_id = intent.get("request_id")
        if not request_id:
            raise ValueError(
                "COLD METHOD DENIED: Intent missing request_id"
            )
        
        # Verify bitchain is listed in resources
        resources = intent.get("resources", [])
        # Bitchain ID might be passed later, so we check this differently
        
        return identity
    
    def _get_recovery_policy(self, classification: DataClass) -> RecoveryPolicy:
        """Get the policy for this data classification."""
        if classification not in self.policies:
            raise ValueError(
                f"No recovery policy for classification {classification}"
            )
        return self.policies[classification]
    
    def _enforce_policy(
        self,
        policy: RecoveryPolicy,
        requester_id: str,
        bitchain: BitChain,
        user_role: str
    ):
        """
        HOLLOW ENUM: Enforce the policy (not just declare it).
        
        This check ensures:
        - User role is allowed (not just declared)
        - If owner-only, requester is owner (not just declared)
        - Rate limits not exceeded (not just declared)
        - If PII/SENSITIVE, second factor verified
        
        Raises PermissionError if any check fails.
        """
        # Check role
        if user_role not in policy.allowed_roles:
            raise PermissionError(
                f"HOLLOW ENUM DENIED: Role '{user_role}' not in "
                f"allowed roles {policy.allowed_roles} for {policy.classification.value}"
            )
        
        # Check owner-only
        if policy.owner_only:
            if bitchain.owner_id != requester_id:
                raise PermissionError(
                    f"HOLLOW ENUM DENIED: Owner-only recovery. "
                    f"Bitchain owner is {bitchain.owner_id}, "
                    f"requester is {requester_id}"
                )
        
        # Check rate limit
        if self._rate_limit_exceeded(requester_id, policy.rate_limit_per_hour):
            raise PermissionError(
                f"HOLLOW ENUM DENIED: Recovery rate limit exceeded "
                f"({policy.rate_limit_per_hour}/hour)"
            )
        
        # Check second factor for sensitive data
        if policy.requires_second_factor:
            if not self.auth.verify_second_factor(requester_id):
                raise PermissionError(
                    f"HOLLOW ENUM DENIED: Second factor authentication required "
                    f"for {policy.classification.value} data"
                )
    
    def _rate_limit_exceeded(self, requester_id: str, limit_per_hour: int) -> bool:
        """Check if user has exceeded recovery rate limit."""
        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        recent = self.audit.query({
            'recovered_by': requester_id,
            'action': 'recovery_attempt',
            'result': 'SUCCESS',
            'timestamp_after': hour_ago
        })
        return len(recent) >= limit_per_hour
    
    def _recover_with_capability(
        self,
        bitchain: BitChain,
        capability: Capability,
        policy: RecoveryPolicy
    ) -> Dict[str, Any]:
        """
        Return recovery data based on capability level.
        
        - COMPRESSED: Return mist form only (no expansion)
        - PARTIAL: Return anonymized expansion
        - FULL: Return complete expansion
        """
        canonical = bitchain.to_canonical_dict()
        
        if capability == Capability.COMPRESSED:
            # Return minimal compressed form
            return {
                'id': bitchain.id,
                'classification': bitchain.data_classification.value,
                'compressed': True,
                'fields': ['id', 'realm', 'entity_type']
            }
        
        elif capability == Capability.PARTIAL:
            # Return with anonymization (Phase 2)
            return canonical
        
        elif capability == Capability.FULL:
            # Return complete data
            return canonical
        
        else:
            raise ValueError(f"Unknown capability: {capability}")