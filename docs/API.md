# Compass API Documentation

**Version:** 1.0.0
**Base URL:** `https://api.compass.example.com` or `http://localhost:8000` (development)

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Sources](#sources)
  - [Feedback](#feedback)
  - [Clusters](#clusters)
  - [Roadmap](#roadmap)
  - [Statistics](#statistics)
  - [API Keys](#api-keys)
  - [Webhooks](#webhooks)
- [SDKs](#sdks)
- [Webhooks Guide](#webhooks-guide)

---

## Getting Started

The Compass API is a RESTful API that allows you to interact with the Compass Customer Feedback Intelligence Platform programmatically. All API endpoints return JSON responses.

### Base URL

```
Production: https://api.compass.example.com
Development: http://localhost:8000
```

### API Versioning

All endpoints are versioned with the `/api/v1/` prefix:

```
GET /api/v1/feedback
POST /api/v1/clustering/run
```

### Quick Example

```bash
curl -X GET "http://localhost:8000/api/v1/stats" \
  -H "X-API-Key: compass_your_api_key_here"
```

---

## Authentication

Compass API uses API key authentication. Include your API key in the `X-API-Key` header with every request.

### Getting an API Key

1. **Create an API key via the API:**

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 365
  }'
```

Response:
```json
{
  "id": 1,
  "name": "My API Key",
  "key": "compass_abc123...",  // Save this! Only shown once
  "key_prefix": "compass_abc",
  "is_active": true,
  "created_at": "2026-08-03T10:00:00Z",
  "expires_at": "2027-08-03T10:00:00Z"
}
```

**⚠️ Important:** The full API key is only shown once during creation. Store it securely!

### Using Your API Key

Include the API key in the `X-API-Key` header:

```bash
curl -X GET "http://localhost:8000/api/v1/feedback" \
  -H "X-API-Key: compass_your_api_key_here"
```

### Authentication Errors

- **401 Unauthorized:** Invalid or missing API key
- **403 Forbidden:** API key expired or deactivated

---

## Rate Limiting

To ensure fair usage, the Compass API implements rate limiting:

| Endpoint Type | Rate Limit |
|--------------|------------|
| Read endpoints (GET) | 60 requests/minute |
| Write endpoints (POST, PATCH, DELETE) | 30 requests/minute |
| Heavy operations (clustering, sync) | 10 requests/minute |
| Root endpoint | 100 requests/minute |

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 57
X-RateLimit-Reset: 1691059200
```

### Rate Limit Exceeded

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Please slow down",
  "code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2026-08-03T10:00:00Z"
}
```

**Best Practices:**
- Implement exponential backoff
- Cache responses when possible
- Use webhooks instead of polling

---

## Pagination

All list endpoints support pagination with consistent parameters:

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Number of items to return (max 1000) |
| `offset` | integer | 0 | Number of items to skip |

### Response Format

```json
{
  "data": [...],
  "meta": {
    "total": 250,
    "limit": 100,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

### Example

```bash
# Get first page
curl "http://localhost:8000/api/v1/feedback?limit=50&offset=0" \
  -H "X-API-Key: your_key"

# Get second page
curl "http://localhost:8000/api/v1/feedback?limit=50&offset=50" \
  -H "X-API-Key: your_key"
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE",
  "timestamp": "2026-08-03T10:00:00Z"
}
```

### HTTP Status Codes

| Status Code | Meaning |
|-------------|---------|
| 200 OK | Request succeeded |
| 201 Created | Resource created |
| 400 Bad Request | Invalid request parameters |
| 401 Unauthorized | Authentication failed |
| 404 Not Found | Resource not found |
| 422 Unprocessable Entity | Validation error |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_ERROR` | Invalid API key |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `VALIDATION_ERROR` | Invalid input |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| `INTERNAL_ERROR` | Server error |

---

## Endpoints

### Sources

#### List Sources

Get all feedback sources with pagination and filtering.

**Endpoint:** `GET /api/v1/sources`

**Parameters:**
- `limit` (integer, optional): Items per page (default: 100, max: 1000)
- `offset` (integer, optional): Offset for pagination (default: 0)
- `is_active` (boolean, optional): Filter by active status

**Example:**
```bash
curl "http://localhost:8000/api/v1/sources?limit=10&is_active=true" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Slack",
      "source_type": "real",
      "is_active": true,
      "created_at": "2026-08-01T10:00:00Z",
      "last_synced_at": "2026-08-03T09:30:00Z",
      "feedback_count": 150
    }
  ],
  "meta": {
    "total": 5,
    "limit": 10,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

#### Sync Sources

Sync feedback from all active sources.

**Endpoint:** `POST /api/v1/sources/sync`
**Authentication:** Required

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/sources/sync" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "total_synced": 47,
  "sources_synced": 3,
  "results": [
    {
      "source": "Slack",
      "synced": 23,
      "status": "success"
    },
    {
      "source": "Zendesk",
      "synced": 24,
      "status": "success"
    }
  ],
  "elapsed_time": 2.34
}
```

---

### Feedback

#### List Feedback

Get feedback with pagination, filtering, sorting, and search.

**Endpoint:** `GET /api/v1/feedback`

**Parameters:**
- `limit` (integer, optional): Items per page (default: 100, max: 1000)
- `offset` (integer, optional): Offset for pagination (default: 0)
- `source_id` (integer, optional): Filter by source ID
- `cluster_id` (integer, optional): Filter by cluster ID (-1 for unclustered)
- `min_sentiment` (float, optional): Minimum sentiment score (-1 to 1)
- `max_sentiment` (float, optional): Maximum sentiment score (-1 to 1)
- `search` (string, optional): Search in feedback text (case-insensitive)
- `sort_by` (string, optional): Field to sort by (default: `submitted_at`)
  - Options: `submitted_at`, `sentiment_score`, `customer_revenue`
- `sort_order` (string, optional): Sort order (default: `desc`)
  - Options: `asc`, `desc`

**Example:**
```bash
curl "http://localhost:8000/api/v1/feedback?limit=50&search=mobile&min_sentiment=0.5&sort_by=submitted_at&sort_order=desc" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 123,
      "text": "The mobile app keeps crashing when I try to upload photos",
      "customer_name": "Acme Corp",
      "customer_revenue": 50000.0,
      "sentiment_score": -0.65,
      "submitted_at": "2026-08-03T09:15:00Z",
      "source_name": "Slack",
      "cluster_id": 5
    }
  ],
  "meta": {
    "total": 87,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### Clusters

#### List Clusters

Get all clusters with pagination, filtering, and sorting.

**Endpoint:** `GET /api/v1/clusters`

**Parameters:**
- `limit` (integer, optional): Items per page (default: 100, max: 1000)
- `offset` (integer, optional): Offset for pagination (default: 0)
- `min_size` (integer, optional): Minimum cluster size
- `sort_by` (string, optional): Field to sort by (default: `priority_score`)
  - Options: `priority_score`, `size`, `total_revenue`, `avg_sentiment`
- `sort_order` (string, optional): Sort order (default: `desc`)

**Example:**
```bash
curl "http://localhost:8000/api/v1/clusters?sort_by=priority_score&sort_order=desc&limit=10" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "label": "Mobile App Crashes",
      "size": 23,
      "priority_score": 8.7,
      "total_revenue": 450000.0,
      "avg_sentiment": -0.68,
      "created_at": "2026-08-02T14:30:00Z"
    }
  ],
  "meta": {
    "total": 15,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Cluster Details

Get a specific cluster with all its feedback items.

**Endpoint:** `GET /api/v1/clusters/{cluster_id}`

**Example:**
```bash
curl "http://localhost:8000/api/v1/clusters/1" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "id": 1,
  "label": "Mobile App Crashes",
  "size": 23,
  "priority_score": 8.7,
  "total_revenue": 450000.0,
  "avg_sentiment": -0.68,
  "created_at": "2026-08-02T14:30:00Z",
  "feedback": [
    {
      "id": 123,
      "text": "The mobile app keeps crashing...",
      "customer_name": "Acme Corp",
      "customer_revenue": 50000.0,
      "sentiment_score": -0.65,
      "submitted_at": "2026-08-03T09:15:00Z"
    }
  ]
}
```

#### Run Clustering

Run NLP clustering on all feedback.

**Endpoint:** `POST /api/v1/clustering/run`
**Authentication:** Required

**Parameters:**
- `eps` (float, optional): DBSCAN epsilon parameter (default: 0.5, range: 0.1-1.0)
- `min_samples` (integer, optional): DBSCAN min_samples parameter (default: 3, range: 2-10)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/clustering/run?eps=0.5&min_samples=3" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "status": "success",
  "feedback_clustered": 250,
  "clusters_created": 15,
  "noise_points": 12,
  "metrics": {
    "silhouette_score": 0.67,
    "n_clusters": 15,
    "n_noise": 12
  },
  "elapsed_time": 12.45
}
```

---

### Roadmap

#### List Roadmap Items

Get prioritized roadmap with pagination and filtering.

**Endpoint:** `GET /api/v1/roadmap`

**Parameters:**
- `limit` (integer, optional): Items per page (default: 100, max: 1000)
- `offset` (integer, optional): Offset for pagination (default: 0)
- `status` (string, optional): Filter by status
  - Options: `proposed`, `planned`, `in_progress`, `shipped`

**Example:**
```bash
curl "http://localhost:8000/api/v1/roadmap?status=proposed&limit=10" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Fix Mobile App Crashes",
      "rank": 1,
      "priority_score": 8.7,
      "request_count": 23,
      "impacted_revenue": 450000.0,
      "status": "proposed",
      "created_at": "2026-08-02T15:00:00Z"
    }
  ],
  "meta": {
    "total": 12,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Update Roadmap Item

Update a roadmap item's status and estimates.

**Endpoint:** `PATCH /api/v1/roadmap/{item_id}`
**Authentication:** Required

**Body:**
```json
{
  "status": "in_progress",
  "estimated_effort": "large",
  "estimated_value": "high"
}
```

**Example:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/roadmap/1" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "estimated_effort": "large"
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Fix Mobile App Crashes",
  "rank": 1,
  "priority_score": 8.7,
  "request_count": 23,
  "impacted_revenue": 450000.0,
  "status": "in_progress",
  "created_at": "2026-08-02T15:00:00Z"
}
```

#### Generate Roadmap

Generate prioritized roadmap from clusters.

**Endpoint:** `POST /api/v1/roadmap/generate`
**Authentication:** Required

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/roadmap/generate" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "status": "success",
  "items_generated": 15,
  "insights": {
    "top_priority": "Fix Mobile App Crashes",
    "total_revenue_impact": 2450000.0,
    "avg_priority_score": 6.3
  },
  "elapsed_time": 0.87
}
```

---

### Statistics

#### Get Dashboard Statistics

Get comprehensive dashboard statistics.

**Endpoint:** `GET /api/v1/stats`

**Example:**
```bash
curl "http://localhost:8000/api/v1/stats" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "total_feedback": 1250,
  "total_sources": 5,
  "total_clusters": 15,
  "total_roadmap_items": 12,
  "total_revenue_impact": 2450000.0,
  "avg_sentiment": 0.12,
  "recent_feedback_30d": 347,
  "timestamp": "2026-08-03T10:00:00Z"
}
```

---

### API Keys

#### Create API Key

Create a new API key for authentication.

**Endpoint:** `POST /api/v1/api-keys`

**Body:**
```json
{
  "name": "Production API Key",
  "expires_in_days": 365
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "expires_in_days": 365
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Production API Key",
  "key": "compass_abc123def456...",  // Only shown once!
  "key_prefix": "compass_abc",
  "is_active": true,
  "created_at": "2026-08-03T10:00:00Z",
  "expires_at": "2027-08-03T10:00:00Z"
}
```

#### List API Keys

List all API keys (without showing actual keys).

**Endpoint:** `GET /api/v1/api-keys`
**Authentication:** Required

**Example:**
```bash
curl "http://localhost:8000/api/v1/api-keys" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Production API Key",
      "key_prefix": "compass_abc",
      "is_active": true,
      "created_at": "2026-08-03T10:00:00Z",
      "expires_at": "2027-08-03T10:00:00Z"
    }
  ]
}
```

#### Revoke API Key

Revoke (deactivate) an API key.

**Endpoint:** `DELETE /api/v1/api-keys/{key_id}`
**Authentication:** Required

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/api-keys/1" \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "status": "success",
  "message": "API key 1 revoked"
}
```

