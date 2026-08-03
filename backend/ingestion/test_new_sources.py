"""
Test script for new feedback sources: GitHub, Discord, and Reddit.

This script tests the three new integrations with example configurations.
Make sure to install dependencies first:
    pip install PyGithub discord.py praw

Usage:
    python test_new_sources.py [source_name]

    source_name: github, discord, reddit, or all (default: all)

Examples:
    python test_new_sources.py github
    python test_new_sources.py discord
    python test_new_sources.py reddit
    python test_new_sources.py all
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Source
from ingestion.sources import GitHubSource, DiscordSource, RedditSource, create_source


def test_github_source():
    """Test GitHub source integration."""
    print("\n" + "=" * 60)
    print("🐙 TESTING GITHUB SOURCE")
    print("=" * 60)

    # Example configuration (UPDATE WITH YOUR VALUES)
    config = {
        "token": "ghp_YOUR_GITHUB_TOKEN_HERE",  # Replace with your token
        "repo_owner": "microsoft",              # Example: microsoft
        "repo_name": "vscode",                  # Example: vscode
        "labels": ["feature-request", "feedback"],  # Labels to filter
        "include_discussions": True,
        "include_prs": False
    }

    # Create source model
    source_model = Source(
        id=100,
        name="GitHub",
        source_type="real",
        is_active=True,
        config=config
    )

    # Create source instance
    source = create_source(source_model)

    # Validate configuration
    print(f"\n✓ Configuration valid: {source.validate_config()}")

    # Test fetching feedback
    print(f"\n📥 Fetching feedback from {config['repo_owner']}/{config['repo_name']}...")
    print("   (This may take a minute for large repos...)")

    # Fetch recent feedback (last 30 days)
    since = datetime.utcnow() - timedelta(days=30)

    try:
        feedback = source.fetch_feedback(since=since)

        print(f"\n✓ Successfully fetched {len(feedback)} feedback items")

        # Show sample feedback
        if feedback:
            print("\n--- Sample Feedback (first 3) ---")
            for i, fb in enumerate(feedback[:3], 1):
                print(f"\n{i}. {fb.get('title', 'No title')}")
                print(f"   Author: {fb['customer_name']}")
                print(f"   Date: {fb['submitted_at']}")
                print(f"   Type: {fb['source_metadata']['type']}")
                print(f"   URL: {fb['source_metadata']['url']}")
                print(f"   Text: {fb['text'][:100]}...")

        # Statistics
        if feedback:
            types = {}
            for fb in feedback:
                fb_type = fb['source_metadata']['type']
                types[fb_type] = types.get(fb_type, 0) + 1

            print("\n--- Statistics ---")
            for fb_type, count in types.items():
                print(f"   {fb_type}: {count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("  1. Replace 'ghp_YOUR_GITHUB_TOKEN_HERE' with your actual token")
        print("  2. Install PyGithub: pip install PyGithub")
        print("  3. Use a valid repo_owner and repo_name")


def test_discord_source():
    """Test Discord source integration."""
    print("\n" + "=" * 60)
    print("💬 TESTING DISCORD SOURCE")
    print("=" * 60)

    # Example configuration (UPDATE WITH YOUR VALUES)
    config = {
        "bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE",
        "guild_id": "YOUR_GUILD_ID_HERE",
        "channel_ids": ["YOUR_CHANNEL_ID_HERE"],
        "include_threads": True,
        "reaction_threshold": 3
    }

    # Create source model
    source_model = Source(
        id=101,
        name="Discord",
        source_type="real",
        is_active=True,
        config=config
    )

    # Create source instance
    source = create_source(source_model)

    # Validate configuration
    print(f"\n✓ Configuration valid: {source.validate_config()}")

    # Test fetching feedback
    print("\n📥 Fetching feedback from Discord...")
    print("   (This may take a minute to connect...)")

    # Fetch recent feedback (last 7 days)
    since = datetime.utcnow() - timedelta(days=7)

    try:
        feedback = source.fetch_feedback(since=since)

        print(f"\n✓ Successfully fetched {len(feedback)} feedback items")

        # Show sample feedback
        if feedback:
            print("\n--- Sample Feedback (first 3) ---")
            for i, fb in enumerate(feedback[:3], 1):
                print(f"\n{i}. {fb.get('title', 'No title')}")
                print(f"   Author: {fb['customer_name']}")
                print(f"   Date: {fb['submitted_at']}")
                print(f"   Channel: {fb['source_metadata']['channel_name']}")
                print(f"   Reactions: {fb['source_metadata']['total_reactions']}")
                print(f"   URL: {fb['source_metadata']['url']}")
                print(f"   Text: {fb['text'][:100]}...")

        # Statistics
        if feedback:
            channels = {}
            high_engagement = 0
            for fb in feedback:
                channel = fb['source_metadata']['channel_name']
                channels[channel] = channels.get(channel, 0) + 1
                if fb['source_metadata'].get('high_engagement'):
                    high_engagement += 1

            print("\n--- Statistics ---")
            for channel, count in channels.items():
                print(f"   {channel}: {count}")
            print(f"   High engagement messages: {high_engagement}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("  1. Create a Discord bot at https://discord.com/developers/applications")
        print("  2. Enable 'Message Content Intent' in bot settings")
        print("  3. Add bot to your server with proper permissions")
        print("  4. Replace config values with your actual bot token and IDs")
        print("  5. Install discord.py: pip install discord.py")


def test_reddit_source():
    """Test Reddit source integration."""
    print("\n" + "=" * 60)
    print("🤖 TESTING REDDIT SOURCE")
    print("=" * 60)

    # Example configuration (UPDATE WITH YOUR VALUES)
    config = {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "user_agent": "compass-feedback-bot/1.0",
        "subreddit": "webdev",  # Example public subreddit
        "flairs": [],  # Optional: filter by flair
        "keywords": ["feedback", "feature", "request", "suggestion"],
        "sort_by": "new",
        "limit": 50
    }

    # Create source model
    source_model = Source(
        id=102,
        name="Reddit",
        source_type="real",
        is_active=True,
        config=config
    )

    # Create source instance
    source = create_source(source_model)

    # Validate configuration
    print(f"\n✓ Configuration valid: {source.validate_config()}")

    # Test fetching feedback
    print(f"\n📥 Fetching feedback from r/{config['subreddit']}...")
    print("   (This may take a minute...)")

    # Fetch recent feedback (last 7 days)
    since = datetime.utcnow() - timedelta(days=7)

    try:
        feedback = source.fetch_feedback(since=since)

        print(f"\n✓ Successfully fetched {len(feedback)} feedback items")

        # Show sample feedback
        if feedback:
            print("\n--- Sample Feedback (first 3) ---")
            for i, fb in enumerate(feedback[:3], 1):
                print(f"\n{i}. {fb.get('title', 'No title')}")
                print(f"   Author: {fb['customer_name']}")
                print(f"   Date: {fb['submitted_at']}")
                print(f"   Type: {fb['source_metadata']['type']}")
                print(f"   Upvotes: {fb['source_metadata'].get('upvotes', 'N/A')}")
                print(f"   URL: {fb['source_metadata']['url']}")
                print(f"   Text: {fb['text'][:100]}...")

        # Statistics
        if feedback:
            types = {}
            total_upvotes = 0
            total_comments = 0

            for fb in feedback:
                fb_type = fb['source_metadata']['type']
                types[fb_type] = types.get(fb_type, 0) + 1
                total_upvotes += fb['source_metadata'].get('upvotes', 0)
                if fb['source_metadata']['type'] == 'post':
                    total_comments += fb['source_metadata'].get('num_comments', 0)

            print("\n--- Statistics ---")
            for fb_type, count in types.items():
                print(f"   {fb_type}: {count}")
            print(f"   Total upvotes: {total_upvotes}")
            print(f"   Total comments on posts: {total_comments}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("  1. Create a Reddit app at https://www.reddit.com/prefs/apps")
        print("  2. Choose 'script' as the app type")
        print("  3. Replace config values with your actual credentials")
        print("  4. Install praw: pip install praw")


def print_usage():
    """Print usage instructions."""
    print("\n" + "=" * 60)
    print("🧪 COMPASS FEEDBACK SOURCES - TEST SUITE")
    print("=" * 60)
    print("\nThis script tests the three new feedback source integrations:")
    print("  • GitHub Issues & Discussions")
    print("  • Discord Server Messages")
    print("  • Reddit Posts & Comments")

    print("\n📋 PREREQUISITES:")
    print("  1. Install dependencies:")
    print("     pip install PyGithub discord.py praw")
    print("\n  2. Set up API credentials for each service")
    print("  3. Update configuration values in this script")

    print("\n🚀 USAGE:")
    print("  python test_new_sources.py [source]")
    print("\n  Where [source] is one of:")
    print("    github  - Test GitHub integration only")
    print("    discord - Test Discord integration only")
    print("    reddit  - Test Reddit integration only")
    print("    all     - Test all integrations (default)")

    print("\n💡 QUICK TEST (no credentials needed):")
    print("  The script will run with example configs and show what")
    print("  errors to expect if credentials aren't configured.")
    print("=" * 60 + "\n")


def main():
    """Main test runner."""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_usage()
        return

    # Determine which sources to test
    test_target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    print_usage()

    if test_target in ["github", "all"]:
        test_github_source()

    if test_target in ["discord", "all"]:
        test_discord_source()

    if test_target in ["reddit", "all"]:
        test_reddit_source()

    if test_target not in ["github", "discord", "reddit", "all"]:
        print(f"\n❌ Unknown source: {test_target}")
        print("   Valid options: github, discord, reddit, all")

    print("\n" + "=" * 60)
    print("✓ TEST SUITE COMPLETE")
    print("=" * 60)
    print("\n📚 NEXT STEPS:")
    print("  1. Update configurations with your actual credentials")
    print("  2. Add sources to your Compass database")
    print("  3. Run ingestion to fetch real feedback")
    print("\n💡 Integration Tips:")
    print("  • GitHub: Use fine-grained tokens with repo read permissions")
    print("  • Discord: Enable 'Message Content Intent' in bot settings")
    print("  • Reddit: Create a 'script' type app for API access")
    print("\n🎯 These integrations give you a HUGE competitive advantage!")
    print("   No other feedback platform connects to GitHub Discussions,")
    print("   Discord communities, and Reddit this seamlessly.\n")


if __name__ == "__main__":
    main()
