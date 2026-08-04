# Public Feedback Board Implementation Guide

**Purpose:** Technical guide for implementing a Canny/UserVoice-style public feedback board in Compass.

**Date:** 2026-08-04

---

## 1. Database Schema

### 1.1 Core Tables

```sql
-- Boards (multiple boards per organization)
CREATE TABLE boards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,  -- URL-friendly name
    description TEXT,
    visibility VARCHAR(20) DEFAULT 'public',  -- public, private, internal
    allow_anonymous_posts BOOLEAN DEFAULT false,
    allow_anonymous_votes BOOLEAN DEFAULT true,
    custom_domain VARCHAR(255),  -- feedback.yourcompany.com
    settings JSONB DEFAULT '{}',  -- Custom settings
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, slug)
);

-- Posts (feature requests, bug reports, etc.)
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id UUID NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    author_email VARCHAR(255),  -- For anonymous posts
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',  -- open, under_review, planned, in_progress, complete, closed
    status_changed_at TIMESTAMP,
    vote_count INT DEFAULT 0,  -- Cached, updated by trigger
    comment_count INT DEFAULT 0,  -- Cached, updated by trigger
    trending_score FLOAT DEFAULT 0,  -- Pre-computed, updated by cron job
    tags TEXT[] DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',  -- Extensible metadata
    merged_into_id UUID REFERENCES posts(id) ON DELETE SET NULL,  -- If merged
    cluster_id UUID REFERENCES clusters(id) ON DELETE SET NULL,  -- NLP clustering
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Votes (one vote per user per post)
CREATE TABLE votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    anonymous_id VARCHAR(255),  -- For anonymous votes (fingerprint)
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(post_id, user_id),  -- Prevent duplicate votes
    UNIQUE(post_id, anonymous_id)  -- Prevent duplicate anonymous votes
);

-- Comments (threaded discussions)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,  -- For threaded replies
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,  -- Private admin notes
    edited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Status History (audit trail)
CREATE TABLE status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    changed_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    note TEXT,  -- Optional explanation
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions (email notifications)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255),  -- For non-users
    notify_on_status_change BOOLEAN DEFAULT true,
    notify_on_comment BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(post_id, user_id),
    UNIQUE(post_id, email)
);
```

### 1.2 Indexes

```sql
-- Performance indexes
CREATE INDEX idx_posts_board_status ON posts(board_id, status);
CREATE INDEX idx_posts_vote_count ON posts(vote_count DESC);
CREATE INDEX idx_posts_trending_score ON posts(trending_score DESC);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_cluster_id ON posts(cluster_id);

CREATE INDEX idx_votes_post_id ON votes(post_id);
CREATE INDEX idx_votes_user_id ON votes(user_id);
CREATE INDEX idx_votes_created_at ON votes(created_at);

CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_post_id ON subscriptions(post_id);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('english', title || ' ' || description));
```

### 1.3 Triggers (Auto-Update Cached Counts)

```sql
-- Trigger to update vote_count when vote is added/removed
CREATE OR REPLACE FUNCTION update_post_vote_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET vote_count = vote_count + 1, updated_at = NOW()
        WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET vote_count = vote_count - 1, updated_at = NOW()
        WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vote_count_trigger
AFTER INSERT OR DELETE ON votes
FOR EACH ROW EXECUTE FUNCTION update_post_vote_count();

-- Trigger to update comment_count
CREATE OR REPLACE FUNCTION update_post_comment_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET comment_count = comment_count + 1, updated_at = NOW()
        WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET comment_count = comment_count - 1, updated_at = NOW()
        WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER comment_count_trigger
AFTER INSERT OR DELETE ON comments
FOR EACH ROW EXECUTE FUNCTION update_post_comment_count();

-- Trigger to record status changes
CREATE OR REPLACE FUNCTION record_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO status_history (post_id, old_status, new_status, changed_by_id)
        VALUES (NEW.id, OLD.status, NEW.status, NULL);  -- TODO: Track changed_by_id
        NEW.status_changed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER status_change_trigger
BEFORE UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION record_status_change();
```

