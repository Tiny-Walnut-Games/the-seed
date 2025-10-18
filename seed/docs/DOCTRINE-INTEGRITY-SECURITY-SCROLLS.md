# 📜 Doctrine Integrity: Security Through Story Test Archetypes

> **For Tiny Walnut Games Dev Team**  
> *How to catch security failures using the same patterns you use to debug Cheekdom*

---

## The Insight

You already have a mental model for catching bugs in **narrative integrity** (TheStoryTest). That same model catches **data integrity** and **security failures**. You don't need to learn a new language—just extend the one you already speak.

---

## The Four Archetypes of System Failure

### 🎭 Phantom Prop
**The Problem:** Data that looks real but isn't. It arrived in the scene, but it doesn't belong there.

**In Game Debugging:**
```
❌ BAD: NPC has reference to deleted item
✓ GOOD: Item exists in registry before NPC can reference it
```

**In Security:**
```
❌ BAD: Recovery operation processes bitchain without verifying it exists in ledger
✓ GOOD: Verify bitchain in ledger + check cryptographic signature before expansion

Phantom Prop Security Failure Example:
- Attacker fabricates a bitchain ID
- System tries to recover it
- No ledger check → System treats fabricated data as real
- Attacker extracts sensitive data from the false recovery

Prevention:
✓ Verify existence in append-only ledger
✓ Validate cryptographic signature
✓ Check provenance chain (can we trace to LUCA?)
✓ Fail closed if any check fails
```

**Test It:**
```python
# Try to recover non-existent bitchain
try:
    recovered = recover_bitchain("fake-id-12345", auth_token)
    assert False, "Should have raised"
except PermissionError as e:
    assert "not found" in str(e)
    # ✓ PASS: System rejected phantom prop
```

---

### ❄️ Cold Method
**The Problem:** A method works in isolation but ignores the environment. It's "cold"—not connected to context.

**In Game Debugging:**
```
❌ BAD: Method rotates character sprite without checking if character is animated
✓ GOOD: Method checks animation state first, then applies rotation
```

**In Security:**
```
❌ BAD: Recovery operation expands bitchain without checking authentication
✓ GOOD: Verify auth token + identity + intent BEFORE expansion

Cold Method Security Failure Example:
- Recovery gate exists but recovery operation bypasses it
- Code expands bitchain without calling authentication check
- Method is "cold"—doesn't know it's running in an unauthenticated context
- Any caller can invoke it, no auth required

Prevention:
✓ Auth token required (bearer, API key, user session)
✓ Identity verification (who is this really?)
✓ Intent declaration (why are you recovering this? what's the linked request?)
✓ Capability scoping (what level of access do you get?)
✓ All checks happen BEFORE data is returned
```

**Test It:**
```python
# Try to recover without auth token
try:
    recovered = recover_bitchain(bitchain_id, auth_token=None, requester_id)
    assert False, "Should have raised"
except AuthenticationError:
    # ✓ PASS: Cold method gate worked

# Try to recover with fake token
try:
    recovered = recover_bitchain(bitchain_id, auth_token="fake", requester_id)
    assert False, "Should have raised"
except AuthenticationError as e:
    # Check that this was logged for security alert
    assert audit.has_rejection("fake_token", bitchain_id)
    # ✓ PASS: Cold method caught bad context
```

---

### 🏮 Hollow Enum
**The Problem:** A policy is declared but never enforced. It looks strong but has no teeth.

**In Game Debugging:**
```
❌ BAD: enum Role { ADMIN, USER, GUEST }; but no check against it
✓ GOOD: if (role != Role.ADMIN) return Unauthorized
```

**In Security:**
```
❌ BAD: ACL says "owner-only recovery" but code doesn't check it
✓ GOOD: Enforce ACL in code, fail closed if check fails

Hollow Enum Security Failure Example:
- Recovery policy says: "Only owner can recover SENSITIVE data"
- Code creates the policy object
- Code never actually calls policy.can_recover(requester_id)
- Anyone can recover because policy is never enforced
- It's a beautiful enum on the spreadsheet but toothless in code

Prevention:
✓ Policy is enforced BEFORE expansion (not after)
✓ Enforcement throws exception if policy denied
✓ No "pass through" or "ignore" options
✓ Policy check is code, not just comment
✓ Every path through recovery gate checks policy
✓ Audit log shows which policy denied recovery (traceability)
```

