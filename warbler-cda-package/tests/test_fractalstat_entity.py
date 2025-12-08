# pylint: disable=import-outside-toplevel, protected-access, missing-function-docstring, missing-class-docstring
"""
Comprehensive unit tests for fractalstat_entity.py core module
"""

import json
from datetime import datetime
from pathlib import Path
import tempfile
import pytest
import torch



class TestRealmEnum:
    """Test Realm enum values and behavior."""

    def test_realm_enum_values(self):
        """Realm enum should have all expected values."""
        from warbler_cda.fractalstat_entity import Realm

        assert Realm.COMPANION.value == "companion"
        assert Realm.BADGE.value == "badge"
        assert Realm.SPONSOR_RING.value == "sponsor_ring"
        assert Realm.ACHIEVEMENT.value == "achievement"
        assert Realm.PATTERN.value == "pattern"
        assert Realm.FACULTY.value == "faculty"
        assert Realm.VOID.value == "void"

    def test_realm_enum_membership(self):
        """Realm enum should support membership testing."""
        from warbler_cda.fractalstat_entity import Realm

        assert Realm.COMPANION in Realm
        assert Realm.BADGE in Realm

    def test_realm_enum_iteration(self):
        """Realm enum should be iterable."""
        from warbler_cda.fractalstat_entity import Realm

        realms = list(Realm)
        assert len(realms) == 8
        assert Realm.COMPANION in realms


class TestHorizonEnum:
    """Test Horizon enum values and behavior."""

    def test_horizon_enum_values(self):
        """Horizon enum should have all lifecycle stages."""
        from warbler_cda.fractalstat_entity import Horizon

        assert Horizon.GENESIS.value == "genesis"
        assert Horizon.EMERGENCE.value == "emergence"
        assert Horizon.PEAK.value == "peak"
        assert Horizon.DECAY.value == "decay"
        assert Horizon.CRYSTALLIZATION.value == "crystallization"
        assert Horizon.ARCHIVED.value == "archived"

    def test_horizon_enum_count(self):
        """Horizon enum should have exactly 6 stages."""
        from warbler_cda.fractalstat_entity import Horizon

        assert len(list(Horizon)) == 6


class TestPolarityEnum:
    """Test Polarity enum values and behavior."""

    def test_polarity_companion_values(self):
        """Polarity should have companion elemental values."""
        from warbler_cda.fractalstat_entity import Polarity

        assert Polarity.LOGIC.value == "logic"
        assert Polarity.CREATIVITY.value == "creativity"
        assert Polarity.ORDER.value == "order"
        assert Polarity.CHAOS.value == "chaos"
        assert Polarity.BALANCE.value == "balance"

    def test_polarity_badge_values(self):
        """Polarity should have badge category values."""
        from warbler_cda.fractalstat_entity import Polarity

        assert Polarity.ACHIEVEMENT.value == "achievement"
        assert Polarity.CONTRIBUTION.value == "contribution"
        assert Polarity.COMMUNITY.value == "community"
        assert Polarity.TECHNICAL.value == "technical"
        assert Polarity.CREATIVE.value == "creative"
        assert Polarity.UNITY.value == "unity"

    def test_polarity_neutral_value(self):
        """Polarity should have void neutral value."""
        from warbler_cda.fractalstat_entity import Polarity

        assert Polarity.VOID.value == "void"


class TestAlignmentEnum:
    """Test Alignment enum values and behavior."""

    def test_alignment_lawful_good_values(self):
        """Alignment should have lawful good values."""
        from warbler_cda.fractalstat_entity import Alignment

        assert Alignment.LAWFUL_GOOD.value == "lawful_good"
        assert Alignment.NEUTRAL_GOOD.value == "neutral_good"
        assert Alignment.CHAOTIC_GOOD.value == "chaotic_good"

    def test_alignment_lawful_neutral_values(self):
        """Alignment should have lawful neutral values."""
        from warbler_cda.fractalstat_entity import Alignment

        assert Alignment.LAWFUL_NEUTRAL.value == "lawful_neutral"
        assert Alignment.TRUE_NEUTRAL.value == "true_neutral"
        assert Alignment.CHAOTIC_NEUTRAL.value == "chaotic_neutral"

    def test_alignment_lawful_evil_values(self):
        """Alignment should have lawful evil values."""
        from warbler_cda.fractalstat_entity import Alignment

        assert Alignment.LAWFUL_EVIL.value == "lawful_evil"
        assert Alignment.NEUTRAL_EVIL.value == "neutral_evil"
        assert Alignment.CHAOTIC_EVIL.value == "chaotic_evil"

    def test_alignment_special_values(self):
        """Alignment should have special FractalStat values."""
        from warbler_cda.fractalstat_entity import Alignment

        assert Alignment.HARMONIC.value == "harmonic"
        assert Alignment.ENTROPIC.value == "entropic"
        assert Alignment.SYMBIOTIC.value == "symbiotic"


