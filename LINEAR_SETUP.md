# Linear OAuth Integration Setup Guide

This guide walks you through setting up the Linear OAuth integration for Compass.

## Overview

The Linear integration allows you to:
- **Import issues as feedback** - Sync Linear issues into Compass for analysis
- **Sync issue comments** - Import issue discussions as customer feedback
- **Two-way sync** - Push Compass roadmap items back to Linear as issues
- **Automatic clustering** - AI-powered grouping of feedback from Linear
- **Priority mapping** - Linear priorities map to Compass priority scores

## Prerequisites

- A Linear account with admin access
- Compass backend running on `http://localhost:8000` (or your domain)
- Linear workspace where you want to create the OAuth app

## Step 1: Create Linear OAuth App

1. Go to **Linear Settings** → **API** → **OAuth applications**
   - Or visit: https://linear.app/settings/api/applications

2. Click **"Create new OAuth application"**

3. Fill in the application details:
   - **Name**: `Compass Feedback Intelligence`
   - **Description**: `Customer feedback intelligence platform`
   - **Callback URLs**: Add the following URLs:
     ```
     http://localhost:8000/api/auth/linear/callback
     http://localhost:5173/integrations?linear_connected=true
     ```
     - First URL: Backend OAuth handler
     - Second URL: Frontend redirect after successful auth

   - **Scopes**: Select these permissions:
     - ✅ **read** - View issues, comments, and teams
     - ✅ **write** - Create and update issues from roadmap

4. Click **"Create application"**

