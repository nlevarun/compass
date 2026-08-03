# Quick Start: Import & Integration Features

Get started with historical data import and Jira/Linear sync in 5 minutes.

---

## Setup (One-time)

### 1. Install Dependencies

```bash
cd /home/wsl-user/compass/backend
pip install -r requirements.txt
```

Key new dependencies:
- `jira==3.5.2` - Jira integration
- `httpx` - Async HTTP (already installed)
- `pandas` - CSV processing (already installed)

### 2. Initialize Database

```bash
python3 database.py
```

This creates new tables:
- `import_jobs` - Track import progress
- `jira_issues` - Jira issue links
- `linear_issues` - Linear issue links

### 3. Start Server

```bash
python3 main.py
# or
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/docs for API docs

---

## Feature 1: Import Historical CSV

### Step 1: Create Sample CSV

```bash
cat > sample_feedback.csv << 'EOF'
customer,feedback_text,date,revenue
Acme Corp,Your mobile app is too slow,2026-01-15,500000
TechStart,Love the new dashboard!,2026-02-20,250000
BigCo,Need better Excel export,2026-03-10,1000000
EOF
```

### Step 2: Upload & Preview

```bash
curl -X POST http://localhost:8000/api/import/csv \
  -F "file=@sample_feedback.csv"
```

Response shows:
- Column preview
- Suggested mapping
- File path for next step

### Step 3: Start Import

```bash
curl -X POST http://localhost:8000/api/import/csv/start \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/tmp/compass_uploads/[file_id]_sample_feedback.csv",
    "column_mapping": {
      "text": "feedback_text",
      "customer_name": "customer",
      "customer_revenue": "revenue",
      "submitted_at": "date"
    },
    "skip_invalid": true
  }'
```

Returns `job_id` to track progress.

### Step 4: Check Progress

```bash
curl http://localhost:8000/api/import/status/{job_id}
```

---

## Feature 2: Jira Integration

### Prerequisites:
1. Jira Cloud account (or Server 8.0+)
2. API token from: https://id.atlassian.com/manage-profile/security/api-tokens
3. Project key (e.g., "ENG")

### Step 1: Test Connection

```bash
curl -X POST http://localhost:8000/api/integrations/jira/test \
  -H "Content-Type: application/json" \
  -d '{
    "jira_url": "https://yourcompany.atlassian.net",
    "username": "your-email@company.com",
    "api_token": "your_api_token_here",
    "default_project": "ENG",
    "default_issue_type": "Story"
  }'
```

Should return:
```json
{
  "status": "success",
  "connected": true,
  "user": "Your Name",
  "projects": ["ENG", "PROD", "CS"]
}
```

### Step 2: Import Feedback & Cluster

```bash
# First, sync mock data
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering
curl -X POST http://localhost:8000/api/clustering/run

# Get clusters
curl http://localhost:8000/api/clusters
```

### Step 3: Create Jira Issue from Cluster

```bash
curl -X POST http://localhost:8000/api/integrations/jira/create-issue \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_id": 1,
    "project_key": "ENG",
    "priority": "High",
    "labels": ["compass", "customer-feedback"]
  }'
```

Returns:
```json
{
  "status": "success",
  "jira_key": "ENG-123",
  "jira_url": "https://yourcompany.atlassian.net/browse/ENG-123"
}
```

### Step 4: Sync Status

```bash
# Sync single issue
curl http://localhost:8000/api/integrations/jira/status/ENG-123

# Sync all issues
curl -X POST http://localhost:8000/api/integrations/jira/sync
```

---

## Feature 3: Linear Integration

### Prerequisites:
1. Linear account
2. API key from: Linear Settings > API
3. Team ID (get from test connection)

### Step 1: Test Connection

```bash
curl -X POST http://localhost:8000/api/integrations/linear/test \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "lin_api_your_key_here"
  }'
```

Returns teams:
```json
{
  "status": "success",
  "teams": [
    {"id": "team-uuid", "name": "Engineering", "key": "ENG"}
  ]
}
```

### Step 2: Create Linear Issue

```bash
curl -X POST http://localhost:8000/api/integrations/linear/create-issue \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_id": 1,
    "team_id": "team-uuid-from-above",
    "priority": 2,
    "labels": ["compass", "customer-feedback"]
  }'
```

Returns:
```json
{
  "status": "success",
  "linear_id": "issue-uuid",
  "linear_identifier": "ENG-123",
  "linear_url": "https://linear.app/company/issue/ENG-123"
}
```

---

## Feature 4: Zendesk Import (Historical)

### Prerequisites:
1. Zendesk account
2. API token from: Admin > Channels > API
3. Subdomain (from yourcompany.zendesk.com)

### Import Last 30 Days of Tickets

```bash
curl -X POST http://localhost:8000/api/import/zendesk \
  -H "Content-Type: application/json" \
  -d '{
    "subdomain": "yourcompany",
    "email": "admin@company.com",
    "api_token": "your_zendesk_token",
    "start_date": "2026-07-01T00:00:00",
    "end_date": "2026-07-31T23:59:59",
    "status_filter": ["closed", "solved"],
    "fetch_comments": true,
    "fetch_users": true
  }'
