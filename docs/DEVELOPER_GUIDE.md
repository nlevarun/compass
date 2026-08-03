# Compass Developer Guide

Welcome to the Compass Developer Portal! This guide will help you integrate with the Compass Customer Feedback Intelligence Platform API.

## Table of Contents

- [Quick Start](#quick-start)
- [API Key Management](#api-key-management)
- [SDK Setup](#sdk-setup)
- [Webhook Configuration](#webhook-configuration)
- [Best Practices](#best-practices)
- [Testing & Sandbox](#testing--sandbox)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Get Your API Key

First, create an API key to authenticate your requests:

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First API Key",
    "expires_in_days": 365
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "My First API Key",
  "key": "compass_abc123def456...",  // ⚠️ Save this!
  "key_prefix": "compass_abc",
  "is_active": true,
  "created_at": "2026-08-03T10:00:00Z",
  "expires_at": "2027-08-03T10:00:00Z"
}
```

**⚠️ IMPORTANT:** The full API key is only shown once. Store it securely (e.g., in environment variables or a secrets manager).

### 2. Make Your First Request

Test your API key with a simple stats request:

```bash
curl "http://localhost:8000/api/v1/stats" \
  -H "X-API-Key: compass_your_api_key_here"
```

### 3. Install SDK (Recommended)

**Python:**
```bash
pip install compass-sdk
```

**TypeScript/JavaScript:**
```bash
npm install compass-sdk
```

### 4. Start Building

**Python:**
```python
from compass_sdk import CompassClient

client = CompassClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

stats = client.stats()
print(f"Total feedback: {stats.total_feedback}")
```

**TypeScript:**
```typescript
import { CompassClient } from 'compass-sdk';

const client = new CompassClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

const stats = await client.stats();
console.log(`Total feedback: ${stats.total_feedback}`);
```

---

## API Key Management

### Creating API Keys

API keys are your credentials for accessing the Compass API. Each key can have:

- **Name:** Descriptive label (e.g., "Production Server", "Analytics Dashboard")
- **Expiration:** Optional expiration date (recommended for security)

**Best Practices:**
- Create separate keys for different environments (dev, staging, prod)
- Use descriptive names to identify keys easily
- Set expiration dates for enhanced security
- Rotate keys regularly (every 6-12 months)

### Listing Your API Keys

```bash
curl "http://localhost:8000/api/v1/api-keys" \
  -H "X-API-Key: your_existing_key"
```

This shows all your keys (without revealing the actual key values):

```json
{
  "data": [
    {
      "id": 1,
      "name": "Production Server",
      "key_prefix": "compass_abc",
      "is_active": true,
      "created_at": "2026-08-01T10:00:00Z",
      "expires_at": "2027-08-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Analytics Dashboard",
      "key_prefix": "compass_def",
      "is_active": true,
      "created_at": "2026-08-02T14:00:00Z",
      "expires_at": null
    }
  ]
}
```

### Revoking API Keys

When a key is compromised or no longer needed, revoke it immediately:

```bash
curl -X DELETE "http://localhost:8000/api/v1/api-keys/1" \
  -H "X-API-Key: your_admin_key"
```

**Note:** Revoking a key is permanent. The key will immediately stop working.

### Key Rotation Strategy

1. **Create new key:** Generate a new API key
2. **Update applications:** Deploy the new key to your applications
3. **Monitor:** Verify the new key is working correctly
4. **Revoke old key:** Deactivate the old key after successful migration

### Storing API Keys Securely

**DO:**
- ✅ Store in environment variables
- ✅ Use secrets management systems (AWS Secrets Manager, HashiCorp Vault, etc.)
- ✅ Encrypt keys at rest
- ✅ Limit access to keys using IAM policies

**DON'T:**
- ❌ Hardcode keys in source code
- ❌ Commit keys to version control
- ❌ Share keys via email or chat
- ❌ Store keys in plain text files

**Example (.env file):**
```bash
COMPASS_API_KEY=compass_your_api_key_here
COMPASS_BASE_URL=https://api.compass.example.com
```

---

## SDK Setup

### Python SDK

#### Installation

```bash
pip install compass-sdk
```

#### Configuration

**Basic setup:**
```python
from compass_sdk import CompassClient

client = CompassClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)
```

**With environment variables:**
```python
import os
from compass_sdk import CompassClient

client = CompassClient(
    api_key=os.environ["COMPASS_API_KEY"],
    base_url=os.environ.get("COMPASS_BASE_URL", "http://localhost:8000")
)
```

**With context manager (recommended):**
```python
with CompassClient(api_key="your_key") as client:
    stats = client.stats()
    # Client automatically closed after use
```

#### Error Handling

```python
from compass_sdk import (
    CompassAPIError,
    CompassAuthenticationError,
    CompassRateLimitError
)

try:
    feedback = client.feedback.list()
except CompassAuthenticationError:
    print("Invalid API key - check your credentials")
except CompassRateLimitError:
    print("Rate limit exceeded - slow down requests")
    time.sleep(60)  # Wait before retrying
except CompassAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

### TypeScript/JavaScript SDK

#### Installation

```bash
npm install compass-sdk
# or
yarn add compass-sdk
```

#### Configuration

**TypeScript:**
```typescript
import { CompassClient } from 'compass-sdk';

const client = new CompassClient({
  apiKey: process.env.COMPASS_API_KEY!,
  baseUrl: process.env.COMPASS_BASE_URL || 'http://localhost:8000',
  timeout: 30000  // Optional: 30 second timeout
});
```

**JavaScript (Node.js):**
```javascript
const { CompassClient } = require('compass-sdk');

const client = new CompassClient({
  apiKey: process.env.COMPASS_API_KEY,
  baseUrl: 'http://localhost:8000'
});
```

#### Error Handling

```typescript
import {
  CompassAPIError,
  CompassAuthenticationError,
  CompassRateLimitError
} from 'compass-sdk';

try {
  const feedback = await client.feedback.list();
} catch (error) {
  if (error instanceof CompassAuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof CompassRateLimitError) {
    console.error('Rate limit exceeded');
    await new Promise(resolve => setTimeout(resolve, 60000));
  } else if (error instanceof CompassAPIError) {
    console.error(`API error: ${error.message}`);
  }
}
```

---

## Webhook Configuration

Webhooks allow you to receive real-time notifications when events occur in Compass, eliminating the need for polling.

### Supported Events

| Event | Triggered When |
|-------|----------------|
| `feedback.created` | New feedback is ingested |
| `cluster.created` | New cluster is created during clustering |
| `roadmap.updated` | Roadmap item status changes |
| `priority.changed` | Cluster priority score changes |

### Creating a Webhook

**1. Set up your webhook endpoint:**

Your endpoint must:
- Accept POST requests
- Return 200-299 status code on success
- Process requests within 10 seconds
- Verify webhook signature (recommended)

**Example (Python/Flask):**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route("/webhooks/compass", methods=["POST"])
def handle_webhook():
    # Get signature
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        return jsonify({"error": "Missing signature"}), 401

    # Verify signature
    payload = request.get_json()
    payload_json = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"error": "Invalid signature"}), 401

    # Process event
    event_type = payload["event"]
    data = payload["data"]

    if event_type == "feedback.created":
        handle_new_feedback(data)
    elif event_type == "cluster.created":
        handle_new_cluster(data)

    return jsonify({"status": "success"}), 200

def handle_new_feedback(data):
    feedback = data["feedback"]
    print(f"New feedback from {feedback['customer_name']}: {feedback['text']}")
    # Send notification, update dashboard, etc.

def handle_new_cluster(data):
    cluster = data["cluster"]
    print(f"New cluster created: {cluster['label']}")
    # Alert team, create Jira ticket, etc.
```

**2. Register the webhook:**

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/compass",
    "events": [
      "feedback.created",
      "cluster.created",
      "roadmap.updated",
      "priority.changed"
    ],
    "secret": "your_webhook_secret"
  }'
```

**Response:**
```json
{
  "id": 1,
  "url": "https://your-app.com/webhooks/compass",
  "events": ["feedback.created", "cluster.created"],
  "is_active": true,
  "status": "active",
  "total_deliveries": 0,
  "successful_deliveries": 0,
  "failed_deliveries": 0,
  "created_at": "2026-08-03T10:00:00Z"
}
```

### Webhook Payload Structure

All webhooks follow this structure:

```json
{
  "event": "feedback.created",
  "data": {
    "id": 123,
    "feedback": {
      "text": "The mobile app keeps crashing",
      "customer_name": "Acme Corp",
      "customer_revenue": 50000.0,
      "sentiment_score": -0.65
    }
  },
  "timestamp": "2026-08-03T10:00:00Z",
  "webhook_id": 1
}
```

### Signature Verification

Every webhook includes an `X-Webhook-Signature` header with an HMAC-SHA256 signature.

**Python:**
```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    payload_json = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

**Node.js:**
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const payloadJson = JSON.stringify(payload, Object.keys(payload).sort());
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payloadJson)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

### Retry Logic

Compass automatically retries failed webhook deliveries:

- **3 retry attempts** with exponential backoff (1s, 5s, 15s)
- **10 second timeout** per request
- After **10 consecutive failures**, webhook is automatically deactivated

### Monitoring Webhook Health

**Check webhook status:**
```bash
curl "http://localhost:8000/api/v1/webhooks/1" \
  -H "X-API-Key: your_key"
```

**View delivery history:**
```bash
curl "http://localhost:8000/api/v1/webhooks/1/deliveries?limit=50" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "webhook_id": 1,
      "event_type": "feedback.created",
      "status_code": 200,
      "success": true,
      "attempt": 1,
      "duration_ms": 145.3,
      "created_at": "2026-08-03T10:00:00Z"
    }
  ],
  "meta": {
    "total": 47,
    "limit": 50,
    "offset": 0
  }
}
```

### Testing Webhooks Locally

Use tools like ngrok to expose your local server:

```bash
# Start ngrok
ngrok http 5000

