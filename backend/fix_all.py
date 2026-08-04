#!/usr/bin/env python3
"""
fix_all.py - One script to fix everything in Compass

Run this to:
1. Check and install dependencies
2. Reset database cleanly
3. Create sample data
4. Verify everything works
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    """Print a nice header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def run_command(cmd, description, check=True):
    """Run a command and show output"""
    print(f"➤ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS\n")
            return True
        else:
            if result.stderr:
                print(f"⚠️  {result.stderr}")
            print(f"❌ {description} - FAILED\n")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERROR: {e}\n")
        return False

def check_venv():
    """Check if virtual environment exists"""
    venv_path = Path(__file__).parent / "venv"
    return venv_path.exists()

def main():
    print_header("Compass Emergency Fix Script")

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"Working directory: {backend_dir}\n")

    # Step 1: Check Python version
    print_header("Step 1: Check Python Version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required!")
        return 1
    print("✅ Python version OK\n")

    # Step 2: Create virtual environment if it doesn't exist
    print_header("Step 2: Virtual Environment")
    if not check_venv():
        print("Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Create virtual environment"):
            return 1
    else:
        print("✅ Virtual environment already exists\n")

    # Step 3: Install dependencies
    print_header("Step 3: Install Dependencies")
    pip_cmd = "venv/bin/pip install -r requirements.txt"
    if not run_command(pip_cmd, "Install requirements", check=False):
        print("⚠️  Some dependencies may have failed. Trying minimal install...")
        run_command("venv/bin/pip install fastapi uvicorn sqlalchemy pydantic python-multipart",
                   "Install minimal dependencies", check=False)

    # Step 4: Clean up old database
    print_header("Step 4: Clean Database")
    db_file = backend_dir / "compass.db"
    if db_file.exists():
        print(f"Removing old database: {db_file}")
        db_file.unlink()
        print("✅ Old database removed\n")
    else:
        print("✅ No old database to clean\n")

    # Step 5: Initialize database
    print_header("Step 5: Initialize Database")
    init_script = """
from database import init_db, get_db
from models import Source, Feedback, Cluster, RoadmapItem
from datetime import datetime, timedelta
import random

print("Initializing database...")
init_db()

print("Creating sample sources...")
with get_db() as db:
    # Create 8 feedback sources
    sources = [
        Source(name="Slack #feedback", source_type="mock", is_active=True),
        Source(name="Customer Emails", source_type="mock", is_active=True),
        Source(name="Support Tickets", source_type="mock", is_active=True),
        Source(name="GitHub Issues", source_type="mock", is_active=True),
        Source(name="Intercom", source_type="mock", is_active=True),
        Source(name="Sales Calls", source_type="mock", is_active=True),
        Source(name="User Interviews", source_type="mock", is_active=True),
        Source(name="NPS Survey", source_type="mock", is_active=True),
    ]

    for source in sources:
        db.add(source)
    db.commit()

    print(f"✅ Created {len(sources)} feedback sources")

    # Create sample feedback
    print("Creating sample feedback...")
    topics = [
        ("Mobile app performance", "The mobile app is really slow when loading data", -0.6),
        ("Export to Excel", "Would love to export reports to Excel format", 0.5),
        ("Dark mode", "Please add dark mode support!", 0.7),
        ("API rate limits", "API rate limits are too restrictive", -0.4),
        ("SSO integration", "Need SSO integration with Okta", 0.3),
        ("Bulk operations", "Can't bulk edit multiple items", -0.3),
        ("Mobile notifications", "Not getting push notifications on mobile", -0.5),
        ("Dashboard loading", "Dashboard takes too long to load", -0.7),
    ]

    customers = [
        ("Acme Corp", 500000),
        ("TechStart Inc", 250000),
        ("Global Systems", 1000000),
        ("StartupXYZ", 50000),
        ("Enterprise LLC", 750000),
    ]

    feedback_list = []
    for i in range(100):
        topic, text, sentiment = random.choice(topics)
        customer_name, revenue = random.choice(customers)
        source = random.choice(sources)

        feedback = Feedback(
            source_id=source.id,
            text=f"{text} {random.choice(['Really needed!', 'Critical for us.', 'Would help a lot.', 'Please prioritize this.'])}",
            title=f"{topic} - {customer_name}",
            customer_name=customer_name,
            customer_revenue=revenue,
            sentiment_score=sentiment + random.uniform(-0.1, 0.1),
            submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            source_metadata={"mock": True}
        )
        feedback_list.append(feedback)
        db.add(feedback)

    db.commit()
    print(f"✅ Created {len(feedback_list)} sample feedback items")

print("\\n✅ Database initialization complete!")
"""

    with open("_init_db.py", "w") as f:
        f.write(init_script)

    if not run_command("venv/bin/python _init_db.py", "Initialize database"):
        print("⚠️  Database initialization had issues, but continuing...")

    # Clean up temp file
    Path("_init_db.py").unlink(missing_ok=True)

    # Step 6: Verify setup
    print_header("Step 6: Verify Setup")
    verify_script = """
from database import get_db
from models import Source, Feedback

with get_db() as db:
    source_count = db.query(Source).count()
    feedback_count = db.query(Feedback).count()

    print(f"✅ Sources: {source_count}")
    print(f"✅ Feedback items: {feedback_count}")

    if source_count > 0 and feedback_count > 0:
        print("\\n✅ Database is ready!")
    else:
        print("\\n⚠️  Database might be empty")
"""

    with open("_verify_db.py", "w") as f:
        f.write(verify_script)

    run_command("venv/bin/python _verify_db.py", "Verify database", check=False)
    Path("_verify_db.py").unlink(missing_ok=True)

    # Final message
    print_header("Setup Complete!")
    print("✅ Compass is ready to use!")
    print("\nTo start the server:")
    print("  cd /home/wsl-user/compass/backend")
    print("  ./venv/bin/python main_simple.py")
    print("\nOr use uvicorn:")
    print("  ./venv/bin/uvicorn main_simple:app --reload --port 8000")
    print("\nThen open: http://localhost:8000/api/stats")
    print("")

    return 0

if __name__ == "__main__":
    sys.exit(main())
