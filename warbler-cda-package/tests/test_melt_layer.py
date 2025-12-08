# pylint: disable=import-outside-toplevel, protected-access
"""
Comprehensive tests for warbler_cda.melt_layer module.

Tests the MeltLayer and MagmaStore for cluster retirement.
"""


class TestMagmaStore:
    """Test MagmaStore class."""

    def test_magma_store_initialization(self):
        """MagmaStore should initialize with empty glyphs list."""
        from warbler_cda.melt_layer import MagmaStore

        store = MagmaStore()
        assert not store.glyphs

    def test_add_glyph(self):
        """add_glyph should append glyph to store."""
        from warbler_cda.melt_layer import MagmaStore

        store = MagmaStore()
        glyph = {"id": "glyph-1", "summary": "test"}
        store.add_glyph(glyph)

        assert len(store.glyphs) == 1
        assert store.glyphs[0] == glyph

    def test_add_multiple_glyphs(self):
        """add_glyph should handle multiple glyphs."""
        from warbler_cda.melt_layer import MagmaStore

        store = MagmaStore()
        for i in range(5):
            store.add_glyph({"id": f"glyph-{i}"})

        assert len(store.glyphs) == 5

    def test_select_hot(self):
        """select_hot should return most recent glyphs."""
        from warbler_cda.melt_layer import MagmaStore

        store = MagmaStore()
        import time
        now = int(time.time())
        for i in range(10):
            created_epoch = now - (9 - i) * 3600
            store.add_glyph({"id": f"glyph-{i}", "created_epoch": created_epoch})

        hot = store.select_hot(limit=3)

        assert len(hot) == 3
        # Should be highest heat glyphs (most recent)
        assert hot[0]["id"] == "glyph-9"
        assert hot[1]["id"] == "glyph-8"
        assert hot[2]["id"] == "glyph-7"

    def test_select_hot_limit_exceeds_size(self):
        """select_hot should handle limit larger than store size."""
        from warbler_cda.melt_layer import MagmaStore

        store = MagmaStore()
        store.add_glyph({"id": "glyph-1"})
        store.add_glyph({"id": "glyph-2"})

        hot = store.select_hot(limit=10)
        assert len(hot) == 2


class TestMeltLayer:
    """Test MeltLayer class."""

    def test_melt_layer_initialization(self):
        """MeltLayer should initialize with magma store."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        assert melt.magma_store == store
        assert melt.embed_fn is not None

    def test_melt_layer_custom_embed_fn(self):
        """MeltLayer should accept custom embedding function."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        def custom_embed(frags):
            # frags is already a list of text strings
            return [0.5, 0.5, 0.5]
        melt = MeltLayer(magma_store=store, embed_fn=custom_embed)

        # Call the embed function with empty list to verify it works
        assert melt.embed_fn([]) == [0.5, 0.5, 0.5]

    def test_retire_cluster_empty(self):
        """retire_cluster should handle empty cluster."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        cluster = {"fragments": []}
        glyph = melt.retire_cluster(cluster)

        assert "id" in glyph
        assert glyph["compressed_summary"] == "(empty cluster)"
        assert len(store.glyphs) == 1

    def test_retire_cluster_with_fragments(self):
        """retire_cluster should process fragments into glyph."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        cluster = {
            "fragments": [
                {"id": "f1", "text": "Fragment one"},
                {"id": "f2", "text": "Fragment two"}
            ]
        }

        glyph = melt.retire_cluster(cluster)

        assert glyph["id"].startswith("mglyph_")
        assert glyph["source_ids"] == ["f1", "f2"]
        assert "Fragment one" in glyph["compressed_summary"]
        assert "embedding" in glyph
        assert "affect" in glyph
        assert glyph["resolution_state"] == "retired"
        assert "provenance_hash" in glyph
        assert "created_epoch" in glyph

    def test_glyph_id_deterministic(self):
        """_glyph_id should be deterministic for same summary."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        id1 = melt._glyph_id("test summary")
        id2 = melt._glyph_id("test summary")

        assert id1 == id2
        assert id1.startswith("mglyph_")

    def test_glyph_id_different_summaries(self):
        """_glyph_id should produce different IDs for different summaries."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        id1 = melt._glyph_id("summary one")
        id2 = melt._glyph_id("summary two")

        assert id1 != id2

    def test_summarize_empty(self):
        """_summarize should handle empty fragments."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        summary = melt._summarize([])
        assert summary == "(empty cluster)"

    def test_summarize_single_fragment(self):
        """_summarize should handle single fragment."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        fragments = [{"text": "Single fragment text"}]
        summary = melt._summarize(fragments)

        assert "Single fragment text" in summary

    def test_summarize_multiple_fragments(self):
        """_summarize should join multiple fragments."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        fragments = [
            {"text": "Fragment one"},
            {"text": "Fragment two"},
            {"text": "Fragment three"}
        ]
        summary = melt._summarize(fragments)

        assert "Fragment one" in summary
        assert "|" in summary  # Separator

    def test_summarize_truncation(self):
        """_summarize should truncate long summaries."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        # Create very long fragments
        fragments = [{"text": "A" * 200} for _ in range(10)]
        summary = melt._summarize(fragments)

        # Should be truncated to 180 chars
        assert len(summary) <= 180

    def test_prov_hash_deterministic(self):
        """_prov_hash should be deterministic."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        fragments = [{"text": "test"}]
        hash1 = melt._prov_hash(fragments)
        hash2 = melt._prov_hash(fragments)

        assert hash1 == hash2
        assert hash1.startswith("sha256:")

    def test_prov_hash_different_fragments(self):
        """_prov_hash should produce different hashes for different fragments."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        fragments1 = [{"text": "test1"}]
        fragments2 = [{"text": "test2"}]

        hash1 = melt._prov_hash(fragments1)
        hash2 = melt._prov_hash(fragments2)

        assert hash1 != hash2


class TestIntegration:
    """Integration tests for melt layer workflow."""

    def test_full_retirement_workflow(self):
        """Test complete cluster retirement workflow."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        def embed_fn(frags):
            # frags is already a list of text strings
            return [0.1, 0.2, 0.3]
        melt = MeltLayer(magma_store=store, embed_fn=embed_fn)

        # Retire cluster
        cluster = {
            "fragments": [
                {"id": "f1", "text": "First fragment"},
                {"id": "f2", "text": "Second fragment"}
            ]
        }

        glyph = melt.retire_cluster(cluster)

        # Verify glyph structure
        assert glyph["id"].startswith("mglyph_")
        assert len(glyph["source_ids"]) == 2
        assert "First fragment" in glyph["compressed_summary"]
        assert glyph["embedding"] == [0.1, 0.2, 0.3]
        assert glyph["resolution_state"] == "retired"

        # Verify stored in magma
        assert len(store.glyphs) == 1
        assert store.glyphs[0] == glyph

    def test_multiple_retirements(self):
        """Test multiple cluster retirements."""
        from warbler_cda.melt_layer import MeltLayer, MagmaStore

        store = MagmaStore()
        melt = MeltLayer(magma_store=store)

        # Retire multiple clusters
        for i in range(5):
            cluster = {
                "fragments": [{"id": f"f{i}", "text": f"Fragment {i}"}]
            }
            melt.retire_cluster(cluster)

        assert len(store.glyphs) == 5

        # Select hot glyphs
        hot = store.select_hot(limit=3)
        assert len(hot) == 3
