"""
Compass API Client

Main client for interacting with the Compass API.
"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import (
    Source, Feedback, Cluster, ClusterDetail, RoadmapItem, Stats,
    APIKey, Webhook, PaginationMeta, SortOrder, RoadmapStatus, WebhookEvent
)
from .exceptions import (
    CompassAPIError, CompassAuthenticationError, CompassNotFoundError,
    CompassRateLimitError, CompassValidationError
)


class ResourceClient:
    """Base class for resource-specific clients"""

    def __init__(self, client: "CompassClient"):
        self.client = client

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make HTTP request"""
        return self.client._request(method, path, **kwargs)


class SourcesClient(ResourceClient):
    """Client for sources endpoints"""

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        List all feedback sources.

        Args:
            limit: Number of items to return (max 1000)
            offset: Number of items to skip
            is_active: Filter by active status

        Returns:
            Dictionary with 'data' (list of sources) and 'meta' (pagination info)
        """
        params = {"limit": limit, "offset": offset}
        if is_active is not None:
            params["is_active"] = is_active

        return self._request("GET", "/api/v1/sources", params=params)

    def sync(self) -> Dict[str, Any]:
        """
        Sync feedback from all active sources.

        Returns:
            Sync results including number of items synced
        """
        return self._request("POST", "/api/v1/sources/sync")


class FeedbackClient(ResourceClient):
    """Client for feedback endpoints"""

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        source_id: Optional[int] = None,
        cluster_id: Optional[int] = None,
        min_sentiment: Optional[float] = None,
        max_sentiment: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: str = "submitted_at",
        sort_order: SortOrder = SortOrder.DESC
    ) -> Dict[str, Any]:
        """
        List feedback with filtering and pagination.

        Args:
            limit: Number of items to return (max 1000)
            offset: Number of items to skip
            source_id: Filter by source ID
            cluster_id: Filter by cluster ID (-1 for unclustered)
            min_sentiment: Minimum sentiment score (-1 to 1)
            max_sentiment: Maximum sentiment score (-1 to 1)
            search: Search in feedback text
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            Dictionary with 'data' (list of feedback) and 'meta' (pagination info)
        """
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_order": sort_order.value
        }

        if source_id is not None:
            params["source_id"] = source_id
        if cluster_id is not None:
            params["cluster_id"] = cluster_id
        if min_sentiment is not None:
            params["min_sentiment"] = min_sentiment
        if max_sentiment is not None:
            params["max_sentiment"] = max_sentiment
        if search:
            params["search"] = search

        return self._request("GET", "/api/v1/feedback", params=params)

    def get(self, feedback_id: int) -> Feedback:
        """
        Get a specific feedback item.

        Args:
            feedback_id: Feedback ID

        Returns:
            Feedback object
        """
        response = self._request("GET", f"/api/v1/feedback/{feedback_id}")
        return Feedback(**response)


class ClustersClient(ResourceClient):
    """Client for clusters endpoints"""

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        min_size: Optional[int] = None,
        sort_by: str = "priority_score",
        sort_order: SortOrder = SortOrder.DESC
    ) -> Dict[str, Any]:
        """
        List clusters with filtering and pagination.

        Args:
            limit: Number of items to return (max 1000)
            offset: Number of items to skip
            min_size: Minimum cluster size
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            Dictionary with 'data' (list of clusters) and 'meta' (pagination info)
        """
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_order": sort_order.value
        }

        if min_size is not None:
            params["min_size"] = min_size

        return self._request("GET", "/api/v1/clusters", params=params)

    def get(self, cluster_id: int) -> ClusterDetail:
        """
        Get cluster with all feedback.

        Args:
            cluster_id: Cluster ID

        Returns:
            ClusterDetail object with feedback
        """
        response = self._request("GET", f"/api/v1/clusters/{cluster_id}")
        return ClusterDetail(**response)

    def run_clustering(
        self,
        eps: float = 0.5,
        min_samples: int = 3
    ) -> Dict[str, Any]:
        """
        Run NLP clustering on all feedback.

        Args:
            eps: DBSCAN epsilon parameter (0.1-1.0)
            min_samples: DBSCAN min_samples parameter (2-10)

        Returns:
            Clustering results
        """
        params = {"eps": eps, "min_samples": min_samples}
        return self._request("POST", "/api/v1/clustering/run", params=params)


class RoadmapClient(ResourceClient):
    """Client for roadmap endpoints"""

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[RoadmapStatus] = None
    ) -> Dict[str, Any]:
        """
        List roadmap items with pagination.

        Args:
            limit: Number of items to return (max 1000)
            offset: Number of items to skip
            status: Filter by status

        Returns:
            Dictionary with 'data' (list of roadmap items) and 'meta' (pagination info)
        """
        params = {"limit": limit, "offset": offset}

        if status:
            params["status"] = status.value

        return self._request("GET", "/api/v1/roadmap", params=params)

    def get(self, item_id: int) -> RoadmapItem:
        """
        Get a specific roadmap item.

        Args:
            item_id: Roadmap item ID

        Returns:
            RoadmapItem object
        """
        response = self._request("GET", f"/api/v1/roadmap/{item_id}")
        return RoadmapItem(**response)

    def update(
        self,
        item_id: int,
        status: Optional[RoadmapStatus] = None,
        estimated_effort: Optional[str] = None,
        estimated_value: Optional[str] = None
    ) -> RoadmapItem:
        """
        Update roadmap item.

        Args:
            item_id: Roadmap item ID
            status: New status
            estimated_effort: Estimated effort (small, medium, large)
            estimated_value: Estimated value (low, medium, high)

        Returns:
            Updated RoadmapItem object
        """
        data = {}
        if status:
            data["status"] = status.value
        if estimated_effort:
            data["estimated_effort"] = estimated_effort
        if estimated_value:
            data["estimated_value"] = estimated_value

        response = self._request("PATCH", f"/api/v1/roadmap/{item_id}", json=data)
        return RoadmapItem(**response)

    def generate(self) -> Dict[str, Any]:
        """
        Generate prioritized roadmap from clusters.

        Returns:
            Generation results with insights
        """
        return self._request("POST", "/api/v1/roadmap/generate")


class APIKeysClient(ResourceClient):
    """Client for API keys endpoints"""

    def create(
        self,
        name: str,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """
        Create a new API key.

        Args:
            name: Descriptive name for the API key
            expires_in_days: Days until expiration (None = never expires)

        Returns:
            APIKey object (with 'key' field - save it!)
        """
        data = {"name": name}
        if expires_in_days:
            data["expires_in_days"] = expires_in_days

        response = self._request("POST", "/api/v1/api-keys", json=data)
        return APIKey(**response)

    def list(self) -> List[APIKey]:
        """
        List all API keys.

        Returns:
            List of APIKey objects (without actual keys)
        """
        response = self._request("GET", "/api/v1/api-keys")
        return [APIKey(**key) for key in response["data"]]

    def revoke(self, key_id: int) -> Dict[str, Any]:
        """
        Revoke (deactivate) an API key.

        Args:
            key_id: API key ID

        Returns:
            Status message
        """
        return self._request("DELETE", f"/api/v1/api-keys/{key_id}")


class WebhooksClient(ResourceClient):
    """Client for webhooks endpoints"""

    def create(
        self,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a new webhook.

        Args:
            url: Webhook URL to POST events to
            events: List of events to subscribe to
            secret: Secret for HMAC signature (auto-generated if not provided)

        Returns:
            Webhook object
        """
        data = {
            "url": url,
            "events": [e.value for e in events]
        }
        if secret:
            data["secret"] = secret

        response = self._request("POST", "/api/v1/webhooks", json=data)
        return Webhook(**response)

    def list(self) -> List[Webhook]:
        """
        List all webhooks.

        Returns:
            List of Webhook objects
        """
        response = self._request("GET", "/api/v1/webhooks")
        return [Webhook(**w) for w in response["data"]]

    def get(self, webhook_id: int) -> Webhook:
        """
        Get a specific webhook.

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook object
        """
        response = self._request("GET", f"/api/v1/webhooks/{webhook_id}")
        return Webhook(**response)

    def update(
        self,
        webhook_id: int,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        is_active: Optional[bool] = None
    ) -> Webhook:
        """
        Update webhook configuration.

        Args:
            webhook_id: Webhook ID
            url: New webhook URL
            events: New list of events
            is_active: Activate/deactivate webhook

        Returns:
            Updated Webhook object
        """
        data = {}
        if url:
            data["url"] = url
        if events:
            data["events"] = [e.value for e in events]
        if is_active is not None:
            data["is_active"] = is_active

        response = self._request("PATCH", f"/api/v1/webhooks/{webhook_id}", json=data)
        return Webhook(**response)

    def delete(self, webhook_id: int) -> Dict[str, Any]:
        """
        Delete a webhook.

        Args:
            webhook_id: Webhook ID

        Returns:
            Status message
        """
        return self._request("DELETE", f"/api/v1/webhooks/{webhook_id}")

    def deliveries(
        self,
        webhook_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get webhook delivery history.

        Args:
            webhook_id: Webhook ID
            limit: Number of items to return
            offset: Number of items to skip

        Returns:
            Dictionary with delivery logs
        """
        params = {"limit": limit, "offset": offset}
        return self._request("GET", f"/api/v1/webhooks/{webhook_id}/deliveries", params=params)


class CompassClient:
    """
    Compass API Client

    Main client for interacting with the Compass Customer Feedback Intelligence Platform.

    Example:
        >>> client = CompassClient(api_key="your-api-key")
        >>> sources = client.sources.list()
        >>> feedback = client.feedback.list(limit=50, search="mobile app")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0
    ):
        """
        Initialize Compass client.

        Args:
            api_key: Your Compass API key
            base_url: Base URL of the Compass API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "User-Agent": "compass-python-sdk/1.0.0"
            },
            timeout=timeout
        )

        # Initialize resource clients
        self.sources = SourcesClient(self)
        self.feedback = FeedbackClient(self)
        self.clusters = ClustersClient(self)
        self.roadmap = RoadmapClient(self)
        self.api_keys = APIKeysClient(self)
        self.webhooks = WebhooksClient(self)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """
        Make HTTP request to API.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional arguments for httpx

        Returns:
            Response JSON

        Raises:
            CompassAPIError: On API errors
        """
        try:
            response = self.client.request(method, path, **kwargs)

            # Handle errors
            if response.status_code == 401:
                raise CompassAuthenticationError(
                    "Authentication failed. Check your API key.",
                    status_code=401,
                    response=response.json() if response.content else None
                )
            elif response.status_code == 404:
                raise CompassNotFoundError(
                    "Resource not found",
                    status_code=404,
                    response=response.json() if response.content else None
                )
            elif response.status_code == 429:
                raise CompassRateLimitError(
                    "Rate limit exceeded. Please slow down.",
                    status_code=429,
                    response=response.json() if response.content else None
                )
            elif response.status_code == 422:
                raise CompassValidationError(
                    "Validation error",
                    status_code=422,
                    response=response.json() if response.content else None
                )
            elif not response.is_success:
                error_data = response.json() if response.content else {}
                raise CompassAPIError(
                    error_data.get("error", "Unknown error"),
                    status_code=response.status_code,
                    response=error_data
                )

            return response.json()

        except httpx.RequestError as e:
            raise CompassAPIError(f"Request failed: {str(e)}")

    def stats(self) -> Stats:
        """
        Get dashboard statistics.

        Returns:
            Stats object
        """
        response = self._request("GET", "/api/v1/stats")
        return Stats(**response)

    def close(self):
        """Close HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
