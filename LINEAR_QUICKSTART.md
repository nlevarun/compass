# Linear Integration - Quick Start

Get Linear integrated with Compass in 5 minutes.

## Prerequisites

- Linear account with admin access
- Compass running locally or deployed

## Step 1: Create Linear OAuth App (2 minutes)

1. Go to https://linear.app/settings/api/applications
2. Click **"Create new OAuth application"**
3. Fill in:
   - **Name**: Compass Feedback Intelligence
   - **Callback URLs**:
     ```
     http://localhost:8000/api/auth/linear/callback
     http://localhost:5173/integrations?linear_connected=true
     ```
   - **Scopes**: Check `read` and `write`
4. Click **"Create application"**
5. Copy your **Client ID** and **Client Secret**

## Step 2: Configure Environment (1 minute)

Add to your `.env` file:

```bash
LINEAR_CLIENT_ID=your_client_id_here
LINEAR_CLIENT_SECRET=your_client_secret_here
LINEAR_REDIRECT_URI=http://localhost:8000/api/auth/linear/callback
```

## Step 3: Restart Compass (1 minute)

```bash
# Stop backend (Ctrl+C)
# Then restart:
cd /home/wsl-user/compass
./start.sh
```

Or manually:
```bash
cd backend
uvicorn main:app --reload
```

## Step 4: Connect in UI (1 minute)

1. Open http://localhost:5173
2. Click **"Collect"** tab
3. Scroll to **Linear Connector**
4. Click **"Connect with Linear"**
5. Authorize in popup
6. Done! You're connected

## Step 5: Sync Issues (30 seconds)

1. In Linear Connector card:
2. Select a team (optional)
3. Click **"Sync Issues"**
4. Wait for confirmation
5. Go to **Feedback** tab to see Linear issues

## Done! 🎉

Your Linear issues are now in Compass:
- View in **Feedback** tab
- See AI clusters in **Insights** tab
- Generate roadmap in **Roadmap** tab

## What's Next?

- **Automatic sync**: Set up cron job to sync daily
- **Comments**: Enable comment syncing in settings
- **Two-way sync**: Push roadmap items back to Linear
- **Webhooks**: Real-time updates (coming soon)

## Troubleshooting

**OAuth popup blocked?**
- Allow popups for localhost:5173

**"Invalid redirect URI"?**
- Check callback URL matches exactly in Linear app

**No issues syncing?**
- Verify you have issues in Linear
- Try "All Teams" option
- Check Linear permissions (need read access)

## Documentation

- **Full Setup Guide**: LINEAR_SETUP.md
- **Testing Guide**: TEST_LINEAR.md
- **Integration Details**: LINEAR_INTEGRATION_README.md

---

**Time to first sync: 5 minutes** ⚡
