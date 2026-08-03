# Compass TypeScript SDK

Official TypeScript/JavaScript client for the [Compass](https://compass.example.com) Customer Feedback Intelligence Platform API.

## Installation

```bash
npm install compass-sdk
# or
yarn add compass-sdk
# or
pnpm add compass-sdk
```

## Quick Start

```typescript
import { CompassClient } from 'compass-sdk';

// Initialize client with your API key
const client = new CompassClient({
  apiKey: 'compass_your_api_key_here',
  baseUrl: 'https://api.compass.example.com', // or http://localhost:8000 for development
});

// Get dashboard statistics
const stats = await client.stats();
console.log(`Total feedback: ${stats.total_feedback}`);
console.log(`Total clusters: ${stats.total_clusters}`);

// List feedback with filters
const feedbackResponse = await client.feedback.list({
  limit: 50,
  search: 'mobile app',
  min_sentiment: 0.5,
  sort_by: 'submitted_at',
  sort_order: 'desc',
});

feedbackResponse.data.forEach((feedback) => {
  console.log(`[${feedback.customer_name}] ${feedback.text.slice(0, 100)}`);
});

// Get clusters sorted by priority
const clustersResponse = await client.clusters.list({
  sort_by: 'priority_score',
  sort_order: 'desc',
});

clustersResponse.data.forEach((cluster) => {
  console.log(`#${cluster.rank} ${cluster.label} - Priority: ${cluster.priority_score.toFixed(2)}`);
});

// Get detailed cluster information
const cluster = await client.clusters.get(1);
console.log(`Cluster: ${cluster.label}`);
console.log(`Feedback items: ${cluster.feedback.length}`);

// Update roadmap item status
await client.roadmap.update(1, {
  status: RoadmapStatus.IN_PROGRESS,
  estimated_effort: 'medium',
});
```

## JavaScript (ES6)

```javascript
const { CompassClient } = require('compass-sdk');

const client = new CompassClient({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:8000',
});

async function main() {
  const stats = await client.stats();
  console.log(stats);
}

main().catch(console.error);
```

## API Reference

### Client Initialization

```typescript
import { CompassClient } from 'compass-sdk';

const client = new CompassClient({
  apiKey: 'your-api-key',           // Required
  baseUrl: 'http://localhost:8000', // Optional, default: http://localhost:8000
  timeout: 30000,                   // Optional, default: 30000ms
  headers: {                        // Optional custom headers
    'X-Custom-Header': 'value',
  },
});
```

### Sources

```typescript
// List all sources
const sources = await client.sources.list({
  limit: 100,
  is_active: true,
});

// Sync feedback from all sources
const result = await client.sources.sync();
console.log(`Synced ${result.total_synced} items`);
```

### Feedback

```typescript
// List feedback with filtering
const feedback = await client.feedback.list({
  limit: 100,
  offset: 0,
  source_id: 1,              // Filter by source
  cluster_id: 2,             // Filter by cluster (-1 for unclustered)
  min_sentiment: -1.0,       // Minimum sentiment score
  max_sentiment: 1.0,        // Maximum sentiment score
  search: 'bug',             // Search text
  sort_by: 'submitted_at',   // Sort field
  sort_order: 'desc',        // Sort order
});

// Access paginated data
feedback.data.forEach((item) => console.log(item));

// Check pagination
const { meta } = feedback;
console.log(`Total: ${meta.total}, Has next: ${meta.has_next}`);

// Get specific feedback
const item = await client.feedback.get(123);
```

### Clusters

```typescript
import { SortOrder } from 'compass-sdk';

// List clusters
const clusters = await client.clusters.list({
  min_size: 5,                     // Minimum cluster size
  sort_by: 'priority_score',       // Sort by priority
  sort_order: SortOrder.DESC,
});

// Get cluster details with feedback
const cluster = await client.clusters.get(1);
console.log(`${cluster.label}: ${cluster.size} items`);
cluster.feedback.forEach((fb) => {
  console.log(`  - ${fb.text.slice(0, 50)}`);
});

// Run clustering
const result = await client.clusters.runClustering({
  eps: 0.5,           // DBSCAN epsilon parameter
  min_samples: 3,     // Minimum samples per cluster
});
console.log(`Created ${result.clusters_created} clusters`);
```

### Roadmap

```typescript
import { RoadmapStatus } from 'compass-sdk';

