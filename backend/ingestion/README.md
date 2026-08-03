# Compass Feedback Ingestion Module

This module handles fetching feedback from multiple sources including GitHub, Discord, Reddit, and Slack.

## Quick Start

### 1. Install Dependencies

```bash
# Install all integrations
pip install -r ../requirements-minimal.txt

# Or install selectively
pip install PyGithub discord.py praw slack-sdk
```

### 2. Test Integrations

```bash
# Test all sources
python test_new_sources.py all

# Test individual sources
python test_new_sources.py github
python test_new_sources.py discord
python test_new_sources.py reddit
```

### 3. Setup Sources

```bash
# Interactive setup
python setup_sources.py

# Auto-setup with examples (for testing)
python setup_sources.py --auto

# List existing sources
python setup_sources.py --list
```

### 4. Sync Feedback

```bash
# Sync all active sources
python sync.py

# Sync specific source
python sync.py --source GitHub

# Dry run (preview without saving)
python sync.py --dry-run
```

## Available Sources

### Real Integrations (4)

1. **GitHub** - Issues, Discussions, PR comments
2. **Discord** - Channel messages, threads, reactions
3. **Reddit** - Posts, comments, upvotes
4. **Slack** - Channel messages (existing)

### Mock Sources (7)

For demo/testing purposes:
- Email
- Support Tickets
- Surveys
- App Reviews
- Sales Calls
- User Interviews
- Social Media

## File Structure

```
ingestion/
├── README.md                    # This file
├── INTEGRATION_GUIDE.md         # Comprehensive setup guide
├── sources.py                   # Source implementations
├── mock_generators.py           # Mock data generation
├── test_new_sources.py          # Test script
├── setup_sources.py             # Interactive setup
├── sync.py                      # Automated sync script
└── source_configs_example.py    # Configuration examples
```

## Key Files

### `sources.py`
Core source implementations:
- `FeedbackSource` - Base class
- `GitHubSource` - GitHub integration
- `DiscordSource` - Discord integration
- `RedditSource` - Reddit integration
- `SlackSource` - Slack integration
- Mock sources for demo data

### `sync.py`
Automated sync script:
- Syncs all active sources
- Handles incremental updates
- Prevents duplicates
- Updates last_synced_at timestamps

### `test_new_sources.py`
Testing utility:
- Tests each integration
- Validates configuration
- Shows sample output
- Displays statistics

### `setup_sources.py`
Database management:
- Interactive source setup
- List existing sources
- Delete sources
- Quick auto-setup for testing

### `source_configs_example.py`
Configuration examples:
- Complete config examples for each source
- Security best practices
- Environment variable templates
- Production deployment patterns

### `INTEGRATION_GUIDE.md`
Comprehensive documentation:
- Detailed setup instructions
- Configuration options
- Troubleshooting guide
- Performance optimization
- Security best practices

## Configuration Examples

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

### Reddit

```python
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "compass-bot/1.0 by u/yourname",
    "subreddit": "yourproduct",
    "keywords": ["feedback", "feature", "request"],
    "sort_by": "new",
    "limit": 100
}
```

## Common Commands

```bash
# Setup
python setup_sources.py                    # Interactive setup
python setup_sources.py --list             # List sources
python setup_sources.py --auto             # Quick test setup

# Testing
python test_new_sources.py all             # Test all sources
python test_new_sources.py github          # Test GitHub only

# Syncing
python sync.py                             # Sync all sources
python sync.py --source GitHub             # Sync GitHub only
python sync.py --full                      # Full sync (ignore last sync)
python sync.py --dry-run                   # Preview without saving

# Development
python sources.py                          # Test source creation
python mock_generators.py                  # Generate mock data
```

## Scheduling Automated Syncs

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line to sync every 15 minutes
*/15 * * * * cd /path/to/compass/backend && python ingestion/sync.py >> /var/log/compass-sync.log 2>&1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 15 minutes
4. Action: Start program
   - Program: `python`
   - Arguments: `C:\path\to\compass\backend\ingestion\sync.py`
   - Start in: `C:\path\to\compass\backend`

### Using systemd Timer (Linux)

Create `/etc/systemd/system/compass-sync.service`:

```ini
[Unit]
Description=Compass Feedback Sync
After=network.target

[Service]
Type=oneshot
User=compass
WorkingDirectory=/opt/compass/backend
ExecStart=/usr/bin/python3 ingestion/sync.py
```

Create `/etc/systemd/system/compass-sync.timer`:

```ini
[Unit]
Description=Compass Feedback Sync Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable compass-sync.timer
sudo systemctl start compass-sync.timer
```

## Troubleshooting

### "Module not found" errors

```bash
# Install missing dependencies
pip install PyGithub discord.py praw
```

### "Invalid configuration" errors

Check configuration in database:
```bash
python setup_sources.py --list
```

Update configuration or re-add source.

### Empty feedback list

- Check date filter (try `--full` sync)
- Verify data exists in source
- Check label/keyword filters
- Test with broader filters

### Rate limiting

- GitHub: 5,000 req/hour (use incremental sync)
- Discord: No strict limit
- Reddit: 60 req/minute (respect limit config)

See `INTEGRATION_GUIDE.md` for detailed troubleshooting.

## Development

### Adding a New Source

1. Create source class in `sources.py`:

```python
class NewSource(FeedbackSource):
    def validate_config(self) -> bool:
        # Validate required config fields
        return "api_key" in self.config

    def fetch_feedback(self, since: Optional[datetime] = None) -> List[Dict]:
        # Fetch and return feedback
        return []
```

2. Add to source factory:

```python
source_map = {
    # ...
    "NewSource": NewSource
}
```

3. Create test in `test_new_sources.py`

4. Add configuration example to `source_configs_example.py`

5. Document in `INTEGRATION_GUIDE.md`

### Running Tests

```bash
# Test individual source
python test_new_sources.py github

# Test all sources
python test_new_sources.py all

# Test sync (dry run)
python sync.py --dry-run
```

## Security

### Never Commit Credentials

Add to `.gitignore`:
```
.env
config_local.py
*_credentials.json
*.db
```

### Use Environment Variables

```python
import os

config = {
    "token": os.getenv("GITHUB_TOKEN"),
    "repo_owner": os.getenv("GITHUB_REPO_OWNER"),
    # ...
}
```

### Principle of Least Privilege

- GitHub: Read-only access
- Discord: Read Messages only
- Reddit: Read-only access

See `INTEGRATION_GUIDE.md` for complete security guidelines.

## Support

- **Documentation**: `INTEGRATION_GUIDE.md`
- **Examples**: `source_configs_example.py`
- **Testing**: `test_new_sources.py`

## License

Part of the Compass Feedback Intelligence Platform.