---

### Webhooks

See [Webhooks Guide](#webhooks-guide) for detailed webhook documentation.

---

## SDKs

Official SDKs are available for Python and TypeScript/JavaScript:

### Python SDK

```bash
pip install compass-sdk
```

```python
from compass_sdk import CompassClient

client = CompassClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Get stats
stats = client.stats()
print(f"Total feedback: {stats.total_feedback}")

# List feedback
feedback = client.feedback.list(limit=50, search="mobile app")
```

**Documentation:** See `backend/sdk/python/README.md`

### TypeScript/JavaScript SDK

```bash
npm install compass-sdk
```

```typescript
import { CompassClient } from 'compass-sdk';

const client = new CompassClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

// Get stats
const stats = await client.stats();
console.log(`Total feedback: ${stats.total_feedback}`);

// List feedback
const feedback = await client.feedback.list({
  limit: 50,
  search: 'mobile app'
});
```

**Documentation:** See `frontend/sdk/typescript/README.md`

---

## Webhooks Guide

Webhooks allow you to receive real-time notifications when events occur in Compass.

### Supported Events

- `feedback.created` - New feedback received
- `cluster.created` - New cluster created
- `roadmap.updated` - Roadmap item updated
- `priority.changed` - Priority score changed

### Creating a Webhook

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/compass",
    "events": ["feedback.created", "cluster.created"],
    "secret": "your_webhook_secret"
  }'
