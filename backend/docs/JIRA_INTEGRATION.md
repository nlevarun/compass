# Jira & Linear Integration Guide

Compass provides **bidirectional sync** with Jira and Linear, allowing you to:
- Create issues from feedback clusters
- Link existing issues to Compass data
- Sync status automatically
- Update priority based on feedback changes
- Add customer feedback as comments

This is a **competitive advantage** - most tools only do one-way sync or sync poorly.

---

## Quick Start

### Jira Setup

```bash
# 1. Get Jira credentials
# - Jira URL: https://yourcompany.atlassian.net
# - Username: your-email@company.com
# - API Token: Generate from https://id.atlassian.com/manage-profile/security/api-tokens

# 2. Test connection
POST /api/integrations/jira/test
{
  "jira_url": "https://yourcompany.atlassian.net",
  "username": "your-email@company.com",
  "api_token": "your_api_token_here",
  "default_project": "PROJ",
  "default_issue_type": "Story"
}

# 3. Create issue from cluster
POST /api/integrations/jira/create-issue
{
  "cluster_id": 123,
  "project_key": "PROJ",
  "priority": "High",
  "labels": ["compass", "customer-feedback"]
}

# 4. Sync status
POST /api/integrations/jira/sync
```

### Linear Setup

```bash
# 1. Get Linear API key
# - Go to Linear Settings > API
# - Generate Personal API Key

# 2. Test connection
POST /api/integrations/linear/test
{
  "api_key": "lin_api_...",
  "default_team_id": "team-uuid-here"
}

# 3. Create issue from cluster
POST /api/integrations/linear/create-issue
{
  "cluster_id": 123,
  "team_id": "team-uuid-here",
  "priority": 2,
  "labels": ["compass", "customer-feedback"]
}

# 4. Sync status
POST /api/integrations/linear/sync
```

---

## Features

### 1. Create Issues from Clusters

**Why it's useful:**
- Automatically aggregates customer feedback
- Shows revenue impact in issue description
- Links all related feedback
- Sets priority based on customer data

**What gets created:**
- Issue title: Cluster label (e.g., "Mobile App Performance Issues")
- Description: Summary with revenue impact, top customers, feedback samples
- Priority: Auto-calculated from cluster priority score
- Labels: "compass", "customer-feedback" + custom
- Comments: Detailed customer feedback (up to 10 samples)

**Jira Example:**
```bash
POST /api/integrations/jira/create-issue
{
  "cluster_id": 45,
  "project_key": "ENG",
  "issue_type": "Story",
  "priority": "High",
  "labels": ["compass", "mobile", "performance"]
}
```

Response:
```json
{
  "status": "success",
  "jira_key": "ENG-234",
  "jira_id": "10234",
  "jira_url": "https://yourcompany.atlassian.net/browse/ENG-234"
}
```

**Linear Example:**
```bash
POST /api/integrations/linear/create-issue
{
  "cluster_id": 45,
  "team_id": "abc-123",
  "priority": 1,
  "labels": ["compass", "mobile", "performance"]
}
```

### 2. Create Issues from Individual Feedback

For high-value customers or critical issues:

```bash
POST /api/integrations/jira/create-issue
{
  "feedback_id": 789,
  "project_key": "ENG",
  "priority": "Highest"
}
```

### 3. Link Existing Issues

Already have issues in Jira/Linear? Link them to Compass:

**Jira:**
```bash
POST /api/integrations/jira/link-issue
{
  "jira_key": "ENG-234",
  "cluster_id": 45
}
```

**Linear:**
```bash
POST /api/integrations/linear/link-issue
{
  "issue_id": "issue-uuid-here",
  "cluster_id": 45
}
```

### 4. Bidirectional Status Sync

**How it works:**
- Compass → Jira/Linear: Updates priority when feedback changes
- Jira/Linear → Compass: Updates roadmap status when issue moves

**Sync individual issue:**
```bash
GET /api/integrations/jira/status/ENG-234
GET /api/integrations/linear/status/issue-uuid
```

**Sync all issues:**
```bash
POST /api/integrations/jira/sync
POST /api/integrations/linear/sync
```

**Status mapping:**

| Jira Status | Linear Status | Compass Status |
|-------------|---------------|----------------|
| To Do / Open | Todo / Backlog | proposed |
| In Progress | In Progress | in_progress |
| In Review | In Review | in_progress |
| Done / Closed | Done / Completed | shipped |
| Resolved | Canceled | shipped |

### 5. Automatic Priority Updates

When feedback patterns change (e.g., more high-value customers report same issue):

```bash
# Compass can update Jira priority
POST /api/integrations/jira/update-priority
{
  "jira_key": "ENG-234",
  "new_priority": "Highest"
}
```

---

## Configuration

### Jira Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `jira_url` | string | Yes | Jira instance URL (cloud or server) |
| `username` | string | Yes | Jira username/email |
| `api_token` | string | Yes | API token (not password!) |
| `default_project` | string | No | Default project key (e.g., "ENG") |
| `default_issue_type` | string | No | Default issue type (default: "Story") |

**Supported Jira Versions:**
- Jira Cloud (recommended)
- Jira Server 8.0+
- Jira Data Center

**Required Permissions:**
- Create issues
- Edit issues
- Add comments
- View projects

### Linear Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `api_key` | string | Yes | Linear Personal API Key |
| `default_team_id` | string | No | Default team ID for creating issues |

**Linear Permissions:**
- Create issues
- Edit issues
- Add comments
- View teams

---

## Priority Mapping

### Compass → Jira

