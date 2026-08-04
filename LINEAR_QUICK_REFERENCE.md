# Linear Integration - Quick Reference Card

## Setup (One-Time)

1. **Create OAuth App**: https://linear.app/settings/api/applications
2. **Add to .env**:
   ```
   LINEAR_CLIENT_ID=your_client_id
   LINEAR_CLIENT_SECRET=your_client_secret
   LINEAR_REDIRECT_URI=http://localhost:8000/api/auth/linear/callback
   ```
3. **Restart backend**: `./start.sh`

## API Endpoints

```bash
# Start OAuth
GET /api/auth/linear

# OAuth callback (automatic)
GET /api/auth/linear/callback?code=xxx

# Sync issues
POST /api/connectors/linear/sync
{"team_id": "optional", "limit": 50}

# Get status
GET /api/connectors/linear/status

# List teams
GET /api/connectors/linear/teams
```

## Frontend Usage

```jsx
import LinearConnector from './components/LinearConnector';

<LinearConnector />
```

## Files

- **Backend**: `/backend/connectors/linear.py`
- **Frontend**: `/frontend/src/components/LinearConnector.jsx`
- **API Routes**: `/backend/main.py` (lines 2218-2391)
- **Setup Guide**: `/LINEAR_SETUP.md`
- **Testing**: `/TEST_LINEAR.md`

## Common Commands

```bash
# Test connection
curl http://localhost:8000/api/connectors/linear/status

# Sync 10 issues
curl -X POST http://localhost:8000/api/connectors/linear/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'

# List teams
curl http://localhost:8000/api/connectors/linear/teams
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth popup blocked | Allow popups for localhost:5173 |
| Invalid redirect URI | Check callback URL in Linear app |
| No issues syncing | Verify Linear permissions (read scope) |
| Token not found | Reconnect Linear in UI |

## Data Flow

```
Linear Issues → GraphQL API → Backend → Database → Frontend → AI Clustering
```

## What Gets Synced

- ✅ Issue ID, title, description
- ✅ State (Todo, In Progress, Done)
- ✅ Priority (None, Low, Med, High, Urgent)
- ✅ Labels, team, creator
- ✅ Created/updated timestamps
- ✅ URL to Linear issue

## Environment Variables

```bash
LINEAR_CLIENT_ID          # Required
LINEAR_CLIENT_SECRET      # Required
LINEAR_REDIRECT_URI       # Required
```

## Performance

- OAuth: < 2 seconds
- Sync 50 issues: < 10 seconds
- Rate limit: 1000 requests/hour

## Documentation

- 📘 **Quick Start**: LINEAR_QUICKSTART.md
- 📗 **Setup**: LINEAR_SETUP.md
- 📙 **Testing**: TEST_LINEAR.md
- 📕 **Full Docs**: LINEAR_INTEGRATION_README.md
- 📓 **Summary**: LINEAR_IMPLEMENTATION_SUMMARY.md

## Support

- Linear API: https://developers.linear.app/docs
- OAuth Docs: https://developers.linear.app/docs/oauth
- GraphQL: https://studio.apollographql.com/public/Linear-API

---

**Time to first sync: 5 minutes** ⚡