// List roadmap items
const roadmap = await client.roadmap.list({
  status: RoadmapStatus.PROPOSED,
  limit: 50,
});

// Get specific roadmap item
const item = await client.roadmap.get(1);

// Update roadmap item
const updated = await client.roadmap.update(1, {
  status: RoadmapStatus.IN_PROGRESS,
  estimated_effort: 'large',
  estimated_value: 'high',
});

// Generate roadmap from clusters
const result = await client.roadmap.generate();
console.log(result.insights);
```

### API Keys

```typescript
// Create new API key
const apiKey = await client.apiKeys.create({
  name: 'Production API Key',
  expires_in_days: 365, // Optional expiration
});
console.log(`Your API key: ${apiKey.key}`); // Save this!

// List API keys
const keys = await client.apiKeys.list();
keys.forEach((key) => {
  console.log(`${key.name}: ${key.key_prefix}...`);
});

// Revoke API key
await client.apiKeys.revoke(1);
```

### Webhooks

```typescript
import { WebhookEvent } from 'compass-sdk';

// Create webhook
const webhook = await client.webhooks.create({
  url: 'https://your-app.com/webhooks/compass',
  events: [
    WebhookEvent.FEEDBACK_CREATED,
    WebhookEvent.CLUSTER_CREATED,
    WebhookEvent.ROADMAP_UPDATED,
  ],
  secret: 'your-webhook-secret', // Optional, auto-generated if not provided
});

// List webhooks
const webhooks = await client.webhooks.list();

// Get specific webhook
const wh = await client.webhooks.get(1);

// Update webhook
const updated = await client.webhooks.update(1, {
  is_active: false, // Pause webhook
});

// Get delivery logs
const deliveries = await client.webhooks.deliveries(1, {
  limit: 50,
});
deliveries.data.forEach((delivery) => {
  console.log(`${delivery.event_type}: ${delivery.success}`);
});

// Delete webhook
await client.webhooks.delete(1);
```

## Error Handling

```typescript
import {
  CompassAPIError,
  CompassAuthenticationError,
  CompassNotFoundError,
  CompassRateLimitError,
  CompassValidationError,
} from 'compass-sdk';

try {
  const feedback = await client.feedback.list();
} catch (error) {
  if (error instanceof CompassAuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof CompassNotFoundError) {
    console.error('Resource not found');
  } else if (error instanceof CompassRateLimitError) {
    console.error('Rate limit exceeded, please wait');
  } else if (error instanceof CompassValidationError) {
    console.error('Validation error:', error.response);
  } else if (error instanceof CompassAPIError) {
    console.error(`API error: ${error.message} (status: ${error.statusCode})`);
  } else {
    console.error('Unknown error:', error);
  }
}
```

## TypeScript Support

The SDK is written in TypeScript and includes full type definitions:

```typescript
import { CompassClient, Cluster, Stats, PaginatedResponse } from 'compass-sdk';

const client = new CompassClient({ apiKey: 'key' });

// Type-safe responses
const cluster: Cluster = await client.clusters.get(1);
const stats: Stats = await client.stats();
const feedback: PaginatedResponse<Feedback> = await client.feedback.list();
```

## Examples

### React Usage

```typescript
import { useEffect, useState } from 'react';
import { CompassClient, Stats } from 'compass-sdk';

const client = new CompassClient({
  apiKey: process.env.REACT_APP_COMPASS_API_KEY!,
});

function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    client.stats().then(setStats);
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total Feedback: {stats.total_feedback}</p>
      <p>Total Clusters: {stats.total_clusters}</p>
    </div>
  );
}
```

### Node.js Server

```typescript
import express from 'express';
import { CompassClient } from 'compass-sdk';

const app = express();
const client = new CompassClient({
  apiKey: process.env.COMPASS_API_KEY!,
});

app.get('/api/feedback', async (req, res) => {
  try {
    const feedback = await client.feedback.list({
      limit: 50,
      search: req.query.search as string,
    });
    res.json(feedback);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run dev

# Run tests
npm test

# Lint
npm run lint

# Format
npm run format
```

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://docs.compass.example.com
- Issues: https://github.com/compass/compass-typescript-sdk/issues
- Email: support@compass.example.com
