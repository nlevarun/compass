# Webhook System Deployment Checklist

Use this checklist to deploy the webhook system step by step.

## ✅ Phase 1: Local Setup (30 minutes)

### Prerequisites
- [ ] Backend is installed and running
- [ ] Frontend is installed and running
- [ ] Database exists (SQLite or PostgreSQL)
- [ ] Python environment active

### Database Migration
- [ ] Run `python migrate_webhook_tables.py`
- [ ] Verify tables created: `webhook_receiver_configs`, `webhook_events`
- [ ] Check for errors in output

### Basic Testing
- [ ] Test Slack endpoint: `curl http://localhost:8000/webhooks/slack/test`
- [ ] Test GitHub endpoint: `curl http://localhost:8000/webhooks/github/test`
- [ ] Test Intercom endpoint: `curl http://localhost:8000/webhooks/intercom/test`
- [ ] All return `"success": true`

### Integration Testing
- [ ] Run `./test_webhook_system.sh`
- [ ] All tests pass
- [ ] Average latency <500ms

### Real-Time Testing
- [ ] Run `python example_webhook_realtime.py`
- [ ] WebSocket connects successfully
- [ ] Trigger test webhook: `curl http://localhost:8000/webhooks/slack/test`
- [ ] Event appears instantly in terminal
- [ ] Shows processing time <100ms

### Frontend Integration
- [ ] Navigate to WebhookSetup component (or add to navigation)
- [ ] All service cards display correctly
- [ ] Test buttons work for all services
- [ ] Webhook URLs are correct
- [ ] Copy buttons work
- [ ] Navigate to WebhookMonitor component
- [ ] Stats display correctly
- [ ] Recent events show up

**✅ Phase 1 Complete: System is working locally!**

---

## ✅ Phase 2: External Service Setup (1 hour)

### Slack Setup

#### App Creation
- [ ] Go to https://api.slack.com/apps
- [ ] Create new app (or select existing)
- [ ] Name: "Compass Feedback Bot"
- [ ] Select workspace

#### Event Subscriptions
- [ ] Enable Event Subscriptions
- [ ] Set Request URL (ngrok for local, real domain for prod)
- [ ] URL verifies successfully (green checkmark)
- [ ] Subscribe to `message.channels`
- [ ] Subscribe to `message.im` (optional)
- [ ] Save changes

#### Signing Secret
- [ ] Go to Basic Information
- [ ] Copy Signing Secret
- [ ] Set environment variable: `export SLACK_SIGNING_SECRET="..."`
- [ ] Restart backend

#### Installation
- [ ] Install app to workspace
- [ ] Add bot to channels you want to monitor
- [ ] Bot appears in channel member list

#### Testing
- [ ] Post test message in channel
- [ ] Message appears in Compass within 1 second
- [ ] Backend logs show: `✓ Slack webhook processed in XXms`
- [ ] Feedback has correct source_metadata

### GitHub Setup

#### Webhook Creation
- [ ] Go to GitHub repo → Settings → Webhooks
- [ ] Click "Add webhook"
- [ ] Set Payload URL
- [ ] Content type: `application/json`

#### Secret Generation
- [ ] Generate secret: `openssl rand -hex 32`
- [ ] Copy secret to webhook settings
- [ ] Set environment variable: `export GITHUB_WEBHOOK_SECRET="..."`
- [ ] Restart backend

#### Event Selection
- [ ] Select "Let me select individual events"
- [ ] Check: Issues
- [ ] Check: Issue comments
- [ ] Uncheck: Push (unless you want it)
- [ ] Ensure "Active" is checked

#### Testing
- [ ] Create test issue
- [ ] Issue appears in Compass within 1 second
- [ ] Backend logs show: `✓ GitHub webhook processed in XXms`
- [ ] Check GitHub webhook delivery log (should show 200 OK)

### Intercom Setup

#### Webhook Creation
- [ ] Log in to Intercom
- [ ] Settings → Developers → Webhooks
- [ ] Click "New webhook"

#### Configuration
- [ ] Set Webhook URL
- [ ] Select topics:
  - [ ] `conversation.user.created`
  - [ ] `conversation.user.replied`

#### Secret
- [ ] Copy webhook secret from Intercom
- [ ] Set environment variable: `export INTERCOM_WEBHOOK_SECRET="..."`
- [ ] Restart backend

