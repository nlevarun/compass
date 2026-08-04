#!/bin/bash
# setup_simple.sh - Simple setup without venv

echo "========================================"
echo "  Compass Simple Setup"
echo "========================================"
echo ""

cd /home/wsl-user/compass/backend

# Install dependencies with --user flag (no venv needed)
echo "Installing dependencies..."
python3 -m pip install --user --quiet fastapi uvicorn sqlalchemy pydantic python-multipart 2>&1 | grep -v "WARNING"

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Clean old database
echo "Cleaning old database..."
if [ -f compass.db ]; then
    rm compass.db
    echo "✅ Old database removed"
else
    echo "✅ No old database to clean"
fi

echo ""

# Initialize database
echo "Initializing database..."
python3 - <<'EOF'
from database import init_db, get_db
from models import Source, Feedback
from datetime import datetime, timedelta
import random

print("Creating database tables...")
init_db()

print("Creating sample sources...")
with get_db() as db:
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
    topics = [
        ("Mobile app crashes", "The mobile app keeps crashing", -0.7),
        ("Export feature", "Need Excel export", 0.5),
        ("Dark mode", "Please add dark mode!", 0.6),
        ("API limits", "API rate limits too restrictive", -0.4),
        ("SSO needed", "Need SSO with Azure AD", 0.3),
    ]

    customers = [
        ("Acme Corp", 500000),
        ("TechStart Inc", 250000),
        ("Global Systems", 1000000),
        ("StartupXYZ", 50000),
    ]

    for i in range(50):
        topic, text, sentiment = random.choice(topics)
        customer, revenue = random.choice(customers)
        source = random.choice(sources)

        feedback = Feedback(
            source_id=source.id,
            text=f"{text} - Really needed!",
            title=f"{topic} - {customer}",
            customer_name=customer,
            customer_revenue=revenue,
            sentiment_score=sentiment,
            submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            source_metadata={"mock": True}
        )
        db.add(feedback)

    db.commit()
    print(f"✅ Created 50 sample feedback items")

print("\n✅ Setup complete!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  ✅ Setup Complete!"
    echo "========================================"
    echo ""
    echo "To start the server:"
    echo "  cd /home/wsl-user/compass/backend"
    echo "  python3 main_simple.py"
    echo ""
    echo "Or with uvicorn:"
    echo "  python3 -m uvicorn main_simple:app --reload --port 8000"
    echo ""
else
    echo ""
    echo "❌ Setup failed"
    exit 1
fi
