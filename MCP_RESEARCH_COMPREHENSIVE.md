# Model Context Protocol (MCP) & Modern Connector Architectures
## Deep Technical Research for Compass 2026

**Date**: August 4, 2026
**Purpose**: Understand cutting-edge integration patterns and position Compass for next-gen connector architecture
**Status**: Comprehensive Research Report

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Part I: Model Context Protocol (MCP)](#part-i-model-context-protocol-mcp)
3. [Part II: Modern Connector Patterns](#part-ii-modern-connector-patterns)
4. [Part III: Competitive Connector Platforms](#part-iii-competitive-connector-platforms)
5. [Part IV: MCP for Compass](#part-iv-mcp-for-compass)
6. [Part V: Architecture Recommendations](#part-v-architecture-recommendations)
7. [Appendices](#appendices)

---

## Executive Summary

### What is MCP?

**Model Context Protocol (MCP)** is Anthropic's open protocol for enabling AI models (like Claude) to securely connect to data sources and tools. Released in November 2024, MCP standardizes how AI applications interact with external systems.

### Key Findings

1. **MCP vs Traditional APIs**:
   - MCP is optimized for AI-to-data communication
   - Traditional APIs (REST/GraphQL) remain better for app-to-app communication
   - MCP excels at providing structured context to AI models

2. **Current State (2026)**:
   - Growing ecosystem with 100+ MCP servers
   - Major platforms (GitHub, Slack, Google Drive) have MCP servers
   - Python and TypeScript are primary implementation languages

3. **For Compass**:
   - MCP could enable AI-powered feedback analysis
   - Natural fit for Claude integration
   - Positions Compass as "AI-native" platform
   - Competitive advantage in 2026-2027 market

### Recommendations for Compass

1. **Short-term (Q3 2026)**: Keep current REST/WebSocket architecture
2. **Medium-term (Q4 2026)**: Build MCP server for Compass data
3. **Long-term (2027)**: Dual protocol support (REST + MCP)

---

## Part I: Model Context Protocol (MCP)

### 1.1 What is MCP?

#### Core Concept

MCP is a **standardized protocol** that enables AI models to:
- Connect to data sources (databases, APIs, filesystems)
- Execute tools and actions
- Maintain secure, controlled access
- Provide structured context to LLMs

#### Architecture

```
┌─────────────┐         MCP Protocol         ┌─────────────┐
│             │◄────────────────────────────►│             │
│  MCP Client │      (JSON-RPC over          │  MCP Server │
│  (Claude)   │       stdio/SSE/WebSocket)   │  (Data)     │
│             │                               │             │
└─────────────┘                               └─────────────┘
       │                                             │
       │ Requests                                    │ Provides
       │ - Resources                                 │ - Resources
       │ - Tools                                     │ - Tools
       │ - Prompts                                   │ - Prompts
       └─────────────────────────────────────────────┘
```

### 1.2 MCP Specification

#### Protocol Details

**Transport Layers**:
- **stdio**: Standard input/output (local processes)
- **SSE**: Server-Sent Events (HTTP-based streaming)
- **WebSocket**: Bidirectional streaming (future)

**Message Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "resources/read",
  "params": {
    "uri": "compass://feedback/123"
  },
  "id": 1
}
```

**Core Primitives**:

1. **Resources**: Data exposed by server
   - URI-based addressing
   - MIME types for content
   - Read-only access

2. **Tools**: Actions the client can invoke
   - Function-like interface
   - Input schemas (JSON Schema)
   - Output results

3. **Prompts**: Reusable prompt templates
   - Parameterized templates
   - Multi-turn conversations
   - Context injection

4. **Sampling**: Server-initiated LLM requests
   - Server can ask client to use LLM
   - Bidirectional AI assistance

#### Authentication & Security

```
┌─────────────────────────────────────┐
│ Security Layers                     │
├─────────────────────────────────────┤
│ 1. Transport Security (TLS)         │
│ 2. Authentication (OAuth/API Keys)  │
│ 3. Authorization (Resource scopes)  │
│ 4. Rate Limiting                    │
│ 5. Audit Logging                    │
└─────────────────────────────────────┘
```

### 1.3 How MCP Works

#### Request Flow

```
1. Client (Claude) sends initialization
   ┌─────────────────────────────────────┐
   │ initialize                          │
   │ {                                   │
   │   "protocolVersion": "2024-11-05",  │
   │   "capabilities": {...}             │
   │ }                                   │
   └─────────────────────────────────────┘

2. Server responds with capabilities
   ┌─────────────────────────────────────┐
   │ initialized                         │
   │ {                                   │
   │   "protocolVersion": "2024-11-05",  │
   │   "capabilities": {                 │
   │     "resources": {},                │
   │     "tools": {}                     │
   │   }                                 │
   │ }                                   │
   └─────────────────────────────────────┘

3. Client requests resource list
   ┌─────────────────────────────────────┐
   │ resources/list                      │
   └─────────────────────────────────────┘

4. Server returns available resources
   ┌─────────────────────────────────────┐
   │ resources:                          │
   │ [                                   │
   │   {                                 │
   │     "uri": "compass://feedback",    │
   │     "name": "Feedback Inbox",       │
   │     "mimeType": "application/json"  │
   │   }                                 │
   │ ]                                   │
   └─────────────────────────────────────┘

5. Client reads specific resource
   ┌─────────────────────────────────────┐
   │ resources/read                      │
   │ {"uri": "compass://feedback/123"}   │
   └─────────────────────────────────────┘

6. Server returns resource content
   ┌─────────────────────────────────────┐
   │ {                                   │
   │   "contents": [{                    │
   │     "uri": "compass://feedback/123",│
   │     "mimeType": "application/json", │
   │     "text": "{...feedback data...}" │
   │   }]                                │
   │ }                                   │
   └─────────────────────────────────────┘
```

### 1.4 Problems MCP Solves

#### Traditional Integration Pain Points

1. **Custom Integrations for Each AI App**
   - Every AI app needs custom code for each data source
   - No standardization = fragmentation
   - **MCP Solution**: One server, many clients

2. **Security & Permissions**
   - Hard to control what AI can access
   - All-or-nothing access models
   - **MCP Solution**: Resource-level permissions

3. **Context Management**
   - AI needs structured data in specific formats
   - Manual prompt engineering for each source
   - **MCP Solution**: Standardized resource schemas

4. **Discovery & Documentation**
   - No standard way to describe capabilities
   - Each integration documented differently
   - **MCP Solution**: Self-describing servers

### 1.5 MCP Server Implementation

#### Basic Python MCP Server

```python
from mcp.server import Server
from mcp.types import Resource, Tool

# Create server
server = Server("compass-mcp-server")

# Define resources
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="compass://feedback",
            name="Feedback Inbox",
            mimeType="application/json",
            description="All feedback entries"
        ),
        Resource(
            uri="compass://clusters",
            name="Feedback Clusters",
            mimeType="application/json",
            description="NLP-generated feedback clusters"
        )
    ]

# Define resource readers
@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "compass://feedback":
        # Fetch from database
        feedback = await get_all_feedback()
        return json.dumps(feedback)

    if uri.startswith("compass://feedback/"):
        feedback_id = uri.split("/")[-1]
        feedback = await get_feedback_by_id(feedback_id)
        return json.dumps(feedback)

    raise ValueError(f"Unknown resource: {uri}")

# Define tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_feedback",
            description="Create new feedback entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["text", "source"]
            }
        )
    ]

# Define tool handlers
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "create_feedback":
        feedback_id = await create_feedback_in_db(arguments)
        return json.dumps({"id": feedback_id, "status": "created"})

    raise ValueError(f"Unknown tool: {name}")

# Run server
if __name__ == "__main__":
    server.run()
```

#### Running the Server

```bash
# Install MCP Python SDK
pip install mcp

# Run server (stdio transport)
python mcp_server.py

