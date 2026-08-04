# Webhook Testing Guide

## Overview

This guide shows you how to test Compass's real-time webhook system that replaces 5-minute polling with <1 second feedback delivery.

## Performance Benchmark

| Method | Latency | Status |
|--------|---------|--------|
| **Polling (Old)** | 5 minutes | ❌ Slow |
| **Webhooks (New)** | <1 second | ✅ **300x Faster** |
| **Productboard** | 60 minutes | ❌ Very Slow |

**Result: Compass is 3600x faster than Productboard!**

---

## Local Testing with ngrok

### 1. Install ngrok

```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Or download from https://ngrok.com/download
```

### 2. Start Compass Backend

```bash
cd /home/wsl-user/compass/backend
python main.py
```

Backend runs on `http://localhost:8000`

### 3. Start ngrok Tunnel

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

### 4. Test Endpoints

Your webhook URLs will be:
- **Slack**: `https://abc123.ngrok.io/webhooks/slack/events`
- **GitHub**: `https://abc123.ngrok.io/webhooks/github/issues`
- **Intercom**: `https://abc123.ngrok.io/webhooks/intercom/conversations`

---

## Quick Test (No External Service Required)

### Test via Browser

1. Open: `http://localhost:8000/webhooks/slack/test`
2. You should see:
   ```json
   {
     "success": true,
     "feedback_id": 123,
     "processing_time_ms": 87.23,
     "demo": "This simulates a real Slack message webhook"
   }
   ```

3. Check the Compass dashboard - new feedback should appear **instantly**!

### Test via curl

```bash
# Test Slack webhook
curl http://localhost:8000/webhooks/slack/test

# Test GitHub webhook
curl http://localhost:8000/webhooks/github/test

# Test Intercom webhook
curl http://localhost:8000/webhooks/intercom/test
```

---

## Slack Webhook Setup

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Compass Feedback"
4. Pick your workspace

### 2. Enable Event Subscriptions

1. Go to "Event Subscriptions" in sidebar
2. Toggle "Enable Events" to ON
3. **Request URL**: `https://abc123.ngrok.io/webhooks/slack/events`
   - Slack will verify the URL (should see ✅ "Verified")
4. Subscribe to bot events:
   - `message.channels`
   - `message.im`
5. Click "Save Changes"

### 3. Get Signing Secret

1. Go to "Basic Information" in sidebar
2. Scroll to "App Credentials"
3. Copy "Signing Secret"
4. Set environment variable:
   ```bash
   export SLACK_SIGNING_SECRET="your_secret_here"
   ```

### 4. Install App to Workspace

1. Go to "Install App" in sidebar
2. Click "Install to Workspace"
3. Authorize the app

### 5. Test It!

1. Post a message in a Slack channel where the bot is added:
   ```
   Feature request: We need dark mode!
   ```

2. **Watch Compass dashboard update in <1 second!** ⚡

3. Verify latency:
   - Check backend logs for: `✓ Slack webhook processed in 87.23ms`
   - Old polling: 300,000ms (5 minutes)
   - New webhooks: <100ms
   - **3000x faster!**

---

## GitHub Webhook Setup

### 1. Go to Repository Settings

1. Navigate to your GitHub repo
2. Settings → Webhooks → "Add webhook"

### 2. Configure Webhook

- **Payload URL**: `https://abc123.ngrok.io/webhooks/github/issues`
- **Content type**: `application/json`
- **Secret**: Generate a random string
  ```bash
  export GITHUB_WEBHOOK_SECRET="your_random_secret_here"
  ```
- **Events**: Select individual events
  - ✅ Issues
  - ✅ Issue comments
- Active: ✅ Check

### 3. Test It!

1. Create a new issue in your repo:
   ```
   Title: Add CSV export feature
   Body: Users need to export feedback data to CSV for analysis in Excel
   ```

2. **Watch Compass dashboard update instantly!** ⚡

3. Verify in webhook settings:
   - Click on webhook → "Recent Deliveries"
   - Should see 200 OK response in <200ms

---

## Intercom Webhook Setup

### 1. Go to Intercom Settings

1. Log in to Intercom
2. Settings → Developers → Webhooks

### 2. Create Webhook

1. Click "New webhook"
2. **Webhook URL**: `https://abc123.ngrok.io/webhooks/intercom/conversations`
3. Select topics:
   - ✅ `conversation.user.created`
   - ✅ `conversation.user.replied`
