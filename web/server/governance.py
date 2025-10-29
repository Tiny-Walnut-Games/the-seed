"""
Governance Engine (Layer 4: Policy Enforcement)

Evaluates commands against chainable, scope-based policies.
Enforces business rules, RBAC, transaction isolation, and audit trails.

Design:
- Policies registered by scope (global, entity:id, command:type, role:role)
- Evaluation order by priority (lower number = higher priority)
- DENY short-circuits immediately
- MUTATE chains payload through subsequent policies
- PERMIT if all applicable policies approve
- All evaluations recorded in audit log with correlation IDs
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class PolicyDecision(Enum):
    """Outcome of policy evaluation."""
    PERMIT = "permit"
    DENY = "deny"
    MUTATE = "mutate"


@dataclass
class PolicyContext:
    """Context passed to policy checker."""
    command_type: str
    entity_id: str
    actor_id: str
    actor_role: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str


@dataclass
class PolicyDecisionResult:
    """Result of policy evaluation."""
    decision: PolicyDecision
    policy_name: str
    reason: str
    mutated_payload: Optional[Dict[str, Any]] = None


@dataclass
class GovernancePolicy:
    """Single governance policy."""
    name: str
    description: str
    scope: str  # "global", "entity:{entity_id}", "command:{command_type}", "role:{role}"
    check_fn: Callable[[PolicyContext], PolicyDecisionResult]
    priority: int = 100
    enabled: bool = True


@dataclass
class AuditEntry:
    """Single audit log entry."""
    timestamp: datetime
    event_type: str
    command_type: str
    entity_id: str
    actor_id: str
    policies_evaluated: List[str]
    policy_results: List[PolicyDecisionResult]
    final_decision: PolicyDecision
    reason: str
    correlation_id: str


class GovernanceEngine:
    """Governance policy enforcement engine."""
    
    def __init__(self):
        self.policies: Dict[str, GovernancePolicy] = {}
        self.audit_log: List[AuditEntry] = []
        self.scope_index: Dict[str, List[str]] = {}  # scope -> [policy_names]
    
    def add_policy(self, policy: GovernancePolicy) -> None:
        """Register a governance policy."""
        self.policies[policy.name] = policy
        if policy.scope not in self.scope_index:
            self.scope_index[policy.scope] = []
        self.scope_index[policy.scope].append(policy.name)
    
    def remove_policy(self, policy_name: str) -> None:
        """Unregister a governance policy."""
        if policy_name in self.policies:
            policy = self.policies[policy_name]
            if policy.scope in self.scope_index:
                self.scope_index[policy.scope].remove(policy_name)
            del self.policies[policy_name]
    
    def evaluate_command(self, context: PolicyContext) -> PolicyDecisionResult:
        """
        Evaluate a command against all applicable policies.
        
        Returns the result of the first DENY, or composite PERMIT/MUTATE.
        """
        applicable_policies = self._find_applicable_policies(context)
        policy_results: List[PolicyDecisionResult] = []
        mutated_payload = dict(context.payload)
        
        # Sort by priority (lower priority number = higher priority)
        sorted_policies = sorted(
            [self.policies[name] for name in applicable_policies],
            key=lambda p: p.priority
        )
        
        for policy in sorted_policies:
            if not policy.enabled:
                continue
            
            result = policy.check_fn(
                PolicyContext(
                    command_type=context.command_type,
                    entity_id=context.entity_id,
                    actor_id=context.actor_id,
                    actor_role=context.actor_role,
                    payload=mutated_payload,
                    timestamp=context.timestamp,
                    correlation_id=context.correlation_id
                )
            )
            policy_results.append(result)
            
            # DENY short-circuits immediately
            if result.decision == PolicyDecision.DENY:
                self._record_audit(context, policy_results, PolicyDecision.DENY, result.reason)
                return result
            
            # MUTATE transforms the payload for next policy
            if result.decision == PolicyDecision.MUTATE and result.mutated_payload:
                mutated_payload = result.mutated_payload
        
        # If we got here, all policies permitted or mutated
        final_decision = PolicyDecision.MUTATE if mutated_payload != context.payload else PolicyDecision.PERMIT
        result = PolicyDecisionResult(
            decision=final_decision,
            policy_name="composite",
            reason="All applicable policies permitted",
            mutated_payload=mutated_payload if final_decision == PolicyDecision.MUTATE else None
        )
        self._record_audit(context, policy_results, final_decision, result.reason)
        return result
    
    def _find_applicable_policies(self, context: PolicyContext) -> List[str]:
        """Find all policies that apply to this context."""
        applicable = []
        
        # Global policies always apply
        if "global" in self.scope_index:
            applicable.extend(self.scope_index["global"])
        
        # Entity-specific policies
        entity_scope = f"entity:{context.entity_id}"
        if entity_scope in self.scope_index:
            applicable.extend(self.scope_index[entity_scope])
        
        # Command-type policies
        command_scope = f"command:{context.command_type}"
        if command_scope in self.scope_index:
            applicable.extend(self.scope_index[command_scope])
        
        # Role-based policies
        role_scope = f"role:{context.actor_role}"
        if role_scope in self.scope_index:
            applicable.extend(self.scope_index[role_scope])
        
        return list(set(applicable))  # Deduplicate
    
    def _record_audit(
        self,
        context: PolicyContext,
        results: List[PolicyDecisionResult],
        decision: PolicyDecision,
        reason: str
    ) -> None:
        """Record policy evaluation in audit log."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            event_type="policy_evaluation",
            command_type=context.command_type,
            entity_id=context.entity_id,
            actor_id=context.actor_id,
            policies_evaluated=[r.policy_name for r in results],
            policy_results=results,
            final_decision=decision,
            reason=reason,
            correlation_id=context.correlation_id
        )
        self.audit_log.append(entry)
    
    def get_audit_log(
        self,
        entity_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """Retrieve audit log with optional filters."""
        log = self.audit_log
        
        if entity_id:
            log = [e for e in log if e.entity_id == entity_id]
        
        if actor_id:
            log = [e for e in log if e.actor_id == actor_id]
        
        if since:
            log = [e for e in log if e.timestamp >= since]
        
        return log
    
    def clear_audit_log(self) -> None:
        """Clear audit log (for testing)."""
        self.audit_log.clear()