---

## 2. API Endpoints

### 2.1 Public Endpoints (No Auth Required)

```python
# FastAPI router for public board
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

router = APIRouter(prefix="/api/public/boards")

# List boards
@router.get("/{org_slug}/boards")
async def list_boards(org_slug: str):
    """Get all public boards for an organization."""
    boards = await Board.filter(
        organization__slug=org_slug,
        visibility="public"
    ).all()
    return {"boards": boards}

# Get board details
@router.get("/{org_slug}/boards/{board_slug}")
async def get_board(org_slug: str, board_slug: str):
    """Get board details and settings."""
    board = await Board.get(
        organization__slug=org_slug,
        slug=board_slug,
        visibility="public"
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

# List posts (paginated, sorted, filtered)
@router.get("/{org_slug}/boards/{board_slug}/posts")
async def list_posts(
    org_slug: str,
    board_slug: str,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = "votes",  # votes, trending, recent
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get posts from a board."""
    board = await Board.get(organization__slug=org_slug, slug=board_slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    query = Post.filter(board_id=board.id, merged_into_id=None)

    # Filters
    if status:
        query = query.filter(status=status)
    if tag:
        query = query.filter(tags__contains=[tag])

    # Sorting
    if sort == "votes":
        query = query.order_by("-vote_count", "-created_at")
    elif sort == "trending":
        query = query.order_by("-trending_score")
    elif sort == "recent":
        query = query.order_by("-created_at")

    # Pagination
    offset = (page - 1) * limit
    posts = await query.offset(offset).limit(limit).all()
    total = await query.count()

    return {
        "posts": posts,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit
    }

# Get post details
@router.get("/{org_slug}/boards/{board_slug}/posts/{post_id}")
async def get_post(org_slug: str, board_slug: str, post_id: str):
    """Get post details with comments."""
    post = await Post.get(id=post_id, board__slug=board_slug, board__organization__slug=org_slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get comments (threaded)
    comments = await Comment.filter(post_id=post_id, is_internal=False).order_by("created_at").all()

    return {
        "post": post,
        "comments": comments
    }

# Search posts
@router.get("/{org_slug}/boards/{board_slug}/search")
async def search_posts(
    org_slug: str,
    board_slug: str,
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """Full-text search across posts."""
    board = await Board.get(organization__slug=org_slug, slug=board_slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # PostgreSQL full-text search
    posts = await Post.raw(
        """
        SELECT *, ts_rank(to_tsvector('english', title || ' ' || description), query) AS rank
        FROM posts, to_tsquery('english', $1) query
        WHERE board_id = $2
          AND to_tsvector('english', title || ' ' || description) @@ query
          AND merged_into_id IS NULL
        ORDER BY rank DESC
        LIMIT $3
        """,
        [q.replace(" ", " & "), str(board.id), limit]
    )

    return {"posts": posts, "query": q}
```

### 2.2 Authenticated Endpoints (Require Login)

