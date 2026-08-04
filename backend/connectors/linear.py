"""
Linear OAuth Connector for Compass

Implements Linear OAuth 2.0 flow and GraphQL API integration.
Docs: https://developers.linear.app/docs/oauth
GraphQL: https://developers.linear.app/docs/graphql/working-with-the-graphql-api

Features:
- OAuth 2.0 authentication
- Fetch issues assigned to user
- Sync issue comments as feedback
- Link Compass roadmap items to Linear issues
- Two-way sync: Compass roadmap → Linear roadmaps
"""

import os
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from models import Source, Feedback


# Linear OAuth Configuration
LINEAR_CLIENT_ID = os.getenv("LINEAR_CLIENT_ID", "")
LINEAR_CLIENT_SECRET = os.getenv("LINEAR_CLIENT_SECRET", "")
LINEAR_REDIRECT_URI = os.getenv("LINEAR_REDIRECT_URI", "http://localhost:8000/api/auth/linear/callback")

# Linear API endpoints
LINEAR_OAUTH_URL = "https://linear.app/oauth/authorize"
LINEAR_TOKEN_URL = "https://api.linear.app/oauth/token"
LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"


class LinearConnector:
    """Linear API connector with OAuth and GraphQL support."""

    def __init__(self, access_token: str):
        """
        Initialize Linear connector with OAuth access token.

        Args:
            access_token: Linear OAuth access token
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

    async def graphql_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query against Linear API.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            API response data
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LINEAR_GRAPHQL_URL,
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_viewer(self) -> Dict[str, Any]:
        """
        Get current authenticated user info.

        Returns:
            User data including id, name, email
        """
        query = """
        query {
            viewer {
                id
                name
                email
                avatarUrl
            }
        }
        """
        result = await self.graphql_query(query)
        return result["data"]["viewer"]

    async def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get all teams accessible to the user.

        Returns:
            List of teams with id, name, key
        """
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                }
            }
        }
        """
        result = await self.graphql_query(query)
        return result["data"]["teams"]["nodes"]

    async def get_issues(
        self,
        team_id: Optional[str] = None,
        limit: int = 50,
        assigned_to_me: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch issues from Linear.

        Args:
            team_id: Optional filter by team ID
            limit: Maximum number of issues to fetch (default 50)
            assigned_to_me: Filter to issues assigned to current user

        Returns:
            List of issues with metadata
        """
        # Build filter
        filter_parts = []
        if team_id:
            filter_parts.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if assigned_to_me:
            filter_parts.append('assignee: { isMe: { eq: true } }')

        filter_str = ""
        if filter_parts:
            filter_str = f'filter: {{ {", ".join(filter_parts)} }}'

        query = f"""
        query {{
            issues({filter_str}, first: {limit}) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    priority
                    priorityLabel
                    state {{
                        id
                        name
                        type
                    }}
                    assignee {{
                        id
                        name
                        email
                    }}
                    creator {{
                        id
                        name
                        email
                    }}
                    team {{
                        id
                        name
                        key
                    }}
                    labels {{
                        nodes {{
                            id
                            name
                            color
                        }}
                    }}
                    createdAt
                    updatedAt
                    url
                }}
            }}
        }}
        """

        result = await self.graphql_query(query)
        return result["data"]["issues"]["nodes"]

    async def get_issue_comments(self, issue_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific issue.

        Args:
            issue_id: Linear issue ID
            limit: Maximum number of comments to fetch

        Returns:
            List of comments
        """
        query = f"""
        query {{
            issue(id: "{issue_id}") {{
                comments(first: {limit}) {{
                    nodes {{
                        id
                        body
                        user {{
                            id
                            name
                            email
                        }}
                        createdAt
                        updatedAt
                    }}
                }}
            }}
        }}
        """

        result = await self.graphql_query(query)
        return result["data"]["issue"]["comments"]["nodes"]

    async def create_issue(
        self,
        team_id: str,
        title: str,
        description: str,
        priority: int = 0,
        label_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue in Linear.

        Args:
            team_id: Team ID to create issue in
            title: Issue title
            description: Issue description
            priority: Priority (0=None, 1=Urgent, 2=High, 3=Medium, 4=Low)
            label_ids: Optional list of label IDs

        Returns:
            Created issue data
        """
        variables = {
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority
        }

        if label_ids:
            variables["labelIds"] = label_ids

        query = """
        mutation IssueCreate($teamId: String!, $title: String!, $description: String, $priority: Int, $labelIds: [String!]) {
            issueCreate(input: {
                teamId: $teamId
                title: $title
                description: $description
                priority: $priority
                labelIds: $labelIds
            }) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                }
            }
        }
        """

        result = await self.graphql_query(query, variables)
        return result["data"]["issueCreate"]["issue"]

    async def update_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        state_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Linear issue.

        Args:
            issue_id: Issue ID to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            state_id: New state ID (optional)

        Returns:
            Updated issue data
        """
        variables = {"issueId": issue_id}
        input_fields = []

        if title is not None:
            variables["title"] = title
            input_fields.append("title: $title")
        if description is not None:
            variables["description"] = description
            input_fields.append("description: $description")
        if priority is not None:
            variables["priority"] = priority
            input_fields.append("priority: $priority")
        if state_id is not None:
            variables["stateId"] = state_id
            input_fields.append("stateId: $stateId")

        query = f"""
        mutation IssueUpdate($issueId: String!, $title: String, $description: String, $priority: Int, $stateId: String) {{
            issueUpdate(id: $issueId, input: {{
                {", ".join(input_fields)}
            }}) {{
                success
                issue {{
                    id
                    identifier
                    title
                    url
                }}
            }}
        }}
        """

        result = await self.graphql_query(query, variables)
        return result["data"]["issueUpdate"]["issue"]


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    Exchange OAuth authorization code for access token.

    Args:
        code: OAuth authorization code from callback

    Returns:
        Token response with access_token
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINEAR_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINEAR_REDIRECT_URI,
                "client_id": LINEAR_CLIENT_ID,
                "client_secret": LINEAR_CLIENT_SECRET
            },
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def sync_issues_to_feedback(
    db: Session,
    access_token: str,
    team_id: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Sync Linear issues to Compass feedback.

    Args:
        db: Database session
        access_token: Linear OAuth access token
        team_id: Optional filter by team ID
        limit: Maximum issues to sync

    Returns:
        Sync results with count and details
    """
    connector = LinearConnector(access_token)

    # Get or create Linear source
    source = db.query(Source).filter(Source.name == "Linear").first()
    if not source:
        source = Source(
            name="Linear",
            source_type="real",
            is_active=True,
            config={"access_token": access_token}
        )
        db.add(source)
        db.commit()
        db.refresh(source)
    else:
        # Update access token
        source.config = {**source.config, "access_token": access_token}
        db.commit()

    # Fetch issues
    issues = await connector.get_issues(team_id=team_id, limit=limit)

    synced_count = 0
    new_count = 0
    updated_count = 0

    for issue in issues:
        # Check if issue already exists
        existing = db.query(Feedback).filter(
            Feedback.source_id == source.id,
            Feedback.source_metadata["linear_issue_id"].astext == issue["id"]
        ).first()

        if existing:
            # Update existing feedback
            existing.text = issue.get("description", "")
            existing.title = f'[{issue["identifier"]}] {issue["title"]}'
            existing.source_metadata = {
                **existing.source_metadata,
                "linear_issue_id": issue["id"],
                "linear_identifier": issue["identifier"],
                "linear_url": issue["url"],
                "linear_state": issue["state"]["name"],
                "linear_priority": issue["priorityLabel"],
                "linear_team": issue["team"]["name"],
                "updated_at": issue["updatedAt"]
            }
            updated_count += 1
        else:
            # Create new feedback
            feedback = Feedback(
                source_id=source.id,
                text=issue.get("description") or issue["title"],
                title=f'[{issue["identifier"]}] {issue["title"]}',
                customer_name=issue["creator"]["name"] if issue.get("creator") else "Unknown",
                submitted_at=datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00")),
                source_metadata={
                    "linear_issue_id": issue["id"],
                    "linear_identifier": issue["identifier"],
                    "linear_url": issue["url"],
                    "linear_state": issue["state"]["name"],
                    "linear_priority": issue["priorityLabel"],
                    "linear_team": issue["team"]["name"],
                    "linear_labels": [label["name"] for label in issue.get("labels", {}).get("nodes", [])],
                    "created_at": issue["createdAt"],
                    "updated_at": issue["updatedAt"]
                }
            )
            db.add(feedback)
            new_count += 1

        synced_count += 1

    db.commit()

    # Update source last_synced_at
    source.last_synced_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "synced": synced_count,
        "new": new_count,
        "updated": updated_count,
        "team_id": team_id,
        "limit": limit
    }