5. **Save your credentials** - You'll see:
   - **Client ID** - Public identifier (looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
   - **Client Secret** - Private key (keep this secret!)

## Step 2: Configure Environment Variables

Add these to your `.env` file in the Compass backend directory:

```bash
# Linear OAuth Configuration
LINEAR_CLIENT_ID=your_client_id_here
LINEAR_CLIENT_SECRET=your_client_secret_here
LINEAR_REDIRECT_URI=http://localhost:8000/api/auth/linear/callback
```

**For production deployment**, update the redirect URI to your domain:
```bash
LINEAR_REDIRECT_URI=https://your-domain.com/api/auth/linear/callback
```

## Step 3: Restart Compass Backend

Restart the backend to load the new environment variables:

```bash
# Stop the backend (Ctrl+C)
# Then restart:
cd /home/wsl-user/compass
./start.sh
```

Or if running manually:
```bash
cd backend
uvicorn main:app --reload
```

## Step 4: Connect Linear in Compass UI

1. Open Compass frontend: http://localhost:5173

2. Navigate to **Collect** tab

3. Find the **Linear Connector** card

4. Click **"Connect with Linear"**

5. A popup will open with Linear's OAuth authorization page

6. Review the permissions and click **"Authorize"**

7. You'll be redirected back to Compass with a success message

8. The Linear connector will now show:
   - ✅ Connected status
   - Your Linear user info
   - List of accessible teams
   - Number of teams

## Step 5: Sync Issues

1. **Select a team** (optional):
   - Use the dropdown to filter by specific team
   - Or leave blank to sync from all teams

2. Click **"Sync Issues"**

3. Compass will import:
   - Issue titles and descriptions
   - Issue comments
   - Labels and priorities
   - Creator and assignee info
   - State (Todo, In Progress, Done, etc.)

4. Check the **Feedback** tab to see imported issues

5. Go to **Insights** tab to see AI-clustered topics

## API Endpoints

The Linear integration adds these endpoints:

### OAuth Flow
```
GET  /api/auth/linear
     → Returns: { auth_url, state }
     → Start OAuth flow (redirect user to auth_url)

GET  /api/auth/linear/callback?code=xxx&state=xxx
     → Handles OAuth callback
     → Exchanges code for access token
     → Stores token in database
```

### Connector Operations
```
POST /api/connectors/linear/sync
     Body: { team_id?: string, limit?: number }
     → Sync issues from Linear to Compass

GET  /api/connectors/linear/status
     → Returns connection status, user info, teams

GET  /api/connectors/linear/teams
     → List all teams accessible to user
```

## Data Sync Details

### What Gets Synced

**From Linear → Compass:**
- Issue ID and identifier (e.g., `ENG-123`)
- Title and description
- State (Todo, In Progress, Done, Canceled)
- Priority (None, Low, Medium, High, Urgent)
- Labels
- Creator and assignee names
- Team info
- Created and updated timestamps
- URL to Linear issue

**Stored in Compass:**
- Issue becomes a Feedback item
- Description → Feedback text
- Title includes Linear identifier: `[ENG-123] Feature title`
- Creator → Customer name
- All metadata stored in `source_metadata` JSON field

### Sync Behavior

- **New issues**: Created as new Feedback items
- **Existing issues**: Updated with latest data
- **Deduplication**: Uses Linear issue ID to prevent duplicates
- **Comments**: Each comment becomes a separate Feedback item
- **Incremental sync**: Only new/updated issues since last sync

## Two-Way Sync (Coming Soon)

Push Compass roadmap items back to Linear:
```
POST /api/integrations/linear/create-issue
     Body: { cluster_id: 123, team_id: "xxx", priority: 2 }
     → Creates Linear issue from Compass cluster

POST /api/integrations/linear/link-issue
     Body: { issue_id: "xxx", roadmap_item_id: 123 }
     → Links existing Linear issue to roadmap item
```

## Troubleshooting

### OAuth popup blocked
**Problem**: Browser blocks the OAuth popup

**Solution**:
- Allow popups for localhost:5173
- Or manually visit the OAuth URL in a new tab

### "Invalid redirect URI" error
**Problem**: Linear OAuth app has wrong callback URL

**Solution**:
1. Go to Linear Settings → API → OAuth applications
2. Edit your app
3. Add exact callback URL: `http://localhost:8000/api/auth/linear/callback`
4. Save changes

### "Access token not found" error
**Problem**: Token not stored in database

**Solution**:
1. Disconnect Linear in Compass UI
2. Reconnect and authorize again
3. Check backend logs for errors during OAuth callback

### No issues syncing
**Problem**: Sync completes but no issues appear

**Solution**:
1. Check if you have any issues in Linear
2. Verify you selected the correct team
3. Try syncing with "All Teams" (leave dropdown blank)
4. Check backend logs: `tail -f backend/logs/app.log`

### "Permission denied" error
**Problem**: Linear OAuth app missing required scopes

**Solution**:
1. Go to Linear Settings → API → OAuth applications
2. Edit your app
3. Ensure both **read** and **write** scopes are selected
4. Save and reconnect in Compass

## Security Notes

- **Client Secret**: Keep this secret! Never commit to git
- **Token Storage**: Access tokens stored encrypted in database
- **Token Refresh**: Linear tokens don't expire (but can be revoked)
- **Revoke Access**: In Linear Settings → API → Authorized Applications
- **Audit Log**: Check Linear audit log for API activity

## Testing

### Test OAuth Flow
```bash
# 1. Get OAuth URL
curl http://localhost:8000/api/auth/linear

# 2. Visit auth_url in browser
# 3. Authorize app
# 4. Check database for stored token
```

### Test Issue Sync
```bash
# Check status
curl http://localhost:8000/api/connectors/linear/status

# Sync issues
curl -X POST http://localhost:8000/api/connectors/linear/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'

# List teams
curl http://localhost:8000/api/connectors/linear/teams
```

## GraphQL API

Linear uses GraphQL. You can test queries in Linear's API explorer:
https://linear.app/your-workspace/settings/api

Example query:
```graphql
query {
  viewer {
    id
    name
    email
  }
  teams {
    nodes {
      id
      name
      key
    }
  }
}
```

## Rate Limits

Linear API limits:
- **1000 requests per hour** per user
- **100 queries per minute** per user
- Compass caches team data to minimize API calls

## Support

- **Linear API Docs**: https://developers.linear.app/docs/graphql
- **OAuth Guide**: https://developers.linear.app/docs/oauth
- **GraphQL Schema**: https://studio.apollographql.com/public/Linear-API/schema/reference

---

**Next Steps:**
1. Set up environment variables
2. Connect Linear in UI
3. Sync your first issues
4. View clustered feedback in Insights tab
5. Generate prioritized roadmap

🎉 **You're ready to use Linear with Compass!**
