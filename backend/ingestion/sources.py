"""
Base class and implementations for feedback sources.

Supports 8 sources: 1 real (Slack) + 7 mock
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Source, Feedback
from ingestion.mock_generators import generate_mock_feedback, MOCK_SOURCES


class FeedbackSource(ABC):
    """Abstract base class for all feedback sources."""

    def __init__(self, source_id: int, name: str, config: Optional[Dict] = None):
        self.source_id = source_id
        self.name = name
        self.config = config or {}

    @abstractmethod
    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch feedback from the source.

        Args:
            since: Only fetch feedback after this timestamp (for incremental sync)

        Returns:
            List of feedback dictionaries ready for database insertion
        """
        pass

    def validate_config(self) -> bool:
        """Validate source configuration."""
        return True


class MockSource(FeedbackSource):
    """Mock feedback source that generates synthetic data."""

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """Generate mock feedback data."""
        # Get count from mock sources config
        count = MOCK_SOURCES.get(self.name, {}).get("feedback_count", 50)

        # Generate mock data
        feedback = generate_mock_feedback(self.name, count)

        # Filter by date if specified
        if since:
            feedback = [f for f in feedback if f["submitted_at"] > since]

        # Add source_id to each entry
        for f in feedback:
            f["source_id"] = self.source_id

        return feedback


class EmailSource(MockSource):
    """Email feedback source (support@company.com, feature-requests@company.com)."""
    pass


class SupportTicketSource(MockSource):
    """Support ticket source (Zendesk, Intercom, Freshdesk)."""
    pass


class SurveySource(MockSource):
    """Survey feedback source (Typeform, SurveyMonkey, Google Forms)."""
    pass


class AppReviewSource(MockSource):
    """App store review source (iOS App Store, Google Play)."""
    pass


class SalesCallSource(MockSource):
    """Sales call notes and transcripts."""
    pass


class UserInterviewSource(MockSource):
    """User research interview transcripts."""
    pass


class SocialMediaSource(MockSource):
    """Social media mentions (Twitter, LinkedIn, Reddit)."""
    pass


class SlackSource(FeedbackSource):
    """
    Real Slack integration using Slack API.

    Configuration required:
    - token: OAuth access token (xoxb-...)
    - channel_ids: List of channel IDs to monitor
    """

    def validate_config(self) -> bool:
        """Validate Slack configuration."""
        return "token" in self.config and "channel_ids" in self.config

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch messages from Slack channels.

        NOTE: Requires slack-sdk to be installed and configured.
        """
        if not self.validate_config():
            raise ValueError("Slack source not configured. Need token and channel_ids.")

        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
        except ImportError:
            print("⚠️  slack-sdk not installed. Returning empty feedback.")
            return []

        client = WebClient(token=self.config["token"])
        feedback_list = []

        # Convert since to Slack timestamp
        oldest = str(int(since.timestamp())) if since else "0"

        for channel_id in self.config.get("channel_ids", []):
            try:
                # Fetch messages
                response = client.conversations_history(
                    channel=channel_id,
                    oldest=oldest,
                    limit=100
                )

                for message in response.get("messages", []):
                    # Skip bot messages and threads (for now)
                    if message.get("subtype") or "thread_ts" in message:
                        continue

                    # Extract user info
                    user_id = message.get("user")
                    user_name = "Unknown User"
                    if user_id:
                        try:
                            user_info = client.users_info(user=user_id)
                            user_name = user_info["user"]["real_name"]
                        except:
                            pass

                    # Create feedback entry
                    feedback = {
                        "source_id": self.source_id,
                        "text": message.get("text", ""),
                        "customer_name": user_name,
                        "submitted_at": datetime.fromtimestamp(float(message["ts"])),
                        "metadata": {
                            "channel_id": channel_id,
                            "message_ts": message["ts"],
                            "user_id": user_id,
                            "reactions": message.get("reactions", [])
                        }
                    }

                    feedback_list.append(feedback)

            except SlackApiError as e:
                print(f"❌ Slack API error for channel {channel_id}: {e.response['error']}")

        return feedback_list


# Source factory
def create_source(source_model: Source) -> FeedbackSource:
    """Create appropriate source instance based on source model."""

    source_map = {
        "Email": EmailSource,
        "Support Tickets": SupportTicketSource,
        "Surveys": SurveySource,
        "App Reviews": AppReviewSource,
        "Sales Calls": SalesCallSource,
        "User Interviews": UserInterviewSource,
        "Social Media": SocialMediaSource,
        "Slack": SlackSource
    }

    source_class = source_map.get(source_model.name, MockSource)
    return source_class(source_model.id, source_model.name, source_model.config)


if __name__ == "__main__":
    # Test source creation
    print("Testing feedback sources...\n")

    # Create a mock source
    from models import Source

    test_source = Source(
        id=1,
        name="Email",
        source_type="mock",
        is_active=True
    )

    source = create_source(test_source)
    feedback = source.fetch_feedback()

    print(f"✓ Generated {len(feedback)} feedback entries from {test_source.name}")
    print(f"\nSample feedback:")
    for f in feedback[:3]:
        print(f"  • {f['customer_name']}: \"{f['text'][:80]}...\"")
