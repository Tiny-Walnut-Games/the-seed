"""
Phase 1 Security Tests: Recovery Gate Implementation

Tests all four Story Test archetypes:
- PHANTOM PROP: Verify data is real
- COLD METHOD: Verify authentication
- HOLLOW ENUM: Verify policy enforcement
- PREMATURE CELEBRATION: Verify audit logging

Plus:
- Eagle-Eye attack scenario
- Rate limiting
- Integrity checks

Status: Phase 1 validation
"""

import sys
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

# Add seed/engine to path
sys.path.insert(0, 'E:/Tiny_Walnut_Games/the-seed/seed/engine')

from stat7_experiments import (
    BitChain, Coordinates, DataClass, Capability, generate_random_bitchain
)
from recovery_gate import (
    RecoveryGate,
    AuditEvent,
    RecoveryPolicy,
    InMemoryLedger,
    InMemoryAuditLedger,
    SimpleAuthService,
    SimpleCryptoService,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def crypto_service():
    """Create a crypto service."""
    return SimpleCryptoService(key=b"test-key-123")


@pytest.fixture
def auth_service():
    """Create an auth service with test tokens."""
    auth = SimpleAuthService()
    
    # Register test tokens
    # alice: owner (for PII/SENSITIVE tests), user (for PUBLIC tests)
    auth.register_token("valid-token-alice", "alice", role="owner")
    auth.register_token("valid-token-bob", "bob", role="admin")
    auth.register_token("valid-token-viewer", "viewer", role="viewer")
    
    return auth


@pytest.fixture
def ledger():
    """Create an in-memory ledger."""
    return InMemoryLedger()


@pytest.fixture
def audit_ledger():
    """Create an audit ledger."""
    return InMemoryAuditLedger(signing_key=b"audit-key-123")


@pytest.fixture
def recovery_gate(ledger, auth_service, audit_ledger, crypto_service):
    """Create a recovery gate with all services."""
    return RecoveryGate(
        ledger=ledger,
        auth_service=auth_service,
        audit_ledger=audit_ledger,
        crypto_service=crypto_service,
    )


@pytest.fixture
def sample_public_bitchain():
    """Create a sample PUBLIC bitchain."""
    bc = generate_random_bitchain()
    bc.data_classification = DataClass.PUBLIC
    bc.owner_id = "alice"
    return bc


@pytest.fixture
def sample_sensitive_bitchain():
    """Create a sample SENSITIVE bitchain."""
    bc = generate_random_bitchain()
    bc.data_classification = DataClass.SENSITIVE
    bc.owner_id = "alice"
    bc.access_control_list = ["owner", "admin"]
    return bc


@pytest.fixture
def sample_pii_bitchain():
    """Create a sample PII bitchain."""
    bc = generate_random_bitchain()
    bc.data_classification = DataClass.PII
    bc.owner_id = "alice"
    bc.access_control_list = ["owner"]
    return bc


# ============================================================================
# TESTS: PHANTOM PROP ARCHETYPE
# ============================================================================

class TestPhantomProp:
    """Test PHANTOM PROP: Verify data is real (not fabricated)."""
    
    def test_phantom_prop_bitchain_not_found(self, recovery_gate):
        """Should deny recovery if bitchain doesn't exist in ledger."""
        with pytest.raises(ValueError, match="not found in ledger"):
            recovery_gate.recover_bitchain(
                bitchain_id="non-existent-id",
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': ['bc-1']}
            )
    
    def test_phantom_prop_missing_signature(self, recovery_gate, sample_public_bitchain):
        """Should deny if bitchain has no signature in ledger."""
        # Store bitchain WITHOUT signature
        recovery_gate.ledger.bitchains[sample_public_bitchain.id] = sample_public_bitchain
        # Don't store signature
        
        with pytest.raises(ValueError, match="No signature"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
            )
    
    def test_phantom_prop_invalid_signature(self, recovery_gate, sample_public_bitchain):
        """Should deny if signature doesn't match."""
        # Store bitchain with WRONG signature
        recovery_gate.ledger.store(
            sample_public_bitchain,
            signature="wrong-signature-12345"
        )
        
        with pytest.raises(ValueError, match="Signature verification failed"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
            )
    
    def test_phantom_prop_valid_bitchain(self, recovery_gate, crypto_service, sample_public_bitchain):
        """Should accept valid bitchain with correct signature."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        # Should pass phantom prop check and fail later on auth
        # (We're testing phantom prop in isolation)
        result = recovery_gate._verify_phantom_prop(sample_public_bitchain.id)
        assert result.id == sample_public_bitchain.id


# ============================================================================
# TESTS: COLD METHOD ARCHETYPE
# ============================================================================

class TestColdMethod:
    """Test COLD METHOD: Verify authentication and identity."""
    
    def test_cold_method_no_auth_token(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should deny recovery without auth token."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        with pytest.raises(ValueError, match="Authentication token required"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token=None,
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
            )
    
    def test_cold_method_invalid_token(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should deny recovery with invalid auth token."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        with pytest.raises(ValueError, match="Invalid.*token"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="fake-token",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
            )
    
    def test_cold_method_identity_mismatch(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should deny if token identity doesn't match requester_id."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        # Token is for "alice", but requester_id is "bob"
        with pytest.raises(ValueError, match="does not match"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="bob",  # MISMATCH
                intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
            )
    
    def test_cold_method_no_intent(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should deny if intent is not declared."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        with pytest.raises(ValueError, match="Intent declaration required"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent=None  # NO INTENT
            )
    
    def test_cold_method_intent_missing_request_id(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should deny if intent has no request_id."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        with pytest.raises(ValueError, match="request_id"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_public_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'resources': [sample_public_bitchain.id]}  # NO request_id
            )


# ============================================================================
# TESTS: HOLLOW ENUM ARCHETYPE
# ============================================================================

class TestHollowEnum:
    """Test HOLLOW ENUM: Verify policy is enforced (not just declared)."""
    
    def test_hollow_enum_role_denied(self, recovery_gate, sample_sensitive_bitchain, crypto_service):
        """Should deny if user role not in allowed roles."""
        signature = crypto_service.sign_bitchain(sample_sensitive_bitchain)
        recovery_gate.ledger.store(sample_sensitive_bitchain, signature)
        
        # "viewer" is not allowed for SENSITIVE data
        with pytest.raises(PermissionError, match="HOLLOW ENUM DENIED"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_sensitive_bitchain.id,
                auth_token="valid-token-viewer",  # viewer role
                requester_id="viewer",
                intent={'request_id': 'req-1', 'resources': [sample_sensitive_bitchain.id]}
            )
    
    def test_hollow_enum_owner_only_denied(self, recovery_gate, sample_pii_bitchain, crypto_service):
        """Should deny if owner-only but requester is not owner."""
        signature = crypto_service.sign_bitchain(sample_pii_bitchain)
        recovery_gate.ledger.store(sample_pii_bitchain, signature)
        
        # bob is trying to recover, but alice is owner
        with pytest.raises(PermissionError, match="HOLLOW ENUM DENIED"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_pii_bitchain.id,
                auth_token="valid-token-bob",  # bob (admin)
                requester_id="bob",
                intent={'request_id': 'req-1', 'resources': [sample_pii_bitchain.id]}
            )
    
    def test_hollow_enum_second_factor_required(self, recovery_gate, sample_pii_bitchain, crypto_service):
        """Should deny PII recovery if second factor not verified."""
        signature = crypto_service.sign_bitchain(sample_pii_bitchain)
        recovery_gate.ledger.store(sample_pii_bitchain, signature)
        
        # alice has valid token but 2FA not verified
        with pytest.raises(PermissionError, match="Second factor"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_pii_bitchain.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_pii_bitchain.id]}
            )
    
    def test_hollow_enum_second_factor_verified(self, recovery_gate, sample_pii_bitchain, crypto_service):
        """Should allow PII recovery if second factor is verified."""
        signature = crypto_service.sign_bitchain(sample_pii_bitchain)
        recovery_gate.ledger.store(sample_pii_bitchain, signature)
        
        # Verify second factor for alice
        recovery_gate.auth.set_second_factor_verified("alice")
        
        # Now should succeed (until we hit rate limit or other checks)
        result = recovery_gate.recover_bitchain(
            bitchain_id=sample_pii_bitchain.id,
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [sample_pii_bitchain.id]}
        )
        assert result is not None
    
    def test_hollow_enum_rate_limit_exceeded(self, recovery_gate, sample_sensitive_bitchain, crypto_service):
        """Should deny if recovery rate limit exceeded."""
        signature = crypto_service.sign_bitchain(sample_sensitive_bitchain)
        recovery_gate.ledger.store(sample_sensitive_bitchain, signature)
        
        # Pre-fill audit log with many recoveries
        now = datetime.now(timezone.utc)
        for i in range(11):  # 11 recoveries (policy limit is 10/hour)
            event = AuditEvent(
                action="recovery_attempt",
                bitchain_id=f"bc-{i}",
                recovered_by="bob",
                timestamp=now.isoformat(),
                classification="SENSITIVE",
                capability_level="partial",
                result="SUCCESS",
            )
            recovery_gate.audit.append(event)
        
        # Now bob should be rate-limited
        with pytest.raises(PermissionError, match="rate limit exceeded"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_sensitive_bitchain.id,
                auth_token="valid-token-bob",
                requester_id="bob",
                intent={'request_id': 'req-1', 'resources': [sample_sensitive_bitchain.id]}
            )


# ============================================================================
# TESTS: PREMATURE CELEBRATION ARCHETYPE
# ============================================================================

class TestPrematureCelebration:
    """Test PREMATURE CELEBRATION: Verify audit is logged BEFORE data returned."""
    
    def test_premature_celebration_audit_logged_on_success(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Should log audit event on successful recovery."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        initial_audit_count = len(recovery_gate.audit.events)
        
        result = recovery_gate.recover_bitchain(
            bitchain_id=sample_public_bitchain.id,
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
        )
        
        # Audit should be logged
        assert len(recovery_gate.audit.events) == initial_audit_count + 1
        
        # Last audit event should be SUCCESS
        last_event = recovery_gate.audit.events[-1]
        assert last_event.result == "SUCCESS"
        assert last_event.recovered_by == "alice"
        assert last_event.bitchain_id == sample_public_bitchain.id
    
    def test_premature_celebration_audit_logged_on_denial(self, recovery_gate, sample_pii_bitchain, crypto_service):
        """Should log audit event even when recovery is denied."""
        signature = crypto_service.sign_bitchain(sample_pii_bitchain)
        recovery_gate.ledger.store(sample_pii_bitchain, signature)
        
        # Make sure bob (who doesn't own the bitchain) tries to recover
        sample_pii_bitchain.owner_id = "alice"  # Different owner
        signature = crypto_service.sign_bitchain(sample_pii_bitchain)
        recovery_gate.ledger.store(sample_pii_bitchain, signature)
        
        initial_audit_count = len(recovery_gate.audit.events)
        
        # Try to recover as non-owner (should fail owner-only check)
        try:
            recovery_gate.recover_bitchain(
                bitchain_id=sample_pii_bitchain.id,
                auth_token="valid-token-bob",  # bob is not owner
                requester_id="bob",
                intent={'request_id': 'req-1', 'resources': [sample_pii_bitchain.id]}
            )
        except PermissionError:
            pass  # Expected
        
        # Audit should still be logged
        assert len(recovery_gate.audit.events) == initial_audit_count + 1
        
        # Event should show DENIED
        last_event = recovery_gate.audit.events[-1]
        assert last_event.result == "DENIED"
        assert "owner" in last_event.reason.lower() or "denied" in last_event.reason.lower()
    
    def test_premature_celebration_audit_immutable(self, recovery_gate, sample_public_bitchain, crypto_service):
        """Audit log should be immutable (signatures verify)."""
        signature = crypto_service.sign_bitchain(sample_public_bitchain)
        recovery_gate.ledger.store(sample_public_bitchain, signature)
        
        result = recovery_gate.recover_bitchain(
            bitchain_id=sample_public_bitchain.id,
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [sample_public_bitchain.id]}
        )
        
        # Verify audit log integrity
        assert recovery_gate.audit.verify_integrity()


# ============================================================================
# EAGLE-EYE ATTACK SCENARIO
# ============================================================================

class TestEagleEyeAttack:
    """Test the Eagle-Eye identity recovery attack from EXP-05-SECURITY-ASSESSMENT.md"""
    
    def test_eagle_eye_attack_direct_recovery_denied(self, recovery_gate, crypto_service):
        """Eagle-Eye attack: Try to recover PII bitchain without auth."""
        # Create a bitchain with GitHub handle and achievement history
        sarah_badge = BitChain(
            id="sarah-badge-001",
            entity_type="badge",
            realm="pattern",
            coordinates=Coordinates(
                realm="pattern",
                lineage=42,
                adjacency=["github-001", "achievement-001"],
                horizon="peak",
                resonance=0.8,
                velocity=0.5,
                density=0.3,
            ),
            created_at=datetime.now(timezone.utc).isoformat(),
            state={
                'github_handle': 'sarah-dev',
                'achievement_history': ['Fixed critical auth bug', 'Reviewed 100+ PRs'],
                'skills': ['Security', 'Go', 'Python'],
            },
            data_classification=DataClass.PII,
            owner_id="sarah",
            access_control_list=["owner"],
        )
        
        signature = crypto_service.sign_bitchain(sarah_badge)
        recovery_gate.ledger.store(sarah_badge, signature)
        
        # Step 1: Attacker tries to recover WITHOUT token
        with pytest.raises(ValueError, match="token required"):
            recovery_gate.recover_bitchain(
                bitchain_id="sarah-badge-001",
                auth_token=None,
                requester_id="attacker",
                intent={'request_id': 'fake-req', 'resources': ['sarah-badge-001']}
            )
    
    def test_eagle_eye_attack_fake_token(self, recovery_gate, crypto_service):
        """Eagle-Eye attack: Try with fake token."""
        sarah_badge = BitChain(
            id="sarah-badge-001",
            entity_type="badge",
            realm="pattern",
            coordinates=Coordinates(
                realm="pattern",
                lineage=42,
                adjacency=["github-001"],
                horizon="peak",
                resonance=0.8,
                velocity=0.5,
                density=0.3,
            ),
            created_at=datetime.now(timezone.utc).isoformat(),
            state={'github_handle': 'sarah-dev'},
            data_classification=DataClass.PII,
            owner_id="sarah",
        )
        
        signature = crypto_service.sign_bitchain(sarah_badge)
        recovery_gate.ledger.store(sarah_badge, signature)
        
        # Step 2: Attacker tries with fake token
        with pytest.raises(ValueError, match="Invalid.*token"):
            recovery_gate.recover_bitchain(
                bitchain_id="sarah-badge-001",
                auth_token="totally-fake-token",
                requester_id="attacker",
                intent={'request_id': 'fake-req', 'resources': ['sarah-badge-001']}
            )
        
        # Step 3: Attack is logged
        denial_event = recovery_gate.audit.events[-1]
        assert denial_event.result == "DENIED"
        assert denial_event.action == "recovery_attempt"
    
    def test_eagle_eye_attack_bulk_extraction_denied(self, recovery_gate, crypto_service):
        """Eagle-Eye attack: Try bulk extraction (multiple recoveries)."""
        # Create 15 bitchains
        bitchains = []
        for i in range(15):
            bc = BitChain(
                id=f"badge-{i}",
                entity_type="badge",
                realm="pattern",
                coordinates=Coordinates(
                    realm="pattern",
                    lineage=i+1,  # Must be > 0
                    adjacency=[],
                    horizon="peak",
                    resonance=0.5,
                    velocity=0.5,
                    density=0.5,
                ),
                created_at=datetime.now(timezone.utc).isoformat(),
                state={'github_handle': f'user-{i}'},
                data_classification=DataClass.SENSITIVE,
                owner_id="admin",  # Attacker got admin creds
            )
            signature = crypto_service.sign_bitchain(bc)
            recovery_gate.ledger.store(bc, signature)
            bitchains.append(bc)
        
        recovery_gate.auth.register_token("admin-token", "admin", role="admin")
        
        # Try to recover all 15
        recovered_count = 0
        for i in range(15):
            try:
                result = recovery_gate.recover_bitchain(
                    bitchain_id=f"badge-{i}",
                    auth_token="admin-token",
                    requester_id="admin",
                    intent={'request_id': f'req-{i}', 'resources': [f'badge-{i}']}
                )
                recovered_count += 1
            except PermissionError as e:
                if "rate limit" in str(e):
                    # Good! Rate limit kicked in
                    break
        
        # Should hit rate limit before recovering all
        assert recovered_count < 15
        
        # Last attempt should be logged as DENIED
        last_event = recovery_gate.audit.events[-1]
        assert last_event.result == "DENIED"
        assert "rate limit" in last_event.reason.lower()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete recovery flow."""
    
    def test_successful_public_recovery(self, recovery_gate, crypto_service):
        """Complete flow: Successfully recover PUBLIC bitchain."""
        bc = generate_random_bitchain()
        bc.data_classification = DataClass.PUBLIC
        bc.owner_id = "alice"
        
        signature = crypto_service.sign_bitchain(bc)
        recovery_gate.ledger.store(bc, signature)
        
        result = recovery_gate.recover_bitchain(
            bitchain_id=bc.id,
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [bc.id]}
        )
        
        assert result is not None
        assert 'id' in result or 'entity_type' in result
    
    def test_successful_sensitive_recovery(self, recovery_gate, crypto_service):
        """Complete flow: Successfully recover SENSITIVE bitchain with admin role."""
        bc = generate_random_bitchain()
        bc.data_classification = DataClass.SENSITIVE
        bc.owner_id = "alice"
        
        signature = crypto_service.sign_bitchain(bc)
        recovery_gate.ledger.store(bc, signature)
        
        result = recovery_gate.recover_bitchain(
            bitchain_id=bc.id,
            auth_token="valid-token-bob",  # bob is admin
            requester_id="bob",
            intent={'request_id': 'req-1', 'resources': [bc.id]}
        )
        
        assert result is not None
    
    def test_audit_trail_complete(self, recovery_gate, crypto_service):
        """Verify complete audit trail for multiple operations."""
        # Create 3 bitchains
        bcs = [generate_random_bitchain() for _ in range(3)]
        for i, bc in enumerate(bcs):
            bc.data_classification = DataClass.PUBLIC
            bc.owner_id = "alice"
            signature = crypto_service.sign_bitchain(bc)
            recovery_gate.ledger.store(bc, signature)
        
        # Recover all 3
        for bc in bcs:
            recovery_gate.recover_bitchain(
                bitchain_id=bc.id,
                auth_token="valid-token-alice",
                requester_id="alice",
                intent={'request_id': f'req-{bc.id}', 'resources': [bc.id]}
            )
        
        # Verify audit trail
        events = recovery_gate.audit.query({'recovered_by': 'alice', 'result': 'SUCCESS'})
        assert len(events) == 3
        assert all(e.result == "SUCCESS" for e in events)
        assert all(e.recovered_by == "alice" for e in events)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])