#### Testing
- [ ] Send test message via Intercom Messenger
- [ ] Conversation appears in Compass within 1 second
- [ ] Backend logs show: `✓ Intercom webhook processed in XXms`
- [ ] Check Intercom webhook logs (should show success)

**✅ Phase 2 Complete: All external services connected!**

---

## ✅ Phase 3: Monitoring & Verification (30 minutes)

### Performance Verification
- [ ] Test latency for each service (<1 second end-to-end)
- [ ] Check backend logs for processing times (<100ms)
- [ ] Verify WebSocket events are emitted
- [ ] Confirm dashboard updates in real-time

### Success Rate
- [ ] Send 10 test events to each service
- [ ] Verify success rate >95%
- [ ] Check WebhookMonitor for statistics
- [ ] Review webhook_events table for any errors

### Error Handling
- [ ] Test with invalid signature (should return 401)
- [ ] Test with malformed payload (should return 400)
- [ ] Test with network error (should log and continue)
- [ ] Verify errors are logged properly

### WebSocket Testing
- [ ] Open dashboard in multiple browser tabs
- [ ] Trigger webhook
- [ ] Verify all tabs update simultaneously
- [ ] Check WebSocket connection in browser console
- [ ] Verify heartbeat messages every 30s

### Database Verification
- [ ] Query webhook_events table: `SELECT * FROM webhook_events ORDER BY received_at DESC LIMIT 10`
- [ ] Verify events are logged
- [ ] Check processing_time_ms is reasonable
- [ ] Verify success=true for most events

**✅ Phase 3 Complete: System is monitored and verified!**

---

## ✅ Phase 4: Production Deployment (1-2 hours)

### Pre-Deployment

#### Environment Variables
- [ ] Set all secrets on production server:
  - [ ] `SLACK_SIGNING_SECRET`
  - [ ] `GITHUB_WEBHOOK_SECRET`
  - [ ] `INTERCOM_WEBHOOK_SECRET`
  - [ ] `APP_URL` (your production domain)
- [ ] Verify with `echo $SLACK_SIGNING_SECRET` (should not be empty)

#### Database
- [ ] Run migration on production: `python migrate_webhook_tables.py`
- [ ] Verify tables created
- [ ] If using PostgreSQL, ensure connection string is correct

#### SSL/HTTPS
- [ ] Ensure production domain has SSL certificate
- [ ] Webhook URLs must be HTTPS (not HTTP)
- [ ] Test HTTPS access: `curl https://your-domain.com/docs`

### Deployment

#### Backend
- [ ] Deploy backend code to production
- [ ] Verify backend starts successfully
- [ ] Check logs for startup errors
- [ ] Test API endpoints: `curl https://your-domain.com/webhooks/slack/test`

#### Frontend
- [ ] Deploy frontend code
- [ ] Update API_URL to production backend
- [ ] Verify WebhookSetup component loads
- [ ] Verify WebhookMonitor component loads

### External Service Updates

#### Slack
- [ ] Update Request URL to production domain
- [ ] Wait for Slack to reverify URL (should show green checkmark)
- [ ] Test with real message

#### GitHub
- [ ] Update Payload URL to production domain
- [ ] GitHub automatically pings new URL
- [ ] Check Recent Deliveries for success
- [ ] Test with real issue

#### Intercom
- [ ] Update Webhook URL to production domain
- [ ] Intercom tests URL automatically
- [ ] Check logs for success
- [ ] Test with real conversation

### Post-Deployment Verification
- [ ] Send test events to all services
- [ ] Verify all appear in dashboard
- [ ] Check production logs for errors
- [ ] Monitor for 30 minutes
- [ ] Verify success rate >99%

**✅ Phase 4 Complete: Production deployment successful!**

---

## ✅ Phase 5: Documentation & Training (1 hour)

### Internal Documentation
- [ ] Add webhook URLs to team wiki
- [ ] Document environment variables
- [ ] Share troubleshooting guide
- [ ] Document monitoring process

### Team Training
- [ ] Train support team on real-time notifications
- [ ] Train PMs on instant feedback visibility
- [ ] Train engineering on webhook monitoring
- [ ] Share demo script with sales team

