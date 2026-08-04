# Slack Connector - Quick Start (5 Minutes)

Get Slack messages flowing into Compass in 5 minutes.

## Step 1: Install (1 minute)

```bash
cd /home/wsl-user/compass/backend
source venv/bin/activate
pip install slack-sdk
python main.py
```

Keep this terminal running.

## Step 2: Start Frontend (30 seconds)

New terminal:
```bash
cd /home/wsl-user/compass/frontend
npm run dev
```

Open: http://localhost:5173

## Step 3: Create Slack App (2 minutes)

1. Go to: https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name: "Compass Feedback", pick your workspace
4. Go to **"OAuth & Permissions"**
5. Under **"Bot Token Scopes"**, add: `channels:history` and `channels:read`
6. Click **"Install to Workspace"** → **"Allow"**
7. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

## Step 4: Get Channel ID (30 seconds)

**Method 1 (Easiest)**: Use Compass
- Continue to Step 5, paste token, click "Browse Channels"

**Method 2**: From Slack
- Right-click channel → View details → Copy Channel ID at bottom

## Step 5: Connect in Compass (1 minute)

1. In Compass, click **"Collect"** tab
2. You'll see **"Slack Connector"**
3. Paste your bot token (xoxb-...)
4. Either:
   - Click **"Browse Channels"** and select one, OR
   - Paste channel ID manually (C01...)
5. Click **"Connect Slack"**
6. Should see: ✓ Connected to Slack

## Step 6: Import Messages (30 seconds)

1. Click **"Sync Now"** button
2. Wait 2-5 seconds
3. You'll see: "Synced X messages from Slack"
4. Go to **"Feedback"** tab
5. See your Slack messages! 🎉

## Test It

1. Go to your Slack channel
2. Post: "We need better analytics"
3. Back in Compass, click **"Sync Now"**
4. Go to **"Feedback"** tab
5. Your new message appears!

## Troubleshooting

### "Invalid token"
- Copy the full token including `xoxb-` prefix
- Make sure app is installed to workspace

### "Channel not found"
- Invite bot to channel: `/invite @Compass Feedback`
- Try browsing channels instead

### No messages appearing
- Check you clicked "Sync Now"
- Refresh the page
- Check browser console for errors

## What's Next?

- **Run Clustering**: Go to "Insights" → "Run Clustering"
- **Generate Roadmap**: Go to "Roadmap" → "Generate Roadmap"
- **Read Full Docs**: See [SLACK_CONNECTOR_INDEX.md](./SLACK_CONNECTOR_INDEX.md)

## Full Documentation

- **[INSTALL_SLACK_CONNECTOR.md](./INSTALL_SLACK_CONNECTOR.md)** - Detailed installation
- **[SLACK_SETUP.md](./SLACK_SETUP.md)** - Complete Slack app setup
- **[TEST_SLACK.md](./TEST_SLACK.md)** - Full testing guide
- **[SLACK_CONNECTOR_README.md](./SLACK_CONNECTOR_README.md)** - Technical docs
- **[SLACK_CONNECTOR_INDEX.md](./SLACK_CONNECTOR_INDEX.md)** - All documentation

---

**Total time**: 5 minutes
**Result**: Real Slack messages in Compass!