class TestFractalStatCoordinates:
    """Test FractalStatCoordinates dataclass."""

    def test_coordinates_initialization(self):
        """FractalStatCoordinates should initialize with all dimensions."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        coords = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=5,
            adjacency=75.5,
            horizon=Horizon.PEAK,
            luminosity=90.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.TRUE_NEUTRAL,
        )

        assert coords.realm == Realm.COMPANION
        assert coords.lineage == 5
        assert coords.adjacency == 75.5
        assert coords.horizon == Horizon.PEAK
        assert coords.luminosity == 90.0
        assert coords.polarity == Polarity.LOGIC
        assert coords.dimensionality == 3
        assert coords.alignment == Alignment.TRUE_NEUTRAL

    def test_coordinates_address_generation(self):
        """address property should generate canonical FractalStat address."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        coords = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=5,
            adjacency=75.5,
            horizon=Horizon.PEAK,
            luminosity=90.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.LAWFUL_GOOD,
        )

        address = coords.address
        assert address == "FractalStat-C-005-75-P-90-L-3-L"

    def test_coordinates_address_format(self):
        """address should follow FractalStat-R-LLL-AA-H-LL-P-D-A format."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        coords = FractalStatCoordinates(
            realm=Realm.BADGE,
            lineage=0,
            adjacency=0.0,
            horizon=Horizon.GENESIS,
            luminosity=0.0,
            polarity=Polarity.ACHIEVEMENT,
            dimensionality=0,
            alignment=Alignment.LAWFUL_GOOD,
        )

        address = coords.address
        parts = address.split("-")

        assert len(parts) == 9
        assert parts[0] == "FractalStat"
        assert parts[1] == "B"
        assert parts[2] == "000"
        assert parts[3] == "00"
        assert parts[4] == "G"
        assert parts[5] == "00" # I noticed this was "00", not "90" as previously written below
        assert parts[6] == "A"
        assert parts[7] == "0"
        assert parts[8] == "L"

    def test_coordinates_from_address_valid(self):
        """from_address should parse valid FractalStat address."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        address = "FractalStat-C-005-75-P-00-L-3-T"
        coords = FractalStatCoordinates.from_address(address)

        assert coords.realm == Realm.COMPANION
        assert coords.lineage == 5
        assert coords.adjacency == 75.0
        assert coords.horizon == Horizon.PEAK
        assert coords.luminosity == 00.0 # I corrected this line from "90" to "00" as per the address above
        assert coords.polarity == Polarity.LOGIC
        assert coords.dimensionality == 3
        assert coords.alignment == Alignment.TRUE_NEUTRAL

    def test_coordinates_from_address_invalid_prefix(self):
        """from_address should raise ValueError for invalid prefix."""
        from warbler_cda.fractalstat_entity import FractalStatCoordinates

        with pytest.raises(ValueError, match="Invalid FractalStat address"):
            FractalStatCoordinates.from_address("INVALID-C-005-75-P-90-L-3")

    def test_coordinates_from_address_invalid_parts(self):
        """from_address should raise ValueError for wrong number of parts."""
        from warbler_cda.fractalstat_entity import FractalStatCoordinates

        with pytest.raises(ValueError, match="Invalid FractalStat address"):
            FractalStatCoordinates.from_address("FractalStat-C-005")


    def test_coordinates_from_address_non_zero_values(self):
        from warbler_cda.fractalstat_entity import (FractalStatCoordinates,
                                                    Realm, Horizon, Polarity, Alignment)
        import pytest

        # Valid case
        address = "FractalStat-P-010-33-E-66-V-1-H"
        coords = FractalStatCoordinates.from_address(address)
        assert coords.realm == Realm.PATTERN
        assert coords.lineage == 10
        assert coords.adjacency == 33.0
        assert coords.horizon == Horizon.EMERGENCE
        assert coords.luminosity == 66.0
        assert coords.polarity == Polarity.VOID
        assert coords.dimensionality == 1
        assert coords.alignment == Alignment.HARMONIC

        # Invalid cases
        with pytest.raises(ValueError, match="Invalid FractalStat address"):
            FractalStatCoordinates.from_address("FractalStat-X-abc-33-E-66-V-1-H")

        with pytest.raises(ValueError, match="Invalid FractalStat address"):
            FractalStatCoordinates.from_address("FractalStat-P-010-33-E-66-V-1-Z")

        with pytest.raises(ValueError, match="Invalid FractalStat address"):
            FractalStatCoordinates.from_address("FractalStat-P-010-33-E-66-V-1")

    def test_coordinates_roundtrip(self):
        """Coordinates should survive address roundtrip."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        original = FractalStatCoordinates(
            realm=Realm.SPONSOR_RING,
            lineage=10,
            adjacency=50.0,
            horizon=Horizon.CRYSTALLIZATION,
            luminosity=100.0,
            polarity=Polarity.UNITY,
            dimensionality=7,
            alignment=Alignment.LAWFUL_GOOD,
        )

        address = original.address
        restored = FractalStatCoordinates.from_address(address)

        assert restored.realm == original.realm
        assert restored.lineage == original.lineage
        assert restored.adjacency == original.adjacency
        assert restored.horizon == original.horizon
        assert restored.luminosity == original.luminosity
        assert restored.polarity == original.polarity
        assert restored.dimensionality == original.dimensionality

    def test_coordinates_to_dict(self):
        """to_dict should convert coordinates to dictionary."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        coords = FractalStatCoordinates(
            realm=Realm.PATTERN,
            lineage=2,
            adjacency=33.3,
            horizon=Horizon.EMERGENCE,
            luminosity=66.6,
            polarity=Polarity.CHAOS,
            dimensionality=1,
            alignment=Alignment.LAWFUL_GOOD,
        )

        data = coords.to_dict()

        assert data["realm"] == "pattern"
        assert data["lineage"] == 2
        assert data["adjacency"] == 33.3
        assert data["horizon"] == "emergence"
        assert data["luminosity"] == 66.6
        assert data["polarity"] == "chaos"
        assert data["dimensionality"] == 1
        assert "address" in data


