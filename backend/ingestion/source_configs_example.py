"""
Example configurations for all Compass feedback sources.

This file demonstrates how to configure each source type.
Copy these examples and update with your actual credentials.

SECURITY WARNING: Never commit real credentials to version control!
Use environment variables or a secrets manager in production.
"""

from datetime import datetime

# =============================================================================
# GITHUB INTEGRATION
# =============================================================================

GITHUB_CONFIG = {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Personal access token
    "repo_owner": "yourorg",                              # GitHub username or org
    "repo_name": "your-product-repo",                     # Repository name
    "labels": ["feedback", "feature-request", "enhancement", "user-feedback"],
    "include_discussions": True,   # Fetch GitHub Discussions (recommended!)
    "include_prs": False           # Set True to include PR comments
}

# Alternative: Monitor multiple repos (create separate sources)
GITHUB_CONFIG_MULTIPLE = [
    {
        "name": "GitHub - Main Repo",
        "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "repo_owner": "yourorg",
        "repo_name": "main-product",
        "labels": ["feedback", "feature-request"],
        "include_discussions": True,
        "include_prs": False
    },
    {
        "name": "GitHub - Public Roadmap",
        "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "repo_owner": "yourorg",
        "repo_name": "public-roadmap",
        "labels": ["community-feedback"],
        "include_discussions": True,
        "include_prs": False
    }
]

# How to get GitHub token:
# 1. Go to: https://github.com/settings/tokens
# 2. Click "Generate new token" → "Personal access tokens (classic)"
# 3. Select scopes:
#    - repo (for private repos) or public_repo (for public only)
#    - read:discussion (for discussions)
# 4. Generate and copy token

# Fine-grained token (recommended):
# 1. Go to: https://github.com/settings/tokens?type=beta
# 2. Select repositories
# 3. Set permissions:
#    - Issues: Read-only
#    - Discussions: Read-only
#    - Pull requests: Read-only (if including PRs)


# =============================================================================
# DISCORD INTEGRATION
# =============================================================================

DISCORD_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",               # Discord bot token
    "guild_id": "123456789012345678",                 # Your server (guild) ID
    "channel_ids": [
        "987654321098765432",                         # #feedback channel
        "876543210987654321"                          # #feature-requests channel
    ],
    "include_threads": True,       # Include thread messages (recommended!)
    "reaction_threshold": 3        # Messages with 3+ reactions = high engagement
}

# Alternative: Monitor community server
DISCORD_CONFIG_COMMUNITY = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "guild_id": "123456789012345678",
    "channel_ids": [
        "111111111111111111",  # #general
        "222222222222222222",  # #feedback
        "333333333333333333",  # #feature-ideas
        "444444444444444444"   # #support
    ],
    "include_threads": True,
    "reaction_threshold": 5  # Higher threshold for busy servers
}

# How to set up Discord bot:
# 1. Go to: https://discord.com/developers/applications
# 2. Click "New Application"
# 3. Go to "Bot" tab → "Add Bot"
# 4. Enable these Privileged Gateway Intents:
#    - MESSAGE CONTENT INTENT (required!)
#    - SERVER MEMBERS INTENT (optional)
# 5. Copy bot token
# 6. Go to OAuth2 → URL Generator:
#    - Scopes: bot
#    - Permissions: Read Messages, Read Message History
# 7. Use generated URL to add bot to your server
# 8. Get IDs (enable Developer Mode in Discord settings):
#    - Right-click server name → Copy ID (guild_id)
#    - Right-click channel → Copy ID (channel_ids)


# =============================================================================
# REDDIT INTEGRATION
# =============================================================================

REDDIT_CONFIG = {
    "client_id": "your_client_id_here",               # Reddit app client ID
    "client_secret": "your_client_secret_here",       # Reddit app secret
    "user_agent": "compass-feedback-bot/1.0 by u/yourusername",  # Required!
    "subreddit": "yourproduct",                       # Subreddit name (no r/)
    "flairs": ["Feedback", "Feature Request", "Suggestion"],  # Optional
    "keywords": ["feature", "request", "feedback", "suggestion", "would love"],
    "sort_by": "new",              # new, hot, top, rising
    "limit": 100                   # Max posts to fetch per sync
}

# Alternative: Monitor product-focused subreddit
REDDIT_CONFIG_PRODUCT = {
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "user_agent": "compass-feedback-bot/1.0 by u/yourusername",
    "subreddit": "SaaS",  # Industry subreddit
    "flairs": [],
    "keywords": ["feedback tool", "customer feedback", "feature requests"],
    "sort_by": "hot",
    "limit": 50
}

# Alternative: Monitor your brand subreddit
REDDIT_CONFIG_BRAND = {
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "user_agent": "compass-feedback-bot/1.0 by u/yourusername",
    "subreddit": "yourproductname",
    "flairs": ["Feedback", "Feature Request", "Bug Report"],
    "keywords": [],  # No keywords = fetch all posts
    "sort_by": "new",
    "limit": 200
}

