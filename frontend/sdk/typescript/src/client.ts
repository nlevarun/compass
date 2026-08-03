/**
 * Compass API Client
 *
 * Main client for interacting with the Compass API.
 */

import {
  CompassConfig,
  DEFAULT_CONFIG,
} from './config';
import {
  PaginatedResponse,
  Source,
  Feedback,
  Cluster,
  ClusterDetail,
  RoadmapItem,
  Stats,
  APIKey,
  Webhook,
  WebhookDelivery,
  SourcesListParams,
  FeedbackListParams,
  ClustersListParams,
  RoadmapListParams,
  ClusteringParams,
  RoadmapUpdateData,
  APIKeyCreateData,
  WebhookCreateData,
  WebhookUpdateData,
  SyncResult,
  ClusteringResult,
  RoadmapGenerateResult,
  SortOrder,
  RoadmapStatus,
  WebhookEvent,
} from './types';
import {
  CompassAPIError,
  CompassAuthenticationError,
  CompassNotFoundError,
  CompassRateLimitError,
  CompassValidationError,
} from './errors';

/**
 * Base resource client
 */
class ResourceClient {
  constructor(protected client: CompassClient) {}

  protected async request<T>(
    method: string,
    path: string,
    options?: RequestInit
  ): Promise<T> {
    return this.client.request<T>(method, path, options);
  }
}

/**
 * Sources API client
 */
export class SourcesClient extends ResourceClient {
  /**
   * List all feedback sources
   */
  async list(params?: SourcesListParams): Promise<PaginatedResponse<Source>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());
    if (params?.is_active !== undefined) queryParams.set('is_active', params.is_active.toString());

    return this.request<PaginatedResponse<Source>>(
      'GET',
      `/api/v1/sources?${queryParams}`
    );
  }

  /**
   * Sync feedback from all active sources
   */
  async sync(): Promise<SyncResult> {
    return this.request<SyncResult>('POST', '/api/v1/sources/sync');
  }
}

/**
 * Feedback API client
 */
export class FeedbackClient extends ResourceClient {
  /**
   * List feedback with filtering and pagination
   */
  async list(params?: FeedbackListParams): Promise<PaginatedResponse<Feedback>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());
    if (params?.source_id) queryParams.set('source_id', params.source_id.toString());
    if (params?.cluster_id !== undefined) queryParams.set('cluster_id', params.cluster_id.toString());
    if (params?.min_sentiment !== undefined) queryParams.set('min_sentiment', params.min_sentiment.toString());
    if (params?.max_sentiment !== undefined) queryParams.set('max_sentiment', params.max_sentiment.toString());
    if (params?.search) queryParams.set('search', params.search);
    if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.set('sort_order', params.sort_order);

    return this.request<PaginatedResponse<Feedback>>(
      'GET',
      `/api/v1/feedback?${queryParams}`
    );
  }

  /**
   * Get a specific feedback item
   */
  async get(feedbackId: number): Promise<Feedback> {
    return this.request<Feedback>('GET', `/api/v1/feedback/${feedbackId}`);
  }
}

/**
 * Clusters API client
 */
export class ClustersClient extends ResourceClient {
  /**
   * List clusters with filtering and pagination
   */
  async list(params?: ClustersListParams): Promise<PaginatedResponse<Cluster>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());
    if (params?.min_size) queryParams.set('min_size', params.min_size.toString());
    if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.set('sort_order', params.sort_order);

    return this.request<PaginatedResponse<Cluster>>(
      'GET',
      `/api/v1/clusters?${queryParams}`
    );
  }

  /**
   * Get cluster with all feedback
   */
  async get(clusterId: number): Promise<ClusterDetail> {
    return this.request<ClusterDetail>('GET', `/api/v1/clusters/${clusterId}`);
  }

  /**
   * Run NLP clustering on all feedback
   */
  async runClustering(params?: ClusteringParams): Promise<ClusteringResult> {
    const queryParams = new URLSearchParams();
    if (params?.eps) queryParams.set('eps', params.eps.toString());
    if (params?.min_samples) queryParams.set('min_samples', params.min_samples.toString());

    return this.request<ClusteringResult>(
      'POST',
      `/api/v1/clustering/run?${queryParams}`
    );
  }
}

/**
 * Roadmap API client
 */
export class RoadmapClient extends ResourceClient {
  /**
   * List roadmap items with pagination
   */
  async list(params?: RoadmapListParams): Promise<PaginatedResponse<RoadmapItem>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());
    if (params?.status) queryParams.set('status', params.status);

    return this.request<PaginatedResponse<RoadmapItem>>(
      'GET',
      `/api/v1/roadmap?${queryParams}`
    );
  }

  /**
   * Get a specific roadmap item
   */
  async get(itemId: number): Promise<RoadmapItem> {
    return this.request<RoadmapItem>('GET', `/api/v1/roadmap/${itemId}`);
  }

  /**
   * Update roadmap item
   */
  async update(itemId: number, data: RoadmapUpdateData): Promise<RoadmapItem> {
    return this.request<RoadmapItem>('PATCH', `/api/v1/roadmap/${itemId}`, {
      body: JSON.stringify(data),
    });
  }

  /**
   * Generate prioritized roadmap from clusters
   */
  async generate(): Promise<RoadmapGenerateResult> {
    return this.request<RoadmapGenerateResult>('POST', '/api/v1/roadmap/generate');
  }
}

