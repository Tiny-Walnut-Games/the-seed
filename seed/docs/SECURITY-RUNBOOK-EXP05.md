# 🔐 Security Runbook: EXP-05 Recovery Gate Implementation

> **Quick reference for implementing security checks on Seed compression recovery operations.**
>
> **Status:** Pre-Production Implementation Plan  
> **Severity:** HIGH (PII/Badge data at risk if not implemented)  
> **Estimated Effort:** Phase 1 = ~16 hours | Phase 2 = ~40 hours | Phase 3 = ~24 hours

---

## Quick Start: What You Need to Do

### 🚨 Phase 1: This Week (CRITICAL BEFORE ANY PRODUCTION USE)

**If you're using Seed to compress badge/pet data, do Phase 1 THIS WEEK or don't ship.**

| Task | Time | Impact | Done |
|------|------|--------|------|
| Add `data_classification` field to BitChain | 30 min | Enables policy tagging | ☐ |
| Implement `RecoveryGate` class skeleton | 1 hr | Sets up enforcement framework | ☐ |
| Add auth token verification (COLD METHOD) | 1.5 hr | Blocks unauthenticated access | ☐ |
| Implement ACL checking (HOLLOW ENUM) | 1.5 hr | Enforces owner/role policies | ☐ |
| Add audit logging (PREMATURE CELEBRATION) | 2 hr | Creates immutable trail | ☐ |
| Add ledger verification (PHANTOM PROP) | 1 hr | Prevents fabricated recoveries | ☐ |
| Write tests for all four archetypes | 6 hr | Validates implementation | ☐ |
| **Phase 1 Total** | **~13.5 hr** | **Fort with locked door** | ☐ |

### 📈 Phase 2: Next Two Weeks (BEFORE SCALING TO PRODUCTION)

| Task | Time | Impact | Done |
|------|------|--------|------|
| Rate limiting on recovery operations | 2 hr | Prevents bulk extraction | ☐ |
| Selective anonymization logic | 2 hr | Hides identity from partial reads | ☐ |
| Second factor for SENSITIVE/PII (2FA) | 3 hr | Extra protection for critical data | ☐ |
| Encryption option for sensitive data | 4 hr | Data protection at rest | ☐ |
| Security audit: run Eagle-Eye attack | 2 hr | Validates that fixes work | ☐ |
| Integration test: badges + recovery | 3 hr | End-to-end validation | ☐ |
| **Phase 2 Total** | **~16 hr** | **Fortress fully secured** | ☐ |

### 🎯 Phase 3: This Month (OPTIONAL BUT RECOMMENDED)

| Task | Time | Impact | Done |
|------|------|--------|------|
| Differential privacy on embeddings | 5 hr | Adds noise to sensitive data | ☐ |
| Zero-knowledge recovery proofs | 8 hr | Prove access without exposing data | ☐ |
| GDPR/CCPA compliance audit | 4 hr | Legal/regulatory validation | ☐ |
| Penetration testing by external firm | 7 hr | Third-party validation | ☐ |
| **Phase 3 Total** | **~24 hr** | **Production-ready hardened system** | ☐ |

---

## Phase 1: The Locked Door (This Week)

### Step 1.1: Add Data Classification to BitChain

**File:** `seed/engine/exp05_compression_expansion.py`

**Change:**
```python
from enum import Enum

class DataClass(Enum):
    PUBLIC = "PUBLIC"           # Anyone can read
    SENSITIVE = "SENSITIVE"     # Authenticated users, role-based
    PII = "PII"                 # Owner-only, requires 2FA

@dataclass
class BitChain:
    # ... existing fields ...
    
    # ADD THESE:
    data_classification: DataClass = DataClass.PUBLIC
    access_control_list: list = None  # ["owner", "org:admin"]
    encryption_key_id: str = None     # For encrypted data
```

**Test:**
```python
def test_bitchain_classification():
    # PUBLIC: no special handling
    bc_public = BitChain(data_classification=DataClass.PUBLIC)
    assert bc_public.data_classification == DataClass.PUBLIC
    
    # SENSITIVE: needs auth + policy
    bc_sensitive = BitChain(
        data_classification=DataClass.SENSITIVE,
        access_control_list=["owner", "admin"]
    )
    assert "owner" in bc_sensitive.access_control_list
    
    # PII: needs strongest protection
    bc_pii = BitChain(
        data_classification=DataClass.PII,
        access_control_list=["owner"]
    )
    assert bc_pii.access_control_list == ["owner"]
```

