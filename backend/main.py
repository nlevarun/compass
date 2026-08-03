"""
Compass FastAPI Application

Core Endpoints:
- GET /api/sources - List all feedback sources
- POST /api/sources/sync - Sync feedback from all sources
- GET /api/feedback - Get all feedback (with filters)
- POST /api/clustering/run - Run NLP clustering on feedback
- GET /api/clusters - Get all clusters
- GET /api/clusters/{id} - Get specific cluster with feedback
- POST /api/roadmap/generate - Generate prioritized roadmap
- GET /api/roadmap - Get current roadmap
- GET /api/stats - Get dashboard statistics

Advanced Priority Endpoints:
- POST /api/roadmap/predict-impact - Predict revenue impact of a feature
- POST /api/priority/custom-score - Calculate score with custom formula
- GET /api/priority/at-risk-customers - Identify at-risk customers
- GET /api/roadmap/{id}/explanation - Get priority explanation
- GET /api/priority/formulas/presets - List preset formulas (ICE, RICE, WSJF)
- GET /api/priority/formulas/variables - List available variables
- POST /api/priority/formulas/validate - Validate custom formula
- POST /api/priority/formulas/compare - Compare multiple formulas

WebSocket & Events:
- WS /ws - Real-time updates
- GET /api/websocket/stats - WebSocket statistics
- GET /api/events/recent - Recent event history
"""

from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import time
import asyncio
import uuid