# Use the ngrok URL for your webhook
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abc123.ngrok.io/webhooks/compass",
    "events": ["feedback.created"]
  }'
```

---

## Best Practices

### Rate Limiting

**Be mindful of rate limits:**
- Read endpoints: 60 requests/minute
- Write endpoints: 30 requests/minute
- Heavy operations: 10 requests/minute

**Implement exponential backoff:**

```python
import time

def make_request_with_backoff(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.feedback.list()
        except CompassRateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

### Caching

Cache responses to reduce API calls:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedCompassClient:
    def __init__(self, client):
        self.client = client
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)

    def get_stats(self):
        cache_key = "stats"
        now = datetime.utcnow()

        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if now - cached_time < self.cache_ttl:
                return cached_data

        stats = self.client.stats()
        self.cache[cache_key] = (stats, now)
        return stats
```

### Pagination

Always paginate large result sets:

```python
def get_all_feedback(client):
    """Fetch all feedback using pagination"""
    all_feedback = []
    offset = 0
    limit = 100

    while True:
        response = client.feedback.list(limit=limit, offset=offset)
        all_feedback.extend(response["data"])

        if not response["meta"]["has_next"]:
            break

        offset += limit

    return all_feedback
```

### Error Handling

Always implement comprehensive error handling:

```python
from compass_sdk import CompassAPIError
import logging

