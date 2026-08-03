# Compass Integrations - Quick Reference Card

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install PyGithub discord.py praw

# 2. Test integrations (with example configs)
cd /home/wsl-user/compass/backend/ingestion
python test_new_sources.py all

# 3. Setup your sources
python setup_sources.py

# 4. Run first sync
python sync.py --dry-run  # Preview
python sync.py            # Real sync
```

---

## 📋 Common Commands

### Testing
```bash
python test_new_sources.py all        # Test all sources
python test_new_sources.py github     # Test GitHub only
python test_new_sources.py discord    # Test Discord only
python test_new_sources.py reddit     # Test Reddit only
```

### Setup & Management
```bash
python setup_sources.py              # Interactive menu
python setup_sources.py --list       # List all sources
python setup_sources.py --auto       # Quick test setup
python setup_sources.py --delete "GitHub"  # Delete source
```

### Syncing
```bash
python sync.py                       # Sync all active sources
python sync.py --source GitHub       # Sync specific source
python sync.py --full                # Full sync (ignore last sync time)
python sync.py --dry-run             # Preview without saving
python sync.py -s Discord --full     # Full sync for Discord
```

---

## ⚙️ Configuration Templates

### GitHub
```python
{
    "token": "ghp_xxxxxxxxxxxx",
    "repo_owner": "yourorg",
    "repo_name": "yourrepo",
    "labels": ["feedback", "feature-request"],
    "include_discussions": True,
    "include_prs": False
}
```

**Get token**: https://github.com/settings/tokens

### Discord
```python
{
    "bot_token": "YOUR_BOT_TOKEN",
    "guild_id": "123456789012345678",
    "channel_ids": ["987654321098765432"],
    "include_threads": True,
    "reaction_threshold": 3
}
```

**Setup bot**: https://discord.com/developers/applications
**CRITICAL**: Enable "Message Content Intent" in bot settings!

### Reddit
```python
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "compass-bot/1.0 by u/yourname",
    "subreddit": "yourproduct",
    "keywords": ["feedback", "feature"],
    "sort_by": "new",
    "limit": 100
}
```

**Create app**: https://www.reddit.com/prefs/apps (choose "script" type)

---

## 🔧 Troubleshooting

### Problem: "Module not found"
```bash
pip install PyGithub discord.py praw
```

### Problem: GitHub "Bad credentials"
- Token expired or invalid
- Missing scopes: need `repo` + `read:discussion`
- Generate new token: https://github.com/settings/tokens

### Problem: Discord "Privileged intent not enabled"
1. Go to Discord Developer Portal
2. Your App → Bot → Privileged Gateway Intents
3. Enable "Message Content Intent"
4. Save changes

### Problem: Reddit "invalid_grant"
- Verify client_id and client_secret
- Ensure app type is "script"
- Check user_agent format: "appname/1.0 by u/username"

### Problem: Empty feedback list
```bash
# Try full sync
python sync.py --full

# Try dry run to see what would be fetched
python sync.py --dry-run

# Check source configuration
python setup_sources.py --list
```

---

## 📅 Scheduling (Production)

### Linux/Mac (cron)
```bash
crontab -e

# Add line (sync every 15 minutes):
*/15 * * * * cd /path/to/compass/backend && python ingestion/sync.py >> /var/log/compass.log 2>&1
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 15 minutes
4. Action: `python C:\path\to\compass\backend\ingestion\sync.py`

### Linux (systemd)
```bash
# Create /etc/systemd/system/compass-sync.timer
# See INTEGRATION_GUIDE.md for full config

sudo systemctl enable compass-sync.timer
sudo systemctl start compass-sync.timer
sudo systemctl status compass-sync.timer
```

---

## 🔒 Security Checklist

- [ ] Never commit credentials to git
- [ ] Add `.env` to `.gitignore`
- [ ] Use environment variables for production
- [ ] GitHub: Read-only token, specific repos only
- [ ] Discord: Read Messages permission only
- [ ] Reddit: Script-type app (read-only)
- [ ] Rotate tokens periodically
- [ ] Use secrets manager in production (AWS/Azure/GCP)

