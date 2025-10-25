from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
import time
import random
import re
from collections import Counter

class EvaporationEngine:
    """Evaporation: converts molten glyphs into mist lines (proto-thoughts) with advanced style bias."""
    def __init__(self, magma_store, cloud_store, config: Optional[Dict[str, Any]] = None):
        self.magma_store = magma_store
        self.cloud_store = cloud_store
        self.config = config or {}

        # Style bias configuration
        self.style_profiles = self._initialize_style_profiles()
        self.current_style = self.config.get("default_style", "balanced")
        self.style_variation = self.config.get("style_variation", 0.3)

        # Language generation parameters
        self.creativity_level = self.config.get("creativity_level", 0.7)
        self.compression_ratio = self.config.get("compression_ratio", 0.6)
        self.mythic_amplification = self.config.get("mythic_amplification", 1.2)

        # Advanced distillation parameters
        self.semantic_density_threshold = self.config.get("semantic_density_threshold", 0.5)
        self.affect_sensitivity = self.config.get("affect_sensitivity", 0.8)
        self.temporal_decay_factor = self.config.get("temporal_decay_factor", 0.1)

    def evaporate(self, limit: int = 5, style_override: Optional[str] = None) -> List[Dict[str, Any]]:
        """Advanced evaporation with style bias and intelligent selection."""
        # Select molten glyphs with enhanced criteria
        molten = self._select_optimal_glyphs(limit * 2)

        mist_lines = []
        for i, glyph in enumerate(molten[:limit]):
            # Apply style variation for diversity
            current_style = style_override or self._determine_style_for_glyph(glyph, i)

            # Advanced mist distillation
            mist = self._advanced_distill_mist(glyph, current_style)
            mist_lines.append(mist)

        # Add to cloud store with metadata
        self.cloud_store.add_mist_lines(mist_lines)

        # Calculate sophisticated humidity
        humidity = self._calculate_advanced_humidity(mist_lines)
        self.cloud_store.update_humidity(humidity)

        # Update generation mode based on mist characteristics
        self._update_generation_mode(mist_lines)

        return mist_lines

    def _select_optimal_glyphs(self, target_count: int) -> List[Dict[str, Any]]:
        """Select optimal glyphs for evaporation based on multiple criteria."""
        molten = self.magma_store.select_hot(target_count * 3)  # Get more candidates

        # Score glyphs based on multiple factors
        scored_glyphs = []
        current_time = time.time()

        for glyph in molten:
            score = 0.0

            # Heat factor (primary)
            score += glyph.get("heat", 0.0) * 0.4

            # Affect diversity factor
            affect = glyph.get("affect", {})
            affect_score = sum(abs(v) for v in affect.values()) / max(len(affect), 1)
            score += affect_score * 0.3

            # Temporal freshness factor
            age = current_time - glyph.get("created_epoch", current_time)
            age_factor = max(0, 1.0 - (age / 86400))  # Decay over 24 hours
            score += age_factor * 0.2

            # Semantic density factor
            summary = glyph.get("compressed_summary", "")
            semantic_density = self._calculate_semantic_density(summary)
            score += semantic_density * 0.1

            scored_glyphs.append((glyph, score))

        # Sort by score and return top candidates
        scored_glyphs.sort(key=lambda x: x[1], reverse=True)
        return [glyph for glyph, _ in scored_glyphs[:target_count]]

    def _determine_style_for_glyph(self, glyph: Dict[str, Any], index: int) -> str:
        """Determine optimal style for a specific glyph."""
        affect = glyph.get("affect", {})
        heat = glyph.get("heat", 0.0)

        # Base style on affect characteristics
        if affect.get("awe", 0) > 0.7:
            base_style = "mythic"
        elif affect.get("curiosity", 0) > 0.6:
            base_style = "exploratory"
        elif affect.get("tension", 0) > 0.5:
            base_style = "dramatic"
        elif heat > 0.8:
            base_style = "intense"
        elif heat > 0.5:
            base_style = "balanced"
        else:
            base_style = "contemplative"

        # Add variation for diversity
        if random.random() < self.style_variation:
            styles = list(self.style_profiles.keys())
            styles.remove(base_style)
            base_style = random.choice(styles)

        return base_style

    def _advanced_distill_mist(self, glyph: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Advanced mist distillation with style bias."""
        summary = glyph.get("compressed_summary", "")
        affect = glyph.get("affect", {})
        heat = glyph.get("heat", 0.0)

        # Get style profile
        style_profile = self.style_profiles.get(style, self.style_profiles["balanced"])

        # Generate proto-thought with style bias
        proto_thought = self._generate_styled_proto_thought(summary, affect, style_profile)

        # Calculate advanced metrics
        evaporation_temp = self._calculate_evaporation_temperature(heat, affect)
        technical_clarity = self._calculate_technical_clarity(summary, style)
        mythic_weight = self._calculate_mythic_weight(affect, style) * self.mythic_amplification

        # Create enhanced mist line
        mist_line = {
            "id": f"mist_{glyph['id'][7:]}",
            "source_glyph": glyph["id"],
            "proto_thought": proto_thought,
            "evaporation_temp": evaporation_temp,
            "mythic_weight": mythic_weight,
            "technical_clarity": technical_clarity,
            "style": style,
            "style_confidence": style_profile.get("confidence", 0.7),
            "semantic_density": self._calculate_semantic_density(summary),
            "affect_signature": self._create_affect_signature(affect),
            "created_epoch": int(time.time()),
            "distillation_quality": self._assess_distillation_quality(proto_thought, summary, affect),
        }
        return mist_line

    def _generate_styled_proto_thought(self, summary: str, affect: Dict[str, Any], style_profile: Dict[str, Any]) -> str:
        """Generate proto-thought with specific style bias."""
        # Extract key concepts from summary
        concepts = self._extract_key_concepts(summary)

        # Apply style transformations
        if style_profile.get("poetic", False):
            proto_thought = self._apply_poetic_style(concepts, affect)
        elif style_profile.get("technical", False):
            proto_thought = self._apply_technical_style(concepts, affect)
        elif style_profile.get("narrative", False):
            proto_thought = self._apply_narrative_style(concepts, affect)
        elif style_profile.get("mythic", False):
            proto_thought = self._apply_mythic_style(concepts, affect)
        else:
            proto_thought = self._apply_balanced_style(concepts, affect)

        # Add affect coloring
        if affect:
            proto_thought = self._apply_affect_coloring(proto_thought, affect)

        # Apply compression based on creativity level
        if self.creativity_level > 0.7:
            proto_thought = self._apply_creative_compression(proto_thought)

        return proto_thought

    def _extract_key_concepts(self, summary: str) -> List[str]:
        """Extract key concepts from summary."""
        # Split by common delimiters
        fragments = re.split(r'[|→,;]', summary)

        # Clean and filter concepts
        concepts = []
        for fragment in fragments:
            concept = fragment.strip()
            if len(concept) > 3 and len(concept) < 100:  # Reasonable length
                concepts.append(concept)

        return concepts[:5]  # Limit to top 5 concepts

    def _apply_poetic_style(self, concepts: List[str], affect: Dict[str, Any]) -> str:
        """Apply poetic style to proto-thought."""
        if not concepts:
            return "[Poetic] Ethereal mist of untold stories..."

        # Poetic connectors and imagery
        poetic_connectors = ["whispers", "dreams", "echoes", "shadows", "light", "flow"]
        poetic_imagery = ["through ancient corridors", "across starlit paths", "within hidden depths", "beyond veiled horizons"]

        connector = random.choice(poetic_connectors)
        imagery = random.choice(poetic_imagery)

        if len(concepts) == 1:
            return f"[Poetic] {concepts[0]} {connector} {imagery}."
        else:
            return f"[Poetic] Where {concepts[0]} and {concepts[1]} {connector} {imagery}."

    def _apply_technical_style(self, concepts: List[str], affect: Dict[str, Any]) -> str:
        """Apply technical style to proto-thought."""
        if not concepts:
            return "[Technical] System processing: null input detected."

        # Technical prefixes and structures
        tech_prefixes = ["System analysis:", "Process optimization:", "Architecture review:", "Implementation note:"]
        tech_connectors = ["enables", "facilitates", "optimizes", "integrates", "synchronizes"]

        prefix = random.choice(tech_prefixes)
        connector = random.choice(tech_connectors)

        if len(concepts) == 1:
            return f"[Technical] {prefix} {concepts[0]} processing complete."
        else:
            return f"[Technical] {prefix} {concepts[0]} {connector} {concepts[1]} subsystem."

    def _apply_narrative_style(self, concepts: List[str], affect: Dict[str, Any]) -> str:
        """Apply narrative style to proto-thought."""
        if not concepts:
            return "[Narrative] Once upon a time, in the realm of forgotten ideas..."

        # Narrative elements
        narrative_openers = ["In the beginning,", "As the story unfolds,", "Beyond the horizon,", "Within the tapestry of"]
        narrative_actions = ["emerges", "dances", "whispers", "journeys", "transforms"]

        opener = random.choice(narrative_openers)
        action = random.choice(narrative_actions)

        if len(concepts) == 1:
            return f"[Narrative] {opener} {concepts[0]} {action} into being."
        else:
            return f"[Narrative] {opener} {concepts[0]} and {concepts[1]} {action} together."

    def _apply_mythic_style(self, concepts: List[str], affect: Dict[str, Any]) -> str:
        """Apply mythic style to proto-thought."""
        if not concepts:
            return "[Mythic] From the primordial void, legends are born..."

        # Mythic elements
        mythic_prefixes = ["Ancient prophecy speaks of", "Legends tell of", "The oracle foretells", "Cosmic wisdom reveals"]
        mythic_entities = ["the eternal flame", "the sacred river", "the celestial dance", "the infinite spiral"]

        prefix = random.choice(mythic_prefixes)
        entity = random.choice(mythic_entities)

        if len(concepts) == 1:
            return f"[Mythic] {prefix} {concepts[0]} as {entity}."
        else:
            return f"[Mythic] {prefix} {concepts[0]} and {concepts[1]} within {entity}."

    def _apply_balanced_style(self, concepts: List[str], affect: Dict[str, Any]) -> str:
        """Apply balanced style to proto-thought."""
        if not concepts:
            return "[Balanced] Contemplation on the nature of existence..."

        if len(concepts) == 1:
            return f"[Balanced] Reflection on {concepts[0]} reveals deeper meaning."
        else:
            return f"[Balanced] The interplay between {concepts[0]} and {concepts[1]} creates harmony."

    def _apply_affect_coloring(self, proto_thought: str, affect: Dict[str, Any]) -> str:
        """Apply affect-based coloring to proto-thought."""
        if not affect:
            return proto_thought

        # Determine dominant affect
        dominant_affect = max(affect.items(), key=lambda x: abs(x[1]))
        affect_name, affect_value = dominant_affect

        if abs(affect_value) < 0.3:
            return proto_thought  # Weak affect, no coloring

        # Apply affect-specific coloring
        if affect_name == "awe" and affect_value > 0:
            return proto_thought.replace("[", "[✨")
        elif affect_name == "curiosity" and affect_value > 0:
            return proto_thought.replace("[", "[🔍")
        elif affect_name == "tension" and affect_value > 0:
            return proto_thought.replace("[", "[⚡")
        elif affect_name == "wonder" and affect_value > 0:
            return proto_thought.replace("[", "[🌟")
        else:
            return proto_thought

    def _apply_creative_compression(self, proto_thought: str) -> str:
        """Apply creative compression to proto-thought."""
        # Remove redundant words while preserving meaning
        words = proto_thought.split()
        if len(words) > 15:
            # Keep first, middle, and last parts
            keep_first = words[:5]
            keep_middle = words[len(words)//2-2:len(words)//2+2]
            keep_last = words[-3:]
            compressed = keep_first + ["..."] + keep_middle + ["..."] + keep_last
            return " ".join(compressed)
        return proto_thought

    def _calculate_advanced_humidity(self, mist_lines: List[Dict[str, Any]]) -> float:
        """Calculate sophisticated humidity based on multiple factors."""
        if not mist_lines:
            return 0.0

        # Base humidity from mist density
        base_humidity = min(len(mist_lines) / 20.0, 0.8)  # Cap at 0.8 for density

        # Mythic weight contribution
        total_mythic = sum(m.get("mythic_weight", 0.0) for m in mist_lines)
        avg_mythic = total_mythic / len(mist_lines)
        mythic_contribution = avg_mythic * 0.3

        # Technical clarity contribution (inverse relationship)
        avg_clarity = sum(m.get("technical_clarity", 0.5) for m in mist_lines) / len(mist_lines)
        clarity_contribution = (1.0 - avg_clarity) * 0.1  # Less clear = more humid

        # Style diversity contribution
        styles = [m.get("style", "balanced") for m in mist_lines]
        style_diversity = len(set(styles)) / len(styles) if styles else 0
        diversity_contribution = style_diversity * 0.15

        # Affect intensity contribution
        total_affect = 0
        for mist in mist_lines:
            affect_sig = mist.get("affect_signature", {})
            total_affect += sum(abs(v) for v in affect_sig.values())
        avg_affect = total_affect / len(mist_lines) if mist_lines else 0
        affect_contribution = min(avg_affect * 0.2, 0.3)

        # Combine all factors
        total_humidity = base_humidity + mythic_contribution + clarity_contribution + diversity_contribution + affect_contribution

        return min(0.95, max(0.1, total_humidity))  # Bound between 0.1 and 0.95

    def _update_generation_mode(self, mist_lines: List[Dict[str, Any]]):
        """Update cloud store generation mode based on mist characteristics."""
        if not mist_lines:
            return

        # Analyze mist characteristics
        avg_mythic = sum(m.get("mythic_weight", 0.0) for m in mist_lines) / len(mist_lines)
        avg_clarity = sum(m.get("technical_clarity", 0.5) for m in mist_lines) / len(mist_lines)
        styles = [m.get("style", "balanced") for m in mist_lines]
        style_diversity = len(set(styles)) / len(styles) if styles else 0

        # Determine generation mode
        if avg_mythic > 0.7 and style_diversity > 0.6:
            mode = "creative"
        elif avg_clarity > 0.8 and avg_mythic < 0.3:
            mode = "analytical"
        elif style_diversity > 0.8:
            mode = "exploratory"
        elif avg_mythic > 0.5:
            mode = "balanced"
        else:
            mode = "focused"

        self.cloud_store.generation_mode = mode

    # Helper methods for advanced calculations
    def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density of text."""
        if not text:
            return 0.0

        words = text.split()
        unique_words = set(word.lower() for word in words if len(word) > 3)

        if not words:
            return 0.0

        # Density = unique meaningful words / total words
        density = len(unique_words) / len(words)

        # Adjust for length (very short or very long texts get penalty)
        length_factor = 1.0
        if len(words) < 5:
            length_factor = 0.5
        elif len(words) > 50:
            length_factor = 0.8

        return min(1.0, density * length_factor)

    def _calculate_evaporation_temperature(self, heat: float, affect: Dict[str, Any]) -> float:
        """Calculate evaporation temperature based on heat and affect."""
        base_temp = heat * 0.8  # Primary factor from heat

        # Affect modulation
        affect_intensity = sum(abs(v) for v in affect.values()) / max(len(affect), 1)
        affect_modulation = affect_intensity * 0.2

        # Combine and bound
        temperature = base_temp + affect_modulation
        return min(1.0, max(0.1, temperature))

    def _calculate_technical_clarity(self, summary: str, style: str) -> float:
        """Calculate technical clarity based on summary and style."""
        base_clarity = 0.7  # Default clarity

        # Style-based adjustments
        style_clarity = {
            "technical": 0.9,
            "balanced": 0.7,
            "poetic": 0.4,
            "narrative": 0.5,
            "mythic": 0.3,
            "exploratory": 0.6,
            "contemplative": 0.8,
            "intense": 0.5,
            "dramatic": 0.4
        }

        clarity = style_clarity.get(style, base_clarity)

        # Summary complexity adjustment
        if summary:
            complexity = len(summary.split()) / 20.0  # Normalize by expected length
            complexity_adjustment = max(-0.2, min(0.2, (0.5 - complexity) * 0.4))
            clarity += complexity_adjustment

        return min(1.0, max(0.1, clarity))

    def _calculate_mythic_weight(self, affect: Dict[str, Any], style: str) -> float:
        """Calculate mythic weight based on affect and style."""
        base_weight = affect.get("awe", 0.0) * 0.6 + affect.get("wonder", 0.0) * 0.4

        # Style multipliers
        style_multipliers = {
            "mythic": 1.5,
            "poetic": 1.2,
            "narrative": 1.1,
            "dramatic": 1.0,
            "balanced": 0.8,
            "technical": 0.5,
            "exploratory": 0.7,
            "contemplative": 0.9,
            "intense": 1.1
        }

        multiplier = style_multipliers.get(style, 1.0)
        return min(1.0, base_weight * multiplier)

    def _create_affect_signature(self, affect: Dict[str, Any]) -> Dict[str, float]:
        """Create normalized affect signature."""
        if not affect:
            return {}

        # Normalize affect values
        total_intensity = sum(abs(v) for v in affect.values())
        if total_intensity == 0:
            return {}

        signature = {}
        for key, value in affect.items():
            signature[key] = value / total_intensity

        return signature

    def _assess_distillation_quality(self, proto_thought: str, original_summary: str, affect: Dict[str, Any]) -> float:
        """Assess the quality of distillation."""
        if not proto_thought:
            return 0.0

        quality_score = 0.5  # Base score

        # Length appropriateness
        proto_length = len(proto_thought.split())
        if 5 <= proto_length <= 20:
            quality_score += 0.2
        elif proto_length > 20:
            quality_score -= 0.1

        # Concept preservation
        original_concepts = set(self._extract_key_concepts(original_summary))
        proto_concepts = set(self._extract_key_concepts(proto_thought))

        if original_concepts:
            preservation = len(original_concepts & proto_concepts) / len(original_concepts)
            quality_score += preservation * 0.2

        # Affect alignment
        if affect:
            affect_words = ["awe", "wonder", "curiosity", "tension"]
            affect_alignment = sum(1 for word in affect_words if word in proto_thought.lower()) * 0.05
            quality_score += min(0.1, affect_alignment)

        return min(1.0, max(0.0, quality_score))

    def _initialize_style_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize style profiles for mist generation."""
        return {
            "balanced": {
                "poetic": False,
                "technical": False,
                "narrative": False,
                "mythic": False,
                "confidence": 0.7,
                "creativity": 0.5
            },
            "poetic": {
                "poetic": True,
                "technical": False,
                "narrative": False,
                "mythic": False,
                "confidence": 0.8,
                "creativity": 0.9
            },
            "technical": {
                "poetic": False,
                "technical": True,
                "narrative": False,
                "mythic": False,
                "confidence": 0.9,
                "creativity": 0.3
            },
            "narrative": {
                "poetic": False,
                "technical": False,
                "narrative": True,
                "mythic": False,
                "confidence": 0.7,
                "creativity": 0.7
            },
            "mythic": {
                "poetic": False,
                "technical": False,
                "narrative": False,
                "mythic": True,
                "confidence": 0.8,
                "creativity": 0.8
            },
            "exploratory": {
                "poetic": True,
                "technical": False,
                "narrative": True,
                "mythic": False,
                "confidence": 0.6,
                "creativity": 0.8
            },
            "contemplative": {
                "poetic": False,
                "technical": False,
                "narrative": False,
                "mythic": False,
                "confidence": 0.8,
                "creativity": 0.4
            },
            "intense": {
                "poetic": False,
                "technical": True,
                "narrative": True,
                "mythic": False,
                "confidence": 0.9,
                "creativity": 0.6
            },
            "dramatic": {
                "poetic": True,
                "technical": False,
                "narrative": True,
                "mythic": False,
                "confidence": 0.8,
                "creativity": 0.7
            }
        }

class CloudStore:
    def __init__(self):
        self.mist_lines = []
        self.humidity_index = 0.0
        self.generation_mode = "balanced"

    def add_mist_lines(self, mist_lines: List[Dict[str, Any]]):
        self.mist_lines.extend(mist_lines)

    def update_humidity(self, humidity: float):
        self.humidity_index = humidity

    def get_active_mist(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get active mist lines filtered by recency and activity."""
        if not self.mist_lines:
            return []

        current_time = time.time()

        # Score mist lines based on multiple factors
        scored_mist = []
        for mist in self.mist_lines:
            score = 0.0

            # Recency factor (newer is better)
            age = current_time - mist.get("created_epoch", current_time)
            recency_score = max(0, 1.0 - (age / 3600))  # Decay over 1 hour
            score += recency_score * 0.4

            # Quality factor
            quality = mist.get("distillation_quality", 0.5)
            score += quality * 0.3

            # Mythic weight factor
            mythic = mist.get("mythic_weight", 0.0)
            score += mythic * 0.2

            # Style confidence factor
            style_confidence = mist.get("style_confidence", 0.5)
            score += style_confidence * 0.1

            scored_mist.append((mist, score))

        # Sort by score and return top results
        scored_mist.sort(key=lambda x: x[1], reverse=True)
        return [mist for mist, _ in scored_mist[:limit]]
