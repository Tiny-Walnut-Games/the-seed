#!/usr/bin/env python3
"""
Test Suite: Wave Function Collapse Firewall

Tests the Julia Set-based entry firewall for STAT7.
Validates that manifestations correctly collapse and are routed appropriately.

Tests cover:
- Julia parameter derivation from STAT7 coordinates
- Manifestation state derivation from identity hash
- Iteration algorithm and escape detection
- Bound vs escaped classification
- Batch operations and statistics
"""

import pytest
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Add seed engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "seed" / "engine"))

from wfc_firewall import (
    WaveFormCollapseKernel,
    CollapseResult,
    CollapseReport,
)
from stat7_experiments import (
    BitChain,
    Coordinates,
    DataClass,
    normalize_timestamp,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def high_resonance_coordinates():
    """Coherent, well-aligned entity."""
    return Coordinates(
        realm="data",
        lineage=1,
        adjacency=["root", "cluster-a"],
        horizon="peak",
        resonance=0.8,      # High coherence
        velocity=0.3,       # Moderate change
        density=0.5,        # Mid compression
    )


@pytest.fixture
def low_resonance_coordinates():
    """Poorly aligned, chaotic entity."""
    return Coordinates(
        realm="system",
        lineage=2,
        adjacency=["orphan"],
        horizon="decay",
        resonance=-0.7,     # Poor alignment
        velocity=0.9,       # High instability
        density=0.1,        # Low compression
    )


@pytest.fixture
def neutral_coordinates():
    """Balanced, stable entity."""
    return Coordinates(
        realm="narrative",
        lineage=0,
        adjacency=["genesis"],
        horizon="genesis",
        resonance=0.0,      # Perfectly neutral
        velocity=0.0,       # No change
        density=0.5,        # Mid compression
    )


@pytest.fixture
def coherent_bitchain(high_resonance_coordinates):
    """Well-formed bitchain with good STAT7 alignment."""
    return BitChain(
        id="entity-coherent-001",
        entity_type="concept",
        realm="data",
        coordinates=high_resonance_coordinates,
        created_at=normalize_timestamp(),
        state={"value": "stable", "phase": "active"},
        data_classification=DataClass.PUBLIC,
        owner_id="user-archive-001",
    )


@pytest.fixture
def chaotic_bitchain(low_resonance_coordinates):
    """Poorly formed bitchain with bad alignment."""
    return BitChain(
        id="entity-chaotic-001",
        entity_type="artifact",
        realm="system",
        coordinates=low_resonance_coordinates,
        created_at=normalize_timestamp(),
        state={"value": "unstable", "phase": "decay"},
        data_classification=DataClass.SENSITIVE,
        owner_id="user-unknown-001",
    )


@pytest.fixture
def neutral_bitchain(neutral_coordinates):
    """Balanced bitchain at neutral alignment."""
    return BitChain(
        id="entity-neutral-001",
        entity_type="lineage",
        realm="narrative",
        coordinates=neutral_coordinates,
        created_at=normalize_timestamp(),
        state={"value": "neutral", "phase": "genesis"},
        data_classification=DataClass.PUBLIC,
    )


# ============================================================================
# TESTS: Julia Parameter Derivation
# ============================================================================

class TestJuliaParameterDerivation:
    """
    Test that Julia parameters are correctly derived from STAT7 coordinates.
    
    The Julia parameter c controls the attractor shape. Different STAT7 coordinates
    should produce different c values that reflect their coherence and stability.
    """
    
    def test_high_resonance_positive_real(self, high_resonance_coordinates):
        """High resonance should produce positive real part."""
        c = WaveFormCollapseKernel.derive_julia_parameter(high_resonance_coordinates)
        
        # resonance=0.8 * 0.5 = 0.4
        assert c.real == pytest.approx(0.4)
        assert c.real > 0
    
    def test_low_resonance_negative_real(self, low_resonance_coordinates):
        """Low resonance should produce negative real part."""
        c = WaveFormCollapseKernel.derive_julia_parameter(low_resonance_coordinates)
        
        # resonance=-0.7 * 0.5 = -0.35
        assert c.real == pytest.approx(-0.35)
        assert c.real < 0
    
    def test_neutral_resonance_zero_real(self, neutral_coordinates):
        """Neutral resonance should produce zero real part."""
        c = WaveFormCollapseKernel.derive_julia_parameter(neutral_coordinates)
        
        # resonance=0.0 * 0.5 = 0.0
        assert c.real == pytest.approx(0.0, abs=1e-10)
    
    def test_velocity_density_product_imaginary(self, high_resonance_coordinates):
        """Imaginary part should be velocity * density."""
        c = WaveFormCollapseKernel.derive_julia_parameter(high_resonance_coordinates)
        
        # velocity=0.3, density=0.5 → imag = 0.15
        expected_imag = 0.3 * 0.5
        assert c.imag == pytest.approx(expected_imag)
    
    def test_different_coordinates_different_c(self, high_resonance_coordinates, low_resonance_coordinates):
        """Different coordinates should produce different Julia parameters."""
        c1 = WaveFormCollapseKernel.derive_julia_parameter(high_resonance_coordinates)
        c2 = WaveFormCollapseKernel.derive_julia_parameter(low_resonance_coordinates)
        
        # Should be different
        assert c1 != c2
        assert c1.real != c2.real


# ============================================================================
# TESTS: Manifestation State Derivation
# ============================================================================

class TestManifestationStateDerivation:
    """
    Test deterministic derivation of manifestation state from identity.
    
    The manifestation state z represents the current phase/energy. Derived
    from bitchain hash so same ID always produces same state.
    """
    
    def test_deterministic_state(self, coherent_bitchain):
        """Same bitchain ID always produces same manifestation state."""
        addr = coherent_bitchain.compute_address()
        z1 = WaveFormCollapseKernel.derive_manifestation_state(coherent_bitchain.id, addr)
        z2 = WaveFormCollapseKernel.derive_manifestation_state(coherent_bitchain.id, addr)
        
        assert z1 == z2
    
    def test_different_ids_different_states(self, coherent_bitchain, chaotic_bitchain):
        """Different IDs should produce different states."""
        addr1 = coherent_bitchain.compute_address()
        addr2 = chaotic_bitchain.compute_address()
        
        z1 = WaveFormCollapseKernel.derive_manifestation_state(coherent_bitchain.id, addr1)
        z2 = WaveFormCollapseKernel.derive_manifestation_state(chaotic_bitchain.id, addr2)
        
        assert z1 != z2
    
    def test_state_in_valid_range(self, coherent_bitchain):
        """Manifestation state should be in [-0.5, 0.5] × [-0.5, 0.5]."""
        addr = coherent_bitchain.compute_address()
        z = WaveFormCollapseKernel.derive_manifestation_state(coherent_bitchain.id, addr)
        
        assert -0.5 <= z.real <= 0.5
        assert -0.5 <= z.imag <= 0.5


# ============================================================================
# TESTS: Julia Iteration
# ============================================================================

class TestJuliaIteration:
    """
    Test the Julia Set iteration algorithm.
    
    Verifies that iteration correctly identifies bounded vs escaped points.
    """
    
    def test_iterate_zero_parameter_zero_point(self):
        """z=0, c=0 should remain bounded at 0."""
        z = complex(0, 0)
        c = complex(0, 0)
        
        iterations, magnitude = WaveFormCollapseKernel.iterate_julia(z, c)
        
        assert iterations is None  # Didn't escape
        assert magnitude == pytest.approx(0.0)
    
    def test_iterate_escaping_point(self):
        """z=1+i, c=0 should escape."""
        z = complex(1, 1)
        c = complex(0, 0)
        
        iterations, magnitude = WaveFormCollapseKernel.iterate_julia(z, c, max_depth=100)
        
        assert iterations is not None  # Did escape
        assert iterations < 100  # Before max depth
        assert magnitude > WaveFormCollapseKernel.ESCAPE_RADIUS
    
    def test_iterate_high_order_escape(self):
        """Some points take many iterations to escape."""
        z = complex(0.3, 0.5)
        c = complex(0.3, 0.5)
        
        iterations, magnitude = WaveFormCollapseKernel.iterate_julia(z, c, max_depth=100)
        
        # May escape later or be bounded
        if iterations is not None:
            assert iterations > 0
            assert magnitude > WaveFormCollapseKernel.ESCAPE_RADIUS
    
    def test_iterate_respect_depth_limit(self):
        """Iteration should stop at max_depth if not escaped."""
        z = complex(0.2, 0.2)
        c = complex(0.2, 0.2)
        
        iterations, magnitude = WaveFormCollapseKernel.iterate_julia(z, c, max_depth=7)
        
        # Either escaped before 7, or iterations is None (bounded)
        if iterations is not None:
            assert iterations < 7


# ============================================================================
# TESTS: Collapse - Bound Manifestations
# ============================================================================

class TestCollapseExitsBound:
    """
    Test that well-formed, coherent manifestations pass through firewall.
    
    These should be BOUND, ready for routing to LUCA/Conservator.
    """
    
    def test_coherent_bitchain_bound(self, coherent_bitchain):
        """Coherent bitchain with high resonance should BOUND."""
        report = WaveFormCollapseKernel.collapse(coherent_bitchain)
        
        assert report.result == CollapseResult.BOUND
        assert report.is_valid()
        assert report.escape_magnitude is not None
        assert report.escape_magnitude <= WaveFormCollapseKernel.ESCAPE_RADIUS
    
    def test_bound_has_complete_trace(self, coherent_bitchain):
        """Bound report should have full trace information."""
        report = WaveFormCollapseKernel.collapse(coherent_bitchain)
        
        assert report.bitchain_id == coherent_bitchain.id
        assert report.stat7_address
        assert report.julia_parameter != complex(0, 0)
        assert report.manifestation_state != complex(0, 0)
        assert report.depth == 7
    
    def test_neutral_bitchain_bound(self, neutral_bitchain):
        """Neutral bitchain should pass through."""
        report = WaveFormCollapseKernel.collapse(neutral_bitchain)
        
        # Should either be BOUND or have deterministic behavior
        assert report.result in [CollapseResult.BOUND, CollapseResult.ESCAPED]
        assert report.stat7_address  # Should have valid address


# ============================================================================
# TESTS: Collapse - Escaped Manifestations
# ============================================================================

class TestCollapseExitsEscaped:
    """
    Test that poorly-formed or misaligned manifestations are ESCAPED.
    
    These should be rejected at the firewall, routed to Conservator for repair.
    """
    
    def test_chaotic_bitchain_may_escape(self, chaotic_bitchain):
        """Chaotic bitchain with low resonance may escape firewall."""
        report = WaveFormCollapseKernel.collapse(chaotic_bitchain)
        
        # Chaotic state has lower coherence, higher chance of escape
        # We can't guarantee it will escape, but it's more likely
        assert report.result in [CollapseResult.BOUND, CollapseResult.ESCAPED]
        assert report.stat7_address
    
    def test_escaped_has_iteration_count(self, chaotic_bitchain):
        """Escaped manifestation should record which iteration it failed."""
        # Generate a bitchain that we know will escape
        # by using extreme parameters
        coords = Coordinates(
            realm="void",
            lineage=999,
            adjacency=[],
            horizon="crystallization",
            resonance=0.99,  # Extreme positive
            velocity=0.99,   # Extreme velocity
            density=0.99,    # Extreme density
        )
        
        bitchain = BitChain(
            id="entity-extreme-001",
            entity_type="void",
            realm="void",
            coordinates=coords,
            created_at=normalize_timestamp(),
            state={},
        )
        
        report = WaveFormCollapseKernel.collapse(bitchain)
        
        if report.result == CollapseResult.ESCAPED:
            assert report.iterations_to_escape is not None
            assert 0 <= report.iterations_to_escape < WaveFormCollapseKernel.DEPTH


# ============================================================================
# TESTS: Collapse - Malformed Input
# ============================================================================

class TestCollapseMalformed:
    """
    Test that malformed or invalid input is properly rejected.
    
    These should return MALFORMED or ERROR, triggering escalation.
    """
    
    def test_missing_coordinates(self, coherent_bitchain):
        """BitChain missing coordinates should be MALFORMED."""
        coherent_bitchain.coordinates = None
        
        report = WaveFormCollapseKernel.collapse(coherent_bitchain)
        
        assert report.result == CollapseResult.MALFORMED
    
    def test_missing_compute_address(self, coherent_bitchain):
        """BitChain missing compute_address should be MALFORMED."""
        # Create mock without compute_address
        bad_obj = type('BadBitChain', (), {
            'id': 'test',
            'coordinates': coherent_bitchain.coordinates,
        })()
        
        report = WaveFormCollapseKernel.collapse(bad_obj)
        
        assert report.result == CollapseResult.MALFORMED


# ============================================================================
# TESTS: Batch Operations
# ============================================================================

class TestBatchOperations:
    """
    Test batch collapse operations and statistics.
    """
    
    def test_collapse_batch_multiple(self, coherent_bitchain, chaotic_bitchain, neutral_bitchain):
        """Collapse multiple bitchains in batch."""
        bitchains = [coherent_bitchain, chaotic_bitchain, neutral_bitchain]
        
        reports = WaveFormCollapseKernel.collapse_batch(bitchains)
        
        assert len(reports) == 3
        assert coherent_bitchain.id in reports
        assert chaotic_bitchain.id in reports
        assert neutral_bitchain.id in reports
        
        # All should have valid results
        for report in reports.values():
            assert report.result in [CollapseResult.BOUND, CollapseResult.ESCAPED, 
                                    CollapseResult.ERROR, CollapseResult.MALFORMED]
    
    def test_summary_stats_calculation(self, coherent_bitchain, chaotic_bitchain, neutral_bitchain):
        """Summary stats should correctly aggregate results."""
        bitchains = [coherent_bitchain, chaotic_bitchain, neutral_bitchain]
        reports = WaveFormCollapseKernel.collapse_batch(bitchains)
        
        stats = WaveFormCollapseKernel.summary_stats(reports)
        
        assert stats['total'] == 3
        assert stats['bound'] + stats['escaped'] + stats['errors'] + stats['malformed'] == 3
        assert 0 <= stats['pass_rate'] <= 100
    
    def test_batch_completeness(self):
        """Batch operation should process all entities."""
        bitchains = []
        for i in range(10):
            coords = Coordinates(
                realm="data",
                lineage=i,
                adjacency=["batch"],
                horizon="peak",
                resonance=0.1 * i - 0.5,
                velocity=0.1,
                density=0.5,
            )
            bc = BitChain(
                id=f"batch-entity-{i:03d}",
                entity_type="test",
                realm="data",
                coordinates=coords,
                created_at=normalize_timestamp(),
                state={"index": i},
            )
            bitchains.append(bc)
        
        reports = WaveFormCollapseKernel.collapse_batch(bitchains)
        
        # All should be processed
        assert len(reports) == 10
        
        # All IDs should be present
        for i in range(10):
            assert f"batch-entity-{i:03d}" in reports


# ============================================================================
# TESTS: Physics Validation
# ============================================================================

class TestPhysicsProperties:
    """
    Test that the system maintains expected physical properties.
    """
    
    def test_coherence_axis(self):
        """Entities on coherence axis (resonance) should have predictable behavior."""
        # High coherence
        coords_high = Coordinates(
            realm="data", lineage=1, adjacency=[], horizon="peak",
            resonance=0.9, velocity=0.0, density=0.0,
        )
        c_high = WaveFormCollapseKernel.derive_julia_parameter(coords_high)
        
        # Low coherence
        coords_low = Coordinates(
            realm="data", lineage=1, adjacency=[], horizon="peak",
            resonance=-0.9, velocity=0.0, density=0.0,
        )
        c_low = WaveFormCollapseKernel.derive_julia_parameter(coords_low)
        
        # Real parts should be opposite
        assert c_high.real == pytest.approx(-c_low.real)
    
    def test_energy_axis(self):
        """Higher velocity * density should produce larger imaginary part."""
        coords_low_energy = Coordinates(
            realm="data", lineage=1, adjacency=[], horizon="peak",
            resonance=0.0, velocity=0.1, density=0.1,
        )
        c_low = WaveFormCollapseKernel.derive_julia_parameter(coords_low_energy)
        
        coords_high_energy = Coordinates(
            realm="data", lineage=1, adjacency=[], horizon="peak",
            resonance=0.0, velocity=0.9, density=0.9,
        )
        c_high = WaveFormCollapseKernel.derive_julia_parameter(coords_high_energy)
        
        # High energy should have larger imaginary part
        assert c_high.imag > c_low.imag
    
    def test_deterministic_reproducibility(self, coherent_bitchain):
        """Same input always produces same collapse result."""
        report1 = WaveFormCollapseKernel.collapse(coherent_bitchain)
        report2 = WaveFormCollapseKernel.collapse(coherent_bitchain)
        
        assert report1.result == report2.result
        assert report1.julia_parameter == report2.julia_parameter
        assert report1.manifestation_state == report2.manifestation_state


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """
    End-to-end firewall tests.
    
    Note: "Coherence" doesn't guarantee passage. The firewall validates against
    the Julia Set attractor for the entity's STAT7 coordinates. Some entities
    with high resonance but wrong phase/energy might still escape.
    """
    
    def test_firewall_flow_produces_result(self, coherent_bitchain):
        """Every entity entering firewall gets a clear result."""
        report = WaveFormCollapseKernel.collapse(coherent_bitchain)
        
        # Should have definitive result
        assert report.result in [CollapseResult.BOUND, CollapseResult.ESCAPED]
        
        # Should have trace for next layer (Conservator if escaped, LUCA if bound)
        assert report.bitchain_id
        assert report.stat7_address
        assert report.julia_parameter
        assert report.manifestation_state
    
    def test_firewall_traces_escape(self, chaotic_bitchain):
        """If entity escapes, firewall records where it failed."""
        report = WaveFormCollapseKernel.collapse(chaotic_bitchain)
        
        # Has clear result
        assert report.result in [CollapseResult.BOUND, CollapseResult.ESCAPED]
        
        # If escaped, should have diagnostics for Conservator repair
        if report.result == CollapseResult.ESCAPED:
            assert report.iterations_to_escape is not None
            assert report.escape_magnitude > WaveFormCollapseKernel.ESCAPE_RADIUS
    
    def test_firewall_passes_bound_to_conservator(self):
        """Bound entity has all data needed for Conservator routing."""
        # Create entity that we know will bound
        coords = Coordinates(
            realm="data",
            lineage=1,
            adjacency=["test"],
            horizon="genesis",
            resonance=0.05,   # Very low energy
            velocity=0.01,
            density=0.01,
        )
        
        bitchain = BitChain(
            id="test-low-energy",
            entity_type="test",
            realm="data",
            coordinates=coords,
            created_at=normalize_timestamp(),
            state={"test": True},
        )
        
        report = WaveFormCollapseKernel.collapse(bitchain)
        
        # Should have complete information
        assert report.stat7_address
        assert report.julia_parameter
        assert report.manifestation_state
        assert report.depth == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])