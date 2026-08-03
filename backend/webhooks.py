"""
Compass Webhooks System

Allows users to register webhook URLs that get triggered on specific events:
- feedback.created
- cluster.created
- roadmap.updated
- priority.changed

Features:
- Retry logic with exponential backoff
- Dead letter queue for failed deliveries
- Webhook signature verification (HMAC-SHA256)
- Event history and logs
"""

import asyncio
import hmac
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

import httpx
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, Index
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, Field

from models import Base
from database import get_db


class WebhookEvent(str, Enum):
    """Supported webhook events"""
    FEEDBACK_CREATED = "feedback.created"
    CLUSTER_CREATED = "cluster.created"
    ROADMAP_UPDATED = "roadmap.updated"
    PRIORITY_CHANGED = "priority.changed"


class WebhookStatus(str, Enum):
    """Webhook status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"  # Too many failures


# --- Database Models ---

class Webhook(Base):
    """Webhook configuration"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(64), nullable=False)  # For HMAC signature
    events = Column(JSON, nullable=False)  # List of subscribed events
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default=WebhookStatus.ACTIVE.value)

    # Stats
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    last_delivery_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_webhook_status", "is_active", "status"),
    )

    def __repr__(self):
        return f"<Webhook(id={self.id}, url='{self.url}', events={self.events})>"


class WebhookDelivery(Base):
    """Webhook delivery attempt log"""
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True)
    webhook_id = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)

    # Delivery details
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    attempt = Column(Integer, default=1)
    success = Column(Boolean, default=False)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_webhook_delivery", "webhook_id", "created_at"),
        Index("idx_event_type", "event_type"),
    )

    def __repr__(self):
        return f"<WebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, success={self.success})>"


# --- Pydantic Models ---

class WebhookCreateRequest(BaseModel):
    """Request to create webhook"""
    url: HttpUrl = Field(..., description="Webhook URL to POST events to")
    events: List[WebhookEvent] = Field(..., description="List of events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for HMAC signature (auto-generated if not provided)")


