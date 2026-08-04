"""
Database migration script to add webhook receiver tables.

Run this to add the new WebhookReceiverConfig and WebhookEvent tables
to your existing Compass database.
"""

from sqlalchemy import create_engine, inspect
from models import Base, WebhookReceiverConfig, WebhookEvent
from database import get_connection_string


def check_table_exists(engine, table_name):
    """Check if a table already exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_webhook_tables():
    """Add webhook receiver tables to database if they don't exist."""
    print("🔄 Starting webhook tables migration...")

    # Get database connection
    connection_string = get_connection_string()
    engine = create_engine(connection_string, echo=True)

    # Check if tables already exist
    webhook_config_exists = check_table_exists(engine, "webhook_receiver_configs")
    webhook_event_exists = check_table_exists(engine, "webhook_events")

    if webhook_config_exists and webhook_event_exists:
        print("✅ Webhook tables already exist. No migration needed.")
        return

    # Create only the new tables
    tables_to_create = []

    if not webhook_config_exists:
        tables_to_create.append(WebhookReceiverConfig.__table__)
        print("📝 Will create: webhook_receiver_configs")

    if not webhook_event_exists:
        tables_to_create.append(WebhookEvent.__table__)
        print("📝 Will create: webhook_events")

    # Create the tables
    if tables_to_create:
        Base.metadata.create_all(engine, tables=tables_to_create)
        print(f"✅ Successfully created {len(tables_to_create)} tables")
    else:
        print("✅ No tables to create")

    print("🎉 Migration complete!")


if __name__ == "__main__":
    migrate_webhook_tables()