---

## 📊 Rate Limits

| Platform | Limit | Recommended Sync |
|----------|-------|------------------|
| GitHub | 5,000 req/hour | Every 15-30 min |
| Discord | No strict limit | Every 5-10 min |
| Reddit | 60 req/min | Every 15-30 min |

---

## 🎯 What You Get

### Data Per Source

**GitHub**:
- Issues (filtered by labels)
- Issue comments
- Discussions (GraphQL)
- Discussion comments
- PR comments (optional)

**Discord**:
- Channel messages
- Thread messages
- Reactions (engagement)
- High-engagement flagging

**Reddit**:
- Posts (filtered by flair/keywords)
- Top 20 comments per post
- Upvotes (engagement)
- Awards

### Standard Fields
Every feedback item includes:
- `text` - Feedback content
- `title` - Post/issue title
- `customer_name` - Username
- `submitted_at` - Timestamp
- `source_metadata` - Platform-specific data (URLs, IDs, reactions, etc.)

---

## 📖 Documentation Files

- `README.md` - Module overview and commands
- `INTEGRATION_GUIDE.md` - Complete setup guide (4,700+ words)
- `IMPLEMENTATION_SUMMARY.md` - Technical details and features
- `QUICK_REFERENCE.md` - This file
- `source_configs_example.py` - Full config examples

---

## 💡 Pro Tips

### GitHub
- Enable Discussions in repo settings
- Use labels like "feedback", "feature-request", "enhancement"
- Monitor public roadmap repos
- Create separate sources for different repos

### Discord
- Monitor specific feedback channels
- Use reaction_threshold to surface popular messages
- Enable threads for organized discussions
- Bot must stay in server

### Reddit
- Monitor your product's subreddit
- Use keyword filtering to reduce noise
- High upvotes = high priority
- Try monitoring industry subreddits (r/SaaS, r/startups)

---

## 🚨 Quick Help

**Dependencies not installing?**
```bash
pip install --upgrade pip
pip install PyGithub discord.py praw
```

**Database errors?**
```bash
# Check database exists
ls -lh compass.db

# Recreate tables
python -c "from models import Base, get_connection_string; from sqlalchemy import create_engine; engine = create_engine(get_connection_string()); Base.metadata.create_all(engine)"
```

**Import errors?**
```bash
# Make sure you're in the right directory
cd /home/wsl-user/compass/backend/ingestion
python sync.py
```

---

## 🎓 Learning Resources

1. **Start here**: `README.md`
2. **Setup guide**: `INTEGRATION_GUIDE.md`
3. **Examples**: `source_configs_example.py`
4. **Test first**: `test_new_sources.py`
5. **Dive deep**: `IMPLEMENTATION_SUMMARY.md`

---

## 🆘 Still Stuck?

1. Check logs for error messages
2. Run with `--dry-run` to see what would happen
3. Test source individually: `python test_new_sources.py github`
4. Verify configuration: `python setup_sources.py --list`
5. Check API credentials are valid
6. Read `INTEGRATION_GUIDE.md` troubleshooting section

---

## ✅ Success Checklist

Day 1:
- [ ] Install dependencies
- [ ] Test integrations
- [ ] Configure sources
- [ ] Run first sync

Week 1:
- [ ] Schedule automated sync
- [ ] Monitor feedback quality
- [ ] Adjust filters if needed
- [ ] Add more sources

Month 1:
- [ ] Analyze feedback patterns
- [ ] Integrate with NLP clustering
- [ ] Build multi-source dashboards
- [ ] Refine configurations

---

**Need more help?** See `INTEGRATION_GUIDE.md` for comprehensive documentation.

**Found a bug?** Check `IMPLEMENTATION_SUMMARY.md` for technical details.

**Want examples?** See `source_configs_example.py` for complete configs.

---

Made with ❤️ for Compass Feedback Intelligence Platform
