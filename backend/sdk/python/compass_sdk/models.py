"""
Compass SDK Data Models

Type-safe Pydantic models for API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


class RoadmapStatus(str, Enum):
    """Roadmap item status"""
    PROPOSED = "proposed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"


class WebhookEvent(str, Enum):
    """Webhook event types"""
    FEEDBACK_CREATED = "feedback.created"
    CLUSTER_CREATED = "cluster.created"
    ROADMAP_UPDATED = "roadmap.updated"
    PRIORITY_CHANGED = "priority.changed"


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class Source(BaseModel):
    """Feedback source"""
    id: int
    name: str
    source_type: str
    is_active: bool
    created_at: datetime
    last_synced_at: Optional[datetime] = None
    feedback_count: int = 0

    class Config:
        from_attributes = True


class Feedback(BaseModel):
    """Customer feedback"""
    id: int
    text: str
    customer_name: Optional[str] = None
    customer_revenue: Optional[float] = None
    sentiment_score: Optional[float] = None
    submitted_at: datetime
    source_name: str
    cluster_id: Optional[int] = None

    class Config:
        from_attributes = True


class Cluster(BaseModel):
    """Feedback cluster"""
    id: int
    label: str
    size: int
    priority_score: float
    total_revenue: float
    avg_sentiment: float
    created_at: datetime

    class Config:
        from_attributes = True


class ClusterDetail(Cluster):
    """Cluster with feedback"""
    feedback: List[Feedback] = Field(default_factory=list)


class RoadmapItem(BaseModel):
    """Roadmap item"""
    id: int
    title: str
    rank: int
    priority_score: float
    request_count: int
    impacted_revenue: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Stats(BaseModel):
    """Dashboard statistics"""
    total_feedback: int
    total_sources: int
    total_clusters: int
    total_roadmap_items: int
    total_revenue_impact: float
    avg_sentiment: float
    recent_feedback_30d: int
    timestamp: str


class APIKey(BaseModel):
    """API key"""
    id: int
    name: str
    key: Optional[str] = None  # Only returned on creation
    key_prefix: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Webhook(BaseModel):
    """Webhook configuration"""
    id: int
    url: str
    events: List[str]
    is_active: bool
    status: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    last_delivery_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response"""
    data: List[dict]
    meta: PaginationMeta
