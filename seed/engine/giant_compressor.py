from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
import time, hashlib, math
import random
from collections import defaultdict
from embeddings.factory import EmbeddingProviderFactory

class GiantCompressor:
    """The Giant: compacts raw fragments into clustered sediment strata.

    Enhanced with semantic clustering using embedding similarity and density-based clustering.
    """
    def __init__(self, sediment_store: "SedimentStore", embed_provider=None, config: Optional[Dict[str, Any]] = None):
        self.sediment_store = sediment_store
        self.config = config or {}

        # Initialize embedding provider
        if embed_provider:
            self.embed_provider = embed_provider
        else:
            provider_config = self.config.get("embeddings", {"provider": "local", "config": {"dimension": 128}})
            self.embed_provider = EmbeddingProviderFactory.create_from_config(provider_config)

        # Clustering parameters
        self.min_cluster_size = self.config.get("min_cluster_size", 3)
        self.max_cluster_distance = self.config.get("max_cluster_distance", 0.7)
        self.clustering_method = self.config.get("clustering_method", "density_based")  # density_based, kmeans, hierarchical

    def stomp(self, raw_fragments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compress fragments using semantic clustering."""
        start = time.time()
        if not raw_fragments:
            return {"clusters": 0, "elapsed_ms": 0.0, "strata_updates": 0}

        # Generate embeddings for all fragments
        texts = [f.get("text", "") for f in raw_fragments]
        embeddings = self.embed_provider.embed_batch(texts)

        # Perform semantic clustering
        clusters = self._semantic_cluster(raw_fragments, embeddings)

        # Store clusters
        stratum_id = self.sediment_store.append_clusters(clusters)

        return {
            "clusters": len(clusters),
            "elapsed_ms": (time.time() - start) * 1000,
            "strata_updates": 1,
            "stratum_id": stratum_id,
            "clustering_method": self.clustering_method,
            "avg_cluster_size": sum(len(c["fragments"]) for c in clusters) / len(clusters) if clusters else 0,
        }

    def _semantic_cluster(self, fragments: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """Perform semantic clustering based on embedding similarity."""
        if self.clustering_method == "density_based":
            return self._density_based_clustering(fragments, embeddings)
        elif self.clustering_method == "kmeans":
            return self._kmeans_clustering(fragments, embeddings)
        elif self.clustering_method == "hierarchical":
            return self._hierarchical_clustering(fragments, embeddings)
        else:
            # Fallback to simple clustering
            return self._simple_clustering(fragments, embeddings)

    def _density_based_clustering(self, fragments: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """Density-based clustering similar to HDBSCAN."""
        if len(fragments) < self.min_cluster_size:
            return self._create_single_cluster(fragments)

        # Calculate distance matrix
        distances = self._calculate_distance_matrix(embeddings)

        # Find core points (points with enough neighbors)
        core_points = self._find_core_points(distances)

        # Expand clusters from core points
        clusters = []
        visited = set()

        for core_idx in core_points:
            if core_idx in visited:
                continue

            # Start new cluster
            cluster = self._expand_cluster(core_idx, distances, visited)
            if len(cluster) >= self.min_cluster_size:
                cluster_fragments = [fragments[i] for i in cluster]
                clusters.append(self._create_cluster(cluster_fragments, cluster))

        # Add noise points as individual clusters
        noise_points = [i for i in range(len(fragments)) if i not in visited]
        for noise_idx in noise_points:
            clusters.append(self._create_cluster([fragments[noise_idx]], [noise_idx]))

        return clusters

    def _kmeans_clustering(self, fragments: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """K-means clustering implementation."""
        if len(fragments) < self.min_cluster_size:
            return self._create_single_cluster(fragments)

        # Determine number of clusters (using elbow method approximation)
        n_clusters = min(max(1, len(fragments) // 5), 10)  # Heuristic: 1 cluster per 5 fragments, max 10

        # Initialize centroids randomly
        centroids = self._initialize_centroids(embeddings, n_clusters)

        # K-means iterations
        for _ in range(50):  # Max iterations
            # Assign points to nearest centroid
            assignments = self._assign_to_centroids(embeddings, centroids)

            # Update centroids
            new_centroids = self._update_centroids(embeddings, assignments, n_clusters)

            # Check convergence
            if self._centroids_converged(centroids, new_centroids):
                break

            centroids = new_centroids

        # Create clusters from assignments
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, assignment in enumerate(assignments) if assignment == cluster_id]
            if cluster_indices:
                cluster_fragments = [fragments[i] for i in cluster_indices]
                clusters.append(self._create_cluster(cluster_fragments, cluster_indices))

        return clusters

    def _hierarchical_clustering(self, fragments: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """Hierarchical agglomerative clustering."""
        if len(fragments) < self.min_cluster_size:
            return self._create_single_cluster(fragments)

        # Start with each fragment as its own cluster
        clusters = [[i] for i in range(len(fragments))]

        # Merge clusters until stopping criteria
        while len(clusters) > 1:
            # Find closest pair of clusters
            min_distance = float('inf')
            merge_i, merge_j = -1, -1

            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    distance = self._cluster_distance(clusters[i], clusters[j], embeddings)
                    if distance < min_distance:
                        min_distance = distance
                        merge_i, merge_j = i, j

            # Stop if clusters are too far apart
            if min_distance > self.max_cluster_distance:
                break

            # Merge closest clusters
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)

        # Filter small clusters
        final_clusters = []
        for cluster_indices in clusters:
            if len(cluster_indices) >= self.min_cluster_size:
                cluster_fragments = [fragments[i] for i in cluster_indices]
                final_clusters.append(self._create_cluster(cluster_fragments, cluster_indices))
            else:
                # Add small clusters as individual fragments
                for idx in cluster_indices:
                    final_clusters.append(self._create_cluster([fragments[idx]], [idx]))

        return final_clusters

    def _simple_clustering(self, fragments: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
        """Simple similarity-based clustering as fallback."""
        if len(fragments) <= self.min_cluster_size:
            return self._create_single_cluster(fragments)

        clusters = []
        used_indices = set()

        for i, fragment in enumerate(fragments):
            if i in used_indices:
                continue

            # Find similar fragments
            similar_indices = [i]
            for j in range(len(fragments)):
                if j != i and j not in used_indices:
                    similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                    if similarity > (1 - self.max_cluster_distance):
                        similar_indices.append(j)
                        used_indices.add(j)

            used_indices.add(i)
            cluster_fragments = [fragments[idx] for idx in similar_indices]
            clusters.append(self._create_cluster(cluster_fragments, similar_indices))

        return clusters

    # Helper methods
    def _calculate_distance_matrix(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Calculate pairwise distance matrix."""
        n = len(embeddings)
        distances = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                distance = 1 - self._cosine_similarity(embeddings[i], embeddings[j])
                distances[i][j] = distances[j][i] = distance

        return distances

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _find_core_points(self, distances: List[List[float]]) -> List[int]:
        """Find core points with enough neighbors within max distance."""
        core_points = []
        n = len(distances)

        for i in range(n):
            neighbors = sum(1 for j in range(n) if i != j and distances[i][j] <= self.max_cluster_distance)
            if neighbors >= self.min_cluster_size - 1:
                core_points.append(i)

        return core_points

    def _expand_cluster(self, core_idx: int, distances: List[List[float]], visited: set) -> List[int]:
        """Expand cluster from core point."""
        cluster = [core_idx]
        visited.add(core_idx)

        # Find all neighbors within max distance
        neighbors = [i for i, dist in enumerate(distances[core_idx]) if i != core_idx and dist <= self.max_cluster_distance]

        # Add neighbors to cluster
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                cluster.append(neighbor)

        return cluster

    def _initialize_centroids(self, embeddings: List[List[float]], n_clusters: int) -> List[List[float]]:
        """Initialize centroids using k-means++ algorithm."""
        if n_clusters >= len(embeddings):
            return embeddings.copy()

        centroids = []
        # Choose first centroid randomly
        first_idx = random.randint(0, len(embeddings) - 1)
        centroids.append(embeddings[first_idx].copy())

        # Choose remaining centroids
        for _ in range(1, n_clusters):
            # Calculate distances to nearest centroid
            distances = []
            for embedding in embeddings:
                min_dist = min(1 - self._cosine_similarity(embedding, centroid) for centroid in centroids)
                distances.append(min_dist)

            # Choose next centroid with probability proportional to distance squared
            total_dist = sum(d * d for d in distances)
            if total_dist == 0:
                break

            probabilities = [d * d / total_dist for d in distances]
            next_idx = random.choices(range(len(embeddings)), weights=probabilities)[0]
            centroids.append(embeddings[next_idx].copy())

        return centroids

    def _assign_to_centroids(self, embeddings: List[List[float]], centroids: List[List[float]]) -> List[int]:
        """Assign each embedding to nearest centroid."""
        assignments = []
        for embedding in embeddings:
            similarities = [self._cosine_similarity(embedding, centroid) for centroid in centroids]
            assignments.append(similarities.index(max(similarities)))
        return assignments

    def _update_centroids(self, embeddings: List[List[float]], assignments: List[int], n_clusters: int) -> List[List[float]]:
        """Update centroids based on current assignments."""
        new_centroids = []
        dimension = len(embeddings[0]) if embeddings else 0

        for cluster_id in range(n_clusters):
            cluster_embeddings = [embeddings[i] for i, assignment in enumerate(assignments) if assignment == cluster_id]

            if cluster_embeddings:
                # Calculate mean of cluster embeddings
                centroid = [sum(embedding[dim] for embedding in cluster_embeddings) / len(cluster_embeddings)
                           for dim in range(dimension)]
                new_centroids.append(centroid)
            else:
                # Keep old centroid if cluster is empty
                new_centroids.append(centroids[cluster_id].copy())

        return new_centroids

    def _centroids_converged(self, centroids: List[List[float]], new_centroids: List[List[float]], threshold: float = 0.001) -> bool:
        """Check if centroids have converged."""
        for old, new in zip(centroids, new_centroids):
            distance = 1 - self._cosine_similarity(old, new)
            if distance > threshold:
                return False
        return True

    def _cluster_distance(self, cluster1: List[int], cluster2: List[int], embeddings: List[List[float]]) -> float:
        """Calculate distance between two clusters (average linkage)."""
        total_distance = 0
        count = 0

        for i in cluster1:
            for j in cluster2:
                total_distance += 1 - self._cosine_similarity(embeddings[i], embeddings[j])
                count += 1

        return total_distance / count if count > 0 else float('inf')

    def _create_cluster(self, fragments: List[Dict[str, Any]], indices: List[int]) -> Dict[str, Any]:
        """Create cluster metadata."""
        # Generate cluster ID based on content hash
        concat = " ".join(f.get("text", "") for f in fragments)
        digest = hashlib.sha256(concat.encode()).hexdigest()[:10]

        # Calculate cluster quality metrics
        if len(fragments) > 1:
            embeddings = [self.embed_provider.embed_text(f.get("text", "")) for f in fragments]
            avg_similarity = sum(
                self._cosine_similarity(embeddings[i], embeddings[j])
                for i in range(len(embeddings))
                for j in range(i + 1, len(embeddings))
            ) / (len(embeddings) * (len(embeddings) - 1) / 2)
        else:
            avg_similarity = 1.0

        return {
            "id": f"cluster_{digest}",
            "fragments": fragments,
            "size": len(fragments),
            "indices": indices,
            "avg_similarity": avg_similarity,
            "cohesion_score": avg_similarity,
            "created_at": time.time(),
        }

    def _create_single_cluster(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a single cluster when clustering is not possible."""
        return [self._create_cluster(fragments, list(range(len(fragments))))]

class SedimentStore:
    def __init__(self):
        self.strata = []  # list of dict

    def append_cluster(self, cluster: Dict[str, Any]) -> str:
        """Legacy method for backward compatibility."""
        return self.append_clusters([cluster])

    def append_clusters(self, clusters: List[Dict[str, Any]]) -> str:
        """Append multiple clusters to a new stratum."""
        if not clusters:
            raise ValueError("Cannot append empty cluster list")

        # Calculate stratum metrics
        total_fragments = sum(cluster["size"] for cluster in clusters)
        avg_similarity = sum(cluster.get("avg_similarity", 0.0) for cluster in clusters) / len(clusters)
        compaction_ratio = total_fragments / len(clusters) if clusters else 1.0

        stratum = {
            "stratum_id": f"stratum_{len(self.strata)+1}",
            "clusters": clusters,
            "total_fragments": total_fragments,
            "cluster_count": len(clusters),
            "avg_cluster_size": total_fragments / len(clusters),
            "avg_similarity": avg_similarity,
            "compaction_ratio": compaction_ratio,
            "created_at": time.time(),
        }
        self.strata.append(stratum)
        return stratum["stratum_id"]

    def get_stratum(self, stratum_id: str) -> Optional[Dict[str, Any]]:
        """Get stratum by ID."""
        for stratum in self.strata:
            if stratum["stratum_id"] == stratum_id:
                return stratum
        return None

    def get_all_strata(self) -> List[Dict[str, Any]]:
        """Get all strata."""
        return self.strata.copy()

    def get_cluster_count(self) -> int:
        """Get total number of clusters across all strata."""
        return sum(len(stratum["clusters"]) for stratum in self.strata)

    def get_fragment_count(self) -> int:
        """Get total number of fragments across all strata."""
        return sum(stratum["total_fragments"] for stratum in self.strata)
