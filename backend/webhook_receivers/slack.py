"""
Slack Event API Webhook Receiver

Receives real-time events from Slack when messages are posted.
Docs: https://api.slack.com/events-api

Replaces: 5-minute polling → <1 second real-time delivery
"""

import hmac
import hashlib
import time
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any
import os

from database import get_db
from models import Feedback, Source
from events import event_emitter

router = APIRouter(prefix="/webhooks/slack", tags=["webhook-receivers"])


def verify_slack_signature(request_body: bytes, timestamp: str, signature: str, signing_secret: str) -> bool:
    """
    Verify Slack request signature for security.

    Docs: https://api.slack.com/authentication/verifying-requests-from-slack

    Args:
        request_body: Raw request body bytes
        timestamp: X-Slack-Request-Timestamp header
        signature: X-Slack-Signature header
        signing_secret: Slack signing secret from environment

    Returns:
        True if signature is valid
    """
    # Prevent replay attacks - reject requests older than 5 minutes
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    # Create signature base string
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"

    # Compute expected signature
    expected_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(expected_signature, signature)


async def process_slack_message(event: Dict[str, Any], db: Session) -> Feedback:
    """
    Process a Slack message and create Feedback entry.

    Args:
        event: Slack message event
        db: Database session

    Returns:
        Created Feedback object
    """
    # Extract message details
    message_text = event.get("text", "")
    user_id = event.get("user")
    channel = event.get("channel")
    timestamp = event.get("ts")
    thread_ts = event.get("thread_ts")

    # Get or create Slack source
    source = db.query(Source).filter(Source.name == "Slack").first()
    if not source:
        source = Source(
            name="Slack",
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
        text=message_text,
        title=f"Slack message from {user_id}",
        customer_name=user_id,
        submitted_at=datetime.now(timezone.utc),
        source_metadata={
            "channel": channel,
            "ts": timestamp,
            "thread_ts": thread_ts,
            "user": user_id,
            "source": "slack_webhook"
        }
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


@router.post("/events")
async def slack_events(request: Request, db: Session = Depends(get_db)):
    """
    Slack Event API webhook endpoint.

    Handles:
    1. URL verification challenge (Slack setup step)
    2. Event callbacks (message.channels, message.im, etc.)

    Performance: Processes events in <100ms for sub-1-second delivery

    Setup:
    1. Go to https://api.slack.com/apps
    2. Create app → Event Subscriptions
    3. Set Request URL: https://your-domain.com/webhooks/slack/events
    4. Subscribe to: message.channels, message.im
    5. Set SLACK_SIGNING_SECRET environment variable
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify Slack signature (security)
    signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
    if signing_secret:
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")

        if not verify_slack_signature(body, timestamp, signature, signing_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    payload = await request.json()

    # Handle URL verification challenge (one-time setup)
    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    # Handle event callbacks
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        event_type = event.get("type")

        # Handle message events
        if event_type == "message":
            # Ignore bot messages and message edits
            if event.get("subtype") in ["bot_message", "message_changed"]:
                return {"ok": True}

            # Process message and create feedback
            start_time = time.time()

            try:
                feedback = await process_slack_message(event, db)

                # Calculate processing time
                processing_time_ms = (time.time() - start_time) * 1000

                # Emit real-time WebSocket event for instant UI update
                await event_emitter.emit_feedback_new({
                    "id": feedback.id,
                    "text": feedback.text,
                    "source": "Slack",
                    "customer_name": feedback.customer_name,
                    "submitted_at": feedback.submitted_at.isoformat(),
                    "processing_time_ms": round(processing_time_ms, 2),
                    "latency": "real-time"  # Badge for UI
                })

                # Emit notification
                await event_emitter.emit_notification(
                    "success",
                    "New Slack Feedback",
                    f"Received feedback from {feedback.customer_name} in {processing_time_ms:.0f}ms"
                )

                print(f"✓ Slack webhook processed in {processing_time_ms:.2f}ms (feedback_id={feedback.id})")

                return {
                    "ok": True,
                    "feedback_id": feedback.id,
                    "processing_time_ms": round(processing_time_ms, 2)
                }

            except Exception as e:
                print(f"✗ Error processing Slack message: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True}


@router.get("/test")
async def test_slack_webhook(db: Session = Depends(get_db)):
    """
    Test endpoint to simulate Slack webhook event.

    Usage: GET /webhooks/slack/test
    """
    # Create test event
    test_event = {
        "text": "Feature request: We need dark mode for the mobile app!",
        "user": "test_user",
        "channel": "feedback",
        "ts": str(time.time()),
        "type": "message"
    }

    start_time = time.time()
    feedback = await process_slack_message(test_event, db)
    processing_time_ms = (time.time() - start_time) * 1000

    # Emit WebSocket event
    await event_emitter.emit_feedback_new({
        "id": feedback.id,
        "text": feedback.text,
        "source": "Slack (Test)",
        "customer_name": feedback.customer_name,
        "submitted_at": feedback.submitted_at.isoformat(),
        "processing_time_ms": round(processing_time_ms, 2),
        "latency": "real-time"
    })

    return {
        "success": True,
        "message": "Test Slack webhook processed",
        "feedback_id": feedback.id,
        "processing_time_ms": round(processing_time_ms, 2),
        "demo": "This simulates a real Slack message webhook"
    }


@router.get("/setup-guide")
async def slack_setup_guide():
    """
    Return setup instructions for Slack webhooks.
    """
    return {
        "service": "Slack Event API",
        "status": "Ready to configure",
        "webhook_url": f"{os.getenv('APP_URL', 'https://your-domain.com')}/webhooks/slack/events",
        "steps": [
            "1. Go to https://api.slack.com/apps",
            "2. Create a new app or select existing app",
            "3. Navigate to 'Event Subscriptions'",
            "4. Enable Events and set Request URL to the webhook_url above",
            "5. Subscribe to bot events: message.channels, message.im",
            "6. Install app to your workspace",
            "7. Set SLACK_SIGNING_SECRET environment variable",
            "8. Test with GET /webhooks/slack/test"
        ],
        "environment_variables": {
            "SLACK_SIGNING_SECRET": "Get from Slack App > Basic Information > Signing Secret",
            "APP_URL": "Your Compass domain (for webhook URL generation)"
        },
        "performance": {
            "before": "5 minutes (polling)",
            "after": "<1 second (webhooks)",
            "improvement": "300x faster"
        }
    }
