# Compass Feedback Sources Integration Guide

## Overview

Compass now supports **11 feedback sources**:
- **8 Mock Sources**: Email, Support Tickets, Surveys, App Reviews, Sales Calls, User Interviews, Social Media, Slack (for demo)
- **4 Real Integrations**: Slack, GitHub, Discord, Reddit

The GitHub, Discord, and Reddit integrations give you a **massive competitive advantage** - no other feedback platform connects to these communities as seamlessly.

---

## Quick Start

### 1. Install Dependencies

```bash
# Install all integrations
pip install -r requirements-minimal.txt

# Or install selectively
pip install PyGithub          # For GitHub
pip install discord.py         # For Discord
pip install praw              # For Reddit
pip install slack-sdk         # For Slack (already included)
```

### 2. Test Integrations

```bash
cd backend/ingestion

# Test all sources
python test_new_sources.py all

# Test individual sources
python test_new_sources.py github
python test_new_sources.py discord
python test_new_sources.py reddit
```

### 3. Configure Your Sources

See `source_configs_example.py` for detailed configuration examples.

---

## Integration Details

### 🐙 GitHub Integration

**What it fetches:**
- Issues (with label filtering)
- Issue comments
- GitHub Discussions (NEW! Few competitors have this)
- Discussion comments
- Pull request comments (optional)

**Setup:**

1. **Create Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Select scopes:
     - `repo` or `public_repo`
     - `read:discussion`
   - Copy token

2. **Configure Source**
   ```python
   GITHUB_CONFIG = {
       "token": "ghp_xxxxxxxxxxxx",
       "repo_owner": "yourorg",
       "repo_name": "your-repo",
       "labels": ["feedback", "feature-request"],
       "include_discussions": True,  # RECOMMENDED!
       "include_prs": False
   }
   ```

3. **Add to Database**
   ```python
   from models import Source
   from database import engine
   from sqlalchemy.orm import Session

   source = Source(
       name="GitHub",
       source_type="real",
       is_active=True,
       config=GITHUB_CONFIG
   )

   with Session(engine) as session:
       session.add(source)
       session.commit()
   ```

**Pro Tips:**
- Use label filtering to avoid noise
- GitHub Discussions are perfect for feature requests
- Set `include_discussions=True` - this is a killer feature!
- Monitor multiple repos by creating separate sources

**Data Captured:**
```json
{
  "text": "Issue/comment body",
  "title": "Issue title",
  "customer_name": "github_username",
  "submitted_at": "2024-01-15T10:30:00Z",
  "source_metadata": {
    "platform": "github",
    "type": "issue|issue_comment|discussion|discussion_comment|pr_comment",
    "url": "https://github.com/org/repo/issues/123",
    "issue_number": 123,
    "state": "open",
    "labels": ["feedback", "enhancement"],
    "comments_count": 5,
    "reactions": {"+1": 15}
  }
}
```

---

### 💬 Discord Integration

**What it fetches:**
- Channel messages
- Thread messages
- Message reactions (as engagement metric)

**Setup:**

1. **Create Discord Bot**
   - Go to: https://discord.com/developers/applications
   - Click "New Application"
   - Go to "Bot" tab → "Add Bot"
   - **IMPORTANT**: Enable "Message Content Intent" under Privileged Gateway Intents
   - Copy bot token

2. **Add Bot to Server**
   - Go to OAuth2 → URL Generator
   - Scopes: `bot`
   - Permissions: `Read Messages`, `Read Message History`
   - Use generated URL to add bot to server

3. **Get IDs**
   - Enable Developer Mode in Discord (Settings → Advanced)
   - Right-click server → Copy ID (guild_id)
   - Right-click channels → Copy ID (channel_ids)

4. **Configure Source**
   ```python
   DISCORD_CONFIG = {
       "bot_token": "YOUR_BOT_TOKEN",
       "guild_id": "123456789012345678",
       "channel_ids": ["987654321098765432"],
       "include_threads": True,
       "reaction_threshold": 3
   }
   ```

