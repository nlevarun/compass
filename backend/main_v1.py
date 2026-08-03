"""
Compass FastAPI Application - Enhanced API v1
API-first design with versioning, pagination, filtering, rate limiting, and comprehensive error handling.

Endpoints:
- GET /api/v1/sources - List all feedback sources (paginated, filterable)
- POST /api/v1/sources/sync - Sync feedback from all sources
- GET /api/v1/feedback - Get all feedback (paginated, filterable, searchable)
- POST /api/v1/clustering/run - Run NLP clustering on feedback
- GET /api/v1/clusters - Get all clusters (paginated, sortable)
- GET /api/v1/clusters/{id} - Get specific cluster with feedback
- POST /api/v1/roadmap/generate - Generate prioritized roadmap
- GET /api/v1/roadmap - Get current roadmap (paginated)
- PATCH /api/v1/roadmap/{id} - Update roadmap item status
- GET /api/v1/stats - Get dashboard statistics
- POST /api/v1/api-keys - Create API key
- GET /api/v1/api-keys - List API keys
- DELETE /api/v1/api-keys/{id} - Revoke API key
"""

from fastapi import FastAPI, Depends, HTTPException, Query, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import secrets
import hashlib
import hmac

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from database import get_db_session, get_db, init_db
from models import Source, Feedback, Cluster, RoadmapItem, Base
from ingestion.sources import create_source, MOCK_SOURCES
from nlp.clustering import FeedbackClusterer
from nlp.sentiment import SentimentAnalyzer
from priority.calculator import PriorityCalculator, generate_priority_insights

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Compass API",
    description="Customer Feedback Intelligence Platform - API-first with comprehensive developer experience",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Key Authentication ---

# Create APIKey model
class APIKey(Base):
    """API key for authentication"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    key_hash = Column(String(64), nullable=False, unique=True)
    key_prefix = Column(String(12), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

from sqlalchemy import Column, Integer, String, Boolean, DateTime

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: Optional[str] = Depends(api_key_header), db: Session = Depends(get_db_session)):
    """Validate API key authentication (optional - for public endpoints)."""
    if not api_key:
        return None

    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Look up in database
    db_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )

    # Check expiration
    if db_key.expires_at and db_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )

    # Update last used
    db_key.last_used_at = datetime.utcnow()
    db.commit()

    return db_key


async def require_api_key(api_key: APIKey = Depends(get_api_key)):
    """Require valid API key (for protected endpoints)."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    return api_key


# --- Enums ---

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class RoadmapStatus(str, Enum):
    proposed = "proposed"
    planned = "planned"
    in_progress = "in_progress"
    shipped = "shipped"


# --- Enhanced Pydantic Models ---

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    meta: PaginationMeta


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: str = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SourceResponse(BaseModel):
    """Source response model"""
    id: int
    name: str
    source_type: str
    is_active: bool
    created_at: datetime
    last_synced_at: Optional[datetime]
    feedback_count: int

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    """Feedback response model"""
    id: int
    text: str
    customer_name: Optional[str]
    customer_revenue: Optional[float]
    sentiment_score: Optional[float]
    submitted_at: datetime
    source_name: str
    cluster_id: Optional[int]

    class Config:
        from_attributes = True


class ClusterResponse(BaseModel):
    """Cluster response model"""
    id: int
    label: str
    size: int
    priority_score: float
    total_revenue: float
    avg_sentiment: float
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    """Roadmap response model"""
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


class RoadmapUpdateRequest(BaseModel):
    """Request to update roadmap item"""
    status: Optional[RoadmapStatus] = None
    estimated_effort: Optional[str] = None
    estimated_value: Optional[str] = None


