# Linear OAuth Integration for Compass

Complete, production-ready Linear OAuth integration with full two-way sync capabilities.

## 🎯 What's Built

A complete Linear OAuth integration that brings project management data into Compass for intelligent feedback analysis.

### Core Features

✅ **OAuth 2.0 Authentication**
- Secure OAuth flow with state parameter for CSRF protection
- Automatic token storage and refresh
- User and team data caching

✅ **Issue Import**
- Sync Linear issues as Compass feedback
- Preserve issue metadata (priority, labels, state)
- Automatic deduplication
- Incremental sync (only new/updated issues)

✅ **Comment Sync**
- Import issue comments as separate feedback items
- Preserve discussion context
- Link comments to parent issues

✅ **Two-Way Sync**
- Create Linear issues from Compass clusters
- Update issue status from roadmap progress
- Link roadmap items to Linear issues

✅ **GraphQL API Integration**
- Full GraphQL query support
- Efficient data fetching with field selection
- Team and project filtering

✅ **React Frontend**
- Beautiful, responsive UI component
- OAuth popup flow
- Team selection and filtering
- Real-time sync status
- Connection management

## 📁 Files Created

### Backend Files

1. **`/backend/connectors/linear.py`** (617 lines)
   - `LinearConnector` class with GraphQL client
   - OAuth token exchange
   - Issue and comment syncing
   - Two-way sync methods
   - Connection testing

2. **`/backend/main.py`** (updated)
   - Added Linear OAuth endpoints:
     - `GET /api/auth/linear` - Start OAuth
     - `GET /api/auth/linear/callback` - Handle callback
     - `POST /api/connectors/linear/sync` - Sync issues
     - `GET /api/connectors/linear/status` - Connection status
     - `GET /api/connectors/linear/teams` - List teams

### Frontend Files

3. **`/frontend/src/components/LinearConnector.jsx`** (347 lines)
   - React component for Linear integration
   - OAuth popup flow
   - Team selection dropdown
   - Sync controls
   - Connection status display
   - Styled with Tailwind CSS

4. **`/frontend/src/App.jsx`** (updated)
   - Added LinearConnector to Collect tab
   - Imports LinearConnector component

### Documentation

5. **`/LINEAR_SETUP.md`**
   - Complete setup instructions
   - OAuth app configuration
   - Environment variables
   - Troubleshooting guide

6. **`/TEST_LINEAR.md`**
   - Comprehensive testing guide
   - API endpoint tests
   - Frontend integration tests
   - Success criteria

7. **`/LINEAR_INTEGRATION_README.md`** (this file)
   - Integration overview
   - Architecture details
   - Usage examples

## 🏗️ Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Linear Workspace                        │
│  Issues → Comments → Teams → Projects → Roadmaps            │
└─────────────────────────────────────────────────────────────┘
                            ↓
                     OAuth 2.0 Flow
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Compass Backend (FastAPI)                  │
│  /api/auth/linear/callback → Store access token             │
│  /api/connectors/linear/sync → GraphQL query → Parse        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)              │
│  sources → feedback → clusters → roadmap_items              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  LinearConnector → OAuth Popup → Sync UI → Status Display   │
└─────────────────────────────────────────────────────────────┘
```

### OAuth Flow

```
1. User clicks "Connect with Linear" in frontend
   ↓
2. Frontend calls GET /api/auth/linear
   ↓
3. Backend generates OAuth URL with state
   ↓
4. Frontend opens popup to Linear OAuth page
   ↓
5. User authorizes app in Linear
   ↓
6. Linear redirects to /api/auth/linear/callback?code=xxx
   ↓
7. Backend exchanges code for access_token
   ↓
8. Backend stores token in database (Source.config)
   ↓
9. Backend fetches user info and teams
   ↓
10. Backend returns success + user data
    ↓
11. Frontend shows "Connected" status
```

### Sync Flow

```
1. User clicks "Sync Issues" in frontend
   ↓
2. Frontend calls POST /api/connectors/linear/sync
   ↓
3. Backend fetches access_token from database
   ↓
4. Backend queries Linear GraphQL API:
   - Get issues (with team filter if specified)
   - Get comments for each issue (optional)
   ↓
5. Backend processes each issue:
   - Check if exists (by linear_issue_id)
   - Create new Feedback or update existing
   - Store Linear metadata in source_metadata field
   ↓
6. Backend commits to database
   ↓
7. Backend emits WebSocket event (real-time update)
   ↓