**Test It:**
```python
# Try to recover with policy that should deny it
policy = RecoveryPolicy(
    classification=DataClass.SENSITIVE,
    allowed_roles=['owner']
)
audit_mock = MagicMock()

try:
    # requester_id is NOT owner
    recovered = recover_bitchain(
        bitchain_id,
        auth_token=valid_token,
        requester_id="not-the-owner",
        policy=policy,
        audit=audit_mock
    )
    assert False, "Should have raised"
except PermissionError as e:
    assert "Policy" in str(e)
    # Check that policy denial was logged
    assert audit_mock.log_rejection.called
    call_args = audit_mock.log_rejection.call_args
    assert "POLICY_DENIED" in str(call_args)
    # ✓ PASS: Hollow enum has teeth
```

---

### 🎉 Premature Celebration
**The Problem:** Success is declared before all the work is done. The celebration is premature.

**In Game Debugging:**
```
❌ BAD: Emit victory event, THEN check if actually won
✓ GOOD: Check if won, THEN emit victory event
```

**In Security:**
```
❌ BAD: Return recovered bitchain, THEN log recovery in audit
✓ GOOD: Log recovery in audit (immutable), THEN return bitchain

Premature Celebration Security Failure Example:
- Recovery operation returns expanded bitchain
- THEN it tries to write to audit log
- Process crashes before audit log is written
- Audit log shows: nothing happened
- But attacker now has the data
- Security theater: celebration (data returned) before the commitment (audit recorded)

Prevention:
✓ Create audit event BEFORE returning data
✓ Sign/commit audit entry (make it immutable)
✓ Use transaction pattern: audit first, data second
✓ If process crashes mid-recovery, audit shows "attempted"
✓ If audit fails, whole recovery fails (fail-safe)
✓ Audit entry is signed with recovery details
```

**Test It:**
```python
# Simulate crash during recovery (after data returned, before audit)
def test_premature_celebration_prevention():
    audit_log = []
    
    def audit_append_side_effect(event):
        # Simulate crash after first audit entry
        if len(audit_log) > 0:
            raise RuntimeError("Simulated crash")
        audit_log.append(event)
    
    audit_mock = MagicMock()
    audit_mock.append_and_sign.side_effect = audit_append_side_effect
    
    # This should fail if audit fails
    try:
        recovered = recover_bitchain(
            bitchain_id,
            auth_token=valid_token,
            requester_id="user",
            audit=audit_mock
        )
        # If we get here, check that audit was at least ATTEMPTED
        assert audit_mock.create_recovery_event.called
        # ✓ PASS: Audit was created BEFORE data returned
    except RuntimeError:
        # Expected: recovery failed when audit failed
        # ✓ PASS: Premature celebration prevented
```

---

## Pattern: The Recovery Ritual

Every recovery operation should flow through these checks in order:

```
1. PHANTOM PROP CHECK    → Verify bitchain exists + integrity
                            (Fail: raise IntegrityError)

2. REALM + LINEAGE       → Verify origin and domain
                            (Fail: raise ValueError)

3. COLD METHOD GATE      → Verify auth + identity + intent
                            (Fail: raise AuthenticationError)

4. ENVIRONMENT APPROVAL  → Verify policy + capability + rate limit
                            (Fail: raise PermissionError)

5. HOLLOW ENUM CHECK     → Enforce policy (not just declare)
                            (Fail: raise PermissionError)

6. PREMATURE CELEBRATION → Create + sign audit event BEFORE data
   PREVENTION              (Fail: raise AuditError)

7. RETURN DATA           → NOW and ONLY NOW return the recovery
```

---

## Using These Patterns in Code Review

When reviewing security-related code, ask:

### Phantom Prop Questions
- [ ] Does this verify the data actually exists?
- [ ] Does this check cryptographic signatures?
- [ ] Could an attacker fabricate this data?
- [ ] Can we trace it back to a trusted source?

### Cold Method Questions
- [ ] Does this check who's calling it?
- [ ] Does this verify intent (why are they calling it)?
- [ ] Does this check if the environment allows this action?
- [ ] Could this be called in an unauthorized context?

### Hollow Enum Questions
- [ ] Is there an explicit check for this policy?
- [ ] Does the check happen BEFORE the risky action?
- [ ] What happens if the check throws an exception?
- [ ] Is the policy enforced or just documented?

