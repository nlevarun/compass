# Compass Python SDK

Official Python client for the [Compass](https://compass.example.com) Customer Feedback Intelligence Platform API.

## Installation

```bash
pip install compass-sdk
```

## Quick Start

```python
from compass_sdk import CompassClient

# Initialize client with your API key
client = CompassClient(
    api_key="compass_your_api_key_here",
    base_url="https://api.compass.example.com"  # or http://localhost:8000 for development
)

# Get dashboard statistics
stats = client.stats()
print(f"Total feedback: {stats.total_feedback}")
print(f"Total clusters: {stats.total_clusters}")

# List feedback with filters
response = client.feedback.list(
    limit=50,
    search="mobile app",
    min_sentiment=0.5,
    sort_by="submitted_at",
    sort_order="desc"
)

for feedback in response["data"]:
    print(f"[{feedback['customer_name']}] {feedback['text'][:100]}")

# Get clusters sorted by priority
clusters_response = client.clusters.list(
    sort_by="priority_score",
    sort_order="desc"
)

for cluster in clusters_response["data"]:
    print(f"#{cluster['rank']} {cluster['label']} - Priority: {cluster['priority_score']:.2f}")

# Get detailed cluster information
cluster = client.clusters.get(cluster_id=1)
print(f"Cluster: {cluster.label}")
print(f"Feedback items: {len(cluster.feedback)}")

# Update roadmap item status
client.roadmap.update(
    item_id=1,
    status=RoadmapStatus.IN_PROGRESS,
    estimated_effort="medium"
)
```

## Context Manager

Use the client as a context manager for automatic cleanup:

```python
with CompassClient(api_key="your-api-key") as client:
    stats = client.stats()
    print(stats)
```

## API Reference

### Sources

```python
# List all sources
sources = client.sources.list(limit=100, is_active=True)

# Sync feedback from all sources
result = client.sources.sync()
print(f"Synced {result['total_synced']} items")
```

### Feedback

```python
# List feedback with filtering
feedback = client.feedback.list(
    limit=100,
    offset=0,
    source_id=1,              # Filter by source
    cluster_id=2,             # Filter by cluster (-1 for unclustered)
    min_sentiment=-1.0,       # Minimum sentiment score
    max_sentiment=1.0,        # Maximum sentiment score
    search="bug",             # Search text
    sort_by="submitted_at",   # Sort field
    sort_order="desc"         # Sort order
)

# Access paginated data
for item in feedback["data"]:
    print(item)

# Check pagination
meta = feedback["meta"]
print(f"Total: {meta['total']}, Has next: {meta['has_next']}")
```

### Clusters

```python
# List clusters
clusters = client.clusters.list(
    min_size=5,                    # Minimum cluster size
    sort_by="priority_score",      # Sort by priority
    sort_order="desc"
)

# Get cluster details with feedback
cluster = client.clusters.get(cluster_id=1)
print(f"{cluster.label}: {cluster.size} items")
for fb in cluster.feedback:
    print(f"  - {fb.text[:50]}")

# Run clustering
result = client.clusters.run_clustering(
    eps=0.5,           # DBSCAN epsilon parameter
    min_samples=3      # Minimum samples per cluster
)
print(f"Created {result['clusters_created']} clusters")
```

### Roadmap

```python
# List roadmap items
roadmap = client.roadmap.list(
    status=RoadmapStatus.PROPOSED,
    limit=50
)

# Update roadmap item
item = client.roadmap.update(
    item_id=1,
    status=RoadmapStatus.IN_PROGRESS,
    estimated_effort="large",
    estimated_value="high"
)

# Generate roadmap from clusters
result = client.roadmap.generate()
print(result["insights"])
```

### API Keys

```python
# Create new API key
api_key = client.api_keys.create(
    name="Production API Key",
    expires_in_days=365  # Optional expiration
)
print(f"Your API key: {api_key.key}")  # Save this!

# List API keys
keys = client.api_keys.list()
for key in keys:
    print(f"{key.name}: {key.key_prefix}...")

# Revoke API key
client.api_keys.revoke(key_id=1)
```

### Webhooks

```python
from compass_sdk import WebhookEvent

# Create webhook
webhook = client.webhooks.create(
    url="https://your-app.com/webhooks/compass",
    events=[
        WebhookEvent.FEEDBACK_CREATED,
        WebhookEvent.CLUSTER_CREATED,
        WebhookEvent.ROADMAP_UPDATED
    ],
    secret="your-webhook-secret"  # Optional, auto-generated if not provided
)

# List webhooks
webhooks = client.webhooks.list()

# Update webhook
webhook = client.webhooks.update(
    webhook_id=1,
    is_active=False  # Pause webhook
)

# Get delivery logs
deliveries = client.webhooks.deliveries(webhook_id=1, limit=50)
for delivery in deliveries["data"]:
    print(f"{delivery['event_type']}: {delivery['success']}")

# Delete webhook
client.webhooks.delete(webhook_id=1)
```

## Error Handling

```python
from compass_sdk import (
    CompassAPIError,
    CompassAuthenticationError,
    CompassNotFoundError,
    CompassRateLimitError
)

try:
    feedback = client.feedback.list()
except CompassAuthenticationError:
    print("Invalid API key")
except CompassNotFoundError:
    print("Resource not found")
except CompassRateLimitError:
    print("Rate limit exceeded, please wait")
except CompassAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Type Hints

The SDK includes full type hints for better IDE support:

```python
from compass_sdk import CompassClient, Cluster
from typing import List

client = CompassClient(api_key="key")

# Type-safe responses
cluster: Cluster = client.clusters.get(1)
stats: Stats = client.stats()
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black compass_sdk/

# Type checking
mypy compass_sdk/
```

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://docs.compass.example.com
- Issues: https://github.com/compass/compass-python-sdk/issues
- Email: support@compass.example.com