# Run server (SSE transport)
uvicorn mcp_server:app --host 0.0.0.0 --port 8080
```

### 1.6 Existing MCP Servers (2026)

#### Official MCP Servers

1. **GitHub MCP Server** (`@modelcontextprotocol/server-github`)
   - Resources: repos, issues, PRs, files
   - Tools: create_issue, create_pr, search_code
   - Authentication: GitHub PAT

2. **Slack MCP Server** (`@modelcontextprotocol/server-slack`)
   - Resources: channels, messages, threads
   - Tools: send_message, create_channel, search_messages
   - Authentication: OAuth 2.0

3. **Google Drive MCP Server** (`@modelcontextprotocol/server-gdrive`)
   - Resources: files, folders
   - Tools: upload, download, share
   - Authentication: OAuth 2.0

4. **PostgreSQL MCP Server** (`@modelcontextprotocol/server-postgres`)
   - Resources: schemas, tables, views
   - Tools: query, insert, update
   - Authentication: Connection string

5. **Filesystem MCP Server** (`@modelcontextprotocol/server-filesystem`)
   - Resources: files, directories
   - Tools: read, write, search
   - Authentication: Path restrictions

#### Community MCP Servers (Selected)

- **Jira** - Issues, boards, sprints
- **Notion** - Pages, databases
- **Linear** - Issues, projects
- **Figma** - Files, comments
- **Stripe** - Customers, payments
- **MongoDB** - Collections, documents
- **Redis** - Keys, values
- **Elasticsearch** - Indices, documents

#### MCP Server Registry

- Official registry: https://github.com/modelcontextprotocol/servers
- 100+ servers as of Q2 2026
- Growing ecosystem

### 1.7 MCP vs Traditional APIs

#### Comparison Matrix

| Feature | REST API | GraphQL | WebSocket | MCP |
|---------|----------|---------|-----------|-----|
| **Purpose** | App-to-app | App-to-app | Real-time | AI-to-data |
| **Format** | JSON/XML | JSON | Binary/JSON | JSON-RPC |
| **Discovery** | OpenAPI | Schema | N/A | Built-in |
| **Streaming** | SSE/polling | Subscriptions | Native | SSE |
| **Tools** | Endpoints | Mutations | Messages | Tools |
| **Resources** | Endpoints | Queries | Messages | Resources |
| **AI-Optimized** | No | No | No | Yes |
| **Self-describing** | OpenAPI | Schema | No | Yes |
| **Bidirectional** | No | Subscriptions | Yes | Yes |
| **Standardized** | HTTP | GraphQL spec | WebSocket | MCP spec |

#### When to Use Each

**REST API**:
- Traditional app-to-app communication
- CRUD operations
- Public APIs
- Mobile/web apps
- **Example**: Compass REST API for frontend

**GraphQL**:
- Complex data requirements
- Flexible queries
- Reduce over-fetching
- BFF (Backend for Frontend)
- **Example**: Compass data aggregation

**WebSocket**:
- Real-time updates
- Bidirectional communication
- Low latency requirements
- **Example**: Compass dashboard updates

**MCP**:
- AI integration
- Structured context for LLMs
- Tool use by AI agents
- AI-native applications
- **Example**: Claude analyzing Compass data

### 1.8 Advantages & Disadvantages of MCP

#### Advantages

1. **Standardization**
   - Single protocol for all AI integrations
   - Reduces integration effort
   - Ecosystem benefits

2. **AI-Optimized**
   - Designed specifically for LLM use cases
   - Structured context format
   - Tool use primitives

3. **Security**
   - Resource-level permissions
   - Audit trails
   - Scoped access

4. **Discovery**
   - Self-describing servers
   - Automatic capability detection
   - No manual documentation parsing

5. **Bidirectional**
   - Server can request LLM assistance
   - Collaborative AI patterns
   - Rich interactions

#### Disadvantages

1. **Nascent Ecosystem**
   - Still new (Nov 2024 launch)
   - Limited tooling
   - Fewer examples

2. **Complexity**
   - More complex than REST
   - Learning curve
   - Infrastructure requirements

3. **Performance**
   - JSON-RPC overhead
   - Not optimized for bulk data
   - Streaming limitations

4. **Adoption**
   - Not widely adopted yet
   - Requires client support (Claude, etc.)
   - Limited to AI use cases

5. **Transport Limitations**
   - stdio not suitable for web
   - SSE one-way
   - WebSocket support limited

### 1.9 Performance Implications

#### Latency Comparison

```
REST API:
┌────────┬────────┬────────┬────────┐
│ DNS    │ TCP    │ TLS    │ HTTP   │
│ 10ms   │ 20ms   │ 50ms   │ 100ms  │
└────────┴────────┴────────┴────────┘
Total: ~180ms per request

MCP (stdio):
┌────────┐
│ IPC    │
│ 1-5ms  │
└────────┘
Total: ~5ms per request

MCP (SSE):
┌────────┬────────┬────────┬────────┬────────┐
│ DNS    │ TCP    │ TLS    │ HTTP   │ SSE    │
│ 10ms   │ 20ms   │ 50ms   │ 100ms  │ 50ms   │
└────────┴────────┴────────┴────────┴────────┘
Total: ~230ms initial, ~50ms streaming
```

#### Throughput

- REST: 1000-10000 req/sec (depends on endpoint)
- GraphQL: 500-5000 req/sec (more complex queries)
- WebSocket: 10000+ messages/sec
- MCP (stdio): 1000+ requests/sec
- MCP (SSE): 100-1000 events/sec

#### Use Case Fit

**MCP is BEST for**:
- AI agents reading structured data
- Tool use by LLMs
- Context-heavy operations
- Long-running AI tasks

**MCP is WORST for**:
- High-frequency updates
- Bulk data transfer
- Simple CRUD operations
- Traditional web/mobile apps

---

## Part II: Modern Connector Patterns

### 2.1 Webhook Architecture

#### What are Webhooks?

**Webhooks** are HTTP callbacks that notify your application when events occur in external systems.

```
┌──────────────┐        Event Occurs        ┌──────────────┐
│   External   │─────────────────────────►│   Your App   │
│   System     │   POST /webhook/callback   │   (Compass)  │
│   (Slack)    │                            │              │
└──────────────┘                            └──────────────┘
```

#### Compass Webhook Implementation

**File**: `/home/wsl-user/compass/backend/webhooks.py`

**Current Features**:
- HMAC-SHA256 signature verification
- Retry logic with exponential backoff (1s, 5s, 15s)
- Dead letter queue for failed deliveries
- Event history and logs
- Multiple event subscriptions

**Supported Events**:
- `feedback.created`
- `cluster.created`
- `roadmap.updated`
- `priority.changed`

#### Best Practices for Webhook Receivers

1. **Signature Verification**
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

2. **Idempotency**
```python
# Store event IDs to prevent duplicate processing
processed_events = set()

def handle_webhook(event_id: str, data: dict):
    if event_id in processed_events:
        return {"status": "already_processed"}

    # Process event
    process_event(data)

    # Mark as processed
    processed_events.add(event_id)
    return {"status": "processed"}
