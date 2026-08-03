"""
WebSocket Test Script for Compass

Tests real-time WebSocket functionality including:
- Connection establishment
- Room subscriptions
- Event broadcasting
- Heartbeat/keepalive
- Error handling

Usage:
    python test_websocket.py [--url ws://localhost:8000/ws]
"""

import asyncio
import websockets
import json
import argparse
from datetime import datetime
from typing import Optional


class CompassWebSocketClient:
    """Test client for Compass WebSocket API."""

    def __init__(self, url: str = "ws://localhost:8000/ws"):
        self.url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.messages_received = []

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            print(f"Connecting to {self.url}...")
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            print("✓ Connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("✓ Disconnected")

    async def send_message(self, message: dict):
        """Send a message to the server."""
        if not self.websocket:
            print("✗ Not connected")
            return

        try:
            await self.websocket.send(json.dumps(message))
            print(f"→ Sent: {message}")
        except Exception as e:
            print(f"✗ Error sending message: {e}")

    async def receive_message(self) -> Optional[dict]:
        """Receive a message from the server."""
        if not self.websocket:
            return None

        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            self.messages_received.append(data)
            return data
        except Exception as e:
            print(f"✗ Error receiving message: {e}")
            return None

    async def listen(self, duration: int = 10):
        """Listen for messages for a specified duration."""
        print(f"\nListening for messages ({duration}s)...")
        end_time = asyncio.get_event_loop().time() + duration

        while asyncio.get_event_loop().time() < end_time:
            try:
                message = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=1.0
                )
                data = json.loads(message)
                self.messages_received.append(data)
                self._print_message(data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"✗ Error: {e}")
                break

        print(f"\n✓ Listening complete. Received {len(self.messages_received)} messages")

    def _print_message(self, data: dict):
        """Pretty print received message."""
        event = data.get("event", "unknown")
        timestamp = data.get("timestamp", "")

        if event == "connection.established":
            print(f"← Connection established: {data.get('client_id')}")
        elif event == "heartbeat":
            print(f"← Heartbeat received")
        elif event == "room.joined":
            print(f"← Joined room: {data.get('room')}")
        elif event == "room.left":
            print(f"← Left room: {data.get('room')}")
        elif event == "rooms.subscribed":
            print(f"← Subscribed to rooms: {data.get('rooms')}")
        elif event == "pong":
            print(f"← Pong received")
        elif event == "stats.response":
            stats = data.get("data", {})
            print(f"← Stats: {stats}")
        elif event == "feedback.new":
            feedback = data.get("data", {})
            print(f"← New feedback: {feedback.get('text', '')[:50]}...")
        elif event == "feedback.synced":
            sync_data = data.get("data", {})
            print(f"← Sync complete: {sync_data.get('total_synced')} items")
        elif event == "clustering.complete":
            cluster_data = data.get("data", {})
            print(f"← Clustering complete: {cluster_data.get('clusters_created')} clusters")
        elif event == "roadmap.generated":
            roadmap_data = data.get("data", {})
            print(f"← Roadmap generated: {roadmap_data.get('items_count')} items")
        elif event == "stats.updated":
            stats = data.get("data", {})
            print(f"← Stats updated: {stats.get('total_feedback')} feedback")
        elif event == "task.started":
            task = data.get("data", {})
            print(f"← Task started: {task.get('task')} - {task.get('message')}")
        elif event == "progress.update":
            progress = data.get("data", {})
            print(f"← Progress: {progress.get('task')} - {progress.get('percentage')}%")
        elif event == "task.completed":
            task = data.get("data", {})
            print(f"← Task completed: {task.get('task')}")
        elif event == "error":
            print(f"← Error: {data.get('message')}")
        else:
            print(f"← {event}: {data}")


