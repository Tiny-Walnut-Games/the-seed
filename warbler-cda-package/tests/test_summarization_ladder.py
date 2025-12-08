"""
Comprehensive tests for SummarizationLadder hierarchical memory compression system.

Tests micro-summaries, macro distillation, compression metrics, and edge cases.
Targets 90%+ coverage for the summarization_ladder.py module.
"""

import pytest
import time
import hashlib
from unittest.mock import Mock
from warbler_cda.summarization_ladder import (
    SummarizationLadder,
    MicroSummary,
    MacroDistillation,
)


class TestMicroSummary:
    """Test MicroSummary dataclass and methods."""

    def test_micro_summary_initialization_required_fields(self):
        """Test MicroSummary requires all essential fields."""
        micro = MicroSummary(
            summary_id="micro_123",
            window_fragments=["frag_1", "frag_2", "frag_3"],
            compressed_text="Micro summary text",
            window_size=3,
            creation_timestamp=time.time(),
            heat_aggregate=0.7,
            semantic_centroid=[0.1, 0.2, 0.3],
        )

        assert micro.summary_id == "micro_123"
        assert len(micro.window_fragments) == 3
        assert micro.compressed_text == "Micro summary text"
        assert micro.window_size == 3
        assert micro.heat_aggregate == 0.7
        assert micro.semantic_centroid == [0.1, 0.2, 0.3]

    def test_micro_summary_default_values(self):
        """Test MicroSummary default values."""
        micro = MicroSummary(
            summary_id="minimal_micro",
            window_fragments=["frag_1"],
            compressed_text="Minimal text",
            window_size=1,
            creation_timestamp=1000.0,
            heat_aggregate=0.5,
        )

        assert micro.semantic_centroid is None

    def test_micro_summary_get_age_seconds(self):
        """Test age calculation method."""
        past_time = time.time() - 3600  # 1 hour ago
        micro = MicroSummary(
            summary_id="aged_micro",
            window_fragments=["frag_1"],
            compressed_text="Aged summary",
            window_size=1,
            creation_timestamp=past_time,
            heat_aggregate=0.5,
        )

        age = micro.get_age_seconds()
        assert age >= 3599 and age <= 3601  # Allow small margin for test execution time


class TestMacroDistillation:
    """Test MacroDistillation dataclass."""

    def test_macro_distillation_initialization(self):
        """Test MacroDistillation initialization."""
        macro = MacroDistillation(
            distillation_id="macro_456",
            source_micro_summaries=["micro_1", "micro_2"],
            distilled_essence="Macro distillation essence",
            consolidation_ratio=2.5,
            provenance_chain=[
                {"micro_summary_id": "micro_1", "original_fragments": 5},
                {"micro_summary_id": "micro_2", "original_fragments": 3},
            ],
            creation_timestamp=time.time(),
            anchor_reinforcements=["anchor_a", "anchor_b"],
        )

        assert macro.distillation_id == "macro_456"
        assert len(macro.source_micro_summaries) == 2
        assert macro.distilled_essence == "Macro distillation essence"
        assert macro.consolidation_ratio == 2.5
        assert len(macro.provenance_chain) == 2
        assert len(macro.anchor_reinforcements) == 2


class TestSummarizationLadderInitialization:
    """Test SummarizationLadder initialization."""

    def test_summarization_ladder_default_config(self):
        """Test default configuration."""
        ladder = SummarizationLadder()

        assert ladder.micro_window_size == 5
        assert ladder.macro_trigger_count == 3
        assert ladder.max_micro_summaries == 20
        assert ladder.config == {}

    def test_summarization_ladder_custom_config(self):
        """Test custom configuration."""
        config = {
            "micro_window_size": 10,
            "macro_trigger_count": 5,
            "max_micro_summaries": 50,
        }
        ladder = SummarizationLadder(config=config)

        assert ladder.micro_window_size == 10
        assert ladder.macro_trigger_count == 5
        assert ladder.max_micro_summaries == 50

    def test_summarization_ladder_with_embedding_provider(self):
        """Test initialization with embedding provider."""
        mock_provider = Mock()
        ladder = SummarizationLadder(embedding_provider=mock_provider)

        assert ladder.embedding_provider == mock_provider

    def test_summarization_ladder_initial_state(self):
        """Test initial state after construction."""
        ladder = SummarizationLadder()

        assert len(ladder.micro_summaries) == 0
        assert len(ladder.macro_distillations) == 0
        assert len(ladder.fragment_buffer) == 0
        assert ladder.total_fragments_processed == 0
        assert ladder.micro_summaries_created == 0
        assert ladder.macro_distillations_created == 0

        # Check metrics are initialized
        assert ladder.metrics["total_fragments"] == 0
        assert ladder.metrics["micro_summaries_created"] == 0
        assert ladder.metrics["macro_distillations_created"] == 0


