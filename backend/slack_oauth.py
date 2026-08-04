"""
Slack OAuth Integration for Compass

Handles the OAuth 2.0 flow for connecting Slack workspaces.
No manual tokens needed - user clicks button and gets connected.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os
import secrets
import json

from slack_sdk import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.errors import SlackApiError

from database import get_db_session
from models import Source, Feedback

# Slack OAuth configuration
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID", "")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET", "")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "http://localhost:8000/api/auth/slack/callback")

# Required OAuth scopes
SLACK_SCOPES = [
    "channels:read",
    "channels:history",
    "groups:read",
    "groups:history",
    "users:read",
    "users:read.email"
]

# Router
router = APIRouter(prefix="/api/auth/slack", tags=["Slack OAuth"])

# In-memory state store (for production, use Redis or database)
oauth_states = {}


@router.get("/connect")
async def slack_oauth_start():
    """
    Start Slack OAuth flow.
    Redirects user to Slack authorization page.
    """
    if not SLACK_CLIENT_ID or not SLACK_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Slack OAuth not configured. Set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET environment variables."
        )

    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"created_at": datetime.utcnow().isoformat()}

    # Build authorization URL
    authorize_url_generator = AuthorizeUrlGenerator(
        client_id=SLACK_CLIENT_ID,
        scopes=SLACK_SCOPES,
        redirect_uri=SLACK_REDIRECT_URI
    )

    auth_url = authorize_url_generator.generate(state=state)

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def slack_oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="CSRF protection state"),
    error: Optional[str] = Query(None, description="Error from Slack")
):
    """
    Handle Slack OAuth callback.
    Exchanges code for access token and stores in database.
    """
    # Check for errors from Slack
    if error:
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family: system-ui; padding: 40px; text-align: center;">
                    <h1 style="color: #e01e5a;">Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p><a href="/">Return to Compass</a></p>
                    <script>
                        // Close window after 3 seconds
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
            </html>
            """,
            status_code=400
        )

    # Verify state (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Remove used state
    del oauth_states[state]

    try:
        # Exchange code for access token
        client = WebClient()
        response = client.oauth_v2_access(
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=SLACK_REDIRECT_URI
        )

        if not response["ok"]:
            raise HTTPException(status_code=400, detail=f"OAuth exchange failed: {response.get('error', 'Unknown error')}")

        # Extract tokens and workspace info
        access_token = response["access_token"]
        team_id = response["team"]["id"]
        team_name = response["team"]["name"]
        bot_user_id = response.get("bot_user_id")
        authed_user = response.get("authed_user", {})

        # Store token in database
        with next(get_db_session()) as db:
            # Check if source already exists for this team
            source = db.query(Source).filter(
                Source.name == f"Slack - {team_name}",
                Source.source_type == "slack"
            ).first()

            if source:
                # Update existing source
                source.config = {
                    "access_token": access_token,
                    "team_id": team_id,
                    "team_name": team_name,
                    "bot_user_id": bot_user_id,
                    "authed_user_id": authed_user.get("id"),
                    "oauth_version": "v2",
                    "scopes": SLACK_SCOPES
                }
                source.is_active = True
                source.last_synced_at = None  # Reset sync status
            else:
                # Create new source
                source = Source(
                    name=f"Slack - {team_name}",
                    source_type="slack",
                    is_active=True,
                    config={
                        "access_token": access_token,
                        "team_id": team_id,
                        "team_name": team_name,
                        "bot_user_id": bot_user_id,
                        "authed_user_id": authed_user.get("id"),
                        "oauth_version": "v2",
                        "scopes": SLACK_SCOPES
                    }
                )
                db.add(source)

            db.commit()
            source_id = source.id

        # Success! Return HTML that closes the popup and notifies parent
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: system-ui, -apple-system, sans-serif;
                            padding: 40px;
                            text-align: center;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }}
                        .success-icon {{
                            font-size: 64px;
                            margin-bottom: 20px;
                        }}
                        h1 {{
                            margin: 0 0 10px 0;
                        }}
                        p {{
                            opacity: 0.9;
                        }}
                    </style>
                </head>
                <body>
                    <div class="success-icon">✓</div>
                    <h1>Connected to Slack!</h1>
                    <p>Workspace: {team_name}</p>
                    <p>This window will close automatically...</p>
                    <script>
                        // Send message to parent window
                        if (window.opener) {{
                            window.opener.postMessage({{
                                type: 'slack_oauth_success',
                                source_id: {source_id},
                                team_name: '{team_name}'
                            }}, '*');
                        }}
                        // Close window after 2 seconds
                        setTimeout(() => {{
                            window.close();
                        }}, 2000);
                    </script>
                </body>
            </html>
            """
        )

    except SlackApiError as e:
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family: system-ui; padding: 40px; text-align: center;">
                    <h1 style="color: #e01e5a;">Connection Failed</h1>
                    <p>Error: {str(e)}</p>
                    <p><a href="/">Return to Compass</a></p>
                    <script>
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
            </html>
            """,
            status_code=400
        )


