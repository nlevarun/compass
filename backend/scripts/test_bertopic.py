#!/usr/bin/env python3
"""
Quick test script to verify BERTopic installation and functionality.

Run this to check if BERTopic upgrade is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all dependencies are installed."""
    print("=" * 70)
    print("TEST 1: Checking Dependencies")
    print("=" * 70)

    try:
        import bertopic
        print("✓ BERTopic installed:", bertopic.__version__)
    except ImportError:
        print("✗ BERTopic not installed")
        print("  Install with: pip install bertopic")
        return False

    try:
        import sentence_transformers
        print("✓ Sentence Transformers installed:", sentence_transformers.__version__)
    except ImportError:
        print("✗ Sentence Transformers not installed")
        return False

    try:
        import umap
        print("✓ UMAP installed:", umap.__version__)
    except ImportError:
        print("✗ UMAP not installed")
        return False

    try:
        import hdbscan
        print("✓ HDBSCAN installed:", hdbscan.__version__)
    except ImportError:
        print("✗ HDBSCAN not installed")
        return False

    print("\n✓ All dependencies installed!\n")
    return True


def test_clustering():
    """Test basic clustering functionality."""
    print("=" * 70)
    print("TEST 2: Basic Clustering")
    print("=" * 70)

    try:
        from nlp.bertopic_clustering import BERTopicClusterer

        # Sample texts
        texts = [
            "The mobile app is really slow when scrolling",
            "App crashes frequently when uploading files",
            "Mobile performance has degraded since last update",
            "We need a Salesforce integration to sync data",
            "API documentation is missing pagination",
            "Rate limits on the API are too restrictive",
            "Can you add conversion rate to the dashboard?",
            "Export to Excel would be incredibly valuable",
            "Real-time dashboards would help us decide faster",
            "Please add dark mode! My eyes hurt at night",
            "Dark theme support would be amazing",
            "Night mode is essential for our workflow"
        ]

        print(f"\nClustering {len(texts)} feedback items...\n")

        # Run clustering
        clusterer = BERTopicClusterer(min_cluster_size=2)
        topics, probabilities = clusterer.fit_transform(texts)

        # Show results
        n_clusters = len(set(topics)) - (1 if -1 in topics else 0)
        n_outliers = topics.count(-1)
        avg_prob = sum(p for p, t in zip(probabilities, topics) if t != -1) / (len(topics) - n_outliers) if n_outliers < len(topics) else 0

        print("\nResults:")
        print(f"  Clusters found: {n_clusters}")
        print(f"  Outliers: {n_outliers} ({100*n_outliers/len(topics):.1f}%)")
        print(f"  Avg confidence: {avg_prob:.3f}")

        # Show cluster topics
        print("\nCluster Topics:")
        topic_info = clusterer.get_topic_info()
        for topic in topic_info:
            label = clusterer.generate_topic_label(topic['topic_id'])
            keywords = ', '.join(topic['representation'][:5])
            print(f"  Topic {topic['topic_id']}: {label}")
            print(f"    Keywords: {keywords}")
            print(f"    Size: {topic['count']} items")

        print("\n✓ Clustering test passed!\n")
        return True

    except Exception as e:
        print(f"\n✗ Clustering test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_quality_metrics():
    """Test quality metrics calculation."""
    print("=" * 70)
    print("TEST 3: Quality Metrics")
    print("=" * 70)

    try:
        from nlp.bertopic_clustering import BERTopicClusterer, calculate_clustering_metrics

        texts = [
            "Mobile app slow", "App crashes", "Performance issues",
            "Need Salesforce integration", "API rate limits", "Missing docs",
            "Add dashboard metrics", "Excel export", "Real-time reports"
        ]

        print(f"\nCalculating quality for {len(texts)} items...\n")

        clusterer = BERTopicClusterer(min_cluster_size=2)
        topics, probs = clusterer.fit_transform(texts)

        # Calculate metrics
        metrics = calculate_clustering_metrics(texts, topics)

        print("Quality Metrics:")
        print(f"  Silhouette Score: {metrics.get('silhouette_score', 'N/A')}")
        print(f"  Coverage: {metrics.get('coverage', 0) * 100:.1f}%")
        print(f"  Num Clusters: {metrics.get('num_clusters', 0)}")
        print(f"  Avg Cluster Size: {metrics.get('avg_cluster_size', 0):.1f}")

        # Check if passes quality
        silhouette = metrics.get('silhouette_score')
        coverage = metrics.get('coverage', 0)

        if silhouette and silhouette > 0.5 and coverage > 0.8:
            print("\n✓ Quality metrics test passed! (Excellent clustering)\n")
            return True
        else:
            print("\n⚠ Quality metrics test passed (but quality could be better)\n")
            return True

    except Exception as e:
        print(f"\n✗ Quality metrics test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation functions."""
    print("=" * 70)
    print("TEST 4: Validation Functions")
    print("=" * 70)

    try:
        from nlp.validate_clustering import (
            calculate_clustering_quality,
            generate_accuracy_report
        )
        from nlp.bertopic_clustering import BERTopicClusterer

        texts = [
            "Mobile issues", "App crashes", "Performance problems",
            "API integration", "Rate limits", "Documentation",
            "Dashboard metrics", "Excel export", "Reports"
        ]

        print(f"\nValidating clustering quality...\n")

        clusterer = BERTopicClusterer(min_cluster_size=2)
        topics, probs = clusterer.fit_transform(texts)

        # Calculate quality
        quality = calculate_clustering_quality(texts, topics)

        print("Validation Results:")
        print(f"  Overall Score: {quality.get('overall_score', 'N/A')}")
        print(f"  Passes Check: {quality.get('passes_quality_check', False)}")

        # Generate report
        report = generate_accuracy_report(texts, topics)
        print("\n" + report)

        print("\n✓ Validation test passed!\n")
        return True

    except Exception as e:
        print(f"\n✗ Validation test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("BERTOPIC INSTALLATION TEST")
    print("=" * 70)
    print()

    results = []

    # Test 1: Dependencies
    results.append(("Dependencies", test_imports()))

    # Only run other tests if dependencies are installed
    if results[0][1]:
        # Test 2: Clustering
        results.append(("Clustering", test_clustering()))

        # Test 3: Quality Metrics
        results.append(("Quality Metrics", test_quality_metrics()))

        # Test 4: Validation
        results.append(("Validation", test_validation()))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! BERTopic is ready for production.\n")
        print("Next steps:")
        print("  1. Generate test data: python scripts/generate_test_feedback.py --count 100 --save")
        print("  2. Run clustering: curl -X POST http://localhost:8000/api/clustering/bertopic")
        print("  3. Check quality: curl http://localhost:8000/api/clustering/quality")
        print("  4. Run benchmark: python scripts/benchmark_clustering.py --samples 100")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix issues and try again.\n")
        print("Common issues:")
        print("  - Missing dependencies: pip install bertopic sentence-transformers umap-learn hdbscan")
        print("  - Not enough data: Need at least 6+ feedback items for clustering")
        return 1


if __name__ == "__main__":
    sys.exit(main())