```

### Webhook Payload

```json
{
  "event": "feedback.created",
  "data": {
    "id": 123,
    "feedback": {
      "text": "The mobile app keeps crashing...",
      "customer_name": "Acme Corp",
      "sentiment_score": -0.65
    }
  },
  "timestamp": "2026-08-03T10:00:00Z",
  "webhook_id": 1
}
```

### Signature Verification

All webhook payloads include an `X-Webhook-Signature` header with HMAC-SHA256 signature:

```python
import hmac
import hashlib
import json

def verify_webhook(payload, signature, secret):
    payload_json = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### Retry Logic

- Failed webhooks are retried 3 times
- Retry delays: 1s, 5s, 15s
- After 10 consecutive failures, webhook is automatically deactivated

### Example Webhook Receiver (Python/Flask)

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route("/webhooks/compass", methods=["POST"])
def handle_webhook():
    # Verify signature
    signature = request.headers.get("X-Webhook-Signature")
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
        print(f"New feedback: {data['feedback']['text']}")

    return jsonify({"status": "success"}), 200
```

---

## Support

- **Documentation:** https://docs.compass.example.com
- **GitHub:** https://github.com/compass/compass
- **Email:** support@compass.example.com
- **Status Page:** https://status.compass.example.com

## Version History

- **v1.0.0** (2026-08-03) - Initial release
  - Core API endpoints
  - Python and TypeScript SDKs
  - Webhooks support
  - Rate limiting
  - API key authentication
