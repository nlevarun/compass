"""
Clustering validation and quality metrics.

Compare clustering algorithms:
- DBSCAN (old baseline)
- BERTopic (new state-of-the-art)

Metrics:
- Silhouette score (cluster separation)
- Topic coherence (semantic consistency)
- Coverage (% successfully clustered)
- Speed (clustering time)
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    import numpy as np

try:
    from sklearn.metrics import silhouette_score
    from sentence_transformers import SentenceTransformer
    import numpy as np
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    np = None  # type: ignore


def calculate_clustering_quality(
    texts: List[str],
    labels: List[int],
    embeddings: Optional[Any] = None,
    ground_truth_labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive clustering quality metrics.

    Metrics:
    - Silhouette score (how well separated clusters are)
      - Range: -1 to 1
      - >0.7: Excellent
      - >0.5: Good
      - >0.25: Fair
      - <0.25: Poor

    - Coherence score (how semantically consistent topics are)
      - Calculated from intra-cluster similarity

    - Coverage (% of feedback successfully clustered)
      - Target: >80%

    Args:
        texts: Feedback texts
        labels: Cluster assignments (-1 = outlier)
        embeddings: Optional pre-computed embeddings
        ground_truth_labels: Optional ground truth for validation

    Returns:
        Dict with quality metrics

    Example:
        quality = calculate_clustering_quality(texts, topics)
        print(f"Quality: {quality['overall_score']:.2%}")
    """
    if not DEPS_AVAILABLE:
        return {
            "error": "Dependencies not installed",
            "silhouette_score": None,
            "coverage": 0.0,
            "overall_score": 0.0
        }

    # Get embeddings if not provided
    if embeddings is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts)

    # Convert to numpy arrays
    labels_arr = np.array(labels)
    embeddings_arr = np.array(embeddings) if not isinstance(embeddings, np.ndarray) else embeddings

    # Filter out outliers (-1)
    valid_mask = labels_arr != -1
    valid_labels = labels_arr[valid_mask]
    valid_embeddings = embeddings_arr[valid_mask]

    # Coverage (% not outliers)
    coverage = float(valid_mask.sum() / len(labels_arr))

    # Silhouette score (cluster separation)
    silhouette = None
    if len(set(valid_labels)) > 1 and len(valid_labels) > 1:
        silhouette = silhouette_score(valid_embeddings, valid_labels, metric='cosine')

    # Intra-cluster coherence (semantic consistency within clusters)
    coherence_scores = []
    for label in set(valid_labels):
        cluster_mask = valid_labels == label
        cluster_embeddings = valid_embeddings[cluster_mask]

        if len(cluster_embeddings) > 1:
            # Calculate average cosine similarity within cluster
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(cluster_embeddings)
            # Average similarity (excluding diagonal)
            n = len(similarities)
            avg_sim = (similarities.sum() - n) / (n * (n - 1)) if n > 1 else 0
            coherence_scores.append(avg_sim)

    coherence = float(np.mean(coherence_scores)) if coherence_scores else None

    # Overall quality score (weighted average)
    # Weights: Silhouette (40%), Coverage (30%), Coherence (30%)
    overall_score = None
    if silhouette is not None and coherence is not None:
        overall_score = (
            0.4 * silhouette +
            0.3 * coverage +
            0.3 * coherence
        )

    # Cluster statistics
    n_clusters = len(set(valid_labels))
    cluster_sizes = [int((valid_labels == label).sum()) for label in set(valid_labels)]

    return {
        "silhouette_score": float(silhouette) if silhouette else None,
        "coverage": float(coverage),
        "coherence": float(coherence) if coherence else None,
        "overall_score": float(overall_score) if overall_score else None,
        "num_clusters": int(n_clusters),
        "outliers": int((~valid_mask).sum()),
        "outlier_percentage": float((~valid_mask).sum() / len(labels_arr) * 100),
        "avg_cluster_size": float(np.mean(cluster_sizes)) if cluster_sizes else 0,
        "min_cluster_size": int(min(cluster_sizes)) if cluster_sizes else 0,
        "max_cluster_size": int(max(cluster_sizes)) if cluster_sizes else 0,
        # Accuracy estimate (simplified)
        "accuracy_estimate": float(silhouette * 100) if silhouette else None,
        # Pass/Fail criteria
        "passes_quality_check": (
            silhouette is not None and
            silhouette > 0.5 and
            coverage > 0.8
        ) if silhouette else False
    }


