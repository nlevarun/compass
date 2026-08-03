"""
Automated sync script for all feedback sources.

This script syncs feedback from all active sources and saves to database.
Can be run manually or scheduled (cron, systemd timer, etc.).

Usage:
    python sync.py                    # Sync all active sources
    python sync.py --source GitHub    # Sync specific source
    python sync.py --full             # Full sync (ignore last_synced_at)
    python sync.py --dry-run          # Preview without saving
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Source, Feedback, get_connection_string, Base
from ingestion.sources import create_source


def sync_source(session: Session, source: Source, since: Optional[datetime] = None, dry_run: bool = False) -> Dict:
    """
    Sync feedback from a single source.

    Args:
        session: Database session
        source: Source model to sync
        since: Only fetch feedback after this timestamp (None = use source.last_synced_at)
        dry_run: If True, don't save to database

    Returns:
        Dictionary with sync results
    """
    result = {
        "source_name": source.name,
        "success": False,
        "new_count": 0,
        "error": None
    }

    try:
        # Create source instance
        source_instance = create_source(source)

        # Validate configuration
        if not source_instance.validate_config():
            result["error"] = "Invalid configuration"
            return result

        # Determine since timestamp
        if since is None:
            # Use last_synced_at from database (with 1-hour overlap for safety)
            if source.last_synced_at:
                since = source.last_synced_at - timedelta(hours=1)
            else:
                # First sync - fetch last 30 days
                since = datetime.utcnow() - timedelta(days=30)

        print(f"\n📥 Syncing {source.name}...")
        print(f"   Fetching feedback since: {since.strftime('%Y-%m-%d %H:%M:%S')}")

        # Fetch feedback
        feedback_list = source_instance.fetch_feedback(since=since)

        if not dry_run:
            # Save to database
            new_count = 0
            for feedback_data in feedback_list:
                # Check if already exists (by source_metadata if available)
                if "source_metadata" in feedback_data:
                    metadata = feedback_data["source_metadata"]

                    # Platform-specific deduplication
                    existing = None
                    if metadata.get("platform") == "github":
                        if metadata.get("type") == "issue":
                            existing = session.query(Feedback).filter(
                                Feedback.source_id == source.id,
                                Feedback.source_metadata["issue_number"].astext == str(metadata.get("issue_number"))
                            ).first()
                        elif metadata.get("type") in ["issue_comment", "discussion_comment"]:
                            existing = session.query(Feedback).filter(
                                Feedback.source_id == source.id,
                                Feedback.source_metadata["comment_id"].astext == str(metadata.get("comment_id"))
                            ).first()

                    elif metadata.get("platform") == "discord":
                        existing = session.query(Feedback).filter(
                            Feedback.source_id == source.id,
                            Feedback.source_metadata["message_id"].astext == str(metadata.get("message_id"))
                        ).first()

                    elif metadata.get("platform") == "reddit":
                        if metadata.get("type") == "post":
                            existing = session.query(Feedback).filter(
                                Feedback.source_id == source.id,
                                Feedback.source_metadata["post_id"].astext == str(metadata.get("post_id"))
                            ).first()
                        elif metadata.get("type") == "comment":
                            existing = session.query(Feedback).filter(
                                Feedback.source_id == source.id,
                                Feedback.source_metadata["comment_id"].astext == str(metadata.get("comment_id"))
                            ).first()

                    if existing:
                        continue  # Skip duplicate

                # Create new feedback entry
                feedback = Feedback(**feedback_data)
                session.add(feedback)
                new_count += 1

            # Update last_synced_at
            source.last_synced_at = datetime.utcnow()
            session.commit()

            result["new_count"] = new_count
            print(f"✓ Added {new_count} new feedback items")
        else:
            result["new_count"] = len(feedback_list)
            print(f"✓ Would add {len(feedback_list)} feedback items (dry run)")

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Error syncing {source.name}: {e}")
        session.rollback()

    return result


def sync_all_sources(
    session: Session,
    source_filter: Optional[str] = None,
    full_sync: bool = False,
    dry_run: bool = False
) -> Dict[str, Dict]:
    """
    Sync feedback from all active sources.

    Args:
        session: Database session
        source_filter: Only sync sources with this name (optional)
        full_sync: If True, ignore last_synced_at and fetch all
        dry_run: If True, don't save to database

    Returns:
        Dictionary mapping source names to sync results
    """
    print("=" * 60)
    print("🔄 COMPASS FEEDBACK SYNC")
    print("=" * 60)
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Get active sources
    query = session.query(Source).filter(Source.is_active == True)

    if source_filter:
        query = query.filter(Source.name == source_filter)

    sources = query.all()

    if not sources:
        print("\n⚠️  No active sources found")
        if source_filter:
            print(f"   Source '{source_filter}' not found or not active")
        return {}

    print(f"\n📋 Found {len(sources)} active source(s)")
    for source in sources:
        print(f"   • {source.name} (type: {source.source_type})")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be saved")

    # Sync each source
    results = {}

    for source in sources:
        since = None if full_sync else None  # None = use source.last_synced_at
        result = sync_source(session, source, since=since, dry_run=dry_run)
        results[source.name] = result

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SYNC SUMMARY")
    print("=" * 60)

    total_new = 0
    total_success = 0
    total_errors = 0

    for source_name, result in results.items():
        status = "✓" if result["success"] else "❌"
        print(f"{status} {source_name}: {result['new_count']} new items")

        if result["error"]:
            print(f"   Error: {result['error']}")
            total_errors += 1

        total_new += result["new_count"]
        if result["success"]:
            total_success += 1

    print(f"\nTotal: {total_new} new feedback items")
    print(f"Success: {total_success}/{len(results)} sources")
    if total_errors:
        print(f"Errors: {total_errors}")

    print(f"\nCompleted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync feedback from all active sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync.py                    # Sync all active sources
  python sync.py --source GitHub    # Sync specific source
  python sync.py --full             # Full sync (ignore last_synced_at)
  python sync.py --dry-run          # Preview without saving
  python sync.py -s Discord --full  # Full sync for Discord only

Scheduling:
  # Run every 15 minutes (cron)
  */15 * * * * cd /path/to/compass/backend && python ingestion/sync.py

  # Run every 30 minutes (systemd timer)
  See INTEGRATION_GUIDE.md for setup instructions
        """
    )

    parser.add_argument(
        "-s", "--source",
        help="Only sync specific source by name (e.g., 'GitHub', 'Discord')"
    )

    parser.add_argument(
        "-f", "--full",
        action="store_true",
        help="Full sync - ignore last_synced_at and fetch all available data"
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Dry run - preview changes without saving to database"
    )

    parser.add_argument(
        "--db-path",
        default="compass.db",
        help="Path to SQLite database file (default: compass.db)"
    )

    args = parser.parse_args()

    # Create database engine
    try:
        engine = create_engine(get_connection_string(db_path=args.db_path))

        # Create tables if they don't exist
        Base.metadata.create_all(engine)

        # Run sync
        with Session(engine) as session:
            results = sync_all_sources(
                session=session,
                source_filter=args.source,
                full_sync=args.full,
                dry_run=args.dry_run
            )

            # Exit with error code if any syncs failed
            if any(not r["success"] for r in results.values()):
                sys.exit(1)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