---

### Step 1.2: Create RecoveryGate Class

**File:** `seed/engine/recovery_gate.py` (NEW FILE)

**Implementation:**
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

class Capability(Enum):
    COMPRESSED = "compressed"  # Read-only mist form
    PARTIAL = "partial"        # Anonymized expansion
    FULL = "full"              # Complete recovery

@dataclass
class AuditEvent:
    action: str
    bitchain_id: str
    recovered_by: str
    timestamp: str
    classification: str
    capability_level: str
    result: str  # SUCCESS, DENIED, FAILED
    reason: str = ""

class RecoveryGate:
    """
    Secure recovery operations using Story Test archetypes:
    - PHANTOM PROP: Verify data is real
    - REALM + LINEAGE: Verify origin
    - COLD METHOD: Verify authentication
    - ENVIRONMENT: Verify policy
    - HOLLOW ENUM: Enforce it
    - PREMATURE CELEBRATION: Audit first
    """
    
    def __init__(self, ledger, auth_service, audit_ledger, crypto_service):
        self.ledger = ledger
        self.auth = auth_service
        self.audit = audit_ledger
        self.crypto = crypto_service
        self.policies = {}  # Will be populated per data class
    
    def recover_bitchain(
        self,
        bitchain_id: str,
        auth_token: str,
        requester_id: str,
        intent: Dict
    ) -> Optional[dict]:
        """
        Recover a bitchain only if ALL security checks pass.
        Fail-safe: any check fails → entire operation fails.
        Audit: logged BEFORE data is returned.
        """
        
        audit_event = AuditEvent(
            action="recovery_attempt",
            bitchain_id=bitchain_id,
            recovered_by=requester_id,
            timestamp=datetime.utcnow().isoformat(),
            classification="unknown",
            capability_level="none",
            result="PENDING"
        )
        
        try:
            # 1. PHANTOM PROP CHECK: Is this real?
            bitchain = self._verify_phantom_prop(bitchain_id)
            audit_event.classification = bitchain.data_classification.value
            
            # 2. REALM + LINEAGE: Do we know where this came from?
            self._verify_realm_lineage(bitchain)
            
            # 3. COLD METHOD: Is the requester real and authorized?
            identity = self._verify_cold_method(auth_token, requester_id, intent)
            
            # 4. ENVIRONMENT: What policy applies?
            policy = self._get_recovery_policy(bitchain.data_classification)
            
            # 5. HOLLOW ENUM: Enforce the policy
            self._enforce_policy(policy, requester_id, bitchain)
            
            # 6. PREMATURE CELEBRATION: Log BEFORE returning data
            capability = policy.default_capability
            audit_event.capability_level = capability.value
            audit_event.result = "SUCCESS"
            self._append_audit_immutable(audit_event)
            
            # 7. NOW safe to return
            return self._recover_with_capability(bitchain, capability, policy)
            
        except Exception as e:
            # Log the rejection
            audit_event.result = "DENIED"
            audit_event.reason = str(e)
            self._append_audit_immutable(audit_event)
            raise
    
    def _verify_phantom_prop(self, bitchain_id: str) -> dict:
        """PHANTOM PROP: Verify data exists and is intact."""
        # Check ledger
        bitchain = self.ledger.get(bitchain_id)
        if not bitchain:
            raise ValueError(f"Bitchain {bitchain_id} not found in ledger")
        
        # Check signature
        if not self.crypto.verify_signature(bitchain):
            raise ValueError(f"Signature verification failed for {bitchain_id}")
        
        return bitchain
    
    def _verify_realm_lineage(self, bitchain: dict):
        """REALM + LINEAGE: Verify origin is trusted."""
        if not bitchain.get('realm'):
            raise ValueError("Bitchain missing realm")
        if not bitchain.get('lineage'):
            raise ValueError("Bitchain missing lineage")
        # Could add checks: is realm valid? can we trace lineage to LUCA?
    
    def _verify_cold_method(self, auth_token: str, requester_id: str, 
                           intent: Dict) -> str:
        """COLD METHOD: Verify authentication and intent."""
        # Verify token
        if not auth_token:
            raise ValueError("Authentication token required")
        
        identity = self.auth.verify_token(auth_token)
        if not identity:
            raise ValueError("Invalid authentication token")
        
        # Verify identity matches requester
        if identity != requester_id:
            raise ValueError(f"Token identity mismatch: {identity} vs {requester_id}")
        
        # Verify intent declaration
        if not intent.get('request_id'):
            raise ValueError("Intent declaration required (request_id missing)")
        
        if bitchain_id not in intent.get('resources', []):
            raise ValueError(f"Bitchain not listed in intent resources")
        
        return identity
    
    def _get_recovery_policy(self, classification: 'DataClass') -> 'RecoveryPolicy':
        """Get the policy for this data classification."""
        if classification not in self.policies:
            raise ValueError(f"No recovery policy for {classification}")
        return self.policies[classification]
    
    def _enforce_policy(self, policy: 'RecoveryPolicy', requester_id: str, 
                       bitchain: dict):
        """HOLLOW ENUM: Enforce the policy (don't just declare it)."""
        # Check roles/ACL
        if requester_id not in policy.allowed_roles:
            raise PermissionError(
                f"Role not in {policy.allowed_roles} for {policy.classification}"
            )
        
        # Check if owner-only
        if policy.owner_only:
            if bitchain.get('owner_id') != requester_id:
                raise PermissionError("Owner-only recovery: not owner")
        
        # Check rate limit
        if self._rate_limit_exceeded(requester_id):
            raise PermissionError("Recovery rate limit exceeded")
        
        # For PII/SENSITIVE: require second factor
        if policy.requires_second_factor:
            if not self.auth.verify_second_factor(requester_id):
                raise PermissionError("Second factor authentication required")
    
    def _rate_limit_exceeded(self, requester_id: str) -> bool:
        """Check if user has exceeded recovery rate limit."""
        # Implementation: query audit log for recent recoveries
        # If > X in last hour, return True
        hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        recent = self.audit.query({
            'recovered_by': requester_id,
            'action': 'recovery_attempt',
            'result': 'SUCCESS',
            'timestamp_after': hour_ago
        })
        return len(recent) > 10  # 10 recoveries per hour limit
    
    def _append_audit_immutable(self, event: AuditEvent):
        """PREMATURE CELEBRATION: Sign and commit audit before returning data."""
        signed = self.crypto.sign(event.__dict__)
        self.audit.append(signed)  # This must succeed or recovery fails
    
    def _recover_with_capability(self, bitchain: dict, capability: Capability,
                                 policy: 'RecoveryPolicy') -> dict:
        """Return recovery based on capability level."""
        if capability == Capability.COMPRESSED:
            return bitchain  # Return mist form only
        elif capability == Capability.PARTIAL:
            return self._anonymize_bitchain(bitchain, policy.anonymization_rules)
        elif capability == Capability.FULL:
            return bitchain  # Return full expansion