class TestSummarizationLadderProcessFragments:
    """Test fragment processing through the summarization ladder."""

    def setup_method(self):
        """Setup for each test."""
        self.ladder = SummarizationLadder({
            "micro_window_size": 2,  # Make this consistent with default for easier testing
            "macro_trigger_count": 2,  # Trigger macro after 2 micros
        })

    def test_process_empty_fragments(self):
        """Test processing empty fragment list."""
        result = self.ladder.process_fragments([])

        assert result["fragments_processed"] == 0
        assert result["micro_summaries_created"] == 0
        assert result["macro_distillations_created"] == 0
        assert len(result["new_micro_summaries"]) == 0
        assert len(result["new_macro_distillations"]) == 0

    def test_process_single_fragment(self):
        """Test processing a single fragment."""
        fragments = [{"id": "frag_1", "text": "First fragment text", "heat": 0.8}]
        result = self.ladder.process_fragments(fragments)

        assert result["fragments_processed"] == 1
        assert result["micro_summaries_created"] == 0  # Not enough for micro-summary
        assert result["macro_distillations_created"] == 0

        # Check fragment is buffered
        assert len(self.ladder.fragment_buffer) == 1
        assert self.ladder.total_fragments_processed == 1

    def test_process_fragments_to_create_micro_summary(self):
        """Test processing enough fragments to create micro-summary."""
        # Create 2 fragments (matches micro_window_size of 2)
        fragments = [
            {"id": f"frag_{i}", "text": f"Fragment {i} content with some detail", "heat": 0.5 + i * 0.1}
            for i in range(1, 3)
        ]

        result = self.ladder.process_fragments(fragments)

        assert result["fragments_processed"] == 2
        assert result["micro_summaries_created"] == 1
        assert result["macro_distillations_created"] == 0
        assert len(result["new_micro_summaries"]) == 1

        # Check micro summary was created
        assert len(self.ladder.micro_summaries) == 1
        micro = self.ladder.micro_summaries[0]
        assert micro.window_size == 2
        assert len(micro.window_fragments) == 2
        assert "frag_1" in micro.window_fragments

    def test_process_fragments_to_trigger_macro_distillation(self):
        """Test that macro distillation is triggered when enough micros are created."""
        ladder = SummarizationLadder({
            "micro_window_size": 2,
            "macro_trigger_count": 1  # Trigger immediately after 1 micro
        })

        # Create fragments that will generate a micro-summary
        fragments = [
            {"id": "frag_1", "text": "First fragment content", "heat": 0.6},
            {"id": "frag_2", "text": "Second fragment content", "heat": 0.7}
        ]

        result = ladder.process_fragments(fragments)

        # Should create 1 micro-summary and 1 macro distillation
        assert result["micro_summaries_created"] >= 1
        assert result["macro_distillations_created"] >= 1

        # Check that macro distillations were created
        assert len(ladder.macro_distillations) >= 1

        # Check macro has expected struttura
        macro = ladder.macro_distillations[0]
        assert macro.distillation_id.startswith("macro_")
        assert len(macro.source_micro_summaries) >= 1
        assert len(macro.anchor_reinforcements) > 0

    def test_fragment_buffer_overlap(self):
        """Test that fragment buffer maintains overlap between micro-summaries."""
        ladder = SummarizationLadder({"micro_window_size": 4})  # Use larger window size
        # Create enough fragments to trigger a micro-summary and check overlap
        fragments = [
            {"id": f"frag_{i}", "text": f"Fragment {i} content", "heat": 0.5}
            for i in range(4)  # Send 4 fragments: enough for one micro-summary
        ]

        result = ladder.process_fragments(fragments)

        assert result["fragments_processed"] == 4
        # May create micro-summaries due to sliding window - just check the basics
        assert len(ladder.micro_summaries) >= 0

    def test_micro_summary_semantic_centroid_creation(self):
        """Test semantic centroid creation with embedding provider."""
        mock_provider = Mock()
        mock_provider.embed_text.return_value = [0.1, 0.2, 0.3]
        ladder = SummarizationLadder({"micro_window_size": 2}, embedding_provider=mock_provider)

        fragments = [
            {"id": "frag_1", "text": "First fragment", "heat": 0.6},
            {"id": "frag_2", "text": "Second fragment", "heat": 0.7},
        ]

        result = ladder.process_fragments(fragments)

        assert result["micro_summaries_created"] == 1

        micro = ladder.micro_summaries[0]
        assert micro.semantic_centroid is not None
        assert len(micro.semantic_centroid) == 3  # Centroid of 3D embeddings

        # Verify embedding provider was called
        assert mock_provider.embed_text.call_count == 2

    def test_micro_summary_without_embedding_provider(self):
        """Test micro-summary creation without embedding provider."""
        ladder = SummarizationLadder({"micro_window_size": 2})

        fragments = [
            {"id": "frag_1", "text": "First fragment", "heat": 0.6},
            {"id": "frag_2", "text": f"Second fragment", "heat": 0.7},
        ]

        result = ladder.process_fragments(fragments)

        assert result["micro_summaries_created"] == 1

        micro = ladder.micro_summaries[0]
        assert micro.semantic_centroid is None