@router.get("/status")
async def get_slack_status():
    """
    Get Slack connection status.
    Returns list of connected workspaces.
    """
    with next(get_db_session()) as db:
        slack_sources = db.query(Source).filter(
            Source.source_type == "slack",
            Source.is_active == True
        ).all()

        workspaces = []
        for source in slack_sources:
            config = source.config or {}
            feedback_count = db.query(Feedback).filter(Feedback.source_id == source.id).count()

            workspaces.append({
                "source_id": source.id,
                "team_name": config.get("team_name", "Unknown"),
                "team_id": config.get("team_id"),
                "connected_at": source.created_at.isoformat(),
                "last_synced_at": source.last_synced_at.isoformat() if source.last_synced_at else None,
                "feedback_count": feedback_count,
                "has_token": bool(config.get("access_token"))
            })

        return {
            "connected": len(workspaces) > 0,
            "workspaces": workspaces,
            "oauth_configured": bool(SLACK_CLIENT_ID and SLACK_CLIENT_SECRET)
        }


@router.post("/disconnect/{source_id}")
async def disconnect_slack(source_id: int):
    """
    Disconnect a Slack workspace.
    Revokes token and deactivates source.
    """
    with next(get_db_session()) as db:
        source = db.query(Source).filter(
            Source.id == source_id,
            Source.source_type == "slack"
        ).first()

        if not source:
            raise HTTPException(status_code=404, detail="Slack source not found")

        # Try to revoke token (optional, graceful failure)
        try:
            config = source.config or {}
            access_token = config.get("access_token")
            if access_token:
                client = WebClient(token=access_token)
                client.auth_revoke()
        except Exception as e:
            print(f"Warning: Failed to revoke Slack token: {e}")

        # Deactivate source
        source.is_active = False
        source.config = {}  # Clear sensitive data

        db.commit()

        return {
            "status": "success",
            "message": f"Disconnected from {source.name}"
        }


@router.get("/channels/{source_id}")
async def get_slack_channels(source_id: int):
    """
    Get list of channels from a connected Slack workspace.
    """
    with next(get_db_session()) as db:
        source = db.query(Source).filter(
            Source.id == source_id,
            Source.source_type == "slack"
        ).first()

        if not source:
            raise HTTPException(status_code=404, detail="Slack source not found")

        config = source.config or {}
        access_token = config.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token found")

        try:
            client = WebClient(token=access_token)

            # Get all channels (public and private)
            channels = []
            cursor = None

            while True:
                response = client.conversations_list(
                    types="public_channel,private_channel",
                    limit=100,
                    cursor=cursor
                )

                for channel in response["channels"]:
                    channels.append({
                        "id": channel["id"],
                        "name": channel["name"],
                        "is_private": channel.get("is_private", False),
                        "is_member": channel.get("is_member", False),
                        "num_members": channel.get("num_members", 0)
                    })

                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

            return {
                "source_id": source_id,
                "team_name": config.get("team_name"),
                "channels": channels
            }

        except SlackApiError as e:
            raise HTTPException(status_code=400, detail=f"Slack API error: {str(e)}")