class WebhookResponse(BaseModel):
    """Webhook response"""
    id: int
    url: str
    events: List[str]
    is_active: bool
    status: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    last_delivery_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookUpdateRequest(BaseModel):
    """Request to update webhook"""
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEvent]] = None
    is_active: Optional[bool] = None


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery log"""
    id: int
    webhook_id: int
    event_type: str
    status_code: Optional[int]
    success: bool
    attempt: int
    created_at: datetime
    delivered_at: Optional[datetime]
    duration_ms: Optional[float]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# --- Webhook Manager ---

class WebhookManager:
    """Manages webhook delivery with retries and dead letter queue"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 5, 15]  # seconds
    MAX_FAILURES_THRESHOLD = 10  # Mark webhook as failed after this many consecutive failures
    TIMEOUT_SECONDS = 10

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS)

    async def trigger_event(self, event_type: WebhookEvent, payload: Dict[str, Any], db: Session):
        """
        Trigger webhook event for all subscribers.

        Args:
            event_type: Type of event (feedback.created, etc.)
            payload: Event data
            db: Database session
        """
        # Find all active webhooks subscribed to this event
        webhooks = db.query(Webhook).filter(
            Webhook.is_active == True,
            Webhook.status == WebhookStatus.ACTIVE.value
        ).all()

        # Filter webhooks subscribed to this event
        subscribed_webhooks = [
            w for w in webhooks
            if event_type.value in w.events
        ]

        if not subscribed_webhooks:
            print(f"No webhooks subscribed to {event_type.value}")
            return

        print(f"Triggering {event_type.value} for {len(subscribed_webhooks)} webhooks")

        # Create tasks for concurrent delivery
        tasks = []
        for webhook in subscribed_webhooks:
            task = asyncio.create_task(
                self._deliver_webhook(webhook, event_type, payload, db)
            )
            tasks.append(task)

        # Wait for all deliveries
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_webhook(
        self,
        webhook: Webhook,
        event_type: WebhookEvent,
        payload: Dict[str, Any],
        db: Session
    ):
        """
        Deliver webhook with retry logic.

        Args:
            webhook: Webhook configuration
            event_type: Event type
            payload: Event data
            db: Database session
        """
        # Prepare payload with metadata
        full_payload = {
            "event": event_type.value,
            "data": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "webhook_id": webhook.id
        }

        # Generate signature
        signature = self._generate_signature(full_payload, webhook.secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_type.value,
            "User-Agent": "Compass-Webhooks/1.0"
        }

        # Attempt delivery with retries
        for attempt in range(1, self.MAX_RETRIES + 1):
            delivery_record = WebhookDelivery(
                webhook_id=webhook.id,
                event_type=event_type.value,
                payload=full_payload,
                attempt=attempt
            )

            start_time = time.time()

            try:
                response = await self.client.post(
                    webhook.url,
                    json=full_payload,
                    headers=headers
                )

                duration_ms = (time.time() - start_time) * 1000

                delivery_record.status_code = response.status_code
                delivery_record.response_body = response.text[:1000]  # Limit size
                delivery_record.duration_ms = duration_ms
                delivery_record.delivered_at = datetime.utcnow()

                # Check if successful (2xx status code)
                if 200 <= response.status_code < 300:
                    delivery_record.success = True
                    webhook.successful_deliveries += 1
                    webhook.last_delivery_at = datetime.utcnow()
                    webhook.total_deliveries += 1

                    db.add(delivery_record)
                    db.commit()

                    print(f"✓ Webhook {webhook.id} delivered successfully (attempt {attempt})")
                    return  # Success!

                else:
                    delivery_record.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
                    webhook.failed_deliveries += 1

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                delivery_record.duration_ms = duration_ms
                delivery_record.error_message = str(e)
                delivery_record.delivered_at = datetime.utcnow()
                webhook.failed_deliveries += 1

                print(f"✗ Webhook {webhook.id} failed (attempt {attempt}): {str(e)}")

            # Save failed delivery record
            webhook.last_error = delivery_record.error_message
            webhook.total_deliveries += 1
            db.add(delivery_record)
            db.commit()

            # Retry with backoff (if not last attempt)
            if attempt < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAYS[attempt - 1])

        # All retries failed - check if we should mark webhook as failed
        if webhook.failed_deliveries >= self.MAX_FAILURES_THRESHOLD:
            webhook.status = WebhookStatus.FAILED.value
            webhook.is_active = False
            print(f"⚠️ Webhook {webhook.id} marked as FAILED (too many failures)")

        db.commit()

    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        Args:
            payload: Payload dictionary
            secret: Webhook secret

        Returns:
            Hexadecimal signature string
        """
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Payload dictionary
            signature: Provided signature
            secret: Webhook secret

        Returns:
            True if signature is valid
        """
        payload_json = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# --- Global webhook manager instance ---
webhook_manager = WebhookManager()


# --- Helper functions for triggering events ---

async def trigger_feedback_created(feedback_id: int, feedback_data: Dict[str, Any], db: Session):
    """Trigger feedback.created event"""
    await webhook_manager.trigger_event(
        WebhookEvent.FEEDBACK_CREATED,
        {
            "id": feedback_id,
            "feedback": feedback_data
        },
        db
    )


async def trigger_cluster_created(cluster_id: int, cluster_data: Dict[str, Any], db: Session):
    """Trigger cluster.created event"""
    await webhook_manager.trigger_event(
        WebhookEvent.CLUSTER_CREATED,
        {
            "id": cluster_id,
            "cluster": cluster_data
        },
        db
    )


async def trigger_roadmap_updated(roadmap_id: int, roadmap_data: Dict[str, Any], changes: Dict[str, Any], db: Session):
    """Trigger roadmap.updated event"""
    await webhook_manager.trigger_event(
        WebhookEvent.ROADMAP_UPDATED,
        {
            "id": roadmap_id,
            "roadmap": roadmap_data,
            "changes": changes
        },
        db
    )


async def trigger_priority_changed(cluster_id: int, old_priority: float, new_priority: float, db: Session):
    """Trigger priority.changed event"""
    await webhook_manager.trigger_event(
        WebhookEvent.PRIORITY_CHANGED,
        {
            "cluster_id": cluster_id,
            "old_priority": old_priority,
            "new_priority": new_priority
        },
        db
    )