```

---

### Step 1.3: Add Authentication Check

**File:** `seed/engine/recovery_gate.py` (update)

**Key method:** `_verify_cold_method()` (already above)

**Test:**
```python
def test_cold_method_auth_required():
    gate = RecoveryGate(ledger, auth_service, audit, crypto)
    
    # No token → denied
    with pytest.raises(ValueError, match="token required"):
        gate.recover_bitchain(
            "bc-123",
            auth_token=None,
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': ['bc-123']}
        )
    
    # Fake token → denied
    with pytest.raises(ValueError, match="Invalid token"):
        gate.recover_bitchain(
            "bc-123",
            auth_token="fake-token",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': ['bc-123']}
        )
    
    # Valid token → proceeds to next check
    # (would require full setup to test end-to-end)
```

---

### Step 1.4: Add ACL Checking

**File:** `seed/engine/recovery_gate.py` (update)

**Key method:** `_enforce_policy()` (already above)

**Test:**
```python
def test_hollow_enum_acl_enforced():
    gate = RecoveryGate(ledger, auth_service, audit, crypto)
    
    # Setup bitchain with owner-only policy
    policy = RecoveryPolicy(
        classification=DataClass.PII,
        allowed_roles=['owner'],
        owner_only=True
    )
    gate.policies[DataClass.PII] = policy
    
    bitchain = {'id': 'bc-123', 'owner_id': 'alice', 'classification': DataClass.PII}
    
    # Alice (owner) → OK
    gate._enforce_policy(policy, 'alice', bitchain)  # Should not raise
    
    # Bob (not owner) → denied
    with pytest.raises(PermissionError, match="not owner"):
        gate._enforce_policy(policy, 'bob', bitchain)