```python
from fastapi import Depends
from .auth import get_current_user, get_optional_user

# Create post
@router.post("/{org_slug}/boards/{board_slug}/posts")
async def create_post(
    org_slug: str,
    board_slug: str,
    title: str,
    description: str,
    tags: List[str] = [],
    user: dict = Depends(get_optional_user)  # Optional for anonymous boards
):
    """Create a new post."""
    board = await Board.get(organization__slug=org_slug, slug=board_slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Check if anonymous posting is allowed
    if not user and not board.allow_anonymous_posts:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check for duplicate (similar title)
    similar_posts = await find_similar_posts(board.id, title)
    if similar_posts:
        return {
            "message": "Similar posts found. Consider voting on an existing post.",
            "similar_posts": similar_posts
        }

    # Create post
    post = await Post.create(
        board_id=board.id,
        author_id=user["id"] if user else None,
        author_email=user["email"] if user else None,
        title=title,
        description=description,
        tags=tags
    )

    # Auto-subscribe author to notifications
    if user:
        await Subscription.create(post_id=post.id, user_id=user["id"])

    # Emit WebSocket event
    await event_emitter.emit("post.created", post, room=f"board:{board.id}")

    return post

# Vote on post
@router.post("/{org_slug}/boards/{board_slug}/posts/{post_id}/vote")
async def vote_post(
    org_slug: str,
    board_slug: str,
    post_id: str,
    user: dict = Depends(get_optional_user),
    anonymous_id: Optional[str] = None  # Browser fingerprint
):
    """Add vote to post."""
    post = await Post.get(id=post_id, board__slug=board_slug, board__organization__slug=org_slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if anonymous voting is allowed
    board = await Board.get(id=post.board_id)
    if not user and not board.allow_anonymous_votes:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Rate limit check
    if not await check_rate_limit(user["id"] if user else anonymous_id, "vote"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Try to create vote
    try:
        vote = await Vote.create(
            post_id=post_id,
            user_id=user["id"] if user else None,
            anonymous_id=anonymous_id if not user else None
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already voted")

    # Vote count is auto-updated by trigger
    updated_post = await Post.get(id=post_id)

    # Emit WebSocket event
    await event_emitter.emit("vote.added", {
        "post_id": post_id,
        "vote_count": updated_post.vote_count
    }, room=f"board:{board.id}")

    return {"success": True, "vote_count": updated_post.vote_count}

# Remove vote
@router.delete("/{org_slug}/boards/{board_slug}/posts/{post_id}/vote")
async def unvote_post(
    org_slug: str,
    board_slug: str,
    post_id: str,
    user: dict = Depends(get_current_user)
):
    """Remove vote from post."""
    vote = await Vote.get(post_id=post_id, user_id=user["id"])
    if not vote:
        raise HTTPException(status_code=400, detail="Not voted")

    await vote.delete()

    # Vote count is auto-updated by trigger
    updated_post = await Post.get(id=post_id)

    # Emit WebSocket event
    await event_emitter.emit("vote.removed", {
        "post_id": post_id,
        "vote_count": updated_post.vote_count
    }, room=f"board:{post.board_id}")

    return {"success": True, "vote_count": updated_post.vote_count}

# Add comment
@router.post("/{org_slug}/boards/{board_slug}/posts/{post_id}/comments")
async def create_comment(
    org_slug: str,
    board_slug: str,
    post_id: str,
    content: str,
    parent_id: Optional[str] = None,  # For threaded replies
    user: dict = Depends(get_current_user)
):
    """Add comment to post."""
    post = await Post.get(id=post_id, board__slug=board_slug, board__organization__slug=org_slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create comment
    comment = await Comment.create(
        post_id=post_id,
        author_id=user["id"],
        parent_id=parent_id,
        content=content
    )

    # Notify subscribers (except author)
    await notify_subscribers(post_id, "comment", exclude_user_id=user["id"])

    # Emit WebSocket event
    await event_emitter.emit("comment.added", comment, room=f"post:{post_id}")

    return comment
```

### 2.3 Admin Endpoints (Require Admin Role)

