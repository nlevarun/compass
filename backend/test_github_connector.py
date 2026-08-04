#!/usr/bin/env python3
"""
Test script for GitHub OAuth connector.

Tests:
1. OAuth URL generation
2. Token exchange (requires actual OAuth flow)
3. Connection test
4. Repository listing
5. Issue fetching
6. Comment fetching
"""

import asyncio
from connectors.github import (
    GitHubConnector,
    get_oauth_url,
    exchange_code_for_token
)


async def test_oauth_url():
    """Test OAuth URL generation."""
    print("\n1. Testing OAuth URL generation...")
    client_id = "test_client_id"
    redirect_uri = "http://localhost:3000/oauth/github/callback"

    oauth_url = get_oauth_url(client_id, redirect_uri, scope="repo")

    assert "github.com/login/oauth/authorize" in oauth_url
    assert client_id in oauth_url
    assert redirect_uri in oauth_url
    print(f"   ✓ OAuth URL generated: {oauth_url}")


async def test_connector_with_token(access_token: str):
    """Test connector with real access token."""
    print("\n2. Testing GitHub connector with access token...")

    connector = GitHubConnector(access_token)

    # Test connection
    print("   Testing connection...")
    connected = await connector.test_connection()
    if not connected:
        print("   ✗ Connection failed - invalid token")
        return False
    print("   ✓ Connection successful")

    # Get user info
    print("   Fetching user info...")
    user_info = await connector.get_user_info()
    if user_info:
        print(f"   ✓ User: {user_info.get('login')} ({user_info.get('name')})")
    else:
        print("   ✗ Failed to fetch user info")

    # Get repositories
    print("   Fetching repositories...")
    repos = await connector.get_repositories(limit=5)
    print(f"   ✓ Found {len(repos)} repositories")
    if repos:
        print("   First few repositories:")
        for repo in repos[:3]:
            print(f"      - {repo['full_name']} ({repo['open_issues_count']} open issues)")

    # Test fetching issues from first repo (if any)
    if repos:
        first_repo = repos[0]['full_name']
        print(f"\n   Fetching issues from {first_repo}...")
        issues = await connector.fetch_issues(first_repo, limit=5)
        print(f"   ✓ Found {len(issues)} issues")

        if issues:
            print("   First few issues:")
            for issue in issues[:3]:
                print(f"      #{issue['number']}: {issue['title']}")
                print(f"         Comments: {issue['comments_count']}, State: {issue['state']}")

                # Test fetching comments for first issue
                if issue['comments_count'] > 0:
                    print(f"      Fetching comments for issue #{issue['number']}...")
                    comments = await connector.fetch_issue_comments(first_repo, issue['number'])
                    print(f"      ✓ Found {len(comments)} comments")
                    if comments:
                        print(f"         First comment by {comments[0]['user']['login']}")

    return True


async def main():
    """Main test function."""
    print("=" * 60)
    print("GitHub OAuth Connector Test Suite")
    print("=" * 60)

    # Test 1: OAuth URL generation (no token needed)
    await test_oauth_url()

    # Test 2: Real connector functionality (requires token)
    print("\n" + "=" * 60)
    print("To test with a real GitHub token:")
    print("1. Create a GitHub OAuth App at:")
    print("   https://github.com/settings/developers")
    print("2. Get a personal access token at:")
    print("   https://github.com/settings/tokens")
    print("3. Run: python test_github_connector.py <YOUR_TOKEN>")
    print("=" * 60)

    # Check if token provided as command line argument
    import sys
    if len(sys.argv) > 1:
        access_token = sys.argv[1]
        success = await test_connector_with_token(access_token)
        if success:
            print("\n✓ All tests passed!")
        else:
            print("\n✗ Some tests failed")
    else:
        print("\nSkipping live tests (no token provided)")
        print("Run with token: python test_github_connector.py YOUR_TOKEN")


if __name__ == "__main__":
    asyncio.run(main())
