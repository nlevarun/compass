"""
Compass SDK - Webhooks Example

Demonstrates webhook creation and management.
"""

from compass_sdk import CompassClient, WebhookEvent
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

# Initialize Flask app for receiving webhooks
app = Flask(__name__)

# Your webhook secret (will be set when creating webhook)
WEBHOOK_SECRET = "your-webhook-secret-here"


@app.route("/webhooks/compass", methods=["POST"])
def handle_webhook():
    """Handle incoming webhook from Compass"""

    # Get signature from headers
    signature = request.headers.get("X-Webhook-Signature")
    event_type = request.headers.get("X-Webhook-Event")

    if not signature:
        return jsonify({"error": "Missing signature"}), 401

    # Verify signature
    payload = request.get_json()
    payload_json = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"error": "Invalid signature"}), 401

    # Process event
    print(f"\n{'=' * 60}")
    print(f"Received webhook: {event_type}")
    print(f"{'=' * 60}")

    if event_type == "feedback.created":
        feedback = payload["data"]["feedback"]
        print(f"New feedback from {feedback['customer_name']}:")
        print(f"  {feedback['text'][:100]}...")

    elif event_type == "cluster.created":
        cluster = payload["data"]["cluster"]
        print(f"New cluster created: {cluster['label']}")
        print(f"  Size: {cluster['size']}, Priority: {cluster['priority_score']:.2f}")

    elif event_type == "roadmap.updated":
        roadmap = payload["data"]["roadmap"]
        changes = payload["data"]["changes"]
        print(f"Roadmap updated: {roadmap['title']}")
        print(f"  Changes: {changes}")

    elif event_type == "priority.changed":
        cluster_id = payload["data"]["cluster_id"]
        old_priority = payload["data"]["old_priority"]
        new_priority = payload["data"]["new_priority"]
        print(f"Priority changed for cluster {cluster_id}:")
        print(f"  {old_priority:.2f} → {new_priority:.2f}")

    return jsonify({"status": "success"}), 200


def setup_webhooks():
    """Setup webhooks using Compass SDK"""

    client = CompassClient(
        api_key="compass_your_api_key_here",
        base_url="http://localhost:8000"
    )

    print("\n" + "=" * 60)
    print("Setting up Compass Webhooks")
    print("=" * 60)

    # Create webhook
    print("\n1. Creating webhook...")
    webhook = client.webhooks.create(
        url="https://your-app.com/webhooks/compass",  # Replace with your URL
        events=[
            WebhookEvent.FEEDBACK_CREATED,
            WebhookEvent.CLUSTER_CREATED,
            WebhookEvent.ROADMAP_UPDATED,
            WebhookEvent.PRIORITY_CHANGED
        ],
        secret=WEBHOOK_SECRET
    )
    print(f"✓ Webhook created with ID: {webhook.id}")
    print(f"  Subscribed to: {', '.join(webhook.events)}")

    # List all webhooks
    print("\n2. Listing all webhooks...")
    webhooks = client.webhooks.list()
    for wh in webhooks:
        print(f"  - #{wh.id}: {wh.url}")
        print(f"    Status: {wh.status}, Active: {wh.is_active}")
        print(f"    Deliveries: {wh.successful_deliveries}/{wh.total_deliveries}")

    # Get webhook details
    print(f"\n3. Getting webhook details...")
    webhook_detail = client.webhooks.get(webhook.id)
    print(f"  URL: {webhook_detail.url}")
    print(f"  Events: {', '.join(webhook_detail.events)}")
    print(f"  Success rate: {webhook_detail.successful_deliveries}/{webhook_detail.total_deliveries}")

    # Get delivery history
    print(f"\n4. Checking delivery history...")
    deliveries = client.webhooks.deliveries(webhook.id, limit=10)
    print(f"  Total deliveries: {deliveries['meta']['total']}")
    for delivery in deliveries["data"]:
        status = "✓" if delivery["success"] else "✗"
        print(f"  {status} {delivery['event_type']} - Attempt {delivery['attempt']}")

    # Pause webhook
    print(f"\n5. Pausing webhook...")
    client.webhooks.update(webhook.id, is_active=False)
    print(f"  ✓ Webhook paused")

    # Resume webhook
    print(f"\n6. Resuming webhook...")
    client.webhooks.update(webhook.id, is_active=True)
    print(f"  ✓ Webhook resumed")

    client.close()

    print("\n" + "=" * 60)
    print("Webhook setup completed!")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Run webhook receiver
        print("Starting webhook receiver on http://localhost:5000")
        app.run(port=5000, debug=True)
    else:
        # Setup webhooks
        setup_webhooks()