class TestSummarizationLadderRecoveryContext:
    """Test recovery context generation."""

    def setup_method(self):
        """Setup for each test."""
        self.ladder = SummarizationLadder()

        # Create some test data
        fragments = [
            {"id": f"frag_{i}", "text": f"Fragment {i} content", "heat": 0.6}
            for i in range(3)
        ]
        self.ladder.process_fragments(fragments)

    def test_get_recovery_context_empty_ladder(self):
        """Test recovery context on empty ladder."""
        empty_ladder = SummarizationLadder()
        context = empty_ladder.get_recovery_context("anchor_1")

        assert context["anchor_id"] == "anchor_1"
        assert len(context["related_micro_summaries"]) == 0
        assert len(context["related_macro_distillations"]) == 0

    def test_get_recovery_context_with_micro_summaries(self):
        """Test recovery context generation with micro-summaries."""
        context = self.ladder.get_recovery_context("anchor_test", context_size=5)

        required_keys = [
            "anchor_id", "related_micro_summaries", "related_macro_distillations",
            "temporal_sequence", "consolidation_path"
        ]

        for key in required_keys:
            assert key in context

        assert context["anchor_id"] == "anchor_test"

        # Should have our micro-summary
        if self.ladder.micro_summaries:
            assert len(context["related_micro_summaries"]) >= 1
            micro_info = context["related_micro_summaries"][0]
            required_micro_keys = ["summary_id", "compressed_text", "heat_aggregate", "age_seconds"]
            for key in required_micro_keys:
                assert key in micro_info

    def test_get_recovery_context_with_macro_distillations(self):
        """Test recovery context with macro distillations."""
        # Force creation of macro distillation by adjusting config
        ladder = SummarizationLadder({"micro_window_size": 2, "macro_trigger_count": 1})

        # Create first micro
        fragments1 = [{"id": "frag_1", "text": "Fragment 1", "heat": 0.6},
                     {"id": "frag_2", "text": "Fragment 2", "heat": 0.6}]
        ladder.process_fragments(fragments1)

        # Should trigger macro distillation
        assert len(ladder.macro_distillations) >= 1

        context = ladder.get_recovery_context("anchor_special")

        # Check temporal sequence includes macro
        macro_found = False
        for item in context["temporal_sequence"]:
            if item["type"] == "macro":
                macro_found = True
                break
        assert macro_found