```

3. **Quick Response**
```python
@app.post("/webhook/slack")
async def receive_slack_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive webhook, respond quickly, process in background"""

    # 1. Verify signature immediately
    if not verify_signature(request):
        raise HTTPException(401, "Invalid signature")

    # 2. Return 200 OK immediately
    payload = await request.json()
    event_id = payload.get("event_id")

    # 3. Queue for background processing
    background_tasks.add_task(process_webhook, payload)

    return {"status": "accepted", "event_id": event_id}
```

4. **Retry Logic**
```python
async def send_webhook_with_retry(url: str, payload: dict, max_retries: int = 3):
    """Send webhook with exponential backoff"""
    delays = [1, 5, 15]  # seconds

    for attempt in range(max_retries):
        try:
            response = await httpx.post(url, json=payload, timeout=10)
            if 200 <= response.status_code < 300:
                return response
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(delays[attempt])
            else:
                raise
```

#### Queue-Based Processing

**With Celery (Python)**:
```python
from celery import Celery

app = Celery('compass', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3)
def process_webhook(self, payload: dict):
    """Process webhook asynchronously"""
    try:
        # Process the webhook
        result = handle_webhook_data(payload)
        return result
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
```

**With BullMQ (Node.js)**:
```typescript
import { Queue, Worker } from 'bullmq';

const webhookQueue = new Queue('webhooks', {
  connection: { host: 'localhost', port: 6379 }
});

// Add webhook to queue
await webhookQueue.add('process', payload, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 }
});

// Process webhooks
new Worker('webhooks', async job => {
  await handleWebhook(job.data);
}, { connection: { host: 'localhost', port: 6379 } });
```

### 2.2 Real-Time Streaming

#### Server-Sent Events (SSE)

**What is SSE?**
- One-way streaming from server to client
- Built on HTTP
- Auto-reconnection
- Text-based format

**Compass SSE Implementation**:
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.get("/api/events/stream")
async def stream_events():
    """Stream events to clients via SSE"""

    async def event_generator():
        while True:
            # Wait for new events
            event = await event_queue.get()

            # Format as SSE
            yield f"event: {event['type']}\n"
            yield f"data: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
```

**Client Usage**:
```javascript
const eventSource = new EventSource('/api/events/stream');

eventSource.addEventListener('feedback.created', (event) => {
  const data = JSON.parse(event.data);
  console.log('New feedback:', data);
});
```

#### WebSocket (Compass Implementation)

**File**: `/home/wsl-user/compass/backend/websockets.py`

**Current Features**:
- Bidirectional communication
- Room-based subscriptions
- Message queuing with rate limiting
- Heartbeat for connection health
- Automatic reconnection

**Architecture**:
```
Client                          Server
  │                               │
  ├─── Connect ──────────────────►│
  │                               │
  │◄────── connection.established─┤
  │                               │
  ├─── subscribe(["feedback"]) ──►│
  │                               │
  │◄────── rooms.subscribed ──────┤
  │                               │
  │                               │
  │◄────── feedback.created ──────┤ (event in room)
  │                               │
  │◄────── heartbeat ─────────────┤ (every 30s)
  │                               │
  ├─── pong ─────────────────────►│
```

#### gRPC Streaming

**What is gRPC?**
- High-performance RPC framework
- Protocol Buffers (binary format)
- Bidirectional streaming
- Language-agnostic

**Example: Feedback Stream**:
```protobuf
// feedback.proto
syntax = "proto3";

service FeedbackService {
  // Server streaming
  rpc StreamFeedback(StreamRequest) returns (stream Feedback);

  // Bidirectional streaming
  rpc BiStreamFeedback(stream FeedbackRequest) returns (stream Feedback);
}

message Feedback {
  int32 id = 1;
  string text = 2;
  string source = 3;
  float sentiment = 4;
}
```

#### When to Use Each

| Feature | SSE | WebSocket | gRPC |
|---------|-----|-----------|------|
| **Direction** | Server→Client | Bidirectional | Bidirectional |
| **Protocol** | HTTP | WebSocket | HTTP/2 |
| **Format** | Text | Text/Binary | Binary (Protobuf) |
| **Reconnect** | Auto | Manual | Auto |
| **Firewall** | Easy | Hard | Easy |
| **Overhead** | Low | Medium | Low |
| **Browser** | Native | Native | Requires proxy |
| **Use Case** | Notifications | Chat, gaming | Microservices |

**For Compass**:
- **SSE**: Dashboard updates, notifications
- **WebSocket**: Real-time collaboration, chat
- **gRPC**: Backend-to-backend (if microservices)

### 2.3 OAuth 2.0 Flows

#### OAuth 2.0 Flow Types

1. **Authorization Code Flow** (Most Secure)
   - For web apps with backend
   - Compass → Slack, GitHub, Google

2. **Client Credentials Flow**
   - For machine-to-machine
   - Compass backend → APIs

3. **Implicit Flow** (Deprecated)
   - Legacy, insecure
   - Don't use

4. **PKCE (Proof Key for Code Exchange)**
   - For mobile/SPA apps
   - Authorization Code + PKCE

#### Authorization Code Flow (Compass + Slack)

```
User                Browser              Compass Backend         Slack
 │                     │                       │                   │
 ├─ Click "Add Slack"─►│                       │                   │
 │                     │                       │                   │
 │                     ├─── GET /oauth/slack ─►│                   │
 │                     │                       │                   │
 │                     │◄──── Redirect ────────┤                   │
 │                     │  slack.com/oauth?     │                   │
 │                     │    client_id=xxx&     │                   │
 │                     │    redirect_uri=...   │                   │
 │                     │                       │                   │
 │                     ├───────────────────────┼─── Authorize ────►│
 │                     │                       │                   │
 │                     │◄──────────────────────┼──── code ─────────┤
 │                     │  yourapp.com/callback?│                   │
 │                     │    code=abc123        │                   │
 │                     │                       │                   │
 │                     ├─ GET /callback?code=..►│                   │
 │                     │                       │                   │
 │                     │                       ├─ Exchange code ───►│
 │                     │                       │   for token        │
 │                     │                       │                   │
 │                     │                       │◄── Access Token ───┤
 │                     │                       │    + Refresh Token │
 │                     │                       │                   │
 │                     │◄──── Success ─────────┤                   │
 │                     │                       │                   │
 │◄──── "Connected!" ──┤                       │                   │
```

#### Implementation Example

```python
from fastapi import FastAPI, HTTPException
from authlib.integrations.starlette_client import OAuth
import os

app = FastAPI()

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='slack',
    client_id=os.getenv('SLACK_CLIENT_ID'),
    client_secret=os.getenv('SLACK_CLIENT_SECRET'),
    authorize_url='https://slack.com/oauth/v2/authorize',
    access_token_url='https://slack.com/api/oauth.v2.access',
    client_kwargs={'scope': 'channels:read channels:history'}
)

@app.get('/oauth/slack')
async def oauth_slack(request: Request):
    """Initiate OAuth flow"""
    redirect_uri = request.url_for('oauth_callback')
    return await oauth.slack.authorize_redirect(request, redirect_uri)

@app.get('/oauth/callback')
async def oauth_callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.slack.authorize_access_token(request)

        # Save token to database
        await save_slack_credentials(
            access_token=token['access_token'],
            refresh_token=token.get('refresh_token'),
            expires_at=token.get('expires_at'),
            team_id=token['team']['id']
        )

        return {"status": "success", "team": token['team']['name']}

    except Exception as e:
        raise HTTPException(400, f"OAuth failed: {e}")
```

#### Token Refresh Pattern

```python
import time

async def get_valid_slack_token(team_id: str) -> str:
    """Get valid access token, refreshing if needed"""

    # Load from database
    creds = await load_slack_credentials(team_id)

    # Check if expired
    if time.time() >= creds['expires_at']:
        # Refresh token
        response = await httpx.post(
            'https://slack.com/api/oauth.v2.access',
            data={
                'grant_type': 'refresh_token',
                'client_id': SLACK_CLIENT_ID,
                'client_secret': SLACK_CLIENT_SECRET,
                'refresh_token': creds['refresh_token']
            }
        )

        new_token = response.json()

        # Update database
        await update_slack_credentials(
            team_id=team_id,
            access_token=new_token['access_token'],
            expires_at=time.time() + new_token['expires_in']
        )

        return new_token['access_token']

    return creds['access_token']
```

#### Multi-Tenant OAuth

```python
class OAuthManager:
    """Manage OAuth credentials for multiple tenants"""

    def __init__(self):
        self.credentials = {}  # In production: use database

    async def store_credentials(self, tenant_id: str, platform: str, token: dict):
        """Store OAuth credentials"""
        key = f"{tenant_id}:{platform}"
        self.credentials[key] = {
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token'),
            'expires_at': time.time() + token.get('expires_in', 3600),
            'scope': token.get('scope'),
            'created_at': time.time()
        }

    async def get_token(self, tenant_id: str, platform: str) -> str:
        """Get valid access token for tenant"""
        key = f"{tenant_id}:{platform}"

        if key not in self.credentials:
            raise ValueError(f"No credentials for {key}")

        creds = self.credentials[key]

        # Refresh if expired
        if time.time() >= creds['expires_at']:
            creds = await self._refresh_token(tenant_id, platform, creds)

        return creds['access_token']
```

### 2.4 Connector Frameworks

#### Airbyte Architecture

**What is Airbyte?**
- Open-source data integration platform
- 300+ connectors
- ELT (Extract, Load, Transform)

**Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                      Airbyte                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐      ┌───────────┐      ┌──────────┐     │
│  │  Source  │─────►│  Airbyte  │─────►│  Dest    │     │
│  │ Connector│      │   Core    │      │ Connector│     │
│  └──────────┘      └───────────┘      └──────────┘     │
│                                                           │
│  Standard Protocol                                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ AirbyteMessage {                                  │  │
│  │   type: "RECORD" | "STATE" | "LOG" | "SPEC"      │  │
│  │   record: {...}                                   │  │
│  │   state: {...}                                    │  │
│  │ }                                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Concepts**:
1. **Source Connector**: Reads from data source
2. **Destination Connector**: Writes to target
3. **Catalog**: Schema discovery
4. **State**: Incremental sync tracking
5. **Protocol**: Standard message format

**How It Works**:
```python
# Airbyte Source Connector (simplified)
class SlackSourceConnector:
    def check(self, config: dict) -> bool:
        """Test connection"""
        return test_slack_connection(config['token'])

    def discover(self, config: dict) -> Catalog:
        """Discover available streams"""
        return Catalog(streams=[
            Stream(name="messages", schema=MESSAGE_SCHEMA),
            Stream(name="users", schema=USER_SCHEMA),
        ])

    def read(self, config: dict, catalog: Catalog, state: dict):
        """Read data from Slack"""
        for stream in catalog.streams:
            if stream.name == "messages":
                for message in fetch_slack_messages(config, state):
                    yield AirbyteMessage(
                        type="RECORD",
                        record={"stream": "messages", "data": message}
                    )
```

#### Fivetran Architecture

**What is Fivetran?**
- Managed ELT platform
- 300+ connectors
- Automatic schema drift handling

**Architecture**:
```
┌────────────────────────────────────────┐
│           Fivetran Cloud               │
├────────────────────────────────────────┤
│                                        │
│  Source → Fivetran → Warehouse        │
│   API       |         (Snowflake,     │
│             |          BigQuery, etc) │
│             ▼                          │
│     ┌──────────────┐                  │
│     │ CDC Engine   │ (Change Data     │
│     │ Schema Drift │  Capture)        │
│     │ Transform    │                  │
│     └──────────────┘                  │
│                                        │
└────────────────────────────────────────┘
```

**Key Concepts**:
1. **Change Data Capture**: Incremental updates
2. **Schema Drift**: Auto-detect schema changes
3. **Transformations**: dbt integration
4. **Monitoring**: Data quality checks

#### Segment Architecture

**What is Segment?**
- Customer data platform (CDP)
- Event collection & routing
- 300+ integrations

**Architecture**:
```
┌───────────────────────────────────────────────────────┐
│                    Segment                            │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Sources          Segment           Destinations     │
│  ┌────────┐       ┌──────┐         ┌────────┐       │
│  │  Web   │──────►│Queue │────────►│ Mixpanel│      │
│  │ Mobile │       │+ETL  │         │ Amplitude│      │
│  │ Server │       │+Rules│         │ Snowflake│      │
│  └────────┘       └──────┘         └────────┘       │
│                                                       │
│  Standard Event Format:                              │
│  {                                                    │
│    "userId": "123",                                   │
│    "event": "Button Clicked",                        │
│    "properties": {...},                              │
│    "timestamp": "2026-08-04T10:00:00Z"               │
│  }                                                    │
└───────────────────────────────────────────────────────┘
```

**Key Concepts**:
1. **Track**: Events (user actions)
2. **Identify**: User properties
3. **Page**: Page views
4. **Group**: Company/org properties

#### Lessons for Compass

1. **Standard Protocol** (from Airbyte)
   - Define standard format for all sources
   - Version protocol
   - Self-describing connectors

2. **Change Data Capture** (from Fivetran)
   - Track incremental changes
   - Efficient syncing
   - Reduce API calls

3. **Event-Driven** (from Segment)
   - Real-time event processing
   - Queue-based architecture
   - Replay capabilities

### 2.5 Rate Limiting & Quotas

#### Common Rate Limits (2026)

| Platform | Rate Limit | Type |
|----------|------------|------|
| GitHub API | 5,000 req/hr | Token-based |
| Slack API | 1 req/sec per method | Per-method |
| Discord API | 50 req/sec | Global + per-route |
| Reddit API | 60 req/min | OAuth app |
| Twitter API | 300 req/15min | User context |
| Linear API | 2,000 req/hr | Workspace |

#### Rate Limiting Strategies

**1. Token Bucket Algorithm**
```python
import time
from collections import deque

class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens"""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on refill rate
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now
```

**2. Sliding Window**
```python
from collections import deque
import time

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()

    def allow_request(self) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()

        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False
