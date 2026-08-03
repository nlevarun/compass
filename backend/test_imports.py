"""
Test script to verify import and integration modules load correctly.
"""

def test_model_imports():
    """Test that new database models can be imported."""
    print("Testing model imports...")
    try:
        from models import ImportJob, JiraIssue, LinearIssue
        print("✓ ImportJob model imported")
        print("✓ JiraIssue model imported")
        print("✓ LinearIssue model imported")
        return True
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False


def test_importer_modules():
    """Test that importer modules can be imported."""
    print("\nTesting importer modules...")
    try:
        # Note: Using 'import' as module name requires special import syntax
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        # Try importing with getattr to handle 'import' keyword
        import importlib
        zendesk_module = importlib.import_module('import.zendesk_importer')
        intercom_module = importlib.import_module('import.intercom_importer')
        csv_module = importlib.import_module('import.csv_importer')

        print("✓ ZendeskImporter module loaded")
        print("✓ IntercomImporter module loaded")
        print("✓ CSVImporter module loaded")
        return True
    except Exception as e:
        print(f"✗ Error importing modules: {e}")
        return False


def test_integration_modules():
    """Test that integration modules can be imported."""
    print("\nTesting integration modules...")
    try:
        from integrations.jira_sync import JiraSync
        from integrations.linear_sync import LinearSync
        print("✓ JiraSync class imported")
        print("✓ LinearSync class imported")
        return True
    except Exception as e:
        print(f"✗ Error importing integrations: {e}")
        return False


def test_database_schema():
    """Test that database schema includes new tables."""
    print("\nTesting database schema...")
    try:
        from sqlalchemy import inspect
        from database import engine

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = ['import_jobs', 'jira_issues', 'linear_issues']
        missing_tables = [t for t in required_tables if t not in tables]

        if missing_tables:
            print(f"✗ Missing tables: {missing_tables}")
            print("  Run: python database.py to create tables")
            return False

        print("✓ All integration tables exist")
        for table in required_tables:
            columns = inspector.get_columns(table)
            print(f"  - {table}: {len(columns)} columns")
        return True
    except Exception as e:
        print(f"✗ Error checking schema: {e}")
        return False


def test_main_imports():
    """Test that main.py can import new dependencies."""
    print("\nTesting main.py imports...")
    try:
        # Test if BackgroundTasks and UploadFile are available
        from fastapi import BackgroundTasks, UploadFile, File
        print("✓ FastAPI background tasks available")
        print("✓ File upload support available")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Compass Import & Integration Module Tests")
    print("=" * 60)

    results = []

    results.append(("Models", test_model_imports()))
    results.append(("Importers", test_importer_modules()))
    results.append(("Integrations", test_integration_modules()))
    results.append(("Main imports", test_main_imports()))
    results.append(("Database Schema", test_database_schema()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nNext steps:")
        print("1. If database tables are missing, run: python database.py")
        print("2. Install Jira library: pip install jira")
        print("3. Start server: python main.py")
        print("4. Test import endpoint: POST /api/import/csv")
    else:
        print("✗ Some tests failed. See errors above.")
        print("\nTroubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: python database.py to create tables")
        print("3. Check Python path and module names")
    print("=" * 60)
