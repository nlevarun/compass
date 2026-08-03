"""
Quick setup script for adding new sources to Compass database.

This script helps you quickly add GitHub, Discord, and Reddit sources
to your Compass database with interactive configuration.

Usage:
    python setup_sources.py                    # Interactive mode
    python setup_sources.py --auto             # Add with example configs
    python setup_sources.py --list             # List existing sources
    python setup_sources.py --delete SOURCE    # Delete a source
"""

import sys
import os
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Source, Feedback, get_connection_string, Base


def list_sources(session: Session):
    """List all sources in database."""
    sources = session.query(Source).all()

    if not sources:
        print("\n📭 No sources found in database")
        return

    print("\n" + "=" * 60)
    print("📋 EXISTING SOURCES")
    print("=" * 60)

    for source in sources:
        status = "✓ Active" if source.is_active else "⚠️  Inactive"
        print(f"\n{source.id}. {source.name} ({source.source_type}) - {status}")

        if source.config:
            print(f"   Configuration:")
            for key, value in source.config.items():
                # Mask sensitive values
                if any(secret in key.lower() for secret in ["token", "secret", "password", "key"]):
                    display_value = f"{str(value)[:10]}..." if value else "Not set"
                else:
                    display_value = value
                print(f"     • {key}: {display_value}")

        if source.last_synced_at:
            print(f"   Last synced: {source.last_synced_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Count feedback
        feedback_count = session.query(Feedback).filter(Feedback.source_id == source.id).count()
        print(f"   Feedback items: {feedback_count}")

    print("=" * 60)


def add_github_source(session: Session, auto: bool = False):
    """Add GitHub source interactively or with defaults."""
    print("\n" + "=" * 60)
    print("🐙 ADDING GITHUB SOURCE")
    print("=" * 60)

    if auto:
        config = {
            "token": "ghp_PLACEHOLDER_TOKEN",
            "repo_owner": "example-org",
            "repo_name": "example-repo",
            "labels": ["feedback", "feature-request"],
            "include_discussions": True,
            "include_prs": False
        }
        print("\n⚠️  Using placeholder config - update with real values!")
    else:
        print("\n📝 Enter GitHub configuration:")
        print("   Get token from: https://github.com/settings/tokens")

        token = input("   GitHub Token: ").strip()
        repo_owner = input("   Repository Owner: ").strip()
        repo_name = input("   Repository Name: ").strip()

        labels_input = input("   Labels to filter (comma-separated, or blank for all): ").strip()
        labels = [l.strip() for l in labels_input.split(",")] if labels_input else []

        include_discussions = input("   Include Discussions? (y/n) [y]: ").strip().lower() or "y"
        include_prs = input("   Include PR Comments? (y/n) [n]: ").strip().lower() or "n"

        config = {
            "token": token,
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "labels": labels,
            "include_discussions": include_discussions == "y",
            "include_prs": include_prs == "y"
        }

    # Create source
    source = Source(
        name="GitHub",
        source_type="real",
        is_active=True,
        config=config,
        created_at=datetime.utcnow()
    )

    session.add(source)
    session.commit()

    print(f"\n✓ Added GitHub source (ID: {source.id})")
    print(f"   Repo: {config['repo_owner']}/{config['repo_name']}")
    print(f"   Labels: {', '.join(config['labels']) if config['labels'] else 'All'}")


def add_discord_source(session: Session, auto: bool = False):
    """Add Discord source interactively or with defaults."""
    print("\n" + "=" * 60)
    print("💬 ADDING DISCORD SOURCE")
    print("=" * 60)

    if auto:
        config = {
            "bot_token": "PLACEHOLDER_BOT_TOKEN",
            "guild_id": "123456789012345678",
            "channel_ids": ["987654321098765432"],
            "include_threads": True,
            "reaction_threshold": 3
        }
        print("\n⚠️  Using placeholder config - update with real values!")
    else:
        print("\n📝 Enter Discord configuration:")
        print("   Setup: https://discord.com/developers/applications")
        print("   IMPORTANT: Enable 'Message Content Intent' in bot settings")

        bot_token = input("   Bot Token: ").strip()
        guild_id = input("   Guild (Server) ID: ").strip()

        channel_ids_input = input("   Channel IDs (comma-separated): ").strip()
        channel_ids = [c.strip() for c in channel_ids_input.split(",")]

        include_threads = input("   Include Threads? (y/n) [y]: ").strip().lower() or "y"
        reaction_threshold = input("   Reaction Threshold [3]: ").strip() or "3"

        config = {
            "bot_token": bot_token,
            "guild_id": guild_id,
            "channel_ids": channel_ids,
            "include_threads": include_threads == "y",
            "reaction_threshold": int(reaction_threshold)
        }

    # Create source
    source = Source(
        name="Discord",
        source_type="real",
        is_active=True,
        config=config,
        created_at=datetime.utcnow()
    )

    session.add(source)
    session.commit()

    print(f"\n✓ Added Discord source (ID: {source.id})")
    print(f"   Guild: {config['guild_id']}")
    print(f"   Channels: {len(config['channel_ids'])}")


def add_reddit_source(session: Session, auto: bool = False):
    """Add Reddit source interactively or with defaults."""
    print("\n" + "=" * 60)
    print("🤖 ADDING REDDIT SOURCE")
    print("=" * 60)

    if auto:
        config = {
            "client_id": "PLACEHOLDER_CLIENT_ID",
            "client_secret": "PLACEHOLDER_CLIENT_SECRET",
            "user_agent": "compass-bot/1.0 by u/yourname",
            "subreddit": "example",
            "flairs": [],
            "keywords": ["feedback", "feature", "request"],
            "sort_by": "new",
            "limit": 100
        }
        print("\n⚠️  Using placeholder config - update with real values!")
    else:
        print("\n📝 Enter Reddit configuration:")
        print("   Setup: https://www.reddit.com/prefs/apps")
        print("   Create a 'script' type app")

        client_id = input("   Client ID: ").strip()
        client_secret = input("   Client Secret: ").strip()
        user_agent = input("   User Agent (e.g., compass-bot/1.0 by u/yourname): ").strip()
        subreddit = input("   Subreddit (without r/): ").strip()

        flairs_input = input("   Flairs to filter (comma-separated, or blank): ").strip()
        flairs = [f.strip() for f in flairs_input.split(",")] if flairs_input else []

        keywords_input = input("   Keywords to filter (comma-separated, or blank): ").strip()
        keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else []

        sort_by = input("   Sort by (new/hot/top/rising) [new]: ").strip() or "new"
        limit = input("   Limit [100]: ").strip() or "100"

        config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "user_agent": user_agent,
            "subreddit": subreddit,
            "flairs": flairs,
            "keywords": keywords,
            "sort_by": sort_by,
            "limit": int(limit)
        }

    # Create source
    source = Source(
        name="Reddit",
        source_type="real",
        is_active=True,
        config=config,
        created_at=datetime.utcnow()
    )

    session.add(source)
    session.commit()

    print(f"\n✓ Added Reddit source (ID: {source.id})")
    print(f"   Subreddit: r/{config['subreddit']}")
    print(f"   Sort by: {config['sort_by']}")
    print(f"   Limit: {config['limit']}")