```python
from .auth import require_admin

# Update post status
@router.patch("/{org_slug}/boards/{board_slug}/posts/{post_id}/status")
async def update_post_status(
    org_slug: str,
    board_slug: str,
    post_id: str,
    status: str,
    note: Optional[str] = None,
    user: dict = Depends(require_admin)
):
    """Update post status (admin only)."""
    post = await Post.get(id=post_id, board__slug=board_slug, board__organization__slug=org_slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    old_status = post.status
    post.status = status
    await post.save()

    # Record in status history
    await StatusHistory.create(
        post_id=post_id,
        old_status=old_status,
        new_status=status,
        changed_by_id=user["id"],
        note=note
    )

    # Notify subscribers
    await notify_subscribers(post_id, "status_change", status=status)

    # Emit WebSocket event
    await event_emitter.emit("post.status_changed", {
        "post_id": post_id,
        "old_status": old_status,
        "new_status": status
    }, room=f"board:{post.board_id}")

    return post

# Merge duplicate posts
@router.post("/{org_slug}/boards/{board_slug}/posts/{post_id}/merge")
async def merge_posts(
    org_slug: str,
    board_slug: str,
    post_id: str,  # Source post (will be merged)
    target_post_id: str,  # Target post (will receive votes)
    user: dict = Depends(require_admin)
):
    """Merge duplicate posts (admin only)."""
    source = await Post.get(id=post_id)
    target = await Post.get(id=target_post_id)

    if not source or not target:
        raise HTTPException(status_code=404, detail="Post not found")

    # Transfer votes
    await Vote.filter(post_id=post_id).update(post_id=target_post_id)

    # Transfer comments
    await Comment.filter(post_id=post_id).update(post_id=target_post_id)

    # Mark source as merged
    source.merged_into_id = target_post_id
    await source.save()

    # Refresh target vote count (trigger will update)
    target = await Post.get(id=target_post_id)

    # Notify subscribers of both posts
    await notify_subscribers(post_id, "merged", target_post_id=target_post_id)

    return {"success": True, "target_post": target}

# Delete post
@router.delete("/{org_slug}/boards/{board_slug}/posts/{post_id}")
async def delete_post(
    org_slug: str,
    board_slug: str,
    post_id: str,
    user: dict = Depends(require_admin)
):
    """Delete post (admin only)."""
    post = await Post.get(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await post.delete()

    # Emit WebSocket event
    await event_emitter.emit("post.deleted", {"post_id": post_id}, room=f"board:{post.board_id}")

    return {"success": True}
```

---

## 3. WebSocket Integration

### 3.1 Room Structure

```python
# WebSocket rooms for public board
{
    "board:{board_id}": [client1, client2, ...],  # All posts in board
    "post:{post_id}": [client1, client2, ...]     # Specific post (for comments)
}
```

### 3.2 Client Subscription

```javascript
// Client subscribes to board updates
ws.send(JSON.stringify({
    action: "subscribe",
    rooms: ["board:abc123"]  // Board ID
}));

// Client subscribes to post updates (for comment section)
ws.send(JSON.stringify({
    action: "subscribe",
    rooms: ["post:def456"]  // Post ID
}));
```

### 3.3 Event Broadcasting

```python
# In API endpoints, emit events after mutations

# New post created
await event_emitter.emit("post.created", {
    "id": post.id,
    "title": post.title,
    "author": post.author.name,
    "vote_count": 0,
    "created_at": post.created_at.isoformat()
}, room=f"board:{board.id}")

# Vote added
await event_emitter.emit("vote.added", {
    "post_id": post.id,
    "vote_count": post.vote_count
}, room=f"board:{board.id}")

# Status changed
await event_emitter.emit("post.status_changed", {
    "post_id": post.id,
    "old_status": old_status,
    "new_status": new_status,
    "changed_by": user.name
}, room=f"board:{board.id}")

# Comment added
await event_emitter.emit("comment.added", {
    "post_id": post.id,
    "comment_id": comment.id,
    "author": comment.author.name,
    "content": comment.content,
    "created_at": comment.created_at.isoformat()
}, room=f"post:{post.id}")
```

---

## 4. Trending Score Calculation

### 4.1 Algorithm (Hacker News-style)

```python
import math
from datetime import datetime, timezone

def calculate_trending_score(post):
    """
    Calculate trending score for a post.
    Similar to Hacker News ranking algorithm.
    """
    # Engagement = votes + (comments * 2)
    engagement = post.vote_count + (post.comment_count * 2)

    # Time decay (penalize older posts)
    age_hours = (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600
    gravity = 1.8  # Decay rate (higher = faster decay)

    # Trending score
    score = engagement / ((age_hours + 2) ** gravity)

    return score
```

