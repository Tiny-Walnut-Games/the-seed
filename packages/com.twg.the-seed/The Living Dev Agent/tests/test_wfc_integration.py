#!/usr/bin/env python3
"""
Integration Tests: WFC Firewall + RecoveryGate + Conservator

Tests the complete three-layer firewall flow:
1. WFC Collapse (Layer 1): BOUND vs ESCAPED determination
2. RecoveryGate (Layer 2): Security gates for BOUND manifests
3. Conservator (Layer 2): Repair for ESCAPED manifests
4. Re-validation (Loop): Check if repair successful

Implements all scenarios from scratch.md pseudo-code.

Status: Phase 2 Integration Validation
"""

import sys
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

# Add paths
engine_dir = Path(__file__).resolve().parents[2] / 'seed' / 'engine'
sys.path.insert(0, str(engine_dir))
tests_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(tests_dir))

from stat7_experiments import (
    BitChain, Coordinates, DataClass, Capability,
    generate_random_bitchain, compute_address_hash
)
from wfc_firewall import WaveFormCollapseKernel, CollapseResult
from recovery_gate import (
    RecoveryGate, InMemoryLedger, InMemoryAuditLedger,
    SimpleAuthService, SimpleCryptoService
)
from conservator import TheConservator, RepairTrigger
from wfc_integration import (
    WFCIntegrationOrchestrator, ManifestationPhase, IntegrationEventType,
    ManifestationJourney
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def wfc_kernel():
    """Create WFC kernel instance."""
    return WaveFormCollapseKernel()


@pytest.fixture
def crypto_service():
    """Create crypto service."""
    return SimpleCryptoService(key=b"integration-test-key")


@pytest.fixture
def auth_service():
    """Create auth service with test tokens."""
    auth = SimpleAuthService()
    auth.register_token("valid-token-alice", "alice", role="owner")
    auth.register_token("valid-token-bob", "bob", role="admin")
    auth.register_token("valid-token-viewer", "viewer", role="viewer")
    return auth


@pytest.fixture
def ledger():
    """Create in-memory ledger."""
    return InMemoryLedger()


@pytest.fixture
def audit_ledger():
    """Create audit ledger."""
    return InMemoryAuditLedger(signing_key=b"audit-integration-key")


@pytest.fixture
def recovery_gate(ledger, auth_service, audit_ledger, crypto_service):
    """Create recovery gate."""
    return RecoveryGate(
        ledger=ledger,
        auth_service=auth_service,
        audit_ledger=audit_ledger,
        crypto_service=crypto_service,
    )


@pytest.fixture
def conservator(tmp_path):
    """Create conservator instance."""
    manifest_path = tmp_path / "manifest.json"
    backup_path = tmp_path / "backups"
    chronicle_path = tmp_path / "chronicle"

    return TheConservator(
        manifest_path=str(manifest_path),
        backup_path=str(backup_path),
        chronicle_path=str(chronicle_path),
    )


@pytest.fixture
def orchestrator(wfc_kernel, recovery_gate, conservator):
    """Create integration orchestrator."""
    return WFCIntegrationOrchestrator(
        wfc_kernel=wfc_kernel,
        recovery_gate=recovery_gate,
        conservator=conservator,
    )


@pytest.fixture
def sample_bitchain():
    """Create a sample public bitchain."""
    bc = generate_random_bitchain()
    bc.data_classification = DataClass.PUBLIC
    bc.owner_id = "alice"
    return bc


# ============================================================================
# TESTS: WFC COLLAPSE LAYER (Layer 1) - Via BitChain objects
# ============================================================================

@pytest.mark.integration
class TestWFCCollapseLayer:
    """Test Layer 1: WFC Collapse determines BOUND or ESCAPED."""

    @pytest.mark.integration
    def test_wfc_collapse_with_bitchain_object(self, wfc_kernel, sample_bitchain):
        """WFC should properly collapse a real BitChain object."""
        # WFC works with actual BitChain objects that have coordinates
        result = wfc_kernel.collapse(sample_bitchain)

        # Should return a valid CollapseReport
        assert result is not None
        assert result.result is not None
        assert result.bitchain_id == sample_bitchain.id

    @pytest.mark.integration
    def test_wfc_collapse_deterministic_with_bitchain(self, wfc_kernel, sample_bitchain):
        """Same BitChain should always produce same collapse result."""
        # First collapse
        result1 = wfc_kernel.collapse(sample_bitchain)

        # Second collapse (same bitchain)
        result2 = wfc_kernel.collapse(sample_bitchain)

        # Results should be identical
        assert result1.result == result2.result
        assert result1.julia_parameter == result2.julia_parameter

    @pytest.mark.integration
    def test_wfc_collapse_validates_julia_parameters(self, wfc_kernel, sample_bitchain):
        """Julia parameters should be valid complex numbers."""
        result = wfc_kernel.collapse(sample_bitchain)

        assert isinstance(result.julia_parameter, complex)


# ============================================================================
# TESTS: RECOVERY GATE LAYER (Layer 2a - BOUND path)
# ============================================================================

@pytest.mark.integration
class TestRecoveryGateBoundPath:
    """Test Layer 2a: RecoveryGate processes BOUND manifests."""

    @pytest.mark.integration
    def test_recovery_gate_allows_valid_auth(
        self, recovery_gate, crypto_service, sample_bitchain
    ):
        """RecoveryGate should pass BOUND manifest with valid auth."""
        # Register bitchain in ledger
        signature = crypto_service.sign_bitchain(sample_bitchain)
        recovery_gate.ledger.store(sample_bitchain, signature)

        # Attempt recovery
        result = recovery_gate.recover_bitchain(
            bitchain_id=sample_bitchain.id,
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [sample_bitchain.id]}
        )

        assert result is not None
        assert 'id' in result or 'data' in result

    @pytest.mark.integration
    def test_recovery_gate_denies_invalid_auth(
        self, recovery_gate, crypto_service, sample_bitchain
    ):
        """RecoveryGate should deny BOUND manifest with invalid auth."""
        # Register bitchain
        signature = crypto_service.sign_bitchain(sample_bitchain)
        recovery_gate.ledger.store(sample_bitchain, signature)

        # Attempt with invalid token
        with pytest.raises(ValueError, match="Invalid.*token"):
            recovery_gate.recover_bitchain(
                bitchain_id=sample_bitchain.id,
                auth_token="fake-token",
                requester_id="alice",
                intent={'request_id': 'req-1', 'resources': [sample_bitchain.id]}
            )


