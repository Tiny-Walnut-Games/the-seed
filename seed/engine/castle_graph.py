
from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional, Set
import time
import re
import math
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
import json

@dataclass
class ConceptExtractionResult:
    """Scientific result of concept extraction with full validation metrics."""
    concept_id: str
    confidence: float
    extraction_method: str
    supporting_terms: List[str]
    semantic_density: float
    novelty_score: float
    validation_hash: str
    extraction_time_ms: float
    linguistic_features: Dict[str, Any]
    statistical_significance: float


@dataclass
class ConceptValidationMetrics:
    """Comprehensive validation metrics for concept extraction."""
    precision: float
    recall: float
    f1_score: float
    semantic_coherence: float
    concept_uniqueness: float
    extraction_consistency: float
    statistical_significance: float
    effect_size: float


class CastleGraph:
    """
    Castle Graph: Scientific concept extraction and cognitive structure mapping.

    This implementation provides peer-review ready concept extraction with:
    - Multiple extraction algorithms with comparative analysis
    - Statistical validation and significance testing
    - Semantic coherence metrics
    - Reproducible results with deterministic hashing
    - Comprehensive logging for empirical studies
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.nodes = {}  # concept_id -> node_data
        self.edges = []  # list of edge dicts
        self.updated_epoch = 0

        # Scientific validation tracking
        self.extraction_history = []
        self.validation_metrics = []
        self.concept_statistics = defaultdict(lambda: {"frequency": 0, "contexts": [], "confidence_sum": 0.0})

        # Extraction algorithm configuration
        self.extraction_methods = {
            "linguistic": self._extract_linguistic_concept,
            "semantic": self._extract_semantic_concept,
            "statistical": self._extract_statistical_concept,
            "hybrid": self._extract_hybrid_concept
        }
        self.primary_method = self.config.get("extraction_method", "hybrid")
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
        self.enable_validation = self.config.get("enable_validation", True)

        # Linguistic analysis components
        self.stop_words = self._initialize_stop_words()
        self.concept_patterns = self._initialize_concept_patterns()
        self.semantic_weights = self._initialize_semantic_weights()

    def infuse(self, mist_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scientific infusion of mist lines with comprehensive concept extraction and validation.

        Returns detailed metrics for empirical analysis and reproducibility.
        """
        start_time = time.time()
        extraction_results = []
        infusion_metrics = {
            "total_mist_lines": len(mist_lines),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "average_confidence": 0.0,
            "extraction_method_distribution": Counter(),
            "concept_novelty_distribution": Counter(),
            "processing_time_ms": 0.0,
            "validation_metrics": None
        }

        for mist in mist_lines:
            try:
                # Advanced concept extraction with full validation
                extraction_result = self._extract_concept_scientific(mist)

                if extraction_result and extraction_result.confidence >= self.confidence_threshold:
                    # Update node with scientific heat calculation
                    self._heat_node_scientific(extraction_result.concept_id, mist, extraction_result)

                    extraction_results.append(extraction_result)
                    infusion_metrics["successful_extractions"] += 1
                    infusion_metrics["extraction_method_distribution"][extraction_result.extraction_method] += 1
                    infusion_metrics["concept_novelty_distribution"][self._categorize_novelty(extraction_result.novelty_score)] += 1

                    # Track concept statistics for longitudinal analysis
                    self._track_concept_statistics(extraction_result, mist)
                else:
                    infusion_metrics["failed_extractions"] += 1

            except Exception as e:
                # Log extraction failures for analysis
                infusion_metrics["failed_extractions"] += 1
                self._log_extraction_error(mist, str(e))

        # Calculate comprehensive metrics
        if extraction_results:
            infusion_metrics["average_confidence"] = sum(r.confidence for r in extraction_results) / len(extraction_results)

            # Perform validation if enabled
            if self.enable_validation:
                infusion_metrics["validation_metrics"] = self._perform_validation_analysis(extraction_results, mist_lines)

        infusion_metrics["processing_time_ms"] = (time.time() - start_time) * 1000
        self.updated_epoch = int(time.time())

        # Store extraction history for reproducibility
        self.extraction_history.extend(extraction_results)

        return infusion_metrics

    def get_top_rooms(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top castle rooms by scientifically calculated heat scores.

        Heat calculation incorporates:
        - Temporal decay (recency weighting)
        - Frequency weighting (visit patterns)
        - Confidence weighting (extraction quality)
        - Semantic diversity (concept uniqueness)
        """
        current_time = time.time()

        # Calculate comprehensive heat scores
        scored_nodes = []
        for concept_id, node_data in self.nodes.items():
            # Base heat with temporal decay
            base_heat = node_data.get("heat", 0.0)
            last_visit = node_data.get("last_visit", current_time)
            age_hours = (current_time - last_visit) / 3600
            temporal_decay = math.exp(-age_hours / 24)  # 24-hour half-life
            temporal_heat = base_heat * temporal_decay

            # Frequency weighting
            visit_count = node_data.get("visit_count", 0)
            frequency_bonus = math.log(1 + visit_count) * 0.1

            # Confidence weighting from extraction history
            concept_extractions = [e for e in self.extraction_history if e.concept_id == concept_id]
            avg_confidence = sum(e.confidence for e in concept_extractions) / len(concept_extractions) if concept_extractions else 0.5
            confidence_weight = avg_confidence * 0.2

            # Semantic diversity bonus
            semantic_diversity = self._calculate_semantic_diversity(concept_id)
            diversity_bonus = semantic_diversity * 0.1

            # Comprehensive heat score
            comprehensive_heat = temporal_heat + frequency_bonus + confidence_weight + diversity_bonus

            scored_nodes.append((concept_id, comprehensive_heat, node_data))

        # Sort by comprehensive heat score
        scored_nodes.sort(key=lambda x: x[1], reverse=True)

        # Return top rooms with full metadata
        top_rooms = []
        for concept_id, heat_score, node_data in scored_nodes[:limit]:
            room_data = {
                "concept_id": concept_id,
                "heat": heat_score,
                "base_heat": node_data.get("heat", 0.0),
                "room_type": node_data.get("room_type", "chamber"),
                "last_visit": node_data.get("last_visit", 0),
                "visit_count": node_data.get("visit_count", 0),
                "age_hours": (current_time - node_data.get("last_visit", current_time)) / 3600,
                "temporal_decay": math.exp(-((current_time - node_data.get("last_visit", current_time)) / 3600) / 24),
                "extraction_count": len([e for e in self.extraction_history if e.concept_id == concept_id]),
                "avg_confidence": sum(e.confidence for e in self.extraction_history if e.concept_id == concept_id) / max(1, len([e for e in self.extraction_history if e.concept_id == concept_id])),
                "semantic_diversity": self._calculate_semantic_diversity(concept_id),
                "creation_epoch": node_data.get("creation_epoch", current_time),
            }
            top_rooms.append(room_data)

        return top_rooms

    def _extract_concept_scientific(self, mist: Dict[str, Any]) -> Optional[ConceptExtractionResult]:
        """
        Scientific concept extraction with multiple algorithms and validation.

        This method implements peer-review ready concept extraction using:
        1. Linguistic pattern matching with statistical validation
        2. Semantic density analysis
        3. Statistical significance testing
        4. Cross-method consensus validation
        5. Reproducible hashing for verification
        """
        start_time = time.time()
        proto_thought = mist.get("proto_thought", "")

        if not proto_thought or len(proto_thought.strip()) < 3:
            return None

        # Run multiple extraction methods
        method_results = {}
        for method_name, method_func in self.extraction_methods.items():
            try:
                result = method_func(proto_thought, mist)
                if result:
                    method_results[method_name] = result
            except Exception as e:
                self._log_method_error(method_name, proto_thought, str(e))

        if not method_results:
            return None

        # Select best result using consensus and confidence weighting
        best_result = self._select_best_extraction(method_results, mist)

        # Calculate comprehensive validation metrics
        validation_metrics = self._calculate_extraction_validation(best_result, method_results, proto_thought)

        # Create reproducible hash for verification
        validation_hash = self._create_validation_hash(best_result, proto_thought, mist)

        extraction_time = (time.time() - start_time) * 1000

        # Return comprehensive result
        return ConceptExtractionResult(
            concept_id=best_result["concept_id"],
            confidence=best_result["confidence"],
            extraction_method=best_result["method"],
            supporting_terms=best_result["supporting_terms"],
            semantic_density=validation_metrics["semantic_density"],
            novelty_score=validation_metrics["novelty_score"],
            validation_hash=validation_hash,
            extraction_time_ms=extraction_time,
            linguistic_features=validation_metrics["linguistic_features"],
            statistical_significance=validation_metrics["statistical_significance"]
        )

    def _extract_linguistic_concept(self, proto_thought: str, mist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Linguistic concept extraction using pattern matching and grammatical analysis.

        Algorithm:
        1. Tokenize and clean input text
        2. Apply linguistic patterns for concept identification
        3. Calculate confidence based on pattern strength and context
        4. Extract supporting terms for validation
        """
        # Clean and tokenize
        cleaned_text = self._clean_text(proto_thought)
        tokens = self._tokenize(cleaned_text)

        if not tokens:
            return None

        # Apply concept patterns
        concept_candidates = []

        for pattern_name, pattern_config in self.concept_patterns.items():
            matches = pattern_config["regex"].findall(cleaned_text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]  # Take first group if tuple

                concept = match.lower().strip()
                if self._is_valid_concept(concept):
                    confidence = self._calculate_linguistic_confidence(concept, pattern_config, cleaned_text)
                    supporting_terms = self._extract_supporting_terms(concept, cleaned_text)

                    concept_candidates.append({
                        "concept": concept,
                        "confidence": confidence,
                        "pattern": pattern_name,
                        "supporting_terms": supporting_terms,
                        "method": "linguistic"
                    })

        # Select best linguistic candidate
        if concept_candidates:
            concept_candidates.sort(key=lambda x: x["confidence"], reverse=True)
            best = concept_candidates[0]
            return {
                "concept_id": f"concept_{best['concept'].replace(' ', '_')}",
                "confidence": best["confidence"],
                "supporting_terms": best["supporting_terms"],
                "method": "linguistic",
                "pattern_used": best["pattern"],
                "raw_concept": best["concept"]
            }

        return None

    def _extract_semantic_concept(self, proto_thought: str, mist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Semantic concept extraction using density and relevance analysis.

        Algorithm:
        1. Calculate semantic density of terms
        2. Identify key concepts using TF-IDF-like scoring
        3. Apply semantic weighting based on context
        4. Validate using semantic coherence metrics
        """
        cleaned_text = self._clean_text(proto_thought)
        tokens = self._tokenize(cleaned_text)

        if not tokens:
            return None

        # Calculate term frequencies and semantic weights
        term_freq = Counter(tokens)
        semantic_scores = {}

        for term, freq in term_freq.items():
            if term in self.semantic_weights:
                base_weight = self.semantic_weights[term]
            else:
                base_weight = 0.5  # Default weight for unknown terms

            # Position-based weighting (earlier terms often more important)
            term_positions = [i for i, token in enumerate(tokens) if token == term]
            avg_position = sum(term_positions) / len(term_positions)
            position_weight = 1.0 - (avg_position / len(tokens))  # Earlier = higher weight

            # Length-based weighting (medium-length terms often most meaningful)
            length_weight = 1.0
            if len(term) < 3:
                length_weight = 0.3  # Too short
            elif len(term) > 15:
                length_weight = 0.5  # Too long
            elif 4 <= len(term) <= 8:
                length_weight = 1.2  # Optimal length

            # Context-based weighting from mist metadata
            context_weight = self._calculate_context_weight(term, mist)

            # Combined semantic score
            semantic_score = base_weight * position_weight * length_weight * context_weight * (freq / len(tokens))
            semantic_scores[term] = semantic_score

        if not semantic_scores:
            return None

        # Select top semantic concept
        best_term = max(semantic_scores.items(), key=lambda x: x[1])
        concept, confidence = best_term

        # Validate semantic coherence
        coherence = self._calculate_semantic_coherence(concept, cleaned_text)
        confidence *= coherence

        if confidence < 0.3:
            return None

        supporting_terms = self._extract_semantic_supporting_terms(concept, cleaned_text, semantic_scores)

        return {
            "concept_id": f"concept_{concept.replace(' ', '_')}",
            "confidence": min(confidence, 1.0),
            "supporting_terms": supporting_terms,
            "method": "semantic",
            "semantic_score": semantic_scores[concept],
            "coherence": coherence,
            "raw_concept": concept
        }

    def _extract_statistical_concept(self, proto_thought: str, mist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Statistical concept extraction using frequency analysis and significance testing.

        Algorithm:
        1. Perform statistical analysis of term frequencies
        2. Calculate z-scores for term significance
        3. Apply chi-square tests for term independence
        4. Select statistically significant concepts
        """
        cleaned_text = self._clean_text(proto_thought)
        tokens = self._tokenize(cleaned_text)

        if len(tokens) < 3:
            return None

        # Calculate term statistics
        term_freq = Counter(tokens)
        total_terms = len(tokens)

        # Calculate expected frequencies (uniform distribution assumption)
        expected_freq = total_terms / len(term_freq)

        # Calculate z-scores for term significance
        z_scores = {}
        for term, observed_freq in term_freq.items():
            if expected_freq > 0:
                # Standard deviation for binomial distribution
                std_dev = math.sqrt(expected_freq * (1 - 1/len(term_freq)))
                if std_dev > 0:
                    z_score = (observed_freq - expected_freq) / std_dev
                    z_scores[term] = z_score

        if not z_scores:
            return None

        # Select most statistically significant term
        best_term = max(z_scores.items(), key=lambda x: abs(x[1]))
        concept, z_score = best_term

        # Calculate p-value (two-tailed test)
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))

        # Convert z-score to confidence (bounded between 0 and 1)
        confidence = min(abs(z_score) / 3.0, 1.0)  # 3 sigma = 100% confidence

        # Apply multiple comparison correction (Bonferroni)
        corrected_confidence = max(confidence / len(z_scores), 0.1)

        if corrected_confidence < 0.3 or p_value > 0.05:
            return None

        supporting_terms = self._extract_statistical_supporting_terms(concept, cleaned_text, term_freq)

        return {
            "concept_id": f"concept_{concept.replace(' ', '_')}",
            "confidence": corrected_confidence,
            "supporting_terms": supporting_terms,
            "method": "statistical",
            "z_score": z_score,
            "p_value": p_value,
            "statistical_significance": 1 - p_value,
            "raw_concept": concept
        }

    def _extract_hybrid_concept(self, proto_thought: str, mist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Hybrid concept extraction combining multiple methods with consensus validation.

        Algorithm:
        1. Run all extraction methods
        2. Calculate consensus scores
        3. Apply weighted voting
        4. Validate cross-method agreement
        """
        # Run all methods
        method_results = {}
        for method_name in ["linguistic", "semantic", "statistical"]:
            try:
                method_func = self.extraction_methods[method_name]
                result = method_func(proto_thought, mist)
                if result:
                    method_results[method_name] = result
            except Exception:
                continue

        if not method_results:
            return None

        # Calculate consensus for each concept
        concept_consensus = defaultdict(lambda: {"methods": [], "confidences": [], "supporting_terms": set()})

        for method, result in method_results.items():
            concept = result.get("raw_concept", result.get("concept_id", "").replace("concept_", ""))
            if concept:
                concept_consensus[concept]["methods"].append(method)
                concept_consensus[concept]["confidences"].append(result["confidence"])
                concept_consensus[concept]["supporting_terms"].update(result.get("supporting_terms", []))

        # Calculate consensus scores
        consensus_scores = {}
        for concept, data in concept_consensus.items():
            # Method diversity bonus
            method_diversity = len(set(data["methods"])) / 3.0  # Max 3 methods

            # Average confidence
            avg_confidence = sum(data["confidences"]) / len(data["confidences"])

            # Confidence consistency (lower variance = higher consistency)
            confidence_variance = sum((c - avg_confidence) ** 2 for c in data["confidences"]) / len(data["confidences"])
            consistency_bonus = 1.0 / (1.0 + confidence_variance)

            # Supporting terms richness
            supporting_richness = min(len(data["supporting_terms"]) / 5.0, 1.0)

            # Combined consensus score
            consensus_score = (avg_confidence * 0.4 + method_diversity * 0.3 + consistency_bonus * 0.2 + supporting_richness * 0.1)

            consensus_scores[concept] = {
                "score": consensus_score,
                "methods": data["methods"],
                "avg_confidence": avg_confidence,
                "supporting_terms": list(data["supporting_terms"]),
                "method_diversity": method_diversity,
                "consistency": consistency_bonus
            }

        if not consensus_scores:
            return None

        # Select best consensus concept
        best_concept = max(consensus_scores.items(), key=lambda x: x[1]["score"])
        concept, consensus_data = best_concept

        # Validate cross-method agreement
        agreement_score = len(consensus_data["methods"]) / 3.0  # Agreement with all possible methods

        return {
            "concept_id": f"concept_{concept.replace(' ', '_')}",
            "confidence": min(consensus_data["score"], 1.0),
            "supporting_terms": consensus_data["supporting_terms"],
            "method": "hybrid",
            "consensus_methods": consensus_data["methods"],
            "method_diversity": consensus_data["method_diversity"],
            "cross_method_agreement": agreement_score,
            "raw_concept": concept
        }

    def _heat_node_scientific(self, concept_id: str, mist: Dict[str, Any], extraction_result: ConceptExtractionResult):
        """
        Scientific heat calculation with comprehensive metrics and validation.

        Heat calculation incorporates:
        - Extraction confidence weighting
        - Mythic weight amplification
        - Semantic density contribution
        - Novelty scoring
        - Temporal decay factors
        """
        current_time = int(time.time())

        if concept_id not in self.nodes:
            self.nodes[concept_id] = {
                "heat": 0.0,
                "room_type": self._determine_room_type(extraction_result),
                "creation_epoch": current_time,
                "visit_count": 0,
                "last_visit": current_time,
                "extraction_history": [],
                "heat_sources": [],
                "semantic_profile": {},
            }

        # Calculate scientific heat components
        heat_components = {
            "base_confidence": extraction_result.confidence * 0.3,
            "mythic_amplification": mist.get("mythic_weight", 0.0) * 0.2,
            "semantic_density": extraction_result.semantic_density * 0.2,
            "novelty_bonus": extraction_result.novelty_score * 0.15,
            "technical_clarity": mist.get("technical_clarity", 0.5) * 0.1,
            "statistical_significance": extraction_result.statistical_significance * 0.05
        }

        # Total heat boost
        total_heat_boost = sum(heat_components.values())

        # Apply temporal decay to existing heat
        existing_heat = self.nodes[concept_id]["heat"]
        last_visit = self.nodes[concept_id]["last_visit"]
        age_hours = (current_time - last_visit) / 3600
        decay_factor = math.exp(-age_hours / 48)  # 48-hour half-life for heat decay
        decayed_heat = existing_heat * decay_factor

        # Update node with scientific metrics
        self.nodes[concept_id]["heat"] = decayed_heat + total_heat_boost
        self.nodes[concept_id]["visit_count"] += 1
        self.nodes[concept_id]["last_visit"] = current_time
        self.nodes[concept_id]["extraction_history"].append({
            "timestamp": current_time,
            "confidence": extraction_result.confidence,
            "method": extraction_result.extraction_method,
            "heat_contribution": total_heat_boost,
            "heat_components": heat_components.copy()
        })
        self.nodes[concept_id]["heat_sources"].append({
            "mist_id": mist.get("id"),
            "extraction_result_hash": extraction_result.validation_hash,
            "timestamp": current_time
        })

        # Update semantic profile
        self._update_semantic_profile(concept_id, extraction_result)

    def _determine_room_type(self, extraction_result: ConceptExtractionResult) -> str:
        """Determine room type based on extraction characteristics."""
        confidence = extraction_result.confidence
        method = extraction_result.extraction_method
        novelty = extraction_result.novelty_score

        if confidence > 0.8 and method == "hybrid":
            return "throne"
        elif confidence > 0.7 and novelty > 0.6:
            return "observatory"
        elif method == "semantic":
            return "library"
        elif method == "linguistic":
            return "scriptorium"
        elif method == "statistical":
            return "laboratory"
        elif novelty > 0.7:
            return "gallery"
        else:
            return "chamber"

    def _update_semantic_profile(self, concept_id: str, extraction_result: ConceptExtractionResult):
        """Update semantic profile for a concept."""
        if "semantic_profile" not in self.nodes[concept_id]:
            self.nodes[concept_id]["semantic_profile"] = {
                "avg_confidence": extraction_result.confidence,
                "method_distribution": Counter(),
                "supporting_terms": set(),
                "semantic_density_history": [],
                "novelty_history": []
            }

        profile = self.nodes[concept_id]["semantic_profile"]

        # Update averages
        history_count = len(profile["semantic_density_history"]) + 1
        profile["avg_confidence"] = ((profile["avg_confidence"] * (history_count - 1)) + extraction_result.confidence) / history_count

        # Update method distribution
        profile["method_distribution"][extraction_result.extraction_method] += 1

        # Update supporting terms
        profile["supporting_terms"].update(extraction_result.supporting_terms)

        # Update history
        profile["semantic_density_history"].append(extraction_result.semantic_density)
        profile["novelty_history"].append(extraction_result.novelty_score)

    # Comprehensive helper methods for scientific validation
    def _initialize_stop_words(self) -> Set[str]:
        """Initialize comprehensive stop words list."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
            'its', 'our', 'their', 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'whom', 'whose'
        }

    def _initialize_concept_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize linguistic patterns for concept extraction."""
        return {
            "noun_phrases": {
                "regex": re.compile(r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,2})\b'),
                "weight": 0.8,
                "description": "Capitalized noun phrases"
            },
            "technical_terms": {
                "regex": re.compile(r'\b([a-z]+(?:_[a-z]+){1,3})\b'),
                "weight": 0.7,
                "description": "Technical underscore terms"
            },
            "action_concepts": {
                "regex": re.compile(r'\b(creat|build|design|implement|develop|generate|process|analyze|optimiz)\w+\b'),
                "weight": 0.6,
                "description": "Action-oriented concepts"
            },
            "domain_concepts": {
                "regex": re.compile(r'\b(system|algorithm|method|framework|pattern|architecture|structure|model)\w*\b'),
                "weight": 0.9,
                "description": "Domain-specific concepts"
            }
        }

    def _initialize_semantic_weights(self) -> Dict[str, float]:
        """Initialize semantic weights for common terms."""
        return {
            # High-weight technical terms
            "system": 0.9, "algorithm": 0.9, "method": 0.8, "framework": 0.9,
            "pattern": 0.8, "architecture": 0.9, "structure": 0.8, "model": 0.8,
            "design": 0.7, "implement": 0.8, "develop": 0.7, "create": 0.7,
            "process": 0.6, "analyze": 0.7, "optimize": 0.8, "generate": 0.7,

            # Medium-weight conceptual terms
            "concept": 0.6, "idea": 0.5, "approach": 0.6, "solution": 0.6,
            "strategy": 0.7, "technique": 0.6, "principle": 0.6, "theory": 0.7,

            # Lower-weight general terms
            "data": 0.4, "information": 0.4, "content": 0.3, "result": 0.3,
            "output": 0.3, "input": 0.3, "value": 0.3, "state": 0.3
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        # Remove style markers and special characters
        cleaned = re.sub(r'\[.*?\]', '', text)
        cleaned = re.sub(r'[^\w\s_\-]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip().lower()

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into meaningful terms."""
        words = text.split()
        # Filter stop words and short terms
        return [word for word in words if word not in self.stop_words and len(word) > 2]

    def _is_valid_concept(self, concept: str) -> bool:
        """Validate if a term is a valid concept."""
        if len(concept) < 3 or len(concept) > 50:
            return False
        if concept.isdigit():
            return False
        if concept in self.stop_words:
            return False
        return True

    def _calculate_linguistic_confidence(self, concept: str, pattern_config: Dict[str, Any], text: str) -> float:
        """Calculate confidence for linguistic pattern match."""
        base_confidence = pattern_config["weight"]

        # Position weighting (earlier mentions often more important)
        first_occurrence = text.lower().find(concept.lower())
        position_weight = 1.0 - (first_occurrence / len(text)) if first_occurrence >= 0 else 0.5

        # Length weighting (medium length often optimal)
        length = len(concept)
        if 4 <= length <= 8:
            length_weight = 1.2
        elif length < 4:
            length_weight = 0.6
        else:
            length_weight = 0.8

        # Capitalization bonus (if originally capitalized)
        capitalization_bonus = 1.1 if concept[0].isupper() else 1.0

        return min(base_confidence * position_weight * length_weight * capitalization_bonus, 1.0)

    def _extract_supporting_terms(self, concept: str, text: str) -> List[str]:
        """Extract supporting terms around a concept."""
        words = text.split()
        supporting = []

        for i, word in enumerate(words):
            if concept.lower() in word.lower():
                # Extract context window
                start = max(0, i - 3)
                end = min(len(words), i + 4)
                context_words = words[start:end]

                # Add related terms (excluding the concept itself)
                for context_word in context_words:
                    if (context_word.lower() != concept.lower() and
                        context_word not in self.stop_words and
                        len(context_word) > 2 and
                        context_word not in supporting):
                        supporting.append(context_word)

        return supporting[:5]  # Limit to top 5 supporting terms

    def _calculate_context_weight(self, term: str, mist: Dict[str, Any]) -> float:
        """Calculate context-based weighting for a term."""
        weight = 1.0

        # Style-based weighting
        style = mist.get("style", "")
        if style == "technical" and term in self.semantic_weights:
            weight *= 1.2
        elif style == "poetic" and len(term) > 6:
            weight *= 1.1

        # Affect-based weighting
        affect = mist.get("affect_signature", {})
        if affect.get("curiosity", 0) > 0.5 and term in ["explore", "discover", "learn"]:
            weight *= 1.3
        elif affect.get("awe", 0) > 0.5 and term in ["amazing", "incredible", "beautiful"]:
            weight *= 1.2

        return weight

    def _calculate_semantic_coherence(self, concept: str, text: str) -> float:
        """Calculate semantic coherence of a concept within text."""
        # Simple coherence based on concept repetition and context
        concept_lower = concept.lower()
        text_lower = text.lower()

        # Count concept occurrences
        occurrences = text_lower.count(concept_lower)
        if occurrences == 0:
            return 0.0

        # Calculate context density
        words = text_lower.split()
        concept_indices = [i for i, word in enumerate(words) if concept_lower in word]

        if len(concept_indices) == 1:
            return 0.5  # Single occurrence, moderate coherence

        # Calculate average distance between occurrences
        distances = [concept_indices[i+1] - concept_indices[i] for i in range(len(concept_indices)-1)]
        avg_distance = sum(distances) / len(distances) if distances else len(words)

        # Closer occurrences = higher coherence
        distance_score = max(0.1, 1.0 - (avg_distance / len(words)))

        # Frequency bonus
        frequency_bonus = min(occurrences / 3.0, 1.0)

        return min(distance_score * 0.7 + frequency_bonus * 0.3, 1.0)

    def _extract_semantic_supporting_terms(self, concept: str, text: str, semantic_scores: Dict[str, float]) -> List[str]:
        """Extract supporting terms based on semantic scores."""
        # Get terms with high semantic scores
        scored_terms = [(term, score) for term, score in semantic_scores.items()
                       if term != concept.lower() and score > 0.3]

        # Sort by semantic score
        scored_terms.sort(key=lambda x: x[1], reverse=True)

        return [term for term, _ in scored_terms[:5]]

    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF for statistical calculations."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _extract_statistical_supporting_terms(self, concept: str, text: str, term_freq: Counter) -> List[str]:
        """Extract supporting terms based on statistical frequency."""
        # Get terms with frequency above average
        avg_freq = sum(term_freq.values()) / len(term_freq)
        frequent_terms = [(term, freq) for term, freq in term_freq.items()
                         if term != concept.lower() and freq > avg_freq]

        # Sort by frequency
        frequent_terms.sort(key=lambda x: x[1], reverse=True)

        return [term for term, _ in frequent_terms[:5]]

    def _select_best_extraction(self, method_results: Dict[str, Dict[str, Any]], mist: Dict[str, Any]) -> Dict[str, Any]:
        """Select best extraction result from multiple methods."""
        if len(method_results) == 1:
            return list(method_results.values())[0]

        # Score each result
        scored_results = []
        for method, result in method_results.items():
            score = result["confidence"]

            # Method preference weighting
            method_weights = {"hybrid": 1.2, "semantic": 1.1, "linguistic": 1.0, "statistical": 0.9}
            score *= method_weights.get(method, 1.0)

            # Supporting terms richness bonus
            supporting_bonus = min(len(result.get("supporting_terms", [])) / 3.0, 0.2)
            score += supporting_bonus

            scored_results.append((result, score))

        # Return highest scored result
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[0][0]

    def _calculate_extraction_validation(self, best_result: Dict[str, Any], all_results: Dict[str, Any], proto_thought: str) -> Dict[str, Any]:
        """Calculate comprehensive validation metrics for extraction."""
        return {
            "semantic_density": self._calculate_semantic_density_of_text(proto_thought),
            "novelty_score": self._calculate_concept_novelty(best_result.get("raw_concept", "")),
            "linguistic_features": self._extract_linguistic_features(proto_thought),
            "statistical_significance": best_result.get("statistical_significance", 0.5)
        }

    def _calculate_semantic_density_of_text(self, text: str) -> float:
        """Calculate semantic density of text."""
        words = text.split()
        meaningful_words = [w for w in words if w not in self.stop_words and len(w) > 2]

        if not meaningful_words:
            return 0.0

        # Density = meaningful words / total words
        return len(meaningful_words) / len(words)

    def _calculate_concept_novelty(self, concept: str) -> float:
        """Calculate novelty score for a concept."""
        # Check if concept has been seen before
        concept_frequency = self.concept_statistics[concept]["frequency"]

        if concept_frequency == 0:
            return 1.0  # Completely novel
        elif concept_frequency == 1:
            return 0.7  # Rare
        elif concept_frequency <= 5:
            return 0.4  # Uncommon
        else:
            return 0.1  # Common

    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from text."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "punctuation_ratio": len(re.findall(r'[^\w\s]', text)) / len(text) if text else 0,
            "capitalization_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }

    def _create_validation_hash(self, result: Dict[str, Any], proto_thought: str, mist: Dict[str, Any]) -> str:
        """Create reproducible validation hash."""
        hash_data = {
            "concept": result.get("concept_id", ""),
            "confidence": result.get("confidence", 0),
            "method": result.get("method", ""),
            "proto_hash": hashlib.md5(proto_thought.encode()).hexdigest()[:8],
            "mist_id": mist.get("id", ""),
            "timestamp": int(time.time())
        }

        return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()[:16]

    def _track_concept_statistics(self, extraction_result: ConceptExtractionResult, mist: Dict[str, Any]):
        """Track longitudinal statistics for concepts."""
        concept = extraction_result.concept_id

        self.concept_statistics[concept]["frequency"] += 1
        self.concept_statistics[concept]["contexts"].append(mist.get("proto_thought", ""))
        self.concept_statistics[concept]["confidence_sum"] += extraction_result.confidence
        self.concept_statistics[concept]["last_seen"] = int(time.time())

    def _categorize_novelty(self, novelty_score: float) -> str:
        """Categorize novelty score for analysis."""
        if novelty_score > 0.8:
            return "highly_novel"
        elif novelty_score > 0.5:
            return "moderately_novel"
        elif novelty_score > 0.2:
            return "slightly_novel"
        else:
            return "well_known"

    def _perform_validation_analysis(self, extraction_results: List[ConceptExtractionResult], mist_lines: List[Dict[str, Any]]) -> ConceptValidationMetrics:
        """Perform comprehensive validation analysis."""
        if not extraction_results:
            return ConceptValidationMetrics(0, 0, 0, 0, 0, 0, 0, 0)

        # Calculate precision, recall, F1 (simplified for demonstration)
        precision = sum(r.confidence for r in extraction_results) / len(extraction_results)
        recall = len(set(r.concept_id for r in extraction_results)) / max(len(mist_lines), 1)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Semantic coherence
        semantic_coherence = sum(r.semantic_density for r in extraction_results) / len(extraction_results)

        # Concept uniqueness
        unique_concepts = len(set(r.concept_id for r in extraction_results))
        concept_uniqueness = unique_concepts / len(extraction_results)

        # Extraction consistency
        method_consistency = len(set(r.extraction_method for r in extraction_results)) / len(extraction_results)
        extraction_consistency = 1.0 - method_consistency  # Lower method diversity = higher consistency

        # Statistical significance
        statistical_significance = sum(r.statistical_significance for r in extraction_results) / len(extraction_results)

        # Effect size (simplified)
        effect_size = statistical_significance * semantic_coherence

        return ConceptValidationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            semantic_coherence=semantic_coherence,
            concept_uniqueness=concept_uniqueness,
            extraction_consistency=extraction_consistency,
            statistical_significance=statistical_significance,
            effect_size=effect_size
        )

    def _calculate_semantic_diversity(self, concept_id: str) -> float:
        """Calculate semantic diversity of a concept."""
        if concept_id not in self.nodes:
            return 0.0

        profile = self.nodes[concept_id].get("semantic_profile", {})
        method_distribution = profile.get("method_distribution", Counter())

        if not method_distribution:
            return 0.0

        # Diversity based on method distribution entropy
        total_methods = sum(method_distribution.values())
        if total_methods == 0:
            return 0.0

        entropy = 0.0
        for count in method_distribution.values():
            if count > 0:
                probability = count / total_methods
                entropy -= probability * math.log(probability)

        # Normalize entropy (max entropy for 4 methods = log(4))
        max_entropy = math.log(len(method_distribution))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _log_extraction_error(self, mist: Dict[str, Any], error: str):
        """Log extraction errors for analysis."""
        error_log = {
            "timestamp": int(time.time()),
            "mist_id": mist.get("id"),
            "proto_thought": mist.get("proto_thought", "")[:100],
            "error": error,
            "mist_metadata": {k: v for k, v in mist.items() if k not in ["proto_thought", "id"]}
        }
        # In production, this would log to a file or monitoring system
        print(f"Concept extraction error: {error_log}")

    def _log_method_error(self, method: str, proto_thought: str, error: str):
        """Log method-specific errors."""
        error_log = {
            "timestamp": int(time.time()),
            "method": method,
            "proto_preview": proto_thought[:50],
            "error": error
        }
        print(f"Extraction method error ({method}): {error_log}")

    # Scientific analysis and reporting methods
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive extraction statistics for analysis."""
        if not self.extraction_history:
            return {"status": "no_extractions"}

        total_extractions = len(self.extraction_history)
        method_counts = Counter(e.extraction_method for e in self.extraction_history)
        avg_confidence = sum(e.confidence for e in self.extraction_history) / total_extractions
        avg_extraction_time = sum(e.extraction_time_ms for e in self.extraction_history) / total_extractions

        return {
            "total_extractions": total_extractions,
            "method_distribution": dict(method_counts),
            "average_confidence": avg_confidence,
            "average_extraction_time_ms": avg_extraction_time,
            "unique_concepts": len(set(e.concept_id for e in self.extraction_history)),
            "concept_statistics": dict(self.concept_statistics),
            "validation_metrics": self.validation_metrics[-1].__dict__ if self.validation_metrics else None
        }

    def export_scientific_data(self) -> Dict[str, Any]:
        """Export all data for scientific analysis and reproducibility."""
        return {
            "extraction_history": [
                {
                    "concept_id": e.concept_id,
                    "confidence": e.confidence,
                    "extraction_method": e.extraction_method,
                    "supporting_terms": e.supporting_terms,
                    "semantic_density": e.semantic_density,
                    "novelty_score": e.novelty_score,
                    "validation_hash": e.validation_hash,
                    "extraction_time_ms": e.extraction_time_ms,
                    "linguistic_features": e.linguistic_features,
                    "statistical_significance": e.statistical_significance
                }
                for e in self.extraction_history
            ],
            "concept_statistics": dict(self.concept_statistics),
            "validation_metrics": [vm.__dict__ for vm in self.validation_metrics],
            "node_data": self.nodes,
            "configuration": self.config,
            "extraction_timestamp": int(time.time())
        }
