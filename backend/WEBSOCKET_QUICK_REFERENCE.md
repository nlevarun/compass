# WebSocket Quick Reference

## Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

## Subscribe to Events

```javascript
ws.send(JSON.stringify({
  action: 'subscribe',
  rooms: ['feedback', 'clusters', 'roadmap', 'dashboard']
}));
```

## Event Handlers

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.event) {
    case 'feedback.new':
      // New feedback arrived
      console.log('New feedback:', data.data);
      break;

    case 'feedback.synced':
      // Sync completed
      console.log('Synced:', data.data.total_synced);
      break;

    case 'clustering.complete':
      // Clustering done
      console.log('Clusters:', data.data.clusters_created);
      break;

    case 'roadmap.generated':
      // Roadmap ready
      console.log('Items:', data.data.items_count);
      break;

    case 'stats.updated':
      // Dashboard stats changed
      console.log('Stats:', data.data);
      break;

    case 'progress.update':
      // Task progress
      const progress = data.data;
      console.log(`${progress.task}: ${progress.percentage}%`);
      break;
  }
};
```

## Client Commands

### Join Room
```javascript
ws.send(JSON.stringify({
  action: 'join',
  room: 'feedback'
}));
```

### Leave Room
```javascript
ws.send(JSON.stringify({
  action: 'leave',
  room: 'feedback'
}));
```

### Request Stats
```javascript
ws.send(JSON.stringify({
  action: 'stats'
}));
```

### Ping
```javascript
ws.send(JSON.stringify({
  action: 'ping'
}));
```

## React Hook

```typescript
import { useEffect, useState } from 'react';

function useCompassWebSocket() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onopen = () => {
      websocket.send(JSON.stringify({
        action: 'subscribe',
        rooms: ['feedback', 'clusters', 'roadmap', 'dashboard']
      }));
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  return { ws, events };
}

// Usage
function Dashboard() {
  const { events } = useCompassWebSocket();

  const latestFeedback = events
    .filter(e => e.event === 'feedback.new')
    .slice(-10);

  return (
    <div>
      {latestFeedback.map(e => (
        <div key={e.data.id}>{e.data.text}</div>
      ))}
    </div>
  );
}
```

## Python Client

```python
import asyncio
import websockets
import json

async def connect():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # Subscribe
        await ws.send(json.dumps({
            'action': 'subscribe',
            'rooms': ['feedback', 'clusters', 'roadmap']
        }))

        # Listen
        async for message in ws:
            data = json.loads(message)
            print(f"{data['event']}: {data.get('data')}")

asyncio.run(connect())
```

## Event Types

| Event | Description | Room |
|-------|-------------|------|
| `feedback.new` | New feedback item | feedback |
| `feedback.synced` | Sync complete | feedback |
| `cluster.created` | New cluster | clusters |
| `clustering.complete` | Clustering done | clusters |
| `roadmap.generated` | Roadmap ready | roadmap |
| `stats.updated` | Stats changed | dashboard |
| `progress.update` | Task progress | all |
| `task.started` | Task began | all |
| `task.completed` | Task finished | all |

## Trigger Events

```bash
# Sync feedback → feedback.synced, stats.updated
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering → clustering.complete, cluster.created
curl -X POST http://localhost:8000/api/clustering/run

# Generate roadmap → roadmap.generated
curl -X POST http://localhost:8000/api/roadmap/generate
```

## REST Endpoints

```bash
# WebSocket stats
curl http://localhost:8000/api/websocket/stats

# Recent events
curl http://localhost:8000/api/events/recent?count=10
```

## Testing

```bash
# Run test suite
python3 test_websocket.py

# Interactive client
python3 test_websocket.py --interactive

# Example client
python3 example_websocket_client.py
```

## Common Patterns

### Auto-reconnect
```javascript
class CompassWS {
  constructor() {
    this.connect();
  }

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws');

    this.ws.onclose = () => {
      console.log('Disconnected, reconnecting...');
      setTimeout(() => this.connect(), 1000);
    };
  }
}
```

### Event Buffer
```javascript
const eventBuffer = [];
const MAX_EVENTS = 100;

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  eventBuffer.push(data);

  if (eventBuffer.length > MAX_EVENTS) {
    eventBuffer.shift();
  }
};
```

### Typed Events
```typescript
interface CompassEvent {
  event: string;
  data: any;
  timestamp: string;
}

interface FeedbackNewEvent extends CompassEvent {
  event: 'feedback.new';
  data: {
    id: number;
    text: string;
    customer_name: string;
    customer_revenue: number;
  };
}

ws.onmessage = (event) => {
  const data: CompassEvent = JSON.parse(event.data);

  if (data.event === 'feedback.new') {
    const feedback = data as FeedbackNewEvent;
    console.log(feedback.data.text);
  }
};
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check server is running: `uvicorn main:app --reload` |
| No events | Subscribe to rooms first |
| Events stop | Check heartbeat, reconnect if needed |
| Wrong URL | Use `ws://` not `wss://` in development |

## Performance Tips

1. **Subscribe selectively** - Only join rooms you need
2. **Buffer events** - Don't update UI on every event
3. **Debounce updates** - Batch UI updates
4. **Reconnect logic** - Handle disconnections gracefully
5. **Event filtering** - Filter events client-side if needed

## Security (Production)

```javascript
// Use WSS in production
const ws = new WebSocket('wss://api.example.com/ws');

// Add authentication
const token = 'jwt-token-here';
const ws = new WebSocket(`wss://api.example.com/ws?token=${token}`);
```

## Files

| File | Purpose |
|------|---------|
| `websockets.py` | Connection manager |
| `events.py` | Event emitter |
| `main.py` | WebSocket endpoint |
| `test_websocket.py` | Test suite |
| `example_websocket_client.py` | Example client |
| `WEBSOCKET_README.md` | Full docs |
| `INSTALLATION.md` | Setup guide |
| `ARCHITECTURE.md` | Architecture |

---

**Ready to go!** Start server: `uvicorn main:app --reload`
