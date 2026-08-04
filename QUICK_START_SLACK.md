# Slack OAuth - Quick Start (5 Minutes)

Get Slack connected in 5 minutes with zero manual token copying.

## Step 1: Create Slack App (2 minutes)

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. Name: **"Compass"**, select your workspace → **Create App**

## Step 2: Add Permissions (1 minute)

1. Click **"OAuth & Permissions"** (sidebar)
2. Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"** and add:
   - `channels:read`
   - `channels:history`
   - `groups:read`
   - `groups:history`
   - `users:read`
   - `users:read.email`

## Step 3: Add Redirect URL (30 seconds)

1. Still in **"OAuth & Permissions"**
2. Under **"Redirect URLs"**, click **"Add New Redirect URL"**
3. Enter: `http://localhost:8000/api/auth/slack/callback`
4. Click **"Add"** → **"Save URLs"**

## Step 4: Get Credentials (30 seconds)

1. Click **"Basic Information"** (sidebar)
2. Under **"App Credentials"**:
   - Copy **Client ID** (like: `1234567890.1234567890`)
   - Copy **Client Secret** (click "Show" first)

## Step 5: Configure Compass (1 minute)

```bash
cd /home/wsl-user/compass
cp .env.example .env
```

Edit `.env`:
```bash
SLACK_CLIENT_ID=paste_your_client_id_here
SLACK_CLIENT_SECRET=paste_your_client_secret_here
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
```

## Step 6: Test & Run

Test configuration:
```bash
cd backend
python test_slack_oauth.py
```

If tests pass ✅, start the server:
```bash
python main_simple.py
```

## Step 7: Connect! (30 seconds)

1. Open http://localhost:5173
2. Go to **"Sources"** tab
3. Click **"Connect Slack Workspace"**
4. Authorize in popup → Done!

## Now What?

1. Click **"Select Channel to Sync"**
2. Choose a channel (e.g., `#customer-feedback`)
3. Click **"Sync"**
4. View messages in the **Feedback** tab
5. Run **Clustering** to group similar feedback
6. Generate **Roadmap** based on customer needs

---

**Need help?** See [SLACK_OAUTH_SETUP.md](SLACK_OAUTH_SETUP.md) for troubleshooting.
