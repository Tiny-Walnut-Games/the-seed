# Helper methods for castle_graph.py - Scientific Concept Extraction Implementation

import re
import math
import time
import json
import hashlib
from typing import Dict, List, Set, Any
from collections import Counter
from dataclasses import dataclass

# Import the main classes from castle_graph
from .castle_graph import ConceptExtractionResult, ConceptValidationMetrics


class CastleGraphHelpers:
    """Helper methods for castle graph concept extraction."""

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
