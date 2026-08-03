"""
Compass SDK - Basic Usage Example

Demonstrates basic operations with the Compass API.
"""

from compass_sdk import CompassClient, RoadmapStatus

# Initialize client
client = CompassClient(
    api_key="compass_your_api_key_here",
    base_url="http://localhost:8000"
)


def main():
    print("=" * 60)
    print("Compass SDK - Basic Usage Example")
    print("=" * 60)

    # 1. Get dashboard statistics
    print("\n1. Dashboard Statistics")
    print("-" * 40)
    stats = client.stats()
    print(f"Total Feedback: {stats.total_feedback}")
    print(f"Total Sources: {stats.total_sources}")
    print(f"Total Clusters: {stats.total_clusters}")
    print(f"Total Roadmap Items: {stats.total_roadmap_items}")
    print(f"Revenue Impact: ${stats.total_revenue_impact:,.2f}")
    print(f"Average Sentiment: {stats.avg_sentiment:.3f}")
    print(f"Recent Feedback (30d): {stats.recent_feedback_30d}")

    # 2. List sources
    print("\n2. Feedback Sources")
    print("-" * 40)
    sources_response = client.sources.list(limit=10)
    for source in sources_response["data"]:
        status = "✓ Active" if source["is_active"] else "✗ Inactive"
        print(f"{status} {source['name']}: {source['feedback_count']} items")

    # 3. List recent feedback
    print("\n3. Recent Feedback")
    print("-" * 40)
    feedback_response = client.feedback.list(
        limit=5,
        sort_by="submitted_at",
        sort_order="desc"
    )
    for fb in feedback_response["data"]:
        sentiment = "😊" if fb["sentiment_score"] > 0.5 else "😐" if fb["sentiment_score"] > 0 else "😞"
        print(f"{sentiment} [{fb['customer_name']}] {fb['text'][:80]}...")
        print(f"   Source: {fb['source_name']}, Sentiment: {fb['sentiment_score']:.2f}")

    # 4. List top clusters
    print("\n4. Top Priority Clusters")
    print("-" * 40)
    clusters_response = client.clusters.list(
        limit=5,
        sort_by="priority_score",
        sort_order="desc"
    )
    for i, cluster in enumerate(clusters_response["data"], 1):
        print(f"{i}. {cluster['label']}")
        print(f"   Size: {cluster['size']}, Priority: {cluster['priority_score']:.2f}")
        print(f"   Revenue: ${cluster['total_revenue']:,.2f}, Sentiment: {cluster['avg_sentiment']:.2f}")

    # 5. Get cluster details
    if clusters_response["data"]:
        print("\n5. Cluster Details (First Cluster)")
        print("-" * 40)
        cluster_id = clusters_response["data"][0]["id"]
        cluster = client.clusters.get(cluster_id)
        print(f"Label: {cluster.label}")
        print(f"Size: {cluster.size} feedback items")
        print(f"\nSample feedback:")
        for fb in cluster.feedback[:3]:
            print(f"  - {fb.text[:100]}")

    # 6. List roadmap
    print("\n6. Product Roadmap (Top 5)")
    print("-" * 40)
    roadmap_response = client.roadmap.list(limit=5)
    for item in roadmap_response["data"]:
        status_emoji = {
            "proposed": "💡",
            "planned": "📋",
            "in_progress": "🚧",
            "shipped": "✅"
        }.get(item["status"], "❓")
        print(f"#{item['rank']} {status_emoji} {item['title']}")
        print(f"   Priority: {item['priority_score']:.2f}, Requests: {item['request_count']}")
        print(f"   Revenue Impact: ${item['impacted_revenue']:,.2f}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        client.close()