async def sync_issue_comments_to_feedback(
    db: Session,
    access_token: str,
    issue_id: str
) -> Dict[str, Any]:
    """
    Sync comments from a Linear issue to Compass feedback.

    Args:
        db: Database session
        access_token: Linear OAuth access token
        issue_id: Linear issue ID

    Returns:
        Sync results
    """
    connector = LinearConnector(access_token)

    # Get Linear source
    source = db.query(Source).filter(Source.name == "Linear").first()
    if not source:
        raise ValueError("Linear source not found. Connect Linear first.")

    # Fetch comments
    comments = await connector.get_issue_comments(issue_id)

    synced_count = 0

    for comment in comments:
        # Check if comment already exists
        existing = db.query(Feedback).filter(
            Feedback.source_id == source.id,
            Feedback.source_metadata["linear_comment_id"].astext == comment["id"]
        ).first()

        if not existing:
            # Create feedback from comment
            feedback = Feedback(
                source_id=source.id,
                text=comment["body"],
                title=f"Comment on Linear issue",
                customer_name=comment["user"]["name"],
                submitted_at=datetime.fromisoformat(comment["createdAt"].replace("Z", "+00:00")),
                source_metadata={
                    "linear_comment_id": comment["id"],
                    "linear_issue_id": issue_id,
                    "created_at": comment["createdAt"],
                    "updated_at": comment["updatedAt"]
                }
            )
            db.add(feedback)
            synced_count += 1

    db.commit()

    return {
        "success": True,
        "synced": synced_count,
        "issue_id": issue_id
    }


def get_oauth_url(state: Optional[str] = None) -> str:
    """
    Generate Linear OAuth authorization URL.

    Args:
        state: Optional state parameter for CSRF protection

    Returns:
        OAuth authorization URL
    """
    params = {
        "client_id": LINEAR_CLIENT_ID,
        "redirect_uri": LINEAR_REDIRECT_URI,
        "response_type": "code",
        "scope": "read,write"  # Request read and write permissions
    }

    if state:
        params["state"] = state

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{LINEAR_OAUTH_URL}?{query_string}"


async def test_connection(access_token: str) -> Dict[str, Any]:
    """
    Test Linear API connection and retrieve user info.

    Args:
        access_token: Linear OAuth access token

    Returns:
        Connection test results with user and teams info
    """
    connector = LinearConnector(access_token)

    try:
        viewer = await connector.get_viewer()
        teams = await connector.get_teams()

        return {
            "success": True,
            "connected": True,
            "user": viewer,
            "teams": teams,
            "team_count": len(teams)
        }
    except Exception as e:
        return {
            "success": False,
            "connected": False,
            "error": str(e)
        }
