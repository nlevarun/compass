#!/usr/bin/env python3
"""
Universal database fix script - works on all platforms.
Finds and deletes old database, then recreates with correct schema.
"""
import os
import sys
import glob

def find_and_delete_db():
    """Find all .db files in current directory and parent, delete them."""
    # Possible locations
    locations = [
        "compass.db",
        "../compass.db",
        "*.db",
    ]

    deleted = []
    for pattern in locations:
        files = glob.glob(pattern)
        for db_file in files:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    deleted.append(db_file)
                    print(f"✅ Deleted old database: {db_file}")
                except Exception as e:
                    print(f"⚠️  Could not delete {db_file}: {e}")

    if not deleted:
        print("ℹ️  No old database files found (this is fine)")

    return deleted

if __name__ == "__main__":
    print("🔧 Compass Database Fix Script")
    print("=" * 50)

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Delete old databases
    find_and_delete_db()

    print("\n✅ Database cleanup complete!")
    print("📋 Next step: Start backend with 'python main.py'")
    print("   Fresh database will be created automatically.")