from sqlalchemy.orm import Session
from database import get_db_session, get_db, init_db
from models import Source, Feedback, Cluster, RoadmapItem
from ingestion.sources import create_source, MOCK_SOURCES
from nlp.clustering import FeedbackClusterer, validate_clustering_accuracy
from nlp.sentiment import SentimentAnalyzer, categorize_sentiment
from priority.calculator import (
    PriorityCalculator,
    generate_priority_insights,
    generate_priority_explanation,
    identify_at_risk_customers
)
from priority.impact_predictor import ImpactPredictor
from priority.custom_scoring import CustomScoringEngine, compare_formulas
from websockets import manager, handle_client_message
from events import event_emitter, TaskTracker


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

    # Connect event emitter to WebSocket manager
    event_emitter.set_manager(manager)

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

    print("✓ Compass API ready!")
    print("✓ WebSocket support enabled at /ws")


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
        "websocket_enabled": True,
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Clients can:
    - Subscribe to rooms: {"action": "join", "room": "feedback"}
    - Subscribe to multiple rooms: {"action": "subscribe", "rooms": ["feedback", "clusters"]}
    - Request stats: {"action": "stats"}
    - Ping: {"action": "ping"}
    """
    # Generate unique client ID
    client_id = str(uuid.uuid4())

    # Connect client
    await manager.connect(websocket, client_id)

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(manager.heartbeat(client_id, websocket))

    try:
        # Listen for client messages
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(client_id, message)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "event": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)

    except WebSocketDisconnect:
        heartbeat_task.cancel()
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        heartbeat_task.cancel()
        manager.disconnect(client_id)


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

    # Start task tracking
    async with TaskTracker("sync", "Syncing feedback from sources") as tracker:
        sources = db.query(Source).filter(Source.is_active == True).all()

        total_synced = 0
        results = []
        new_feedback_items = []

        for idx, source_model in enumerate(sources):
            try:
                # Update progress
                await tracker.progress(idx, len(sources), f"Syncing {source_model.name}")

                # Create source instance
                source = create_source(source_model)

                # Fetch feedback
                feedback_data = source.fetch_feedback(since=source_model.last_synced_at)

                # Save to database and emit events
                for fb_data in feedback_data:
                    feedback = Feedback(**fb_data)
                    db.add(feedback)
                    db.flush()  # Get feedback ID

                    # Prepare for real-time emission
                    feedback_item = {
                        "id": feedback.id,
                        "text": feedback.text,
                        "customer_name": feedback.customer_name,
                        "customer_revenue": feedback.customer_revenue,
                        "source_name": source_model.name,
                        "submitted_at": feedback.submitted_at.isoformat()
                    }
                    new_feedback_items.append(feedback_item)

                    # Emit individual feedback (throttled for large batches)
                    if len(feedback_data) <= 10:
                        await event_emitter.emit_feedback_new(feedback_item)

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

        response = {
            "total_synced": total_synced,
            "sources_synced": len(sources),
            "results": results,
            "elapsed_time": round(elapsed_time, 2)
        }

        # Emit sync completion event
        await event_emitter.emit_feedback_synced(response)

        # Update stats
        stats = await get_stats(db)
        await event_emitter.emit_stats_updated(stats)

        return response


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

    # Start task tracking
    async with TaskTracker("clustering", "Running NLP clustering") as tracker:
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
        await tracker.progress(1, 4, "Generating embeddings...")
        print(f"Generating embeddings for {len(texts)} feedback entries...")
        embeddings = clusterer.generate_embeddings(texts)

        # Update sentiment scores (if not already set)
        await tracker.progress(2, 4, "Analyzing sentiment...")
        print("Analyzing sentiment...")
        for fb, text in zip(feedback_list, texts):
            if fb.sentiment_score is None:
                fb.sentiment_score = sentiment_analyzer.analyze(text)
            fb.embedding = json.dumps(embeddings[feedback_list.index(fb)].tolist() if hasattr(embeddings[feedback_list.index(fb)], 'tolist') else embeddings[feedback_list.index(fb)])

        db.commit()

        # Cluster feedback
        await tracker.progress(3, 4, "Clustering feedback...")
        print("Clustering feedback...")
        labels, metrics = clusterer.cluster_feedback(texts, embeddings)

        # Clear existing clusters
        db.query(Cluster).delete()
        db.commit()

        # Create new clusters
        await tracker.progress(4, 4, "Creating clusters...")
        cluster_map = {}
        created_clusters = []

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

            # Prepare cluster data for event
            cluster_data = {
                "id": cluster.id,
                "label": label_text,
                "size": len(cluster_feedback),
                "total_revenue": total_revenue,
                "avg_sentiment": avg_sentiment
            }
            created_clusters.append(cluster_data)

            # Emit cluster creation event
            await event_emitter.emit_cluster_created(cluster_data)

            # Update feedback cluster assignments
            for fb in cluster_feedback:
                fb.cluster_id = cluster.id

        db.commit()

        elapsed_time = time.time() - start_time

        response = {
            "status": "success",
            "feedback_clustered": len(feedback_list),
            "clusters_created": len(cluster_map),
            "noise_points": metrics["n_noise"],
            "metrics": metrics,
            "elapsed_time": round(elapsed_time, 2)
        }

        # Emit clustering completion
        await event_emitter.emit_clustering_complete(response)

        # Update stats
        stats = await get_stats(db)
        await event_emitter.emit_stats_updated(stats)

        return response


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

    # Start task tracking
    async with TaskTracker("roadmap", "Generating prioritized roadmap") as tracker:
        # Get all clusters
        await tracker.progress(1, 3, "Loading clusters...")
        clusters = db.query(Cluster).all()

        if len(clusters) == 0:
            raise HTTPException(status_code=400, detail="No clusters found. Run clustering first.")

        # Initialize priority calculator
        calculator = PriorityCalculator()

        # Prepare items for ranking
        await tracker.progress(2, 3, "Calculating priorities...")
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
        await tracker.progress(3, 3, "Creating roadmap items...")
        roadmap_items_data = []

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
            db.flush()

            # Prepare for event emission
            roadmap_items_data.append({
                "id": roadmap_item.id,
                "title": roadmap_item.title,
                "rank": rank,
                "priority_score": priority,
                "request_count": item_data["request_count"],
                "impacted_revenue": item_data["total_revenue"]
            })

            # Update cluster priority score
            cluster = db.query(Cluster).filter(Cluster.id == item_data["cluster_id"]).first()
            cluster.priority_score = priority

        db.commit()

        elapsed_time = time.time() - start_time

        # Generate insights
        insights = generate_priority_insights(ranked)

        response = {
            "status": "success",
            "items_generated": len(ranked),
            "insights": insights,
            "elapsed_time": round(elapsed_time, 2)
        }

        # Emit roadmap generation event
        await event_emitter.emit_roadmap_generated({
            "items_count": len(ranked),
            "items": roadmap_items_data[:5],  # Send top 5 for preview
            "insights": insights
        })

        # Update stats
        stats = await get_stats(db)
        await event_emitter.emit_stats_updated(stats)

        return response


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


@app.get("/api/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return manager.get_stats()


@app.get("/api/events/recent")
async def get_recent_events(count: int = Query(10, ge=1, le=100)):
    """Get recent event history."""
    return {
        "events": event_emitter.get_recent_events(count),
        "timestamp": datetime.utcnow().isoformat()
    }


# --- Advanced Priority Endpoints ---

class ImpactPredictionRequest(BaseModel):
    """Request model for impact prediction."""
    request_count: int
    impacted_revenue: float
    avg_sentiment: float
    effort: str
    feedback_volume_current: int = 0


class CustomScoreRequest(BaseModel):
    """Request model for custom scoring."""
    formula: str
    variables: Dict[str, Any]


@app.post("/api/roadmap/predict-impact")
async def predict_impact(request: ImpactPredictionRequest):
    """
    Predict revenue impact of building a feature.

    Uses ML model if available, falls back to heuristics.
    """
    start_time = time.time()

    # Initialize predictor
    predictor = ImpactPredictor()

    # TODO: Load historical data from database
    # For now, predictor will use heuristics

    try:
        prediction = predictor.predict_impact(
            request_count=request.request_count,
            impacted_revenue=request.impacted_revenue,
            avg_sentiment=request.avg_sentiment,
            effort=request.effort,
            feedback_volume_current=request.feedback_volume_current
        )

        elapsed_time = time.time() - start_time

        return {
            "status": "success",
            "prediction": prediction,
            "elapsed_time": round(elapsed_time, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@app.post("/api/priority/custom-score")
async def calculate_custom_score(request: CustomScoreRequest):
    """
    Calculate priority score using custom formula.

    Supports ICE, RICE, WSJF, and custom formulas.
    """
    start_time = time.time()

    engine = CustomScoringEngine()

    try:
        # Validate formula first
        validation = engine.validate_formula(request.formula)

        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid formula",
                    "validation_errors": validation['errors']
                }
            )

        # Calculate score
        result = engine.calculate_score(request.formula, request.variables)

        elapsed_time = time.time() - start_time

        return {
            "status": "success",
            "result": result,
            "validation": validation,
            "elapsed_time": round(elapsed_time, 3)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@app.get("/api/priority/at-risk-customers")
async def get_at_risk_customers(
    revenue_threshold: float = Query(100_000),
    sentiment_threshold: float = Query(-0.3),
    recent_days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db_session)
):
    """
    Identify at-risk customers based on feedback patterns.

    Returns high-value customers with negative sentiment and recent activity.
    """
    start_time = time.time()

    # Get all feedback with customer info
    feedback_list = db.query(Feedback).filter(
        Feedback.customer_name.isnot(None),
        Feedback.customer_revenue.isnot(None)
    ).all()

    if not feedback_list:
        return {
            "status": "success",
            "at_risk_customers": [],
            "message": "No customer data available"
        }

    # Convert to dictionaries
    feedback_dicts = [
        {
            'customer_name': fb.customer_name,
            'customer_revenue': fb.customer_revenue,
            'sentiment_score': fb.sentiment_score,
            'submitted_at': fb.submitted_at,
            'text': fb.text
        }
        for fb in feedback_list
    ]

    # Identify at-risk customers
    at_risk = identify_at_risk_customers(
        feedback_dicts,
        revenue_threshold=revenue_threshold,
        sentiment_threshold=sentiment_threshold,
        recent_days=recent_days
    )

    elapsed_time = time.time() - start_time

    return {
        "status": "success",
        "at_risk_customers": at_risk,
        "total_count": len(at_risk),
        "parameters": {
            "revenue_threshold": revenue_threshold,
            "sentiment_threshold": sentiment_threshold,
            "recent_days": recent_days
        },
        "elapsed_time": round(elapsed_time, 2)
    }


@app.get("/api/roadmap/{item_id}/explanation")
async def get_roadmap_explanation(
    item_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get detailed explanation of why a roadmap item has its priority.

    Returns contributing factors and their weights.
    """
    # Get roadmap item
    roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()

    if not roadmap_item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")

    # Get cluster for additional data
    cluster = db.query(Cluster).filter(Cluster.id == roadmap_item.cluster_id).first()

    # Build item dictionary
    item_dict = {
        'title': roadmap_item.title,
        'request_count': roadmap_item.request_count,
        'total_revenue': roadmap_item.impacted_revenue,
        'avg_sentiment': cluster.avg_sentiment if cluster else 0,
        'estimated_effort': roadmap_item.estimated_effort or 'medium',
        # TODO: Add advanced factors when available
        'churn_risk_score': 0.0,
        'recent_request_count': 0,
        'historical_request_count': 0,
        'competitor_mentions': 0,
        'technical_complexity': 3
    }

    # Generate explanation
    calculator = PriorityCalculator()
    explanation = generate_priority_explanation(
        item_dict,
        roadmap_item.priority_score,
        calculator
    )

    return {
        "status": "success",
        "roadmap_item": {
            "id": roadmap_item.id,
            "title": roadmap_item.title,
            "rank": roadmap_item.rank,
            "priority_score": roadmap_item.priority_score
        },
        "explanation": explanation
    }