class APIKeyCreateRequest(BaseModel):
    """Request to create API key"""
    name: str = Field(..., description="Descriptive name for the API key", min_length=1, max_length=200)
    expires_in_days: Optional[int] = Field(None, description="Days until expiration (null = never)", ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response (only shows key on creation)"""
    id: int
    name: str
    key: Optional[str] = Field(None, description="Only returned on creation")
    key_prefix: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Initialization ---

@app.on_event("startup")
async def startup_event():
    """Initialize database and create mock sources."""
    print("🚀 Starting Compass API v1...")
    init_db()

    # Create api_keys table if it doesn't exist
    from sqlalchemy import create_engine
    from database import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    # Create mock sources if they don't exist
    with get_db() as db:
        existing_sources = db.query(Source).count()
        if existing_sources == 0:
            print("Creating mock sources...")
            for source_name, config in MOCK_SOURCES.items():
                source = Source(
                    name=source_name,
                    source_type="mock",
                    is_active=True,
                    config=config
                )
                db.add(source)

            # Add Slack source (initially inactive)
            slack_source = Source(
                name="Slack",
                source_type="real",
                is_active=False,
                config={"token": None, "channel_ids": []}
            )
            db.add(slack_source)

            db.commit()
            print(f"✓ Created {db.query(Source).count()} sources")

    print("✓ Compass API v1 ready!")


# --- API Endpoints v1 ---

@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Health check endpoint."""
    return {
        "service": "Compass API",
        "version": "1.0.0",
        "status": "healthy",
        "api_version": "v1",
        "docs": "/api/v1/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/sources")
@limiter.limit("60/minute")
async def get_sources(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """
    Get all feedback sources with pagination and filtering.

    - **limit**: Number of items to return (max 1000)
    - **offset**: Number of items to skip for pagination
    - **is_active**: Filter by active status
    """
    query = db.query(Source)

    # Apply filters
    if is_active is not None:
        query = query.filter(Source.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    sources = query.order_by(Source.created_at.desc()).limit(limit).offset(offset).all()

    # Build response with feedback counts
    data = []
    for source in sources:
        feedback_count = db.query(Feedback).filter(Feedback.source_id == source.id).count()
        data.append({
            "id": source.id,
            "name": source.name,
            "source_type": source.source_type,
            "is_active": source.is_active,
            "created_at": source.created_at,
            "last_synced_at": source.last_synced_at,
            "feedback_count": feedback_count
        })

    return {
        "data": data,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }
    }


@app.post("/api/v1/sources/sync")
@limiter.limit("10/minute")
async def sync_sources(
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """
    Sync feedback from all active sources.
    Requires API key authentication.
    """
    start_time = time.time()

    sources = db.query(Source).filter(Source.is_active == True).all()

    total_synced = 0
    results = []

    for source_model in sources:
        try:
            # Create source instance
            source = create_source(source_model)

            # Fetch feedback
            feedback_data = source.fetch_feedback(since=source_model.last_synced_at)

            # Save to database
            for fb_data in feedback_data:
                feedback = Feedback(**fb_data)
                db.add(feedback)

            # Update last synced timestamp
            source_model.last_synced_at = datetime.utcnow()

            db.commit()

            total_synced += len(feedback_data)
            results.append({
                "source": source_model.name,
                "synced": len(feedback_data),
                "status": "success"
            })

        except Exception as e:
            results.append({
                "source": source_model.name,
                "synced": 0,
                "status": "error",
                "error": str(e)
            })

    elapsed_time = time.time() - start_time

    return {
        "total_synced": total_synced,
        "sources_synced": len(sources),
        "results": results,
        "elapsed_time": round(elapsed_time, 2)
    }


@app.get("/api/v1/feedback")
@limiter.limit("60/minute")
async def get_feedback(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    cluster_id: Optional[int] = Query(None, description="Filter by cluster ID (-1 for unclustered)"),
    min_sentiment: Optional[float] = Query(None, ge=-1, le=1, description="Minimum sentiment score"),
    max_sentiment: Optional[float] = Query(None, ge=-1, le=1, description="Maximum sentiment score"),
    search: Optional[str] = Query(None, description="Search in feedback text"),
    sort_by: str = Query("submitted_at", description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order"),
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """
    Get feedback with pagination, filtering, sorting, and search.

    - **limit**: Number of items to return (max 1000)
    - **offset**: Number of items to skip for pagination
    - **source_id**: Filter by source ID
    - **cluster_id**: Filter by cluster ID (-1 for unclustered)
    - **min_sentiment**: Minimum sentiment score (-1 to 1)
    - **max_sentiment**: Maximum sentiment score (-1 to 1)
    - **search**: Search in feedback text (case-insensitive)
    - **sort_by**: Field to sort by (submitted_at, sentiment_score, customer_revenue)
    - **sort_order**: Sort order (asc or desc)
    """
    query = db.query(Feedback).join(Source)

    # Apply filters
    if source_id:
        query = query.filter(Feedback.source_id == source_id)

    if cluster_id is not None:
        if cluster_id == -1:
            query = query.filter(Feedback.cluster_id == None)
        else:
            query = query.filter(Feedback.cluster_id == cluster_id)

    if min_sentiment is not None:
        query = query.filter(Feedback.sentiment_score >= min_sentiment)

    if max_sentiment is not None:
        query = query.filter(Feedback.sentiment_score <= max_sentiment)

    if search:
        query = query.filter(Feedback.text.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Apply sorting
    sort_field = getattr(Feedback, sort_by, Feedback.submitted_at)
    if sort_order == SortOrder.desc:
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))

    # Apply pagination
    feedback_list = query.limit(limit).offset(offset).all()

    # Build response
    data = []
    for fb in feedback_list:
        data.append({
            "id": fb.id,
            "text": fb.text,
            "customer_name": fb.customer_name,
            "customer_revenue": fb.customer_revenue,
            "sentiment_score": fb.sentiment_score,
            "submitted_at": fb.submitted_at,
            "source_name": fb.source.name,
            "cluster_id": fb.cluster_id
        })

    return {
        "data": data,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }
    }


@app.post("/api/v1/clustering/run")
@limiter.limit("5/minute")
async def run_clustering(
    request: Request,
    eps: float = Query(0.5, ge=0.1, le=1.0, description="DBSCAN epsilon parameter"),
    min_samples: int = Query(3, ge=2, le=10, description="DBSCAN min_samples parameter"),
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """
    Run NLP clustering on all feedback.
    Requires API key authentication.

    - **eps**: DBSCAN epsilon parameter (0.1-1.0)
    - **min_samples**: DBSCAN min_samples parameter (2-10)
    """
    start_time = time.time()

    # Get all feedback
    feedback_list = db.query(Feedback).all()

    if len(feedback_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No feedback to cluster. Run sync first."
        )

    # Extract texts
    texts = [fb.text for fb in feedback_list]

    # Initialize clusterer and sentiment analyzer
    clusterer = FeedbackClusterer(eps=eps, min_samples=min_samples)
    sentiment_analyzer = SentimentAnalyzer()

    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} feedback entries...")
    embeddings = clusterer.generate_embeddings(texts)

    # Update sentiment scores (if not already set)
    print("Analyzing sentiment...")
    for fb, text in zip(feedback_list, texts):
        if fb.sentiment_score is None:
            fb.sentiment_score = sentiment_analyzer.analyze(text)
        fb.embedding = json.dumps(embeddings[feedback_list.index(fb)].tolist() if hasattr(embeddings[feedback_list.index(fb)], 'tolist') else embeddings[feedback_list.index(fb)])

    db.commit()

    # Cluster feedback
    print("Clustering feedback...")
    labels, metrics = clusterer.cluster_feedback(texts, embeddings)

    # Clear existing clusters
    db.query(Cluster).delete()
    db.commit()

    # Create new clusters
    cluster_map = {}
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue  # Skip noise

        # Get feedback in this cluster
        cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
        cluster_feedback = [feedback_list[i] for i in cluster_indices]
        cluster_texts = [texts[i] for i in cluster_indices]

        # Generate cluster label
        label_text = clusterer.generate_cluster_label(cluster_texts)

        # Calculate metrics
        total_revenue = sum(fb.customer_revenue or 0 for fb in cluster_feedback)
        avg_sentiment = sum(fb.sentiment_score or 0 for fb in cluster_feedback) / len(cluster_feedback)

        # Calculate centroid
        cluster_embeddings = [embeddings[i] for i in cluster_indices]
        centroid = clusterer.calculate_centroid(cluster_embeddings)

        # Create cluster
        cluster = Cluster(
            label=label_text,
            size=len(cluster_feedback),
            total_revenue=total_revenue,
            avg_sentiment=avg_sentiment,
            centroid=json.dumps(centroid)
        )
        db.add(cluster)
        db.flush()  # Get cluster ID

        cluster_map[cluster_id] = cluster.id

        # Update feedback cluster assignments
        for fb in cluster_feedback:
            fb.cluster_id = cluster.id

    db.commit()

    elapsed_time = time.time() - start_time

    return {
        "status": "success",
        "feedback_clustered": len(feedback_list),
        "clusters_created": len(cluster_map),
        "noise_points": metrics["n_noise"],
        "metrics": metrics,
        "elapsed_time": round(elapsed_time, 2)
    }


@app.get("/api/v1/clusters")
@limiter.limit("60/minute")
async def get_clusters(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    min_size: Optional[int] = Query(None, ge=1, description="Minimum cluster size"),
    sort_by: str = Query("priority_score", description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order"),
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """
    Get all clusters with pagination, filtering, and sorting.

    - **limit**: Number of items to return (max 1000)
    - **offset**: Number of items to skip for pagination
    - **min_size**: Minimum cluster size
    - **sort_by**: Field to sort by (priority_score, size, total_revenue, avg_sentiment)
    - **sort_order**: Sort order (asc or desc)
    """
    query = db.query(Cluster)

    # Apply filters
    if min_size:
        query = query.filter(Cluster.size >= min_size)

    # Get total count
    total = query.count()

    # Apply sorting
    sort_field = getattr(Cluster, sort_by, Cluster.priority_score)
    if sort_order == SortOrder.desc:
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))

    # Apply pagination
    clusters = query.limit(limit).offset(offset).all()

    data = [ClusterResponse.from_orm(cluster) for cluster in clusters]

    return {
        "data": data,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }
    }


@app.get("/api/v1/clusters/{cluster_id}")
@limiter.limit("60/minute")
async def get_cluster_detail(
    cluster_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """Get cluster with all feedback."""
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster {cluster_id} not found"
        )

    # Get feedback
    feedback_list = db.query(Feedback).filter(Feedback.cluster_id == cluster_id).all()

    return {
        "id": cluster.id,
        "label": cluster.label,
        "size": cluster.size,
        "priority_score": cluster.priority_score,
        "total_revenue": cluster.total_revenue,
        "avg_sentiment": cluster.avg_sentiment,
        "created_at": cluster.created_at,
        "feedback": [
            {
                "id": fb.id,
                "text": fb.text,
                "customer_name": fb.customer_name,
                "customer_revenue": fb.customer_revenue,
                "sentiment_score": fb.sentiment_score,
                "submitted_at": fb.submitted_at
            }
            for fb in feedback_list
        ]
    }


@app.post("/api/v1/roadmap/generate")
@limiter.limit("10/minute")
async def generate_roadmap(
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """
    Generate prioritized roadmap from clusters.
    Requires API key authentication.
    """
    start_time = time.time()

    # Get all clusters
    clusters = db.query(Cluster).all()

    if len(clusters) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clusters found. Run clustering first."
        )

    # Initialize priority calculator
    calculator = PriorityCalculator()

    # Prepare items for ranking
    items = []
    for cluster in clusters:
        items.append({
            "cluster_id": cluster.id,
            "title": cluster.label,
            "request_count": cluster.size,
            "total_revenue": cluster.total_revenue,
            "avg_sentiment": cluster.avg_sentiment,
            "estimated_effort": "medium"  # Default; can be enhanced later
        })

    # Rank items
    ranked = calculator.rank_roadmap_items(items)

    # Clear existing roadmap
    db.query(RoadmapItem).delete()
    db.commit()

    # Create roadmap items
    for item_data, rank, priority in ranked:
        roadmap_item = RoadmapItem(
            cluster_id=item_data["cluster_id"],
            title=item_data["title"],
            rank=rank,
            priority_score=priority,
            request_count=item_data["request_count"],
            impacted_revenue=item_data["total_revenue"],
            status="proposed"
        )
        db.add(roadmap_item)

        # Update cluster priority score
        cluster = db.query(Cluster).filter(Cluster.id == item_data["cluster_id"]).first()
        cluster.priority_score = priority

    db.commit()

    elapsed_time = time.time() - start_time

    # Generate insights
    insights = generate_priority_insights(ranked)

    return {
        "status": "success",
        "items_generated": len(ranked),
        "insights": insights,
        "elapsed_time": round(elapsed_time, 2)
    }


@app.get("/api/v1/roadmap")
@limiter.limit("60/minute")
async def get_roadmap(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    status: Optional[RoadmapStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """
    Get prioritized roadmap with pagination and filtering.

    - **limit**: Number of items to return (max 1000)
    - **offset**: Number of items to skip for pagination
    - **status**: Filter by status (proposed, planned, in_progress, shipped)
    """
    query = db.query(RoadmapItem)

    # Apply filters
    if status:
        query = query.filter(RoadmapItem.status == status.value)

    # Get total count
    total = query.count()

    # Apply sorting and pagination
    items = query.order_by(RoadmapItem.rank).limit(limit).offset(offset).all()

    data = [RoadmapResponse.from_orm(item) for item in items]

    return {
        "data": data,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }
    }


@app.patch("/api/v1/roadmap/{item_id}")
@limiter.limit("30/minute")
async def update_roadmap_item(
    item_id: int,
    update: RoadmapUpdateRequest,
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """
    Update roadmap item status and estimates.
    Requires API key authentication.
    """
    item = db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roadmap item {item_id} not found"
        )

    # Update fields
    if update.status:
        item.status = update.status.value
    if update.estimated_effort:
        item.estimated_effort = update.estimated_effort
    if update.estimated_value:
        item.estimated_value = update.estimated_value

    item.updated_at = datetime.utcnow()
    db.commit()

    return RoadmapResponse.from_orm(item)


@app.get("/api/v1/stats")
@limiter.limit("60/minute")
async def get_stats(
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    """Get dashboard statistics."""
    total_feedback = db.query(Feedback).count()
    total_sources = db.query(Source).filter(Source.is_active == True).count()
    total_clusters = db.query(Cluster).count()
    total_roadmap_items = db.query(RoadmapItem).count()

    # Calculate total revenue impact
    total_revenue = db.query(Feedback).with_entities(
        func.sum(Feedback.customer_revenue)
    ).scalar() or 0

    # Average sentiment
    avg_sentiment = db.query(Feedback).with_entities(
        func.avg(Feedback.sentiment_score)
    ).scalar() or 0

    # Recent feedback (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_feedback = db.query(Feedback).filter(
        Feedback.submitted_at >= thirty_days_ago
    ).count()

    return {
        "total_feedback": total_feedback,
        "total_sources": total_sources,
        "total_clusters": total_clusters,
        "total_roadmap_items": total_roadmap_items,
        "total_revenue_impact": round(total_revenue, 2),
        "avg_sentiment": round(avg_sentiment, 3),
        "recent_feedback_30d": recent_feedback,
        "timestamp": datetime.utcnow().isoformat()
    }


# --- API Key Management ---

@app.post("/api/v1/api-keys", response_model=APIKeyResponse)
@limiter.limit("10/minute")
async def create_api_key(
    key_request: APIKeyCreateRequest,
    request: Request,
    db: Session = Depends(get_db_session)
):
    """
    Create a new API key.
    Returns the key only once - store it securely!
    """
    # Generate random API key
    api_key = f"compass_{secrets.token_urlsafe(32)}"

    # Hash the key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:12]

    # Calculate expiration
    expires_at = None
    if key_request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_request.expires_in_days)

    # Create API key record
    db_key = APIKey(
        name=key_request.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=expires_at
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # Return with actual key (only time it's shown)
    return APIKeyResponse(
        id=db_key.id,
        name=db_key.name,
        key=api_key,  # Only returned here
        key_prefix=db_key.key_prefix,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
        expires_at=db_key.expires_at
    )


@app.get("/api/v1/api-keys")
@limiter.limit("30/minute")
async def list_api_keys(
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """List all API keys (without showing actual keys)."""
    keys = db.query(APIKey).order_by(APIKey.created_at.desc()).all()

    return {
        "data": [
            APIKeyResponse(
                id=k.id,
                name=k.name,
                key=None,  # Never return actual key
                key_prefix=k.key_prefix,
                is_active=k.is_active,
                created_at=k.created_at,
                expires_at=k.expires_at
            )
            for k in keys
        ]
    }


@app.delete("/api/v1/api-keys/{key_id}")
@limiter.limit("30/minute")
async def revoke_api_key(
    key_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
    api_key: APIKey = Depends(require_api_key)
):
    """Revoke (deactivate) an API key."""
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {key_id} not found"
        )

    db_key.is_active = False
    db.commit()

    return {"status": "success", "message": f"API key {key_id} revoked"}


if __name__ == "__main__":
    import uvicorn
    print("Starting Compass API v1 server...")
    uvicorn.run("main_v1:app", host="0.0.0.0", port=8000, reload=True)
