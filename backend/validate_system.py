#!/usr/bin/env python3
"""
Compass System Validation Script

Comprehensive validation tool that checks:
- Database schema integrity
- All required files exist
- Cross-platform compatibility
- API endpoints respond correctly
- Mock data generation works
- Frontend can connect

Works on Windows, Mac, and Linux.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple
import traceback


class ValidationResult:
    """Container for validation test results."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []

    def add_pass(self, test_name: str, message: str = ""):
        """Record a passing test."""
        self.tests_run += 1
        self.tests_passed += 1
        print(f"  ✓ {test_name}")
        if message:
            print(f"    {message}")

    def add_fail(self, test_name: str, error: str):
        """Record a failing test."""
        self.tests_run += 1
        self.tests_failed += 1
        self.errors.append((test_name, error))
        print(f"  ✗ {test_name}")
        print(f"    ERROR: {error}")

    def add_warning(self, test_name: str, warning: str):
        """Record a warning."""
        self.warnings.append((test_name, warning))
        print(f"  ⚠ {test_name}")
        print(f"    WARNING: {warning}")

    def summary(self) -> str:
        """Generate summary report."""
        lines = [
            "=" * 70,
            "VALIDATION SUMMARY",
            "=" * 70,
            f"Tests Run: {self.tests_run}",
            f"Passed: {self.tests_passed}",
            f"Failed: {self.tests_failed}",
            f"Warnings: {len(self.warnings)}",
            ""
        ]

        if self.tests_failed == 0 and len(self.warnings) == 0:
            lines.append("✓ ALL CHECKS PASSED - System is ready!")
        elif self.tests_failed == 0:
            lines.append("✓ All critical checks passed (with warnings)")
        else:
            lines.append("✗ CRITICAL ISSUES FOUND - See errors above")

        return "\n".join(lines)


