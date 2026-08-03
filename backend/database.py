"""
Database connection and session management for Compass.

Supports both SQLite (MVP) and PostgreSQL (production) with async capabilities.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from models import Base, get_connection_string


# Database configuration
DATABASE_URL = get_connection_string("sqlite", "compass.db")

# Create engine with connection pooling
# For SQLite: use StaticPool and check_same_thread=False for FastAPI async
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False  # Set to True for SQL debugging
)

# Enable WAL mode for SQLite (better concurrency)
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at {DATABASE_URL}")


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup.

    Usage:
        with get_db() as db:
            results = db.query(Feedback).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session():
    """
    Dependency for FastAPI endpoints.

    Usage in FastAPI:
        @app.get("/feedback")
        def get_feedback(db: Session = Depends(get_db_session)):
            return db.query(Feedback).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Migration utilities for PostgreSQL
def migrate_to_postgresql(pg_url: str):
    """
    Migrate from SQLite to PostgreSQL.

    Steps:
    1. Create PostgreSQL database
    2. Export SQLite data
    3. Import to PostgreSQL
    4. Update connection string
    """
    # TODO: Implement when scaling beyond MVP
    raise NotImplementedError("PostgreSQL migration not yet implemented")


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing Compass database...")
    init_db()

    # Verify tables created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n✓ Created tables: {', '.join(tables)}")

    # Show schema
    print("\nDatabase schema:")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n{table}:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