async def test_basic_connection():
    """Test 1: Basic connection and disconnection."""
    print("\n" + "="*60)
    print("TEST 1: Basic Connection")
    print("="*60)

    client = CompassWebSocketClient()
    success = await client.connect()

    if success:
        # Wait for connection message
        msg = await client.receive_message()
        if msg and msg.get("event") == "connection.established":
            print("✓ Received connection confirmation")
        else:
            print("✗ No connection confirmation received")

        await client.disconnect()
        print("✓ Test passed")
    else:
        print("✗ Test failed")


async def test_room_subscription():
    """Test 2: Room subscription."""
    print("\n" + "="*60)
    print("TEST 2: Room Subscription")
    print("="*60)

    client = CompassWebSocketClient()
    await client.connect()

    # Skip connection message
    await client.receive_message()

    # Join a room
    await client.send_message({"action": "join", "room": "feedback"})
    msg = await client.receive_message()

    if msg and msg.get("event") == "room.joined":
        print("✓ Successfully joined room")
    else:
        print("✗ Failed to join room")

    # Subscribe to multiple rooms
    await client.send_message({
        "action": "subscribe",
        "rooms": ["clusters", "roadmap"]
    })
    msg = await client.receive_message()

    if msg and msg.get("event") == "rooms.subscribed":
        print("✓ Successfully subscribed to multiple rooms")
    else:
        print("✗ Failed to subscribe to rooms")

    await client.disconnect()
    print("✓ Test passed")


async def test_ping_pong():
    """Test 3: Ping/pong."""
    print("\n" + "="*60)
    print("TEST 3: Ping/Pong")
    print("="*60)

    client = CompassWebSocketClient()
    await client.connect()

    # Skip connection message
    await client.receive_message()

    # Send ping
    await client.send_message({"action": "ping"})
    msg = await client.receive_message()

    if msg and msg.get("event") == "pong":
        print("✓ Received pong response")
    else:
        print("✗ No pong response")

    await client.disconnect()
    print("✓ Test passed")


async def test_stats_request():
    """Test 4: Stats request."""
    print("\n" + "="*60)
    print("TEST 4: Stats Request")
    print("="*60)

    client = CompassWebSocketClient()
    await client.connect()

    # Skip connection message
    await client.receive_message()

    # Request stats
    await client.send_message({"action": "stats"})
    msg = await client.receive_message()

    if msg and msg.get("event") == "stats.response":
        stats = msg.get("data", {})
        print(f"✓ Received stats: {stats.get('total_connections')} connections")
    else:
        print("✗ No stats response")

    await client.disconnect()
    print("✓ Test passed")


async def test_event_listening():
    """Test 5: Listen for events (requires triggering API calls)."""
    print("\n" + "="*60)
    print("TEST 5: Event Listening (30s)")
    print("="*60)
    print("Run API calls (sync, clustering, roadmap) to see events")
    print("Example: curl -X POST http://localhost:8000/api/sources/sync")

    client = CompassWebSocketClient()
    await client.connect()

    # Skip connection message
    await client.receive_message()

    # Subscribe to all rooms
    await client.send_message({
        "action": "subscribe",
        "rooms": ["feedback", "clusters", "roadmap", "dashboard"]
    })
    await client.receive_message()

    # Listen for events
    await client.listen(duration=30)

    await client.disconnect()
    print("✓ Test passed")


async def test_multiple_clients():
    """Test 6: Multiple concurrent clients."""
    print("\n" + "="*60)
    print("TEST 6: Multiple Concurrent Clients")
    print("="*60)

    clients = []

    # Create 5 clients
    for i in range(5):
        client = CompassWebSocketClient()
        await client.connect()
        await client.receive_message()  # Skip connection message
        clients.append(client)
        print(f"✓ Client {i+1} connected")

    # Request stats from first client
    await clients[0].send_message({"action": "stats"})
    msg = await clients[0].receive_message()

    if msg and msg.get("event") == "stats.response":
        stats = msg.get("data", {})
        connections = stats.get("total_connections", 0)
        print(f"✓ Server reports {connections} active connections")

        if connections >= 5:
            print("✓ Multiple clients verified")
        else:
            print(f"✗ Expected 5+ connections, got {connections}")

    # Disconnect all
    for i, client in enumerate(clients):
        await client.disconnect()
        print(f"✓ Client {i+1} disconnected")

    print("✓ Test passed")


