"""
GitHub OAuth connector for fetching issues and comments as feedback.

Features:
- OAuth connection flow
- Fetch issues from repositories
- Fetch issue comments as feedback
- Track reactions as votes
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime


class GitHubConnector:
    """
    GitHub connector for OAuth-based issue tracking.

    Features:
    - OAuth authentication
    - Fetch repository issues
    - Fetch issue comments
    - Track reactions/votes
    """

    def __init__(self, access_token: str):
        """
        Initialize GitHub connector.

        Args:
            access_token: GitHub OAuth access token
        """
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def test_connection(self) -> bool:
        """
        Test if the access token is valid.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    async def get_user_info(self) -> Optional[Dict]:
        """
        Get authenticated user information.

        Returns:
            Dict with user info or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self.headers
                )
                if response.status_code == 200:
                    user = response.json()
                    return {
                        "id": user["id"],
                        "login": user["login"],
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "avatar_url": user.get("avatar_url")
                    }
        except Exception as e:
            print(f"Error fetching user info: {e}")
        return None

    async def get_repositories(self, limit: int = 100) -> List[Dict]:
        """
        Get list of repositories the user has access to.

        Args:
            limit: Maximum number of repositories to fetch

        Returns:
            List of repository dicts
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user/repos",
                    headers=self.headers,
                    params={
                        "per_page": min(limit, 100),
                        "sort": "updated",
                        "affiliation": "owner,collaborator,organization_member"
                    }
                )

                if response.status_code == 200:
                    repos = response.json()
                    return [
                        {
                            "id": repo["id"],
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "owner": repo["owner"]["login"],
                            "description": repo.get("description"),
                            "private": repo["private"],
                            "url": repo["html_url"],
                            "open_issues_count": repo["open_issues_count"]
                        }
                        for repo in repos
                    ]
        except Exception as e:
            print(f"Error fetching repositories: {e}")
        return []

    async def fetch_issues(
        self,
        repo_full_name: str,
        state: str = "all",
        labels: Optional[List[str]] = None,
        limit: int = 100,
        since: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch issues from a repository.

        Args:
            repo_full_name: Repository full name (e.g., "owner/repo")
            state: Issue state ("open", "closed", "all")
            labels: Filter by labels (optional)
            limit: Maximum number of issues to fetch
            since: Only issues updated after this timestamp (ISO 8601 format)

        Returns:
            List of issue dicts
        """
        try:
            params = {
                "state": state,
                "per_page": min(limit, 100),
                "sort": "updated",
                "direction": "desc"
            }

            if labels:
                params["labels"] = ",".join(labels)

            if since:
                params["since"] = since

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}/issues",
                    headers=self.headers,
                    params=params
                )

                if response.status_code == 200:
                    issues = response.json()
                    result = []

                    for issue in issues:
                        # Skip pull requests (they appear in issues endpoint)
                        if "pull_request" in issue:
                            continue

                        result.append({
                            "id": issue["id"],
                            "number": issue["number"],
                            "title": issue["title"],
                            "body": issue.get("body", ""),
                            "state": issue["state"],
                            "labels": [label["name"] for label in issue.get("labels", [])],
                            "user": {
                                "login": issue["user"]["login"],
                                "id": issue["user"]["id"],
                                "avatar_url": issue["user"]["avatar_url"]
                            },
                            "reactions": issue.get("reactions", {}),
                            "comments_count": issue["comments"],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"],
                            "url": issue["html_url"],
                            "api_url": issue["url"]
                        })

                    return result
        except Exception as e:
            print(f"Error fetching issues: {e}")
        return []

    async def fetch_issue_comments(
        self,
        repo_full_name: str,
        issue_number: int
    ) -> List[Dict]:
        """
        Fetch comments for a specific issue.

        Args:
            repo_full_name: Repository full name (e.g., "owner/repo")
            issue_number: Issue number

        Returns:
            List of comment dicts
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}/issues/{issue_number}/comments",
                    headers=self.headers
                )

                if response.status_code == 200:
                    comments = response.json()
                    return [
                        {
                            "id": comment["id"],
                            "body": comment["body"],
                            "user": {
                                "login": comment["user"]["login"],
                                "id": comment["user"]["id"]
                            },
                            "reactions": comment.get("reactions", {}),
                            "created_at": comment["created_at"],
                            "updated_at": comment["updated_at"]
                        }
                        for comment in comments
                    ]
        except Exception as e:
            print(f"Error fetching issue comments: {e}")
        return []

    async def get_total_reactions(self, reactions: Dict) -> int:
        """
        Calculate total reactions (votes) from GitHub reactions object.

        Args:
            reactions: GitHub reactions object

        Returns:
            Total number of reactions
        """
        return sum([
            reactions.get("+1", 0),
            reactions.get("-1", 0),
            reactions.get("laugh", 0),
            reactions.get("hooray", 0),
            reactions.get("confused", 0),
            reactions.get("heart", 0),
            reactions.get("rocket", 0),
            reactions.get("eyes", 0)
        ])


async def exchange_code_for_token(
    client_id: str,
    client_secret: str,
    code: str
) -> Optional[str]:
    """
    Exchange OAuth code for access token.

    Args:
        client_id: GitHub OAuth app client ID
        client_secret: GitHub OAuth app client secret
        code: OAuth authorization code

    Returns:
        Access token or None if failed
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json"
                },
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
    except Exception as e:
        print(f"Error exchanging code for token: {e}")
    return None


def get_oauth_url(client_id: str, redirect_uri: str, scope: str = "repo") -> str:
    """
    Generate GitHub OAuth authorization URL.

    Args:
        client_id: GitHub OAuth app client ID
        redirect_uri: OAuth redirect URI
        scope: OAuth scopes (default: "repo")

    Returns:
        OAuth authorization URL
    """
    return (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}"
    )