@router.post("/sync/{source_id}")
async def sync_slack_messages(
    source_id: int,
    channel_id: str = Query(..., description="Channel ID to sync"),
    limit: int = Query(100, description="Number of messages to fetch")
):
    """
    Sync messages from a Slack channel.
    """
    with next(get_db_session()) as db:
        source = db.query(Source).filter(
            Source.id == source_id,
            Source.source_type == "slack"
        ).first()

        if not source:
            raise HTTPException(status_code=404, detail="Slack source not found")

        config = source.config or {}
        access_token = config.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token found")

        try:
            client = WebClient(token=access_token)

            # Get bot user ID to filter out bot messages
            auth_response = client.auth_test()
            bot_user_id = auth_response.get("user_id")

            # Fetch messages
            oldest = None
            if source.last_synced_at:
                oldest = str(source.last_synced_at.timestamp())

            response = client.conversations_history(
                channel=channel_id,
                limit=limit,
                oldest=oldest
            )

            messages = response.get("messages", [])
            synced_count = 0

            # Process messages
            for msg in reversed(messages):  # Process oldest first
                # Skip bot messages and system messages
                if msg.get("type") != "message" or msg.get("subtype"):
                    continue

                # Skip messages from our bot
                if msg.get("user") == bot_user_id:
                    continue

                # Get user info
                user_id = msg.get("user")
                user_name = "Unknown User"
                user_email = None

                if user_id:
                    try:
                        user_info = client.users_info(user=user_id)
                        if user_info["ok"]:
                            user = user_info["user"]
                            user_name = user.get("real_name") or user.get("name", "Unknown User")
                            user_email = user.get("profile", {}).get("email")
                    except SlackApiError:
                        pass

                # Create feedback entry
                timestamp = float(msg["ts"])
                submitted_at = datetime.fromtimestamp(timestamp)

                # Check if message already exists
                # Note: Using simple approach since SQLite doesn't support JSONB operators
                existing_feedbacks = db.query(Feedback).filter(
                    Feedback.source_id == source_id
                ).all()

                existing = None
                for fb in existing_feedbacks:
                    if fb.source_metadata and fb.source_metadata.get("slack_ts") == msg["ts"]:
                        existing = fb
                        break

                if not existing:
                    feedback = Feedback(
                        source_id=source_id,
                        text=msg["text"],
                        title=f"Slack message from {user_name}",
                        customer_name=user_name,
                        submitted_at=submitted_at,
                        source_metadata={
                            "slack_ts": msg["ts"],
                            "slack_channel": channel_id,
                            "slack_user": user_id,
                            "slack_user_email": user_email,
                            "slack_type": msg.get("type"),
                            "slack_permalink": f"https://slack.com/archives/{channel_id}/p{msg['ts'].replace('.', '')}"
                        }
                    )
                    db.add(feedback)
                    synced_count += 1

            # Update last synced timestamp
            source.last_synced_at = datetime.utcnow()

            # Store channel ID in config
            config["last_channel_id"] = channel_id
            source.config = config

            db.commit()

            return {
                "status": "success",
                "synced": synced_count,
                "channel_id": channel_id,
                "total_messages": len(messages)
            }

        except SlackApiError as e:
            error_msg = f"Slack API error: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"   Response: {e.response}")

            # Provide helpful error messages for common issues
            if e.response.get("error") == "not_in_channel":
                raise HTTPException(
                    status_code=400,
                    detail="Bot is not in this channel. Please invite the bot by typing '/invite @YourAppName' in the Slack channel first."
                )
            elif e.response.get("error") == "channel_not_found":
                raise HTTPException(
                    status_code=404,
                    detail="Channel not found. It may have been deleted or archived."
                )
            elif e.response.get("error") == "missing_scope":
                raise HTTPException(
                    status_code=403,
                    detail="Missing required Slack permissions. Please reconnect your workspace with updated permissions."
                )
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=error_msg)
