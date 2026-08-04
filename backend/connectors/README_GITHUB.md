# GitHub OAuth Connector

Simple, OAuth-based GitHub integration for Compass.

## Quick Start

```python
from connectors.github import GitHubConnector, get_oauth_url, exchange_code_for_token

# 1. Get OAuth URL
oauth_url = get_oauth_url(
    client_id="Iv1.abc123...",
    redirect_uri="http://localhost:3000/callback",
    scope="repo"
)
# Send user to oauth_url

# 2. Exchange code for token
access_token = await exchange_code_for_token(
    client_id="Iv1.abc123...",
    client_secret="secret...",
    code="code_from_callback"
)

# 3. Use connector
connector = GitHubConnector(access_token)

# Test connection
if await connector.test_connection():
    print("Connected!")

# Get user info
user = await connector.get_user_info()
print(f"User: {user['login']}")

# Get repositories
repos = await connector.get_repositories(limit=10)
for repo in repos:
    print(f"- {repo['full_name']} ({repo['open_issues_count']} issues)")

# Fetch issues
issues = await connector.fetch_issues(
    repo_full_name="owner/repo",
    state="all",
    labels=["bug", "feature-request"],
    limit=50
)

for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")
    print(f"  Comments: {issue['comments_count']}")
    print(f"  Reactions: {issue['reactions']}")

# Fetch comments
comments = await connector.fetch_issue_comments(
    repo_full_name="owner/repo",
    issue_number=42
)
```

## Features

- **OAuth 2.0** - Secure authentication
- **Async/await** - Fast concurrent operations
- **Repository listing** - Get all accessible repos
- **Issue fetching** - Filter by state, labels, date
- **Comment fetching** - Get all comments for an issue
- **Reaction counting** - Track votes/engagement
- **Error handling** - Graceful failure handling

## API Reference

### `get_oauth_url(client_id, redirect_uri, scope="repo")`

Generate OAuth authorization URL.

**Returns:** `str` - Authorization URL

### `exchange_code_for_token(client_id, client_secret, code)`

Exchange OAuth code for access token.

**Returns:** `str` or `None` - Access token

### `GitHubConnector(access_token)`

Initialize connector with access token.

#### `test_connection() -> bool`

Test if access token is valid.

#### `get_user_info() -> Dict`

Get authenticated user information.

**Returns:**
```python
{
    "id": 12345,
    "login": "username",
    "name": "Full Name",
    "email": "user@example.com",
    "avatar_url": "https://..."
}
```

#### `get_repositories(limit=100) -> List[Dict]`

Get repositories user has access to.

**Returns:**
```python
[
    {
        "id": 123456,
        "name": "repo-name",
        "full_name": "owner/repo-name",
        "owner": "owner",
        "description": "Repo description",
        "private": False,
        "url": "https://github.com/owner/repo-name",
        "open_issues_count": 15
    }
]
```

#### `fetch_issues(repo_full_name, state="all", labels=None, limit=100, since=None) -> List[Dict]`

Fetch issues from repository.

**Parameters:**
- `repo_full_name`: "owner/repo"
- `state`: "open", "closed", or "all"
- `labels`: List of label names to filter by
- `limit`: Max issues to fetch (default 100)
- `since`: ISO 8601 timestamp (only issues updated after this)

**Returns:**
```python
[
    {
        "id": 123456,
        "number": 42,
        "title": "Issue title",
        "body": "Issue description",
        "state": "open",
        "labels": ["bug", "feature-request"],
        "user": {
            "login": "username",
            "id": 12345,
            "avatar_url": "https://..."
        },
        "reactions": {
            "+1": 5,
            "heart": 2,
            "hooray": 1,
            "rocket": 3
        },
        "comments_count": 10,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "url": "https://github.com/owner/repo/issues/42",
        "api_url": "https://api.github.com/repos/owner/repo/issues/42"
    }
]
```

#### `fetch_issue_comments(repo_full_name, issue_number) -> List[Dict]`

Fetch comments for specific issue.

**Returns:**
```python
[
    {
        "id": 789012,
        "body": "Comment text",
        "user": {
            "login": "username",
            "id": 12345
        },
        "reactions": {
            "+1": 2,
            "heart": 1
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

## GitHub API Rate Limits

- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour

Check rate limit status:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

## Error Handling

```python
try:
    connector = GitHubConnector(token)
    if not await connector.test_connection():
        print("Invalid token")
        return

    issues = await connector.fetch_issues("owner/repo")
except Exception as e:
    print(f"Error: {e}")
```

## OAuth Scopes

- `repo` - Full access to repositories (read/write)
- `public_repo` - Access to public repositories only
- `read:org` - Read org and team membership

For read-only access, use: `scope="public_repo"`

## Examples

### Sync all issues from a repo

```python
async def sync_repo(token, repo_name):
    connector = GitHubConnector(token)
    issues = await connector.fetch_issues(
        repo_full_name=repo_name,
        state="all",
        limit=1000
    )

    for issue in issues:
        # Fetch comments for each issue
        comments = await connector.fetch_issue_comments(
            repo_full_name=repo_name,
            issue_number=issue['number']
        )
        issue['comments'] = comments

    return issues
```

### Get highly voted issues

```python
async def get_popular_issues(token, repo_name, min_votes=5):
    connector = GitHubConnector(token)
    issues = await connector.fetch_issues(repo_full_name=repo_name)

    popular = []
    for issue in issues:
        total_votes = (
            issue['reactions'].get('+1', 0) +
            issue['reactions'].get('heart', 0) +
            issue['reactions'].get('hooray', 0) +
            issue['reactions'].get('rocket', 0)
        )
        if total_votes >= min_votes:
            issue['total_votes'] = total_votes
            popular.append(issue)

    return sorted(popular, key=lambda x: x['total_votes'], reverse=True)
```

### Monitor multiple repos

```python
async def sync_multiple_repos(token, repo_names):
    connector = GitHubConnector(token)
    all_issues = []

    for repo in repo_names:
        issues = await connector.fetch_issues(
            repo_full_name=repo,
            labels=["feature-request", "customer-feedback"]
        )
        all_issues.extend(issues)

    return all_issues
```

## Testing

```bash
# Test OAuth URL generation
python test_github_connector.py

# Test with real token
python test_github_connector.py YOUR_GITHUB_TOKEN
```

## Dependencies

- `httpx` - Async HTTP client

## See Also

- [GitHub REST API Docs](https://docs.github.com/en/rest)
- [GitHub OAuth Guide](https://docs.github.com/en/apps/oauth-apps)
- [Compass GitHub Setup](../../GITHUB_OAUTH_SETUP.md)