logger = logging.getLogger(__name__)

def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with logging"""
    try:
        return func(*args, **kwargs)
    except CompassAPIError as e:
        logger.error(f"API error: {e.message} (status: {e.status_code})")
        logger.error(f"Response: {e.response}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
```

### Webhooks vs Polling

**Use webhooks when:**
- ✅ You need real-time updates
- ✅ You want to reduce API calls
- ✅ You have a stable, publicly accessible endpoint

**Use polling when:**
- ✅ Webhooks aren't feasible (firewall restrictions, etc.)
- ✅ You need to control the timing of updates
- ✅ You're in development/testing phase

---

## Testing & Sandbox

### Local Development

1. **Start the Compass API locally:**
```bash
cd compass/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main_v1.py
```

2. **Access the API:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/api/v1/docs
- Alternative docs: http://localhost:8000/api/v1/redoc

### Test Data

The local instance comes with mock data generators:

```bash
# Sync test data
curl -X POST "http://localhost:8000/api/v1/sources/sync" \
  -H "X-API-Key: your_key"

# Run clustering
curl -X POST "http://localhost:8000/api/v1/clustering/run" \
  -H "X-API-Key: your_key"

# Generate roadmap
curl -X POST "http://localhost:8000/api/v1/roadmap/generate" \
  -H "X-API-Key: your_key"
```

### Interactive API Documentation

Explore and test the API using the built-in Swagger UI:

http://localhost:8000/api/v1/docs

Features:
- Try all endpoints interactively
- See request/response schemas
- Generate code samples
- Test authentication

---

## Common Use Cases

### 1. Dashboard Integration

**Display key metrics in your dashboard:**

```python
def get_dashboard_data(client):
    stats = client.stats()
    top_clusters = client.clusters.list(limit=5, sort_by="priority_score")
    roadmap = client.roadmap.list(limit=10, status="proposed")

    return {
        "stats": stats,
        "top_priorities": top_clusters["data"],
        "roadmap": roadmap["data"]
    }
```

### 2. Sentiment Monitoring

**Monitor negative feedback:**

```python
def monitor_negative_feedback(client):
    # Get negative feedback (sentiment < 0)
    negative_feedback = client.feedback.list(
        max_sentiment=0,
        sort_by="submitted_at",
        sort_order="desc",
        limit=50
    )

    # Alert on high-value customer complaints
    for fb in negative_feedback["data"]:
        if fb["customer_revenue"] and fb["customer_revenue"] > 100000:
            send_alert(f"High-value customer complaint: {fb['text'][:100]}")
```

### 3. Automated Roadmap Prioritization

**Automatically update roadmap based on new feedback:**

```python
def update_roadmap_on_new_cluster(cluster_data):
    """Webhook handler for cluster.created event"""
    cluster_id = cluster_data["id"]
    cluster = cluster_data["cluster"]

    # Generate new roadmap
    client.roadmap.generate()

    # Get updated roadmap position
    roadmap = client.roadmap.list(limit=100)

    # Find this cluster in roadmap
    for item in roadmap["data"]:
        if item["cluster_id"] == cluster_id:
            # Notify team of new priority
            send_notification(
                f"New priority #{item['rank']}: {item['title']}"
            )
            break
```

### 4. Slack Integration

**Post top priorities to Slack:**

```python
from slack_sdk import WebClient

def post_priorities_to_slack(client, slack_client, channel):
    # Get top 5 priorities
    roadmap = client.roadmap.list(limit=5, status="proposed")

    message = "🎯 *Top Priorities This Week*\n\n"
    for item in roadmap["data"]:
        message += f"{item['rank']}. *{item['title']}*\n"
        message += f"   Priority: {item['priority_score']:.1f} | "
        message += f"Requests: {item['request_count']} | "
        message += f"Revenue Impact: ${item['impacted_revenue']:,.0f}\n\n"

    slack_client.chat_postMessage(channel=channel, text=message)
```

---

## Troubleshooting

### Common Issues

**1. 401 Unauthorized**
- **Cause:** Invalid or missing API key
- **Solution:** Check that you're including the `X-API-Key` header with a valid key

**2. 429 Rate Limit Exceeded**
- **Cause:** Too many requests
- **Solution:** Implement rate limiting and exponential backoff

**3. 422 Validation Error**
- **Cause:** Invalid request parameters
- **Solution:** Check the error response for details about which parameters are invalid

**4. Webhook not receiving events**
- **Cause:** URL not accessible, signature verification failing, or timeout
- **Solution:** Check webhook delivery logs, verify signature implementation, ensure endpoint responds within 10s

### Debug Mode

**Enable detailed logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("compass_sdk")
logger.setLevel(logging.DEBUG)
```

**Check webhook deliveries:**

```bash
curl "http://localhost:8000/api/v1/webhooks/1/deliveries" \
  -H "X-API-Key: your_key"
```

### Getting Help

- **Documentation:** https://docs.compass.example.com
- **GitHub Issues:** https://github.com/compass/compass/issues
- **Email Support:** support@compass.example.com
- **Community Slack:** https://compass-community.slack.com

---

## Next Steps

1. ✅ Get your API key
2. ✅ Install an SDK
3. ✅ Make your first API call
4. ✅ Set up webhooks
5. ✅ Build your integration

**Ready to go deeper?**
- Read the full [API Documentation](API.md)
- Explore [SDK examples](../backend/sdk/python/examples/)
- Check out the [GitHub repository](https://github.com/compass/compass)

---

**Happy building! 🚀**