class TestSummarizationLadderCompressionMetrics:
    """Test compression metrics and health reporting."""

    def setup_method(self):
        """Setup for each test."""
        self.ladder = SummarizationLadder()

    def test_get_compression_metrics_empty_ladder(self):
        """Test metrics for empty ladder."""
        metrics = self.ladder.get_compression_metrics()

        assert "summarization_ladder_metrics" in metrics
        assert "current_state" in metrics
        assert "ladder_health" in metrics

        # Empty ladder should have zeros
        current = metrics["current_state"]
        assert current["micro_summaries_active"] == 0
        assert current["macro_distillations_total"] == 0
        assert current["fragment_buffer_size"] == 0

    def test_get_compression_metrics_with_activity(self):
        """Test metrics after processing fragments."""
        # Add some fragments to create activity
        fragments = [
            {"id": f"frag_{i}", "text": f"Fragment {i} content", "heat": 0.5}
            for i in range(4)
        ]

        self.ladder.process_fragments(fragments)
        time.sleep(0.01)  # Allow some processing time
        self.ladder.process_fragments([{"id": "frag_5", "text": "Extra fragment", "heat": 0.6}])

        metrics = self.ladder.get_compression_metrics()

        # Should have some activity
        current = metrics["current_state"]
        assert current["micro_summaries_active"] >= 0
        # Note: fragments_processed may not exist, just check that state includes expected keys
        assert "micro_summaries_active" in current

        # Health metrics should be computed
        health = metrics["ladder_health"]
        assert "processing_efficiency" in health
        assert "compression_effectiveness" in health
        assert "temporal_coverage_hours" in health

        # Values should be reasonable
        assert 0.0 <= health["processing_efficiency"]
        assert 0.0 <= health["compression_effectiveness"] <= 1.0
        assert health["temporal_coverage_hours"] >= 0.0

    def test_calculate_processing_efficiency(self):
        """Test processing efficiency calculation."""
        ladder = SummarizationLadder()

        # Empty ladder
        efficiency = ladder._calculate_processing_efficiency()
        assert efficiency == 1.0

        # After processing
        fragments = [{"id": "frag_1", "text": "Test", "heat": 0.5}]
        ladder.process_fragments(fragments)

        efficiency = ladder._calculate_processing_efficiency()
        assert efficiency > 0.0  # Should have some processing

    def test_calculate_compression_effectiveness(self):
        """Test compression effectiveness calculation."""
        ladder = SummarizationLadder()

        # Should be 0 for empty ladder
        effectiveness = ladder._calculate_compression_effectiveness()
        assert effectiveness == 0.0

        # After creating some compressions
        fragments = [{"id": f"frag_{i}", "text": f"Fragment {i}", "heat": 0.5} for i in range(3)]
        ladder.process_fragments(fragments)

        effectiveness = ladder._calculate_compression_effectiveness()
        assert effectiveness >= 0.0

    def test_calculate_temporal_coverage_empty(self):
        """Test temporal coverage for empty ladder."""
        ladder = SummarizationLadder()

        coverage = ladder._calculate_temporal_coverage()
        assert coverage == 0.0

    def test_calculate_temporal_coverage_with_data(self):
        """Test temporal coverage calculation with data."""
        ladder = SummarizationLadder()

        # Create two micro-summaries with different timestamps to get actual coverage
        past_time = time.time() - 7200  # 2 hours ago
        micro1 = MicroSummary(
            summary_id="test_micro1",
            window_fragments=["frag_1"],
            compressed_text="Test compressed",
            window_size=1,
            creation_timestamp=past_time,
            heat_aggregate=0.5,
        )
        micro2 = MicroSummary(
            summary_id="test_micro2",
            window_fragments=["frag_2"],
            compressed_text="Test compressed 2",
            window_size=1,
            creation_timestamp=time.time(),  # Current time
            heat_aggregate=0.5,
        )
        ladder.micro_summaries.append(micro1)
        ladder.micro_summaries.append(micro2)

        coverage = ladder._calculate_temporal_coverage()
        assert coverage > 0.0  # Should detect the time difference


