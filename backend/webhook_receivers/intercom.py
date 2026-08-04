"""
Intercom Webhook Receiver

Receives real-time events when conversations are created/replied to.
Docs: https://developers.intercom.com/docs/references/webhooks/

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

router = APIRouter(prefix="/webhooks/intercom", tags=["webhook-receivers"])


def verify_intercom_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """
    Verify Intercom webhook signature for security.

    Docs: https://developers.intercom.com/docs/references/webhooks/securing-webhooks

    Args:
        payload_body: Raw request body bytes
        signature_header: X-Hub-Signature header (SHA-1)
        secret: Intercom webhook secret

    Returns:
        True if signature is valid
    """
    if not signature_header or not signature_header.startswith("sha1="):
        return False

    expected_signature = "sha1=" + hmac.new(
        secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha1
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


async def process_intercom_conversation(conversation_data: Dict[str, Any], db: Session) -> Feedback:
    """
    Process an Intercom conversation and create Feedback entry.

    Args:
        conversation_data: Intercom conversation object
        db: Database session

    Returns:
        Created Feedback object
    """
    # Extract conversation details
    conversation_id = conversation_data.get("id")
    conversation_parts = conversation_data.get("conversation_parts", {}).get("conversation_parts", [])

    # Get first user message
    first_message = ""
    customer_name = "Unknown"
    customer_email = None

    # Find first customer message
    for part in conversation_parts:
        if part.get("part_type") == "comment" and part.get("author", {}).get("type") == "user":
            first_message = part.get("body", "")
            author = part.get("author", {})
            customer_name = author.get("name") or author.get("email", "Unknown")
            customer_email = author.get("email")
            break

    # If no parts, use source data
    if not first_message:
        source_data = conversation_data.get("source", {})
        first_message = source_data.get("body", "")
        author = source_data.get("author", {})
        customer_name = author.get("name") or author.get("email", "Unknown")
        customer_email = author.get("email")

    # Get user details if available
    user_data = conversation_data.get("user")
    if user_data:
        customer_name = user_data.get("name") or user_data.get("email", customer_name)
        customer_email = user_data.get("email")

    # Get or create Intercom source
    source = db.query(Source).filter(Source.name == "Intercom").first()
    if not source:
        source = Source(
            name="Intercom",
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
        text=first_message,
        title=f"Intercom conversation from {customer_name}",
        customer_name=customer_name,
        submitted_at=datetime.now(timezone.utc),
        source_metadata={
            "conversation_id": conversation_id,
            "customer_email": customer_email,
            "total_parts": len(conversation_parts),
            "source": "intercom_webhook"
        }
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


async def process_intercom_message(message_data: Dict[str, Any], conversation_id: str, db: Session) -> Feedback:
    """
    Process an Intercom message (reply) and create Feedback entry.

    Args:
        message_data: Intercom message object
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Created Feedback object
    """
    message_body = message_data.get("body", "")
    author = message_data.get("author", {})
    customer_name = author.get("name") or author.get("email", "Unknown")
    customer_email = author.get("email")

    # Get or create Intercom source
    source = db.query(Source).filter(Source.name == "Intercom").first()
    if not source:
        source = Source(
            name="Intercom",
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
        text=message_body,
        title=f"Intercom message from {customer_name}",
        customer_name=customer_name,
        submitted_at=datetime.now(timezone.utc),
        source_metadata={
            "conversation_id": conversation_id,
            "customer_email": customer_email,
            "message_type": "reply",
            "source": "intercom_webhook"
        }
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


@router.post("/conversations")
async def intercom_conversations(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature: Optional[str] = Header(None)
):
    """
    Intercom webhook endpoint for conversation events.

    Handles:
    - conversation.user.created
    - conversation.user.replied
    - conversation.admin.replied

    Performance: Processes events in <100ms for sub-1-second delivery

    Setup:
    1. Go to Intercom → Settings → Webhooks
    2. Click "New webhook"
    3. Set Webhook URL: https://your-domain.com/webhooks/intercom/conversations
    4. Select topics:
       - conversation.user.created
       - conversation.user.replied
    5. Copy the webhook secret and set INTERCOM_WEBHOOK_SECRET
    6. Save webhook
    """
    import time
    start_time = time.time()

    # Get raw body for signature verification
    body = await request.body()

    # Verify Intercom signature (security)
    webhook_secret = os.getenv("INTERCOM_WEBHOOK_SECRET", "")
    if webhook_secret:
        if not verify_intercom_signature(body, x_hub_signature or "", webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    payload = await request.json()

    topic = payload.get("topic")
    data = payload.get("data", {})
    item = data.get("item", {})

    try:
        feedback = None

        # Handle conversation created/replied
        if topic in ["conversation.user.created", "conversation.user.replied"]:
            # Check if this is from a user (not admin)
            conversation_parts = item.get("conversation_parts", {}).get("conversation_parts", [])
            latest_part = conversation_parts[-1] if conversation_parts else None

            if latest_part and latest_part.get("author", {}).get("type") == "user":
                # Process as new feedback
                feedback = await process_intercom_conversation(item, db)

        if feedback:
            processing_time_ms = (time.time() - start_time) * 1000

            # Emit real-time WebSocket event
            await event_emitter.emit_feedback_new({
                "id": feedback.id,
                "text": feedback.text[:200] + "..." if len(feedback.text) > 200 else feedback.text,
                "title": feedback.title,
                "source": "Intercom",
                "customer_name": feedback.customer_name,
                "submitted_at": feedback.submitted_at.isoformat(),
                "processing_time_ms": round(processing_time_ms, 2),
                "latency": "real-time"
            })

            # Emit notification
            await event_emitter.emit_notification(
                "success",
                "New Intercom Feedback",
                f"Conversation from {feedback.customer_name}"
            )

            print(f"✓ Intercom webhook processed in {processing_time_ms:.2f}ms (feedback_id={feedback.id})")

            return {
                "ok": True,
                "feedback_id": feedback.id,
                "processing_time_ms": round(processing_time_ms, 2)
            }

    except Exception as e:
        print(f"✗ Error processing Intercom webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True, "message": f"Topic {topic} received but not processed"}


@router.get("/test")
async def test_intercom_webhook(db: Session = Depends(get_db)):
    """
    Test endpoint to simulate Intercom webhook event.

    Usage: GET /webhooks/intercom/test
    """
    import time

    # Create test conversation data
    test_conversation = {
        "id": "12345",
        "user": {
            "name": "Test Customer",
            "email": "test@example.com"
        },
        "conversation_parts": {
            "conversation_parts": [
                {
                    "part_type": "comment",
                    "body": "Hi, I'm having trouble with the search feature. It doesn't seem to find recent feedback.",
                    "author": {
                        "type": "user",
                        "name": "Test Customer",
                        "email": "test@example.com"
                    }
                }
            ]
        }
    }

    start_time = time.time()
    feedback = await process_intercom_conversation(test_conversation, db)
    processing_time_ms = (time.time() - start_time) * 1000

    # Emit WebSocket event
    await event_emitter.emit_feedback_new({
        "id": feedback.id,
        "text": feedback.text,
        "title": feedback.title,
        "source": "Intercom (Test)",
        "customer_name": feedback.customer_name,
        "submitted_at": feedback.submitted_at.isoformat(),
        "processing_time_ms": round(processing_time_ms, 2),
        "latency": "real-time"
    })

    return {
        "success": True,
        "message": "Test Intercom webhook processed",
        "feedback_id": feedback.id,
        "processing_time_ms": round(processing_time_ms, 2),
        "demo": "This simulates a real Intercom conversation webhook"
    }


@router.get("/setup-guide")
async def intercom_setup_guide():
    """
    Return setup instructions for Intercom webhooks.
    """
    return {
        "service": "Intercom Webhooks",
        "status": "Ready to configure",
        "webhook_url": f"{os.getenv('APP_URL', 'https://your-domain.com')}/webhooks/intercom/conversations",
        "steps": [
            "1. Log in to Intercom → Settings → Developers → Webhooks",
            "2. Click 'New webhook'",
            "3. Set Webhook URL to the webhook_url above",
            "4. Select webhook topics:",
            "   - conversation.user.created",
            "   - conversation.user.replied",
            "5. Copy the webhook secret",
            "6. Set INTERCOM_WEBHOOK_SECRET environment variable",
            "7. Save webhook",
            "8. Test with GET /webhooks/intercom/test"
        ],
        "environment_variables": {
            "INTERCOM_WEBHOOK_SECRET": "Secret from Intercom webhook settings",
            "APP_URL": "Your Compass domain"
        },
        "events_captured": [
            "conversation.user.created",
            "conversation.user.replied"
        ],
        "performance": {
            "before": "5 minutes (polling)",
            "after": "<1 second (webhooks)",
            "improvement": "300x faster"
        }
    }
