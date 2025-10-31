"""
Governance Integration Tests (Layer 4: Policy Enforcement)

This test suite defines the contract for governance policies that operate
across Event Store, Tick Engine, and API Gateway. Policies enforce business rules,
prevent invalid state transitions, and audit command execution.

All tests MUST pass before governance implementation is considered complete.

Test Coverage:
- Policy creation and enforcement
- Command validation against policies
- Policy rejection with reason
- Policy mutation (command transformation)
- Policy composition (multiple policies)
- Policy scope (entity/user/command type)
- Cascade reactions with governance
- Audit trail recording
- Policy precedence and conflict resolution
"""

import pytest
import sys
from pathlib import Path as PathlibPath
from datetime import datetime
import uuid

# Add web/server to path so we can import governance
sys.path.insert(0, str(PathlibPath(__file__).parent.parent / "web" / "server"))

from governance import (
    PolicyDecision,
    PolicyContext,
    PolicyDecisionResult,
    GovernancePolicy,
    AuditEntry,
    GovernanceEngine,
)


# ============================================================================
# TEST CLASSES
# ============================================================================

@pytest.mark.e2e
class TestGovernancePolicyCreation:
    """Policies can be created, registered, and removed."""
    
    @pytest.mark.e2e
    def test_add_policy_to_engine(self):
        """Policy is registered in engine."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test", "ok")
        
        policy = GovernancePolicy(
            name="test_policy",
            description="Test policy",
            scope="global",
            check_fn=check_fn
        )
        
        engine.add_policy(policy)
        assert "test_policy" in engine.policies
        assert engine.policies["test_policy"].name == "test_policy"
    
    @pytest.mark.e2e
    def test_remove_policy_from_engine(self):
        """Policy is unregistered from engine."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test", "ok")
        
        policy = GovernancePolicy(
            name="test_policy",
            description="Test policy",
            scope="global",
            check_fn=check_fn
        )
        
        engine.add_policy(policy)
        assert "test_policy" in engine.policies
        
        engine.remove_policy("test_policy")
        assert "test_policy" not in engine.policies
    
    @pytest.mark.e2e
    def test_policy_scope_indexing(self):
        """Policies are indexed by scope for fast lookup."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test", "ok")
        
        policy1 = GovernancePolicy(
            name="global_policy",
            description="Global policy",
            scope="global",
            check_fn=check_fn
        )
        
        policy2 = GovernancePolicy(
            name="entity_policy",
            description="Entity-specific policy",
            scope="entity:entity_1",
            check_fn=check_fn
        )
        
        engine.add_policy(policy1)
        engine.add_policy(policy2)
        
        assert "global_policy" in engine.scope_index["global"]
        assert "entity_policy" in engine.scope_index["entity:entity_1"]


@pytest.mark.e2e
class TestGovernancePolicyEvaluation:
    """Policies can evaluate commands and permit/deny them."""
    
    @pytest.mark.e2e
    def test_simple_permit_policy(self):
        """Policy permits command."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "always_permit", "ok")
        
        policy = GovernancePolicy(
            name="always_permit",
            description="Always permit",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="admin",
            payload={"key": "value"},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        assert result.decision == PolicyDecision.PERMIT
    
    @pytest.mark.e2e
    def test_simple_deny_policy(self):
        """Policy denies command."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.DENY, "always_deny", "forbidden")
        
        policy = GovernancePolicy(
            name="always_deny",
            description="Always deny",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={"key": "value"},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "forbidden"
    
    @pytest.mark.e2e
    def test_role_based_policy(self):
        """Policy enforces role-based access."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            if ctx.actor_role == "admin":
                return PolicyDecisionResult(PolicyDecision.PERMIT, "role_check", "admin allowed")
            else:
                return PolicyDecisionResult(PolicyDecision.DENY, "role_check", "only admins can delete")
        
        policy = GovernancePolicy(
            name="role_check",
            description="Role-based access",
            scope="command:DeleteEntity",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        # Admin can delete
        admin_ctx = PolicyContext(
            command_type="DeleteEntity",
            entity_id="entity_1",
            actor_id="admin_1",
            actor_role="admin",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        result = engine.evaluate_command(admin_ctx)
        assert result.decision == PolicyDecision.PERMIT
        
        # User cannot delete
        user_ctx = PolicyContext(
            command_type="DeleteEntity",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        result = engine.evaluate_command(user_ctx)
        assert result.decision == PolicyDecision.DENY


@pytest.mark.e2e
class TestGovernancePolicyMutation:
    """Policies can mutate commands before they are processed."""
    
    @pytest.mark.e2e
    def test_simple_mutation_policy(self):
        """Policy can mutate payload."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            mutated = dict(ctx.payload)
            mutated["audit_required"] = True
            return PolicyDecisionResult(
                PolicyDecision.MUTATE,
                "add_audit_flag",
                "audit flag added",
                mutated_payload=mutated
            )
        
        policy = GovernancePolicy(
            name="add_audit_flag",
            description="Add audit flag",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={"key": "value"},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        assert result.decision == PolicyDecision.MUTATE
        assert result.mutated_payload is not None
        assert result.mutated_payload["audit_required"] is True
        assert result.mutated_payload["key"] == "value"
    
    @pytest.mark.e2e
    def test_mutation_chain(self):
        """Multiple policies mutate payload sequentially."""
        engine = GovernanceEngine()
        
        def add_timestamp(ctx: PolicyContext) -> PolicyDecisionResult:
            mutated = dict(ctx.payload)
            mutated["timestamp_added"] = True
            return PolicyDecisionResult(
                PolicyDecision.MUTATE,
                "add_timestamp",
                "timestamp added",
                mutated_payload=mutated
            )
        
        def add_user_id(ctx: PolicyContext) -> PolicyDecisionResult:
            mutated = dict(ctx.payload)
            mutated["actor_id_recorded"] = ctx.actor_id
            return PolicyDecisionResult(
                PolicyDecision.MUTATE,
                "add_user_id",
                "user id added",
                mutated_payload=mutated
            )
        
        policy1 = GovernancePolicy(
            name="add_timestamp",
            description="Add timestamp",
            scope="global",
            check_fn=add_timestamp,
            priority=1
        )
        policy2 = GovernancePolicy(
            name="add_user_id",
            description="Add user id",
            scope="global",
            check_fn=add_user_id,
            priority=2
        )
        
        engine.add_policy(policy1)
        engine.add_policy(policy2)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={"key": "value"},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        assert result.decision == PolicyDecision.MUTATE
        assert result.mutated_payload["timestamp_added"] is True
        assert result.mutated_payload["actor_id_recorded"] == "user_1"


@pytest.mark.e2e
class TestGovernancePolicyScope:
    """Policies apply to the correct scope."""
    
    @pytest.mark.e2e
    def test_global_policy_applies_to_all(self):
        """Global policy applies to all commands."""
        engine = GovernanceEngine()
        
        evaluated_commands = []
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            evaluated_commands.append(ctx.command_type)
            return PolicyDecisionResult(PolicyDecision.PERMIT, "global", "ok")
        
        policy = GovernancePolicy(
            name="global",
            description="Global",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        for command_type in ["SetValue", "DeleteEntity", "AddChild"]:
            ctx = PolicyContext(
                command_type=command_type,
                entity_id="entity_1",
                actor_id="user_1",
                actor_role="user",
                payload={},
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4())
            )
            engine.evaluate_command(ctx)
        
        assert len(evaluated_commands) == 3
        assert all(c in ["SetValue", "DeleteEntity", "AddChild"] for c in evaluated_commands)
    
    @pytest.mark.e2e
    def test_entity_policy_applies_to_entity_only(self):
        """Entity-specific policy applies only to that entity."""
        engine = GovernanceEngine()
        
        evaluated_entities = []
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            evaluated_entities.append(ctx.entity_id)
            return PolicyDecisionResult(PolicyDecision.PERMIT, "entity_specific", "ok")
        
        policy = GovernancePolicy(
            name="entity_specific",
            description="Entity-specific",
            scope="entity:entity_1",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        for entity_id in ["entity_1", "entity_2", "entity_3"]:
            ctx = PolicyContext(
                command_type="SetValue",
                entity_id=entity_id,
                actor_id="user_1",
                actor_role="user",
                payload={},
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4())
            )
            engine.evaluate_command(ctx)
        
        # Policy only evaluated for entity_1
        assert len(evaluated_entities) == 1
        assert evaluated_entities[0] == "entity_1"
    
    @pytest.mark.e2e
    def test_command_type_policy_applies_to_command_only(self):
        """Command-type policy applies only to that command type."""
        engine = GovernanceEngine()
        
        evaluated_commands = []
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            evaluated_commands.append(ctx.command_type)
            return PolicyDecisionResult(PolicyDecision.PERMIT, "command_specific", "ok")
        
        policy = GovernancePolicy(
            name="command_specific",
            description="Command-specific",
            scope="command:DeleteEntity",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        for command_type in ["SetValue", "DeleteEntity", "AddChild"]:
            ctx = PolicyContext(
                command_type=command_type,
                entity_id="entity_1",
                actor_id="user_1",
                actor_role="user",
                payload={},
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4())
            )
            engine.evaluate_command(ctx)
        
        # Policy only evaluated for DeleteEntity
        assert len(evaluated_commands) == 1
        assert evaluated_commands[0] == "DeleteEntity"


@pytest.mark.e2e
class TestGovernancePolicyPriority:
    """Policies execute in priority order."""
    
    @pytest.mark.e2e
    def test_priority_ordering(self):
        """Policies execute in priority order (lower number = higher priority)."""
        engine = GovernanceEngine()
        execution_order = []
        
        def make_check_fn(priority_level):
            def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
                execution_order.append(priority_level)
                return PolicyDecisionResult(PolicyDecision.PERMIT, f"priority_{priority_level}", "ok")
            return check_fn
        
        # Add policies in non-priority order
        for priority in [50, 10, 30, 20]:
            policy = GovernancePolicy(
                name=f"policy_{priority}",
                description=f"Priority {priority}",
                scope="global",
                check_fn=make_check_fn(priority),
                priority=priority
            )
            engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        engine.evaluate_command(ctx)
        
        # Should execute in order: 10, 20, 30, 50
        assert execution_order == [10, 20, 30, 50]
    
    @pytest.mark.e2e
    def test_deny_short_circuits_execution(self):
        """DENY result short-circuits remaining policies."""
        engine = GovernanceEngine()
        execution_order = []
        
        def policy_1(ctx: PolicyContext) -> PolicyDecisionResult:
            execution_order.append(1)
            return PolicyDecisionResult(PolicyDecision.PERMIT, "policy_1", "ok")
        
        def policy_2(ctx: PolicyContext) -> PolicyDecisionResult:
            execution_order.append(2)
            return PolicyDecisionResult(PolicyDecision.DENY, "policy_2", "denied")
        
        def policy_3(ctx: PolicyContext) -> PolicyDecisionResult:
            execution_order.append(3)
            return PolicyDecisionResult(PolicyDecision.PERMIT, "policy_3", "ok")
        
        engine.add_policy(GovernancePolicy("p1", "Policy 1", "global", policy_1, priority=1))
        engine.add_policy(GovernancePolicy("p2", "Policy 2", "global", policy_2, priority=2))
        engine.add_policy(GovernancePolicy("p3", "Policy 3", "global", policy_3, priority=3))
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        
        # Policy 3 should NOT execute
        assert execution_order == [1, 2]
        assert result.decision == PolicyDecision.DENY


@pytest.mark.e2e
class TestGovernanceAuditLog:
    """Policy evaluations are recorded in audit log."""
    
    @pytest.mark.e2e
    def test_audit_log_records_permit(self):
        """Audit log records PERMIT decisions."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test_policy", "ok")
        
        policy = GovernancePolicy(
            name="test_policy",
            description="Test",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        correlation_id = str(uuid.uuid4())
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id
        )
        
        engine.evaluate_command(ctx)
        
        audit_log = engine.get_audit_log()
        assert len(audit_log) == 1
        entry = audit_log[0]
        assert entry.command_type == "SetValue"
        assert entry.entity_id == "entity_1"
        assert entry.actor_id == "user_1"
        assert entry.final_decision == PolicyDecision.PERMIT
        assert entry.correlation_id == correlation_id
    
    @pytest.mark.e2e
    def test_audit_log_records_deny(self):
        """Audit log records DENY decisions."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.DENY, "test_policy", "forbidden")
        
        policy = GovernancePolicy(
            name="test_policy",
            description="Test",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        engine.evaluate_command(ctx)
        
        audit_log = engine.get_audit_log()
        assert len(audit_log) == 1
        assert audit_log[0].final_decision == PolicyDecision.DENY
        assert audit_log[0].reason == "forbidden"
    
    @pytest.mark.e2e
    def test_audit_log_filters_by_entity(self):
        """Audit log can filter by entity_id."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test", "ok")
        
        policy = GovernancePolicy(
            name="test",
            description="Test",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        for entity_id in ["entity_1", "entity_2", "entity_1"]:
            ctx = PolicyContext(
                command_type="SetValue",
                entity_id=entity_id,
                actor_id="user_1",
                actor_role="user",
                payload={},
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4())
            )
            engine.evaluate_command(ctx)
        
        all_entries = engine.get_audit_log()
        assert len(all_entries) == 3
        
        entity_1_entries = engine.get_audit_log(entity_id="entity_1")
        assert len(entity_1_entries) == 2
        assert all(e.entity_id == "entity_1" for e in entity_1_entries)
    
    @pytest.mark.e2e
    def test_audit_log_filters_by_actor(self):
        """Audit log can filter by actor_id."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            return PolicyDecisionResult(PolicyDecision.PERMIT, "test", "ok")
        
        policy = GovernancePolicy(
            name="test",
            description="Test",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        for actor_id in ["user_1", "user_2", "user_1"]:
            ctx = PolicyContext(
                command_type="SetValue",
                entity_id="entity_1",
                actor_id=actor_id,
                actor_role="user",
                payload={},
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4())
            )
            engine.evaluate_command(ctx)
        
        all_entries = engine.get_audit_log()
        assert len(all_entries) == 3
        
        user_1_entries = engine.get_audit_log(actor_id="user_1")
        assert len(user_1_entries) == 2
        assert all(e.actor_id == "user_1" for e in user_1_entries)


@pytest.mark.e2e
class TestGovernanceIntegrationWithEventStore:
    """Governance policies integrate with Event Store operations."""
    
    @pytest.mark.e2e
    def test_policy_can_prevent_event_persistence(self):
        """Policies can deny commands before they are persisted."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            if ctx.payload.get("sensitive") is True:
                return PolicyDecisionResult(
                    PolicyDecision.DENY,
                    "sensitive_check",
                    "sensitive operations require approval"
                )
            return PolicyDecisionResult(PolicyDecision.PERMIT, "sensitive_check", "ok")
        
        policy = GovernancePolicy(
            name="sensitive_check",
            description="Prevent sensitive operations",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        # Non-sensitive command is permitted
        ctx1 = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={"sensitive": False},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        result1 = engine.evaluate_command(ctx1)
        assert result1.decision == PolicyDecision.PERMIT
        
        # Sensitive command is denied
        ctx2 = PolicyContext(
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="user_1",
            actor_role="user",
            payload={"sensitive": True},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        result2 = engine.evaluate_command(ctx2)
        assert result2.decision == PolicyDecision.DENY


@pytest.mark.e2e
class TestGovernanceIntegrationWithTickEngine:
    """Governance policies integrate with Tick Engine cascades."""
    
    @pytest.mark.e2e
    def test_policy_can_prevent_cascade_reactions(self):
        """Policies can prevent reactions from cascading."""
        engine = GovernanceEngine()
        
        def check_fn(ctx: PolicyContext) -> PolicyDecisionResult:
            # Prevent DeleteEntity commands from triggering cascades
            if ctx.command_type == "DeleteEntity":
                return PolicyDecisionResult(
                    PolicyDecision.DENY,
                    "cascade_prevention",
                    "cascading deletes not allowed"
                )
            return PolicyDecisionResult(PolicyDecision.PERMIT, "cascade_prevention", "ok")
        
        policy = GovernancePolicy(
            name="cascade_prevention",
            description="Prevent cascading deletes",
            scope="global",
            check_fn=check_fn
        )
        engine.add_policy(policy)
        
        ctx = PolicyContext(
            command_type="DeleteEntity",
            entity_id="entity_1",
            actor_id="admin_1",
            actor_role="admin",
            payload={},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        result = engine.evaluate_command(ctx)
        assert result.decision == PolicyDecision.DENY


# ============================================================================
# RITUAL CLOSURE
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])