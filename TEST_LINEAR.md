# Testing Linear OAuth Integration

Quick guide to test the Linear integration in Compass.

## Prerequisites

1. **Set up Linear OAuth app** (see LINEAR_SETUP.md)
2. **Configure environment variables** in `.env`:
   ```bash
   LINEAR_CLIENT_ID=your_client_id
   LINEAR_CLIENT_SECRET=your_client_secret
   LINEAR_REDIRECT_URI=http://localhost:8000/api/auth/linear/callback
   ```
3. **Backend running** on http://localhost:8000
4. **Frontend running** on http://localhost:5173

## Test 1: Backend OAuth Endpoints

### 1.1 Get OAuth URL
```bash
curl http://localhost:8000/api/auth/linear
```

**Expected Response:**
```json
{
  "auth_url": "https://linear.app/oauth/authorize?client_id=...&redirect_uri=...&response_type=code&scope=read,write&state=...",
  "state": "random_token_here",
  "message": "Redirect user to auth_url to authorize Linear access"
}
```

### 1.2 Test OAuth Callback (Manual)
1. Visit the `auth_url` from step 1.1 in your browser
2. Authorize the app in Linear
3. You'll be redirected to: `http://localhost:8000/api/auth/linear/callback?code=...&state=...`
4. Check the response - should redirect to frontend with success

**Expected Response:**
```json
{
  "success": true,
  "message": "Linear connected successfully",
  "user": {
    "id": "...",
    "name": "Your Name",
    "email": "you@example.com"
  },
  "teams": [...],
  "redirect": "http://localhost:5173/integrations?linear_connected=true"
}
```

## Test 2: Connection Status

### 2.1 Check Connection Status
```bash
curl http://localhost:8000/api/connectors/linear/status
```

**Before connecting:**
```json
{
  "connected": false,
  "message": "Linear not configured"
}
```

**After connecting:**
```json
{
  "connected": true,
  "user": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "teams": [
    {
      "id": "team-123",
      "name": "Engineering",
      "key": "ENG"
    }
  ],
  "team_count": 1,
  "last_synced": null,
  "feedback_count": 0
}
```

## Test 3: List Teams

```bash
curl http://localhost:8000/api/connectors/linear/teams
```

**Expected Response:**
```json
{
  "teams": [
    {
      "id": "team-id-123",
      "name": "Engineering",
      "key": "ENG",
      "description": "Engineering team"
    },
    {
      "id": "team-id-456",
      "name": "Product",
      "key": "PROD",
      "description": null
    }
  ],
  "count": 2
}
```

## Test 4: Sync Issues

### 4.1 Sync from All Teams
```bash
curl -X POST http://localhost:8000/api/connectors/linear/sync \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10
  }'
```

### 4.2 Sync from Specific Team
```bash
curl -X POST http://localhost:8000/api/connectors/linear/sync \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "your-team-id-here",
    "limit": 50
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "synced": 10,
  "new": 8,
  "updated": 2,
  "team_id": null,
  "limit": 10
}
```

### 4.3 Verify Feedback Created
```bash
curl http://localhost:8000/api/feedback
```

Should now include feedback items with:
- `source`: "Linear"
- `title`: "[ENG-123] Issue title"
- `source_metadata`: Contains Linear issue data

## Test 5: Frontend Integration

### 5.1 Open Frontend
1. Go to http://localhost:5173
2. Click **"Collect"** tab
3. Scroll to **Linear Connector** card

### 5.2 Connect Flow
1. Click **"Connect with Linear"**
2. OAuth popup opens with Linear authorization
3. Click **"Authorize"** in Linear
4. Popup closes
5. Linear Connector shows:
   - ✅ Green "Connected to Linear" badge
   - Your user name and email
   - Team count
   - Synced issues count (0 initially)

### 5.3 Sync Issues
1. Select a team from dropdown (or leave blank for all)
2. Click **"Sync Issues"**
3. Wait for sync to complete
4. Alert shows: "Synced X new issues and updated Y existing issues from Linear!"
5. Stats update:
   - "Issues Synced" count increases
   - "Last Synced" shows current time

