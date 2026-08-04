# Quick Start: Webhooks in 5 Minutes

Get Compass webhooks up and running in 5 minutes or less!

## Prerequisites

- Compass backend running
- Compass frontend running
- (Optional) ngrok for local testing with external services

## Step 1: Migrate Database (30 seconds)

```bash
cd /home/wsl-user/compass/backend
python migrate_webhook_tables.py
```

You should see:
```
✅ Successfully created 2 tables
🎉 Migration complete!
```

## Step 2: Test Locally (1 minute)

### Start backend (if not already running)
```bash
python main.py
```

### Test the webhooks
```bash
# Test Slack webhook
curl http://localhost:8000/webhooks/slack/test

# Test GitHub webhook
curl http://localhost:8000/webhooks/github/test

# Test Intercom webhook
curl http://localhost:8000/webhooks/intercom/test
```

Each should return:
```json
{
  "success": true,
  "feedback_id": 123,
  "processing_time_ms": 87.23
}
```

### See it in real-time!
```bash
# In another terminal, watch the WebSocket events
python example_webhook_realtime.py
```

Then trigger a webhook:
```bash
curl http://localhost:8000/webhooks/slack/test
```

You should see the event appear **instantly** in the WebSocket listener! ⚡

## Step 3: Setup External Service (3 minutes)

Choose one service to start with. Slack is easiest!

### Option A: Slack (Recommended for first test)

1. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 8000
   ```
   Copy the URL (e.g., `https://abc123.ngrok.io`)

2. **Go to Slack**:
   - Visit https://api.slack.com/apps
   - Create New App → From scratch
   - Name it "Compass Feedback"

3. **Enable Events**:
   - Go to "Event Subscriptions"
   - Toggle ON
   - Request URL: `https://abc123.ngrok.io/webhooks/slack/events`
   - Subscribe to: `message.channels`
   - Save

4. **Get Secret**:
   - Go to "Basic Information"
   - Copy "Signing Secret"
   - Run:
     ```bash
     export SLACK_SIGNING_SECRET="your_secret_here"
     ```
   - Restart backend: `python main.py`

5. **Install App**:
   - Go to "Install App"
   - Install to workspace
   - Add bot to a channel

6. **Test it!**:
   - Post in the channel: "Feature request: dark mode"
   - Check Compass dashboard → Should appear in <1 second! 🎉

### Option B: GitHub

1. **Start ngrok** (if not already running)
2. **Go to your GitHub repo** → Settings → Webhooks → Add webhook
3. **Configure**:
   - Payload URL: `https://abc123.ngrok.io/webhooks/github/issues`
   - Content type: `application/json`
   - Secret: Generate one with `openssl rand -hex 32`
   - Events: Issues, Issue comments
4. **Set secret**:
   ```bash
   export GITHUB_WEBHOOK_SECRET="your_secret"
   ```
   Restart backend
5. **Test**: Create an issue → Should appear in Compass instantly!

### Option C: Intercom

1. **Start ngrok** (if not already running)
2. **Go to Intercom** → Settings → Developers → Webhooks
3. **New webhook**:
   - URL: `https://abc123.ngrok.io/webhooks/intercom/conversations`
   - Topics: `conversation.user.created`, `conversation.user.replied`
   - Copy the secret
4. **Set secret**:
   ```bash
   export INTERCOM_WEBHOOK_SECRET="your_secret"
   ```
   Restart backend
5. **Test**: Send a message → Should appear in Compass instantly!

## Step 4: View in Dashboard (1 minute)

1. **Open Compass frontend** (usually `http://localhost:5173`)

2. **Navigate to Feedback Inbox** → You should see your test feedback!

3. **Check Webhook Setup page** (if added to navigation):
   - Shows webhook URLs
   - Shows performance stats
   - Test buttons for each service

4. **Check Webhook Monitor** (if added to navigation):
   - Real-time statistics
   - Success rates
   - Recent events

## Verification Checklist

✅ Backend running on port 8000
✅ Test endpoints return success
✅ Database migrated (webhook tables added)
✅ At least one external service configured
✅ Test message appears in dashboard in <1 second
✅ Backend logs show processing time <100ms
✅ WebSocket events working (if tested)

## What's Next?

### Configure All Services

Set up Slack, GitHub, AND Intercom for complete coverage:
- See [WEBHOOKS_README.md](./WEBHOOKS_README.md) for full setup guides

### Deploy to Production

1. Replace ngrok with real domain
2. Update webhook URLs in all services
3. Set environment variables on production server
4. Monitor performance in Webhook Monitor

### Integrate into Your Workflow

1. Connect webhook events to your team's Slack
2. Auto-notify PMs when high-value feedback arrives
3. Auto-create Linear/Jira issues from feedback clusters
4. Close the loop: Notify customers when features ship

### Showcase the Speed

Use the demo script to impress stakeholders:
- See [DEMO_WEBHOOKS.md](./DEMO_WEBHOOKS.md)

## Troubleshooting

### "Module not found" errors

```bash
cd /home/wsl-user/compass/backend
pip install -r requirements.txt
```

### Webhook URL verification fails

- Check ngrok is running: `curl https://abc123.ngrok.io/docs`
- Check backend is running: `curl http://localhost:8000/docs`
- Restart backend after setting environment variables

### Events not appearing

1. Check backend logs for errors
2. Verify WebSocket connection in browser console
3. Refresh the page
4. Try the test endpoint first: `/webhooks/slack/test`

### High latency (>500ms)

- Check database location (SSD recommended)
- Check ngrok isn't adding too much latency
- Check backend has enough resources

## Success! 🎉

If you can:
1. ✅ Trigger a test webhook
2. ✅ See it appear in the dashboard in <1 second
3. ✅ Backend logs show <100ms processing time

**You're done!** You now have real-time webhooks that are **300x faster** than polling!

## Performance Comparison

Your setup:
- **Latency**: <1 second (probably <500ms)
- **Old polling**: 5 minutes (300 seconds)
- **Improvement**: 300x-600x faster!

vs. Competitors:
- **Productboard**: 60 minutes
- **Compass**: <1 second
- **You're 3600x faster!** ⚡

## Need Help?

- 📖 Full documentation: [WEBHOOKS_README.md](./WEBHOOKS_README.md)
- 🧪 Testing guide: [WEBHOOK_TESTING.md](./WEBHOOK_TESTING.md)
- 🎬 Demo script: [DEMO_WEBHOOKS.md](./DEMO_WEBHOOKS.md)
- 🐛 Check backend logs: `tail -f compass.log`
- 💬 Check service webhook logs (Slack/GitHub/Intercom admin panels)

---

**Congratulations!** You're now receiving feedback in real-time. 🚀
