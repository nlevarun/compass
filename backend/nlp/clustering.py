"""
NLP clustering engine for grouping similar feedback.

Uses:
- sentence-transformers (all-MiniLM-L6-v2) for semantic embeddings
- DBSCAN for automatic cluster detection
- Extractive summarization for cluster labels
"""

import json
from typing import List, Dict, Tuple, Optional
from collections import Counter
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️  NLP dependencies not installed. Using simplified clustering.")


class FeedbackClusterer:
    """
    Clusters feedback using semantic similarity.

    Key hyperparameters:
    - eps: Maximum distance between samples in same cluster (tune for 85%+ accuracy)
    - min_samples: Minimum cluster size (prevents tiny clusters)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", eps: float = 0.5, min_samples: int = 3):
        """
        Initialize clusterer.

        Args:
            model_name: Sentence transformer model
            eps: DBSCAN epsilon (smaller = tighter clusters)
            min_samples: Minimum samples per cluster
        """
        self.model_name = model_name
        self.eps = eps
        self.min_samples = min_samples

        if DEPS_AVAILABLE:
            print(f"Loading sentence transformer model: {model_name}...")
            self.model = SentenceTransformer(model_name)
        else:
            self.model = None

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate semantic embeddings for texts.

        Args:
            texts: List of feedback texts
            batch_size: Batch size for encoding (performance optimization)

        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        if not DEPS_AVAILABLE:
            # Fallback: simple bag-of-words hash-based embeddings
            return self._simple_embeddings(texts)

        # Encode in batches for performance
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        return embeddings

    def _simple_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Simple fallback embeddings based on word hashing."""
        embeddings = []
        for text in texts:
            # Simple word-based feature vector
            words = text.lower().split()
            # Create a simple feature vector based on word presence
            features = [0.0] * 100  # 100-dim vector

            for word in words:
                # Hash word to index
                idx = hash(word) % 100
                features[idx] += 1.0

            # Normalize
            total = sum(features) or 1.0
            features = [f / total for f in features]

            embeddings.append(features)

        return embeddings

    def cluster_feedback(self, texts: List[str], embeddings: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Dict]:
        """
        Cluster feedback using DBSCAN.

        Args:
            texts: List of feedback texts
            embeddings: Pre-computed embeddings (optional)

        Returns:
            Tuple of (cluster_labels, metrics)
            - cluster_labels: Array of cluster IDs (-1 = noise/outlier)
            - metrics: Clustering quality metrics
        """
        # Generate embeddings if not provided
        if embeddings is None:
            embeddings = self.generate_embeddings(texts)

        if DEPS_AVAILABLE:
            # DBSCAN clustering
            clusterer = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric="cosine")
            labels = clusterer.fit_predict(embeddings)

            # Calculate metrics
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = list(labels).count(-1)

            # Silhouette score (only if we have 2+ clusters)
            silhouette = None
            if n_clusters > 1:
                # Exclude noise points for silhouette calculation
                mask = labels != -1
                if mask.sum() > 1:
                    silhouette = silhouette_score(embeddings[mask], labels[mask], metric="cosine")

            metrics = {
                "n_clusters": n_clusters,
                "n_noise": n_noise,
                "silhouette_score": float(silhouette) if silhouette else None,
                "noise_percentage": round(100 * n_noise / len(labels), 2)
            }

        else:
            # Simplified fallback clustering based on keyword similarity
            labels = self._simple_clustering(texts)
            metrics = {
                "n_clusters": len(set(labels)) - (1 if -1 in labels else 0),
                "n_noise": list(labels).count(-1),
                "silhouette_score": None,
                "noise_percentage": 0
            }

        return labels, metrics

    def _simple_clustering(self, texts: List[str]) -> List[int]:
        """Simple fallback clustering based on keyword matching."""
        # Define keyword groups
        keyword_groups = {
            0: ["mobile", "app", "slow", "crash", "performance", "freeze"],
            1: ["api", "integration", "webhook", "endpoint", "rate limit"],
            2: ["report", "dashboard", "export", "analytics", "metric"],
            3: ["user", "sso", "permission", "role", "access"],
            4: ["price", "billing", "invoice", "cost", "payment"],
            5: ["ui", "interface", "design", "dark mode", "keyboard"],
            6: ["collaboration", "comment", "share", "team", "workspace"],
            7: ["security", "compliance", "encryption", "audit", "gdpr"],
            8: ["search", "filter", "query", "find", "sort"],
            9: ["notification", "alert", "email", "slack", "push"],
        }

        labels = []
        for text in texts:
            text_lower = text.lower()
            best_group = -1
            best_score = 0

            for group_id, keywords in keyword_groups.items():
                score = sum(1 for kw in keywords if kw in text_lower)
                if score > best_score:
                    best_score = score
                    best_group = group_id

            labels.append(best_group)

        return labels

    def generate_cluster_label(self, texts: List[str], max_words: int = 5) -> str:
        """
        Generate descriptive label for cluster by extracting key terms.

        Args:
            texts: Feedback texts in cluster
            max_words: Maximum words in label

        Returns:
            Cluster label (e.g., "Mobile App Performance Issues")
        """
        # Extract all words (excluding common stopwords)
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "can", "may", "might", "must", "this", "that", "these", "those",
            "i", "you", "he", "she", "it", "we", "they", "my", "your", "our",
            "need", "want", "please", "very", "really", "just", "like"
        }

        # Collect all words
        word_counts = Counter()
        for text in texts:
            words = text.lower().split()
            # Filter out stopwords and short words
            words = [w.strip(".,!?;:\"'") for w in words if len(w) > 3 and w.lower() not in stopwords]
            word_counts.update(words)

        # Get top keywords
        top_keywords = [word for word, _ in word_counts.most_common(max_words)]

        # Capitalize and join
        label = " ".join(word.capitalize() for word in top_keywords)

        return label or "Miscellaneous Feedback"

    def calculate_centroid(self, embeddings: np.ndarray) -> List[float]:
        """Calculate cluster centroid (mean embedding)."""
        if DEPS_AVAILABLE:
            return embeddings.mean(axis=0).tolist()
        else:
            # Simple mean for list of lists
            n_dim = len(embeddings[0])
            centroid = [0.0] * n_dim
            for emb in embeddings:
                for i, val in enumerate(emb):
                    centroid[i] += val
            return [c / len(embeddings) for c in centroid]


