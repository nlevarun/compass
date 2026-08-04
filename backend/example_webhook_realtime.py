"""
Example: Real-Time Webhook Demo

This script demonstrates the real-time nature of the webhook system.
It connects via WebSocket and shows events as they arrive.

Usage:
    python example_webhook_realtime.py

Then trigger a webhook (e.g., POST to /webhooks/slack/test) and watch it appear instantly!
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime


async def listen_for_events():
    """Connect to Compass WebSocket and listen for real-time events."""
    uri = "ws://localhost:8000/ws"

    print("🔌 Connecting to Compass WebSocket...")
    print(f"   URI: {uri}")
    print()

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Compass!")
            print()
            print("📡 Listening for real-time events...")
            print("   Try triggering a webhook:")
            print("   - curl http://localhost:8000/webhooks/slack/test")
            print("   - curl http://localhost:8000/webhooks/github/test")
            print("   - curl http://localhost:8000/webhooks/intercom/test")
            print()
            print("=" * 80)
            print()

            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    handle_event(data)
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON: {message}")
                except KeyboardInterrupt:
                    print("\n👋 Disconnecting...")
                    break

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        print()
        print("Is the backend running? Try: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_event(data):
    """Handle and display a WebSocket event."""
    event_type = data.get("event")
    timestamp = data.get("timestamp", "")
    event_data = data.get("data", {})

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M:%S")
    except:
        time_str = timestamp

    # Handle different event types
    if event_type == "connection.established":
        print(f"🟢 [{time_str}] Connected!")
        print(f"   Client ID: {event_data.get('client_id')}")
        print()

    elif event_type == "feedback.new":
        # 🎉 This is the magic moment - new feedback arrived via webhook!
        print("⚡" * 40)
        print(f"🎉 [{time_str}] NEW FEEDBACK (Real-Time!)")
        print("⚡" * 40)
        print(f"   Source: {event_data.get('source')}")
        print(f"   Customer: {event_data.get('customer_name')}")
        print(f"   Text: {event_data.get('text', '')[:100]}...")

        # Show latency metrics
        latency = event_data.get('processing_time_ms')
        if latency:
            print(f"   Latency: {latency:.2f}ms ⚡")

            # Comparison
            polling_time_ms = 5 * 60 * 1000  # 5 minutes
            improvement = polling_time_ms / latency
            print(f"   vs Polling: {improvement:.0f}x faster!")

        print()

    elif event_type == "feedback.synced":
        print(f"📥 [{time_str}] Feedback synced")
        print(f"   New items: {event_data.get('new_items', 0)}")
        print()

    elif event_type == "clustering.complete":
        print(f"🔗 [{time_str}] Clustering complete")
        print(f"   Clusters: {event_data.get('total_clusters', 0)}")
        print()

    elif event_type == "roadmap.generated":
        print(f"🗺️  [{time_str}] Roadmap generated")
        print(f"   Items: {event_data.get('total_items', 0)}")
        print()

    elif event_type == "notification":
        level = event_data.get('level', 'info')
        title = event_data.get('title', '')
        message = event_data.get('message', '')

        emoji = {
            'success': '✅',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌'
        }.get(level, 'ℹ️')

        print(f"{emoji} [{time_str}] {title}")
        if message:
            print(f"   {message}")
        print()

    elif event_type == "heartbeat":
        # Don't print heartbeats (too noisy)
        pass

    else:
        # Unknown event type
        print(f"📨 [{time_str}] {event_type}")
        print(f"   Data: {json.dumps(event_data, indent=2)}")
        print()


async def demo_mode():
    """
    Demo mode: Trigger webhooks automatically and show the real-time response.
    """
    print("🎬 DEMO MODE - Automated Webhook Demo")
    print()
    print("This will:")
    print("1. Connect to WebSocket")
    print("2. Trigger 3 webhook events")
    print("3. Show real-time delivery (<1 second)")
    print()

    # Start listening in background
    listen_task = asyncio.create_task(listen_for_events())

    # Wait for connection
    await asyncio.sleep(2)

    # Trigger webhooks
    import httpx

    services = ["slack", "github", "intercom"]

    for i, service in enumerate(services, 1):
        print(f"\n🚀 [{i}/3] Triggering {service.title()} webhook...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8000/webhooks/{service}/test")

                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Webhook sent successfully")
                    print(f"   Backend processed in: {result.get('processing_time_ms', 0):.2f}ms")
                else:
                    print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Wait to see the real-time event
        await asyncio.sleep(3)

    print("\n✨ Demo complete!")
    print("The events you saw above arrived in <1 second via WebSocket.")
    print("Compare to polling: Would take 5 minutes to see all 3!")
    print()
    print("Press Ctrl+C to exit...")

    # Keep listening
    await listen_task


def main():
    """Main entry point."""
    # Check if demo mode
    demo = "--demo" in sys.argv

    if demo:
        print("=" * 80)
        print("COMPASS REAL-TIME WEBHOOK DEMO")
        print("=" * 80)
        print()
        asyncio.run(demo_mode())
    else:
        print("=" * 80)
        print("COMPASS REAL-TIME EVENT LISTENER")
        print("=" * 80)
        print()
        asyncio.run(listen_for_events())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
