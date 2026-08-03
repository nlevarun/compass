"""
Mock data generators for 7 feedback sources.

Generates 500+ realistic feedback entries with:
- Diverse customer names and realistic revenue distribution (power law)
- Temporal patterns (recent feedback weighted higher)
- Varied sentiment and content
- 50 templates × 10+ variations = 500+ unique entries
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


# Customer data with power law revenue distribution
COMPANIES = [
    ("Acme Corp", 5000000), ("TechStart Inc", 150000), ("Global Dynamics", 3200000),
    ("Micro Solutions", 80000), ("Enterprise Systems", 4500000), ("Digital Ventures", 250000),
    ("Cloud Nine", 750000), ("Data Insights", 1200000), ("Smart Analytics", 95000),
    ("Future Tech", 180000), ("Quantum Labs", 2800000), ("Pixel Perfect", 120000),
    ("Code Crafters", 420000), ("Beta Testing Co", 65000), ("Alpha Innovations", 3800000),
    ("Omega Solutions", 220000), ("Prime Industries", 1900000), ("Summit Corp", 380000),
    ("Apex Systems", 540000), ("Vertex Tech", 890000), ("Nexus Digital", 1500000),
    ("Horizon Enterprises", 280000), ("Phoenix Solutions", 670000), ("Atlas Group", 2100000),
    ("Titan Technologies", 310000), ("Orion Systems", 450000), ("Zenith Corp", 1800000),
    ("Nova Innovations", 190000), ("Eclipse Tech", 560000), ("Pulse Analytics", 740000),
    ("Spark Digital", 125000), ("Blaze Software", 980000), ("Storm Systems", 410000),
    ("Thunder Tech", 290000), ("Lightning Fast", 620000), ("Rocket Labs", 2400000),
    ("Turbo Solutions", 170000), ("Sprint Systems", 830000), ("Dash Technologies", 350000),
    ("Zoom Corp", 710000), ("Flash Innovations", 260000), ("Swift Digital", 1600000),
    ("Rapid Systems", 390000), ("Quick Solutions", 520000), ("Fast Track", 880000),
    ("Velocity Tech", 1100000), ("Speed Corp", 240000), ("Pace Innovations", 640000),
    ("Momentum Systems", 930000), ("Flow Solutions", 470000)
]


# Feedback templates by theme
FEEDBACK_TEMPLATES = {
    # Performance issues (Mobile app)
    "mobile_performance": [
        "The mobile app is really slow when {action}. Takes {time} to load.",
        "App crashes frequently when {action}. Very frustrating for our team.",
        "Mobile performance has degraded since {version}. Please fix!",
        "Loading times on mobile are unacceptable. {metric} is way too high.",
        "The app freezes when {action}. Need better mobile optimization.",
    ],

    # API/Integration requests
    "api_integration": [
        "We need a {platform} integration to sync our data automatically.",
        "API documentation is missing {feature}. Can you add this?",
        "Rate limits on the API are too restrictive for our {use_case}.",
        "Webhook support for {event} would save us hours of manual work.",
        "Need better API error messages. Current ones don't help debug.",
    ],

    # Reporting/Analytics
    "reporting": [
        "Can you add {metric} to the analytics dashboard?",
        "Export to {format} would be incredibly valuable for our workflow.",
        "Custom report builder is missing {feature}. This is critical.",
        "Real-time dashboards would help us make faster decisions.",
        "Historical data beyond {timeframe} is not available. Need longer retention.",
    ],

    # User management
    "user_management": [
        "SSO with {provider} is essential for our enterprise deployment.",
        "Role-based permissions are too basic. Need {granularity}.",
        "Can't bulk import users. This is painful for onboarding.",
        "Audit logs don't capture {action}. Required for compliance.",
        "User provisioning via SCIM would streamline our IT processes.",
    ],

    # Pricing/Billing
    "pricing": [
        "Per-seat pricing doesn't work for our {team_size} organization.",
        "Need usage-based billing instead of flat rate.",
        "Annual commitment discount would help us commit long-term.",
        "Billing dashboard is confusing. Can't see {metric} easily.",
        "Invoice customization for {requirement} is needed for procurement.",
    ],

    # UI/UX improvements
    "ui_ux": [
        "The {screen} interface is cluttered. Needs simplification.",
        "Dark mode support would be amazing for late-night work.",
        "Keyboard shortcuts for {action} would boost productivity.",
        "Can you add {feature} to the quick actions menu?",
        "Drag-and-drop for {object} would make workflows much faster.",
    ],

    # Collaboration features
    "collaboration": [
        "Comments on {object} would improve team communication.",
        "@mentions in {context} would help notify the right people.",
        "Shared workspaces for cross-functional teams are needed.",
        "Activity feed showing {event} changes would keep everyone aligned.",
        "Version history for {object} is crucial for our workflow.",
    ],

    # Security/Compliance
    "security": [
        "SOC 2 compliance documentation is missing. We need this for audit.",
        "Data encryption at rest is required for our industry.",
        "IP whitelisting would meet our security policies.",
        "2FA via {method} is needed for our security team.",
        "Data residency in {region} is a hard requirement for us.",
    ],

    # Search/Filtering
    "search": [
        "Search doesn't work well for {query_type}. Results are irrelevant.",
        "Advanced filters for {attribute} would save tons of time.",
        "Saved search queries would eliminate repetitive work.",
        "Fuzzy matching for {field} would help with typos.",
        "Boolean search operators would make queries more powerful.",
    ],

    # Notifications
    "notifications": [
        "Email notifications are too frequent. Need better controls.",
        "Slack integration for {event} alerts would be super useful.",
        "Digest emails (daily/weekly) instead of individual notifications.",
        "Custom notification rules based on {condition} please.",
        "Mobile push notifications for {event} are critical.",
    ]
}

# Substitution options for templates
SUBSTITUTIONS = {
    "action": ["scrolling", "uploading files", "searching", "opening reports", "syncing data", "switching views", "filtering lists"],
    "time": ["10+ seconds", "over 30 seconds", "several minutes", "too long", "forever"],
    "version": ["last update", "v2.3", "the recent release", "March update", "latest version"],
    "metric": ["response time", "page load", "query execution", "API latency", "rendering"],
    "platform": ["Salesforce", "Slack", "Jira", "HubSpot", "Zapier", "Monday.com", "Asana"],
    "feature": ["pagination", "rate limit info", "endpoint for X", "authentication details", "webhook signatures"],
    "use_case": ["data sync", "batch processing", "real-time updates", "large imports", "automated workflows"],
    "event": ["record updates", "user actions", "status changes", "new entries", "deletions"],
    "format": ["Excel", "CSV", "PDF", "Google Sheets", "JSON"],
    "metric": ["conversion rate", "user engagement", "retention metrics", "revenue breakdown", "funnel analysis"],
    "timeframe": ["90 days", "6 months", "1 year", "2 years", "Q1 2024"],
    "provider": ["Okta", "Azure AD", "Google Workspace", "OneLogin", "Auth0"],
    "granularity": ["field-level permissions", "object-level controls", "custom roles", "department isolation"],
    "action": ["password resets", "role changes", "data exports", "permission updates", "login attempts"],
    "team_size": ["500+", "enterprise", "growing", "distributed", "multi-regional"],
    "requirement": ["PO numbers", "cost centers", "department codes", "multi-currency", "tax compliance"],
    "screen": ["dashboard", "settings", "reports", "admin panel", "user profile"],
    "object": ["tasks", "projects", "reports", "documents", "records"],
    "context": ["comments", "updates", "chat", "notes", "discussions"],
    "method": ["hardware keys", "authenticator app", "SMS backup", "biometric", "FIDO2"],
    "region": ["EU", "US", "UK", "Canada", "Australia"],
    "query_type": ["partial matches", "dates", "numbers", "multi-word", "special characters"],
    "attribute": ["date ranges", "custom fields", "tags", "status", "assignee"],
    "field": ["names", "emails", "company names", "addresses", "titles"],
    "condition": ["priority", "assignee", "status", "tag", "custom field"],
}


def generate_feedback_text(theme: str) -> Tuple[str, str]:
    """Generate feedback text from template with substitutions."""
    template = random.choice(FEEDBACK_TEMPLATES[theme])

    # Make substitutions
    text = template
    for key, options in SUBSTITUTIONS.items():
        if f"{{{key}}}" in text:
            text = text.replace(f"{{{key}}}", random.choice(options))

    return text, theme


def generate_temporal_date(days_back: int = 180) -> datetime:
    """
    Generate dates with recency bias (more recent = higher probability).
    Uses exponential distribution for realistic temporal patterns.
    """
    # Exponential decay: more recent dates are more likely
    days_ago = int(random.expovariate(1 / 30))  # Average 30 days back
    days_ago = min(days_ago, days_back)  # Cap at days_back
    return datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))


def generate_mock_feedback(source_name: str, count: int) -> List[Dict]:
    """
    Generate realistic mock feedback for a source.

    Args:
        source_name: Name of the feedback source
        count: Number of feedback entries to generate

    Returns:
        List of feedback dictionaries
    """
    feedback_list = []
    themes = list(FEEDBACK_TEMPLATES.keys())

    for i in range(count):
        # Select company (with some repeat customers for realism)
        company, revenue = random.choice(COMPANIES)

        # Generate feedback
        theme = random.choice(themes)
        text, _ = generate_feedback_text(theme)

        # Generate sentiment (correlated with content)
        # Negative themes get lower sentiment
        negative_themes = {"mobile_performance", "pricing", "security"}
        if theme in negative_themes:
            sentiment = random.uniform(-0.8, 0.2)
        else:
            sentiment = random.uniform(-0.3, 0.8)

        # Add contact name variation
        contact_names = [f"{company} User", f"PM at {company}", f"Engineer at {company}", f"CTO at {company}"]

        feedback = {
            "text": text,
            "title": f"Feature request: {theme.replace('_', ' ').title()}" if "request" in source_name.lower() else None,
            "customer_name": random.choice(contact_names),
            "customer_revenue": revenue,
            "sentiment_score": round(sentiment, 3),
            "submitted_at": generate_temporal_date(),
            "metadata": {
                "theme": theme,
                "source": source_name,
                "synthetic": True
            }
        }

        feedback_list.append(feedback)

    return feedback_list


# Source configurations
MOCK_SOURCES = {
    "Email": {
        "type": "mock",
        "description": "Customer emails to support@company.com",
        "feedback_count": 85
    },
    "Support Tickets": {
        "type": "mock",
        "description": "Zendesk/Intercom support tickets",
        "feedback_count": 120
    },
    "Surveys": {
        "type": "mock",
        "description": "Post-purchase NPS and feature surveys",
        "feedback_count": 95
    },
    "App Reviews": {
        "type": "mock",
        "description": "iOS App Store and Google Play reviews",
        "feedback_count": 65
    },
    "Sales Calls": {
        "type": "mock",
        "description": "Notes from sales discovery calls",
        "feedback_count": 45
    },
    "User Interviews": {
        "type": "mock",
        "description": "Transcripts from user research interviews",
        "feedback_count": 35
    },
    "Social Media": {
        "type": "mock",
        "description": "Twitter mentions and LinkedIn posts",
        "feedback_count": 55
    }
}


def generate_all_mock_data() -> Dict[str, List[Dict]]:
    """
    Generate all mock data for 7 sources (500+ total feedback entries).

    Returns:
        Dictionary mapping source name to list of feedback entries
    """
    all_data = {}

    for source_name, config in MOCK_SOURCES.items():
        print(f"Generating {config['feedback_count']} entries for {source_name}...")
        feedback = generate_mock_feedback(source_name, config['feedback_count'])
        all_data[source_name] = feedback

    total = sum(len(f) for f in all_data.values())
    print(f"\n✓ Generated {total} total feedback entries across {len(all_data)} sources")

    return all_data


if __name__ == "__main__":
    # Test data generation
    print("Testing mock data generation...\n")

    data = generate_all_mock_data()

    # Show samples
    print("\n--- Sample Feedback ---")
    for source, feedback_list in list(data.items())[:2]:
        print(f"\n{source} (showing 2/{len(feedback_list)}):")
        for fb in feedback_list[:2]:
            print(f"  • {fb['customer_name']}: \"{fb['text']}\"")
            print(f"    Revenue: ${fb['customer_revenue']:,} | Sentiment: {fb['sentiment_score']}")