```

Returns `job_id`. Monitor with:

```bash
curl http://localhost:8000/api/import/status/{job_id}
```

---

## Feature 5: Intercom Import (Historical)

### Prerequisites:
1. Intercom account
2. Access token from: Settings > Developers > Developer Hub

### Import Closed Conversations

```bash
curl -X POST http://localhost:8000/api/import/intercom \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "your_intercom_token",
    "start_date": "2026-01-01T00:00:00",
    "end_date": "2026-07-31T23:59:59",
    "state_filter": "closed",
    "fetch_parts": true,
    "fetch_users": true
  }'
```

Returns `job_id` for tracking.

---

## Common Workflows

### Workflow 1: Import → Cluster → Jira

```bash
# 1. Import CSV
JOB_ID=$(curl -X POST http://localhost:8000/api/import/csv/start \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/tmp/compass_uploads/file.csv", "column_mapping": {...}}' \
  | jq -r '.job_id')

# 2. Wait for completion (or poll status)
sleep 30

# 3. Run clustering
curl -X POST http://localhost:8000/api/clustering/run

# 4. Generate roadmap
curl -X POST http://localhost:8000/api/roadmap/generate

# 5. Create Jira issues for top 5 clusters
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/integrations/jira/create-issue \
    -d "{\"cluster_id\": $i, \"project_key\": \"ENG\"}"
done
```

### Workflow 2: Continuous Sync

```bash
# Add to crontab for hourly Jira sync:
0 * * * * curl -X POST http://localhost:8000/api/integrations/jira/sync

# Or Linear:
0 * * * * curl -X POST http://localhost:8000/api/integrations/linear/sync
```

### Workflow 3: Link Existing Issues

```bash
# Link existing Jira issue to cluster
curl -X POST http://localhost:8000/api/integrations/jira/link-issue \
  -d '{"jira_key": "ENG-456", "cluster_id": 3}'

# Link to roadmap item
curl -X POST http://localhost:8000/api/integrations/jira/link-issue \
  -d '{"jira_key": "ENG-456", "roadmap_item_id": 12}'
```

---

## Troubleshooting

### Import Issues

**Job stuck at pending:**
```bash
# Check job status
curl http://localhost:8000/api/import/status/{job_id}

# List all jobs
curl http://localhost:8000/api/import/jobs
```

**CSV auto-mapping wrong:**
```bash
# Specify exact mapping:
{
  "column_mapping": {
    "text": "exact_column_name",
    "customer_name": "another_exact_name"
  }
}
```

### Jira Issues

**Authentication failed:**
- Verify API token (not password!)
- Check username is email for Cloud
- Test connection first

**Project not found:**
- Project key is case-sensitive: "ENG", not "eng"
- User must have project access

### Linear Issues

**Team not found:**
- Get team ID from test connection response
- Team ID is UUID, not name

**GraphQL error:**
- Check API key is valid
- Review error message in response

---

## Environment Variables (Optional)

Create `.env` file:

```bash
# Jira
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=email@company.com
JIRA_API_TOKEN=your_token
JIRA_PROJECT=ENG

# Linear
LINEAR_API_KEY=lin_api_...
LINEAR_TEAM_ID=team-uuid

# Zendesk
ZENDESK_SUBDOMAIN=yourcompany
ZENDESK_EMAIL=admin@company.com
ZENDESK_TOKEN=your_token

# Intercom
INTERCOM_TOKEN=your_token
```

Then use in code:
```python
import os
from dotenv import load_dotenv
load_dotenv()

jira_url = os.getenv("JIRA_URL")
```

---

## Next Steps

1. **Read Full Docs:**
   - [Import Guide](docs/IMPORTING_DATA.md)
   - [Integration Guide](docs/JIRA_INTEGRATION.md)

2. **Try Advanced Features:**
   - Custom field mapping
   - Bulk operations
   - Priority updates
   - Webhooks (coming soon)

3. **Production Setup:**
   - Move to PostgreSQL
   - Set up automated sync (cron)
   - Configure rate limiting
   - Enable SSL/TLS

---

## API Reference

**Import Endpoints:**
- POST `/api/import/zendesk`
- POST `/api/import/intercom`
- POST `/api/import/csv`
- POST `/api/import/csv/start`
- GET `/api/import/status/{job_id}`
- GET `/api/import/jobs`

**Jira Endpoints:**
- POST `/api/integrations/jira/test`
- POST `/api/integrations/jira/create-issue`
- POST `/api/integrations/jira/link-issue`
- GET `/api/integrations/jira/status/{jira_key}`
- POST `/api/integrations/jira/sync`

**Linear Endpoints:**
- POST `/api/integrations/linear/test`
- POST `/api/integrations/linear/create-issue`
- POST `/api/integrations/linear/link-issue`
- GET `/api/integrations/linear/status/{issue_id}`
- POST `/api/integrations/linear/sync`

---

## Support

- Full Docs: `/docs/`
- API Docs: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/redoc

**Need help?**
- Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Review error logs in API responses
- Test endpoints with curl examples above

---

**Last Updated:** 2026-08-03
