#!/usr/bin/env python3
"""
Quick database migration script to add missing columns.
Run this if you get "no such column" errors.
"""

import sqlite3
import os

DB_PATH = "compass.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"✅ No existing database found at {DB_PATH}")
        print("   Database will be created fresh on next startup")
        return

    print(f"🔧 Migrating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check and add missing columns
    migrations = [
        ("feedback", "external_ids", "TEXT"),  # JSON column for external IDs
    ]

    for table, column, col_type in migrations:
        try:
            # Check if column exists
            cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            print(f"   ✓ Column {table}.{column} already exists")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            print(f"   + Adding column {table}.{column}")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            conn.commit()
            print(f"   ✅ Added {table}.{column}")

    conn.close()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
