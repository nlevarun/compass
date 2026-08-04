"""
GitHub Webhook Receiver

Receives real-time events when issues are created/commented.
Docs: https://docs.github.com/en/webhooks

Replaces: 5-minute polling → <1 second real-time delivery
"""

import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os

from database import get_db
from models import Feedback, Source
from events import event_emitter

router = APIRouter(prefix="/webhooks/github", tags=["webhook-receivers"])


def verify_github_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """
    Verify GitHub webhook signature for security.

    Docs: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries

    Args:
        payload_body: Raw request body bytes
        signature_header: X-Hub-Signature-256 header
        secret: GitHub webhook secret

    Returns:
        True if signature is valid
    """
    if not signature_header:
        return False

    hash_object = hmac.new(secret.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


async def process_github_issue(issue_data: Dict[str, Any], action: str, db: Session) -> Feedback:
    """
    Process a GitHub issue and create Feedback entry.

    Args:
        issue_data: GitHub issue object
        action: Action type (opened, edited, etc.)
        db: Database session

    Returns:
        Created Feedback object
    """
    title = issue_data.get("title", "")
    body = issue_data.get("body", "") or ""
    user = issue_data.get("user", {}).get("login", "unknown")
    issue_number = issue_data.get("number")
    issue_url = issue_data.get("html_url")
    labels = [label.get("name") for label in issue_data.get("labels", [])]
    created_at = issue_data.get("created_at")

    # Get or create GitHub source
    source = db.query(Source).filter(Source.name == "GitHub").first()
    if not source:
        source = Source(
            name="GitHub",
            source_type="real",
            is_active=True,
            config={}
        )
        db.add(source)
        db.commit()
        db.refresh(source)

    # Combine title and body for feedback text
    feedback_text = f"{title}\n\n{body}"

    # Create feedback entry
    feedback = Feedback(
        source_id=source.id,
        text=feedback_text,
        title=title,
        customer_name=user,
        submitted_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now(timezone.utc),
        source_metadata={
            "issue_number": issue_number,
            "issue_url": issue_url,
            "labels": labels,
            "action": action,
            "source": "github_webhook"
        }
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


async def process_github_issue_comment(issue_data: Dict[str, Any], comment_data: Dict[str, Any], db: Session) -> Feedback:
    """
    Process a GitHub issue comment and create Feedback entry.

    Args:
        issue_data: GitHub issue object
        comment_data: GitHub comment object
        db: Database session

    Returns:
        Created Feedback object
    """
    issue_title = issue_data.get("title", "")
    comment_body = comment_data.get("body", "")
    user = comment_data.get("user", {}).get("login", "unknown")
    issue_number = issue_data.get("number")
    comment_url = comment_data.get("html_url")
    created_at = comment_data.get("created_at")

    # Get or create GitHub source
    source = db.query(Source).filter(Source.name == "GitHub").first()
    if not source:
        source = Source(
            name="GitHub",
            source_type="real",
            is_active=True,
            config={}
        )
        db.add(source)
        db.commit()
        db.refresh(source)

    # Create feedback entry
    feedback = Feedback(
        source_id=source.id,
        text=comment_body,
        title=f"Comment on: {issue_title}",
        customer_name=user,
        submitted_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now(timezone.utc),
        source_metadata={
            "issue_number": issue_number,
            "comment_url": comment_url,
            "issue_title": issue_title,
            "source": "github_webhook_comment"
        }
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


@router.post("/issues")
async def github_issues(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint for issue events.

    Handles:
    - issues (opened, edited)
    - issue_comment (created)

    Performance: Processes events in <100ms for sub-1-second delivery

    Setup:
    1. Go to GitHub repo → Settings → Webhooks → Add webhook
    2. Payload URL: https://your-domain.com/webhooks/github/issues
    3. Content type: application/json
    4. Secret: Generate and set in GITHUB_WEBHOOK_SECRET
    5. Select events: Issues, Issue comments
    6. Active: Check
    """
    import time
    start_time = time.time()

    # Get raw body for signature verification
    body = await request.body()

    # Verify GitHub signature (security)
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    if webhook_secret:
        if not verify_github_signature(body, x_hub_signature_256 or "", webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    payload = await request.json()

    event_type = x_github_event
    action = payload.get("action")

    try:
        feedback = None

        # Handle issue events
        if event_type == "issues" and action in ["opened", "edited"]:
            issue = payload.get("issue", {})
            feedback = await process_github_issue(issue, action, db)

        # Handle issue comment events
        elif event_type == "issue_comment" and action == "created":
            issue = payload.get("issue", {})
            comment = payload.get("comment", {})
            feedback = await process_github_issue_comment(issue, comment, db)

        if feedback:
            processing_time_ms = (time.time() - start_time) * 1000

            # Emit real-time WebSocket event
            await event_emitter.emit_feedback_new({
                "id": feedback.id,
                "text": feedback.text[:200] + "..." if len(feedback.text) > 200 else feedback.text,
                "title": feedback.title,
                "source": "GitHub",
                "customer_name": feedback.customer_name,
                "submitted_at": feedback.submitted_at.isoformat(),
                "processing_time_ms": round(processing_time_ms, 2),
                "latency": "real-time"
            })

            # Emit notification
            await event_emitter.emit_notification(
                "success",
                "New GitHub Feedback",
                f"Issue #{feedback.source_metadata.get('issue_number')} from {feedback.customer_name}"
            )

            print(f"✓ GitHub webhook processed in {processing_time_ms:.2f}ms (feedback_id={feedback.id})")

            return {
                "ok": True,
                "feedback_id": feedback.id,
                "processing_time_ms": round(processing_time_ms, 2)
            }

    except Exception as e:
        print(f"✗ Error processing GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True, "message": f"Event {event_type}/{action} received but not processed"}


@router.get("/test")
async def test_github_webhook(db: Session = Depends(get_db)):
    """
    Test endpoint to simulate GitHub webhook event.

    Usage: GET /webhooks/github/test
    """
    import time

    # Create test issue data
    test_issue = {
        "number": 42,
        "title": "Feature Request: Add export to CSV functionality",
        "body": "It would be great if we could export all feedback data to CSV format for analysis in Excel.",
        "user": {"login": "test_user"},
        "html_url": "https://github.com/test/repo/issues/42",
        "labels": [{"name": "enhancement"}, {"name": "feedback"}],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    start_time = time.time()
    feedback = await process_github_issue(test_issue, "opened", db)
    processing_time_ms = (time.time() - start_time) * 1000

    # Emit WebSocket event
    await event_emitter.emit_feedback_new({
        "id": feedback.id,
        "text": feedback.text,
        "title": feedback.title,
        "source": "GitHub (Test)",
        "customer_name": feedback.customer_name,
        "submitted_at": feedback.submitted_at.isoformat(),
        "processing_time_ms": round(processing_time_ms, 2),
        "latency": "real-time"
    })

    return {
        "success": True,
        "message": "Test GitHub webhook processed",
        "feedback_id": feedback.id,
        "processing_time_ms": round(processing_time_ms, 2),
        "demo": "This simulates a real GitHub issue webhook"
    }


@router.get("/setup-guide")
async def github_setup_guide():
    """
    Return setup instructions for GitHub webhooks.
    """
    return {
        "service": "GitHub Webhooks",
        "status": "Ready to configure",
        "webhook_url": f"{os.getenv('APP_URL', 'https://your-domain.com')}/webhooks/github/issues",
        "steps": [
            "1. Go to your GitHub repository",
            "2. Navigate to Settings → Webhooks → Add webhook",
            "3. Set Payload URL to the webhook_url above",
            "4. Set Content type: application/json",
            "5. Generate a secret and set it in GITHUB_WEBHOOK_SECRET environment variable",
            "6. Select individual events: Issues, Issue comments",
            "7. Ensure Active is checked",
            "8. Save webhook",
            "9. Test with GET /webhooks/github/test"
        ],
        "environment_variables": {
            "GITHUB_WEBHOOK_SECRET": "Secret token from GitHub webhook settings",
            "APP_URL": "Your Compass domain"
        },
        "events_captured": [
            "issues (opened, edited)",
            "issue_comment (created)"
        ],
        "performance": {
            "before": "5 minutes (polling)",
            "after": "<1 second (webhooks)",
            "improvement": "300x faster"
        }
    }