/**
 * API Keys client
 */
export class APIKeysClient extends ResourceClient {
  /**
   * Create a new API key
   */
  async create(data: APIKeyCreateData): Promise<APIKey> {
    return this.request<APIKey>('POST', '/api/v1/api-keys', {
      body: JSON.stringify(data),
    });
  }

  /**
   * List all API keys
   */
  async list(): Promise<APIKey[]> {
    const response = await this.request<{ data: APIKey[] }>('GET', '/api/v1/api-keys');
    return response.data;
  }

  /**
   * Revoke (deactivate) an API key
   */
  async revoke(keyId: number): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>(
      'DELETE',
      `/api/v1/api-keys/${keyId}`
    );
  }
}

/**
 * Webhooks client
 */
export class WebhooksClient extends ResourceClient {
  /**
   * Create a new webhook
   */
  async create(data: WebhookCreateData): Promise<Webhook> {
    return this.request<Webhook>('POST', '/api/v1/webhooks', {
      body: JSON.stringify(data),
    });
  }

  /**
   * List all webhooks
   */
  async list(): Promise<Webhook[]> {
    const response = await this.request<{ data: Webhook[] }>('GET', '/api/v1/webhooks');
    return response.data;
  }

  /**
   * Get a specific webhook
   */
  async get(webhookId: number): Promise<Webhook> {
    return this.request<Webhook>('GET', `/api/v1/webhooks/${webhookId}`);
  }

  /**
   * Update webhook configuration
   */
  async update(webhookId: number, data: WebhookUpdateData): Promise<Webhook> {
    return this.request<Webhook>('PATCH', `/api/v1/webhooks/${webhookId}`, {
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete a webhook
   */
  async delete(webhookId: number): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>(
      'DELETE',
      `/api/v1/webhooks/${webhookId}`
    );
  }

  /**
   * Get webhook delivery history
   */
  async deliveries(
    webhookId: number,
    params?: { limit?: number; offset?: number }
  ): Promise<PaginatedResponse<WebhookDelivery>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());

    return this.request<PaginatedResponse<WebhookDelivery>>(
      'GET',
      `/api/v1/webhooks/${webhookId}/deliveries?${queryParams}`
    );
  }
}

/**
 * Main Compass API Client
 *
 * @example
 * ```typescript
 * const client = new CompassClient({
 *   apiKey: 'your-api-key',
 *   baseUrl: 'http://localhost:8000'
 * });
 *
 * const stats = await client.stats();
 * console.log(`Total feedback: ${stats.total_feedback}`);
 *
 * const feedback = await client.feedback.list({ limit: 50 });
 * console.log(`Found ${feedback.data.length} items`);
 * ```
 */
export class CompassClient {
  private config: Required<CompassConfig>;

  public sources: SourcesClient;
  public feedback: FeedbackClient;
  public clusters: ClustersClient;
  public roadmap: RoadmapClient;
  public apiKeys: APIKeysClient;
  public webhooks: WebhooksClient;

  constructor(config: CompassConfig) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
      baseUrl: config.baseUrl?.replace(/\/$/, '') || DEFAULT_CONFIG.baseUrl!,
    } as Required<CompassConfig>;

    // Initialize resource clients
    this.sources = new SourcesClient(this);
    this.feedback = new FeedbackClient(this);
    this.clusters = new ClustersClient(this);
    this.roadmap = new RoadmapClient(this);
    this.apiKeys = new APIKeysClient(this);
    this.webhooks = new WebhooksClient(this);
  }

  /**
   * Make HTTP request to API
   */
  async request<T>(
    method: string,
    path: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': this.config.apiKey,
      'User-Agent': 'compass-typescript-sdk/1.0.0',
      ...this.config.headers,
      ...((options?.headers as Record<string, string>) || {}),
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(url, {
        ...options,
        method,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        switch (response.status) {
          case 401:
            throw new CompassAuthenticationError(
              errorData.error || 'Authentication failed',
              errorData
            );
          case 404:
            throw new CompassNotFoundError(
              errorData.error || 'Resource not found',
              errorData
            );
          case 429:
            throw new CompassRateLimitError(
              errorData.error || 'Rate limit exceeded',
              errorData
            );
          case 422:
            throw new CompassValidationError(
              errorData.error || 'Validation error',
              errorData
            );
          default:
            throw new CompassAPIError(
              errorData.error || 'Unknown error',
              response.status,
              errorData
            );
        }
      }

      return response.json();
    } catch (error) {
      if (error instanceof CompassAPIError) {
        throw error;
      }
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new CompassAPIError('Request timeout');
        }
        throw new CompassAPIError(`Request failed: ${error.message}`);
      }
      throw new CompassAPIError('Unknown error occurred');
    }
  }

  /**
   * Get dashboard statistics
   */
  async stats(): Promise<Stats> {
    return this.request<Stats>('GET', '/api/v1/stats');
  }
}
