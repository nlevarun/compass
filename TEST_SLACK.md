# Test Slack Connector (10 minutes)

Follow this guide to test the Slack connector with real data from your workspace.

## Prerequisites

- Your own Slack workspace (free tier works!)
- Workspace admin access to create apps
- 10 minutes

## Test Steps

### 1. Setup Slack App (5 minutes)

Follow [SLACK_SETUP.md](./SLACK_SETUP.md) to:
- Create a Slack app
- Get your bot token (xoxb-...)
- Get your channel ID (C...)

**What you'll have**:
- Bot token: `xoxb-1234567890-1234567890-abcdefghij...`
- Channel ID: `C01AB23CD45`

### 2. Start Compass (1 minute)

#### Backend:
```bash
cd compass/backend
source venv/bin/activate
python main.py
```

Should see:
```
🚀 Starting Compass API...
✓ Compass API ready!
✓ WebSocket support enabled at /ws
```

#### Frontend (new terminal):
```bash
cd compass/frontend
npm run dev
```

Open: http://localhost:5173

### 3. Connect Slack (1 minute)

1. Open Compass at http://localhost:5173
2. Find the Slack Connector component (integrate it into your app)
3. Or test directly via API:

```bash
# Test connection
curl -X POST http://localhost:8000/api/connectors/slack/test \
  -H "Content-Type: application/json" \
  -d '{"token": "xoxb-YOUR-TOKEN", "channel_id": "C01AB23CD45"}'

# Should return: {"success": true, "channels": [...]}
```

4. Connect via UI:
   - Paste your bot token
   - Paste your channel ID
   - Click "Connect Slack"
   - Should see: ✓ Connected to Slack

### 4. Post Test Messages (1 minute)

Go to your Slack channel and post these test messages:

```
We need better analytics for our dashboard
```

```
Feature request: export data to CSV
```

```
Bug: mobile app crashes on iOS when uploading images
```

```
Love the new design! The UI is so much cleaner now 🎉
```

### 5. Sync Messages (1 minute)

1. Go back to Compass
2. Click **"Sync Now"** button
3. Wait 5 seconds
4. Should see alert: "Synced 4 new messages from Slack!"

### 6. Verify Data (2 minutes)

#### In UI:
1. Go to **"Feedback"** tab
2. You should see all 4 messages
3. Check that each message shows:
   - The text content
   - Source: "Slack"
   - Timestamp
   - (Optional) Sentiment score if NLP is running

#### Via API:
```bash
curl http://localhost:8000/api/feedback | jq
```

Should see your Slack messages in the response.

### 7. Test More Features (Optional)

#### A. Check Slack Status
```bash
curl http://localhost:8000/api/connectors/slack/status | jq
```

Should show:
```json
{
  "connected": true,
  "channel_id": "C01AB23CD45",
  "last_synced": "2026-08-04T10:30:00",
  "feedback_count": 4
}
```

#### B. Browse Channels
```bash
curl http://localhost:8000/api/connectors/slack/channels | jq
```

Should list all channels your bot can see.

#### C. Sync Again (should get 0 new)
1. Click "Sync Now" again
2. Should see: "Synced 0 new messages from Slack"
3. This proves duplicate detection works!

#### D. Post New Message
1. Go to Slack
2. Post: "Another feature request: dark mode"
3. Sync in Compass
4. Should see: "Synced 1 new message from Slack"

### 8. Test Clustering (Optional)

If you have NLP enabled:

1. Go to **"Insights"** tab
2. Click **"Run Clustering"**
3. Wait for it to complete
4. Should see clusters like:
   - "Feature Requests" (analytics, export, dark mode)
   - "Bug Reports" (iOS crash)
   - "Positive Feedback" (love the design)

### 9. Test Roadmap (Optional)

1. Go to **"Roadmap"** tab
2. Click **"Generate Roadmap"**
3. Should see prioritized features based on:
   - Number of requests
   - Sentiment
   - (If you added revenue data) Customer revenue

## Success Criteria

- ✅ Slack shows as "Connected"
- ✅ Messages appear in Compass after sync
- ✅ Can see message text and author
- ✅ No duplicate messages on second sync
- ✅ New messages sync correctly
- ✅ Sentiment analysis works (if NLP enabled)

## Common Issues

### Issue: "Invalid token"
**Solution**: Make sure you:
- Copied the full token including `xoxb-` prefix
- No extra spaces or line breaks
- Installed app to workspace in Slack

### Issue: "Channel not found"
**Solution**:
- Invite bot to channel: `/invite @Compass Feedback`
- Make sure Channel ID starts with `C`
- Try browsing channels instead of manual entry

### Issue: No messages appearing
**Solution**:
- Check messages were posted AFTER connecting
- Click "Sync Now" button
- Check browser console for errors
- Verify bot has `channels:history` scope

### Issue: Messages sync but don't show in UI
**Solution**:
- Refresh the page
- Check the Feedback tab specifically
- Look in browser dev tools Network tab for API errors
- Check backend logs for errors

## Performance Check

With 100 messages:
- Sync should take < 5 seconds
- No errors in console
- All messages appear in UI

With 1000+ messages:
- First sync may take 10-30 seconds
- Use pagination in UI to view all
- Clustering may take longer

## Next Steps After Testing

1. **Connect Multiple Channels**: Test with 2-3 different channels
2. **Add Revenue Data**: Add customer_revenue to test prioritization
3. **Set Up Auto-Sync**: Schedule sync every 30 minutes (coming soon)
4. **Try Other Connectors**: Test email, CSV import, etc.
5. **Share with Team**: Invite team to test feedback workflow

## Debugging Commands

```bash
# Check if Slack source exists
curl http://localhost:8000/api/sources | jq '.[] | select(.name=="Slack")'

# Get all feedback from Slack
curl "http://localhost:8000/api/feedback?source=Slack" | jq

# Check database directly (SQLite)
cd compass/backend
sqlite3 compass.db "SELECT COUNT(*) FROM feedback WHERE source_id = (SELECT id FROM sources WHERE name='Slack');"

# View recent feedback
sqlite3 compass.db "SELECT text, customer_name, submitted_at FROM feedback ORDER BY submitted_at DESC LIMIT 5;"
```

## Cleanup (Optional)

To reset and test again:

```bash
# Delete all Slack feedback
curl -X DELETE http://localhost:8000/api/feedback?source=Slack

# Or reset entire database
cd compass/backend
./reset_db.sh
```

---

**Total time**: 10 minutes
**Difficulty**: Easy
**Result**: Working Slack integration with real data!

Found a bug? Create an issue with:
- Steps to reproduce
- Expected vs actual behavior
- Console errors
- Backend logs