```

---

### Step 1.5: Add Audit Logging

**File:** `seed/engine/recovery_gate.py`

**Key method:** `_append_audit_immutable()` (already above)

**Test:**
```python
def test_premature_celebration_audit_before_data():
    gate = RecoveryGate(ledger, auth_service, audit, crypto)
    
    # Simulate: what gets logged before recovery?
    with mock.patch.object(gate.audit, 'append') as mock_append:
        with mock.patch.object(gate.crypto, 'sign', return_value={'signed': True}):
            try:
                gate.recover_bitchain(...)  # Will fail on auth
            except Exception:
                pass
            
            # Even on failure, audit.append was called
            assert mock_append.called
```

---

### Step 1.6: Full Integration Test

**File:** `tests/test_recovery_gate_phase1.py` (NEW FILE)

```python
import pytest
from datetime import datetime
from seed.engine.recovery_gate import RecoveryGate, DataClass, Capability

@pytest.fixture
def gate_with_policies():
    """Setup RecoveryGate with default policies."""
    ledger = MockLedger()
    auth = MockAuthService()
    audit = MockAuditLedger()
    crypto = MockCrypto()
    
    gate = RecoveryGate(ledger, auth, audit, crypto)
    
    # Setup policies
    gate.policies[DataClass.PUBLIC] = RecoveryPolicy(
        classification=DataClass.PUBLIC,
        allowed_roles=['anyone'],
        default_capability=Capability.COMPRESSED
    )
    
    gate.policies[DataClass.SENSITIVE] = RecoveryPolicy(
        classification=DataClass.SENSITIVE,
        allowed_roles=['owner', 'admin'],
        owner_only=True,
        default_capability=Capability.COMPRESSED,
        requires_second_factor=False
    )
    
    gate.policies[DataClass.PII] = RecoveryPolicy(
        classification=DataClass.PII,
        allowed_roles=['owner'],
        owner_only=True,
        default_capability=Capability.COMPRESSED,
        requires_second_factor=True,
        anonymization_rules={'identity': 'HASH'}
    )
    
    return gate, ledger, auth, audit, crypto

def test_phantom_prop_rejects_nonexistent(gate_with_policies):
    """PHANTOM PROP: Nonexistent bitchain rejected."""
    gate, ledger, _, _, _ = gate_with_policies
    
    with pytest.raises(ValueError, match="not found"):
        gate.recover_bitchain(
            "nonexistent-id",
            auth_token="valid",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': ['nonexistent-id']}
        )

def test_cold_method_rejects_no_auth(gate_with_policies):
    """COLD METHOD: No auth token rejected."""
    gate, _, _, _, _ = gate_with_policies
    
    with pytest.raises(ValueError, match="token required"):
        gate.recover_bitchain(
            "bc-123",
            auth_token=None,
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': ['bc-123']}
        )

def test_hollow_enum_enforces_acl(gate_with_policies):
    """HOLLOW ENUM: ACL policy is enforced."""
    gate, ledger, auth, _, _ = gate_with_policies
    
    # Create owner-only SENSITIVE bitchain
    auth.set_valid_token("bob_token", "bob")
    ledger.create({
        'id': 'bc-123',
        'owner_id': 'alice',
        'classification': DataClass.SENSITIVE,
        'compressed': True
    })
    
    # Alice (owner) can recover
    gate.recover_bitchain(
        "bc-123",
        auth_token="alice_token",
        requester_id="alice",
        intent={'request_id': 'req-1', 'resources': ['bc-123']}
    )
    
    # Bob (not owner) cannot
    with pytest.raises(PermissionError, match="not owner"):
        gate.recover_bitchain(
            "bc-123",
            auth_token="bob_token",
            requester_id="bob",
            intent={'request_id': 'req-1', 'resources': ['bc-123']}
        )

def test_premature_celebration_audit_logged(gate_with_policies):
    """PREMATURE CELEBRATION: Audit created before data returned."""
    gate, ledger, auth, audit, crypto = gate_with_policies
    
    # Success case
    auth.set_valid_token("valid", "alice")
    ledger.create({
        'id': 'bc-123',
        'owner_id': 'alice',
        'classification': DataClass.PUBLIC,
        'compressed': True
    })
    
    result = gate.recover_bitchain(
        "bc-123",
        auth_token="valid",
        requester_id="alice",
        intent={'request_id': 'req-1', 'resources': ['bc-123']}
    )
    
    # Audit logged with SUCCESS
    assert audit.last_event['result'] == 'SUCCESS'
    assert audit.last_event['recovered_by'] == 'alice'
    
    # Denial case
    auth.set_valid_token("bob_token", "bob")
    
    try:
        gate.recover_bitchain(
            "bc-123",
            auth_token="bob_token",
            requester_id="bob",
            intent={'request_id': 'req-1', 'resources': ['bc-123']}
        )
    except PermissionError:
        pass
    
    # Audit logged with DENIED
    assert audit.last_event['result'] == 'DENIED'
    assert audit.last_event['reason'] != ""