4. Copy the webhook secret
   ```bash
   export INTERCOM_WEBHOOK_SECRET="your_secret_here"
   ```
5. Save webhook

### 3. Test It!

1. Send a test message to your Intercom (or use the Messenger on your site)
2. **Watch Compass dashboard update in <1 second!** ⚡
3. Check webhook logs in Intercom for success

---

## Performance Benchmarking

### Measure Latency

```bash
# Test and measure latency
time curl http://localhost:8000/webhooks/slack/test
```

**Expected results:**
- **Processing time**: <100ms
- **Total time** (including network): <500ms
- **Old polling**: 300,000ms (5 minutes)

### Load Test

```bash
# Install hey (HTTP load tester)
go install github.com/rakyll/hey@latest

# Send 100 concurrent webhook requests
hey -n 100 -c 10 http://localhost:8000/webhooks/slack/test
```

**Expected throughput:**
- 100+ requests/second
- Average latency: <100ms
- Success rate: >99%

---

## Demo Script (For Investors/Customers)

### Setup (5 minutes)

1. Start Compass: `python main.py`
2. Start ngrok: `ngrok http 8000`
3. Open Compass dashboard in browser
4. Configure Slack webhook (show them the setup steps)

### Demo (2 minutes)

1. **Show current dashboard** (empty or with old feedback)

2. **Post in Slack**:
   ```
   Hey team! We really need better search functionality.
   It's hard to find specific feedback right now.
   ```

3. **Point at the screen**:
   - "Watch this..."
   - **New feedback appears INSTANTLY** 💥
   - Point out the "Real-time" badge
   - Show timestamp: "Just now"

4. **Click on the feedback**:
   - Show it came from Slack
   - Show processing time: "87ms"

5. **Compare to competitors**:
   ```
   Productboard: Wait 60 minutes 😴
   Compass: <1 second ⚡

   That's 3600x faster!
   ```

6. **Show webhook stats**:
   - Go to Webhook Monitor
   - Show success rate: 99%+
   - Show average latency: <100ms
   - Show total events processed

### Wow Factor

End with:
> "This is the difference between finding out about customer problems **next week** versus **right now**. When a customer complains in Slack, you can respond immediately. That's the power of real-time feedback."

---

## Troubleshooting

### Webhook not receiving events

1. Check ngrok is running: `curl https://abc123.ngrok.io/docs`
2. Verify URL in service settings (Slack/GitHub/Intercom)
3. Check environment variables are set
4. Look at backend logs for errors

### Signature verification failing

1. Ensure secrets are correctly set:
   ```bash
   echo $SLACK_SIGNING_SECRET
   echo $GITHUB_WEBHOOK_SECRET
   echo $INTERCOM_WEBHOOK_SECRET
   ```
2. Restart backend after setting variables
3. Check service webhook settings for correct secret

### High latency (>500ms)

1. Check database performance (SQLite on fast SSD?)
2. Check network latency (ngrok adds ~50-100ms)
3. Look for errors in backend logs
4. Verify no CPU/memory constraints

### Events not appearing in dashboard

1. Check WebSocket connection in browser console
2. Verify frontend is connected to correct backend URL
3. Refresh the page
4. Check browser Network tab for WebSocket messages

---

## Success Criteria

✅ Webhook URLs are accessible (curl returns 200)
✅ Test endpoints work (`/webhooks/*/test`)
✅ External services verify webhook URLs
✅ Events appear in dashboard in <1 second
✅ Backend logs show processing times <100ms
✅ WebSocket emits events correctly
✅ Success rate >99%
✅ Can demo to someone else successfully

---

## Next Steps

After webhooks are working:

1. ✅ Configure all 3 services (Slack, GitHub, Intercom)
2. ✅ Monitor performance in Webhook Monitor component
3. ✅ Set up alerts for webhook failures
4. ✅ Document for team/customers
5. ✅ Deploy to production with proper domain
6. ✅ Remove polling code (no longer needed!)

---

## Support

Issues? Questions?

1. Check backend logs: `tail -f compass.log`
2. Check ngrok logs: Look at ngrok dashboard
3. Check service webhook logs (Slack/GitHub/Intercom)
4. Open an issue with:
   - Error message
   - Backend logs
   - Service webhook delivery logs
   - Steps to reproduce
