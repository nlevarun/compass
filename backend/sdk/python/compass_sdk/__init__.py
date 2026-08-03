"""
Compass Python SDK

Official Python client for the Compass Customer Feedback Intelligence Platform API.

Example usage:
    >>> from compass_sdk import CompassClient
    >>> client = CompassClient(api_key="your-api-key", base_url="http://localhost:8000")
    >>> feedback = client.feedback.list(limit=10)
    >>> print(f"Found {len(feedback)} feedback items")
"""

from .client import CompassClient
from .models import (
    Source,
    Feedback,
    Cluster,
    RoadmapItem,
    WebhookEvent,
    RoadmapStatus
)
from .exceptions import (
    CompassAPIError,
    CompassAuthenticationError,
    CompassNotFoundError,
    CompassRateLimitError
)

__version__ = "1.0.0"
__all__ = [
    "CompassClient",
    "Source",
    "Feedback",
    "Cluster",
    "RoadmapItem",
    "WebhookEvent",
    "RoadmapStatus",
    "CompassAPIError",
    "CompassAuthenticationError",
    "CompassNotFoundError",
    "CompassRateLimitError",
]