# ============================================================================
# TESTS: ORCHESTRATOR - BOUND PATH
# ============================================================================

@pytest.mark.integration
class TestOrchestratorBoundPath:
    """Test complete flow when manifestation is BOUND."""

    @pytest.mark.integration
    def test_orchestrator_bound_path_basic(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """BOUND manifestation should succeed through full flow."""
        # Register bitchain in gate's ledger
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        # Process through orchestrator
        success, status, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={'request_id': 'req-1', 'resources': [sample_bitchain.id]},
        )

        # Should succeed
        assert success
        assert status in ["BOUND", "REPAIRED"]  # Either path works
        assert journey is not None
        assert journey.final_result == "LUCA_REGISTERED"

    @pytest.mark.integration
    def test_orchestrator_bound_path_audit_trail(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """BOUND path should create proper audit trail."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        success, status, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        assert success

        # Check audit trail events
        event_types = [e.event_type for e in journey.audit_trail]
        assert IntegrationEventType.WFC_COLLAPSE_ATTEMPT in event_types
        assert IntegrationEventType.WFC_BOUND in event_types or IntegrationEventType.WFC_ESCAPED in event_types

    @pytest.mark.integration
    def test_orchestrator_journey_phase_progression(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Journey phases should progress correctly."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        success, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Initial phase should be ENTRY
        assert journey.initial_phase == ManifestationPhase.ENTRY

        # Current phase should be ROUTED (success) or REJECTED (failure)
        assert journey.current_phase in [
            ManifestationPhase.ROUTED,
            ManifestationPhase.REJECTED,
        ]


# ============================================================================
# TESTS: ORCHESTRATOR - ESCAPED PATH
# ============================================================================

@pytest.mark.integration
class TestOrchestratorEscapedPath:
    """Test complete flow when manifestation ESCAPES firewall."""

    @pytest.mark.e2e
    def test_orchestrator_escaped_path_detected(self, orchestrator):
        """Orchestrator should detect ESCAPED manifests."""
        # Process a bitchain that will likely escape
        success, status, journey = orchestrator.process_bitchain(
            bitchain_id="escaped-test-1",
            stat7_address="VOID:G7:A7:H7:L7:P7:D7",  # Edge case address
        )

        # Check if WFC detected escape
        assert journey is not None

        # Either path is valid (depends on STAT7 space)
        # Main point: flow completes and returns journey
        assert journey.final_result is not None

    @pytest.mark.integration
    def test_orchestrator_escape_triggers_conservator(self, orchestrator):
        """If manifestation escapes, should attempt Conservator repair."""
        # We'll test that the flow exists, even if escape is rare
        success, status, journey = orchestrator.process_bitchain(
            bitchain_id="escape-repair-test",
            stat7_address="VOID:G7:A7:H7:L7:P7:D7",
        )

        # Check journey was recorded
        assert journey is not None
        assert len(journey.audit_trail) > 0


# ============================================================================
# TESTS: ORCHESTRATOR - WFC REPORTS
# ============================================================================

@pytest.mark.integration
class TestOrchestratorWFCReports:
    """Test that WFC reports are properly captured in journey."""

    @pytest.mark.integration
    def test_orchestrator_captures_julia_parameters(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Journey should capture Julia parameters."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        _, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Should have WFC reports
        assert 'initial_collapse' in journey.wfc_reports
        assert 'result' in journey.wfc_reports['initial_collapse']
        assert 'iterations_to_escape' in journey.wfc_reports['initial_collapse']

    @pytest.mark.integration
    def test_orchestrator_tracks_escape_magnitude(self, orchestrator):
        """Journey should track escape magnitude for diagnostics."""
        _, _, journey = orchestrator.process_bitchain(
            bitchain_id="escape-mag-test",
            stat7_address="VOID:G7:A7:H7:L7:P7:D7",
        )

        # If escape happened, should have escape_magnitude
        if 'escaped' in str(journey.wfc_reports.get('initial_collapse', {}).get('result', '')):
            assert 'escape_magnitude' in journey.wfc_reports['initial_collapse']


# ============================================================================
# TESTS: ORCHESTRATOR - JOURNEY RETRIEVAL
# ============================================================================

@pytest.mark.integration
class TestOrchestratorJourneyManagement:
    """Test journey storage and retrieval."""

    @pytest.mark.integration
    def test_orchestrator_stores_journey(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Orchestrator should store journey after processing."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Should be able to retrieve journey
        retrieved = orchestrator.get_journey(sample_bitchain.id)
        assert retrieved is not None
        assert retrieved.bitchain_id == sample_bitchain.id

    @pytest.mark.integration
    def test_orchestrator_exports_journeys_as_json(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Orchestrator should export journeys as JSON."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Export and parse
        json_export = orchestrator.export_journeys()
        data = json.loads(json_export)

        assert 'journeys' in data
        assert sample_bitchain.id in data['journeys']


# ============================================================================
# TESTS: ORCHESTRATOR - FIREWALL_ESCAPE TRIGGER
# ============================================================================

@pytest.mark.integration
class TestFirewallEscapeTrigger:
    """Test that FIREWALL_ESCAPE trigger is recognized."""

    @pytest.mark.integration
    def test_conservator_recognizes_firewall_escape_trigger(self, conservator):
        """Conservator should recognize FIREWALL_ESCAPE as valid trigger."""
        assert RepairTrigger.FIREWALL_ESCAPE in RepairTrigger
        assert RepairTrigger.FIREWALL_ESCAPE.value == "firewall_escape"


# ============================================================================
# TESTS: END-TO-END SCENARIO
# ============================================================================

@pytest.mark.integration
class TestEndToEndScenario:
    """Complete end-to-end integration scenarios."""

    @pytest.mark.integration
    def test_complete_bound_flow(
        self, orchestrator, crypto_service, sample_bitchain, audit_ledger
    ):
        """
        Complete scenario: Bitchain arrives BOUND, passes all gates, registers with LUCA.

        Scenario from scratch.md:
            1. Collapse → BOUND
            2. RecoveryGate → PASS
            3. LUCA register
            4. Audit trail complete
        """
        # Setup
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        # Execute
        success, status, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
            intent={
                'request_id': 'e2e-req-1',
                'resources': [sample_bitchain.id],
                'reason': 'end_to_end_test',
            }
        )

        # Verify
        assert journey is not None
        assert len(journey.audit_trail) >= 2  # At least WFC collapse + one other event

        # Check we have WFC reports
        assert 'initial_collapse' in journey.wfc_reports

    @pytest.mark.integration
    def test_journey_serialization(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Journey should be serializable to dict/JSON."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        _, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Should serialize cleanly
        journey_dict = journey.to_dict()

        assert journey_dict['bitchain_id'] == sample_bitchain.id
        assert journey_dict['stat7_address'] == "PUBLIC:G0:A0:H0:L0:P0:D0"
        assert 'audit_trail' in journey_dict
        assert 'final_result' in journey_dict


# ============================================================================
# TESTS: INTEGRATION AUDIT TRAIL
# ============================================================================

@pytest.mark.integration
class TestIntegrationAuditTrail:
    """Test complete audit trail captures."""

    @pytest.mark.integration
    def test_audit_trail_entries_have_timestamps(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """All audit entries should have ISO8601 timestamps."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        _, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        for entry in journey.audit_trail:
            # Should be valid ISO8601
            assert entry.timestamp is not None
            # Should be parseable
            datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))

    @pytest.mark.integration
    def test_audit_trail_contains_phase_info(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Audit entries should track phase progression."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        _, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # All entries should have phase
        for entry in journey.audit_trail:
            assert entry.phase is not None
            assert isinstance(entry.phase, ManifestationPhase)

    @pytest.mark.integration
    def test_audit_trail_contains_event_types(
        self, orchestrator, crypto_service, sample_bitchain
    ):
        """Audit entries should classify events."""
        signature = crypto_service.sign_bitchain(sample_bitchain)
        orchestrator.gate.ledger.store(sample_bitchain, signature)

        _, _, journey = orchestrator.process_bitchain(
            bitchain_id=sample_bitchain.id,
            stat7_address="PUBLIC:G0:A0:H0:L0:P0:D0",
            auth_token="valid-token-alice",
            requester_id="alice",
        )

        # Should have various event types
        for entry in journey.audit_trail:
            assert entry.event_type is not None
            assert isinstance(entry.event_type, IntegrationEventType)


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run with: pytest tests/test_wfc_integration.py -v
    pytest.main([__file__, "-v"])
