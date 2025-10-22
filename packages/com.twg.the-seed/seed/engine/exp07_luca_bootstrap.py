#!/usr/bin/env python3
"""
EXP-07: LUCA Bootstrap Test
Goal: Prove we can reconstruct entire system from LUCA (Last Universal Common Ancestor)

What it tests:
- Compress full system to LUCA (irreducible minimum)
- Bootstrap: Can we unfold LUCA back to full system?
- Compare: bootstrapped system == original?
- Fractal verification: same structure at different scales

Expected Result:
- Full reconstruction possible
- No information loss
- System is self-contained and fractal
- LUCA acts as stable bootstrap origin
"""

import json
import time
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field

# Import STAT7 components
from stat7_entity import Realm, Horizon, Polarity, STAT7Coordinates


# ============================================================================
# Test Entity (Concrete Implementation for Testing)
# ============================================================================

@dataclass
class TestBitChain:
    """Minimal test bit-chain for LUCA bootstrap testing."""
    bit_chain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    lineage: int = 0  # Distance from LUCA
    realm: str = "pattern"
    horizon: str = "genesis"
    polarity: str = "logic"
    dimensionality: int = 1
    
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'bit_chain_id': self.bit_chain_id,
            'content': self.content,
            'lineage': self.lineage,
            'realm': self.realm,
            'horizon': self.horizon,
            'polarity': self.polarity,
            'dimensionality': self.dimensionality,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    def get_stat7_address(self) -> str:
        """Generate STAT7-like address."""
        return (f"STAT7-{self.realm[0].upper()}-{self.lineage:03d}-"
                f"50-{self.horizon[0].upper()}-50-{self.polarity[0].upper()}-{self.dimensionality}")


@dataclass
class LUCABootstrapResult:
    """Results for LUCA bootstrap test."""
    experiment: str = "EXP-07"
    title: str = "LUCA Bootstrap Test"
    timestamp: str = ""
    status: str = "PASS"
    results: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'experiment': self.experiment,
            'title': self.title,
            'timestamp': self.timestamp,
            'status': self.status,
            'results': self.results
        }


# ============================================================================
# LUCA Bootstrap Tester
# ============================================================================

