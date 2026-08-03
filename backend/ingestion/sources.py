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
                        "source_metadata": {
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


class GitHubSource(FeedbackSource):
    """
    Real GitHub integration using PyGithub.

    Configuration required:
    - token: GitHub personal access token or OAuth token
    - repo_owner: Repository owner (username or organization)
    - repo_name: Repository name
    - labels: List of labels to filter issues (optional, e.g., ["feedback", "feature-request"])
    - include_discussions: Whether to fetch discussions (default: True)
    - include_prs: Whether to fetch PR comments (default: False)

    Example config:
    {
        "token": "ghp_xxxxxxxxxxxx",
        "repo_owner": "myorg",
        "repo_name": "myproject",
        "labels": ["feedback", "feature-request", "enhancement"],
        "include_discussions": True,
        "include_prs": False
    }
    """

    def validate_config(self) -> bool:
        """Validate GitHub configuration."""
        return all(key in self.config for key in ["token", "repo_owner", "repo_name"])

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch feedback from GitHub issues, discussions, and PR comments.

        NOTE: Requires PyGithub to be installed.
        """
        if not self.validate_config():
            raise ValueError("GitHub source not configured. Need token, repo_owner, and repo_name.")

        try:
            from github import Github, GithubException
        except ImportError:
            print("⚠️  PyGithub not installed. Run: pip install PyGithub")
            return []

        try:
            # Initialize GitHub client
            gh = Github(self.config["token"])
            repo = gh.get_repo(f"{self.config['repo_owner']}/{self.config['repo_name']}")

            feedback_list = []
            labels_filter = self.config.get("labels", [])
            include_discussions = self.config.get("include_discussions", True)
            include_prs = self.config.get("include_prs", False)

            # Fetch Issues
            print(f"📥 Fetching GitHub issues from {repo.full_name}...")
            issues_params = {"state": "all"}
            if since:
                issues_params["since"] = since

            issues = repo.get_issues(**issues_params)

            for issue in issues:
                # Skip pull requests (they appear in issues endpoint)
                if issue.pull_request:
                    continue

                # Filter by labels if specified
                if labels_filter:
                    issue_labels = [label.name for label in issue.labels]
                    if not any(label in issue_labels for label in labels_filter):
                        continue

                # Create feedback entry for issue
                feedback = {
                    "source_id": self.source_id,
                    "text": f"{issue.body or ''}",
                    "title": issue.title,
                    "customer_name": issue.user.login if issue.user else "Unknown",
                    "submitted_at": issue.created_at,
                    "source_metadata": {
                        "platform": "github",
                        "type": "issue",
                        "issue_number": issue.number,
                        "url": issue.html_url,
                        "state": issue.state,
                        "labels": [label.name for label in issue.labels],
                        "comments_count": issue.comments,
                        "reactions": {
                            "+1": issue.get_reactions().totalCount if hasattr(issue, 'get_reactions') else 0
                        }
                    }
                }
                feedback_list.append(feedback)

                # Fetch issue comments
                if issue.comments > 0:
                    for comment in issue.get_comments():
                        if since and comment.created_at < since:
                            continue

                        comment_feedback = {
                            "source_id": self.source_id,
                            "text": comment.body or "",
                            "title": f"Comment on: {issue.title}",
                            "customer_name": comment.user.login if comment.user else "Unknown",
                            "submitted_at": comment.created_at,
                            "source_metadata": {
                                "platform": "github",
                                "type": "issue_comment",
                                "issue_number": issue.number,
                                "comment_id": comment.id,
                                "url": comment.html_url,
                                "parent_issue_url": issue.html_url
                            }
                        }
                        feedback_list.append(comment_feedback)

            # Fetch Discussions (if enabled)
            if include_discussions:
                print(f"📥 Fetching GitHub discussions...")
                try:
                    # Use GraphQL to fetch discussions
                    discussions = self._fetch_discussions(gh, repo, since)
                    feedback_list.extend(discussions)
                except Exception as e:
                    print(f"⚠️  Could not fetch discussions: {e}")

            # Fetch PR Comments (if enabled)
            if include_prs:
                print(f"📥 Fetching PR comments...")
                try:
                    pr_params = {"state": "all"}
                    pulls = repo.get_pulls(**pr_params)

                    for pr in pulls:
                        if since and pr.created_at < since:
                            continue

                        # Fetch PR review comments
                        for comment in pr.get_review_comments():
                            if since and comment.created_at < since:
                                continue

                            pr_feedback = {
                                "source_id": self.source_id,
                                "text": comment.body or "",
                                "title": f"PR Review: {pr.title}",
                                "customer_name": comment.user.login if comment.user else "Unknown",
                                "submitted_at": comment.created_at,
                                "source_metadata": {
                                    "platform": "github",
                                    "type": "pr_comment",
                                    "pr_number": pr.number,
                                    "comment_id": comment.id,
                                    "url": comment.html_url,
                                    "pr_url": pr.html_url
                                }
                            }
                            feedback_list.append(pr_feedback)
                except Exception as e:
                    print(f"⚠️  Error fetching PR comments: {e}")

            print(f"✓ Fetched {len(feedback_list)} feedback items from GitHub")
            return feedback_list

        except GithubException as e:
            print(f"❌ GitHub API error: {e.data.get('message', str(e))}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return []

    def _fetch_discussions(self, gh, repo, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch GitHub Discussions using GraphQL API."""
        discussions_list = []

        # GraphQL query for discussions
        query = """
        query($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            discussions(first: 50, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                title
                body
                createdAt
                url
                author {
                  login
                }
                category {
                  name
                }
                comments(first: 10) {
                  nodes {
                    id
                    body
                    createdAt
                    url
                    author {
                      login
                    }
                  }
                }
                reactions {
                  totalCount
                }
              }
            }
          }
        }
        """

        variables = {
            "owner": self.config["repo_owner"],
            "repo": self.config["repo_name"],
            "cursor": None
        }

        try:
            # Make GraphQL request
            headers = {"Authorization": f"token {self.config['token']}"}
            import requests

            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                discussions = data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])

                for disc in discussions:
                    # Parse created_at
                    created_at = datetime.fromisoformat(disc["createdAt"].replace("Z", "+00:00"))

                    if since and created_at < since:
                        continue

                    # Create feedback entry for discussion
                    feedback = {
                        "source_id": self.source_id,
                        "text": disc.get("body", ""),
                        "title": disc.get("title", ""),
                        "customer_name": disc.get("author", {}).get("login", "Unknown") if disc.get("author") else "Unknown",
                        "submitted_at": created_at,
                        "source_metadata": {
                            "platform": "github",
                            "type": "discussion",
                            "discussion_id": disc["id"],
                            "url": disc["url"],
                            "category": disc.get("category", {}).get("name", ""),
                            "reactions_count": disc.get("reactions", {}).get("totalCount", 0)
                        }
                    }
                    discussions_list.append(feedback)

                    # Add discussion comments
                    for comment in disc.get("comments", {}).get("nodes", []):
                        comment_created = datetime.fromisoformat(comment["createdAt"].replace("Z", "+00:00"))

                        if since and comment_created < since:
                            continue

                        comment_feedback = {
                            "source_id": self.source_id,
                            "text": comment.get("body", ""),
                            "title": f"Discussion comment: {disc.get('title', '')}",
                            "customer_name": comment.get("author", {}).get("login", "Unknown") if comment.get("author") else "Unknown",
                            "submitted_at": comment_created,
                            "source_metadata": {
                                "platform": "github",
                                "type": "discussion_comment",
                                "comment_id": comment["id"],
                                "url": comment["url"],
                                "parent_discussion_url": disc["url"]
                            }
                        }
                        discussions_list.append(comment_feedback)

        except Exception as e:
            print(f"⚠️  Error fetching discussions via GraphQL: {e}")

        return discussions_list