```

**Run tests:**
```bash
pytest tests/test_recovery_gate_phase1.py -v
```

If all Phase 1 tests pass: ✅ **Fort has locked door**

---

## Phase 2: Scale & Harden (Next Two Weeks)

### Step 2.1: Rate Limiting

**Update `recovery_gate.py`:**
```python
def _rate_limit_exceeded(self, requester_id: str) -> bool:
    """Prevent bulk extraction attacks."""
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = self.audit.query({
        'recovered_by': requester_id,
        'result': 'SUCCESS',
        'timestamp_after': hour_ago.isoformat()
    })
    
    LIMIT_PER_HOUR = 10
    if len(recent) >= LIMIT_PER_HOUR:
        # Alert security team
        self._alert_security_team(
            f"User {requester_id} exceeded recovery rate limit",
            severity="HIGH"
        )
        return True
    
    return False
```

### Step 2.2: Selective Anonymization

**Add to `recovery_gate.py`:**
```python
def _anonymize_bitchain(self, bitchain: dict, rules: dict) -> dict:
    """Anonymize fields per policy during partial recovery."""
    anon = dict(bitchain)
    
    for field, action in rules.items():
        if action == 'HASH':
            anon[field] = self.crypto.hash_field(anon.get(field, ''))
        elif action == 'OMIT':
            anon.pop(field, None)
        elif action == 'ANONYMIZE':
            anon[field] = f"[ANONYMIZED_{field.upper()}]"
    
    return anon
```

### Step 2.3: Second Factor Auth

**Add to `recovery_gate.py`:**
```python
def _enforce_policy(self, policy, requester_id, bitchain):
    """... existing code ..."""
    
    if policy.requires_second_factor:
        if not self.auth.verify_second_factor(requester_id):
            raise PermissionError("Second factor auth required")
```

### Step 2.4: Eagle-Eye Attack Test

**File:** `tests/test_eagle_eye_attack.py` (NEW FILE)

```python
def test_eagle_eye_attack_prevented():
    """
    Simulate the Eagle-Eye attack: intercept badge data and extract identity.
    Verify all defense layers work.
    """
    gate = RecoveryGate(ledger, auth, audit, crypto)
    
    # Setup: Sarah's badge (PII data)
    sarah_badge = {
        'id': 'badge-sarah-001',
        'owner_id': 'sarah',
        'github_handle': 'sarah-techcorp',  # PII
        'achievements': ['auth-bug-fix', 'perf-optimization'],
        'classification': DataClass.PII,
        'compressed': True
    }
    
    # Attacker 1: Try without auth (COLD METHOD defense)
    with pytest.raises(ValueError, match="token required"):
        gate.recover_bitchain(
            'badge-sarah-001',
            auth_token=None,
            requester_id='attacker',
            intent={'request_id': 'req-attack', 'resources': ['badge-sarah-001']}
        )
    
    # Attacker 2: Try with stolen token (HOLLOW ENUM defense)
    with pytest.raises(PermissionError, match="not owner"):
        gate.recover_bitchain(
            'badge-sarah-001',
            auth_token='sarah_token_stolen',
            requester_id='attacker',  # Owner check fails
            intent={'request_id': 'req-attack', 'resources': ['badge-sarah-001']}
        )
    
    # Attacker 3: Try bulk extraction (RATE LIMIT defense)
    for i in range(15):  # Try 15 times
        try:
            gate.recover_bitchain(
                f'badge-victim-{i:03d}',
                auth_token='some_valid_token',
                requester_id='attacker',
                intent={'request_id': f'req-{i}', 'resources': [f'badge-victim-{i:03d}']}
            )
        except PermissionError as e:
            # Should hit rate limit
            if "rate limit" in str(e):
                break
    else:
        pytest.fail("Rate limit not enforced after 15 attempts")
    
    # Sarah: Can recover her own (PREMATURE CELEBRATION + audit)
    result = gate.recover_bitchain(
        'badge-sarah-001',
        auth_token='sarah_token',
        requester_id='sarah',
        intent={'request_id': 'req-sarah-valid', 'resources': ['badge-sarah-001']}
    )
    
    # Should be anonymized (HOLLOW ENUM enforcement)
    assert result['github_handle'] != 'sarah-techcorp'  # Hashed
    assert 'timestamp' not in result  # Omitted
    
    # Audit shows Sarah's legitimate recovery
    assert audit.query({'recovered_by': 'sarah', 'result': 'SUCCESS'})
    
    # Audit shows attacker attempts
    attacks = audit.query({'recovered_by': 'attacker', 'result': 'DENIED'})
    assert len(attacks) >= 3  # At least 3 failed attempts logged
