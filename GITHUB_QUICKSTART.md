# GitHub OAuth Integration - Quick Start

Get GitHub issues into Compass in 5 minutes.

## What You Get

- Issues → Feedback items
- Comments → Additional feedback
- Reactions → Vote counts
- OAuth → Easy connection (no manual tokens!)

## Setup (5 minutes)

### 1. Create GitHub OAuth App (2 min)

```bash
# Go to: https://github.com/settings/developers
# Click: "New OAuth App"
# Set:
#   - App name: Compass Feedback
#   - Homepage: http://localhost:3000
#   - Callback: http://localhost:3000/oauth/github/callback
# Save Client ID & Secret
```

### 2. Connect in Compass (1 min)

```bash
# 1. Start Compass
cd compass
./start.sh

# 2. Open browser: http://localhost:3000
# 3. Go to "Collect" tab
# 4. Find "GitHub Connector"
# 5. Enter Client ID & Secret
# 6. Click "Connect with GitHub"
# 7. Authorize the app
```

### 3. Select Repos & Sync (2 min)

```bash
# 1. Choose repositories to monitor
# 2. (Optional) Add label filters: bug, feature-request, feedback
# 3. Click "Configure Repositories"
# 4. Click "Sync Now"
# 5. Done! Check the "Feedback" tab
```

## What Gets Imported

```
GitHub Issue #42: "Add dark mode"
  ├─ Title → Feedback title
  ├─ Description → Feedback text
  ├─ Labels → Metadata
  ├─ 👍 ❤️ reactions → Vote count
  └─ Comments → Additional feedback items
```

## Example Use Cases

### Customer Feedback Repo

Create a dedicated GitHub repo for customer feedback:

```bash
# 1. Create repo: "customer-feedback"
# 2. Add labels: feature-request, bug, improvement
# 3. Share with customers
# 4. Connect to Compass
# 5. Issues auto-sync to roadmap
```

### Open Source Projects

Track community feedback from your OSS projects:

```bash
# 1. Connect your public repos
# 2. Filter by label: "feature-request"
# 3. Most upvoted issues → Priority features
# 4. Compass clusters similar requests
# 5. Data-driven roadmap decisions
```

### Internal Tools

Track feedback from your internal tools:

```bash
# 1. Connect internal repos
# 2. No label filters (get everything)
# 3. Team reports issues directly
# 4. Auto-analyzed and prioritized
# 5. Build what matters most
```

## API Quick Reference

```bash
# Start OAuth
GET /api/auth/github?client_id=YOUR_ID

# Handle callback
POST /api/auth/github/callback
{
  "client_id": "...",
  "client_secret": "...",
  "code": "..."
}

# Get repos
GET /api/connectors/github/repositories

# Configure
POST /api/connectors/github/configure
{
  "repository_full_names": ["owner/repo"],
  "labels": ["feature-request"]
}

# Sync
POST /api/connectors/github/sync
```

## Troubleshooting

**Q: "Failed to exchange code for token"**
- Check Client ID & Secret are correct
- Ensure callback URL matches OAuth app settings

**Q: "No repositories showing"**
- Grant OAuth app access to your repos
- Check permissions in GitHub → Settings → Applications

**Q: "Sync not working"**
- Verify at least one repository is configured
- Check `/api/connectors/github/status` for errors

## Next Steps

- Set up hourly auto-sync (coming soon)
- Configure GitHub webhooks for real-time updates
- Use reactions as vote weights in prioritization
- Link high-priority feedback to Linear/Jira

## Files Created

```
backend/
  connectors/
    github.py                    # GitHub OAuth connector
  main.py                        # Added GitHub endpoints
  test_github_connector.py       # Test suite

frontend/
  src/
    components/
      GitHubConnector.jsx        # React component

GITHUB_OAUTH_SETUP.md            # Full documentation
GITHUB_QUICKSTART.md             # This file
```

## Testing

```bash
# Backend test
cd compass/backend
python test_github_connector.py YOUR_GITHUB_TOKEN

# Frontend test
# 1. Open http://localhost:3000
# 2. Go to "Collect" tab
# 3. Test OAuth flow
```

## Production Deployment

Update callback URLs for production:

```python
# Backend: main.py
redirect_uri = "https://yourapp.com/oauth/github/callback"

# Frontend: GitHubConnector.jsx
# OAuth callback URL in GitHub app settings:
# https://yourapp.com/oauth/github/callback
```

## Support

- Full docs: `GITHUB_OAUTH_SETUP.md`
- GitHub API: https://docs.github.com/en/rest
- OAuth guide: https://docs.github.com/en/apps/oauth-apps

Done! 🚀