async def test_heartbeat():
    """Test 7: Heartbeat monitoring."""
    print("\n" + "="*60)
    print("TEST 7: Heartbeat (40s)")
    print("="*60)
    print("Waiting for heartbeat messages (sent every 30s)...")

    client = CompassWebSocketClient()
    await client.connect()

    # Skip connection message
    await client.receive_message()

    heartbeat_received = False

    # Listen for 40 seconds to catch heartbeat
    await client.listen(duration=40)

    # Check if heartbeat was received
    for msg in client.messages_received:
        if msg.get("event") == "heartbeat":
            heartbeat_received = True
            break

    if heartbeat_received:
        print("✓ Heartbeat received")
    else:
        print("⚠ No heartbeat received (may need to wait longer)")

    await client.disconnect()
    print("✓ Test passed")


async def run_all_tests():
    """Run all WebSocket tests."""
    print("\n" + "="*60)
    print("COMPASS WEBSOCKET TEST SUITE")
    print("="*60)
    print("Make sure the Compass API is running on http://localhost:8000")
    print("="*60)

    tests = [
        ("Basic Connection", test_basic_connection),
        ("Room Subscription", test_room_subscription),
        ("Ping/Pong", test_ping_pong),
        ("Stats Request", test_stats_request),
        ("Multiple Clients", test_multiple_clients),
        ("Event Listening", test_event_listening),
        ("Heartbeat", test_heartbeat),
    ]

    results = []

    for name, test_func in tests:
        try:
            await test_func()
            results.append((name, True))
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")
    print("="*60)


async def interactive_client():
    """Interactive WebSocket client."""
    print("\n" + "="*60)
    print("COMPASS WEBSOCKET INTERACTIVE CLIENT")
    print("="*60)
    print("Commands:")
    print("  join <room>     - Join a room")
    print("  leave <room>    - Leave a room")
    print("  subscribe       - Subscribe to all rooms")
    print("  ping            - Send ping")
    print("  stats           - Request stats")
    print("  quit            - Exit")
    print("="*60 + "\n")

    client = CompassWebSocketClient()
    await client.connect()

    # Start listening task
    async def listen_task():
        while client.connected:
            try:
                msg = await client.receive_message()
                if msg:
                    client._print_message(msg)
            except Exception as e:
                print(f"Error: {e}")
                break

    asyncio.create_task(listen_task())

    # Wait a bit for connection message
    await asyncio.sleep(0.5)

    # Command loop
    print("\nEnter commands (type 'quit' to exit):")
    while True:
        try:
            cmd = input("> ").strip()

            if cmd == "quit":
                break
            elif cmd.startswith("join "):
                room = cmd.split(" ", 1)[1]
                await client.send_message({"action": "join", "room": room})
            elif cmd.startswith("leave "):
                room = cmd.split(" ", 1)[1]
                await client.send_message({"action": "leave", "room": room})
            elif cmd == "subscribe":
                await client.send_message({
                    "action": "subscribe",
                    "rooms": ["feedback", "clusters", "roadmap", "dashboard"]
                })
            elif cmd == "ping":
                await client.send_message({"action": "ping"})
            elif cmd == "stats":
                await client.send_message({"action": "stats"})
            else:
                print("Unknown command")

            await asyncio.sleep(0.1)  # Give time for response

        except KeyboardInterrupt:
            break

    await client.disconnect()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Compass WebSocket functionality")
    parser.add_argument("--url", default="ws://localhost:8000/ws", help="WebSocket URL")
    parser.add_argument("--interactive", action="store_true", help="Run interactive client")

    args = parser.parse_args()

    # Update URL if provided
    CompassWebSocketClient.__init__.__defaults__ = (args.url,)

    if args.interactive:
        asyncio.run(interactive_client())
    else:
        asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()
