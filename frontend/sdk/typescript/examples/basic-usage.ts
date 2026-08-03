/**
 * Compass SDK - Basic Usage Example (TypeScript)
 *
 * Demonstrates basic operations with the Compass API.
 */

import { CompassClient, SortOrder } from '../src';

// Initialize client
const client = new CompassClient({
  apiKey: 'compass_your_api_key_here',
  baseUrl: 'http://localhost:8000',
});

async function main() {
  console.log('='.repeat(60));
  console.log('Compass SDK - Basic Usage Example');
  console.log('='.repeat(60));

  try {
    // 1. Get dashboard statistics
    console.log('\n1. Dashboard Statistics');
    console.log('-'.repeat(40));
    const stats = await client.stats();
    console.log(`Total Feedback: ${stats.total_feedback}`);
    console.log(`Total Sources: ${stats.total_sources}`);
    console.log(`Total Clusters: ${stats.total_clusters}`);
    console.log(`Total Roadmap Items: ${stats.total_roadmap_items}`);
    console.log(`Revenue Impact: $${stats.total_revenue_impact.toLocaleString()}`);
    console.log(`Average Sentiment: ${stats.avg_sentiment.toFixed(3)}`);
    console.log(`Recent Feedback (30d): ${stats.recent_feedback_30d}`);

    // 2. List sources
    console.log('\n2. Feedback Sources');
    console.log('-'.repeat(40));
    const sourcesResponse = await client.sources.list({ limit: 10 });
    sourcesResponse.data.forEach((source) => {
      const status = source.is_active ? '✓ Active' : '✗ Inactive';
      console.log(`${status} ${source.name}: ${source.feedback_count} items`);
    });

    // 3. List recent feedback
    console.log('\n3. Recent Feedback');
    console.log('-'.repeat(40));
    const feedbackResponse = await client.feedback.list({
      limit: 5,
      sort_by: 'submitted_at',
      sort_order: SortOrder.DESC,
    });
    feedbackResponse.data.forEach((fb) => {
      const sentiment =
        fb.sentiment_score! > 0.5 ? '😊' : fb.sentiment_score! > 0 ? '😐' : '😞';
      console.log(
        `${sentiment} [${fb.customer_name}] ${fb.text.slice(0, 80)}...`
      );
      console.log(
        `   Source: ${fb.source_name}, Sentiment: ${fb.sentiment_score?.toFixed(2)}`
      );
    });

    // 4. List top clusters
    console.log('\n4. Top Priority Clusters');
    console.log('-'.repeat(40));
    const clustersResponse = await client.clusters.list({
      limit: 5,
      sort_by: 'priority_score',
      sort_order: SortOrder.DESC,
    });
    clustersResponse.data.forEach((cluster, i) => {
      console.log(`${i + 1}. ${cluster.label}`);
      console.log(
        `   Size: ${cluster.size}, Priority: ${cluster.priority_score.toFixed(2)}`
      );
      console.log(
        `   Revenue: $${cluster.total_revenue.toLocaleString()}, Sentiment: ${cluster.avg_sentiment.toFixed(2)}`
      );
    });

    // 5. Get cluster details
    if (clustersResponse.data.length > 0) {
      console.log('\n5. Cluster Details (First Cluster)');
      console.log('-'.repeat(40));
      const clusterId = clustersResponse.data[0].id;
      const cluster = await client.clusters.get(clusterId);
      console.log(`Label: ${cluster.label}`);
      console.log(`Size: ${cluster.size} feedback items`);
      console.log('\nSample feedback:');
      cluster.feedback.slice(0, 3).forEach((fb) => {
        console.log(`  - ${fb.text.slice(0, 100)}`);
      });
    }

    // 6. List roadmap
    console.log('\n6. Product Roadmap (Top 5)');
    console.log('-'.repeat(40));
    const roadmapResponse = await client.roadmap.list({ limit: 5 });
    roadmapResponse.data.forEach((item) => {
      const statusEmoji: Record<string, string> = {
        proposed: '💡',
        planned: '📋',
        in_progress: '🚧',
        shipped: '✅',
      };
      const emoji = statusEmoji[item.status] || '❓';
      console.log(`#${item.rank} ${emoji} ${item.title}`);
      console.log(
        `   Priority: ${item.priority_score.toFixed(2)}, Requests: ${item.request_count}`
      );
      console.log(
        `   Revenue Impact: $${item.impacted_revenue.toLocaleString()}`
      );
    });

    console.log('\n' + '='.repeat(60));
    console.log('Example completed successfully!');
    console.log('='.repeat(60));
  } catch (error) {
    console.error('\nError:', error);
  }
}

main();