| Compass Priority Score | Jira Priority |
|------------------------|---------------|
| 0.8 - 1.0 | Highest |
| 0.6 - 0.8 | High |
| 0.4 - 0.6 | Medium |
| 0.2 - 0.4 | Low |
| 0.0 - 0.2 | Lowest |

### Compass → Linear

| Compass Priority Score | Linear Priority |
|------------------------|-----------------|
| 0.8 - 1.0 | 1 (Urgent) |
| 0.6 - 0.8 | 2 (High) |
| 0.4 - 0.6 | 3 (Medium) |
| < 0.4 | 4 (Low) |

---

## Best Practices

### 1. Start with Top Clusters

Don't create issues for every cluster. Start with:
- Top 10 clusters by priority
- Clusters with high revenue impact (>$500K)
- Clusters with negative sentiment

### 2. Use Labels Consistently

Recommended label scheme:
- `compass` - All issues from Compass
- `customer-feedback` - Customer-driven
- `high-revenue` - >$1M revenue impact
- `churn-risk` - Customers at risk

### 3. Sync Regularly

Set up automated sync:
```bash
# Cron job (every hour)
0 * * * * curl -X POST https://compass.yourcompany.com/api/integrations/jira/sync
```

### 4. Add Context in Comments

When creating issues, Compass automatically adds:
- Top 5-10 customer feedback samples
- Customer names and revenue
- Sentiment scores
- Submission dates

### 5. Link to Roadmap Items

```bash
POST /api/integrations/jira/link-issue
{
  "jira_key": "ENG-234",
  "roadmap_item_id": 12
}
```

This enables:
- Roadmap status updates when issue moves
- Direct link from roadmap to Jira
- Impact tracking

---

## Advanced Features

### Webhooks (Coming Soon)

For real-time sync:
- Jira webhook → Compass (status changes)
- Linear webhook → Compass (status changes)
- Compass webhook → Jira/Linear (priority changes)

### Custom Fields

Map custom fields:
```bash
POST /api/integrations/jira/create-issue
{
  "cluster_id": 45,
  "custom_fields": {
    "customfield_10001": "High Value",
    "customfield_10002": 1500000
  }
}
```

### Bulk Operations

Create issues for multiple clusters:
```bash
POST /api/integrations/jira/bulk-create
{
  "cluster_ids": [45, 67, 89],
  "project_key": "ENG",
  "labels": ["compass", "q3-2026"]
}
```

---

## Troubleshooting

### Jira Issues

#### "Authentication failed"
- Verify API token is correct
- Ensure username is email (for Cloud)
- Check token hasn't expired

#### "Project not found"
- Verify project key (e.g., "ENG", not "Engineering")
- Check user has access to project
- Test connection first

#### "Issue type not found"
- Common types: "Story", "Task", "Bug", "Epic"
- Check issue type exists in project
- Case-sensitive!

### Linear Issues

#### "Invalid API key"
- Generate new key from Linear Settings
- Ensure key has correct scope
- Test connection first

#### "Team not found"
- Get team ID from test connection response
- Team ID is UUID, not team name

#### "GraphQL error"
- Check API version compatibility
- Review error message for details
- Linear API docs: https://developers.linear.app

---

## API Reference

### Jira Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/integrations/jira/test` | POST | Test connection |
| `/api/integrations/jira/create-issue` | POST | Create issue from cluster/feedback |
| `/api/integrations/jira/link-issue` | POST | Link existing issue |
| `/api/integrations/jira/status/{key}` | GET | Sync issue status |
| `/api/integrations/jira/sync` | POST | Sync all issues |

### Linear Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/integrations/linear/test` | POST | Test connection |
| `/api/integrations/linear/create-issue` | POST | Create issue from cluster/feedback |
| `/api/integrations/linear/link-issue` | POST | Link existing issue |
| `/api/integrations/linear/status/{id}` | GET | Sync issue status |
| `/api/integrations/linear/sync` | POST | Sync all issues |

---

## Competitive Comparison

| Feature | Compass | Productboard | Aha! | UserVoice |
|---------|---------|--------------|------|-----------|
| Bidirectional sync | ✅ | ❌ | ⚠️ Limited | ❌ |
| Auto priority mapping | ✅ | ❌ | ❌ | ❌ |
| Customer feedback in comments | ✅ | ✅ | ⚠️ Manual | ✅ |
| Linear support | ✅ | ❌ | ❌ | ❌ |
| Jira Cloud + Server | ✅ | ✅ | ✅ | ✅ |
| Real-time sync | 🔜 Soon | ✅ | ✅ | ❌ |

---

## Examples

### Complete Workflow

```bash
# 1. Import historical feedback
POST /api/import/zendesk
# ... (see IMPORTING_DATA.md)

# 2. Run clustering
POST /api/clustering/run

# 3. Generate roadmap
POST /api/roadmap/generate

# 4. Create Jira issues for top 10 items
for cluster_id in $(curl /api/clusters | jq -r '.[0:10].id'); do
  curl -X POST /api/integrations/jira/create-issue \
    -d "{\"cluster_id\": $cluster_id, \"project_key\": \"ENG\"}"
done

# 5. Set up daily sync
# Add to cron: 0 9 * * * curl -X POST .../api/integrations/jira/sync
```

---

## Support

- Jira Cloud docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- Linear API docs: https://developers.linear.app/docs
- Compass support: Check error logs in API responses

---

## Changelog

- **2026-08-03**: Initial version
- Bidirectional Jira sync
- Linear integration
- Priority mapping
- Status sync