```

---

## Phase 3: Production Hardening (This Month)

### Differential Privacy
- Add noise to embeddings for SENSITIVE data
- Aggregate achievement counts instead of raw history

### Zero-Knowledge Proofs
- Prove user has >100 XP without revealing exact count
- Prove user fixed security bugs without revealing which ones

### GDPR/CCPA Audit
- Document all data collected in badges
- Map to GDPR/CCPA requirements
- Implement right-to-be-forgotten

### Penetration Testing
- Hire external firm to test Seed recovery gates
- Run full threat model against implementation
- Document findings and remediation

---

## Checklist Before Production

### Before Shipping Badge/Pet Data Through Seed

- [ ] Phase 1 complete: All four archetypes implemented
- [ ] Phase 1 tests passing: 100% pass rate
- [ ] Authentication required: No unauthenticated recovery
- [ ] ACL enforced: Policy checks in code, not docs
- [ ] Audit trail: Every recovery logged
- [ ] Rate limiting: Bulk extraction prevented
- [ ] Eagle-Eye test: Attack scenario fails
- [ ] Code review: Security team signs off
- [ ] Documentation: Team knows how to use it

### Before Scaling to Other Data

- [ ] Phase 2 complete: Rate limiting, 2FA, encryption working
- [ ] Differential privacy: Sensitive fields anonymized
- [ ] GDPR/CCPA: Compliance audit passed
- [ ] Penetration test: External firm cleared it
- [ ] Monitoring: Alerts set for suspicious patterns
- [ ] Runbook: On-call team knows incident response

---

## Quick Reference: The Four Archetypes

| Archetype | Failure | Prevention | Test |
|-----------|---------|-----------|------|
| **Phantom Prop** | Fabricated data accepted | Verify in ledger + signature | Reject fake ID |
| **Cold Method** | Unguarded recovery path | Auth required | Try without token |
| **Hollow Enum** | Policy listed but not enforced | Code checks policy before return | Role not in ACL → denied |
| **Premature Celebration** | Audit logged after data returned | Log BEFORE returning | Kill process mid-recovery |

---

## Key Files to Create/Update

```
seed/engine/
├── recovery_gate.py              (NEW)    - RecoveryGate class
├── exp05_compression_expansion.py (UPDATE) - Add DataClass field
└── policies.py                   (NEW)    - Recovery policies per classification

tests/
├── test_recovery_gate_phase1.py  (NEW)    - Phase 1 tests
├── test_eagle_eye_attack.py      (NEW)    - Attack scenario test
└── test_rate_limiting.py         (NEW)    - Phase 2 tests

seed/docs/
├── DOCTRINE-INTEGRITY-SECURITY-SCROLLS.md (CREATED)
├── EXP-05-SECURITY-ASSESSMENT.md           (UPDATED)
└── SECURITY-RUNBOOK-EXP05.md               (THIS FILE)
```

---

## Questions?

- **What's the timeline?** Phase 1 must be done before shipping badge data. Phase 2 within 2 weeks.
- **What if we skip security?** Badge data includes GitHub handles + achievement history. An attacker could extract complete dev profiles. Not optional.
- **How do we test this?** Run the Eagle-Eye test. If it fails (attacker denied), security works.
- **What's the impact on performance?** Phase 1 adds ~10ms to recovery (audit append + auth checks). Acceptable.

---

**Status:** Ready for implementation  
**Next:** Start with Step 1.1 (add classification field)  
**Questions:** See DOCTRINE-INTEGRITY-SECURITY-SCROLLS.md for pattern explanations