class TestLifecycleEvent:
    """Test LifecycleEvent dataclass."""

    def test_lifecycle_event_initialization(self):
        """LifecycleEvent should initialize with required fields."""
        from warbler_cda.fractalstat_entity import LifecycleEvent

        timestamp = datetime.now()
        event = LifecycleEvent(
            timestamp=timestamp,
            event_type="birth",
            description="Entity created",
        )

        assert event.timestamp == timestamp
        assert event.event_type == "birth"
        assert event.description == "Entity created"
        assert event.metadata == {}

    def test_lifecycle_event_with_metadata(self):
        """LifecycleEvent should accept metadata."""
        from warbler_cda.fractalstat_entity import LifecycleEvent

        metadata = {"key": "value", "count": 42}
        event = LifecycleEvent(
            timestamp=datetime.now(),
            event_type="evolution",
            description="Entity evolved",
            metadata=metadata,
        )

        assert event.metadata == metadata

    def test_lifecycle_event_to_dict(self):
        """to_dict should convert event to dictionary."""
        from warbler_cda.fractalstat_entity import LifecycleEvent

        timestamp = datetime(2025, 1, 1, 12, 0, 0)
        event = LifecycleEvent(
            timestamp=timestamp,
            event_type="mint",
            description="NFT minted",
            metadata={"token_id": 123},
        )

        data = event.to_dict()

        assert data["timestamp"] == timestamp.isoformat()
        assert data["event_type"] == "mint"
        assert data["description"] == "NFT minted"
        assert data["metadata"]["token_id"] == 123


