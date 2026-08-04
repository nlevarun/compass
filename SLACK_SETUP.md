# Connect Slack to Compass (5 minutes)

Get real customer feedback flowing from Slack into Compass in just 5 minutes.

## Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. **App Name**: "Compass Feedback" (or your choice)
4. **Pick a workspace**: Select your Slack workspace
5. Click **"Create App"**

## Step 2: Add Bot Permissions

Your bot needs permission to read channel messages.

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll down to **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add these three scopes:
   - `channels:history` - Read messages from public channels
   - `channels:read` - View basic channel info
   - `chat:write` - (Optional) Allow bot to post messages
4. Scroll back to top and click **"Install to Workspace"**
5. Review permissions and click **"Allow"**

## Step 3: Get Your Bot Token

1. After installation, you'll see **"Bot User OAuth Token"**
2. It starts with `xoxb-` and looks like: `xoxb-YOUR-TOKEN-HERE`
3. Click **"Copy"** to copy the token
4. **Keep this secure!** Don't commit it to git.

## Step 4: Get Channel ID

You need the ID of the channel you want to monitor.

### Method 1: From Slack Desktop
1. Open Slack and go to the channel you want to monitor
2. Right-click on the channel name (or click the channel name)
3. Select **"View channel details"** (or **"Open channel details"**)
4. Scroll to the bottom of the details panel
5. You'll see **"Channel ID"** - it looks like `C01AB23CD45`
6. Click to copy it

### Method 2: From Channel URL
1. Open the channel in Slack
2. Look at the URL in your browser: `https://app.slack.com/client/T01XX/C01YY/...`
3. The `C01YY` part is your Channel ID

### Method 3: Use Compass (Easiest!)
1. Open Compass: http://localhost:5173
2. Go to the **"Collect"** tab (or wherever you added the Slack connector)
3. Paste your bot token
4. Click **"Browse Channels"**
5. Select your channel from the list!

## Step 5: Connect in Compass

1. Open Compass: http://localhost:5173
2. Navigate to the integration/connector section
3. Find **"Slack Connector"**
4. Paste your **Bot Token** (xoxb-...)
5. Paste your **Channel ID** (C01...)
6. Click **"Connect Slack"**
7. You should see: ✓ Connected to Slack

## Step 6: Test It!

1. Go to your Slack channel
2. Post a test message: "Feature request: dark mode for mobile app"
3. Go back to Compass
4. Click **"Sync Now"**
5. Wait a few seconds
6. Go to the **Feedback** tab
7. You should see your message! 🎉

## Troubleshooting

### "Invalid token" error
- Make sure you copied the full token starting with `xoxb-`
- Don't include any extra spaces
- Make sure you installed the app to your workspace

### "Channel not found" error
- Verify the Channel ID is correct (starts with C)
- Make sure the bot has been added to the channel:
  - Go to the channel in Slack
  - Type `/invite @Compass Feedback` (or your bot name)
  - The bot should join the channel

### No messages appearing
- Make sure you clicked "Sync Now" after posting
- Check that the messages were posted AFTER you connected (or use "Sync All" if available)
- Verify the bot has `channels:history` permission

### Bot not in channel list when browsing
- You need to manually invite the bot to private channels
- Public channels show automatically, but you may need to join them
- Use `/invite @Compass Feedback` in any channel

## What's Next?

After connecting Slack:

1. **Automatic Sync**: Set up automatic syncing every 30 minutes (coming soon)
2. **Multiple Channels**: Connect multiple channels to track different products/teams
3. **Sentiment Analysis**: Compass automatically analyzes message sentiment
4. **Clustering**: Run NLP clustering to group similar feedback
5. **Roadmap**: Generate prioritized roadmap from Slack feedback

## Security Notes

- Your bot token is stored securely in the Compass database
- The bot can only read channels it's invited to
- The bot cannot read DMs or private channels unless explicitly invited
- You can revoke access anytime at https://api.slack.com/apps

## Need Help?

- **Slack API Docs**: https://api.slack.com/start
- **Bot Token Scopes**: https://api.slack.com/scopes
- **Test your bot**: Use the "Test Connection" button in Compass

---

**Estimated time**: 5 minutes
**Difficulty**: Easy
**Required**: Slack workspace admin access