```

**3. Exponential Backoff**
```python
import asyncio
import random

async def fetch_with_backoff(url: str, max_retries: int = 5):
    """Fetch with exponential backoff"""

    for attempt in range(max_retries):
        try:
            response = await httpx.get(url)

            if response.status_code == 200:
                return response

            if response.status_code == 429:  # Rate limited
                # Calculate backoff delay
                retry_after = int(response.headers.get('Retry-After', 0))
                if retry_after:
                    delay = retry_after
                else:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)

                print(f"Rate limited. Waiting {delay}s...")
                await asyncio.sleep(delay)
                continue

            # Other error
            raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

#### Queue Management

**Redis-Based Queue**:
```python
import redis
import json

class RedisRateLimitQueue:
    """Rate-limited queue using Redis"""

    def __init__(self, redis_client: redis.Redis, rate_limit: int):
        self.redis = redis_client
        self.rate_limit = rate_limit
        self.queue_key = "api_queue"
        self.rate_key = "api_rate"

    def enqueue(self, task: dict):
        """Add task to queue"""
        self.redis.rpush(self.queue_key, json.dumps(task))

    async def process_queue(self):
        """Process queue with rate limiting"""
        while True:
            # Check rate limit (sliding window in Redis)
            current_count = self.redis.incr(self.rate_key)

            if current_count == 1:
                # Set expiry on first request
                self.redis.expire(self.rate_key, 60)  # 1 minute window

            if current_count > self.rate_limit:
                # Wait until window resets
                ttl = self.redis.ttl(self.rate_key)
                await asyncio.sleep(ttl)
                continue

            # Dequeue and process
            task_json = self.redis.lpop(self.queue_key)
            if task_json:
                task = json.loads(task_json)
                await process_task(task)
            else:
                await asyncio.sleep(0.1)
```

#### Parallel Processing with Rate Limits

```python
import asyncio
from asyncio import Semaphore

class RateLimitedClient:
    """HTTP client with rate limiting"""

    def __init__(self, rate_limit: int, window_seconds: int = 60):
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.semaphore = Semaphore(rate_limit)
        self.requests = []

    async def fetch(self, url: str):
        """Fetch with rate limiting"""

        # Wait for available slot
        async with self.semaphore:
            # Clean old requests
            now = asyncio.get_event_loop().time()
            self.requests = [t for t in self.requests if t > now - self.window_seconds]

            # Wait if at limit
            if len(self.requests) >= self.rate_limit:
                wait_time = self.requests[0] + self.window_seconds - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            # Make request
            self.requests.append(now)
            return await httpx.get(url)

# Usage: parallel fetching with rate limit
client = RateLimitedClient(rate_limit=100, window_seconds=60)

async def fetch_all(urls: list):
    tasks = [client.fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 2.6 Data Sync Strategies

#### Full Sync vs Incremental Sync

**Full Sync**:
```python
async def full_sync(source: FeedbackSource):
    """Fetch all data from source"""

    # Fetch all feedback
    all_feedback = await source.fetch_feedback()

    # Clear existing data
    await db.execute("DELETE FROM feedback WHERE source_id = ?", source.id)

    # Insert all feedback
    for feedback in all_feedback:
        await db.execute("INSERT INTO feedback (...) VALUES (...)", feedback)

    return len(all_feedback)
