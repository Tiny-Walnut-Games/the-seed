"""
Basic tests for warbler_cda.evaporation module.

Tests the EvaporationEngine and CloudStore for glyph evaporation and mist generation.
"""

import pytest
from unittest.mock import Mock


class TestEvaporationEngine:
    """Test EvaporationEngine basic functionality."""

    def test_evaporation_engine_initialization(self):
        """EvaporationEngine should initialize properly."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)

        assert engine.magma_store == magma_store
        assert engine.cloud_store == cloud_store
        assert engine.current_style == "balanced"

    def test_evaporate_with_empty_glyphs(self):
        """evaporate should handle empty glyph selection gracefully."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        magma_store.select_hot.return_value = []

        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)
        result = engine.evaporate(limit=3)

        assert result == []
        assert cloud_store.mist_lines == []
        assert cloud_store.humidity_index == 0.0

    def test_evaporate_with_glyphs(self):
        """evaporate should process glyphs into mist lines."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore
        import time

        # Create mock glyphs
        glyphs = [
            {
                "id": "glyph_001",
                "compressed_summary": "Test summary one",
                "heat": 0.8,
                "affect": {"awe": 0.5, "curiosity": 0.3},
                "created_epoch": int(time.time())
            }
        ]

        magma_store = Mock()
        magma_store.select_hot.return_value = glyphs

        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)
        result = engine.evaporate(limit=1)

        # Should return mist lines
        assert len(result) == 1
        assert len(cloud_store.mist_lines) == 1

        mist = result[0]
        assert "id" in mist
        assert "proto_thought" in mist
        assert "style" in mist
        assert mist["source_glyph"] == "glyph_001"


class TestCloudStore:
    """Test CloudStore functionality."""

    def test_cloud_store_initialization(self):
        """CloudStore should initialize with default values."""
        from warbler_cda.evaporation import CloudStore

        store = CloudStore()
        assert store.mist_lines == []
        assert store.humidity_index == 0.0
        assert store.generation_mode == "balanced"

    def test_add_mist_lines(self):
        """add_mist_lines should append mist lines."""
        from warbler_cda.evaporation import CloudStore

        store = CloudStore()
        mist_lines = [
            {"id": "mist_001", "proto_thought": "test thought"},
            {"id": "mist_002", "proto_thought": "another thought"}
        ]
        store.add_mist_lines(mist_lines)

        assert len(store.mist_lines) == 2

    def test_get_active_mist_empty(self):
        """get_active_mist should return empty list when no mist lines."""
        from warbler_cda.evaporation import CloudStore

        store = CloudStore()
        active = store.get_active_mist()

        assert active == []

    def test_get_active_mist_with_data(self):
        """get_active_mist should return mist lines when available."""
        from warbler_cda.evaporation import CloudStore
        import time

        store = CloudStore()
        mist_lines = [
            {
                "id": "mist_001",
                "proto_thought": "test thought",
                "distillation_quality": 0.8,
                "mythic_weight": 0.5,
                "style_confidence": 0.7,
                "created_epoch": int(time.time())
            }
        ]
        store.mist_lines = mist_lines

        active = store.get_active_mist(limit=1)
        assert len(active) == 1
        assert active[0]["id"] == "mist_001"


class TestStyleMethods:
    """Test style-related methods."""

    def test_apply_balanced_style(self):
        """apply_balanced_style should return balanced proto-thought."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)

        concepts = ["concept1", "concept2"]
        result = engine._apply_balanced_style(concepts, {})

        assert result.startswith("[Balanced]")
        assert "concept1" in result
        assert "concept2" in result

    def test_apply_poetic_style(self):
        """apply_poetic_style should return poetic proto-thought."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)

        concepts = ["dreams"]
        result = engine._apply_poetic_style(concepts, {})

        assert result.startswith("[Poetic]")
        assert "dreams" in result


class TestHelperMethods:
    """Test helper methods."""

    def test_extract_key_concepts(self):
        """extract_key_concepts should extract concepts from text."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)

        # Test with separators
        summary = "concept1 | concept2 → concept3"
        concepts = engine._extract_key_concepts(summary)
        assert len(concepts) > 0
        assert "concept1" in concepts

    def test_calculate_semantic_density(self):
        """calculate_semantic_density should return a float."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore

        magma_store = Mock()
        cloud_store = CloudStore()

        engine = EvaporationEngine(magma_store, cloud_store)

        density = engine._calculate_semantic_density("test text with words")
        assert isinstance(density, float)
        assert 0.0 <= density <= 1.0


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_evaporation_workflow(self):
        """Test complete evaporation process."""
        from warbler_cda.evaporation import EvaporationEngine, CloudStore
        import time

        # Set up mock magma store
        magma_store = Mock()
        glyphs = [
            {
                "id": "glyph_001",
                "compressed_summary": "philosophical insights about reality",
                "heat": 0.9,
                "affect": {"awe": 0.8, "wonder": 0.7},
                "created_epoch": int(time.time())
            }
        ]
        magma_store.select_hot.return_value = glyphs

        cloud_store = CloudStore()

        # Initialize engine
        engine = EvaporationEngine(magma_store, cloud_store)

        # Execute evaporation
        mist_lines = engine.evaporate(limit=1)

        # Verify results
        assert len(mist_lines) == 1
        assert len(cloud_store.mist_lines) == 1

        mist = mist_lines[0]
        required_keys = ["id", "proto_thought", "style", "mythic_weight", "distillation_quality"]
        for key in required_keys:
            assert key in mist
