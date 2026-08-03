# Compass WebSocket Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMPASS BACKEND                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   REST API   │      │  WebSocket   │      │   Database   │  │
│  │  Endpoints   │─────▶│   Manager    │◀─────│   SQLite     │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                                 │
│         │                      │                                 │
│         ▼                      ▼                                 │
│  ┌──────────────────────────────────────┐                       │
│  │        Event Emitter                 │                       │
│  │  - emit_feedback_synced()            │                       │
│  │  - emit_clustering_complete()        │                       │
│  │  - emit_roadmap_generated()          │                       │
│  │  - emit_stats_updated()              │                       │
│  └──────────────────────────────────────┘                       │
│                       │                                          │
└───────────────────────┼──────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   WebSocket Broadcast         │
        │   (to subscribed clients)     │
        └───────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────┐              ┌──────────────┐
│   Client 1   │              │   Client 2   │
│  (Frontend)  │              │  (Frontend)  │
└──────────────┘              └──────────────┘
```

## Component Architecture

### 1. Connection Manager (`websockets.py`)

```
ConnectionManager
├── active_connections: Dict[client_id, WebSocket]
├── rooms: Dict[room_name, Set[client_id]]
├── client_metadata: Dict[client_id, dict]
├── message_queues: Dict[client_id, List[dict]]
└── connection_times: Dict[client_id, datetime]

Methods:
├── connect(websocket, client_id) → bool
├── disconnect(client_id)
├── join_room(client_id, room_name)
├── leave_room(client_id, room_name)
├── send_personal_message(message, client_id)
├── broadcast(message, room_name?)
├── broadcast_with_rate_limit(message, room_name?, rate_limit)
├── process_message_queues() [background task]
├── heartbeat(client_id, websocket) [background task]
└── get_stats() → dict
```

### 2. Event Emitter (`events.py`)

```
EventEmitter
├── manager: ConnectionManager
├── event_history: List[dict] (max 100)
└── max_history: int

Methods:
├── emit(event_type, data, room?) → async
├── emit_feedback_new(feedback_data)
├── emit_feedback_synced(sync_results)
├── emit_clustering_complete(clustering_results)
├── emit_cluster_created(cluster_data)
├── emit_roadmap_generated(roadmap_data)
├── emit_stats_updated(stats)
├── emit_progress(task, progress, total, message)
├── emit_task_started(task, message)
├── emit_task_completed(task, results)
├── emit_task_error(task, error)
└── get_recent_events(count) → List[dict]

TaskTracker [context manager]
├── __aenter__() → emit_task_started
├── __aexit__() → emit_task_completed or emit_task_error
└── progress(current, total, message) → emit_progress
```

### 3. Integration (`main.py`)

```
FastAPI App
├── /ws [WebSocket endpoint]
│   ├── Accept connection
│   ├── Generate client_id
│   ├── Start heartbeat task
│   ├── Listen for client messages
│   └── Handle disconnect
│
├── POST /api/sources/sync
│   ├── Sync feedback from sources
│   ├── emit_feedback_new() [per item]
│   ├── emit_feedback_synced() [completion]
│   └── emit_stats_updated()
│
├── POST /api/clustering/run
│   ├── Generate embeddings
│   ├── emit_progress() [4 stages]
│   ├── Create clusters
│   ├── emit_cluster_created() [per cluster]
│   ├── emit_clustering_complete()
│   └── emit_stats_updated()
│
├── POST /api/roadmap/generate
│   ├── Calculate priorities
│   ├── emit_progress() [3 stages]
│   ├── emit_roadmap_generated()
│   └── emit_stats_updated()
│
├── GET /api/websocket/stats
│   └── Return manager.get_stats()
│
└── GET /api/events/recent?count=N
    └── Return event_emitter.get_recent_events(count)
```

## Data Flow

### Example: Feedback Sync

```
1. Client A subscribes to "feedback" room
   Client → WS: {"action": "subscribe", "rooms": ["feedback"]}

2. Client B calls REST API
   Client B → POST /api/sources/sync

3. Backend syncs feedback
   main.py → SourceManager.fetch_feedback()

4. For each new feedback item
   main.py → event_emitter.emit_feedback_new(feedback_data)
   event_emitter → manager.broadcast(event, room="feedback")
   manager → Client A (receives event)

5. Sync completes
   main.py → event_emitter.emit_feedback_synced(results)
   event_emitter → manager.broadcast(event, room="feedback")
   manager → Client A (receives event)

6. Stats updated
   main.py → event_emitter.emit_stats_updated(stats)
   event_emitter → manager.broadcast(event, room="dashboard")
   manager → All clients subscribed to "dashboard"
```

## Room System

```
Rooms (Channels)
├── "feedback"    → Feedback events
├── "clusters"    → Clustering events
├── "roadmap"     → Roadmap events
└── "dashboard"   → Stats events

Client subscribes to rooms:
{"action": "subscribe", "rooms": ["feedback", "clusters"]}

Events broadcast to specific rooms:
event_emitter.emit("event.type", data, room="feedback")
```

## Message Flow

### Client → Server

```json
{
  "action": "join|leave|subscribe|stats|ping",
  "room": "feedback",          // for join/leave
  "rooms": ["feedback", ...]   // for subscribe
}
```

### Server → Client

```json
{
  "event": "event.type",
  "data": { /* event-specific data */ },
  "timestamp": "2026-08-03T10:00:00.000000"
}
```

## Event Types

```
Connection Events
├── connection.established
├── heartbeat
├── room.joined
├── room.left
├── rooms.subscribed
├── pong
└── error