```

**Incremental Sync (Compass Approach)**:
```python
async def incremental_sync(source: FeedbackSource):
    """Fetch only new data since last sync"""

    # Get last sync timestamp
    last_synced = await db.fetchval(
        "SELECT last_synced_at FROM sources WHERE id = ?",
        source.id
    )

    # Fetch new feedback only
    new_feedback = await source.fetch_feedback(since=last_synced)

    # Insert new feedback (with deduplication)
    for feedback in new_feedback:
        await db.execute("""
            INSERT INTO feedback (...)
            VALUES (...)
            ON CONFLICT (external_id) DO UPDATE SET ...
        """, feedback)

    # Update last_synced timestamp
    await db.execute(
        "UPDATE sources SET last_synced_at = ? WHERE id = ?",
        datetime.utcnow(), source.id
    )

    return len(new_feedback)
```

#### Change Data Capture (CDC)

**Database CDC (PostgreSQL)**:
```python
# Using PostgreSQL logical replication

# 1. Enable logical replication
# ALTER SYSTEM SET wal_level = logical;

# 2. Create publication
# CREATE PUBLICATION feedback_changes FOR TABLE feedback;

# 3. Listen for changes
import asyncpg

async def listen_for_changes():
    """Listen for database changes"""
    conn = await asyncpg.connect('postgresql://...')

    # Subscribe to changes
    await conn.add_listener('feedback_changes', handle_change)

    # Keep connection alive
    await asyncio.Future()

def handle_change(conn, pid, channel, payload):
    """Handle database change event"""
    change = json.loads(payload)

    if change['action'] == 'INSERT':
        # New feedback
        emit_event('feedback.created', change['data'])
    elif change['action'] == 'UPDATE':
        # Updated feedback
        emit_event('feedback.updated', change['data'])
```

**API-Based CDC (Webhooks)**:
```python
# External system sends us changes via webhook

@app.post("/webhook/slack/events")
async def slack_webhook(event: dict):
    """Receive Slack events (CDC)"""

    if event['type'] == 'message':
        # New message = new feedback
        feedback = await create_feedback_from_slack_message(event)
        await emit_event('feedback.created', feedback)

    elif event['type'] == 'message_changed':
        # Updated message = updated feedback
        feedback = await update_feedback_from_slack_message(event)
        await emit_event('feedback.updated', feedback)

    return {"status": "ok"}
```

#### Cursor-Based Pagination

```python
async def fetch_with_cursor(api_url: str, page_size: int = 100):
    """Fetch all data using cursor-based pagination"""

    all_results = []
    cursor = None

    while True:
        # Fetch page
        params = {'limit': page_size}
        if cursor:
            params['cursor'] = cursor

        response = await httpx.get(api_url, params=params)
        data = response.json()

        # Collect results
        all_results.extend(data['results'])

        # Check for more pages
        if not data.get('has_more'):
            break

        cursor = data['next_cursor']

    return all_results
```

#### Timestamp-Based Sync

```python
async def sync_since_timestamp(source: str, since: datetime):
    """Sync data modified since timestamp"""

    # Fetch data modified since timestamp
    params = {
        'modified_since': since.isoformat(),
        'sort': 'modified_asc'
    }

    response = await httpx.get(f"{API_URL}/{source}", params=params)
    items = response.json()

    # Process items
    for item in items:
        # Check if exists
        existing = await db.fetchone(
            "SELECT id, modified_at FROM items WHERE external_id = ?",
            item['id']
        )

        if existing:
            # Update if newer
            if item['modified_at'] > existing['modified_at']:
                await db.execute("UPDATE items SET ... WHERE id = ?", existing['id'])
        else:
            # Insert new
            await db.execute("INSERT INTO items (...) VALUES (...)")

    return len(items)
```

### 2.7 Error Handling

#### Retry Strategies

**Exponential Backoff** (already covered in 2.5)

**Circuit Breaker Pattern**:
```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, don't try
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for API calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""

        if self.state == CircuitState.OPEN:
            # Check if should try again
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            # Success - reset if in half-open state
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise

# Usage
slack_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

async def fetch_slack_messages():
    return await slack_breaker.call(slack_api.get_messages)
```

#### Dead Letter Queues

```python
class DeadLetterQueue:
    """Handle failed messages"""

    def __init__(self):
        self.failed_messages = []

    async def process_with_dlq(self, message: dict, handler):
        """Process message with DLQ fallback"""

        max_retries = 3

        for attempt in range(max_retries):
            try:
                result = await handler(message)
                return result

            except Exception as e:
                if attempt < max_retries - 1:
                    # Retry
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Max retries reached - send to DLQ
                    await self.send_to_dlq(message, e)
                    raise

    async def send_to_dlq(self, message: dict, error: Exception):
        """Send failed message to dead letter queue"""

        dlq_entry = {
            'message': message,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'attempts': 3
        }

        # Store in database
        await db.execute("""
            INSERT INTO dead_letter_queue (message, error, timestamp)
            VALUES (?, ?, ?)
        """, json.dumps(message), str(error), datetime.utcnow())

        # Alert admins
        await send_alert(f"Message failed after 3 retries: {error}")

    async def replay_dlq(self, message_id: int):
        """Replay failed message"""

        # Get from DLQ
        message = await db.fetchone(
            "SELECT * FROM dead_letter_queue WHERE id = ?",
            message_id
        )

        # Try processing again
        try:
            await process_message(json.loads(message['message']))

            # Success - remove from DLQ
            await db.execute(
                "DELETE FROM dead_letter_queue WHERE id = ?",
                message_id
            )
        except Exception as e:
            # Still failing
            raise
```

#### Monitoring and Alerting

```python
from datetime import datetime, timedelta

class IntegrationMonitor:
    """Monitor integration health"""

    def __init__(self):
        self.metrics = {
            'requests': 0,
            'errors': 0,
            'latencies': []
        }

    async def track_request(self, source: str, func, *args, **kwargs):
        """Track request metrics"""

        start = time.time()

        try:
            result = await func(*args, **kwargs)

            # Track success
            self.metrics['requests'] += 1
            latency = time.time() - start
            self.metrics['latencies'].append(latency)

            # Log slow requests
            if latency > 5.0:
                print(f"⚠️ Slow request: {source} took {latency:.2f}s")

            return result

        except Exception as e:
            # Track error
            self.metrics['errors'] += 1

            # Alert on high error rate
            error_rate = self.metrics['errors'] / max(self.metrics['requests'], 1)
            if error_rate > 0.1:  # 10% error rate
                await send_alert(f"High error rate for {source}: {error_rate:.1%}")

            raise

    def get_stats(self) -> dict:
        """Get monitoring stats"""
        return {
            'total_requests': self.metrics['requests'],
            'total_errors': self.metrics['errors'],
            'error_rate': self.metrics['errors'] / max(self.metrics['requests'], 1),
            'avg_latency': sum(self.metrics['latencies']) / len(self.metrics['latencies']) if self.metrics['latencies'] else 0,
            'p95_latency': self._percentile(self.metrics['latencies'], 0.95),
            'p99_latency': self._percentile(self.metrics['latencies'], 0.99)
        }

    def _percentile(self, data: list, percentile: float) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
```

#### User-Facing Error Messages

```python
class UserFriendlyError(Exception):
    """Exception with user-friendly message"""

    def __init__(self, technical_message: str, user_message: str):
        self.technical_message = technical_message
        self.user_message = user_message
        super().__init__(technical_message)

# API error handler
@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    """Handle errors with user-friendly messages"""

    # Log technical details
    logger.error(f"Error: {exc}", exc_info=True)

    # Return user-friendly message
    if isinstance(exc, UserFriendlyError):
        message = exc.user_message
    elif isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 401:
            message = "Authentication failed. Please check your credentials."
        elif exc.response.status_code == 403:
            message = "Access denied. Please check your permissions."
        elif exc.response.status_code == 429:
            message = "Rate limit exceeded. Please try again later."
        else:
            message = f"API error: {exc.response.status_code}"
    else:
        message = "An unexpected error occurred. Please try again."

    return JSONResponse(
        status_code=500,
        content={
            "error": message,
            "error_id": str(uuid.uuid4())  # For support tracking
        }
    )