# How to set up Reddit app:
# 1. Go to: https://www.reddit.com/prefs/apps
# 2. Scroll to bottom → "create another app..."
# 3. Choose "script" type
# 4. Fill in:
#    - name: compass-feedback-integration
#    - description: Feedback collection for Compass
#    - redirect uri: http://localhost:8080 (not used for scripts)
# 5. Click "create app"
# 6. Copy:
#    - Client ID: text under app name
#    - Client Secret: labeled "secret"
# 7. user_agent format: "appname/version by u/yourusername"


# =============================================================================
# SLACK INTEGRATION (EXISTING)
# =============================================================================

SLACK_CONFIG = {
    "token": "xoxb-your-slack-bot-token",
    "channel_ids": ["C01234567890", "C09876543210"]
}


# =============================================================================
# DATABASE INSERTION EXAMPLE
# =============================================================================

def insert_sources_to_db(db_session):
    """
    Example function showing how to add these sources to your database.

    Usage:
        from sqlalchemy.orm import Session
        from database import engine
        from models import Source

        with Session(engine) as session:
            insert_sources_to_db(session)
    """
    from models import Source

    sources = [
        Source(
            name="GitHub",
            source_type="real",
            is_active=True,
            config=GITHUB_CONFIG,
            created_at=datetime.utcnow()
        ),
        Source(
            name="Discord",
            source_type="real",
            is_active=True,
            config=DISCORD_CONFIG,
            created_at=datetime.utcnow()
        ),
        Source(
            name="Reddit",
            source_type="real",
            is_active=True,
            config=REDDIT_CONFIG,
            created_at=datetime.utcnow()
        )
    ]

    for source in sources:
        db_session.add(source)

    db_session.commit()
    print(f"✓ Added {len(sources)} sources to database")


# =============================================================================
# ENVIRONMENT VARIABLES (RECOMMENDED FOR PRODUCTION)
# =============================================================================

"""
In production, use environment variables instead of hardcoded credentials:

import os

GITHUB_CONFIG = {
    "token": os.getenv("GITHUB_TOKEN"),
    "repo_owner": os.getenv("GITHUB_REPO_OWNER"),
    "repo_name": os.getenv("GITHUB_REPO_NAME"),
    # ...
}

DISCORD_CONFIG = {
    "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
    "guild_id": os.getenv("DISCORD_GUILD_ID"),
    "channel_ids": os.getenv("DISCORD_CHANNEL_IDS", "").split(","),
    # ...
}

REDDIT_CONFIG = {
    "client_id": os.getenv("REDDIT_CLIENT_ID"),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
    "user_agent": os.getenv("REDDIT_USER_AGENT"),
    "subreddit": os.getenv("REDDIT_SUBREDDIT"),
    # ...
}

Then create a .env file:
    GITHUB_TOKEN=ghp_xxxxx
    GITHUB_REPO_OWNER=yourorg
    GITHUB_REPO_NAME=yourrepo

    DISCORD_BOT_TOKEN=xxxxx
    DISCORD_GUILD_ID=123456789
    DISCORD_CHANNEL_IDS=111111,222222,333333

    REDDIT_CLIENT_ID=xxxxx
    REDDIT_CLIENT_SECRET=xxxxx
    REDDIT_USER_AGENT=compass-bot/1.0
    REDDIT_SUBREDDIT=yourproduct
"""


# =============================================================================
# TESTING CONFIGURATIONS
# =============================================================================

def test_configuration(config_name: str, config: dict):
    """
    Test if a configuration has all required fields.

    Usage:
        test_configuration("GitHub", GITHUB_CONFIG)
    """
    required_fields = {
        "GitHub": ["token", "repo_owner", "repo_name"],
        "Discord": ["bot_token", "guild_id", "channel_ids"],
        "Reddit": ["client_id", "client_secret", "user_agent", "subreddit"]
    }

    missing = []
    for field in required_fields.get(config_name, []):
        if field not in config or not config[field]:
            missing.append(field)

    if missing:
        print(f"❌ {config_name} config missing: {', '.join(missing)}")
        return False
    else:
        print(f"✓ {config_name} config looks good!")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("COMPASS FEEDBACK SOURCES - CONFIGURATION EXAMPLES")
    print("=" * 60)

    print("\n📋 This file contains example configurations for:")
    print("  • GitHub Issues & Discussions")
    print("  • Discord Server Messages")
    print("  • Reddit Posts & Comments")
    print("  • Slack Messages (existing)")

    print("\n⚠️  SECURITY REMINDER:")
    print("  Never commit real credentials to version control!")
    print("  Use environment variables or a secrets manager.")

    print("\n🧪 Testing configurations...")
    test_configuration("GitHub", GITHUB_CONFIG)
    test_configuration("Discord", DISCORD_CONFIG)
    test_configuration("Reddit", REDDIT_CONFIG)

    print("\n📚 Next steps:")
    print("  1. Copy these examples to your config file")
    print("  2. Replace placeholder values with real credentials")
    print("  3. Test with: python test_new_sources.py")
    print("  4. Add to database using insert_sources_to_db()")
    print("=" * 60)