Business Events
├── feedback.new
├── feedback.synced
├── feedback.batch
├── cluster.created
├── cluster.updated
├── clustering.complete
├── roadmap.generated
├── roadmap.updated
└── stats.updated

Task Events
├── task.started
├── progress.update
├── task.completed
└── task.error
```

## Performance Features

### Rate Limiting
```
Per-client message queue (10 messages)
├── Queue full → Drop oldest message
├── Background processing (100ms interval)
└── Prevents client overwhelm
```

### Connection Pooling
```
Unlimited concurrent connections
├── Dict-based storage (O(1) lookup)
├── Automatic cleanup on disconnect
└── Room-based filtering (O(n) where n = room size)
```

### Heartbeat
```
Every 30 seconds
├── Detect dead connections
├── Keep NAT/firewall holes open
└── Client can respond (optional)
```

## Scalability

### Current (Single Server)
```
┌──────────────┐
│   Server     │
│  ┌────────┐  │
│  │Manager │  │
│  │Clients │  │
│  └────────┘  │
└──────────────┘
```

### Future (Multi-Server with Redis)
```
┌────────────┐      ┌────────────┐
│ Server 1   │      │ Server 2   │
│ ┌────────┐ │      │ ┌────────┐ │
│ │Clients │ │      │ │Clients │ │
│ └───┬────┘ │      │ └───┬────┘ │
└─────┼──────┘      └─────┼──────┘
      │                   │
      └────────┬──────────┘
               ▼
        ┌──────────┐
        │  Redis   │
        │ Pub/Sub  │
        └──────────┘
```

## Security Model

### Current (MVP - Development)
```
No authentication
├── Open WebSocket connections
├── All clients see all events
└── Suitable for internal use
```

### Production (Recommended)
```
JWT Authentication
├── Token in connection URL or header
├── Validate on connect
├── Store user_id in client_metadata
└── Filter events by user permissions

Authorization
├── Room-based access control
├── Event filtering by user role
└── Rate limiting per user

Encryption
├── WSS (WebSocket Secure)
├── TLS/SSL certificates
└── Reverse proxy (nginx)
```

## Error Handling

```
Connection Level
├── Accept failure → Log and reject
├── Send failure → Disconnect client
├── Receive failure → Disconnect client
└── Timeout → Heartbeat reconnection

Application Level
├── Invalid JSON → Send error event
├── Unknown action → Send error event
├── Invalid room → Send error event
└── Task failure → Emit task.error event

Recovery
├── Automatic client cleanup
├── Room cleanup on last client leave
├── Event history for reconnection
└── Graceful degradation
```

## Testing Strategy

```
Unit Tests (test_websocket.py)
├── 1. Basic connection
├── 2. Room subscription
├── 3. Ping/pong
├── 4. Stats request
├── 5. Multiple concurrent clients
├── 6. Event listening
└── 7. Heartbeat monitoring

Integration Tests
├── Trigger sync → Verify events
├── Trigger clustering → Verify events
├── Trigger roadmap → Verify events
└── Multi-client broadcast

Manual Tests
├── Interactive client
└── Example client
```

## File Structure

```
/home/wsl-user/compass/backend/
├── main.py                          [REST API + WebSocket endpoint]
├── websockets.py                    [ConnectionManager]
├── events.py                        [EventEmitter + TaskTracker]
├── test_websocket.py                [Test suite]
├── example_websocket_client.py      [Example usage]
├── requirements-minimal.txt         [Dependencies]
├── WEBSOCKET_README.md              [Full documentation]
├── INSTALLATION.md                  [Setup guide]
├── ARCHITECTURE.md                  [This file]
└── WEBSOCKET_IMPLEMENTATION_SUMMARY.md  [Summary]
```

## Dependencies

```
FastAPI Stack
├── fastapi==0.109.0
├── uvicorn[standard]==0.27.0
└── python-multipart==0.0.6

WebSocket
└── websockets==12.0

Database
└── sqlalchemy==2.0.25

Utilities
├── pydantic==2.5.3
├── python-dotenv==1.0.0
└── httpx==0.26.0
```

## Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout-keep-alive 60
```

### Docker
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

### Metrics to Track
```
Connection Metrics
├── Total active connections
├── Connections per room
├── Connection duration
└── Connection churn rate

Event Metrics
├── Events emitted per second
├── Event types distribution
├── Event delivery latency
└── Failed event deliveries

Performance Metrics
├── Message queue depth
├── Broadcast latency
├── Memory usage per connection
└── CPU usage
```

### Endpoints
```
GET /api/websocket/stats
├── total_connections
├── active_rooms
└── room_details

GET /api/events/recent?count=10
├── Recent events
└── Event history
```

## Future Enhancements

1. **Redis Integration** - Multi-server pub/sub
2. **Authentication** - JWT-based auth
3. **Authorization** - Role-based access
4. **Compression** - WebSocket message compression
5. **Replay** - Event replay on reconnection
6. **Filtering** - Client-side event filtering
7. **Acknowledgments** - Confirm event delivery
8. **Metrics** - Prometheus integration
9. **Admin Dashboard** - Real-time connection monitoring
10. **Load Balancing** - Sticky sessions for WebSocket