def validate_clustering_accuracy(
    true_labels: List[int],
    predicted_labels: List[int]
) -> Dict[str, float]:
    """
    Validate clustering accuracy against ground truth.

    Metrics:
    - Adjusted Rand Index (ARI): 1.0 = perfect, 0.0 = random
    - Normalized Mutual Information (NMI): 1.0 = perfect match
    """
    if not DEPS_AVAILABLE:
        return {"error": "sklearn not available"}

    ari = adjusted_rand_score(true_labels, predicted_labels)
    nmi = normalized_mutual_info_score(true_labels, predicted_labels)

    return {
        "adjusted_rand_index": round(ari, 3),
        "normalized_mutual_info": round(nmi, 3),
        "passes_threshold": ari > 0.70 and nmi > 0.75  # Target: 85%+ similarity
    }


if __name__ == "__main__":
    # Test clustering
    print("Testing feedback clustering...\n")

    sample_texts = [
        "The mobile app is really slow when scrolling. Takes 10+ seconds to load.",
        "App crashes frequently when uploading files. Very frustrating.",
        "Mobile performance has degraded since last update. Please fix!",
        "We need a Salesforce integration to sync our data automatically.",
        "API documentation is missing pagination. Can you add this?",
        "Rate limits on the API are too restrictive for our data sync.",
        "Can you add conversion rate to the analytics dashboard?",
        "Export to Excel would be incredibly valuable for our workflow.",
        "Real-time dashboards would help us make faster decisions.",
        "SSO with Okta is essential for our enterprise deployment.",
    ]

    clusterer = FeedbackClusterer(eps=0.5, min_samples=2)

    print("Generating embeddings...")
    embeddings = clusterer.generate_embeddings(sample_texts)

    print("Clustering feedback...")
    labels, metrics = clusterer.cluster_feedback(sample_texts, embeddings)

    print(f"\n✓ Clustering complete!")
    print(f"  Clusters found: {metrics['n_clusters']}")
    print(f"  Noise points: {metrics['n_noise']}")
    if metrics['silhouette_score']:
        print(f"  Silhouette score: {metrics['silhouette_score']:.3f}")

    # Show clusters
    print("\n--- Clusters ---")
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue

        cluster_texts = [text for text, label in zip(sample_texts, labels) if label == cluster_id]
        cluster_label = clusterer.generate_cluster_label(cluster_texts)

        print(f"\nCluster {cluster_id}: {cluster_label}")
        for text in cluster_texts:
            print(f"  • {text[:80]}...")
