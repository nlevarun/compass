# Slack OAuth Setup Guide

This guide will help you set up Slack OAuth integration for Compass in under 5 minutes.

## Quick Start

### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it **"Compass"** and select your workspace
4. Click **"Create App"**

### 2. Configure OAuth Scopes

1. In your app settings, go to **"OAuth & Permissions"** (left sidebar)
2. Scroll down to **"Scopes"** → **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add these 6 scopes:
   - `channels:read` - View basic channel info
   - `channels:history` - View messages in public channels
   - `groups:read` - View basic info about private channels
   - `groups:history` - View messages in private channels
   - `users:read` - View people in the workspace
   - `users:read.email` - View email addresses of people

### 3. Add Redirect URL

1. Still in **"OAuth & Permissions"**
2. Scroll up to **"Redirect URLs"**
3. Click **"Add New Redirect URL"**
4. Enter: `http://localhost:8000/api/auth/slack/callback`
5. Click **"Add"** then **"Save URLs"**

For production, add your production URL:
```
https://your-domain.com/api/auth/slack/callback
```

### 4. Get Your Credentials

1. Go to **"Basic Information"** (left sidebar)
2. Scroll down to **"App Credentials"**
3. Copy your **"Client ID"** (looks like: `1234567890.1234567890`)
4. Copy your **"Client Secret"** (click "Show" first)

### 5. Configure Compass

Create a `.env` file in the `compass` directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
SLACK_CLIENT_ID=1234567890.1234567890
SLACK_CLIENT_SECRET=your_client_secret_here
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
```

### 6. Restart the Backend

```bash
cd backend
python main_simple.py
```

### 7. Connect Your Workspace

1. Open Compass in your browser: http://localhost:5173
2. Go to the **"Sources"** or **"Slack"** tab
3. Click **"Connect Slack Workspace"**
4. Authorize the app in the popup
5. Done! You're connected!

## How to Use

### Sync Messages

1. After connecting, click **"Select Channel to Sync"**
2. Choose a channel (e.g., `#customer-feedback`)
3. Click **"Sync"**
4. Messages will appear in the Feedback tab

### Best Practices

- **Invite the bot to channels**: After installing, invite `@Compass` to channels you want to sync
- **Choose the right channels**: Focus on channels where customers give feedback
- **Sync regularly**: Set up automatic syncing or sync manually after important discussions
- **Use clustering**: After syncing, run clustering to group similar feedback

### Channel Recommendations

Good channels to sync:
- `#customer-feedback` - Direct customer input
- `#feature-requests` - Product ideas
- `#support` - Support tickets and issues
- `#sales` - Customer pain points from sales calls

Avoid syncing:
- `#general` - Too noisy
- `#random` - Off-topic
- Internal dev/eng channels - Not customer-facing

## Troubleshooting

### "OAuth not configured" error

Make sure:
1. `.env` file exists in the `compass` directory
2. `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET` are set correctly
3. You restarted the backend after adding the environment variables

### "Popup blocked" error

Allow popups for `localhost:5173` in your browser settings.

### "Invalid redirect_uri" error

Make sure the redirect URI in your `.env` file **exactly matches** the one in Slack app settings (including protocol: `http://` not `https://` for localhost).

### No channels showing up

After installing the app:
1. Go to Slack
2. Open a channel you want to sync
3. Type `/invite @Compass`
4. The bot needs to be a member to read messages

### "Missing scope" error

Go back to OAuth & Permissions in your Slack app settings and verify all 6 scopes are added. If you add new scopes, you need to **reinstall** the app to your workspace.

## Security Notes

- **Never commit `.env`** to version control (it's in `.gitignore`)
- Client Secret is sensitive - treat it like a password
- Access tokens are stored securely in the database
- Tokens can be revoked anytime from Slack app settings

## Production Deployment

When deploying to production:

1. Update redirect URL in Slack app settings:
   ```
   https://your-domain.com/api/auth/slack/callback
   ```

2. Update `.env` on your server:
   ```bash
   SLACK_REDIRECT_URI=https://your-domain.com/api/auth/slack/callback
   ```

3. Use environment variables (not `.env` file) on your hosting platform:
   - Heroku: `heroku config:set SLACK_CLIENT_ID=...`
   - AWS: Use Parameter Store or Secrets Manager
   - Vercel/Netlify: Add in dashboard environment variables

## API Endpoints

The OAuth integration adds these endpoints:

- `GET /api/auth/slack/connect` - Start OAuth flow
- `GET /api/auth/slack/callback` - OAuth callback (Slack redirects here)
- `GET /api/auth/slack/status` - Get connection status
- `POST /api/auth/slack/disconnect/{source_id}` - Disconnect workspace
- `GET /api/auth/slack/channels/{source_id}` - List channels
- `POST /api/auth/slack/sync/{source_id}` - Sync messages from channel

## What Gets Synced?

For each message:
- **Text content** - The message text
- **Author** - User's real name
- **Timestamp** - When it was posted
- **Channel** - Which channel it's from
- **Link** - Direct link back to Slack message

What doesn't get synced:
- Bot messages (filtered out)
- System messages (joins/leaves)
- File uploads (coming soon)
- Thread replies (coming soon)

## Multiple Workspaces

You can connect multiple Slack workspaces:
1. Click **"Connect Another Workspace"**
2. Authorize the app in the second workspace
3. Each workspace appears as a separate source

## Next Steps

After connecting Slack:

1. **Sync messages** from customer-facing channels
2. **Run clustering** to find common themes
3. **Generate roadmap** based on customer feedback
4. **Set up webhooks** for real-time sync (coming soon)

---

Need help? Check the [main README](README.md) or open an issue on GitHub.