### 4.2 Batch Update (Cron Job)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("interval", minutes=5)
async def update_trending_scores():
    """Update trending scores for all posts (every 5 minutes)."""
    posts = await Post.filter(
        status__in=["open", "under_review"],
        merged_into_id=None
    ).all()

    for post in posts:
        score = calculate_trending_score(post)
        post.trending_score = score
        await post.save()

    print(f"Updated trending scores for {len(posts)} posts")

# Start scheduler
scheduler.start()
```

---

## 5. Duplicate Detection (NLP-Based)

### 5.1 Using Existing Compass Clustering

```python
from backend.nlp.clustering import generate_embedding

async def find_similar_posts(board_id: str, title: str, threshold: float = 0.85):
    """
    Find similar posts using semantic similarity.
    Reuses Compass's existing NLP pipeline.
    """
    # Generate embedding for new post title
    new_embedding = generate_embedding(title)

    # Get all posts in board
    posts = await Post.filter(board_id=board_id, merged_into_id=None).all()

    similar_posts = []
    for post in posts:
        # Generate embedding for existing post
        existing_embedding = generate_embedding(post.title)

        # Cosine similarity
        similarity = cosine_similarity(new_embedding, existing_embedding)

        if similarity >= threshold:
            similar_posts.append({
                "post": post,
                "similarity": similarity
            })

    # Sort by similarity (descending)
    similar_posts.sort(key=lambda x: x["similarity"], reverse=True)

    return similar_posts[:5]  # Top 5 similar posts
```

### 5.2 Auto-Suggest on Post Creation

```python
# In create_post endpoint
@router.post("/{org_slug}/boards/{board_slug}/posts")
async def create_post(
    org_slug: str,
    board_slug: str,
    title: str,
    description: str,
    check_duplicates: bool = True,
    user: dict = Depends(get_optional_user)
):
    board = await Board.get(organization__slug=org_slug, slug=board_slug)

    # Check for duplicates before creating
    if check_duplicates:
        similar_posts = await find_similar_posts(board.id, title)

        if similar_posts:
            return {
                "message": "Similar posts found. Consider voting on an existing post instead.",
                "similar_posts": [
                    {
                        "id": sp["post"].id,
                        "title": sp["post"].title,
                        "vote_count": sp["post"].vote_count,
                        "similarity": sp["similarity"]
                    }
                    for sp in similar_posts
                ],
                "action": "confirm_create"  # Frontend can show confirmation dialog
            }

    # Create post if no duplicates or user confirms
    post = await Post.create(...)
    return post
```

---

## 6. Email Notifications

### 6.1 SendGrid Template

```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

async def send_status_change_email(post_id: str, new_status: str):
    """Send email to all subscribers when post status changes."""
    post = await Post.get(id=post_id)
    subscribers = await Subscription.filter(
        post_id=post_id,
        notify_on_status_change=True
    ).all()

    for sub in subscribers:
        # Get user email
        email = sub.user.email if sub.user else sub.email

        # Send email via SendGrid
        message = Mail(
            from_email='notifications@compass.app',
            to_emails=email,
            subject=f'Post status updated: {post.title}',
            html_content=f"""
            <h2>Status Update</h2>
            <p>The post you're following has been updated:</p>
            <h3>{post.title}</h3>
            <p><strong>New Status:</strong> {new_status}</p>
            <p><a href="https://feedback.yourcompany.com/posts/{post_id}">View Post</a></p>
            <hr>
            <p><small><a href="https://feedback.yourcompany.com/unsubscribe/{sub.id}">Unsubscribe</a></small></p>
            """
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"Email sent to {email}: {response.status_code}")
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
```

### 6.2 Notification Preferences

```python
# User can configure notification preferences
@router.patch("/api/subscriptions/{subscription_id}")
async def update_subscription_preferences(
    subscription_id: str,
    notify_on_status_change: bool = True,
    notify_on_comment: bool = False,
    user: dict = Depends(get_current_user)
):
    """Update notification preferences for a subscription."""
    sub = await Subscription.get(id=subscription_id, user_id=user["id"])
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub.notify_on_status_change = notify_on_status_change
    sub.notify_on_comment = notify_on_comment
    await sub.save()

    return sub
