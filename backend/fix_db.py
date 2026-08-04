#!/usr/bin/env python3
"""
Universal database fix script - works on all platforms.
Finds and deletes old database, then recreates with correct schema.
"""
import os
import sys
import glob
from pathlib import Path

def find_and_delete_db():
    """Find all .db files in current directory and parent, delete them."""
    # Get script directory using pathlib for cross-platform compatibility
    script_dir = Path(__file__).parent.resolve()

    # Possible locations (using pathlib for cross-platform paths)
    locations = [
        script_dir / "compass.db",
        script_dir.parent / "compass.db",
    ]

    # Also check for any .db files in current directory
    db_files_in_dir = list(script_dir.glob("*.db"))

    all_files = locations + db_files_in_dir
    deleted = []

    for db_file in all_files:
        if db_file.exists():
            try:
                os.remove(db_file)
                deleted.append(str(db_file))
                print(f"✅ Deleted old database: {db_file}")
            except Exception as e:
                print(f"⚠️  Could not delete {db_file}: {e}")

    if not deleted:
        print("ℹ️  No old database files found (this is fine)")

    return deleted

def verify_models():
    """Verify models.py can be loaded."""
    try:
        import models
        print("✅ models.py loaded successfully")

        # Check that critical models exist
        critical_models = ['Source', 'Feedback', 'Cluster', 'RoadmapItem', 'ImportJob', 'JiraIssue', 'LinearIssue']
        for model_name in critical_models:
            if hasattr(models, model_name):
                print(f"  ✓ {model_name} model found")
            else:
                print(f"  ✗ {model_name} model NOT found")
                return False
        return True
    except ImportError as e:
        print(f"✗ Error loading models.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Compass Database Fix Script")
    print("=" * 50)

    # Change to script directory (cross-platform)
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    print()

    # Verify models first
    print("Verifying database models...")
    if not verify_models():
        print("\n✗ Model verification failed!")
        print("   Make sure you're in the backend directory and models.py exists.")
        sys.exit(1)
    print()

    # Delete old databases
    print("Cleaning up old database files...")
    find_and_delete_db()

    print("\n✅ Database cleanup complete!")
    print("\n📋 Next steps:")
    print("   1. Start backend: python main.py")
    print("   2. Fresh database will be created automatically with correct schema")
    print("   3. Visit http://localhost:8000/docs to verify API is running")