def compare_clustering_algorithms(
    texts: List[str],
    dbscan_labels: List[int],
    bertopic_labels: List[int],
    embeddings: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Compare DBSCAN vs BERTopic clustering quality.

    Args:
        texts: Feedback texts
        dbscan_labels: Labels from old DBSCAN clustering
        bertopic_labels: Labels from new BERTopic clustering
        embeddings: Optional pre-computed embeddings

    Returns:
        Comparison metrics showing improvement

    Example:
        comparison = compare_clustering_algorithms(texts, old_labels, new_labels)
        print(f"Improvement: {comparison['improvement_percentage']:.1f}%")
    """
    # Calculate quality for both
    dbscan_quality = calculate_clustering_quality(texts, dbscan_labels, embeddings)
    bertopic_quality = calculate_clustering_quality(texts, bertopic_labels, embeddings)

    # Calculate improvement
    improvements = {}
    for metric in ['silhouette_score', 'coverage', 'overall_score']:
        dbscan_val = dbscan_quality.get(metric)
        bertopic_val = bertopic_quality.get(metric)

        if dbscan_val is not None and bertopic_val is not None:
            improvement = (bertopic_val - dbscan_val) / dbscan_val * 100
            improvements[f"{metric}_improvement"] = float(improvement)

    return {
        "dbscan": dbscan_quality,
        "bertopic": bertopic_quality,
        "improvements": improvements,
        "winner": "BERTopic" if bertopic_quality.get("overall_score", 0) > dbscan_quality.get("overall_score", 0) else "DBSCAN",
        "improvement_percentage": improvements.get("overall_score_improvement", 0.0)
    }


def benchmark_clustering_speed(
    texts: List[str],
    algorithm: str = "bertopic"
) -> Dict[str, Any]:
    """
    Benchmark clustering speed.

    Args:
        texts: Feedback texts
        algorithm: "bertopic" or "dbscan"

    Returns:
        Timing metrics

    Example:
        timing = benchmark_clustering_speed(texts, "bertopic")
        print(f"Time: {timing['total_seconds']:.1f}s")
    """
    from nlp.bertopic_clustering import BERTopicClusterer
    from nlp.clustering import FeedbackClusterer

    start = time.time()

    if algorithm == "bertopic":
        clusterer = BERTopicClusterer(min_cluster_size=5)
        topics, probs = clusterer.fit_transform(texts)
    elif algorithm == "dbscan":
        clusterer = FeedbackClusterer(eps=0.5, min_samples=3)
        topics, metrics = clusterer.cluster_feedback(texts)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    end = time.time()
    elapsed = end - start

    return {
        "algorithm": algorithm,
        "total_seconds": float(elapsed),
        "texts_per_second": float(len(texts) / elapsed),
        "num_texts": len(texts)
    }


def generate_accuracy_report(
    texts: List[str],
    bertopic_labels: List[int],
    embeddings: Optional[Any] = None
) -> str:
    """
    Generate human-readable accuracy report.

    Args:
        texts: Feedback texts
        bertopic_labels: BERTopic cluster assignments
        embeddings: Optional embeddings

    Returns:
        Formatted report string

    Example:
        report = generate_accuracy_report(texts, topics)
        print(report)
    """
    quality = calculate_clustering_quality(texts, bertopic_labels, embeddings)

    report = []
    report.append("=" * 60)
    report.append("CLUSTERING QUALITY REPORT")
    report.append("=" * 60)
    report.append("")

    # Overall score
    overall = quality.get('overall_score')
    if overall:
        report.append(f"Overall Quality Score: {overall:.3f} ({overall*100:.1f}%)")
        if overall > 0.8:
            report.append("  Rating: ✓ EXCELLENT")
        elif overall > 0.6:
            report.append("  Rating: ✓ GOOD")
        elif overall > 0.4:
            report.append("  Rating: ⚠ FAIR")
        else:
            report.append("  Rating: ✗ POOR")
        report.append("")

    # Individual metrics
    report.append("Detailed Metrics:")
    report.append("")

    silhouette = quality.get('silhouette_score')
    if silhouette:
        report.append(f"  Silhouette Score: {silhouette:.3f}")
        if silhouette > 0.7:
            report.append("    ✓ Excellent cluster separation")
        elif silhouette > 0.5:
            report.append("    ✓ Good cluster separation")
        else:
            report.append("    ⚠ Could be better")
        report.append("")

    coverage = quality.get('coverage', 0)
    report.append(f"  Coverage: {coverage:.2%}")
    if coverage > 0.8:
        report.append("    ✓ Most feedback successfully clustered")
    else:
        report.append("    ⚠ Too many outliers")
    report.append("")

    coherence = quality.get('coherence')
    if coherence:
        report.append(f"  Coherence: {coherence:.3f}")
        if coherence > 0.7:
            report.append("    ✓ Topics are semantically consistent")
        report.append("")

    # Cluster stats
    report.append("Cluster Statistics:")
    report.append(f"  Total Clusters: {quality.get('num_clusters', 0)}")
    report.append(f"  Avg Cluster Size: {quality.get('avg_cluster_size', 0):.1f}")
    report.append(f"  Outliers: {quality.get('outliers', 0)} ({quality.get('outlier_percentage', 0):.1f}%)")
    report.append("")

    # Pass/Fail
    report.append("=" * 60)
    if quality.get('passes_quality_check'):
        report.append("✓ PASSES QUALITY CHECK")
        report.append("  Ready for production use!")
    else:
        report.append("✗ DOES NOT PASS QUALITY CHECK")
        report.append("  Recommendations:")
        if silhouette and silhouette < 0.5:
            report.append("  - Adjust min_cluster_size parameter")
        if coverage < 0.8:
            report.append("  - Too many outliers - lower eps threshold")
        report.append("  - Collect more diverse feedback data")
    report.append("=" * 60)

    return "\n".join(report)


if __name__ == "__main__":
    # Test validation
    print("Testing clustering validation...\n")

    from nlp.bertopic_clustering import BERTopicClusterer

    sample_texts = [
        "The mobile app is really slow when scrolling.",
        "App crashes frequently when uploading files.",
        "Mobile performance has degraded since last update.",
        "We need a Salesforce integration.",
        "API documentation is missing pagination.",
        "Can you add conversion rate to the dashboard?",
        "Export to Excel would be valuable.",
        "Real-time dashboards would help.",
        "Please add dark mode!",
        "Dark theme support would be amazing.",
    ]

    # Run BERTopic
    clusterer = BERTopicClusterer(min_cluster_size=2)
    topics, probs = clusterer.fit_transform(sample_texts)

    # Generate report
    report = generate_accuracy_report(sample_texts, topics)
    print(report)