```

---

## 7. Rate Limiting & Spam Prevention

### 7.1 Redis-Based Rate Limiting

```python
import redis
from fastapi import HTTPException

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def check_rate_limit(user_id: str, action: str = "vote", limit: int = 10, window: int = 3600):
    """
    Check if user has exceeded rate limit.

    Args:
        user_id: User or anonymous ID
        action: Action type (vote, post, comment)
        limit: Max actions per window
        window: Time window in seconds (default: 1 hour)

    Returns:
        True if allowed, False if rate limited
    """
    key = f"rate_limit:{action}:{user_id}"
    current_count = redis_client.get(key)

    if current_count is None:
        # First action in window
        redis_client.setex(key, window, 1)
        return True
    elif int(current_count) < limit:
        # Increment count
        redis_client.incr(key)
        return True
    else:
        # Rate limited
        return False
```

### 7.2 Spam Detection (Simple Heuristics)

```python
async def is_spam(content: str, user_id: str = None) -> bool:
    """
    Detect if content is likely spam.
    """
    # Check for common spam patterns
    spam_keywords = ["viagra", "casino", "lottery", "click here", "free money"]
    content_lower = content.lower()

    for keyword in spam_keywords:
        if keyword in content_lower:
            return True

    # Check for excessive URLs
    url_count = content.count("http://") + content.count("https://")
    if url_count > 3:
        return True

    # Check for excessive capitalization
    if sum(1 for c in content if c.isupper()) / len(content) > 0.5:
        return True

    # Check user history (if available)
    if user_id:
        recent_posts = await Post.filter(
            author_id=user_id,
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).count()

        if recent_posts > 5:  # More than 5 posts in 1 hour
            return True

    return False
```

### 7.3 Shadow Banning

```python
# Add to users table
ALTER TABLE users ADD COLUMN is_shadow_banned BOOLEAN DEFAULT false;

# In vote endpoint
@router.post("/{org_slug}/boards/{board_slug}/posts/{post_id}/vote")
async def vote_post(...):
    user = await User.get(id=user_id)

    # Shadow banned users think their vote worked, but it doesn't actually count
    if user.is_shadow_banned:
        return {"success": True, "vote_count": post.vote_count}  # Fake success

    # Normal vote logic
    vote = await Vote.create(...)
    return {"success": True, "vote_count": post.vote_count + 1}
