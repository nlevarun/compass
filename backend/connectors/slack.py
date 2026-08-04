"""
Simple Slack connector that actually works.
Polls messages every 30 seconds.

Usage:
    connector = SlackConnector(token="xoxb-...", channel_id="C12345...")

    # Test connection
    if connector.test_connection():
        print("Connected!")

    # Fetch recent messages
    messages = connector.fetch_messages(limit=100)
    for msg in messages:
        print(f"{msg['user']}: {msg['text']}")
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict, Optional
from datetime import datetime


class SlackConnector:
    """
    Slack connector for fetching messages from channels.

    Features:
    - Test connection validity
    - Fetch recent messages
    - Track last synced timestamp to avoid duplicates
    - Get channel list
    - Get user info
    """

    def __init__(self, token: str, channel_id: str = None):
        """
        Initialize Slack connector.

        Args:
            token: Slack bot token (starts with xoxb-)
            channel_id: Channel ID to monitor (optional, can be set later)
        """
        self.client = WebClient(token=token)
        self.channel_id = channel_id
        self.last_ts = None
        self._bot_user_id = None

    def test_connection(self) -> bool:
        """
        Test if the token is valid.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = self.client.auth_test()
            self._bot_user_id = response.get("user_id")
            return response["ok"]
        except SlackApiError as e:
            print(f"Connection test failed: {e}")
            return False

    def get_channels(self) -> List[Dict]:
        """
        Get list of channels the bot can access.

        Returns:
            List of channel dicts with 'id', 'name', 'is_member'
        """
        try:
            result = self.client.conversations_list(
                types="public_channel,private_channel",
                limit=100
            )

            channels = []
            for channel in result.get("channels", []):
                channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_member": channel.get("is_member", False),
                    "is_private": channel.get("is_private", False)
                })

            return channels
        except SlackApiError as e:
            print(f"Error fetching channels: {e}")
            return []

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Get user information.

        Args:
            user_id: Slack user ID

        Returns:
            Dict with 'name', 'real_name', 'email' or None if error
        """
        try:
            result = self.client.users_info(user=user_id)
            if result["ok"]:
                user = result["user"]
                return {
                    "id": user["id"],
                    "name": user.get("name"),
                    "real_name": user.get("real_name"),
                    "email": user.get("profile", {}).get("email")
                }
        except SlackApiError as e:
            print(f"Error fetching user info: {e}")

        return None

    def fetch_messages(self, limit: int = 100, oldest: str = None) -> List[Dict]:
        """
        Fetch recent messages from the configured channel.

        Args:
            limit: Maximum number of messages to fetch (default 100)
            oldest: Only messages after this timestamp (optional)

        Returns:
            List of message dicts with 'text', 'user', 'timestamp', 'link'
        """
        if not self.channel_id:
            raise ValueError("Channel ID not set. Call set_channel() first.")

        try:
            # Use the last synced timestamp if no oldest timestamp provided
            if oldest is None and self.last_ts:
                oldest = self.last_ts

            result = self.client.conversations_history(
                channel=self.channel_id,
                limit=limit,
                oldest=oldest
            )

            messages = []
            for msg in result.get("messages", []):
                # Skip bot messages and system messages
                if msg.get("type") == "message" and not msg.get("subtype"):
                    # Skip messages from our own bot
                    if msg.get("user") != self._bot_user_id:
                        messages.append({
                            "text": msg["text"],
                            "user": msg.get("user", "Unknown"),
                            "timestamp": msg["ts"],
                            "link": self._get_message_link(msg["ts"])
                        })

            # Update last timestamp to the most recent message
            if messages:
                self.last_ts = messages[0]["timestamp"]

            return messages

        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return []

    def _get_message_link(self, ts: str) -> str:
        """
        Generate a Slack message permalink.

        Args:
            ts: Message timestamp

        Returns:
            Direct link to the message in Slack
        """
        # Format: https://workspace.slack.com/archives/CHANNEL_ID/pTIMESTAMP
        # The 'p' prefix and removing the dot from timestamp is required
        timestamp_formatted = ts.replace(".", "")
        return f"https://slack.com/archives/{self.channel_id}/p{timestamp_formatted}"

    def set_channel(self, channel_id: str):
        """
        Set or change the channel to monitor.

        Args:
            channel_id: Slack channel ID (e.g., C12345...)
        """
        self.channel_id = channel_id
        # Reset last timestamp when changing channels
        self.last_ts = None

    def reset_sync(self):
        """
        Reset sync state to fetch all messages again.
        """
        self.last_ts = None


# Convenience function for quick testing
def test_slack_connection(token: str) -> Dict:
    """
    Quick test of Slack connection.

    Args:
        token: Slack bot token

    Returns:
        Dict with connection status and available channels
    """
    connector = SlackConnector(token)

    if not connector.test_connection():
        return {
            "success": False,
            "error": "Invalid token or connection failed"
        }

    channels = connector.get_channels()

    return {
        "success": True,
        "channels": channels,
        "message": f"Connected! Found {len(channels)} channels."
    }