@app.get("/api/priority/formulas/presets")
async def list_preset_formulas():
    """
    List all available preset scoring formulas.

    Includes ICE, RICE, WSJF, and other popular frameworks.
    """
    engine = CustomScoringEngine()
    presets = engine.list_preset_formulas()

    return {
        "status": "success",
        "presets": presets,
        "count": len(presets)
    }


@app.get("/api/priority/formulas/variables")
async def list_formula_variables():
    """
    List all available variables for custom formulas.

    Returns variable names, descriptions, and example values.
    """
    engine = CustomScoringEngine()
    variables = engine.list_available_variables()

    return {
        "status": "success",
        "variables": variables,
        "count": len(variables)
    }


@app.post("/api/priority/formulas/validate")
async def validate_formula(formula: str):
    """
    Validate a custom scoring formula.

    Checks syntax, variable names, and safety.
    """
    engine = CustomScoringEngine()
    validation = engine.validate_formula(formula)

    return {
        "status": "success",
        "validation": validation
    }


@app.post("/api/priority/formulas/compare")
async def compare_scoring_formulas(
    formulas: List[str],
    test_cases: List[Dict[str, Any]]
):
    """
    Compare multiple scoring formulas across test cases.

    Useful for deciding which formula to use.
    """
    if not formulas or not test_cases:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least one formula and one test case"
        )

    start_time = time.time()

    try:
        comparison = compare_formulas(formulas, test_cases)

        elapsed_time = time.time() - start_time

        return {
            "status": "success",
            "comparison": comparison,
            "formulas_count": len(formulas),
            "test_cases_count": len(test_cases),
            "elapsed_time": round(elapsed_time, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Comparison failed: {str(e)}")


# --- Import Endpoints ---

# Store active import jobs in memory (in production, use Redis or database)
active_import_jobs = {}


class ZendeskImportRequest(BaseModel):
    """Request model for Zendesk import."""
    subdomain: str
    email: str
    api_token: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status_filter: Optional[List[str]] = None
    fetch_comments: bool = True
    fetch_users: bool = True


class IntercomImportRequest(BaseModel):
    """Request model for Intercom import."""
    access_token: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    state_filter: Optional[str] = None
    fetch_parts: bool = True
    fetch_users: bool = True


class CSVImportRequest(BaseModel):
    """Request model for CSV import."""
    column_mapping: Dict[str, str]
    skip_invalid: bool = True


async def run_import_job_background(job_id: str, job_type: str, config: Dict, db: Session):
    """Background task to run import job."""
    import sys
    sys.path.append('/home/wsl-user/compass/backend')
    from importers.zendesk_importer import ZendeskImporter
    from importers.intercom_importer import IntercomImporter
    from importers.csv_importer import CSVImporter

    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    job.status = "running"
    db.commit()

    def progress_callback(processed, total):
        """Update job progress."""
        job.processed_items = processed
        job.total_items = total
        db.commit()

    try:
        # Get or create source
        source_name = f"{job_type.capitalize()} Import"
        source = db.query(Source).filter(Source.name == source_name).first()
        if not source:
            source = Source(
                name=source_name,
                source_type="import",
                is_active=False,
                config={}
            )
            db.add(source)
            db.commit()

        result = None

        if job_type == "zendesk":
            importer = ZendeskImporter(
                subdomain=config["subdomain"],
                email=config["email"],
                api_token=config["api_token"],
                source_id=source.id,
                db=db,
                progress_callback=progress_callback
            )
            start_date = datetime.fromisoformat(config["start_date"]) if config.get("start_date") else None
            end_date = datetime.fromisoformat(config["end_date"]) if config.get("end_date") else None
            result = await importer.import_tickets(
                start_date=start_date,
                end_date=end_date,
                status_filter=config.get("status_filter"),
                fetch_comments=config.get("fetch_comments", True),
                fetch_users=config.get("fetch_users", True)
            )

        elif job_type == "intercom":
            importer = IntercomImporter(
                access_token=config["access_token"],
                source_id=source.id,
                db=db,
                progress_callback=progress_callback
            )
            start_date = datetime.fromisoformat(config["start_date"]) if config.get("start_date") else None
            end_date = datetime.fromisoformat(config["end_date"]) if config.get("end_date") else None
            result = await importer.import_conversations(
                start_date=start_date,
                end_date=end_date,
                state_filter=config.get("state_filter"),
                fetch_parts=config.get("fetch_parts", True),
                fetch_users=config.get("fetch_users", True)
            )

        elif job_type == "csv":
            importer = CSVImporter(
                file_path=config["file_path"],
                source_id=source.id,
                db=db,
                progress_callback=progress_callback
            )
            result = importer.import_csv(
                column_mapping=config["column_mapping"],
                skip_invalid=config.get("skip_invalid", True)
            )

        # Update job with result
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result_summary = result
        db.commit()

        # Remove from active jobs
        if job_id in active_import_jobs:
            del active_import_jobs[job_id]

    except Exception as e:
        job.status = "failed"
        job.error_log = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

        if job_id in active_import_jobs:
            del active_import_jobs[job_id]


@app.post("/api/import/zendesk")
async def import_zendesk(
    request: ZendeskImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Start Zendesk historical data import."""
    job_id = str(uuid.uuid4())

    # Create import job
    import_job = ImportJob(
        id=job_id,
        job_type="zendesk",
        status="pending",
        config=request.dict(),
        initiated_by="api"
    )
    db.add(import_job)
    db.commit()

    # Add to background tasks
    background_tasks.add_task(
        run_import_job_background,
        job_id,
        "zendesk",
        request.dict(),
        db
    )

    active_import_jobs[job_id] = {
        "type": "zendesk",
        "status": "pending",
        "started_at": datetime.utcnow().isoformat()
    }

    return {
        "status": "success",
        "job_id": job_id,
        "message": "Zendesk import job started"
    }


@app.post("/api/import/intercom")
async def import_intercom(
    request: IntercomImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Start Intercom historical data import."""
    job_id = str(uuid.uuid4())

    import_job = ImportJob(
        id=job_id,
        job_type="intercom",
        status="pending",
        config=request.dict(),
        initiated_by="api"
    )
    db.add(import_job)
    db.commit()

    background_tasks.add_task(
        run_import_job_background,
        job_id,
        "intercom",
        request.dict(),
        db
    )

    active_import_jobs[job_id] = {
        "type": "intercom",
        "status": "pending",
        "started_at": datetime.utcnow().isoformat()
    }

    return {
        "status": "success",
        "job_id": job_id,
        "message": "Intercom import job started"
    }


@app.post("/api/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db_session)
):
    """Upload and import CSV file."""
    # Save uploaded file
    upload_dir = "/tmp/compass_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Preview CSV structure
    from importers.csv_importer import CSVImporter
    temp_source = db.query(Source).first()  # Use any source temporarily
    importer = CSVImporter(file_path, temp_source.id if temp_source else 1, db)
    preview = importer.preview_csv(num_rows=5)

    if preview["status"] == "error":
        return preview

    # Auto-detect mapping
    auto_mapping = importer.auto_detect_mapping()

    return {
        "status": "success",
        "file_path": file_path,
        "preview": preview,
        "suggested_mapping": auto_mapping,
        "message": "CSV uploaded. Review mapping and call POST /api/import/csv/start to begin import"
    }


@app.post("/api/import/csv/start")
async def start_csv_import(
    request: CSVImportRequest,
    file_path: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Start CSV import with column mapping."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CSV file not found. Please upload first.")

    job_id = str(uuid.uuid4())

    config = request.dict()
    config["file_path"] = file_path

    import_job = ImportJob(
        id=job_id,
        job_type="csv",
        status="pending",
        config=config,
        initiated_by="api"
    )
    db.add(import_job)
    db.commit()

    background_tasks.add_task(
        run_import_job_background,
        job_id,
        "csv",
        config,
        db
    )

    active_import_jobs[job_id] = {
        "type": "csv",
        "status": "pending",
        "started_at": datetime.utcnow().isoformat()
    }

    return {
        "status": "success",
        "job_id": job_id,
        "message": "CSV import job started"
    }


@app.get("/api/import/status/{job_id}")
async def get_import_status(job_id: str, db: Session = Depends(get_db_session)):
    """Get import job status."""
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    return {
        "job_id": job.id,
        "type": job.job_type,
        "status": job.status,
        "total_items": job.total_items,
        "processed_items": job.processed_items,
        "failed_items": job.failed_items,
        "started_at": job.started_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "result_summary": job.result_summary,
        "error_log": job.error_log
    }


@app.get("/api/import/jobs")
async def list_import_jobs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db_session)
):
    """List all import jobs."""
    jobs = db.query(ImportJob).order_by(ImportJob.started_at.desc()).limit(limit).all()

    return {
        "jobs": [
            {
                "job_id": job.id,
                "type": job.job_type,
                "status": job.status,
                "total_items": job.total_items,
                "processed_items": job.processed_items,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in jobs
        ],
        "total": len(jobs)
    }


# --- Jira Integration Endpoints ---

class JiraConfigRequest(BaseModel):
    """Request model for Jira configuration."""
    jira_url: str
    username: str
    api_token: str
    default_project: Optional[str] = None
    default_issue_type: str = "Story"


class JiraCreateIssueRequest(BaseModel):
    """Request model for creating Jira issue."""
    cluster_id: Optional[int] = None
    feedback_id: Optional[int] = None
    project_key: Optional[str] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None


class JiraLinkIssueRequest(BaseModel):
    """Request model for linking Jira issue."""
    jira_key: str
    cluster_id: Optional[int] = None
    roadmap_item_id: Optional[int] = None


@app.post("/api/integrations/jira/test")
async def test_jira_connection(config: JiraConfigRequest, db: Session = Depends(get_db_session)):
    """Test Jira connection and list accessible projects."""
    from integrations.jira_sync import JiraSync

    jira = JiraSync(
        jira_url=config.jira_url,
        username=config.username,
        api_token=config.api_token,
        db=db,
        default_project=config.default_project,
        default_issue_type=config.default_issue_type
    )

    result = jira.test_connection()
    return result


@app.post("/api/integrations/jira/create-issue")
async def create_jira_issue(
    request: JiraCreateIssueRequest,
    config: JiraConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Create Jira issue from cluster or feedback."""
    from integrations.jira_sync import JiraSync

    jira = JiraSync(
        jira_url=config.jira_url,
        username=config.username,
        api_token=config.api_token,
        db=db,
        default_project=config.default_project,
        default_issue_type=config.default_issue_type
    )

    if request.cluster_id:
        result = jira.create_issue_from_cluster(
            cluster_id=request.cluster_id,
            project_key=request.project_key,
            issue_type=request.issue_type,
            priority=request.priority,
            labels=request.labels
        )
    elif request.feedback_id:
        result = jira.create_issue_from_feedback(
            feedback_id=request.feedback_id,
            project_key=request.project_key,
            issue_type=request.issue_type,
            priority=request.priority
        )
    else:
        raise HTTPException(status_code=400, detail="Must specify cluster_id or feedback_id")

    return result


@app.post("/api/integrations/jira/link-issue")
async def link_jira_issue(
    request: JiraLinkIssueRequest,
    config: JiraConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Link existing Jira issue to cluster or roadmap item."""
    from integrations.jira_sync import JiraSync

    jira = JiraSync(
        jira_url=config.jira_url,
        username=config.username,
        api_token=config.api_token,
        db=db
    )

    result = jira.link_existing_issue(
        jira_key=request.jira_key,
        cluster_id=request.cluster_id,
        roadmap_item_id=request.roadmap_item_id
    )
    return result


@app.get("/api/integrations/jira/status/{jira_key}")
async def sync_jira_status(
    jira_key: str,
    config: JiraConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Sync status from Jira to Compass."""
    from integrations.jira_sync import JiraSync

    jira = JiraSync(
        jira_url=config.jira_url,
        username=config.username,
        api_token=config.api_token,
        db=db
    )

    result = jira.sync_issue_status(jira_key)
    return result


@app.post("/api/integrations/jira/sync")
async def sync_all_jira_issues(
    config: JiraConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Sync all linked Jira issues."""
    from integrations.jira_sync import JiraSync

    jira = JiraSync(
        jira_url=config.jira_url,
        username=config.username,
        api_token=config.api_token,
        db=db
    )

    result = jira.sync_all_issues()
    return result


# --- Linear Integration Endpoints ---

class LinearConfigRequest(BaseModel):
    """Request model for Linear configuration."""
    api_key: str
    default_team_id: Optional[str] = None


class LinearCreateIssueRequest(BaseModel):
    """Request model for creating Linear issue."""
    cluster_id: Optional[int] = None
    feedback_id: Optional[int] = None
    team_id: Optional[str] = None
    priority: Optional[int] = None
    labels: Optional[List[str]] = None


class LinearLinkIssueRequest(BaseModel):
    """Request model for linking Linear issue."""
    issue_id: str
    cluster_id: Optional[int] = None
    roadmap_item_id: Optional[int] = None


@app.post("/api/integrations/linear/test")
async def test_linear_connection(config: LinearConfigRequest, db: Session = Depends(get_db_session)):
    """Test Linear connection and list accessible teams."""
    from integrations.linear_sync import LinearSync

    linear = LinearSync(
        api_key=config.api_key,
        db=db,
        default_team_id=config.default_team_id
    )

    result = await linear.test_connection()
    return result


@app.post("/api/integrations/linear/create-issue")
async def create_linear_issue(
    request: LinearCreateIssueRequest,
    config: LinearConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Create Linear issue from cluster or feedback."""
    from integrations.linear_sync import LinearSync

    linear = LinearSync(
        api_key=config.api_key,
        db=db,
        default_team_id=config.default_team_id
    )

    if request.cluster_id:
        result = await linear.create_issue_from_cluster(
            cluster_id=request.cluster_id,
            team_id=request.team_id,
            priority=request.priority,
            labels=request.labels
        )
    elif request.feedback_id:
        result = await linear.create_issue_from_feedback(
            feedback_id=request.feedback_id,
            team_id=request.team_id,
            priority=request.priority
        )
    else:
        raise HTTPException(status_code=400, detail="Must specify cluster_id or feedback_id")

    return result


@app.post("/api/integrations/linear/link-issue")
async def link_linear_issue(
    request: LinearLinkIssueRequest,
    config: LinearConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Link existing Linear issue to cluster or roadmap item."""
    from integrations.linear_sync import LinearSync

    linear = LinearSync(
        api_key=config.api_key,
        db=db
    )

    result = await linear.link_existing_issue(
        issue_id=request.issue_id,
        cluster_id=request.cluster_id,
        roadmap_item_id=request.roadmap_item_id
    )
    return result


@app.get("/api/integrations/linear/status/{issue_id}")
async def sync_linear_status(
    issue_id: str,
    config: LinearConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Sync status from Linear to Compass."""
    from integrations.linear_sync import LinearSync

    linear = LinearSync(
        api_key=config.api_key,
        db=db
    )

    result = await linear.sync_issue_status(issue_id)
    return result


@app.post("/api/integrations/linear/sync")
async def sync_all_linear_issues(
    config: LinearConfigRequest,
    db: Session = Depends(get_db_session)
):
    """Sync all linked Linear issues."""
    from integrations.linear_sync import LinearSync

    linear = LinearSync(
        api_key=config.api_key,
        db=db
    )

    result = await linear.sync_all_issues()
    return result


if __name__ == "__main__":
    import uvicorn
    print("Starting Compass API server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