```

---

## 8. Frontend Components (React Example)

### 8.1 PostList Component

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWebSocket } from './hooks/useWebSocket';

export default function PostList({ boardSlug }) {
  const [posts, setPosts] = useState([]);
  const [sort, setSort] = useState('votes');
  const [status, setStatus] = useState(null);

  // Fetch posts
  useEffect(() => {
    fetchPosts();
  }, [sort, status]);

  const fetchPosts = async () => {
    const params = { sort, status };
    const response = await axios.get(`/api/public/boards/${boardSlug}/posts`, { params });
    setPosts(response.data.posts);
  };

  // WebSocket for real-time updates
  const { lastMessage } = useWebSocket(`board:${boardSlug}`);

  useEffect(() => {
    if (lastMessage) {
      const { event, data } = JSON.parse(lastMessage.data);

      if (event === 'post.created') {
        setPosts(prev => [data, ...prev]);
      } else if (event === 'vote.added') {
        setPosts(prev => prev.map(post =>
          post.id === data.post_id
            ? { ...post, vote_count: data.vote_count }
            : post
        ));
      } else if (event === 'post.status_changed') {
        setPosts(prev => prev.map(post =>
          post.id === data.post_id
            ? { ...post, status: data.new_status }
            : post
        ));
      }
    }
  }, [lastMessage]);

  return (
    <div className="post-list">
      {/* Filters */}
      <div className="filters">
        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="votes">Most Votes</option>
          <option value="trending">Trending</option>
          <option value="recent">Recent</option>
        </select>

        <select value={status || ''} onChange={(e) => setStatus(e.target.value || null)}>
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="planned">Planned</option>
          <option value="in_progress">In Progress</option>
          <option value="complete">Complete</option>
        </select>
      </div>

      {/* Posts */}
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### 8.2 VoteButton Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

export default function VoteButton({ post }) {
  const [voted, setVoted] = useState(post.user_has_voted);
  const [voteCount, setVoteCount] = useState(post.vote_count);
  const [loading, setLoading] = useState(false);

  const handleVote = async () => {
    setLoading(true);

    try {
      if (voted) {
        // Unvote
        await axios.delete(`/api/public/boards/${post.board.slug}/posts/${post.id}/vote`);
        setVoted(false);
        setVoteCount(prev => prev - 1);
      } else {
        // Vote
        const response = await axios.post(`/api/public/boards/${post.board.slug}/posts/${post.id}/vote`);
        setVoted(true);
        setVoteCount(response.data.vote_count);
      }
    } catch (error) {
      if (error.response?.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      } else {
        alert('Error voting. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      className={`vote-button ${voted ? 'voted' : ''}`}
      onClick={handleVote}
      disabled={loading}
    >
      <span className="arrow">▲</span>
      <span className="count">{voteCount}</span>
    </button>
  );
}
```

### 8.3 CreatePostModal Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

