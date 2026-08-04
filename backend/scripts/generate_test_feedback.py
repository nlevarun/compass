"""
Generate realistic test feedback data for clustering validation.

Creates diverse feedback across multiple categories:
- Mobile app performance
- API/Integration requests
- Analytics/Reporting
- UI/UX improvements
- Security/Compliance
- Pricing/Billing
- Other

Use this to test and validate clustering accuracy.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy.orm import Session
    from models import Feedback, Source
    from database import SessionLocal, init_db
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


# Feedback templates by category
FEEDBACK_TEMPLATES = {
    "mobile_performance": [
        "The mobile app is extremely slow when scrolling through lists",
        "App crashes every time I try to upload a large file",
        "Performance has gotten significantly worse since the last update",
        "iPhone app freezes when opening documents larger than 5MB",
        "Android version is laggy and unresponsive, especially on older devices",
        "Loading times are unacceptable on mobile - takes 10+ seconds",
        "App drains my battery way too fast, can't use it all day",
        "Can't use the app offline, this is very frustrating for our field team",
        "Push notifications don't work half the time",
        "Mobile search is broken - can't find anything quickly",
        "App becomes unresponsive after 10 minutes of use",
        "Scrolling performance is terrible with large datasets",
        "Memory usage is too high, causes device to slow down",
        "App takes forever to sync data on cellular connection",
        "Video playback is choppy and buffers constantly"
    ],

    "api_integration": [
        "We desperately need a Salesforce integration to sync customer data",
        "API rate limits are too restrictive for our data volume needs",
        "Missing pagination in the API documentation, very confusing",
        "Webhook reliability is poor - we're missing critical events",
        "Need GraphQL support instead of REST only",
        "API authentication flow is confusing and poorly documented",
        "Bulk operations are not supported, have to make thousands of calls",
        "No way to sync historical data via API efficiently",
        "API response times are slow during peak hours (>2 seconds)",
        "Need better error messages from API - getting generic 500 errors",
        "Missing webhooks for real-time updates",
        "API versioning is confusing, breaking changes without notice",
        "Need better SDKs for Python and Node.js",
        "Can't filter API responses, have to fetch everything",
        "API documentation is outdated and has wrong examples"
    ],

    "analytics_reporting": [
        "Can you add conversion rate metrics to the main dashboard?",
        "Export to Excel would be incredibly valuable for our board meetings",
        "Real-time dashboards would help us make faster business decisions",
        "Need custom date ranges in all reports, not just preset options",
        "Missing key SaaS metrics like MRR, ARR, and churn rate",
        "Can't filter reports by customer segment or region",
        "Dashboard is too slow to load with our data volume",
        "Need to schedule automated report emails weekly",
        "Missing cohort analysis features for understanding retention",
        "Can't create custom calculated fields or formulas",
        "Need better data visualization options (heatmaps, funnels)",
        "Can't export reports to PDF for executive presentations",
        "Missing drill-down capabilities in dashboards",
        "Need year-over-year comparison reports",
        "Can't share reports with external stakeholders securely"
    ],

    "ui_ux": [
        "Please add dark mode! My eyes hurt working at night",
        "Dark theme support would be amazing for our team",
        "Night mode is essential for our 24/7 operations workflow",
        "UI is cluttered and hard to navigate, too much information",
        "Need keyboard shortcuts for power users to work faster",
        "Design feels outdated compared to competitors like Notion",
        "Too many clicks to complete basic tasks - needs streamlining",
        "Mobile UI is not intuitive, users get lost easily",
        "Need customizable layouts and views for different roles",
        "Colors are hard to read for colorblind users (accessibility issue)",
        "Font size is too small, hard to read on laptop screens",
        "Need better onboarding tour for new users",
        "Search functionality is terrible, can't find what I need",
        "Too many confirmation dialogs, slows down workflow",
        "Need drag-and-drop interface for organizing items"
    ],

    "security_compliance": [
        "SSO with Okta is essential for our enterprise security requirements",
        "Need better permission controls for teams and roles",
        "GDPR compliance features are missing (data export, deletion)",
        "Audit logs are not detailed enough for compliance requirements",
        "Need SOC 2 Type II certification to use with enterprise clients",
        "Two-factor authentication is not working properly",
        "Need IP whitelist functionality for security",
        "Session timeout is too long for our security policy",
        "Need end-to-end encryption for sensitive data",
        "Missing SAML support for enterprise SSO",
        "Need better data residency options (EU, US, etc.)",
        "Can't restrict API access by IP address",
        "Need field-level encryption for PII data",
        "Missing security headers (CSP, HSTS, etc.)",
        "Need HIPAA compliance for healthcare clients"
    ],

    "pricing_billing": [
        "Pricing is too high for small teams, can't justify the cost",
        "Need annual billing option for discount (20% off would be great)",
        "Free tier is too limited, can't properly evaluate the product",
        "Billing is confusing, unclear what we're being charged for",
        "Need per-user pricing instead of per-project",
        "Enterprise plan is too expensive compared to competitors",
        "Hidden costs - API calls and storage not included in base plan",
        "Need ability to downgrade plan without losing data",
        "Invoice doesn't have enough detail for accounting",
        "Need multi-currency support for international teams",
        "Can't use purchase orders, credit card only is problematic",
        "Trial period is too short (7 days) to properly evaluate",
        "Need education/non-profit discount",
        "Overage charges are too high (2x base rate)",
        "Need more flexible contract terms (month-to-month)"
    ],

    "collaboration": [
        "Collaboration features are lacking compared to competitors",
        "Can't @mention teammates in comments to notify them",
        "Need real-time co-editing like Google Docs",
        "Missing threaded conversations in comments",
        "Need better workspace organization for large teams",
        "Can't assign tasks to specific team members",
        "Need activity feed to see what team is working on",
        "Missing Slack integration for notifications",
        "Can't share views/filters with team members",
        "Need guest access for external collaborators",
        "Comment notifications are too aggressive (too many emails)",
        "Can't react to comments with emoji",
        "Need version history to see who changed what",
        "Missing team templates for consistent workflows",
        "Can't duplicate projects for new team members"
    ],

    "other": [
        "Documentation is outdated and incomplete, very frustrating",
        "Support response times are too slow (24+ hours)",
        "Need video tutorials for complex features",
        "Mobile app is not available on iPad",
        "Need offline mode for traveling/poor connectivity",
        "Can't import data from competitors (Notion, Asana, etc.)",
        "Email notifications are not customizable enough",
        "Need browser extension for quick access",
        "Desktop app would be better than web-only",
        "Need better search across all content",
        "Performance degrades with large datasets (10k+ items)",
        "Need API usage analytics/monitoring",
        "Can't backup data automatically",
        "Need more integration options (Zapier, Make, etc.)",
        "Language support needed (Spanish, French, German)"
    ]
}


# Customer names and revenues for realistic data
CUSTOMER_DATA = [
    ("Acme Corp", 250000),
    ("TechStart Inc", 50000),
    ("Enterprise Solutions", 1000000),
    ("Small Business Co", 10000),
    ("Global Systems", 500000),
    ("Innovation Labs", 75000),
    ("Digital Dynamics", 150000),
    ("Cloud Services LLC", 300000),
    ("Data Systems Inc", 200000),
    ("Solutions Plus", 100000),
    ("MegaCorp", 2000000),
    ("Startup XYZ", 25000),
    ("Regional Bank", 750000),
    ("Healthcare Partners", 400000),
    ("Retail Chain", 600000),
    ("Manufacturing Co", 350000),
    ("Consulting Group", 125000),
    ("Media Company", 175000),
    ("Finance Tech", 800000),
    ("Education Platform", 90000)
]


def generate_feedback_items(count: int = 100) -> list:
    """
    Generate realistic test feedback items.

    Args:
        count: Number of feedback items to generate

    Returns:
        List of feedback dicts
    """
    feedback_items = []
    categories = list(FEEDBACK_TEMPLATES.keys())

    # Calculate items per category (distributed evenly)
    items_per_category = count // len(categories)
    remainder = count % len(categories)

    for category in categories:
        templates = FEEDBACK_TEMPLATES[category]
        num_items = items_per_category + (1 if remainder > 0 else 0)
        remainder -= 1

        # Generate feedback for this category
        for i in range(num_items):
            # Pick random template
            text = random.choice(templates)

            # Add slight variation to avoid exact duplicates
            variations = [
                text,
                text + " Please prioritize this!",
                text + " Our team really needs this.",
                text + " This is blocking our workflow.",
                text + " Many customers are asking for this."
            ]
            text = random.choice(variations)

            # Pick random customer
            customer_name, customer_revenue = random.choice(CUSTOMER_DATA)

            # Random sentiment (-1 to 1, slightly negative bias for feedback)
            sentiment = random.uniform(-0.5, 0.3)

            # Random timestamp in last 90 days
            days_ago = random.randint(0, 90)
            submitted_at = datetime.utcnow() - timedelta(days=days_ago)

            feedback_items.append({
                "text": text,
                "title": f"Feedback: {category.replace('_', ' ').title()}",
                "customer_name": customer_name,
                "customer_revenue": customer_revenue,
                "sentiment_score": sentiment,
                "submitted_at": submitted_at,
                "category": category
            })

    return feedback_items


def save_to_database(feedback_items: list, source_name: str = "Test Data"):
    """
    Save generated feedback to database.

    Args:
        feedback_items: List of feedback dicts
        source_name: Name of the source
    """
    if not DEPS_AVAILABLE:
        print("Error: Database dependencies not available")
        return

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Get or create test source
        source = db.query(Source).filter(Source.name == source_name).first()
        if not source:
            source = Source(
                name=source_name,
                source_type="mock",
                is_active=True,
                config={"description": "Generated test data for clustering validation"}
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        print(f"Using source: {source.name} (ID: {source.id})")

        # Add feedback
        for item in feedback_items:
            feedback = Feedback(
                source_id=source.id,
                text=item["text"],
                title=item["title"],
                customer_name=item["customer_name"],
                customer_revenue=item["customer_revenue"],
                sentiment_score=item["sentiment_score"],
                submitted_at=item["submitted_at"],
                source_metadata={"category": item["category"]}
            )
            db.add(feedback)

        db.commit()
        print(f"✓ Added {len(feedback_items)} feedback items to database")

    except Exception as e:
        print(f"Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Generate test feedback data")
    parser.add_argument("--count", type=int, default=100, help="Number of feedback items to generate")
    parser.add_argument("--save", action="store_true", help="Save to database")
    parser.add_argument("--output", type=str, help="Save to JSON file")

    args = parser.parse_args()

    print("=" * 70)
    print("GENERATING TEST FEEDBACK DATA")
    print("=" * 70)
    print(f"\nGenerating {args.count} feedback items...\n")

    # Generate feedback
    feedback_items = generate_feedback_items(args.count)

    # Show statistics
    print("Categories:")
    categories = {}
    for item in feedback_items:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} items")

    # Save to database
    if args.save:
        print("\nSaving to database...")
        save_to_database(feedback_items)

    # Save to JSON
    if args.output:
        import json
        output_path = args.output
        with open(output_path, 'w') as f:
            # Convert datetime to string for JSON
            for item in feedback_items:
                item["submitted_at"] = item["submitted_at"].isoformat()
            json.dump(feedback_items, f, indent=2)
        print(f"\n✓ Saved to: {output_path}")

    print("\n" + "=" * 70)
    print("✓ DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
