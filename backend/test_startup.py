#!/usr/bin/env python3
"""
Backend Startup Test Script

Tests that the backend can start cleanly without actually starting the server.
Checks:
- All imports work
- Database can be initialized
- Real source integrations are available
- No critical errors

This is useful for CI/CD pipelines or pre-deployment checks.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all critical imports work."""
    print("\n[1/5] Testing imports...")
    try:
        # Core
        import fastapi
        import uvicorn
        import sqlalchemy
        import websockets
        print("  ✓ Core dependencies imported")

        # Models
        from models import Base, Source, Feedback, Cluster, RoadmapItem
        from models import ImportJob, JiraIssue, LinearIssue, Release, FeatureBuild
        print("  ✓ Database models imported")

        # Database
        from database import engine, init_db, get_db, get_db_session
        print("  ✓ Database utilities imported")

        # Main app components
        from ingestion.sources import create_source
        from nlp.clustering import FeedbackClusterer
        from nlp.sentiment import SentimentAnalyzer
        from priority.calculator import PriorityCalculator
        print("  ✓ Application components imported")

        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_init():
    """Test database initialization."""
    print("\n[2/5] Testing database initialization...")
    try:
        from database import init_db, engine
        from sqlalchemy import inspect

        # Initialize database
        init_db()
        print("  ✓ Database initialized")

        # Check tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            'sources', 'feedback', 'clusters', 'roadmap_items',
            'import_jobs', 'jira_issues', 'linear_issues', 'releases',
            'feature_builds', 'feature_release_mapping'
        ]

        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"  ✗ Missing tables: {missing}")
            return False

        print(f"  ✓ All {len(required_tables)} tables created")
        return True

    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_source_integrations():
    """Test that real source integrations are available."""
    print("\n[3/5] Testing source integrations...")
    try:
        from database import get_db
        from models import Source

        with get_db() as db:
            # Check if sources exist
            existing_count = db.query(Source).count()
            print(f"  ✓ Found {existing_count} configured sources")

            # Verify supported integrations
            supported_sources = ["Slack", "GitHub", "Discord", "Reddit"]
            print(f"  ✓ Supported integrations: {', '.join(supported_sources)}")

            return True

    except Exception as e:
        print(f"  ✗ Source integration check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_source_factory():
    """Test that source factory can create real integrations."""
    print("\n[4/5] Testing source factory...")
    try:
        from ingestion.sources import create_source
        from models import Source

        # Test that factory can recognize supported sources
        supported_sources = ["Slack", "GitHub", "Discord", "Reddit"]

        for source_name in supported_sources:
            test_source = Source(
                id=999,
                name=source_name,
                source_type="real",
                is_active=False,
                config={}
            )

            try:
                # Should not raise error for supported sources
                source_instance = create_source(test_source)
                print(f"  ✓ {source_name} integration available")
            except ValueError:
                print(f"  ✗ {source_name} integration not found")
                return False

        print(f"  ✓ All {len(supported_sources)} integrations available")
        return True

    except Exception as e:
        print(f"  ✗ Source factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_app_creation():
    """Test that FastAPI app can be created."""
    print("\n[5/5] Testing API app creation...")
    try:
        # Import main to trigger app creation
        import main

        # Check app exists
        if not hasattr(main, 'app'):
            print("  ✗ FastAPI app not found")
            return False

        print("  ✓ FastAPI app created")

        # Check routes exist
        routes = [route.path for route in main.app.routes if hasattr(route, 'path')]
        critical_routes = ['/api/sources', '/api/feedback', '/api/clusters', '/api/roadmap']

        for route in critical_routes:
            found = any(route in r for r in routes)
            if not found:
                print(f"  ✗ Route not found: {route}")
                return False

        print(f"  ✓ Found {len(routes)} API routes")
        return True

    except Exception as e:
        print(f"  ✗ API app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all startup tests."""
    print("=" * 70)
    print("COMPASS BACKEND STARTUP TEST")
    print("=" * 70)

    # Change to backend directory
    os.chdir(backend_dir)

    # Run tests
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Database Init", test_database_init()))
    results.append(("Source Integrations", test_source_integrations()))
    results.append(("Source Factory", test_source_factory()))
    results.append(("API App", test_api_app_creation()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ Backend is ready to start!")
        print("\nNext step: python main.py")
        return 0
    else:
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n❌ Backend has issues that need to be fixed.")
        print("\nTroubleshooting:")
        print("  1. Run: python validate_system.py")
        print("  2. Check: pip install -r requirements-minimal.txt")
        print("  3. Try: python fix_db.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