### 5.4 View Synced Feedback
1. Click **"Feedback"** tab
2. Should see Linear issues as feedback items
3. Each item shows:
   - Title with Linear identifier: `[ENG-123] Feature title`
   - Source: Linear
   - Customer: Issue creator name
   - Metadata: Linear issue URL, state, priority

### 5.5 View Clusters
1. Click **"Insights"** tab
2. Click **"Run Clustering"**
3. Should see clusters including Linear issues
4. AI groups similar issues together

## Test 6: Error Cases

### 6.1 Test Without Connection
```bash
# Try to sync without connecting
curl -X POST http://localhost:8000/api/connectors/linear/sync
```

**Expected Error:**
```json
{
  "detail": "Linear not connected. Connect first via OAuth at GET /api/auth/linear"
}
```

### 6.2 Test Invalid Team ID
```bash
curl -X POST http://localhost:8000/api/connectors/linear/sync \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "invalid-team-id"
  }'
```

Should return empty results (no issues for that team).

### 6.3 Test Without OAuth Credentials
1. Remove `LINEAR_CLIENT_ID` from `.env`
2. Restart backend
3. Try to get OAuth URL:
```bash
curl http://localhost:8000/api/auth/linear
```

Should return OAuth URL with empty client_id (will fail at Linear).

## Test 7: Database Verification

### 7.1 Check Source Created
```bash
# Connect to SQLite database
sqlite3 compass.db "SELECT * FROM sources WHERE name = 'Linear';"
```

Should show:
- `name`: "Linear"
- `source_type`: "real"
- `is_active`: 1
- `config`: JSON with `access_token`, `user`, `teams`

### 7.2 Check Feedback Created
```bash
sqlite3 compass.db "SELECT id, title, customer_name, source_metadata FROM feedback WHERE source_id = (SELECT id FROM sources WHERE name = 'Linear') LIMIT 3;"
```

Should show Linear issues with:
- Titles starting with `[ENG-123]` format
- Customer names from Linear users
- `source_metadata` JSON with Linear issue data

## Test 8: Real-Time Updates (WebSocket)

1. Open frontend with DevTools console
2. Connect to Linear
3. Sync issues
4. Watch console for WebSocket events:
   ```
   [WebSocket] feedback_synced event: {source: "Linear", count: 10, ...}
   ```

## Success Criteria

✅ **OAuth flow works**: Can authorize and receive access token
✅ **Status endpoint works**: Shows connected status and user info
✅ **Teams endpoint works**: Lists all accessible teams
✅ **Sync works**: Issues imported as feedback items
✅ **Deduplication works**: Re-syncing doesn't create duplicates
✅ **Frontend shows connection**: UI displays connected state
✅ **Frontend sync works**: Can trigger sync and see results
✅ **Feedback tab shows Linear issues**: Issues appear in feedback list
✅ **Clustering includes Linear data**: AI clusters Linear issues

## Common Issues

### "OAuth popup blocked"
**Fix**: Allow popups for localhost:5173 in browser settings

### "Invalid redirect URI"
**Fix**: Ensure callback URL in Linear OAuth app exactly matches:
```
http://localhost:8000/api/auth/linear/callback
```

### "No issues syncing"
**Fix**:
- Check if you have issues in Linear
- Try different team or "All Teams"
- Check Linear permissions (need read access to issues)

### "Token not found"
**Fix**: Reconnect Linear - the OAuth callback may have failed

## Performance Benchmarks

Expected performance:
- **OAuth flow**: < 2 seconds total
- **Sync 10 issues**: < 3 seconds
- **Sync 50 issues**: < 10 seconds
- **Sync 100 issues**: < 20 seconds

Linear API rate limits:
- 1000 requests/hour per user
- 100 queries/minute per user

## Next Steps After Testing

1. ✅ OAuth connection works
2. ✅ Issue sync works
3. ✅ Frontend integration works
4. 🔄 Add comment syncing (optional)
5. 🔄 Add two-way sync (push roadmap to Linear)
6. 🔄 Add webhook support (real-time updates)
7. 🔄 Add automatic sync scheduling

---

**Ready to test in production?** See LINEAR_SETUP.md for deployment guide.
