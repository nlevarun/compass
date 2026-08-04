"""
Public Board API - Canny Competitor Feature

Endpoints for creating and managing public feedback boards with revenue-weighted voting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import uuid
import re

from database import get_db_session
from models import PublicBoard, PublicPost, Vote, Comment
from ws_manager import manager as ws_manager


router = APIRouter(prefix="/api/public-boards", tags=["public-boards"])


# Request/Response Models
class BoardCreateRequest(BaseModel):
    organization_name: str
    title: str
    description: Optional[str] = None
    allow_anonymous: bool = True
    theme_color: str = "#4F46E5"
    owner_email: Optional[str] = None


class BoardResponse(BaseModel):
    id: str
    slug: str
    organization_name: str
    title: str
    description: Optional[str]
    is_public: bool
    allow_anonymous: bool
    theme_color: str
    created_at: datetime
    post_count: int = 0
    board_url: str


class PostCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = "feature"  # feature, bug, improvement, question
    author_email: Optional[str] = None
    author_name: Optional[str] = None


class PostResponse(BaseModel):
    id: str
    board_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: str
    vote_count: int
    revenue_weighted_score: float
    author_name: Optional[str]
    created_at: datetime
    user_has_voted: bool = False
    comment_count: int = 0


class VoteRequest(BaseModel):
    user_email: str
    user_name: Optional[str] = None
    user_revenue: float = 0.0  # Revenue-weighted voting!


class CommentCreateRequest(BaseModel):
    text: str
    author_email: Optional[str] = None
    author_name: Optional[str] = None


class CommentResponse(BaseModel):
    id: str
    text: str
    author_name: Optional[str]
    is_admin: bool
    created_at: datetime


# Utility functions
def generate_slug(organization_name: str) -> str:
    """Generate URL-friendly slug from organization name"""
    slug = organization_name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def calculate_revenue_weighted_score(post: PublicPost, db: Session) -> float:
    """Calculate revenue-weighted voting score"""
    votes = db.query(Vote).filter(Vote.post_id == post.id).all()

    # Simple formula: sum of (1 + log10(revenue/1000)) for each vote
    # Free users = 1 point
    # $1k customer = ~1 point
    # $10k customer = ~2 points
    # $100k customer = ~3 points
    total_score = 0.0
    for vote in votes:
        if vote.user_revenue > 0:
            import math
            revenue_weight = 1 + math.log10(max(vote.user_revenue / 1000, 1))
            total_score += revenue_weight
        else:
            total_score += 1.0  # Free user = 1 point

    return round(total_score, 2)


# Endpoints

@router.post("/boards", response_model=BoardResponse)
async def create_board(board_data: BoardCreateRequest, db: Session = Depends(get_db_session)):
    """Create a new public feedback board"""

    # Generate unique slug
    base_slug = generate_slug(board_data.organization_name)
    slug = base_slug
    counter = 1

    while db.query(PublicBoard).filter(PublicBoard.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create board
    board = PublicBoard(
        id=str(uuid.uuid4()),
        slug=slug,
        organization_name=board_data.organization_name,
        title=board_data.title,
        description=board_data.description,
        allow_anonymous=board_data.allow_anonymous,
        theme_color=board_data.theme_color,
        owner_email=board_data.owner_email
    )

    db.add(board)
    db.commit()
    db.refresh(board)

    return BoardResponse(
        id=board.id,
        slug=board.slug,
        organization_name=board.organization_name,
        title=board.title,
        description=board.description,
        is_public=board.is_public,
        allow_anonymous=board.allow_anonymous,
        theme_color=board.theme_color,
        created_at=board.created_at,
        post_count=0,
        board_url=f"/boards/{board.slug}"
    )


@router.get("/boards/{slug}", response_model=BoardResponse)
async def get_board(slug: str, db: Session = Depends(get_db_session)):
    """Get public board by slug"""

    board = db.query(PublicBoard).filter(PublicBoard.slug == slug).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    post_count = db.query(PublicPost).filter(PublicPost.board_id == board.id).count()

    return BoardResponse(
        id=board.id,
        slug=board.slug,
        organization_name=board.organization_name,
        title=board.title,
        description=board.description,
        is_public=board.is_public,
        allow_anonymous=board.allow_anonymous,
        theme_color=board.theme_color,
        created_at=board.created_at,
        post_count=post_count,
        board_url=f"/boards/{board.slug}"
    )


@router.get("/boards", response_model=List[BoardResponse])
async def list_boards(db: Session = Depends(get_db_session)):
    """List all public boards"""

    boards = db.query(PublicBoard).filter(PublicBoard.is_public == True).all()

    result = []
    for board in boards:
        post_count = db.query(PublicPost).filter(PublicPost.board_id == board.id).count()
        result.append(BoardResponse(
            id=board.id,
            slug=board.slug,
            organization_name=board.organization_name,
            title=board.title,
            description=board.description,
            is_public=board.is_public,
            allow_anonymous=board.allow_anonymous,
            theme_color=board.theme_color,
            created_at=board.created_at,
            post_count=post_count,
            board_url=f"/boards/{board.slug}"
        ))

    return result


@router.post("/boards/{slug}/posts", response_model=PostResponse)
async def create_post(slug: str, post_data: PostCreateRequest, db: Session = Depends(get_db_session)):
    """Submit feedback post to board"""

    board = db.query(PublicBoard).filter(PublicBoard.slug == slug).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Create post
    post = PublicPost(
        id=str(uuid.uuid4()),
        board_id=board.id,
        title=post_data.title,
        description=post_data.description,
        category=post_data.category,
        author_email=post_data.author_email,
        author_name=post_data.author_name or "Anonymous"
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # Send WebSocket notification
    await ws_manager.broadcast_event({
        "type": "post_created",
        "board_slug": slug,
        "post": {
            "id": post.id,
            "title": post.title,
            "author": post.author_name
        }
    })

    return PostResponse(
        id=post.id,
        board_id=post.board_id,
        title=post.title,
        description=post.description,
        category=post.category,
        status=post.status,
        vote_count=0,
        revenue_weighted_score=0.0,
        author_name=post.author_name,
        created_at=post.created_at,
        user_has_voted=False,
        comment_count=0
    )


@router.get("/boards/{slug}/posts", response_model=List[PostResponse])
async def get_posts(
    slug: str,
    sort_by: str = Query("votes", regex="^(votes|revenue_weighted|recent|trending)$"),
    status: Optional[str] = None,
    category: Optional[str] = None,
    user_email: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """Get posts for a board with sorting and filtering"""

    board = db.query(PublicBoard).filter(PublicBoard.slug == slug).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Base query
    query = db.query(PublicPost).filter(PublicPost.board_id == board.id)

    # Filters
    if status:
        query = query.filter(PublicPost.status == status)
    if category:
        query = query.filter(PublicPost.category == category)

    # Sorting
    if sort_by == "votes":
        query = query.order_by(desc(PublicPost.vote_count))
    elif sort_by == "revenue_weighted":
        query = query.order_by(desc(PublicPost.revenue_weighted_score))
    elif sort_by == "recent":
        query = query.order_by(desc(PublicPost.created_at))
    elif sort_by == "trending":
        # Trending = votes in last 7 days (simplified for MVP)
        query = query.order_by(desc(PublicPost.vote_count))

    posts = query.all()

    # Check if user has voted (if email provided)
    user_voted_posts = set()
    if user_email:
        user_votes = db.query(Vote.post_id).filter(Vote.user_email == user_email).all()
        user_voted_posts = {v[0] for v in user_votes}

    # Build response
    result = []
    for post in posts:
        comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        result.append(PostResponse(
            id=post.id,
            board_id=post.board_id,
            title=post.title,
            description=post.description,
            category=post.category,
            status=post.status,
            vote_count=post.vote_count,
            revenue_weighted_score=post.revenue_weighted_score,
            author_name=post.author_name,
            created_at=post.created_at,
            user_has_voted=(post.id in user_voted_posts),
            comment_count=comment_count
        ))

    return result


@router.post("/posts/{post_id}/vote")
async def vote_on_post(post_id: str, vote_data: VoteRequest, db: Session = Depends(get_db_session)):
    """Vote on a post (with revenue weighting)"""

    post = db.query(PublicPost).filter(PublicPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.user_email == vote_data.user_email
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted on this post")

    # Create vote
    vote = Vote(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_email=vote_data.user_email,
        user_name=vote_data.user_name,
        user_revenue=vote_data.user_revenue
    )

    db.add(vote)

    # Update post vote count
    post.vote_count += 1

    # Recalculate revenue-weighted score
    post.revenue_weighted_score = calculate_revenue_weighted_score(post, db)

    db.commit()
    db.refresh(post)

    # Send WebSocket notification (instant update!)
    await ws_manager.broadcast_event({
        "type": "vote_added",
        "post_id": post_id,
        "vote_count": post.vote_count,
        "revenue_weighted_score": post.revenue_weighted_score
    })

    return {
        "success": True,
        "vote_count": post.vote_count,
        "revenue_weighted_score": post.revenue_weighted_score
    }


@router.delete("/posts/{post_id}/vote")
async def remove_vote(post_id: str, user_email: str, db: Session = Depends(get_db_session)):
    """Remove vote from a post"""

    post = db.query(PublicPost).filter(PublicPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    vote = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.user_email == user_email
    ).first()

    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    db.delete(vote)
    post.vote_count -= 1
    post.revenue_weighted_score = calculate_revenue_weighted_score(post, db)

    db.commit()

    # Send WebSocket notification
    await ws_manager.broadcast_event({
        "type": "vote_removed",
        "post_id": post_id,
        "vote_count": post.vote_count,
        "revenue_weighted_score": post.revenue_weighted_score
    })

    return {"success": True, "vote_count": post.vote_count}


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def add_comment(post_id: str, comment_data: CommentCreateRequest, db: Session = Depends(get_db_session)):
    """Add comment to a post"""

    post = db.query(PublicPost).filter(PublicPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        id=str(uuid.uuid4()),
        post_id=post_id,
        text=comment_data.text,
        author_email=comment_data.author_email,
        author_name=comment_data.author_name or "Anonymous"
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        text=comment.text,
        author_name=comment.author_name,
        is_admin=comment.is_admin,
        created_at=comment.created_at
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(post_id: str, db: Session = Depends(get_db_session)):
    """Get comments for a post"""

    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()

    return [
        CommentResponse(
            id=c.id,
            text=c.text,
            author_name=c.author_name,
            is_admin=c.is_admin,
            created_at=c.created_at
        )
        for c in comments
    ]


@router.patch("/posts/{post_id}/status")
async def update_post_status(
    post_id: str,
    status: str,
    admin_email: str,  # Should verify this is board owner
    db: Session = Depends(get_db_session)
):
    """Update post status (admin only)"""

    post = db.query(PublicPost).filter(PublicPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    board = db.query(PublicBoard).filter(PublicBoard.id == post.board_id).first()

    # Verify admin
    if board.owner_email != admin_email:
        raise HTTPException(status_code=403, detail="Not authorized")

    post.status = status
    db.commit()

    # Send WebSocket notification
    await ws_manager.broadcast_event({
        "type": "status_updated",
        "post_id": post_id,
        "status": status
    })

    return {"success": True, "status": status}


@router.get("/boards/{slug}/analytics")
async def get_board_analytics(slug: str, db: Session = Depends(get_db_session)):
    """Get analytics for board (admin only)"""

    board = db.query(PublicBoard).filter(PublicBoard.slug == slug).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Stats
    total_posts = db.query(PublicPost).filter(PublicPost.board_id == board.id).count()
    total_votes = db.query(Vote).join(PublicPost).filter(PublicPost.board_id == board.id).count()
    total_comments = db.query(Comment).join(PublicPost).filter(PublicPost.board_id == board.id).count()

    # Top posts
    top_posts = db.query(PublicPost).filter(
        PublicPost.board_id == board.id
    ).order_by(desc(PublicPost.vote_count)).limit(5).all()

    # Top voters by revenue
    top_voters = db.query(
        Vote.user_email,
        Vote.user_name,
        func.sum(Vote.user_revenue).label('total_revenue'),
        func.count(Vote.id).label('vote_count')
    ).join(PublicPost).filter(
        PublicPost.board_id == board.id
    ).group_by(Vote.user_email, Vote.user_name).order_by(
        desc('total_revenue')
    ).limit(10).all()

    return {
        "board": {
            "id": board.id,
            "slug": board.slug,
            "title": board.title
        },
        "stats": {
            "total_posts": total_posts,
            "total_votes": total_votes,
            "total_comments": total_comments
        },
        "top_posts": [
            {
                "id": p.id,
                "title": p.title,
                "votes": p.vote_count,
                "revenue_score": p.revenue_weighted_score
            }
            for p in top_posts
        ],
        "top_voters": [
            {
                "email": v.user_email,
                "name": v.user_name,
                "total_revenue": float(v.total_revenue),
                "vote_count": v.vote_count
            }
            for v in top_voters
        ]
    }