### Premature Celebration Questions
- [ ] When is logging done relative to the action?
- [ ] What if the process crashes before logging?
- [ ] Is the audit entry immutable/signed?
- [ ] Could an attacker hide their activity by crashing?

---

## Pattern: Data Classification Scrolls

Apply archetypes based on data sensitivity:

### 📜 PUBLIC Data
```
Phantom Prop:  Minimal (can be replicated)
Cold Method:   Minimal (less sensitive about who accesses)
Hollow Enum:   Light (basic access controls OK)
Premature:     Light (logging can be async)

Recovery Gate Pattern: Compressed read, no auth required
```

### 📜 SENSITIVE Data (e.g., Badges/XP History)
```
Phantom Prop:  Strict (verify provenance rigorously)
Cold Method:   Strict (auth required, intent verified)
Hollow Enum:   Strict (enforce ACL rigorously)
Premature:     Strict (audit MUST be immutable first)

Recovery Gate Pattern:
  1. Auth required
  2. Verify identity
  3. Check ACL (owner-only or org-wide)
  4. Create audit entry (sign it)
  5. Return compressed-only or partial with anonymization
```

### 📜 PII Data (e.g., GitHub Handles, Real Names)
```
Phantom Prop:  Maximum (zero tolerance for fabrication)
Cold Method:   Maximum (2FA often required)
Hollow Enum:   Maximum (fail closed, enforce strictly)
Premature:     Maximum (immutable audit with alerts)

Recovery Gate Pattern:
  1. Auth required
  2. Verify identity
  3. Check ACL (owner-only)
  4. Require second factor verification
  5. Create audit entry (sign + alert)
  6. Return anonymized or encrypted only (never plaintext)
  7. Log to security team
```

---

## Integration with Seed Compression

When bit-chains are compressed and expanded:

**During Compression:**
- ✓ Add `data_classification` field
- ✓ Add `access_control_list` field
- ✓ Embed breadcrumbs for recovery (Phantom Prop prevention)

**During Recovery (Expansion):**
- ✓ Check all four archetypes
- ✓ Log everything to audit trail
- ✓ Enforce policy before returning data
- ✓ Make audit immutable first

**Test Coverage:**
- ✓ Test Phantom Prop: fabricated bitchain rejected
- ✓ Test Cold Method: unauthenticated recovery denied
- ✓ Test Hollow Enum: policy enforced in code
- ✓ Test Premature: audit created before data returned

---

## For Teams Building with Seed

### When Adding New Recovery Endpoints

1. **Identify the data classification** (PUBLIC / SENSITIVE / PII)
2. **Ask Phantom Prop questions:** How do we know this bitchain is real?
3. **Ask Cold Method questions:** Who should be allowed to recover this?
4. **Ask Hollow Enum questions:** What's the policy and how do we enforce it?
5. **Ask Premature questions:** When and how is recovery logged?
6. **Write tests** for all four archetypes
7. **Code review** against the checklist above

### When Integrating with Pets/Badges

- Badges contain SENSITIVE data (GitHub handles + achievement history)
- Use SENSITIVE classification by default
- Require auth for any recovery
- Enforce ACL checking (owner-only or org-with-approval)
- Return compressed-only or anonymized partial
- Log all recovery attempts
- Alert on unusual patterns (bulk extraction, off-hours, etc.)

---

## Example: Building a Secure Recovery Gate

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class DataClass(Enum):
    PUBLIC = "PUBLIC"
    SENSITIVE = "SENSITIVE"
    PII = "PII"

class Capability(Enum):
    COMPRESSED = "compressed"
    PARTIAL = "partial"
    FULL = "full"

@dataclass
class RecoveryPolicy:
    classification: DataClass
    allowed_roles: List[str]
    requires_second_factor: bool = False
    default_capability: Capability = Capability.COMPRESSED
    anonymization_rules: dict = None