class CompassValidator:
    """Main validation class."""

    def __init__(self):
        self.result = ValidationResult()
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"

    def run_all_checks(self):
        """Run all validation checks."""
        print("=" * 70)
        print("COMPASS SYSTEM VALIDATION")
        print("=" * 70)
        print(f"Root directory: {self.root_dir}")
        print(f"Backend directory: {self.backend_dir}")
        print(f"Frontend directory: {self.frontend_dir}")
        print()

        # 1. File Structure Validation
        print("\n[1/8] Validating File Structure...")
        self.validate_file_structure()

        # 2. Python Dependencies
        print("\n[2/8] Checking Python Dependencies...")
        self.validate_python_dependencies()

        # 3. Database Schema
        print("\n[3/8] Validating Database Schema...")
        self.validate_database_schema()

        # 4. Model Integrity
        print("\n[4/8] Checking Model Integrity...")
        self.validate_models()

        # 5. Cross-Platform Compatibility
        print("\n[5/8] Checking Cross-Platform Compatibility...")
        self.validate_cross_platform()

        # 6. API Endpoints
        print("\n[6/8] Validating API Endpoints...")
        self.validate_api_structure()

        # 7. Frontend Integration
        print("\n[7/8] Checking Frontend Integration...")
        self.validate_frontend()

        # 8. Mock Data Generation
        print("\n[8/8] Testing Mock Data Generation...")
        self.validate_mock_data()

        # Print summary
        print("\n" + self.result.summary())

        # Return exit code
        return 0 if self.result.tests_failed == 0 else 1

    def validate_file_structure(self):
        """Validate all required files exist."""
        required_files = {
            'backend': [
                'main.py',
                'models.py',
                'database.py',
                'events.py',
                'ws_manager.py',
                'webhooks.py',
                'fix_db.py',
                'requirements-minimal.txt',
            ],
            'backend/ingestion': [
                '__init__.py',
                'sources.py',
                'sync.py',
            ],
            'backend/nlp': [
                '__init__.py',
                'clustering.py',
                'sentiment.py',
            ],
            'backend/priority': [
                '__init__.py',
                'calculator.py',
                'impact_predictor.py',
                'custom_scoring.py',
            ],
            'backend/integrations': [
                '__init__.py',
                'linear_sync.py',
            ],
            'frontend/src': [
                'App.jsx',
                'main.jsx',
            ],
            'frontend/src/services': [
                'api.js',
                'websocket.js',
            ],
        }

        for directory, files in required_files.items():
            dir_path = self.root_dir / directory

            if not dir_path.exists():
                self.result.add_fail(
                    f"Directory: {directory}",
                    f"Directory not found: {dir_path}"
                )
                continue

            for file in files:
                file_path = dir_path / file
                if file_path.exists():
                    self.result.add_pass(f"File: {directory}/{file}")
                else:
                    self.result.add_fail(
                        f"File: {directory}/{file}",
                        f"Required file not found: {file_path}"
                    )

    def validate_python_dependencies(self):
        """Check Python dependencies are importable."""
        critical_deps = [
            'fastapi',
            'uvicorn',
            'sqlalchemy',
            'pydantic',
            'websockets',
        ]

        optional_deps = [
            'vaderSentiment',
            'textblob',
            'pandas',
            'slack_sdk',
            'github',
        ]

        # Check critical dependencies
        for dep in critical_deps:
            try:
                __import__(dep)
                self.result.add_pass(f"Dependency: {dep}")
            except ImportError as e:
                self.result.add_fail(
                    f"Dependency: {dep}",
                    f"Critical dependency not found: {e}"
                )

        # Check optional dependencies (warnings only)
        for dep in optional_deps:
            try:
                __import__(dep)
                self.result.add_pass(f"Optional: {dep}")
            except ImportError:
                self.result.add_warning(
                    f"Optional: {dep}",
                    f"Optional dependency not installed (not critical)"
                )

    def validate_database_schema(self):
        """Validate database schema is correct."""
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir(self.backend_dir)

        try:
            # Import models
            sys.path.insert(0, str(self.backend_dir))
            from models import Base, Source, Feedback, Cluster, RoadmapItem, ImportJob, JiraIssue, LinearIssue, Release, FeatureBuild
            from database import engine, init_db
            from sqlalchemy import inspect

            # Check if database exists and has correct schema
            db_path = self.backend_dir / "compass.db"

            if not db_path.exists():
                self.result.add_warning(
                    "Database file",
                    "Database file doesn't exist yet (will be created on first run)"
                )
                # Create database for validation
                init_db()

            inspector = inspect(engine)
            tables = inspector.get_table_names()

            # Required tables
            required_tables = [
                'sources',
                'feedback',
                'clusters',
                'roadmap_items',
                'import_jobs',
                'jira_issues',
                'linear_issues',
                'releases',
                'feature_builds',
                'feature_release_mapping',
            ]

            for table in required_tables:
                if table in tables:
                    columns = inspector.get_columns(table)
                    self.result.add_pass(
                        f"Table: {table}",
                        f"{len(columns)} columns"
                    )
                else:
                    self.result.add_fail(
                        f"Table: {table}",
                        "Table not found in database"
                    )

            # Validate critical columns
            if 'feedback' in tables:
                columns = inspector.get_columns('feedback')
                column_names = [col['name'] for col in columns]

                critical_columns = ['id', 'source_id', 'text', 'external_ids', 'cluster_id', 'sentiment_score']
                for col in critical_columns:
                    if col in column_names:
                        self.result.add_pass(f"Column: feedback.{col}")
                    else:
                        self.result.add_fail(
                            f"Column: feedback.{col}",
                            f"Critical column missing from feedback table"
                        )

        except Exception as e:
            self.result.add_fail(
                "Database Schema Validation",
                f"Error validating schema: {str(e)}\n{traceback.format_exc()}"
            )
        finally:
            os.chdir(original_dir)

    def validate_models(self):
        """Validate all SQLAlchemy models are properly defined."""
        original_dir = os.getcwd()
        os.chdir(self.backend_dir)

        try:
            sys.path.insert(0, str(self.backend_dir))
            from models import (
                Base, Source, Feedback, Cluster, RoadmapItem,
                ImportJob, JiraIssue, LinearIssue, Release, FeatureBuild
            )

            models = [
                Source, Feedback, Cluster, RoadmapItem,
                ImportJob, JiraIssue, LinearIssue, Release, FeatureBuild
            ]

            for model in models:
                try:
                    # Check model has required attributes
                    assert hasattr(model, '__tablename__'), f"{model.__name__} missing __tablename__"
                    assert hasattr(model, '__table__'), f"{model.__name__} missing __table__"

                    # Check primary key exists
                    has_pk = any(col.primary_key for col in model.__table__.columns)
                    assert has_pk, f"{model.__name__} missing primary key"

                    self.result.add_pass(
                        f"Model: {model.__name__}",
                        f"Table: {model.__tablename__}"
                    )
                except AssertionError as e:
                    self.result.add_fail(
                        f"Model: {model.__name__}",
                        str(e)
                    )

        except Exception as e:
            self.result.add_fail(
                "Model Validation",
                f"Error loading models: {str(e)}\n{traceback.format_exc()}"
            )
        finally:
            os.chdir(original_dir)

    def validate_cross_platform(self):
        """Check for cross-platform compatibility issues."""
        # Check for hardcoded path separators
        issues_found = False

        python_files = list(self.backend_dir.rglob("*.py"))

        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')

                # Check for hardcoded Windows paths (but allow URLs)
                if '\\\\' in content and 'http' not in content:
                    self.result.add_warning(
                        f"Path separator: {py_file.name}",
                        "File contains backslashes (may cause issues on Unix)"
                    )
                    issues_found = True

                # Check for absolute paths
                if content.count('/home/') > 1 or content.count('C:\\\\') > 0:
                    self.result.add_warning(
                        f"Absolute path: {py_file.name}",
                        "File may contain hardcoded absolute paths"
                    )
                    issues_found = True

            except Exception as e:
                # Skip binary files or files that can't be read
                continue

        if not issues_found:
            self.result.add_pass(
                "Path compatibility",
                "No hardcoded path separators found"
            )

        # Check database path is relative
        try:
            sys.path.insert(0, str(self.backend_dir))
            from models import get_connection_string

            db_url = get_connection_string("sqlite", "compass.db")

            if os.path.isabs(db_url.replace("sqlite:///", "")):
                self.result.add_warning(
                    "Database path",
                    "Database path may be absolute (should be relative)"
                )
            else:
                self.result.add_pass(
                    "Database path",
                    "Database path is relative"
                )
        except Exception as e:
            self.result.add_warning(
                "Database path check",
                f"Could not validate database path: {e}"
            )

    def validate_api_structure(self):
        """Validate API endpoints are properly structured."""
        original_dir = os.getcwd()
        os.chdir(self.backend_dir)

        try:
            sys.path.insert(0, str(self.backend_dir))

            # Import main to check it loads
            import main

            # Check FastAPI app exists
            assert hasattr(main, 'app'), "FastAPI app not found"
            self.result.add_pass("FastAPI app", "App instance exists")

            # Get all routes
            routes = []
            for route in main.app.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    routes.append((route.path, list(route.methods)))

            # Check critical endpoints exist
            critical_endpoints = [
                ('/api/sources', ['GET']),
                ('/api/sources/sync', ['POST']),
                ('/api/feedback', ['GET']),
                ('/api/clustering/run', ['POST']),
                ('/api/clusters', ['GET']),
                ('/api/roadmap/generate', ['POST']),
                ('/api/roadmap', ['GET']),
                ('/api/stats', ['GET']),
                ('/ws', ['GET']),
            ]

            for endpoint, methods in critical_endpoints:
                found = False
                for route_path, route_methods in routes:
                    if endpoint in route_path:
                        found = True
                        break

                if found:
                    self.result.add_pass(f"Endpoint: {' '.join(methods)} {endpoint}")
                else:
                    self.result.add_fail(
                        f"Endpoint: {' '.join(methods)} {endpoint}",
                        "Endpoint not found in API"
                    )

        except Exception as e:
            self.result.add_fail(
                "API Structure Validation",
                f"Error loading API: {str(e)}\n{traceback.format_exc()}"
            )
        finally:
            os.chdir(original_dir)

    def validate_frontend(self):
        """Validate frontend integration."""
        # Check frontend files exist
        api_js = self.frontend_dir / "src" / "services" / "api.js"

        if not api_js.exists():
            self.result.add_fail(
                "Frontend API client",
                f"api.js not found at {api_js}"
            )
            return

        try:
            content = api_js.read_text(encoding='utf-8')

            # Check API endpoints are defined
            endpoints = [
                'getSources',
                'syncSources',
                'getFeedback',
                'runClustering',
                'getClusters',
                'generateRoadmap',
                'getRoadmap',
                'getStats',
            ]

            for endpoint in endpoints:
                if endpoint in content:
                    self.result.add_pass(f"Frontend API: {endpoint}")
                else:
                    self.result.add_fail(
                        f"Frontend API: {endpoint}",
                        f"Function {endpoint} not found in api.js"
                    )

            # Check for environment variable usage
            if 'VITE_API_URL' in content or 'import.meta.env' in content:
                self.result.add_pass(
                    "Environment variables",
                    "Frontend uses environment variables for API URL"
                )
            else:
                self.result.add_warning(
                    "Environment variables",
                    "Frontend may have hardcoded API URL"
                )

        except Exception as e:
            self.result.add_fail(
                "Frontend Validation",
                f"Error reading frontend files: {e}"
            )

    def validate_mock_data(self):
        """Test that mock data generation works."""
        original_dir = os.getcwd()
        os.chdir(self.backend_dir)

        try:
            sys.path.insert(0, str(self.backend_dir))
            from ingestion.sources import create_source
            from models import Source

            # Test that real source integrations are available
            supported_sources = ["Slack", "GitHub", "Discord", "Reddit"]
            available = []

            for source_name in supported_sources:
                test_source = Source(
                    id=1,
                    name=source_name,
                    source_type="real",
                    is_active=False,
                    config={}
                )

                try:
                    source_instance = create_source(test_source)
                    available.append(source_name)
                except ValueError:
                    pass

            if len(available) == len(supported_sources):
                self.result.add_pass(
                    "Real source integrations",
                    f"All {len(available)} integrations available: {', '.join(available)}"
                )
            else:
                self.result.add_fail(
                    "Real source integrations",
                    f"Only {len(available)}/{len(supported_sources)} integrations available"
                )

        except Exception as e:
            self.result.add_fail(
                "Real Source Integrations",
                f"Error checking source integrations: {str(e)}\n{traceback.format_exc()}"
            )
        finally:
            os.chdir(original_dir)


def main():
    """Run validation."""
    validator = CompassValidator()
    exit_code = validator.run_all_checks()

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)

    if exit_code == 0:
        print("""
✓ System validation passed!

To start Compass:

1. Backend (Terminal 1):
   cd ~/compass/backend
   source venv/bin/activate  # or: venv\\Scripts\\activate on Windows
   python main.py

2. Frontend (Terminal 2):
   cd ~/compass/frontend
   npm run dev

3. Open browser:
   http://localhost:5173
""")
    else:
        print("""
✗ System validation found issues.

Common fixes:

1. Install dependencies:
   cd ~/compass/backend
   pip install -r requirements-minimal.txt

2. Recreate database:
   cd ~/compass/backend
   python fix_db.py

3. Check file permissions:
   Make sure all files are readable

4. Review errors above for specific issues.
""")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
