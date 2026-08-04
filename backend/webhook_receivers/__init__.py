"""
Webhook Receivers for Compass - INBOUND Webhooks from External Services

Replaces polling with real-time webhook receivers for:
- Slack Event API
- GitHub Webhooks
- Intercom Webhooks

These webhooks receive events FROM external services (opposite of webhooks.py which sends events TO external services).
"""

from .slack import router as slack_router
from .github import router as github_router
from .intercom import router as intercom_router

__all__ = ["slack_router", "github_router", "intercom_router"]