class SecureRecoveryGate:
    """Security through Story Test archetypes."""
    
    def recover(self, bitchain_id: str, auth_token: str, 
               requester_id: str, intent: dict) -> dict:
        """
        All four archetypes enforced in order.
        Fail-safe: any check fails → entire recovery fails.
        """
        
        try:
            # 1. PHANTOM PROP: Verify bitchain reality
            bc = self._verify_existence(bitchain_id)
            self._verify_signature(bc)
            
            # 2. REALM + LINEAGE: Verify origin
            self._trace_lineage(bc)
            
            # 3. COLD METHOD: Verify context
            identity = self._verify_auth_token(auth_token)
            self._verify_intent(intent, bitchain_id)
            
            # 4 & 5. ENVIRONMENT + HOLLOW ENUM: Enforce policy
            policy = self._get_policy(bc.classification)
            if requester_id not in policy.allowed_roles:
                self._audit_rejection("POLICY_DENIED", bitchain_id, requester_id)
                raise PermissionError(f"Role not in {policy.allowed_roles}")
            
            if policy.requires_second_factor:
                if not self._verify_second_factor(requester_id):
                    self._audit_rejection("2FA_FAIL", bitchain_id, requester_id)
                    raise PermissionError("Second factor required")
            
            # 6. PREMATURE CELEBRATION: Audit BEFORE returning
            capability = policy.default_capability
            audit_event = self._create_audit_event(
                bitchain_id, requester_id, capability, bc.classification
            )
            self._append_audit_immutable(audit_event)  # Commit now
            
            # 7. NOW safe to return
            if capability == Capability.COMPRESSED:
                return bc.compressed_form
            elif capability == Capability.PARTIAL:
                return self._anonymize(bc, policy.anonymization_rules)
            else:
                return bc.full_form
                
        except Exception as e:
            # Audit the failure
            self._audit_rejection("EXCEPTION", bitchain_id, requester_id, str(e))
            raise  # Re-raise: fail closed
    
    # Implementation of each check
    def _verify_existence(self, bitchain_id: str) -> dict:
        """PHANTOM PROP: Is this real?"""
        bc = self.ledger.get(bitchain_id)
        if not bc:
            raise ValueError(f"Bitchain {bitchain_id} not in ledger")
        return bc
    
    def _verify_signature(self, bc: dict):
        """PHANTOM PROP: Is it intact?"""
        if not self.crypto.verify_signature(bc):
            raise ValueError(f"Signature verification failed")
    
    def _verify_auth_token(self, token: str) -> str:
        """COLD METHOD: Is this person real?"""
        identity = self.auth.verify_token(token)
        if not identity:
            raise AuthenticationError("Invalid token")
        return identity
    
    def _verify_intent(self, intent: dict, bitchain_id: str):
        """COLD METHOD: Why do they want this?"""
        if not intent.get('request_id'):
            raise ValueError("Intent declaration required (request_id)")
        if bitchain_id not in intent.get('resources', []):
            raise ValueError("Bitchain not in declared intent")
    
    def _get_policy(self, classification: DataClass) -> RecoveryPolicy:
        """HOLLOW ENUM: What's the policy?"""
        return self.policies[classification]
    
    def _create_audit_event(self, bitchain_id: str, requester_id: str,
                           capability: Capability, classification: DataClass) -> dict:
        """PREMATURE CELEBRATION: Document the moment."""
        return {
            'action': 'recovery',
            'bitchain_id': bitchain_id,
            'recovered_by': requester_id,
            'capability': capability.value,
            'classification': classification.value,
            'timestamp': now_iso8601(),
        }
    
    def _append_audit_immutable(self, event: dict):
        """PREMATURE CELEBRATION: Sign it now (before returning data)."""
        signed_event = self.crypto.sign(event)
        self.audit_ledger.append(signed_event)
        # If this fails, everything fails (no recovery returned)
    
    def _audit_rejection(self, reason: str, bitchain_id: str, 
                        requester_id: str, details: str = ""):
        """Log all rejections for security review."""
        event = {
            'action': 'recovery_rejected',
            'reason': reason,
            'bitchain_id': bitchain_id,
            'attempted_by': requester_id,
            'details': details,
            'timestamp': now_iso8601(),
        }
        signed = self.crypto.sign(event)
        self.audit_ledger.append(signed)
```

---

## The Bottom Line

Security isn't a separate language. It's the same patterns you already know:
- **Verify props are real** (not fabricated)
- **Check methods know their context** (not cold)
- **Enforce policies in code** (not hollow)
- **Commit before celebrating** (not premature)

By extending Story Test archetypes into security, you make security feel like part of your culture, not an external burden.

Every developer already knows these patterns. Now they just apply them to data integrity too.

🔐 + 📜 = 💪

---

**Last Updated:** 2025-01-[current]  
**Applies To:** Seed compression, badge recovery, any sensitive data access  
**For:** Tiny Walnut Games development team