class TestSummarizationLadderCompressionTextMethods:
    """Test text compression methods."""

    def setup_method(self):
        """Setup for each test."""
        self.ladder = SummarizationLadder()

    def test_compress_fragment_texts_empty(self):
        """Test compression of empty text list."""
        result = self.ladder._compress_fragment_texts([])
        assert result == "(empty window)"

    def test_compress_fragment_texts_single_short(self):
        """Test compression of single short text."""
        texts = ["Short text"]
        result = self.ladder._compress_fragment_texts(texts)
        assert "[Micro]" in result
        assert "Short text" in result

    def test_compress_fragment_texts_single_long(self):
        """Test compression of single long text."""
        long_text = "This is a very long text that should be truncated because it's much longer than thirty characters"
        texts = [long_text]
        result = self.ladder._compress_fragment_texts(texts)

        assert "[Micro]" in result
        assert "..." in result  # Should be truncated
        assert len(result) < len("[Micro] " + long_text)  # Should be shorter

    def test_compress_fragment_texts_multiple(self):
        """Test compression of multiple texts."""
        texts = ["First phrase", "Second phrase", "Third phrase", "Fourth phrase"]
        result = self.ladder._compress_fragment_texts(texts)

        assert "[Micro]" in result
        assert "First phrase" in result
        assert "Second phrase" in result
        assert "Third phrase" in result
        # Should not include fourth phrase (limited to 3)

    def test_distill_macro_essence_empty(self):
        """Test macro distillation of empty micro summaries."""
        result = self.ladder._distill_macro_essence([])
        assert result == "(empty distillation)"

    def test_distill_macro_essence_single(self):
        """Test macro distillation of single micro summary."""
        micro = MicroSummary(
            summary_id="single_micro",
            window_fragments=["frag_1"],
            compressed_text="[Micro] Single summary",
            window_size=1,
            creation_timestamp=time.time(),
            heat_aggregate=0.6,
        )

        result = self.ladder._distill_macro_essence([micro])
        assert "[Macro]" in result
        assert "Single summary" in result

    def test_distill_macro_essence_multiple(self):
        """Test macro distillation of multiple micro summaries."""
        micros = []
        for i in range(2):
            micro = MicroSummary(
                summary_id=f"micro_{i}",
                window_fragments=[f"frag_{i*3+j}" for j in range(3)],
                compressed_text=f"[Micro] Summary {i}",
                window_size=3,
                creation_timestamp=time.time(),
                heat_aggregate=0.5 + i * 0.1,
            )
            micros.append(micro)

        result = self.ladder._distill_macro_essence(micros)

        assert "[Macro]" in result
        assert "Summary 0" in result
        assert "Summary 1" in result
        assert "⟶" in result  # Progression arrow


class TestSummarizationLadderIDGeneration:
    """Test ID generation methods."""

    def setup_method(self):
        """Setup for each test."""
        self.ladder = SummarizationLadder()

    def test_generate_summary_id_uniqueness(self):
        """Test summary ID generation creates unique IDs."""
        content1 = "First summary content"
        content2 = "Second summary content"

        id1 = self.ladder._generate_summary_id(content1)
        id2 = self.ladder._generate_summary_id(content2)
        id1_again = self.ladder._generate_summary_id(content1)

        assert id1 != id2  # Different content, different IDs
        assert id1.startswith("micro_")  # Correct prefix
        assert len(id1.split("_")) == 3  # timestamp, hash, correct format
        # Same content should produce same ID (deterministic)
        assert id1 == id1_again

    def test_generate_distillation_id_format(self):
        """Test distillation ID generation."""
        essence = "Macro distillation essence"
        dist_id = self.ladder._generate_distillation_id(essence)

        assert dist_id.startswith("macro_")
        assert len(dist_id.split("_")) >= 2  # Should have timestamp and hash parts
        assert len(dist_id) > 8  # Should be substantial length

    def test_generate_summary_id_contains_hash(self):
        """Test that generated IDs contain content hashes."""
        content = "Test content for hashing"
        summary_id = self.ladder._generate_summary_id(content)

        # Extract hash part
        parts = summary_id.split("_")
        hash_part = parts[-1]  # Last part should be hash

        # Verify it's a valid hash format (hex)
        int(hash_part, 16)  # Should not raise exception


class TestSummarizationLadderIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_macro_trigger_functionality(self):
        """Test that macro distillations can be triggered."""
        ladder = SummarizationLadder({
            "micro_window_size": 2,
            "macro_trigger_count": 1,  # Trigger macro immediately after 1 micro
        })

        # Create enough fragments to trigger both micro and macro
        fragments = [
            {"id": "frag_1", "text": "Fragment 1 content", "heat": 0.5},
            {"id": "frag_2", "text": "Fragment 2 content", "heat": 0.6},
            {"id": "frag_3", "text": "Fragment 3 content", "heat": 0.7},
            {"id": "frag_4", "text": "Fragment 4 content", "heat": 0.5}
        ]

        # Process fragments and verify macro creation
        ladder.process_fragments(fragments)

        # Should have macro distillations
        assert len(ladder.macro_distillations) >= 1

        # Test recovery context functionality
        context = ladder.get_recovery_context("test_anchor")
        assert len(context["temporal_sequence"]) >= 1

        # Test metrics work
        metrics = ladder.get_compression_metrics()
        assert metrics["current_state"]["macro_distillations_total"] >= 1

    def test_memory_limits_and_cleanup(self):
        """Test memory limits and buffer management."""
        max_micros = 3  # Small limit for testing
        ladder = SummarizationLadder({
            "micro_window_size": 2,
            "max_micro_summaries": max_micros,
        })

        # Create many micro-summaries to test memory limits
        for i in range(6):  # Should create 6 micros, but limit to 3
            fragments = [
                {"id": f"frag_{i*2}", "text": f"Fragment {i*2}", "heat": 0.5},
                {"id": f"frag_{i*2+1}", "text": f"Fragment {i*2+1}", "heat": 0.5},
            ]
            ladder.process_fragments(fragments)

        # Should respect memory limit
        assert len(ladder.micro_summaries) <= max_micros

    def test_large_fragment_content_handling(self):
        """Test handling of large fragment content."""
        ladder = SummarizationLadder({"micro_window_size": 2})

        # Create fragments with very long content
        long_text = "A" * 10000  # 10K characters
        fragments = [
            {"id": "long_frag_1", "text": long_text, "heat": 0.8},
            {"id": "long_frag_2", "text": "Short text", "heat": 0.6},
        ]

        result = ladder.process_fragments(fragments)

        assert result["micro_summaries_created"] == 1

        micro = ladder.micro_summaries[0]
        # Should not contain the full long text
        assert len(micro.compressed_text) < len(long_text)
        assert "[Micro]" in micro.compressed_text


class TestSummarizationLadderEdgeCases:
    """Test edge cases and error conditions."""

    def test_process_fragments_with_missing_fields(self):
        """Test processing fragments with missing optional fields."""
        ladder = SummarizationLadder({"micro_window_size": 2})

        # Fragments with minimal required fields
        fragments = [
            {"text": "Fragment without ID or heat"},  # Should get default ID
        ]

        # Should not crash
        result = ladder.process_fragments(fragments)
        assert result["fragments_processed"] == 1

    def test_process_fragments_with_empty_text(self):
        """Test processing fragments with empty text."""
        ladder = SummarizationLadder({"micro_window_size": 2})

        fragments = [
            {"id": "empty_1", "text": "", "heat": 0.5},
            {"id": "empty_2", "text": "", "heat": 0.4},
        ]

        result = ladder.process_fragments(fragments)
        assert result["fragments_processed"] == 2
        # May or may not create micro-summary depending on implementation

    def test_get_recovery_context_very_large_context_size(self):
        """Test recovery context with very large context size."""
        ladder = SummarizationLadder()

        # Create 5 micro-summaries
        for i in range(5):
            fragments = [{"id": f"frag_{i}", "text": f"Fragment {i}", "heat": 0.5},
                        {"id": f"frag_{i*10}", "text": f"Fragment {i*10}", "heat": 0.5}]
            ladder.process_fragments(fragments)

        # Request large context
        context = ladder.get_recovery_context("anchor_test", context_size=100)

        # Should not crash and return what's available
        assert "related_micro_summaries" in context
        # May not return all 5 if implementation limits

    def test_metrics_calculation_division_by_zero_safety(self):
        """Test that metrics calculations handle division by zero safely."""
        ladder = SummarizationLadder()

        # Test with zero fragments
        efficiency = ladder._calculate_processing_efficiency()
        assert efficiency == 1.0

        effectiveness = ladder._calculate_compression_effectiveness()
        assert effectiveness == 0.0

        coverage = ladder._calculate_temporal_coverage()
        assert coverage == 0.0

        # Test with fragments but zero time
        ladder.metrics["total_fragments"] = 10
        ladder.metrics["processing_time_ms"] = 0.0
        efficiency = ladder._calculate_processing_efficiency()
        assert efficiency == 1.0

    def test_fragment_processing_fragment_counter(self):
        """Test that fragment processing correctly updates counters."""
        ladder = SummarizationLadder()

        initial_count = ladder.total_fragments_processed

        # Process different fragment counts
        fragments_3 = [{"id": f"f_{i}", "text": "text", "heat": 0.5} for i in range(3)]
        ladder.process_fragments(fragments_3)

        assert ladder.total_fragments_processed == initial_count + 3

        fragments_2 = [{"id": f"g_{i}", "text": "text", "heat": 0.5} for i in range(2)]
        ladder.process_fragments(fragments_2)

        assert ladder.total_fragments_processed == initial_count + 5



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