### Customer-Facing
- [ ] Add "Real-time updates" to feature list
- [ ] Update product demos to showcase speed
- [ ] Add performance benchmarks to marketing
- [ ] Create customer setup guides (if offering self-service)

### Monitoring Setup
- [ ] Set up alerts for webhook failures
- [ ] Add webhook metrics to dashboards
- [ ] Configure error notifications
- [ ] Schedule weekly performance reviews

**✅ Phase 5 Complete: Team is trained and documented!**

---

## ✅ Phase 6: Optimization & Scale (Ongoing)

### Performance Optimization
- [ ] Benchmark under load (100+ concurrent webhooks)
- [ ] Optimize database queries if needed
- [ ] Add caching if beneficial
- [ ] Consider PostgreSQL if using SQLite at scale

### Feature Enhancements
- [ ] Add more webhook sources (Zendesk, Linear, etc.)
- [ ] Build webhook analytics dashboard
- [ ] Add webhook transformation rules
- [ ] Create webhook marketplace

### Monitoring & Alerts
- [ ] Set up Sentry/error tracking
- [ ] Configure uptime monitoring
- [ ] Add performance alerting
- [ ] Set up weekly reports

### Scaling (if needed)
- [ ] Add load balancer for multiple backend instances
- [ ] Use managed PostgreSQL
- [ ] Add Redis for caching/queuing
- [ ] Consider multi-region deployment

**✅ Phase 6 Complete: System is optimized and scaling!**

---

## 🚨 Troubleshooting Checklist

### Webhook Not Receiving Events
- [ ] Check backend is running
- [ ] Verify webhook URL is correct in service settings
- [ ] Check SSL certificate (must be valid for HTTPS)
- [ ] Verify no firewall blocking
- [ ] Check service webhook delivery logs
- [ ] Test with test endpoint first

### Signature Verification Failing
- [ ] Verify environment variables are set
- [ ] Check secrets match service settings
- [ ] Restart backend after setting variables
- [ ] Check backend logs for exact error
- [ ] Test with `echo $SECRET_NAME` to verify

### Events Not Appearing in Dashboard
- [ ] Check WebSocket connection in browser console
- [ ] Verify backend event emission (check logs)
- [ ] Refresh browser page
- [ ] Check database for feedback entries
- [ ] Verify frontend API_URL is correct

### High Latency (>1 second)
- [ ] Check database performance
- [ ] Check network latency (ping backend)
- [ ] Review backend logs for slow queries
- [ ] Check server resources (CPU, memory)
- [ ] Consider moving to PostgreSQL

### Low Success Rate (<95%)
- [ ] Review webhook_events table for errors
- [ ] Check backend logs for exceptions
- [ ] Verify database isn't full/locked
- [ ] Check network stability
- [ ] Review error patterns

---

## 📊 Success Metrics

After full deployment, you should see:

### Performance
- ✅ End-to-end latency: <1 second
- ✅ Backend processing time: <100ms
- ✅ Success rate: >99%
- ✅ Throughput: 100+ webhooks/sec

### User Experience
- ✅ Feedback appears instantly in dashboard
- ✅ Real-time notifications work
- ✅ No more 5-minute delays
- ✅ Users say "wow" when they see it

### Business Impact
- ✅ Faster response to customer issues
- ✅ Better product decisions (real-time data)
- ✅ Competitive advantage vs polling-based tools
- ✅ Lower server costs (90% less load)

---

## 🎉 Completion Checklist

- [ ] Phase 1: Local Setup ✅
- [ ] Phase 2: External Services ✅
- [ ] Phase 3: Monitoring ✅
- [ ] Phase 4: Production Deployment ✅
- [ ] Phase 5: Documentation & Training ✅
- [ ] Phase 6: Optimization ✅

### Final Verification
- [ ] All services connected and working
- [ ] Success rate >99%
- [ ] Latency <1 second
- [ ] Team trained
- [ ] Monitoring active
- [ ] Documentation complete

**🚀 Congratulations! Your webhook system is fully deployed!**

---

## 📝 Notes

### Common Issues Encountered:


### Performance Benchmarks:


### Team Feedback:


### Future Improvements:


---

**Deployed by:** _________________

**Date:** _________________

**Sign-off:** _________________

---

**Need help?** See [WEBHOOKS_INDEX.md](./WEBHOOKS_INDEX.md) for documentation.