```

---

## Part III: Competitive Connector Platforms

### 3.1 Zapier Technical Details

#### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Zapier                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Trigger App       Zapier Engine       Action App  │
│  ┌──────────┐     ┌──────────┐       ┌──────────┐ │
│  │  Gmail   │────►│  Filter  │──────►│  Slack   │ │
│  │ (Trigger)│     │Transform │       │ (Action) │ │
│  └──────────┘     │  Delay   │       └──────────┘ │
│                   └──────────┘                     │
│                                                     │
│  Types of Triggers:                                │
│  - Polling (check every 5-15 minutes)              │
│  - Instant (webhooks)                              │
│  - Schedule (cron-like)                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### How Zapier Integrations Work

**Trigger Types**:

1. **Polling Trigger** (most common):
```javascript
// Zapier checks API periodically
module.exports = {
  key: 'new_feedback',
  noun: 'Feedback',
  display: {
    label: 'New Feedback',
    description: 'Triggers when new feedback is created.'
  },

  operation: {
    // How often to poll (seconds)
    polling: {
      interval: 300  // 5 minutes
    },

    // Fetch recent items
    perform: async (z, bundle) => {
      const response = await z.request({
        url: 'https://compass-api.com/feedback',
        params: {
          since: bundle.meta.lastPoll  // Only fetch new items
        }
      });

      return response.json;  // Array of feedback items
    },

    // Dedupe based on ID
    deduplicationKey: 'id'
  }
};
```

2. **Instant Trigger** (webhook-based):
```javascript
module.exports = {
  key: 'new_feedback_instant',
  noun: 'Feedback',
  display: {
    label: 'New Feedback (Instant)',
    description: 'Instant trigger via webhook.'
  },

  operation: {
    type: 'hook',

    // Called when user enables Zap
    performSubscribe: async (z, bundle) => {
      const response = await z.request({
        url: 'https://compass-api.com/webhooks',
        method: 'POST',
        body: {
          url: bundle.targetUrl,  // Zapier webhook URL
          event: 'feedback.created'
        }
      });

      return response.json;  // {id: webhook_id}
    },

    // Called when user disables Zap
    performUnsubscribe: async (z, bundle) => {
      await z.request({
        url: `https://compass-api.com/webhooks/${bundle.subscribeData.id}`,
        method: 'DELETE'
      });
    },

    // Process webhook payload
    perform: (z, bundle) => {
      return [bundle.cleanedRequest];  // Return webhook data
    }
  }
};
```

**Action Implementation**:
```javascript
module.exports = {
  key: 'create_feedback',
  noun: 'Feedback',
  display: {
    label: 'Create Feedback',
    description: 'Creates a new feedback entry.'
  },

  operation: {
    // Input fields
    inputFields: [
      {
        key: 'text',
        label: 'Feedback Text',
        type: 'text',
        required: true
      },
      {
        key: 'source',
        label: 'Source',
        type: 'string',
        required: true,
        choices: ['email', 'slack', 'github']
      },
      {
        key: 'sentiment',
        label: 'Sentiment',
        type: 'number',
        required: false
      }
    ],

    // Execute action
    perform: async (z, bundle) => {
      const response = await z.request({
        url: 'https://compass-api.com/feedback',
        method: 'POST',
        body: {
          text: bundle.inputData.text,
          source: bundle.inputData.source,
          sentiment: bundle.inputData.sentiment
        }
      });

      return response.json;  // Created feedback object
    }
  }
};
```

#### Authentication
```javascript
module.exports = {
  type: 'custom',

  fields: [
    {
      key: 'api_key',
      label: 'API Key',
      required: true,
      type: 'string'
    }
  ],

  // Test authentication
  test: async (z, bundle) => {
    const response = await z.request({
      url: 'https://compass-api.com/auth/test',
      headers: {
        'Authorization': `Bearer ${bundle.authData.api_key}`
      }
    });

    return response.json;
  },

  // Add auth to all requests
  connectionLabel: (z, bundle) => {
    return bundle.inputData.email;  // Display in UI
  }
};
```

### 3.2 Make (Integromat) Technical Details

#### Visual Flow Builder

```
┌──────────────────────────────────────────────────┐
│               Make Scenario                      │
├──────────────────────────────────────────────────┤
│                                                  │
│   [Webhook] ──► [Filter] ──► [Router] ──┬──► [Slack]   │
│                                          │              │
│                                          └──► [Email]   │
│                                                  │
│   Features:                                      │
│   - Visual node editor                           │
│   - Data mapping (drag & drop)                   │
│   - Advanced routing                             │
│   - Error handling                               │
│   - Scheduling                                   │
│                                                  │
└──────────────────────────────────────────────────┘
```

#### Module Definition (Make's version of connector)

```json
{
  "name": "compass",
  "label": "Compass Feedback",
  "description": "AI-powered feedback management",

  "connection": {
    "type": "apiKey",
    "label": "API Key",
    "help": "Get your API key from Compass settings"
  },

  "triggers": [
    {
      "name": "watchFeedback",
      "label": "Watch Feedback",
      "type": "webhook",
      "hookUrl": "https://compass-api.com/webhooks/make",

      "communication": {
        "url": "/feedback",
        "method": "GET",
        "qs": {
          "since": "{{parameters.timestamp}}"
        },
        "response": {
          "iterate": "{{body}}",
          "output": {
            "id": "{{item.id}}",
            "text": "{{item.text}}",
            "source": "{{item.source}}",
            "sentiment": "{{item.sentiment}}",
            "created_at": "{{item.created_at}}"
          }
        }
      }
    }
  ],

  "actions": [
    {
      "name": "createFeedback",
      "label": "Create Feedback",

      "parameters": [
        {
          "name": "text",
          "type": "text",
          "label": "Feedback Text",
          "required": true
        },
        {
          "name": "source",
          "type": "select",
          "label": "Source",
          "options": ["email", "slack", "github"]
        }
      ],

      "communication": {
        "url": "/feedback",
        "method": "POST",
        "body": {
          "text": "{{parameters.text}}",
          "source": "{{parameters.source}}"
        },
        "response": {
          "output": {
            "id": "{{body.id}}",
            "status": "{{body.status}}"
          }
        }
      }
    }
  ]
}
```

### 3.3 n8n (Open Source) Technical Details

#### Node-Based Workflow

```
┌─────────────────────────────────────────────┐
│              n8n Workflow                   │
├─────────────────────────────────────────────┤
│                                             │
│  [Trigger]     [Process]      [Action]     │
│     │             │              │          │
│  Webhook ──► Transform ──► HTTP Request    │
│              │                              │
│           [Code Node]                       │
│           (Custom JS)                       │
│                                             │
│  Features:                                  │
│  - Self-hosted                              │
│  - Custom code nodes                        │
│  - Fair-code license                        │
│  - 200+ integrations                        │
│                                             │
└─────────────────────────────────────────────┘
```

#### Custom Node Development

```typescript
// Compass.node.ts
import { INodeType, INodeTypeDescription } from 'n8n-workflow';