class DiscordSource(FeedbackSource):
    """
    Real Discord integration using discord.py.

    Configuration required:
    - bot_token: Discord bot token
    - guild_id: Discord server (guild) ID
    - channel_ids: List of channel IDs to monitor
    - include_threads: Whether to include thread messages (default: True)
    - reaction_threshold: Minimum reactions to consider as high-engagement (default: 3)

    Example config:
    {
        "bot_token": "your_discord_bot_token",
        "guild_id": "123456789012345678",
        "channel_ids": ["987654321098765432", "876543210987654321"],
        "include_threads": True,
        "reaction_threshold": 3
    }

    Setup Instructions:
    1. Create a Discord bot at https://discord.com/developers/applications
    2. Enable "Message Content Intent" in Bot settings
    3. Add bot to your server with permissions: Read Messages, Read Message History
    4. Copy bot token and channel IDs
    """

    def validate_config(self) -> bool:
        """Validate Discord configuration."""
        return all(key in self.config for key in ["bot_token", "guild_id", "channel_ids"])

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch messages from Discord channels and threads.

        NOTE: Requires discord.py to be installed.
        """
        if not self.validate_config():
            raise ValueError("Discord source not configured. Need bot_token, guild_id, and channel_ids.")

        try:
            import discord
        except ImportError:
            print("⚠️  discord.py not installed. Run: pip install discord.py")
            return []

        import asyncio

        # Run async fetch in sync context
        return asyncio.run(self._fetch_discord_messages(since))

    async def _fetch_discord_messages(self, since: Optional[datetime] = None) -> List[Dict]:
        """Async method to fetch Discord messages."""
        import discord

        feedback_list = []

        # Create Discord client with necessary intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            try:
                print(f"📥 Connected to Discord as {client.user}")

                guild_id = int(self.config["guild_id"])
                guild = client.get_guild(guild_id)

                if not guild:
                    print(f"❌ Could not find guild with ID {guild_id}")
                    await client.close()
                    return

                channel_ids = [int(cid) for cid in self.config.get("channel_ids", [])]
                include_threads = self.config.get("include_threads", True)
                reaction_threshold = self.config.get("reaction_threshold", 3)

                for channel_id in channel_ids:
                    channel = guild.get_channel(channel_id)

                    if not channel:
                        print(f"⚠️  Could not find channel {channel_id}")
                        continue

                    print(f"📥 Fetching messages from #{channel.name}...")

                    # Fetch channel messages
                    try:
                        async for message in channel.history(limit=200, after=since):
                            # Skip bot messages
                            if message.author.bot:
                                continue

                            # Count reactions
                            total_reactions = sum(reaction.count for reaction in message.reactions)

                            # Create feedback entry
                            feedback = {
                                "source_id": self.source_id,
                                "text": message.content,
                                "title": f"Message in #{channel.name}",
                                "customer_name": f"{message.author.name}#{message.author.discriminator}" if message.author.discriminator != "0" else message.author.name,
                                "submitted_at": message.created_at,
                                "source_metadata": {
                                    "platform": "discord",
                                    "type": "message",
                                    "message_id": str(message.id),
                                    "channel_id": str(channel.id),
                                    "channel_name": channel.name,
                                    "guild_id": str(guild.id),
                                    "guild_name": guild.name,
                                    "url": message.jump_url,
                                    "reactions": [
                                        {"emoji": str(reaction.emoji), "count": reaction.count}
                                        for reaction in message.reactions
                                    ],
                                    "total_reactions": total_reactions,
                                    "has_attachments": len(message.attachments) > 0,
                                    "high_engagement": total_reactions >= reaction_threshold
                                }
                            }

                            # Only include if has content or attachments
                            if message.content or message.attachments:
                                feedback_list.append(feedback)

                    except discord.Forbidden:
                        print(f"❌ No permission to read channel #{channel.name}")
                    except Exception as e:
                        print(f"❌ Error fetching from #{channel.name}: {e}")

                    # Fetch thread messages if enabled
                    if include_threads and hasattr(channel, 'threads'):
                        try:
                            # Active threads
                            for thread in channel.threads:
                                async for message in thread.history(limit=100, after=since):
                                    if message.author.bot:
                                        continue

                                    total_reactions = sum(reaction.count for reaction in message.reactions)

                                    feedback = {
                                        "source_id": self.source_id,
                                        "text": message.content,
                                        "title": f"Thread: {thread.name}",
                                        "customer_name": f"{message.author.name}#{message.author.discriminator}" if message.author.discriminator != "0" else message.author.name,
                                        "submitted_at": message.created_at,
                                        "source_metadata": {
                                            "platform": "discord",
                                            "type": "thread_message",
                                            "message_id": str(message.id),
                                            "thread_id": str(thread.id),
                                            "thread_name": thread.name,
                                            "channel_id": str(channel.id),
                                            "channel_name": channel.name,
                                            "guild_id": str(guild.id),
                                            "url": message.jump_url,
                                            "reactions": [
                                                {"emoji": str(reaction.emoji), "count": reaction.count}
                                                for reaction in message.reactions
                                            ],
                                            "total_reactions": total_reactions
                                        }
                                    }

                                    if message.content or message.attachments:
                                        feedback_list.append(feedback)

                        except Exception as e:
                            print(f"⚠️  Error fetching threads: {e}")

                print(f"✓ Fetched {len(feedback_list)} feedback items from Discord")

            except Exception as e:
                print(f"❌ Error in Discord fetch: {e}")
            finally:
                await client.close()

        try:
            # Start client and wait for completion
            await client.start(self.config["bot_token"])
        except discord.LoginFailure:
            print("❌ Invalid Discord bot token")
        except Exception as e:
            print(f"❌ Discord connection error: {e}")

        return feedback_list


class RedditSource(FeedbackSource):
    """
    Real Reddit integration using PRAW (Python Reddit API Wrapper).

    Configuration required:
    - client_id: Reddit application client ID
    - client_secret: Reddit application client secret
    - user_agent: User agent string (e.g., "compass-feedback-bot/1.0")
    - subreddit: Subreddit name (without r/)
    - flairs: List of post flairs to filter (optional)
    - keywords: List of keywords to search for (optional)
    - sort_by: How to sort posts - "hot", "new", "top", "rising" (default: "new")
    - limit: Max posts to fetch (default: 100)

    Example config:
    {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "user_agent": "compass-feedback-bot/1.0",
        "subreddit": "producthunt",
        "flairs": ["Feedback", "Feature Request"],
        "keywords": ["feature", "request", "feedback", "suggestion"],
        "sort_by": "new",
        "limit": 100
    }

    Setup Instructions:
    1. Create a Reddit app at https://www.reddit.com/prefs/apps
    2. Choose "script" as the app type
    3. Copy client_id and client_secret
    4. Set a descriptive user_agent
    """

    def validate_config(self) -> bool:
        """Validate Reddit configuration."""
        return all(key in self.config for key in ["client_id", "client_secret", "user_agent", "subreddit"])

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch posts and comments from Reddit.

        NOTE: Requires praw to be installed.
        """
        if not self.validate_config():
            raise ValueError("Reddit source not configured. Need client_id, client_secret, user_agent, and subreddit.")

        try:
            import praw
        except ImportError:
            print("⚠️  praw not installed. Run: pip install praw")
            return []

        try:
            # Initialize Reddit client
            reddit = praw.Reddit(
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                user_agent=self.config["user_agent"]
            )

            subreddit = reddit.subreddit(self.config["subreddit"])
            feedback_list = []

            flairs_filter = self.config.get("flairs", [])
            keywords_filter = self.config.get("keywords", [])
            sort_by = self.config.get("sort_by", "new")
            limit = self.config.get("limit", 100)

            print(f"📥 Fetching from r/{self.config['subreddit']}...")

            # Get posts based on sort preference
            if sort_by == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort_by == "top":
                submissions = subreddit.top(limit=limit, time_filter="month")
            elif sort_by == "rising":
                submissions = subreddit.rising(limit=limit)
            else:  # default to new
                submissions = subreddit.new(limit=limit)

            for submission in submissions:
                # Convert timestamp
                submitted_at = datetime.fromtimestamp(submission.created_utc)

                # Filter by date if specified
                if since and submitted_at < since:
                    continue

                # Filter by flair if specified
                if flairs_filter and submission.link_flair_text:
                    if submission.link_flair_text not in flairs_filter:
                        continue

                # Filter by keywords if specified
                if keywords_filter:
                    text_to_search = f"{submission.title} {submission.selftext}".lower()
                    if not any(keyword.lower() in text_to_search for keyword in keywords_filter):
                        continue

                # Calculate engagement score (upvotes as proxy for importance)
                engagement_score = submission.score

                # Create feedback entry for post
                feedback = {
                    "source_id": self.source_id,
                    "text": submission.selftext or submission.title,
                    "title": submission.title,
                    "customer_name": f"u/{submission.author.name}" if submission.author else "Unknown",
                    "submitted_at": submitted_at,
                    "source_metadata": {
                        "platform": "reddit",
                        "type": "post",
                        "post_id": submission.id,
                        "subreddit": str(submission.subreddit),
                        "url": f"https://reddit.com{submission.permalink}",
                        "flair": submission.link_flair_text,
                        "upvotes": submission.score,
                        "upvote_ratio": submission.upvote_ratio,
                        "num_comments": submission.num_comments,
                        "engagement_score": engagement_score,
                        "awards": submission.total_awards_received,
                        "is_self": submission.is_self
                    }
                }
                feedback_list.append(feedback)

                # Fetch top comments
                try:
                    submission.comments.replace_more(limit=0)  # Skip "load more" comments

                    for comment in submission.comments.list()[:20]:  # Top 20 comments
                        if not hasattr(comment, 'body'):
                            continue

                        comment_created = datetime.fromtimestamp(comment.created_utc)

                        if since and comment_created < since:
                            continue

                        # Skip short comments (likely not feedback)
                        if len(comment.body) < 20:
                            continue

                        comment_feedback = {
                            "source_id": self.source_id,
                            "text": comment.body,
                            "title": f"Comment on: {submission.title}",
                            "customer_name": f"u/{comment.author.name}" if comment.author else "Unknown",
                            "submitted_at": comment_created,
                            "source_metadata": {
                                "platform": "reddit",
                                "type": "comment",
                                "comment_id": comment.id,
                                "post_id": submission.id,
                                "subreddit": str(submission.subreddit),
                                "url": f"https://reddit.com{comment.permalink}",
                                "parent_post_url": f"https://reddit.com{submission.permalink}",
                                "upvotes": comment.score,
                                "is_submitter": comment.is_submitter
                            }
                        }
                        feedback_list.append(comment_feedback)

                except Exception as e:
                    print(f"⚠️  Error fetching comments for post {submission.id}: {e}")

            print(f"✓ Fetched {len(feedback_list)} feedback items from Reddit")
            return feedback_list

        except Exception as e:
            print(f"❌ Reddit API error: {str(e)}")
            return []


# Source factory
def create_source(source_model: Source) -> FeedbackSource:
    """Create appropriate source instance based on source model."""

    source_map = {
        # Mock sources
        "Email": EmailSource,
        "Support Tickets": SupportTicketSource,
        "Surveys": SurveySource,
        "App Reviews": AppReviewSource,
        "Sales Calls": SalesCallSource,
        "User Interviews": UserInterviewSource,
        "Social Media": SocialMediaSource,

        # Real integrations
        "Slack": SlackSource,
        "GitHub": GitHubSource,
        "Discord": DiscordSource,
        "Reddit": RedditSource
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