export default function CreatePostModal({ boardSlug, onClose, onPostCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [similarPosts, setSimilarPosts] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`/api/public/boards/${boardSlug}/posts`, {
        title,
        description,
        check_duplicates: true
      });

      if (response.data.action === 'confirm_create') {
        // Show similar posts
        setSimilarPosts(response.data.similar_posts);
      } else {
        // Post created successfully
        onPostCreated(response.data);
        onClose();
      }
    } catch (error) {
      alert('Error creating post. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmCreate = async () => {
    setLoading(true);

    try {
      const response = await axios.post(`/api/public/boards/${boardSlug}/posts`, {
        title,
        description,
        check_duplicates: false  // Skip duplicate check
      });

      onPostCreated(response.data);
      onClose();
    } catch (error) {
      alert('Error creating post. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Create New Post</h2>

        {similarPosts.length === 0 ? (
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Post title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            <textarea
              placeholder="Describe your idea or issue..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={5}
            />

            <div className="buttons">
              <button type="button" onClick={onClose}>Cancel</button>
              <button type="submit" disabled={loading}>Create Post</button>
            </div>
          </form>
        ) : (
          <div className="similar-posts">
            <p>We found similar posts. Consider voting on an existing post instead:</p>

            {similarPosts.map(sp => (
              <div key={sp.id} className="similar-post">
                <h4>{sp.title}</h4>
                <p>{sp.vote_count} votes • {(sp.similarity * 100).toFixed(0)}% similar</p>
                <a href={`/posts/${sp.id}`} target="_blank">View Post</a>
              </div>
            ))}

            <div className="buttons">
              <button onClick={() => setSimilarPosts([])}>Go Back</button>
              <button onClick={handleConfirmCreate}>Create Anyway</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 9. Integration with Existing Compass

### 9.1 Link Public Posts to Clusters

```python
# When running NLP clustering, include public board posts
@router.post("/api/clustering/run")
async def run_clustering():
    # Get all feedback from sources (existing)
    feedback_items = await Feedback.all()

    # ALSO get all public board posts
    public_posts = await Post.filter(merged_into_id=None).all()

    # Convert posts to feedback format
    for post in public_posts:
        feedback_items.append({
            "id": post.id,
            "text": f"{post.title} {post.description}",
            "source": "public_board",
            "metadata": {
                "vote_count": post.vote_count,
                "status": post.status
            }
        })

    # Run clustering (existing)
    clusters = await cluster_feedback(feedback_items)

    # Link posts to clusters
    for cluster in clusters:
        for item_id in cluster.item_ids:
            post = await Post.get_or_none(id=item_id)
            if post:
                post.cluster_id = cluster.id
                await post.save()

    return clusters
```

### 9.2 Weighted Priority with Public Board Votes

```python
# Enhanced priority calculation
def calculate_priority(cluster):
    """
    Calculate priority for a cluster, considering public board votes.
    """
    # Get all posts in cluster
    posts = await Post.filter(cluster_id=cluster.id)
    total_votes = sum(post.vote_count for post in posts)

    # Existing Compass priority
    frequency = math.log1p(cluster.feedback_count)
    revenue_weight = math.log1p(cluster.total_revenue)
    sentiment_boost = 1 + (cluster.avg_sentiment * 0.5)  # 1.0 to 1.5x

    # NEW: Public demand multiplier (based on votes)
    public_demand = math.log1p(total_votes) * 0.3  # Add up to 30% boost

    # Final priority
    priority = (frequency * revenue_weight * sentiment_boost + public_demand) / cluster.estimated_effort

    return priority
```

---

## 10. Deployment Checklist

### 10.1 Database

- [x] Create tables (boards, posts, votes, comments, subscriptions, status_history)
- [x] Create indexes
- [x] Create triggers (vote_count, comment_count, status_history)
- [ ] Set up PostgreSQL connection pooling (pgBouncer)
- [ ] Configure backups (daily snapshots)

### 10.2 Backend

- [ ] Implement all API endpoints (public, auth, admin)
- [ ] Add authentication (JWT, OAuth)
- [ ] Add rate limiting (Redis)
- [ ] Add spam detection
- [ ] Integrate with WebSocket system (reuse existing)
- [ ] Set up email notifications (SendGrid)
- [ ] Add cron job for trending scores
- [ ] Add error tracking (Sentry)

### 10.3 Frontend

- [ ] Build public board UI (React)
- [ ] Implement voting UI (real-time updates)
- [ ] Add post creation flow (with duplicate detection)
- [ ] Add comment threads
- [ ] Add admin dashboard (moderation, status updates)
- [ ] Responsive design (mobile-friendly)
- [ ] SEO optimization (meta tags, sitemap)

### 10.4 Integrations

- [ ] Jira integration (bi-directional sync)
- [ ] Linear integration
- [ ] Slack integration (notifications)
- [ ] Zapier integration (webhooks)
- [ ] API documentation (auto-generated via FastAPI)

### 10.5 Launch

- [ ] Set up custom domain (feedback.yourcompany.com)
- [ ] SSL certificate (Let's Encrypt)
- [ ] CDN for static assets (CloudFlare)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Load testing (JMeter, Locust)
- [ ] Security audit (penetration testing)
- [ ] Beta testing (invite-only)
- [ ] Public launch announcement

---

## Conclusion

This implementation guide provides a complete technical blueprint for building a Canny/UserVoice-style public feedback board in Compass. The design leverages existing Compass features (NLP clustering, priority calculation, WebSocket system) while adding public-facing components.

**Key Differentiators:**
1. Revenue-weighted voting (not just vote count)
2. NLP-powered duplicate detection (better than keyword matching)
3. Automatic roadmap generation (AI-driven prioritization)
4. Multi-source feedback aggregation (public board + internal sources)

**Next Steps:**
1. Start with MVP (database + basic API + simple UI)
2. Add real-time features (WebSocket integration)
3. Build admin tools (moderation, status updates)
4. Add integrations (Jira, Slack, Zapier)
5. Launch beta and iterate based on feedback

---

**Author:** Claude (Sonnet 4.5)
**Date:** 2026-08-04
