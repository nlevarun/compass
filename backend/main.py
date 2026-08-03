"""
Compass FastAPI Application

Endpoints:
- GET /api/sources - List all feedback sources
- POST /api/sources/sync - Sync feedback from all sources
- GET /api/feedback - Get all feedback (with filters)
- POST /api/clustering/run - Run NLP clustering on feedback
- GET /api/clusters - Get all clusters
- GET /api/clusters/{id} - Get specific cluster with feedback
- POST /api/roadmap/generate - Generate prioritized roadmap
- GET /api/roadmap - Get current roadmap
- GET /api/stats - Get dashboard statistics
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import time

from sqlalchemy.orm import Session
from database import get_db_session, init_db
from models import Source, Feedback, Cluster, RoadmapItem
from ingestion.sources import create_source, MOCK_SOURCES
from nlp.clustering import FeedbackClusterer, validate_clustering_accuracy
from nlp.sentiment import SentimentAnalyzer, categorize_sentiment
from priority.calculator import PriorityCalculator, generate_priority_insights


# Initialize FastAPI app
app = FastAPI(
    title="Compass API",
    description="Customer Feedback Intelligence Platform",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create mock sources."""
    print("🚀 Starting Compass API...")
    init_db()

    # Create mock sources if they don't exist
    with get_db_session() as db:
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

    print("✓ Compass API ready!")


# --- Pydantic Models ---

class SourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    is_active: bool
    created_at: datetime
    feedback_count: int

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
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
    id: int
    title: str
    rank: int
    priority_score: float
    request_count: int
    impacted_revenue: float
    status: str

    class Config:
        from_attributes = True


# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Compass API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/sources", response_model=List[SourceResponse])
async def get_sources(db: Session = Depends(get_db_session)):
    """Get all feedback sources."""
    sources = db.query(Source).all()

    # Add feedback counts
    response = []
    for source in sources:
        feedback_count = db.query(Feedback).filter(Feedback.source_id == source.id).count()
        response.append({
            "id": source.id,
            "name": source.name,
            "source_type": source.source_type,
            "is_active": source.is_active,
            "created_at": source.created_at,
            "feedback_count": feedback_count
        })

    return response


@app.post("/api/sources/sync")
async def sync_sources(db: Session = Depends(get_db_session)):
    """Sync feedback from all active sources."""
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


@app.get("/api/feedback", response_model=List[FeedbackResponse])
async def get_feedback(
    source_id: Optional[int] = Query(None),
    cluster_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db_session)
):
    """Get feedback with optional filters."""
    query = db.query(Feedback).join(Source)

    if source_id:
        query = query.filter(Feedback.source_id == source_id)

    if cluster_id is not None:
        if cluster_id == -1:
            query = query.filter(Feedback.cluster_id == None)
        else:
            query = query.filter(Feedback.cluster_id == cluster_id)

    feedback_list = query.order_by(Feedback.submitted_at.desc()).limit(limit).all()

    # Build response
    response = []
    for fb in feedback_list:
        response.append({
            "id": fb.id,
            "text": fb.text,
            "customer_name": fb.customer_name,
            "customer_revenue": fb.customer_revenue,
            "sentiment_score": fb.sentiment_score,
            "submitted_at": fb.submitted_at,
            "source_name": fb.source.name,
            "cluster_id": fb.cluster_id
        })

    return response


@app.post("/api/clustering/run")
async def run_clustering(
    eps: float = Query(0.5, ge=0.1, le=1.0),
    min_samples: int = Query(3, ge=2, le=10),
    db: Session = Depends(get_db_session)
):
    """Run NLP clustering on all feedback."""
    start_time = time.time()

    # Get all feedback
    feedback_list = db.query(Feedback).all()

    if len(feedback_list) == 0:
        raise HTTPException(status_code=400, detail="No feedback to cluster. Run sync first.")

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


@app.get("/api/clusters", response_model=List[ClusterResponse])
async def get_clusters(db: Session = Depends(get_db_session)):
    """Get all clusters sorted by priority."""
    clusters = db.query(Cluster).order_by(Cluster.priority_score.desc()).all()
    return clusters


@app.get("/api/clusters/{cluster_id}")
async def get_cluster_detail(cluster_id: int, db: Session = Depends(get_db_session)):
    """Get cluster with all feedback."""
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Get feedback
    feedback_list = db.query(Feedback).filter(Feedback.cluster_id == cluster_id).all()

    return {
        "id": cluster.id,
        "label": cluster.label,
        "size": cluster.size,
        "priority_score": cluster.priority_score,
        "total_revenue": cluster.total_revenue,
        "avg_sentiment": cluster.avg_sentiment,
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


@app.post("/api/roadmap/generate")
async def generate_roadmap(db: Session = Depends(get_db_session)):
    """Generate prioritized roadmap from clusters."""
    start_time = time.time()

    # Get all clusters
    clusters = db.query(Cluster).all()

    if len(clusters) == 0:
        raise HTTPException(status_code=400, detail="No clusters found. Run clustering first.")

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


@app.get("/api/roadmap", response_model=List[RoadmapResponse])
async def get_roadmap(db: Session = Depends(get_db_session)):
    """Get prioritized roadmap."""
    items = db.query(RoadmapItem).order_by(RoadmapItem.rank).all()
    return items


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db_session)):
    """Get dashboard statistics."""
    total_feedback = db.query(Feedback).count()
    total_sources = db.query(Source).filter(Source.is_active == True).count()
    total_clusters = db.query(Cluster).count()
    total_roadmap_items = db.query(RoadmapItem).count()

    # Calculate total revenue impact
    total_revenue = db.query(Feedback).with_entities(
        db.func.sum(Feedback.customer_revenue)
    ).scalar() or 0

    # Average sentiment
    avg_sentiment = db.query(Feedback).with_entities(
        db.func.avg(Feedback.sentiment_score)
    ).scalar() or 0

    # Recent feedback (last 30 days)
    from datetime import timedelta
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


if __name__ == "__main__":
    import uvicorn
    print("Starting Compass API server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
