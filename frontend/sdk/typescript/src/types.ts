/**
 * Compass API Types
 *
 * TypeScript type definitions for all API models and responses.
 */

export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc',
}

export enum RoadmapStatus {
  PROPOSED = 'proposed',
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  SHIPPED = 'shipped',
}

export enum WebhookEvent {
  FEEDBACK_CREATED = 'feedback.created',
  CLUSTER_CREATED = 'cluster.created',
  ROADMAP_UPDATED = 'roadmap.updated',
  PRIORITY_CHANGED = 'priority.changed',
}

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface Source {
  id: number;
  name: string;
  source_type: string;
  is_active: boolean;
  created_at: string;
  last_synced_at: string | null;
  feedback_count: number;
}

export interface Feedback {
  id: number;
  text: string;
  customer_name: string | null;
  customer_revenue: number | null;
  sentiment_score: number | null;
  submitted_at: string;
  source_name: string;
  cluster_id: number | null;
}

export interface Cluster {
  id: number;
  label: string;
  size: number;
  priority_score: number;
  total_revenue: number;
  avg_sentiment: number;
  created_at: string;
}

export interface ClusterDetail extends Cluster {
  feedback: Feedback[];
}

export interface RoadmapItem {
  id: number;
  title: string;
  rank: number;
  priority_score: number;
  request_count: number;
  impacted_revenue: number;
  status: string;
  created_at: string;
}

export interface Stats {
  total_feedback: number;
  total_sources: number;
  total_clusters: number;
  total_roadmap_items: number;
  total_revenue_impact: number;
  avg_sentiment: number;
  recent_feedback_30d: number;
  timestamp: string;
}

export interface APIKey {
  id: number;
  name: string;
  key?: string; // Only returned on creation
  key_prefix: string;
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
}

export interface Webhook {
  id: number;
  url: string;
  events: string[];
  is_active: boolean;
  status: string;
  total_deliveries: number;
  successful_deliveries: number;
  failed_deliveries: number;
  last_delivery_at: string | null;
  created_at: string;
}

export interface WebhookDelivery {
  id: number;
  webhook_id: number;
  event_type: string;
  status_code: number | null;
  success: boolean;
  attempt: number;
  created_at: string;
  delivered_at: string | null;
  duration_ms: number | null;
  error_message: string | null;
}

// Request types
export interface SourcesListParams {
  limit?: number;
  offset?: number;
  is_active?: boolean;
}

export interface FeedbackListParams {
  limit?: number;
  offset?: number;
  source_id?: number;
  cluster_id?: number;
  min_sentiment?: number;
  max_sentiment?: number;
  search?: string;
  sort_by?: string;
  sort_order?: SortOrder;
}

export interface ClustersListParams {
  limit?: number;
  offset?: number;
  min_size?: number;
  sort_by?: string;
  sort_order?: SortOrder;
}

export interface RoadmapListParams {
  limit?: number;
  offset?: number;
  status?: RoadmapStatus;
}

export interface ClusteringParams {
  eps?: number;
  min_samples?: number;
}

export interface RoadmapUpdateData {
  status?: RoadmapStatus;
  estimated_effort?: string;
  estimated_value?: string;
}

export interface APIKeyCreateData {
  name: string;
  expires_in_days?: number;
}

export interface WebhookCreateData {
  url: string;
  events: WebhookEvent[];
  secret?: string;
}

export interface WebhookUpdateData {
  url?: string;
  events?: WebhookEvent[];
  is_active?: boolean;
}

export interface SyncResult {
  total_synced: number;
  sources_synced: number;
  results: Array<{
    source: string;
    synced: number;
    status: string;
    error?: string;
  }>;
  elapsed_time: number;
}

export interface ClusteringResult {
  status: string;
  feedback_clustered: number;
  clusters_created: number;
  noise_points: number;
  metrics: Record<string, any>;
  elapsed_time: number;
}

export interface RoadmapGenerateResult {
  status: string;
  items_generated: number;
  insights: Record<string, any>;
  elapsed_time: number;
}
