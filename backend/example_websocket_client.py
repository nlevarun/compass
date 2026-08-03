"""
Simple Example WebSocket Client for Compass

Demonstrates how to connect and receive real-time updates.

Usage:
    python example_websocket_client.py
"""

import asyncio
import websockets
import json


async def compass_realtime_client():
    """
    Simple example client that connects to Compass and displays real-time updates.
    """
    uri = "ws://localhost:8000/ws"

    print("Connecting to Compass WebSocket API...")

    async with websockets.connect(uri) as websocket:
        print("✓ Connected!")

        # Receive connection confirmation
        message = await websocket.recv()
        data = json.loads(message)
        print(f"← {data}")

        # Subscribe to all data types
        print("\nSubscribing to real-time updates...")
        await websocket.send(json.dumps({
            "action": "subscribe",
            "rooms": ["feedback", "clusters", "roadmap", "dashboard"]
        }))

        # Receive subscription confirmation
        message = await websocket.recv()
        data = json.loads(message)
        print(f"← {data}")

        print("\n" + "="*60)
        print("LISTENING FOR REAL-TIME UPDATES")
        print("="*60)
        print("Trigger events by making API calls:")
        print("  - POST /api/sources/sync")
        print("  - POST /api/clustering/run")
        print("  - POST /api/roadmap/generate")
        print("\nPress Ctrl+C to exit\n")

        # Listen for events
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                # Pretty print events
                event_type = data.get("event")
                timestamp = data.get("timestamp", "")

                if event_type == "heartbeat":
                    print(f"[{timestamp}] 💓 Heartbeat")

                elif event_type == "feedback.new":
                    feedback = data.get("data", {})
                    print(f"\n[{timestamp}] 📝 NEW FEEDBACK")
                    print(f"  Text: {feedback.get('text', '')[:60]}...")
                    print(f"  Customer: {feedback.get('customer_name')}")
                    print(f"  Revenue: ${feedback.get('customer_revenue', 0):,.2f}")

                elif event_type == "feedback.synced":
                    sync_data = data.get("data", {})
                    print(f"\n[{timestamp}] 🔄 SYNC COMPLETE")
                    print(f"  Total synced: {sync_data.get('total_synced')}")
                    print(f"  Sources: {sync_data.get('sources_synced')}")
                    print(f"  Time: {sync_data.get('elapsed_time')}s")

                elif event_type == "clustering.complete":
                    cluster_data = data.get("data", {})
                    print(f"\n[{timestamp}] 🎯 CLUSTERING COMPLETE")
                    print(f"  Clusters created: {cluster_data.get('clusters_created')}")
                    print(f"  Feedback clustered: {cluster_data.get('feedback_clustered')}")
                    print(f"  Noise points: {cluster_data.get('noise_points')}")
                    print(f"  Time: {cluster_data.get('elapsed_time')}s")

                elif event_type == "cluster.created":
                    cluster = data.get("data", {})
                    print(f"\n[{timestamp}] ➕ NEW CLUSTER")
                    print(f"  Label: {cluster.get('label')}")
                    print(f"  Size: {cluster.get('size')}")
                    print(f"  Revenue: ${cluster.get('total_revenue', 0):,.2f}")
                    print(f"  Sentiment: {cluster.get('avg_sentiment', 0):.2f}")

                elif event_type == "roadmap.generated":
                    roadmap_data = data.get("data", {})
                    print(f"\n[{timestamp}] 🗺️  ROADMAP GENERATED")
                    print(f"  Items: {roadmap_data.get('items_count')}")
                    if "items" in roadmap_data:
                        print(f"  Top 3 priorities:")
                        for i, item in enumerate(roadmap_data.get("items", [])[:3], 1):
                            print(f"    {i}. {item.get('title')} (score: {item.get('priority_score'):.2f})")

                elif event_type == "stats.updated":
                    stats = data.get("data", {})
                    print(f"\n[{timestamp}] 📊 STATS UPDATED")
                    print(f"  Total feedback: {stats.get('total_feedback')}")
                    print(f"  Clusters: {stats.get('total_clusters')}")
                    print(f"  Roadmap items: {stats.get('total_roadmap_items')}")
                    print(f"  Revenue impact: ${stats.get('total_revenue_impact', 0):,.2f}")
                    print(f"  Avg sentiment: {stats.get('avg_sentiment', 0):.3f}")

                elif event_type == "task.started":
                    task_data = data.get("data", {})
                    print(f"\n[{timestamp}] ▶️  TASK STARTED")
                    print(f"  Task: {task_data.get('task')}")
                    print(f"  Message: {task_data.get('message')}")

                elif event_type == "progress.update":
                    progress = data.get("data", {})
                    percentage = progress.get("percentage", 0)
                    task = progress.get("task")
                    message = progress.get("message", "")
                    bar_length = 30
                    filled = int(bar_length * percentage / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    print(f"\r[{task}] {bar} {percentage}% - {message}", end="", flush=True)

                elif event_type == "task.completed":
                    task_data = data.get("data", {})
                    print(f"\n[{timestamp}] ✅ TASK COMPLETED")
                    print(f"  Task: {task_data.get('task')}")
                    results = task_data.get("results", {})
                    if "elapsed_time" in results:
                        print(f"  Time: {results.get('elapsed_time')}s")

                elif event_type == "task.error":
                    task_data = data.get("data", {})
                    print(f"\n[{timestamp}] ❌ TASK ERROR")
                    print(f"  Task: {task_data.get('task')}")
                    print(f"  Error: {task_data.get('error')}")

                else:
                    print(f"\n[{timestamp}] {event_type}")
                    print(f"  Data: {data.get('data')}")

        except KeyboardInterrupt:
            print("\n\nDisconnecting...")


if __name__ == "__main__":
    print("="*60)
    print("COMPASS REAL-TIME CLIENT")
    print("="*60)
    print("This client demonstrates real-time updates from Compass.")
    print("Make sure the Compass API is running on http://localhost:8000")
    print("="*60 + "\n")

    try:
        asyncio.run(compass_realtime_client())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the Compass API server is running!")
