# GitHub OAuth Integration - Setup Guide

## Overview

The GitHub OAuth integration allows Compass to import issues and comments from GitHub repositories as customer feedback. Issues become feedback items, comments become additional feedback, and reactions are tracked as votes.

## Features

- **OAuth Authentication** - Secure, user-friendly connection via GitHub OAuth
- **Repository Selection** - Choose which repositories to monitor
- **Issue Import** - Import issues as feedback with full context
- **Comment Import** - Import issue comments as additional feedback
- **Reaction Tracking** - Track GitHub reactions (+1, heart, hooray, rocket) as vote counts
- **Label Filtering** - Filter by labels (e.g., "feature-request", "customer-feedback")
- **Auto-sync** - Sync new issues and comments on demand

## Setup Instructions

### 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"New OAuth App"**
3. Fill in the details:
   - **Application name**: `Compass Feedback`
   - **Homepage URL**: `http://localhost:3000` (or your domain)
   - **Authorization callback URL**: `http://localhost:3000/oauth/github/callback`
4. Click **"Register application"**
5. Copy the **Client ID**
6. Click **"Generate a new client secret"** and copy it

### 2. Connect in Compass

1. Open Compass frontend at `http://localhost:3000`
2. Go to the **"Collect"** tab
3. Find the **GitHub Connector** section
4. Enter your **Client ID** and **Client Secret**
5. Click **"Connect with GitHub"**
6. Authorize the app in GitHub
7. Select repositories to monitor
8. (Optional) Enter label filters
9. Click **"Configure Repositories"**
10. Click **"Sync Now"** to import issues

### 3. What Gets Imported

When you sync, Compass imports:

- **Issues**: Title + description become feedback text
- **Comments**: Each comment becomes a separate feedback item
- **Reactions**: +1, heart, hooray, rocket reactions are counted as votes
- **Labels**: Stored as metadata for categorization
- **State**: Open/closed status is tracked
- **Author**: GitHub username stored as customer name

## API Endpoints

### Start OAuth Flow

```http
GET /api/auth/github?client_id=YOUR_CLIENT_ID
```

Returns the GitHub authorization URL to redirect the user to.

**Response:**
```json
{
  "oauth_url": "https://github.com/login/oauth/authorize?client_id=..."
}
```

### Handle OAuth Callback

```http
POST /api/auth/github/callback
```

**Request Body:**
```json
{
  "client_id": "Iv1.abc123...",
  "client_secret": "secret...",
  "code": "authorization_code_from_github"
}
```

**Response:**
```json
{
  "success": true,
  "message": "GitHub connected successfully",
  "user": {
    "id": 12345,
    "login": "johndoe",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Get Repositories

```http
GET /api/connectors/github/repositories
```

Returns list of repositories the authenticated user has access to.

**Response:**
```json
{
  "repositories": [
    {
      "id": 123456,
      "name": "my-repo",
      "full_name": "owner/my-repo",
      "owner": "owner",
      "description": "My repository",
      "private": false,
      "url": "https://github.com/owner/my-repo",
      "open_issues_count": 15
    }
  ],
  "count": 1
}
```

### Configure Repositories

```http
POST /api/connectors/github/configure
```

**Request Body:**
```json
{
  "repository_full_names": ["owner/repo1", "owner/repo2"],
  "labels": ["bug", "feature-request", "customer-feedback"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configured 2 repositories",
  "repositories": ["owner/repo1", "owner/repo2"]
}
```

### Sync Issues

```http
POST /api/connectors/github/sync
```

**Request Body (optional):**
```json
{
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "synced": 45,
  "repositories": ["owner/repo1", "owner/repo2"]
}
```

### Get Status

```http
GET /api/connectors/github/status
```

**Response:**
```json
{
  "connected": true,
  "repositories": ["owner/repo1"],
  "labels": ["bug", "feature-request"],
  "last_synced": "2026-08-04T10:30:00Z",
  "feedback_count": 45
}
```

## Frontend Component

### Usage

```jsx
import GitHubConnector from './components/GitHubConnector';

function App() {
  return (
    <div>
      <GitHubConnector />
    </div>
  );
}
```

### Features

- OAuth flow handling
- Repository selection UI
- Label filtering
- Sync status display
- Error handling

## Backend Connector

### Usage

```python
from connectors.github import GitHubConnector

# Initialize with access token
connector = GitHubConnector(access_token="ghp_...")

# Test connection
connected = await connector.test_connection()

# Get user info
user = await connector.get_user_info()

# Get repositories
repos = await connector.get_repositories(limit=100)

# Fetch issues
issues = await connector.fetch_issues(
    repo_full_name="owner/repo",
    state="all",
    labels=["bug", "feature-request"],
    limit=100
)

# Fetch issue comments
comments = await connector.fetch_issue_comments(
    repo_full_name="owner/repo",
    issue_number=42
)
```

## Database Schema

GitHub feedback is stored with the following metadata:

```json
{
  "github_issue_id": 123456,
  "github_issue_number": 42,
  "github_repo": "owner/repo",
  "github_url": "https://github.com/owner/repo/issues/42",
  "github_state": "open",
  "github_labels": ["bug", "feature-request"],
  "vote_count": 5,
  "comments_count": 3
}
```

For comments:

```json
{
  "github_comment_id": 789012,
  "github_issue_id": 123456,
  "github_issue_number": 42,
  "github_repo": "owner/repo",
  "vote_count": 2
}
```

## Security Notes

1. **OAuth Tokens** - Access tokens are stored encrypted in the database
2. **Scopes** - Only requests `repo` scope (read access to repositories)
3. **Rate Limits** - GitHub API has rate limits (5000 requests/hour for authenticated users)
4. **Webhook Alternative** - For real-time updates, consider GitHub webhooks instead of polling

## Troubleshooting

### "Failed to exchange code for token"

- Check that your Client ID and Client Secret are correct
- Ensure the authorization callback URL matches your OAuth app settings
- Make sure you're using the code within 10 minutes (it expires)

### "GitHub not connected. Complete OAuth first."

- You need to complete the OAuth flow before using other endpoints
- Check the `/api/connectors/github/status` endpoint to verify connection

### "No repositories configured"

- After connecting, you must select at least one repository
- Use the `/api/connectors/github/configure` endpoint or the UI

### Rate Limit Issues

- GitHub allows 5000 API requests per hour for authenticated users
- Reduce sync frequency or limit number of repositories
- Consider implementing caching

## Best Practices

1. **Label Filtering** - Use labels to filter only relevant issues (e.g., "customer-feedback", "feature-request")
2. **Regular Syncs** - Set up periodic syncs (e.g., every hour) to keep feedback up to date
3. **Monitor Specific Repos** - Only monitor repositories where customers report feedback
4. **Reaction Weights** - Use reaction counts as vote weights for prioritization
5. **Comment Threading** - Link comments back to parent issues for context

## Example Workflow

1. Customer creates GitHub issue in your repository
2. Other users add +1 reactions to show support
3. Compass syncs issues hourly
4. Issue appears as feedback with vote count
5. NLP clustering groups similar issues
6. Priority calculator weighs vote counts
7. Features appear on roadmap based on demand

## Next Steps

- Set up automatic hourly syncs via cron job
- Configure GitHub webhooks for real-time updates
- Integrate with Linear/Jira to create tickets from high-priority feedback
- Set up email notifications when high-vote issues are created