**Pro Tips:**
- Monitor specific feedback channels (#feedback, #feature-requests)
- Use `reaction_threshold` to surface high-engagement messages
- Include threads - lots of good feedback happens there
- Bot needs to stay in the server to work

**Data Captured:**
```json
{
  "text": "Message content",
  "title": "Message in #feedback",
  "customer_name": "username#1234",
  "submitted_at": "2024-01-15T10:30:00Z",
  "source_metadata": {
    "platform": "discord",
    "type": "message|thread_message",
    "message_id": "123456789",
    "channel_name": "feedback",
    "guild_name": "Your Server",
    "url": "https://discord.com/channels/...",
    "reactions": [
      {"emoji": "👍", "count": 5},
      {"emoji": "🔥", "count": 3}
    ],
    "total_reactions": 8,
    "high_engagement": true
  }
}
```

---

### 🤖 Reddit Integration

**What it fetches:**
- Subreddit posts (with flair/keyword filtering)
- Post comments
- Upvotes as engagement metric

**Setup:**

1. **Create Reddit App**
   - Go to: https://www.reddit.com/prefs/apps
   - Click "create another app..."
   - Choose type: "script"
   - Name: `compass-feedback-integration`
   - Redirect URI: `http://localhost:8080` (not used)
   - Create app

2. **Get Credentials**
   - Client ID: text under app name
   - Client Secret: labeled "secret"
   - User Agent: `appname/version by u/yourusername`

3. **Configure Source**
   ```python
   REDDIT_CONFIG = {
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "user_agent": "compass-bot/1.0 by u/yourname",
       "subreddit": "yourproduct",
       "flairs": ["Feedback", "Feature Request"],
       "keywords": ["feature", "feedback", "suggestion"],
       "sort_by": "new",
       "limit": 100
   }
   ```

**Pro Tips:**
- Monitor your product's subreddit
- Use keyword filtering to reduce noise
- Upvotes indicate importance - high upvotes = high priority
- Comments often contain detailed feedback
- Try monitoring industry subreddits (r/SaaS, r/startups, etc.)

**Data Captured:**
```json
{
  "text": "Post/comment body",
  "title": "Post title",
  "customer_name": "u/username",
  "submitted_at": "2024-01-15T10:30:00Z",
  "source_metadata": {
    "platform": "reddit",
    "type": "post|comment",
    "post_id": "abc123",
    "subreddit": "yourproduct",
    "url": "https://reddit.com/r/yourproduct/comments/...",
    "flair": "Feature Request",
    "upvotes": 247,
    "upvote_ratio": 0.96,
    "num_comments": 42,
    "engagement_score": 247,
    "awards": 3
  }
}
```

---

## Usage in Code

### Fetching Feedback

```python
from ingestion.sources import create_source
from models import Source
from datetime import datetime, timedelta

# Get source from database
source_model = session.query(Source).filter_by(name="GitHub").first()

# Create source instance
source = create_source(source_model)

# Fetch feedback from last 7 days
since = datetime.utcnow() - timedelta(days=7)
feedback_list = source.fetch_feedback(since=since)

# Insert into database
for feedback_data in feedback_list:
    feedback = Feedback(**feedback_data)
    session.add(feedback)

session.commit()
```

### Automated Sync

```python
from ingestion.sync import sync_all_sources

# Sync all active sources
results = sync_all_sources(session)

for source_name, count in results.items():
    print(f"✓ {source_name}: {count} new items")
```

---

## Advanced Configuration

### Multiple GitHub Repos

```python
sources = [
    Source(
        name="GitHub - Main Product",
        source_type="real",
        config={
            "token": "ghp_xxx",
            "repo_owner": "yourorg",
            "repo_name": "main-product",
            "labels": ["feedback"]
        }
    ),
    Source(
        name="GitHub - Public Roadmap",
        source_type="real",
        config={
            "token": "ghp_xxx",
            "repo_owner": "yourorg",
            "repo_name": "public-roadmap",
            "labels": ["community-request"]
        }
    )
]
```

### Multiple Discord Servers

```python
sources = [
    Source(
        name="Discord - Community",
        config={
            "bot_token": "xxx",
            "guild_id": "111111",
            "channel_ids": ["222222", "333333"]
        }
    ),
    Source(
        name="Discord - Premium Users",
        config={
            "bot_token": "xxx",
            "guild_id": "444444",
            "channel_ids": ["555555"]
        }
    )
]
```

### Multiple Subreddits

```python
sources = [
    Source(
        name="Reddit - Brand Subreddit",
        config={
            "client_id": "xxx",
            "client_secret": "xxx",
            "user_agent": "compass-bot/1.0",
            "subreddit": "yourproduct",
            "keywords": []  # All posts
        }
    ),
    Source(
        name="Reddit - Industry Monitoring",
        config={
            "client_id": "xxx",
            "client_secret": "xxx",
            "user_agent": "compass-bot/1.0",
            "subreddit": "SaaS",
            "keywords": ["feedback tool", "your product name"]
        }
    )
]
```

---

## Security Best Practices

### 1. Use Environment Variables

Never hardcode credentials:

```python
import os

config = {
    "token": os.getenv("GITHUB_TOKEN"),
    "repo_owner": os.getenv("GITHUB_REPO_OWNER"),
    "repo_name": os.getenv("GITHUB_REPO_NAME")
}
```

### 2. Use .env File (Development)

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_REPO_OWNER=yourorg
GITHUB_REPO_NAME=yourrepo

DISCORD_BOT_TOKEN=xxxxxxxxx
DISCORD_GUILD_ID=123456789
DISCORD_CHANNEL_IDS=111111,222222

REDDIT_CLIENT_ID=xxxxxxxxx
REDDIT_CLIENT_SECRET=xxxxxxxxx
REDDIT_SUBREDDIT=yourproduct
```

### 3. Use Secrets Manager (Production)

- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

### 4. Principle of Least Privilege

- GitHub: Read-only access, specific repos only
- Discord: Read Messages only, no admin permissions
- Reddit: Read-only access

### 5. Add to .gitignore

```gitignore
.env
config_local.py
*_credentials.json
```

---

## Troubleshooting

### GitHub: "Bad credentials" or 401

- Token expired or invalid
- Missing required scopes (repo, read:discussion)
- Token doesn't have access to the repository

**Fix:** Generate new token with correct scopes

### Discord: "Privileged intent provided is not enabled"

- Message Content Intent not enabled

**Fix:**
1. Go to Discord Developer Portal
2. Select your app → Bot
3. Enable "Message Content Intent"
4. Save changes

### Discord: Bot not fetching messages

- Bot not in server
- Bot lacks read permissions
- Wrong guild_id or channel_ids

**Fix:**
1. Check bot is in server
2. Verify IDs (enable Developer Mode)
3. Check bot role permissions

### Reddit: "invalid_grant" or 401

- Invalid client_id or client_secret
- App type not "script"
- User agent not set correctly

**Fix:**
1. Verify credentials from app settings
2. Ensure app type is "script"
3. Use format: "appname/version by u/username"

### General: Empty feedback list

- Check date filter (`since` parameter)
- Verify data exists in source
- Check label/keyword filters aren't too restrictive
- Run with `since=None` to test

---

## Performance Optimization

### Rate Limits

| Platform | Rate Limit | Recommendation |
|----------|------------|----------------|
| GitHub | 5,000 req/hour (authenticated) | Sync every 15-30 minutes |
| Discord | No strict limit | Sync every 5-10 minutes |
| Reddit | 60 req/minute | Sync every 15-30 minutes |

### Pagination

All sources handle pagination automatically:
- GitHub: Fetches all matching issues/discussions
- Discord: Fetches last 200 messages per channel
- Reddit: Respects `limit` config parameter

### Incremental Sync

Always use `since` parameter for incremental syncing:

```python
# Get last sync time
last_sync = source_model.last_synced_at

# Fetch only new feedback
feedback = source.fetch_feedback(since=last_sync)

# Update last sync time
source_model.last_synced_at = datetime.utcnow()
session.commit()
```

---

## Competitive Advantages

### Why These Integrations Matter

1. **GitHub Discussions** (HUGE!)
   - Few competitors connect to GitHub Discussions
   - Perfect for open-source projects and developer tools
   - Rich, structured feedback from technical users

2. **Discord Communities**
   - Gaming, crypto, Web3, developer communities live on Discord
   - Real-time feedback from engaged users
   - Reaction tracking shows what resonates

3. **Reddit Monitoring**
   - Brand monitoring across communities
   - Unfiltered user opinions
   - Upvotes indicate community priorities

4. **Multi-Platform View**
   - See feedback from GitHub, Discord, Reddit in one place
   - Cross-reference discussions
   - Identify patterns across communities

### Market Positioning

**Most feedback tools only connect to:**
- Email
- Support tickets (Zendesk, Intercom)
- Surveys

**Compass connects to:**
- ✅ All of the above
- ✅ GitHub Issues & Discussions
- ✅ Discord communities
- ✅ Reddit monitoring
- ✅ Slack (existing)

**This is your unfair advantage!**

---

## Next Steps

1. **Test Integrations**
   ```bash
   python test_new_sources.py all
   ```

2. **Configure Sources**
   - Copy `source_configs_example.py`
   - Update with your credentials
   - Test each source

3. **Add to Database**
   ```python
   from source_configs_example import insert_sources_to_db
   insert_sources_to_db(session)
   ```

4. **Set Up Automated Sync**
   - Create cron job or scheduled task
   - Run sync every 15-30 minutes
   - Monitor for errors

5. **Monitor & Iterate**
   - Check feedback quality
   - Adjust filters (labels, keywords)
   - Add more sources as needed

---

## Support

Questions? Issues? Suggestions?

- Check test script: `test_new_sources.py`
- Review examples: `source_configs_example.py`
- Read source code: `sources.py`

Happy feedback collecting! 🚀