class TestFractalStatEntityBase:
    """Test FractalStatEntity abstract base class."""

    def create_concrete_entity(self):
        """Helper to create a concrete FractalStatEntity subclass."""
        from warbler_cda.fractalstat_entity import (
            FractalStatEntity,
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        class ConcreteEntity(FractalStatEntity):
            def _compute_fractalstat_coordinates(self):
                return FractalStatCoordinates(
                    realm=Realm.COMPANION,
                    lineage=0,
                    adjacency=0.0,
                    horizon=Horizon.GENESIS,
                    luminosity=0.0,
                    polarity=Polarity.BALANCE,
                    dimensionality=0,
                    alignment=Alignment.TRUE_NEUTRAL
                )

            def to_collectible_card_data(self):
                return {
                    "title": "Test Entity",
                    "fluff_text": "Test description",
                    "icon_url": "http://example.com/icon.png",
                    "artwork_url": "http://example.com/art.png",
                    "rarity": "common",
                    "key_stats": {"stat1": 10},
                    "properties": {"prop1": "value1"},
                }

            def validate_hybrid_encoding(self):
                return (True, "Valid")

            def get_luca_trace(self):
                return {
                    "entity_id": self.entity_id,
                    "luca_distance": self.luca_distance,
                    "realm": self.fractalstat.realm.value,
                    "lineage": self.fractalstat.lineage,
                    "created_at": self.created_at.isoformat(),
                    "migration_source": self.migration_source,
                    "event_count": len(self.lifecycle_events),
                }

        return ConcreteEntity

    def test_entity_default_initialization(self):
        """FractalStatEntity should initialize with default values."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        assert entity.entity_id is not None
        assert len(entity.entity_id) > 0
        assert entity.entity_type == ""
        assert entity.fractalstat is not None
        assert entity.legacy_data == {}
        assert entity.migration_source is None
        assert entity.nft_minted is False
        assert entity.nft_contract is None
        assert entity.nft_token_id is None
        assert entity.nft_metadata_ipfs is None
        assert entity.entangled_entities == []
        assert entity.entanglement_strength == []
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.last_activity, datetime)
        assert len(entity.lifecycle_events) >= 1
        assert entity.owner_id == ""
        # assert entity.opt_in_fractalstat_nft is True
        assert entity.opt_in_blockchain is False
        assert entity.preferred_zoom_level == 1

    def test_entity_luca_distance_and_trace(self):
        """FractalStatEntity should expose LUCA distance and trace.""" 
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        # Manually set fractalstat lineage
        from warbler_cda.fractalstat_entity import FractalStatCoordinates
        from warbler_cda.fractalstat_entity import Realm, Horizon, Polarity, Alignment

        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=7,
            adjacency=50.0,
            horizon=Horizon.PEAK,
            luminosity=80.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.TRUE_NEUTRAL,
        )

        assert entity.luca_distance == 7

        trace = entity.get_luca_trace()
        assert trace["entity_id"] == entity.entity_id
        assert trace["luca_distance"] == 7
        assert trace["realm"] == "companion"
        assert trace["lineage"] == 7
        assert trace["event_count"] == len(entity.lifecycle_events)

    def test_entity_luca_distance_error_when_missing_fractalstat(self):
        """luca_distance should raise error when fractalstat missing."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = None

        with pytest.raises(ValueError, match="fractalstat coordinates must be initialized"):
            _ = entity.luca_distance

    def test_entity_prepare_for_minting_success(self):
        """prepare_for_minting should generate NFT metadata when opted in."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.entity_type = "TestEntity"

        nft_data = entity.prepare_for_minting()

        assert nft_data["name"] == "Test Entity"
        assert nft_data["description"] == "Test description"
        assert nft_data["external_url"].endswith(entity.entity_id)
        traits = {t["trait_type"]: t["value"] for t in nft_data["attributes"]}
        assert traits["Entity Type"] == "TestEntity"
        assert "FractalStat Address" in traits

    def test_entity_prepare_for_minting_opt_out(self):
        """prepare_for_minting should raise if entity not opted into NFTs.""" 
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.opt_in_fractalstat_nft = False

        with pytest.raises(ValueError, match="Entity not opted in to FractalStat-NFT system"):
            entity.prepare_for_minting()

    def test_entity_record_mint_updates_state(self):
        """record_mint should update NFT fields and record event."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        initial_events = len(entity.lifecycle_events)
        entity.record_mint("0xABCDEF", 123, "QmHash")

        assert entity.nft_minted is True
        assert entity.nft_contract == "0xABCDEF"
        assert entity.nft_token_id == 123
        assert entity.nft_metadata_ipfs == "QmHash"
        assert len(entity.lifecycle_events) == initial_events + 1
        assert entity.lifecycle_events[-1].event_type == "nft_minted"

    def test_entity_alignment_details(self):
        """_get_alignment_details should return coordination and social dynamics.""" 
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=1,
            adjacency=50.0,
            horizon=Horizon.PEAK,
            luminosity=80.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.HARMONIC,
        )
        entity.add_entanglement("other-1", 0.8)

        details = entity._get_alignment_details() # pylint: disable=protected-access
        assert details["alignment"] == Alignment.HARMONIC.value
        assert details["coordination_style"] == "naturally_coordinating"
        assert "social_dynamics" in details
        assert details["social_dynamics"]["social_pattern"] == "coordinating_harmonious"

    def test_entity_calculate_coordination_potential(self):
        """_calculate_coordination_potential should respect alignment modifiers.""" 
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=1,
            adjacency=50.0,
            horizon=Horizon.PEAK,
            luminosity=80.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.HARMONIC,
        )
        # Add multiple entanglements
        entity.add_entanglement("e1", 0.5)
        entity.add_entanglement("e2", 0.5)
        potential = entity._calculate_coordination_potential() # pylint: disable=W0212

        assert 0.0 <= potential <= 1.0
        # With 2 entanglements and harmonic bonus, should be > 0.2
        assert potential > 0.2

    def test_bitchain_coordinates_to_dict(self):
        """Coordinates.to_dict should normalize and sort adjacency.""" 
        from warbler_cda.fractalstat_entity import Coordinates, Alignment, Polarity

        coords = Coordinates(
            realm="data",
            lineage=1,
            adjacency=["b", "a"],
            horizon="genesis",
            luminosity=12.3456789,
            polarity=Polarity.LOGIC,
            dimensionality=2,
            alignment=Alignment.LAWFUL_GOOD,
        )

        data = coords.to_dict()
        assert data["adjacency"] == ["a", "b"]
        assert data["luminosity"].startswith("12.")
        assert data["polarity"] == "LOGIC"
        assert data["alignment"] == "LAWFUL_GOOD"

    def test_bitchain_compute_address_and_uri(self):
        """BitChain should compute deterministic address and URI.""" 
        from warbler_cda.fractalstat_entity import BitChain, Coordinates, Alignment, Polarity

        coords = Coordinates(
            realm="data",
            lineage=1,
            adjacency=["id1", "id2"],
            horizon="genesis",
            luminosity=42.0,
            polarity=Polarity.LOGIC,
            dimensionality=2,
            alignment=Alignment.TRUE_NEUTRAL,
        )

        bitchain = BitChain(
            id="test-id",
            entity_type="concept",
            realm="data",
            coordinates=coords,
            created_at="2024-01-01T00:00:00.000Z",
            state={"value": 1},
        )

        address1 = bitchain.compute_address()
        address2 = bitchain.compute_address()
        assert address1 == address2

        uri = bitchain.get_fractalstat_uri()
        assert uri.startswith("fractalstat://data/1/")
        assert "r=" in uri
        assert "&p=LOGIC" in uri
        assert "&d=2" in uri
        assert "&s=test-id" in uri
        assert "&a=TRUE_NEUTRAL" in uri

    def test_normalize_float_and_timestamp_helpers(self):
        """Helper functions normalize_float and normalize_timestamp should behave as expected.""" 
        from warbler_cda.fractalstat_entity import normalize_float, normalize_timestamp
        from datetime import datetime  # noqa: F401, pylint: disable=W0621 W0404 C0415 W0611

        assert normalize_float(1.234567891) == "1.23456789"
        assert normalize_float(1.0) == "1.0"

        # Timestamp now
        ts_now = normalize_timestamp()
        assert ts_now.endswith("Z")

        # Specific timestamp
        iso_ts = "2024-01-01T00:00:00Z"
        norm_ts = normalize_timestamp(iso_ts)
        assert norm_ts.startswith("2024-01-01T00:00:00")
        assert norm_ts.endswith("Z")

    def test_compute_address_hash_and_sort_json_keys(self):
        """compute_address_hash and sort_json_keys should be deterministic.""" 
        from warbler_cda.fractalstat_entity import compute_address_hash, sort_json_keys

        data1 = {"b": 2, "a": {"y": 2, "x": 1}}
        data2 = {"a": {"x": 1, "y": 2}, "b": 2}

        assert sort_json_keys(data1) == sort_json_keys(data2)
        hash1 = compute_address_hash(data1)
        hash2 = compute_address_hash(data2)
        assert hash1 == hash2

    def test_generate_random_bitchain_deterministic_with_seed(self):
        """generate_random_bitchain should be deterministic with a seed."""
        from warbler_cda.fractalstat_entity import generate_random_bitchain

        bc1 = generate_random_bitchain(seed=42)
        bc2 = generate_random_bitchain(seed=42)

        # IDs should match
        assert bc1.id == bc2.id
        # Realms should match
        assert bc1.realm == bc2.realm
        # Created timestamps should match
        assert bc1.created_at == bc2.created_at

    def test_generate_random_bitchain_without_seed(self):
        """generate_random_bitchain without seed should produce valid BitChain.""" 
        from warbler_cda.fractalstat_entity import generate_random_bitchain

        bc = generate_random_bitchain()
        assert bc.id is not None
        assert bc.coordinates is not None
        assert isinstance(bc.state, dict)

    def test_entity_custom_entity_id(self):
        """FractalStatEntity should accept custom entity_id."""
        ConcreteEntity = self.create_concrete_entity()
        custom_id = "custom-entity-123"
        entity = ConcreteEntity(entity_id=custom_id)

        assert entity.entity_id == custom_id
        assert entity.owner_id is None or isinstance(entity.owner_id, str)

    def test_entity_record_event(self):
        """_record_event should add lifecycle event."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        initial_count = len(entity.lifecycle_events)
        entity._record_event("test_event", "Test description", {"key": "value"}) # pylint: disable=protected-access

        assert len(entity.lifecycle_events) == initial_count + 1
        event = entity.lifecycle_events[-1]
        assert event.event_type == "test_event"
        assert event.description == "Test description"
        assert event.metadata["key"] == "value"

    def test_entity_last_activity_tracking(self):
        """Entity should track last_activity timestamp."""
        from datetime import timezone

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        assert isinstance(entity.last_activity, datetime)
        now_utc = datetime.now(timezone.utc)
        assert entity.last_activity <= now_utc

    def test_entity_add_entanglement(self):
        """add_entanglement should track entangled entities."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        entity.add_entanglement("entity-123", 0.75)

        assert "entity-123" in entity.entangled_entities
        idx = entity.entangled_entities.index("entity-123")
        assert entity.entanglement_strength[idx] == 0.75

    def test_entity_add_entanglement_duplicate(self):
        """add_entanglement should not add duplicate entities."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        entity.add_entanglement("entity-123", 0.5)
        entity.add_entanglement("entity-123", 0.9)

        assert entity.entangled_entities.count("entity-123") == 1

    def test_entity_remove_entanglement(self):
        """remove_entanglement should remove entangled entity."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        entity.add_entanglement("entity-123", 0.75)
        entity.remove_entanglement("entity-123")

        assert "entity-123" not in entity.entangled_entities
        assert len(entity.entangled_entities) == len(entity.entanglement_strength)

    def test_entity_remove_entanglement_nonexistent(self):
        """remove_entanglement should handle nonexistent entity gracefully."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        entity.remove_entanglement("nonexistent")

    def test_entity_get_entanglements(self):
        """get_entanglements should return list of entanglement tuples."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        entity.add_entanglement("entity-1", 0.5)
        entity.add_entanglement("entity-2", 0.9)

        entanglements = entity.get_entanglements()

        assert len(entanglements) == 2
        assert ("entity-1", 0.5) in entanglements
        assert ("entity-2", 0.9) in entanglements

    def test_entity_collectible_card_data(self):
        """to_collectible_card_data should return card display data."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        card_data = entity.to_collectible_card_data()

        assert card_data["title"] == "Test Entity"
        assert card_data["fluff_text"] == "Test description"
        assert "icon_url" in card_data
        assert "artwork_url" in card_data

    def test_entity_record_mint(self):
        """record_mint should update NFT status."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        initial_events = len(entity.lifecycle_events)
        entity.record_mint("0x123abc", 42, "QmHash123")

        assert entity.nft_minted is True
        assert entity.nft_contract == "0x123abc"
        assert entity.nft_token_id == 42
        assert entity.nft_metadata_ipfs == "QmHash123"
        assert len(entity.lifecycle_events) == initial_events + 1
        assert entity.lifecycle_events[-1].event_type == "nft_minted"

    def test_entity_to_dict(self):
        """to_dict should convert entity to dictionary."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.entity_type = "TestEntity"
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=5,
            adjacency=75.0,
            horizon=Horizon.PEAK,
            luminosity=90.0,
            polarity=Polarity.LOGIC,
            dimensionality=3,
            alignment=Alignment.LAWFUL_GOOD,
        )
        entity.owner_id = "user-123"

        data = entity.to_dict()

        assert data["entity_id"] == entity.entity_id
        assert data["entity_type"] == "TestEntity"
        assert data["fractalstat"] is not None
        assert data["owner_id"] == "user-123"
        assert "created_at" in data
        assert "last_activity" in data

    def test_entity_save_to_file(self):
        """save_to_file should persist entity to JSON."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.entity_type = "TestEntity"

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_entity.json"
            entity.save_to_file(file_path)

            assert file_path.exists()

            with open(file_path, "r", encoding="UTF-8") as f:
                data = json.load(f)

            assert data["entity_id"] == entity.entity_id
            assert data["entity_type"] == "TestEntity"

    def test_entity_save_to_file_creates_directory(self):
        """save_to_file should create parent directories."""
        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "test_entity.json"
            entity.save_to_file(file_path)

            assert file_path.exists()

    def test_entity_load_from_file_raises_not_implemented(self):
        """load_from_file should raise NotImplementedError."""
        ConcreteEntity = self.create_concrete_entity()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            with open(file_path, "w", encoding="UTF-8") as f:
                json.dump({"entity_type": "test"}, f)

            with pytest.raises(NotImplementedError):
                ConcreteEntity.load_from_file(file_path)

    def test_entity_render_zoom_level_1_badge(self):
        """render_zoom_level(1) should return badge view."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.BADGE,
            lineage=0,
            adjacency=0.0,
            horizon=Horizon.GENESIS,
            luminosity=0.0,
            polarity=Polarity.ACHIEVEMENT,
            dimensionality=0,
            alignment=Alignment.LAWFUL_GOOD,
        )

        view = entity.render_zoom_level(1)

        assert view["type"] == "badge"
        assert view["zoom_level"] == 1
        assert "icon" in view
        assert "rarity" in view

    def test_entity_render_zoom_level_2_dog_tag(self):
        """render_zoom_level(2) should return dog-tag view."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=1,
            adjacency=50.0,
            horizon=Horizon.EMERGENCE,
            luminosity=50.0,
            polarity=Polarity.BALANCE,
            dimensionality=1,
            alignment=Alignment.LAWFUL_GOOD,
        )

        view = entity.render_zoom_level(2)

        assert view["type"] == "dog_tag"
        assert view["zoom_level"] == 2
        assert "icon" in view
        assert "title" in view
        assert "stats" in view

    def test_entity_render_zoom_level_3_card(self):
        """render_zoom_level(3) should return collectible card view."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=2,
            adjacency=75.0,
            horizon=Horizon.PEAK,
            luminosity=90.0,
            polarity=Polarity.LOGIC,
            dimensionality=2,
            alignment=Alignment.LAWFUL_GOOD,
        )

        view = entity.render_zoom_level(3)

        assert view["type"] == "collectible_card"
        assert view["zoom_level"] == 3

    def test_entity_render_zoom_level_4_profile_panel(self):
        """render_zoom_level(4) should return profile panel view."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=3,
            adjacency=80.0,
            horizon=Horizon.PEAK,
            luminosity=95.0,
            polarity=Polarity.CREATIVITY,
            dimensionality=3,
            alignment=Alignment.LAWFUL_GOOD,
        )
        entity.owner_id = "user-123"
        entity.add_entanglement("entity-1", 0.5)

        view = entity.render_zoom_level(4)

        assert view["type"] == "profile_panel"
        assert view["zoom_level"] == 4
        assert view["owner"] == "user-123"
        assert view["entangled_count"] == 1

    def test_entity_render_zoom_level_5_full_profile(self):
        """render_zoom_level(5) should return full entity profile."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=4,
            adjacency=85.0,
            horizon=Horizon.CRYSTALLIZATION,
            luminosity=100.0,
            polarity=Polarity.ORDER,
            dimensionality=4,
            alignment=Alignment.LAWFUL_GOOD,
        )
        entity._record_event("test", "Test event") # pylint: disable=protected-access

        view = entity.render_zoom_level(5)

        assert view["type"] == "entity_profile"
        assert view["zoom_level"] == 5
        assert "lifecycle_events" in view
        assert "entanglements" in view
        assert "luca_trace" in view

    def test_entity_render_zoom_level_6_fractal_descent(self):
        """render_zoom_level(6+) should return fractal descent view."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.PATTERN,
            lineage=5,
            adjacency=90.0,
            horizon=Horizon.PEAK,
            luminosity=100.0,
            polarity=Polarity.CHAOS,
            dimensionality=5,
            alignment=Alignment.LAWFUL_GOOD,
        )

        view = entity.render_zoom_level(6)

        assert view["type"] == "fractal_descent"
        assert view["zoom_level"] == 6
        assert "fractalstat_dimensions" in view
        assert "realm_details" in view
        assert "entanglement_network" in view
        assert "event_chronology" in view

    def test_entity_render_zoom_level_invalid_low(self):
        """render_zoom_level should raise ValueError for level < 1."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=0,
            adjacency=0.0,
            horizon=Horizon.GENESIS,
            luminosity=0.0,
            polarity=Polarity.BALANCE,
            dimensionality=0,
            alignment=Alignment.LAWFUL_GOOD,
        )

        with pytest.raises(ValueError, match="Invalid zoom level"):
            entity.render_zoom_level(0)

    def test_entity_render_zoom_level_invalid_high(self):
        """render_zoom_level should raise ValueError for level > 7."""
        from warbler_cda.fractalstat_entity import (
            FractalStatCoordinates,
            Realm,
            Horizon,
            Polarity,
            Alignment,
        )

        ConcreteEntity = self.create_concrete_entity()
        entity = ConcreteEntity()
        entity.fractalstat = FractalStatCoordinates(
            realm=Realm.COMPANION,
            lineage=0,
            adjacency=0.0,
            horizon=Horizon.GENESIS,
            luminosity=0.0,
            polarity=Polarity.BALANCE,
            dimensionality=0,
            alignment=Alignment.LAWFUL_GOOD,
        )

        with pytest.raises(ValueError, match="Invalid zoom level"):
            entity.render_zoom_level(9)


class TestHelperFunctions:
    """Test helper functions."""

    def test_hash_for_coordinates_deterministic(self):
        """hash_for_coordinates should be deterministic."""
        from warbler_cda.fractalstat_entity import hash_for_coordinates

        data = {"key1": "value1", "key2": 42}
        hash1 = hash_for_coordinates(data)
        hash2 = hash_for_coordinates(data)

        assert hash1 == hash2

    def test_hash_for_coordinates_different_data(self):
        """hash_for_coordinates should produce different hashes for different data."""
        from warbler_cda.fractalstat_entity import hash_for_coordinates

        data1 = {"key": "value1"}
        data2 = {"key": "value2"}

        hash1 = hash_for_coordinates(data1)
        hash2 = hash_for_coordinates(data2)

        assert hash1 != hash2

    def test_hash_for_coordinates_order_independent(self):
        """hash_for_coordinates should be order-independent."""
        from warbler_cda.fractalstat_entity import hash_for_coordinates

        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}

        hash1 = hash_for_coordinates(data1)
        hash2 = hash_for_coordinates(data2)

        assert hash1 == hash2

    def test_compute_adjacency_score_identical_tags(self):
        """compute_adjacency_score should return 100 for identical tags."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        tags = ["tag1", "tag2", "tag3"]
        score = compute_adjacency_score(tags, tags)

        assert score == 100.0

    def test_compute_adjacency_score_no_overlap(self):
        """compute_adjacency_score should return 0 for no overlap."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        tags1 = ["tag1", "tag2"]
        tags2 = ["tag3", "tag4"]
        score = compute_adjacency_score(tags1, tags2)

        assert score == 0.0

    def test_compute_adjacency_score_partial_overlap(self):
        """compute_adjacency_score should calculate partial overlap correctly."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        tags1 = ["tag1", "tag2", "tag3"]
        tags2 = ["tag2", "tag3", "tag4"]
        score = compute_adjacency_score(tags1, tags2)

        assert 0.0 < score < 100.0
        assert abs(score - 50.0) < 1.0

    def test_compute_adjacency_score_empty_tags1(self):
        """compute_adjacency_score should return 0 for empty first list."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        score = compute_adjacency_score([], ["tag1", "tag2"])

        assert score == 0.0

    def test_compute_adjacency_score_empty_tags2(self):
        """compute_adjacency_score should return 0 for empty second list."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        score = compute_adjacency_score(["tag1", "tag2"], [])

        assert score == 0.0

    def test_compute_adjacency_score_both_empty(self):
        """compute_adjacency_score should return 0 for both empty lists."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        score = compute_adjacency_score([], [])

        assert score == 0.0

    def test_compute_adjacency_score_duplicate_tags(self):
        """compute_adjacency_score should handle duplicate tags."""
        from warbler_cda.fractalstat_entity import compute_adjacency_score

        tags1 = ["tag1", "tag1", "tag2"]
        tags2 = ["tag1", "tag2", "tag2"]
        score = compute_adjacency_score(tags1, tags2)

        assert score == 100.0
