# Compass WebSocket Real-Time API

Real-time WebSocket implementation for streaming feedback, clustering, and roadmap updates.

## Overview

The Compass WebSocket API provides real-time event streaming for all major operations:

- **Feedback ingestion** - Stream new feedback as it arrives
- **Clustering** - Real-time clustering progress and results
- **Roadmap generation** - Live roadmap updates
- **Dashboard stats** - Real-time statistics updates
- **Task progress** - Live progress tracking for long-running operations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-minimal.txt
```

### 2. Start the Server

```bash
cd /home/wsl-user/compass/backend
uvicorn main:app --reload
```

The WebSocket endpoint will be available at: `ws://localhost:8000/ws`

### 3. Connect a Client

```python
import asyncio
import websockets
import json

async def connect():
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        # Receive connection confirmation
        msg = await ws.recv()
        print(json.loads(msg))

        # Subscribe to events
        await ws.send(json.dumps({
            "action": "subscribe",
            "rooms": ["feedback", "clusters", "roadmap"]
        }))

        # Listen for events
        while True:
            msg = await ws.recv()
            print(json.loads(msg))

asyncio.run(connect())
```

## WebSocket Protocol

### Connection

Connect to `ws://localhost:8000/ws`. Upon connection, you'll receive:

```json
{
  "event": "connection.established",
  "client_id": "uuid-here",
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

### Client Messages

Send JSON messages to interact with the server:

#### Join a Room

```json
{
  "action": "join",
  "room": "feedback"
}
```

**Available rooms:**
- `feedback` - New feedback events
- `clusters` - Clustering events
- `roadmap` - Roadmap updates
- `dashboard` - Stats updates

#### Subscribe to Multiple Rooms

```json
{
  "action": "subscribe",
  "rooms": ["feedback", "clusters", "roadmap", "dashboard"]
}
```

#### Leave a Room

```json
{
  "action": "leave",
  "room": "feedback"
}
```

#### Request Stats

```json
{
  "action": "stats"
}
```

Response:
```json
{
  "event": "stats.response",
  "data": {
    "total_connections": 5,
    "active_rooms": 3,
    "room_details": {
      "feedback": 2,
      "clusters": 1
    }
  }
}
```

#### Ping

```json
{
  "action": "ping"
}
```

Response:
```json
{
  "event": "pong",
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

### Server Events

All events follow this structure:

```json
{
  "event": "event.type",
  "data": { /* event-specific data */ },
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

#### Feedback Events

**feedback.new** - New feedback ingested
```json
{
  "event": "feedback.new",
  "data": {
    "id": 123,
    "text": "Love the new feature!",
    "customer_name": "Acme Corp",
    "customer_revenue": 50000,
    "source_name": "Slack",
    "submitted_at": "2026-08-03T09:30:00.000000"
  }
}
```

**feedback.synced** - Sync completed
```json
{
  "event": "feedback.synced",
  "data": {
    "total_synced": 25,
    "sources_synced": 3,
    "elapsed_time": 2.5
  }
}
```

#### Clustering Events

**cluster.created** - New cluster created
```json
{
  "event": "cluster.created",
  "data": {
    "id": 5,
    "label": "Mobile App Performance Issues",
    "size": 12,
    "total_revenue": 250000,
    "avg_sentiment": -0.45
  }
}
```

**clustering.complete** - Clustering finished
```json
{
  "event": "clustering.complete",
  "data": {
    "feedback_clustered": 100,
    "clusters_created": 8,
    "noise_points": 5,
    "elapsed_time": 15.3
  }
}
```

#### Roadmap Events

**roadmap.generated** - Roadmap created
```json
{
  "event": "roadmap.generated",
  "data": {
    "items_count": 8,
    "items": [
      {
        "id": 1,
        "title": "Mobile App Performance",
        "rank": 1,
        "priority_score": 0.92
      }
    ]
  }
}
```

#### Stats Events

**stats.updated** - Dashboard stats changed
```json
{
  "event": "stats.updated",
  "data": {
    "total_feedback": 100,
    "total_clusters": 8,
    "total_roadmap_items": 8,
    "total_revenue_impact": 1250000,
    "avg_sentiment": 0.15
  }
}
```

#### Task Events

**task.started** - Long-running task started
```json
{
  "event": "task.started",
  "data": {
    "task": "clustering",
    "message": "Running NLP clustering"
  }
}
```

**progress.update** - Task progress update
```json
{
  "event": "progress.update",
  "data": {
    "task": "clustering",
    "progress": 50,
    "total": 100,
    "percentage": 50.0,
    "message": "Generating embeddings..."
  }
}
```

**task.completed** - Task finished
```json
{
  "event": "task.completed",
  "data": {
    "task": "clustering",
    "results": {
      "elapsed_time": 15.3
    }
  }
}
```

**task.error** - Task failed
```json
{
  "event": "task.error",
  "data": {
    "task": "sync",
    "error": "Connection timeout"
  }
}
```

#### System Events

**heartbeat** - Keepalive ping (every 30s)
```json
{
  "event": "heartbeat",
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

## Testing

### Run Test Suite

```bash
cd /home/wsl-user/compass/backend
python test_websocket.py
```

Tests include:
1. Basic connection
2. Room subscription
3. Ping/pong
4. Stats request
5. Multiple concurrent clients
6. Event listening
7. Heartbeat monitoring

### Run Interactive Client

```bash
python test_websocket.py --interactive
```

Commands:
- `join <room>` - Join a room
- `leave <room>` - Leave a room
- `subscribe` - Subscribe to all rooms
- `ping` - Send ping
- `stats` - Request stats
- `quit` - Exit

### Run Example Client

```bash
python example_websocket_client.py
```

This demonstrates a real-world client that displays formatted events.

## Architecture

### Components

**`websockets.py`** - Connection manager
- Manages WebSocket connections
- Handles room subscriptions
- Broadcasts messages
- Rate limiting and queuing
- Heartbeat/keepalive

**`events.py`** - Event emitter
- Emits typed events
- Event history tracking
- Task tracking context manager
- Async/sync helper functions

**`main.py`** - Integration
- WebSocket endpoint (`/ws`)
- Event emission in API endpoints
- Stats and event history endpoints

### Flow

```
API Endpoint → EventEmitter → WebSocket Manager → Connected Clients
```

Example:
1. User calls `POST /api/sources/sync`
2. Endpoint emits `feedback.synced` event via EventEmitter
3. EventEmitter broadcasts to WebSocket Manager
4. Manager sends to all clients subscribed to "feedback" room

## Frontend Integration

### JavaScript/TypeScript

```typescript
class CompassWebSocket {
  private ws: WebSocket;

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws');

    this.ws.onopen = () => {
      // Subscribe to events
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        rooms: ['feedback', 'clusters', 'roadmap']
      }));
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };
  }

  handleEvent(data: any) {
    switch (data.event) {
      case 'feedback.new':
        // Update UI with new feedback
        break;
      case 'clustering.complete':
        // Refresh clusters
        break;
      case 'stats.updated':
        // Update dashboard
        break;
    }
  }
}
```

### React Hook

```typescript
import { useEffect, useState } from 'react';

function useCompassWebSocket(rooms: string[]) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      ws.send(JSON.stringify({
        action: 'subscribe',
        rooms
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    };

    return () => ws.close();
  }, [rooms]);

  return events;
}

// Usage
function Dashboard() {
  const events = useCompassWebSocket(['feedback', 'dashboard']);

  // events array contains all received events
}
```

## Performance

### Connection Pooling
- Supports unlimited concurrent connections
- Per-connection message queuing
- Automatic cleanup on disconnect

### Rate Limiting
- Per-connection queue (default: 10 messages)
- Drop old messages when queue is full
- Background queue processing (100ms interval)

### Graceful Degradation
- Automatic reconnection handling
- Heartbeat monitoring (30s interval)
- Error recovery and logging

### Scalability Considerations

For production deployments with many connections:

1. **Use Redis for pub/sub** - Share events across multiple server instances
2. **Connection limits** - Set `uvicorn --limit-concurrency`
3. **Load balancing** - Use sticky sessions for WebSocket connections
4. **Message compression** - Enable WebSocket compression
5. **Monitoring** - Track connection counts via `/api/websocket/stats`

## API Endpoints

### WebSocket Stats

**GET** `/api/websocket/stats`

Returns current WebSocket statistics:

```json
{
  "total_connections": 5,
  "active_rooms": 3,
  "room_details": {
    "feedback": 2,
    "clusters": 1,
    "roadmap": 2
  },
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

### Recent Events

**GET** `/api/events/recent?count=10`

Returns recent event history:

```json
{
  "events": [
    {
      "event": "feedback.new",
      "data": {...},
      "timestamp": "..."
    }
  ],
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

## Security Considerations

### Current Implementation (MVP)

- No authentication required
- Open WebSocket connections
- Suitable for internal/development use

### Production Recommendations

1. **Authentication**
   - JWT token in connection URL: `ws://host/ws?token=jwt-token`
   - Validate token on connection
   - Store user ID in client metadata

2. **Authorization**
   - Room-based permissions
   - Filter events based on user access
   - Rate limiting per user

3. **Encryption**
   - Use WSS (WebSocket Secure) in production
   - TLS/SSL certificates
   - Reverse proxy (nginx, Caddy)

4. **Input Validation**
   - Validate all client messages
   - Sanitize room names
   - Limit message size

## Troubleshooting

### Connection Refused

**Problem:** Cannot connect to WebSocket

**Solution:**
1. Ensure server is running: `uvicorn main:app --reload`
2. Check firewall settings
3. Verify URL: `ws://localhost:8000/ws` (not `wss://`)

### No Events Received

**Problem:** Connected but not receiving events

**Solution:**
1. Subscribe to rooms: `{"action": "subscribe", "rooms": [...]}`
2. Trigger events by calling API endpoints
3. Check event history: `GET /api/events/recent`

### Heartbeat Timeout

**Problem:** Connection drops after 30 seconds

**Solution:**
1. Implement heartbeat response in client
2. Set longer timeout in uvicorn: `--timeout-keep-alive 60`
3. Use reverse proxy with WebSocket keep-alive

### High Memory Usage

**Problem:** Server memory grows with many connections

**Solution:**
1. Enable message rate limiting
2. Limit event history: Adjust `max_history` in EventEmitter
3. Use Redis for event storage instead of in-memory

## Examples

See:
- `test_websocket.py` - Comprehensive test suite
- `example_websocket_client.py` - Simple example client
- Frontend integration examples above

## Contributing

When adding new events:

1. Add event emitter method in `events.py`:
   ```python
   async def emit_my_event(self, data: dict):
       await self.emit("my.event", data, room="my_room")
   ```

2. Emit in API endpoint:
   ```python
   await event_emitter.emit_my_event({"key": "value"})
   ```

3. Document in this README

## License

Part of the Compass Customer Feedback Intelligence Platform.