export class Compass implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Compass',
    name: 'compass',
    group: ['transform'],
    version: 1,
    description: 'Interact with Compass API',

    defaults: {
      name: 'Compass',
    },

    inputs: ['main'],
    outputs: ['main'],

    credentials: [
      {
        name: 'compassApi',
        required: true,
      },
    ],

    properties: [
      {
        displayName: 'Resource',
        name: 'resource',
        type: 'options',
        options: [
          {
            name: 'Feedback',
            value: 'feedback',
          },
          {
            name: 'Cluster',
            value: 'cluster',
          },
        ],
        default: 'feedback',
      },
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        displayOptions: {
          show: {
            resource: ['feedback'],
          },
        },
        options: [
          {
            name: 'Create',
            value: 'create',
          },
          {
            name: 'Get All',
            value: 'getAll',
          },
        ],
        default: 'create',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: IDataObject[] = [];

    const resource = this.getNodeParameter('resource', 0) as string;
    const operation = this.getNodeParameter('operation', 0) as string;

    if (resource === 'feedback') {
      if (operation === 'create') {
        for (let i = 0; i < items.length; i++) {
          const text = this.getNodeParameter('text', i) as string;
          const source = this.getNodeParameter('source', i) as string;

          const response = await this.helpers.request({
            method: 'POST',
            url: 'https://compass-api.com/feedback',
            body: { text, source },
            json: true,
          });

          returnData.push(response);
        }
      }
    }

    return [this.helpers.returnJsonArray(returnData)];
  }
}
```

---

## Part IV: MCP for Compass

### 4.1 Could Compass Use MCP?

#### Yes! Multiple Use Cases

**1. AI-Powered Feedback Analysis**
```
User: "Claude, analyze my Compass feedback"

Claude ──► MCP Client ──► Compass MCP Server
                            │
                            ├─ Resources:
                            │  ├─ compass://feedback
                            │  ├─ compass://clusters
                            │  └─ compass://roadmap
                            │
                            └─ Tools:
                               ├─ analyze_sentiment()
                               ├─ create_cluster()
                               └─ prioritize_feedback()
```

**2. Conversational Roadmap Generation**
```
User: "Generate a roadmap focusing on mobile app features"

Claude:
1. Reads compass://feedback (via MCP)
2. Filters by keywords ("mobile", "app", "iOS", "Android")
3. Calls create_cluster("mobile_features")
4. Calls prioritize_feedback()
5. Generates roadmap summary
```

**3. Cross-Platform Insights**
```
User: "Compare sentiment across Slack vs GitHub feedback"

Claude:
1. Reads compass://feedback?source=slack
2. Reads compass://feedback?source=github
3. Calls analyze_sentiment() for each
4. Generates comparison report
```

### 4.2 How Would MCP Help Compass Integrations?

#### Benefits for Compass

**1. AI-Native Positioning**
- Market as "AI-ready" platform
- Natural Claude integration
- Competitive advantage vs Productboard, Canny, etc.

**2. Natural Language Queries**
```
Without MCP:
User → Dashboard → Filters → Search → Export → Analyze

With MCP:
User → "Claude, what are the top 5 requests from enterprise customers?"
Claude → Queries Compass via MCP → Returns answer
```

**3. Automated Insights**
```python
# Claude can automatically analyze feedback daily

# Morning report:
"Good morning! Here's your Compass summary:
- 23 new feedback items (↑12% vs yesterday)
- Top request: 'Dark mode' (12 mentions, avg sentiment 0.8)
- Urgent cluster: 'Payment bugs' (5 items, all negative)
- Recommended priority change: Move 'API rate limits' to High"
```

**4. Intelligent Integrations**
```
# Claude can orchestrate multi-platform workflows

User: "When someone requests a feature on Slack, create a cluster if similar requests exist"

Claude (via MCP):
1. Watches Slack for keywords
2. Queries Compass for similar feedback
3. Creates/updates cluster
4. Notifies team
```

### 4.3 Example: MCP Server for Slack Feedback

#### Compass Slack MCP Server

```python
from mcp.server import Server
from mcp.types import Resource, Tool
import httpx

# Create MCP server
server = Server("compass-slack-mcp")