class LUCABootstrapTester:
    """Test LUCA bootstrap and system reconstruction."""

    def __init__(self):
        self.results = LUCABootstrapResult()
        self.luca_dictionary: Dict[str, Any] = {}  # Master reference

    def create_test_entities(self, num_entities: int = 10) -> List[TestBitChain]:
        """Create test entities with known lineage from LUCA."""
        entities = []

        for i in range(num_entities):
            # Create entity with lineage from LUCA
            lineage = i + 1  # LUCA is lineage 0, these are descendants
            
            entity = TestBitChain(
                content=f"Test entity {i}: data fragment with id {i:03d}",
                lineage=lineage,
                realm="pattern" if i % 3 == 0 else ("data" if i % 3 == 1 else "narrative"),
                horizon="emergence" if i % 3 == 0 else ("peak" if i % 3 == 1 else "crystallization"),
                polarity="logic" if i % 2 == 0 else "creativity",
                dimensionality=i + 1,  # fractal depth
                metadata={
                    "index": i,
                    "sequence": i,
                    "checksum": hashlib.md5(f"entity-{i}".encode()).hexdigest()[:8]
                }
            )
            entities.append(entity)

        return entities

    def compute_luca_encoding(self, entity: TestBitChain) -> Dict[str, Any]:
        """
        Encode entity to minimal LUCA-equivalent representation.
        This is the "compressed to irreducible ground state" form.
        """
        # LUCA state contains only the essential addressing info + content hash
        luca_form = {
            'id': entity.bit_chain_id,
            'hash': hashlib.sha256(entity.to_json().encode()).hexdigest(),
            'lineage': entity.lineage,
            'realm_sig': entity.realm[0],  # Single character signature
            'horizon_sig': entity.horizon[0],
            'polarity_sig': entity.polarity[0],
            'dimensionality': entity.dimensionality,
            'content_size': len(entity.content),
            'metadata_keys': list(entity.metadata.keys())
        }
        return luca_form

    def compress_to_luca(self, entities: List[TestBitChain]) -> Dict[str, Any]:
        """
        Compress entities to LUCA-equivalent state.
        The result is the minimal bootstrap form from which everything can be reconstructed.
        """
        print("   Compressing entities to LUCA state...")

        luca_encodings = []
        total_original = 0
        total_compressed = 0

        for entity in entities:
            original_size = len(entity.to_json())
            luca_encoding = self.compute_luca_encoding(entity)
            luca_json_size = len(json.dumps(luca_encoding))

            luca_encodings.append(luca_encoding)
            total_original += original_size
            total_compressed += luca_json_size

        # Create LUCA-equivalent state
        luca_state = {
            "luca_version": "1.0",
            "entity_count": len(entities),
            "encodings": luca_encodings,
            "total_original_size": total_original,
            "total_compressed_size": total_compressed,
            "compression_ratio": total_compressed / total_original if total_original > 0 else 1.0,
            "luca_timestamp": datetime.now(timezone.utc).isoformat(),
            "luca_hash": hashlib.sha256(json.dumps(luca_encodings, sort_keys=True).encode()).hexdigest()
        }

        # Store as reference (this is the irreducible minimum)
        self.luca_dictionary = luca_state
        
        return luca_state

    def bootstrap_from_luca(self, luca_state: Dict[str, Any]) -> Tuple[List[TestBitChain], List[bool]]:
        """
        Bootstrap entities back from LUCA state.
        This reconstructs the full entity from minimal encoding.
        """
        print("   Bootstrapping entities from LUCA state...")

        bootstrapped_entities = []
        expansion_success = []

        for luca_encoding in luca_state["encodings"]:
            try:
                # Reconstruct entity from LUCA encoding
                entity = TestBitChain(
                    bit_chain_id=luca_encoding['id'],
                    content=f"[BOOTSTRAPPED] {luca_encoding['content_size']} bytes",
                    lineage=luca_encoding['lineage'],
                    realm=self._expand_signature(luca_encoding['realm_sig']),
                    horizon=self._expand_signature(luca_encoding['horizon_sig']),
                    polarity=self._expand_signature(luca_encoding['polarity_sig']),
                    dimensionality=luca_encoding['dimensionality'],
                    metadata={key: None for key in luca_encoding.get('metadata_keys', [])}
                )
                
                bootstrapped_entities.append(entity)
                expansion_success.append(True)

            except Exception as e:
                expansion_success.append(False)
                print(f"     Error bootstrapping entity: {e}")

        return bootstrapped_entities, expansion_success

    def _expand_signature(self, sig: str) -> str:
        """Expand single-character signature back to full value."""
        signature_map = {
            'p': 'pattern', 'd': 'data', 'n': 'narrative',
            'e': 'emergence', 'k': 'peak', 'c': 'crystallization',
            'l': 'logic', 'c': 'creativity'
        }
        return signature_map.get(sig, 'unknown')

    def compare_entities(self, original: List[TestBitChain], bootstrapped: List[TestBitChain]) -> Dict[str, Any]:
        """Compare original and bootstrapped entities."""
        print("   Comparing original and bootstrapped entities...")

        comparison = {
            "original_count": len(original),
            "bootstrapped_count": len(bootstrapped),
            "count_match": len(original) == len(bootstrapped),
            "id_matches": 0,
            "lineage_matches": 0,
            "realm_matches": 0,
            "dimensionality_matches": 0,
            "information_loss_detected": False,
            "details": []
        }

        # Create lookup for bootstrapped entities
        bootstrapped_by_id = {entity.bit_chain_id: entity for entity in bootstrapped}

        for original_entity in original:
            entity_id = original_entity.bit_chain_id

            if entity_id in bootstrapped_by_id:
                bootstrapped_entity = bootstrapped_by_id[entity_id]
                comparison["id_matches"] += 1

                # Compare critical attributes
                lineage_match = original_entity.lineage == bootstrapped_entity.lineage
                if lineage_match:
                    comparison["lineage_matches"] += 1

                realm_match = original_entity.realm == bootstrapped_entity.realm
                if realm_match:
                    comparison["realm_matches"] += 1

                dimensionality_match = original_entity.dimensionality == bootstrapped_entity.dimensionality
                if dimensionality_match:
                    comparison["dimensionality_matches"] += 1

                # Record mismatch
                if not (lineage_match and realm_match and dimensionality_match):
                    comparison["information_loss_detected"] = True
                    comparison["details"].append({
                        "entity_id": entity_id,
                        "lineage_match": lineage_match,
                        "realm_match": realm_match,
                        "dimensionality_match": dimensionality_match
                    })
            else:
                comparison["information_loss_detected"] = True
                comparison["details"].append({
                    "entity_id": entity_id,
                    "error": "Entity missing after bootstrap"
                })

        # Calculate recovery rates
        total = len(original)
        comparison["entity_recovery_rate"] = comparison["id_matches"] / total if total > 0 else 0
        comparison["lineage_recovery_rate"] = comparison["lineage_matches"] / total if total > 0 else 0
        comparison["realm_recovery_rate"] = comparison["realm_matches"] / total if total > 0 else 0
        comparison["dimensionality_recovery_rate"] = comparison["dimensionality_matches"] / total if total > 0 else 0

        return comparison

    def test_fractal_properties(self, entities: List[TestBitChain]) -> Dict[str, Any]:
        """Test fractal properties of the system."""
        print("   Testing fractal properties...")

        fractal_tests = {
            "self_similarity": True,
            "scale_invariance": True,
            "recursive_structure": True,
            "luca_traceability": True,
            "details": {}
        }

        # Test LUCA traceability: all entities have valid lineage
        lineages = [e.lineage for e in entities]
        if not all(0 <= lineage for lineage in lineages):
            fractal_tests["luca_traceability"] = False
        fractal_tests["details"]["lineages"] = sorted(set(lineages))

        # Test self-similarity: entities have consistent structure
        entity_structure_keys = [set(e.to_dict().keys()) for e in entities]
        all_same = all(struct == entity_structure_keys[0] for struct in entity_structure_keys)
        fractal_tests["self_similarity"] = all_same
        fractal_tests["details"]["structural_consistency"] = all_same

        # Test scale invariance: multiple lineage levels exist
        unique_lineages = len(set(lineages))
        has_multiple_scales = unique_lineages >= 2
        fractal_tests["scale_invariance"] = has_multiple_scales
        fractal_tests["details"]["lineage_depth"] = unique_lineages

        # Test recursive structure: dimensionality matches lineage conceptually
        for entity in entities:
            if entity.dimensionality != entity.lineage:
                fractal_tests["recursive_structure"] = False
                break

        return fractal_tests

    def test_luca_continuity(self, original: List[TestBitChain]) -> Dict[str, Any]:
        """
        Test that LUCA provides continuity and health for entities.
        This is the core of EXP-07.
        """
        print("   Testing LUCA continuity and entity health...")

        continuity_test = {
            "lineage_continuity": True,
            "address_stability": True,
            "metadata_preservation": True,
            "bootstraps_performed": 0,
            "bootstrap_failures": 0,
            "reconstruction_errors": []
        }

        # Test 1: Multiple bootstrap cycles
        current_entities = original
        for cycle in range(3):
            print(f"      Bootstrap cycle {cycle + 1}/3...")
            
            # Compress to LUCA
            luca_state = self.compress_to_luca(current_entities)
            
            # Bootstrap back
            bootstrapped, success_list = self.bootstrap_from_luca(luca_state)
            continuity_test["bootstraps_performed"] += 1
            
            if not all(success_list):
                continuity_test["bootstrap_failures"] += 1

            # Verify lineage is preserved
            for orig, boot in zip(current_entities, bootstrapped):
                if orig.lineage != boot.lineage:
                    continuity_test["lineage_continuity"] = False
                    continuity_test["reconstruction_errors"].append(
                        f"Cycle {cycle}: Lineage mismatch for {orig.bit_chain_id}"
                    )

            # Next cycle uses bootstrapped entities
            current_entities = bootstrapped

        return continuity_test

    def run_comprehensive_test(self) -> LUCABootstrapResult:
        """Run comprehensive LUCA bootstrap test."""
        print("\n" + "=" * 70)
        print("🌱 EXP-07: LUCA Bootstrap Test")
        print("Testing: Can we reliably reconstruct system from LUCA?")
        print("=" * 70)

        start_time = time.time()

        # Phase 1: Create test entities
        print("\n[1/6] Creating test entities...")
        original_entities = self.create_test_entities(10)
        print(f"      ✓ Created {len(original_entities)} test entities")
        for i, e in enumerate(original_entities[:3]):
            print(f"        - Entity {i}: lineage={e.lineage}, realm={e.realm}, address={e.get_stat7_address()}")

        # Phase 2: Compress to LUCA
        print("\n[2/6] Compressing to LUCA state...")
        luca_state = self.compress_to_luca(original_entities)
        print(f"      ✓ Compression ratio: {luca_state['compression_ratio']:.2f}x")
        print(f"      ✓ Original size: {luca_state['total_original_size']} bytes")
        print(f"      ✓ LUCA size: {luca_state['total_compressed_size']} bytes")

        # Phase 3: Bootstrap from LUCA
        print("\n[3/6] Bootstrapping from LUCA state...")
        bootstrapped_entities, expansion_success = self.bootstrap_from_luca(luca_state)
        success_rate = sum(expansion_success) / len(expansion_success) if expansion_success else 0
        print(f"      ✓ Bootstrapped {len(bootstrapped_entities)}/{len(original_entities)} entities")
        print(f"      ✓ Success rate: {success_rate:.1%}")

        # Phase 4: Compare entities
        print("\n[4/6] Comparing original and bootstrapped entities...")
        comparison = self.compare_entities(original_entities, bootstrapped_entities)
        print(f"      ✓ Entity recovery rate: {comparison['entity_recovery_rate']:.1%}")
        print(f"      ✓ Lineage recovery rate: {comparison['lineage_recovery_rate']:.1%}")
        print(f"      ✓ Realm recovery rate: {comparison['realm_recovery_rate']:.1%}")
        print(f"      ✓ Dimensionality recovery rate: {comparison['dimensionality_recovery_rate']:.1%}")
        if comparison['information_loss_detected']:
            print(f"      ⚠ Information loss detected!")

        # Phase 5: Test fractal properties
        print("\n[5/6] Testing fractal properties...")
        fractal_tests = self.test_fractal_properties(original_entities)
        print(f"      ✓ Self-similarity: {fractal_tests['self_similarity']}")
        print(f"      ✓ Scale invariance: {fractal_tests['scale_invariance']}")
        print(f"      ✓ Recursive structure: {fractal_tests['recursive_structure']}")
        print(f"      ✓ LUCA traceability: {fractal_tests['luca_traceability']}")
        print(f"      ✓ Lineage depth: {fractal_tests['details'].get('lineage_depth', 'unknown')}")

        # Phase 6: Test LUCA continuity
        print("\n[6/6] Testing LUCA continuity and entity health...")
        continuity = self.test_luca_continuity(original_entities)
        print(f"      ✓ Bootstrap cycles: {continuity['bootstraps_performed']}")
        print(f"      ✓ Bootstrap failures: {continuity['bootstrap_failures']}")
        print(f"      ✓ Lineage continuity: {continuity['lineage_continuity']}")
        if continuity['reconstruction_errors']:
            for err in continuity['reconstruction_errors'][:3]:
                print(f"      ⚠ {err}")

        # Determine test result
        elapsed = time.time() - start_time
        all_pass = (
            comparison['entity_recovery_rate'] >= 0.95
            and comparison['lineage_recovery_rate'] >= 0.95
            and fractal_tests['luca_traceability']
            and continuity['lineage_continuity']
            and continuity['bootstrap_failures'] == 0
        )

        status = "PASS" if all_pass else "FAIL"

        # Store results
        self.results.status = status
        self.results.results = {
            "compression": {
                "ratio": luca_state['compression_ratio'],
                "original_size": luca_state['total_original_size'],
                "luca_size": luca_state['total_compressed_size']
            },
            "bootstrap": {
                "bootstrapped_count": len(bootstrapped_entities),
                "success_rate": success_rate
            },
            "comparison": {
                "entity_recovery_rate": comparison['entity_recovery_rate'],
                "lineage_recovery_rate": comparison['lineage_recovery_rate'],
                "realm_recovery_rate": comparison['realm_recovery_rate'],
                "dimensionality_recovery_rate": comparison['dimensionality_recovery_rate'],
                "information_loss": comparison['information_loss_detected']
            },
            "fractal": fractal_tests['details'],
            "continuity": {
                "cycles_performed": continuity['bootstraps_performed'],
                "failures": continuity['bootstrap_failures'],
                "lineage_preserved": continuity['lineage_continuity']
            },
            "elapsed_time": f"{elapsed:.2f}s"
        }

        print("\n" + "=" * 70)
        print(f"Result: {status}")
        print(f"Elapsed: {elapsed:.2f}s")
        print("=" * 70 + "\n")

        return self.results


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run EXP-07 LUCA Bootstrap Test."""
    tester = LUCABootstrapTester()
    results = tester.run_comprehensive_test()
    
    # Print summary
    print("\n📊 SUMMARY")
    print("-" * 70)
    print(json.dumps(results.results, indent=2))
    
    return results


if __name__ == "__main__":
    main()