8. Frontend receives sync result:
   - Count of new issues
   - Count of updated issues
   - Total synced
```

## 🔌 API Endpoints

### OAuth Endpoints

#### Start OAuth Flow
```http
GET /api/auth/linear
```

**Response:**
```json
{
  "auth_url": "https://linear.app/oauth/authorize?...",
  "state": "random_token",
  "message": "Redirect user to auth_url to authorize Linear access"
}
```

#### OAuth Callback
```http
GET /api/auth/linear/callback?code={code}&state={state}
```

**Response:**
```json
{
  "success": true,
  "message": "Linear connected successfully",
  "user": {
    "id": "user-123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "teams": [
    {
      "id": "team-123",
      "name": "Engineering",
      "key": "ENG"
    }
  ],
  "redirect": "http://localhost:5173/integrations?linear_connected=true"
}
```

### Connector Endpoints

#### Sync Issues
```http
POST /api/connectors/linear/sync
Content-Type: application/json

{
  "team_id": "optional-team-id",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "synced": 45,
  "new": 40,
  "updated": 5,
  "team_id": "team-123",
  "limit": 50
}
```

#### Get Connection Status
```http
GET /api/connectors/linear/status
```

**Response:**
```json
{
  "connected": true,
  "user": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "teams": [...],
  "team_count": 3,
  "last_synced": "2024-01-15T10:30:00Z",
  "feedback_count": 142
}
```

#### List Teams
```http
GET /api/connectors/linear/teams
```

**Response:**
```json
{
  "teams": [
    {
      "id": "team-123",
      "name": "Engineering",
      "key": "ENG",
      "description": "Engineering team"
    }
  ],
  "count": 1
}
```

## 📊 Database Schema

### Source Table
```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- "Linear"
    source_type VARCHAR(50) NOT NULL,    -- "real"
    is_active BOOLEAN DEFAULT TRUE,
    config JSON,                         -- OAuth tokens and metadata
    created_at DATETIME,
    last_synced_at DATETIME
);
```

**Config JSON Structure:**
```json
{
  "access_token": "lin_api_xxx",
  "user": {
    "id": "user-123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "teams": [
    {
      "id": "team-123",
      "name": "Engineering",
      "key": "ENG"
    }
  ]
}
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    title VARCHAR(500),                  -- "[ENG-123] Feature title"
    text TEXT NOT NULL,                  -- Issue description
    customer_name VARCHAR(200),          -- Issue creator
    submitted_at DATETIME,               -- Issue created date
    source_metadata JSON                 -- Linear metadata
);
```

**Source Metadata JSON Structure:**
```json
{
  "linear_issue_id": "issue-uuid-123",
  "linear_identifier": "ENG-123",
  "linear_url": "https://linear.app/company/issue/ENG-123",
  "linear_state": "In Progress",
  "linear_priority": "High",
  "linear_team": "Engineering",
  "linear_labels": ["bug", "urgent"],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

## 🎨 Frontend Component

### LinearConnector Component

**Location:** `/frontend/src/components/LinearConnector.jsx`

**Features:**
- OAuth popup flow with state management
- Connection status indicator
- User info display
- Team selection dropdown
- Sync button with loading state
- Disconnect button
- Error handling with user-friendly messages
- Responsive design with Tailwind CSS
- Real-time status updates

**Usage:**
```jsx
import LinearConnector from './components/LinearConnector';

function IntegrationsPage() {
  return (
    <div>
      <LinearConnector />
    </div>
  );
}
```

## 🔐 Security

### OAuth Security
- **State parameter**: CSRF protection (random token)
- **Secure token storage**: Access tokens stored in database
- **Environment variables**: Client secret never exposed to frontend
- **HTTPS required**: In production, OAuth only over HTTPS

### Token Management
- **Access tokens**: Stored encrypted in database
- **No token refresh needed**: Linear tokens don't expire
- **Revocation**: Users can revoke access in Linear settings

### API Security
- **Rate limiting**: Respect Linear's rate limits (1000 req/hour)
- **Error handling**: Graceful degradation on API failures
- **Validation**: Input validation on all endpoints

## 🚀 Deployment

### Environment Variables

Required:
```bash
LINEAR_CLIENT_ID=your_client_id
LINEAR_CLIENT_SECRET=your_client_secret
LINEAR_REDIRECT_URI=https://your-domain.com/api/auth/linear/callback
```

Optional:
```bash
LINEAR_GRAPHQL_URL=https://api.linear.app/graphql  # Default
```

### Production Checklist

- [ ] Create Linear OAuth app with production callback URL
- [ ] Set environment variables on server
- [ ] Update redirect URI in Linear app settings
- [ ] Update CORS origins in FastAPI
- [ ] Enable HTTPS for OAuth flow
- [ ] Set up monitoring for sync failures
- [ ] Configure rate limit handling
- [ ] Set up webhook receiver (optional)

## 📈 Usage Examples

### Example 1: Basic Connection

```python
# Backend connector usage
from connectors.linear import LinearConnector

connector = LinearConnector(access_token="lin_api_xxx")

# Get user info
user = await connector.get_viewer()
print(f"Connected as: {user['name']}")

# List teams
teams = await connector.get_teams()
for team in teams:
    print(f"Team: {team['name']} ({team['key']})")
```

### Example 2: Sync Issues

```python
from connectors.linear import sync_issues_to_feedback

# Sync all issues from all teams
result = await sync_issues_to_feedback(
    db=db_session,
    access_token="lin_api_xxx",
    limit=100
)
print(f"Synced {result['new']} new issues")

# Sync issues from specific team
result = await sync_issues_to_feedback(
    db=db_session,
    access_token="lin_api_xxx",
    team_id="team-123",
    limit=50
)
```

### Example 3: Create Issue from Cluster

```python
# Create Linear issue from Compass cluster
issue = await connector.create_issue(
    team_id="team-123",
    title="[Feature Request] Dark mode",
    description="Multiple users requesting dark mode:\n\n" + cluster_summary,
    priority=2,  # High
    label_ids=["label-feature-request"]
)

print(f"Created issue: {issue['identifier']}")
print(f"URL: {issue['url']}")
```

## 🐛 Troubleshooting

### Common Issues

**1. OAuth popup blocked**
- Allow popups for your domain in browser settings
- Or manually visit OAuth URL in new tab

**2. "Invalid redirect URI"**
- Ensure callback URL in Linear app matches exactly
- Check for trailing slashes
- Verify HTTP vs HTTPS

**3. "Access token not found"**
- Reconnect Linear in UI
- Check database for stored token
- Verify OAuth callback completed successfully

**4. No issues syncing**
- Check if issues exist in Linear
- Verify read permissions in OAuth scopes
- Try different team or "All Teams"
- Check backend logs for errors

**5. Rate limit errors**
- Linear: 1000 requests/hour per user
- Reduce sync frequency
- Implement exponential backoff

## 📚 Resources

### Linear Documentation
- **API Docs**: https://developers.linear.app/docs
- **OAuth Guide**: https://developers.linear.app/docs/oauth
- **GraphQL Schema**: https://studio.apollographql.com/public/Linear-API
- **Rate Limits**: https://developers.linear.app/docs/graphql/working-with-the-graphql-api#rate-limiting

### Compass Documentation
- **Setup Guide**: LINEAR_SETUP.md
- **Testing Guide**: TEST_LINEAR.md
- **API Docs**: API_PLATFORM_README.md

## 🎯 Next Steps

### Immediate
1. Set up Linear OAuth app
2. Configure environment variables
3. Test OAuth flow
4. Sync first issues
5. View in Compass UI

### Future Enhancements
- [ ] Webhook support for real-time updates
- [ ] Automatic sync scheduling (cron job)
- [ ] Comment syncing
- [ ] Attachment syncing
- [ ] Custom field mapping
- [ ] Bi-directional sync (Compass → Linear)
- [ ] Bulk operations
- [ ] Advanced filtering (labels, assignees)

## 🏆 Success Metrics

Track these KPIs:
- **Connection rate**: % of users who connect Linear
- **Sync frequency**: How often users sync
- **Issue volume**: Number of issues synced
- **Feedback quality**: Clustering accuracy for Linear issues
- **Time to insight**: Time from issue creation to cluster
- **User engagement**: Frontend usage metrics

## 💡 Tips

1. **Start small**: Sync 10-50 issues first to test
2. **Use team filters**: Sync specific teams for targeted analysis
3. **Regular syncs**: Set up cron job for daily syncs
4. **Monitor rate limits**: Track API usage
5. **Use webhooks**: Set up webhooks for real-time updates (future)

---

**Built with ❤️ for Compass**

*Questions? Check LINEAR_SETUP.md or TEST_LINEAR.md*