# Resources
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="compass://slack/channels",
            name="Slack Channels",
            mimeType="application/json",
            description="All connected Slack channels"
        ),
        Resource(
            uri="compass://slack/messages",
            name="Slack Messages",
            mimeType="application/json",
            description="Recent Slack messages (potential feedback)"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "compass://slack/channels":
        channels = await get_slack_channels()
        return json.dumps(channels)

    if uri == "compass://slack/messages":
        messages = await get_recent_slack_messages()
        return json.dumps(messages)

    raise ValueError(f"Unknown resource: {uri}")

# Tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="import_slack_feedback",
            description="Import Slack message as feedback",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "channel_id": {"type": "string"},
                    "category": {"type": "string", "enum": ["feature_request", "bug", "question"]}
                },
                "required": ["message_id", "channel_id"]
            }
        ),
        Tool(
            name="analyze_slack_sentiment",
            description="Analyze sentiment of Slack messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "since": {"type": "string", "format": "date-time"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "import_slack_feedback":
        # Get message
        message = await get_slack_message(
            arguments['channel_id'],
            arguments['message_id']
        )

        # Create feedback in Compass
        feedback = await create_feedback({
            'text': message['text'],
            'source': 'slack',
            'external_id': message['id'],
            'metadata': {
                'channel': message['channel'],
                'user': message['user'],
                'timestamp': message['timestamp']
            }
        })

        return json.dumps({
            "status": "imported",
            "feedback_id": feedback['id']
        })

    if name == "analyze_slack_sentiment":
        messages = await get_slack_messages(
            arguments['channel_id'],
            since=arguments.get('since')
        )

        sentiments = []
        for msg in messages:
            sentiment = await analyze_sentiment(msg['text'])
            sentiments.append({
                'message_id': msg['id'],
                'sentiment': sentiment,
                'text': msg['text'][:100]
            })

        return json.dumps({
            "messages_analyzed": len(sentiments),
            "average_sentiment": sum(s['sentiment'] for s in sentiments) / len(sentiments),
            "sentiments": sentiments
        })

# Run server
if __name__ == "__main__":
    server.run()
```

#### Usage Example

```
User: "Claude, import all feature requests from #feedback-channel"

Claude:
1. List resources: compass://slack/channels
2. Find #feedback-channel
3. Read resource: compass://slack/messages?channel=feedback
4. For each message with keywords:
   - Call tool: import_slack_feedback(message_id, channel_id, "feature_request")
5. Report: "Imported 12 feature requests from #feedback-channel"
```

### 4.4 Example: MCP Server for GitHub Issues

```python
server = Server("compass-github-mcp")

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="compass://github/repos",
            name="Connected Repositories"
        ),
        Resource(
            uri="compass://github/issues",
            name="GitHub Issues"
        )
    ]

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sync_github_issues",
            description="Sync GitHub issues to Compass",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}}
                }
            }
        ),
        Tool(
            name="create_github_issue_from_cluster",
            description="Create GitHub issue from feedback cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_id": {"type": "integer"},
                    "repo": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "create_github_issue_from_cluster":
        # Get cluster data
        cluster = await get_cluster(arguments['cluster_id'])

        # Create GitHub issue
        issue = await create_github_issue(
            repo=arguments['repo'],
            title=cluster['title'],
            body=f"""
            ## Feedback Cluster from Compass

            **Frequency**: {cluster['frequency']} requests
            **Priority Score**: {cluster['priority']}
            **Average Sentiment**: {cluster['avg_sentiment']}

            ### Representative Feedback:
            {cluster['representative_feedback']}

            ### All Related Feedback:
            {chr(10).join(f"- {f['text']}" for f in cluster['feedback'])}
            """,
            labels=["from-compass", "feature-request"]
        )

        return json.dumps({
            "status": "created",
            "issue_url": issue['html_url'],
            "issue_number": issue['number']
        })
```

---

## Part V: Architecture Recommendations

### 5.1 Short-Term: Current Architecture (Q3 2026)

#### Recommendation: Keep REST + WebSocket

**Why**:
- MCP still new (7 months old)
- Limited client support
- REST/WebSocket proven and battle-tested
- Existing integrations work well

**Current Stack**:
```
┌─────────────────────────────────────────────────────┐
│                  Compass Stack                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Frontend       Backend              Integrations  │
│  ┌────────┐    ┌──────────┐         ┌──────────┐  │
│  │ React  │───►│ FastAPI  │◄────────│  Slack   │  │
│  │        │    │ REST API │         │  GitHub  │  │
│  │        │    │          │         │  Discord │  │
│  └────────┘    └──────────┘         └──────────┘  │
│      │              │                               │
│      │              │                               │
│      └──WebSocket───┘                               │
│       (real-time)                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Continue Building**:
1. More REST API endpoints
2. Enhanced WebSocket events
3. More source integrations
4. Webhook improvements

### 5.2 Medium-Term: MCP Server (Q4 2026)

#### Recommendation: Build Compass MCP Server

**Why**:
- Position as AI-native platform
- Enable Claude integration
- Competitive advantage
- Low risk (additive, not replacement)

**Architecture**:
```
┌──────────────────────────────────────────────────────┐
│                  Compass (Q4 2026)                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────┐    ┌──────────┐    ┌─────────────┐ │
│  │   React    │───►│ FastAPI  │    │     MCP     │ │
│  │  Frontend  │    │ REST API │    │    Server   │ │
│  └────────────┘    └──────────┘    └─────────────┘ │
│        │                │                  ▲         │
│        │                │                  │         │
│        └────WebSocket───┘                  │         │
│                                            │         │
│                                      ┌─────┴─────┐   │
│                                      │   Claude  │   │
│                                      │    API    │   │
│                                      └───────────┘   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**MCP Server Features**:
- Resources: feedback, clusters, roadmap
- Tools: analyze, create, prioritize
- Prompts: common analysis templates
- Authentication: API key-based

**Implementation Plan**:
1. **Week 1-2**: MCP server basics
   - Setup Python MCP SDK
   - Implement resources (read-only)
   - Test with Claude Desktop

2. **Week 3-4**: Tools & prompts
   - Implement key tools
   - Add prompt templates
   - Documentation

3. **Week 5-6**: Polish & launch
   - Security review
   - Performance testing
   - Public announcement

### 5.3 Long-Term: Dual Protocol (2027)

#### Recommendation: REST + MCP Co-existence

**Architecture**:
```
┌───────────────────────────────────────────────────────┐
│              Compass (2027 Vision)                    │
├───────────────────────────────────────────────────────┤
│                                                       │
│             ┌───────────────┐                         │
│             │  Core Engine  │                         │
│             │  (Business    │                         │
│             │   Logic)      │                         │
│             └───────────────┘                         │
│                     │                                 │
│        ┌────────────┼────────────┐                    │
│        │                         │                    │
│   ┌────▼─────┐            ┌─────▼────┐               │
│   │   REST   │            │   MCP    │               │
│   │   API    │            │  Server  │               │
│   └────┬─────┘            └─────┬────┘               │
│        │                         │                    │
│   ┌────▼──────┐            ┌────▼─────┐              │
│   │  Web/     │            │  Claude  │              │
│   │  Mobile   │            │  & AI    │              │
│   │  Apps     │            │  Agents  │              │
│   └───────────┘            └──────────┘              │
│                                                       │
└───────────────────────────────────────────────────────┘
```

**Protocol Selection**:

| Use Case | Protocol | Reason |
|----------|----------|--------|
| Web dashboard | REST + WebSocket | Real-time UI |
| Mobile app | REST | Standard, well-supported |
| AI analysis | MCP | AI-optimized |
| Integrations | REST + Webhooks | Standard |
| AI agents | MCP | Native support |
| Bulk export | REST | Pagination |
| Real-time updates | WebSocket | Push |

### 5.4 MCP vs REST/WebSocket: When to Use What

#### Decision Matrix

```
┌─────────────────────────────────────────────────────┐
│                  Protocol Decision                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Action                    Best Protocol      │
│  ────────────────────────────────────────────      │
│                                                     │
│  View dashboard                 REST + WebSocket   │
│  Create feedback                REST POST          │
│  Get real-time updates          WebSocket          │
│  Export data                    REST (paginated)   │
│  Trigger external system        Webhook (outbound) │
│  Receive external event         Webhook (inbound)  │
│  AI analyzes feedback           MCP                │
│  AI generates roadmap           MCP                │
│  Conversational query           MCP                │
│  Automated reporting            MCP                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 5.5 Implementation Priority

#### Phase 1: Foundation (Complete)
- ✅ REST API
- ✅ WebSocket real-time
- ✅ Webhook system
- ✅ Source integrations (Slack, GitHub, Discord, Reddit)

#### Phase 2: Enhancements (Q3 2026)
- 🔨 More API endpoints
- 🔨 Advanced filtering
- 🔨 Bulk operations
- 🔨 API versioning

#### Phase 3: AI Integration (Q4 2026)
- 📋 MCP server implementation
- 📋 Claude integration
- 📋 AI-powered insights
- 📋 Natural language queries

#### Phase 4: Ecosystem (2027)
- 📋 Zapier integration
- 📋 Make.com integration
- 📋 Public API marketplace
- 📋 Developer platform

---

## Appendices

### Appendix A: Comparison Table

| Feature | REST | GraphQL | WebSocket | MCP | Webhook |
|---------|------|---------|-----------|-----|---------|
| **Protocol** | HTTP | HTTP | WebSocket | JSON-RPC | HTTP |
| **Direction** | Client→Server | Client→Server | Bidirectional | Bidirectional | Server→Client |
| **Real-time** | Polling/SSE | Subscriptions | Native | SSE | Native |
| **Overhead** | Medium | Medium | Low | Medium | Low |
| **Caching** | Easy | Complex | N/A | Complex | N/A |
| **Tooling** | Excellent | Good | Good | Limited | Good |
| **AI-Optimized** | No | No | No | Yes | No |
| **Use Case** | CRUD | Complex queries | Chat/gaming | AI integration | Event notification |

### Appendix B: Code Examples Repository

All code examples from this document are available at:
- `/home/wsl-user/compass/backend/` (existing)
- `/home/wsl-user/compass/examples/mcp/` (to be created)
- `/home/wsl-user/compass/examples/webhooks/` (to be created)

### Appendix C: Further Reading

**MCP Resources**:
- Official Spec: https://spec.modelcontextprotocol.io
- GitHub: https://github.com/modelcontextprotocol
- Server Registry: https://github.com/modelcontextprotocol/servers
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

**Connector Frameworks**:
- Airbyte: https://docs.airbyte.com
- Zapier Platform: https://platform.zapier.com/docs
- Make: https://www.make.com/en/api-documentation
- n8n: https://docs.n8n.io

**OAuth & Security**:
- OAuth 2.0 RFC: https://oauth.net/2/
- PKCE: https://oauth.net/2/pkce/
- JWT: https://jwt.io

**Real-Time Patterns**:
- WebSocket RFC: https://datatracker.ietf.org/doc/html/rfc6455
- SSE Spec: https://html.spec.whatwg.org/multipage/server-sent-events.html
- gRPC: https://grpc.io/docs/

### Appendix D: Glossary

- **CDC**: Change Data Capture - detecting and capturing changes in data
- **ELT**: Extract, Load, Transform - data pipeline pattern
- **ETL**: Extract, Transform, Load - traditional data pipeline
- **JSON-RPC**: JSON Remote Procedure Call - RPC protocol using JSON
- **MCP**: Model Context Protocol - Anthropic's protocol for AI-to-data communication
- **PKCE**: Proof Key for Code Exchange - OAuth security extension
- **SSE**: Server-Sent Events - one-way streaming over HTTP
- **stdio**: Standard input/output - inter-process communication method

---

## Conclusion

### Key Takeaways

1. **MCP is the future** for AI-native applications
2. **REST/WebSocket remain essential** for traditional apps
3. **Compass should adopt both** for maximum flexibility
4. **Timing matters**: Build MCP server in Q4 2026 (not Q3)
5. **Competitive advantage**: MCP positions Compass as AI-native

### Next Steps

1. **Q3 2026**: Continue REST/WebSocket development
2. **Q4 2026**: Build MCP server prototype
3. **Q1 2027**: Launch public MCP integration
4. **Q2 2027**: Expand to connector platforms (Zapier, etc.)

### Strategic Positioning

**Compass in 2027**:
- "The AI-native feedback platform"
- "Works with Claude, GPT, and all major LLMs"
- "Natural language roadmap generation"
- "Intelligent feedback analysis"

This positions Compass ahead of competitors still stuck in traditional dashboard UIs.

---

**End of Report**

*Prepared by: Claude (Anthropic)*
*Date: August 4, 2026*
*Status: Comprehensive Research Complete*