def delete_source(session: Session, source_name: str):
    """Delete a source and its feedback."""
    source = session.query(Source).filter(Source.name == source_name).first()

    if not source:
        print(f"\n❌ Source '{source_name}' not found")
        return

    feedback_count = session.query(Feedback).filter(Feedback.source_id == source.id).count()

    print(f"\n⚠️  WARNING: This will delete:")
    print(f"   • Source: {source.name}")
    print(f"   • {feedback_count} feedback items")

    confirm = input("\n   Type 'DELETE' to confirm: ").strip()

    if confirm == "DELETE":
        session.delete(source)
        session.commit()
        print(f"\n✓ Deleted source '{source_name}' and {feedback_count} feedback items")
    else:
        print("\n❌ Deletion cancelled")


def interactive_menu(session: Session):
    """Interactive menu for source management."""
    while True:
        print("\n" + "=" * 60)
        print("🧭 COMPASS SOURCE SETUP")
        print("=" * 60)
        print("\n1. List existing sources")
        print("2. Add GitHub source")
        print("3. Add Discord source")
        print("4. Add Reddit source")
        print("5. Delete source")
        print("6. Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == "1":
            list_sources(session)
        elif choice == "2":
            add_github_source(session, auto=False)
        elif choice == "3":
            add_discord_source(session, auto=False)
        elif choice == "4":
            add_reddit_source(session, auto=False)
        elif choice == "5":
            source_name = input("\nSource name to delete: ").strip()
            delete_source(session, source_name)
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Setup and manage Compass feedback sources",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Add all sources with example configs (for testing)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all existing sources"
    )

    parser.add_argument(
        "--delete",
        metavar="SOURCE",
        help="Delete a source by name"
    )

    parser.add_argument(
        "--db-path",
        default="compass.db",
        help="Path to SQLite database file (default: compass.db)"
    )

    args = parser.parse_args()

    # Create database engine
    engine = create_engine(get_connection_string(db_path=args.db_path))

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        if args.list:
            list_sources(session)
        elif args.delete:
            delete_source(session, args.delete)
        elif args.auto:
            print("\n🚀 Adding sources with example configs...")
            add_github_source(session, auto=True)
            add_discord_source(session, auto=True)
            add_reddit_source(session, auto=True)
            print("\n✓ All sources added!")
            print("\n⚠️  IMPORTANT: Update configs with real credentials before syncing")
            print("   Use: python setup_sources.py --list")
        else:
            interactive_menu(session)


if __name__ == "__main__":
    main()
