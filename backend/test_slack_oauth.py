#!/usr/bin/env python3
"""
Quick test script to verify Slack OAuth configuration.

Usage:
    python test_slack_oauth.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_oauth_config():
    """Test if Slack OAuth is properly configured."""
    print("=" * 60)
    print("Slack OAuth Configuration Test")
    print("=" * 60)
    print()

    # Check environment variables
    client_id = os.getenv("SLACK_CLIENT_ID", "")
    client_secret = os.getenv("SLACK_CLIENT_SECRET", "")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI", "")

    errors = []
    warnings = []

    # Test Client ID
    print("1. Testing SLACK_CLIENT_ID...")
    if not client_id:
        errors.append("SLACK_CLIENT_ID is not set")
        print("   ❌ NOT SET")
    elif not client_id.count(".") == 1:
        warnings.append("SLACK_CLIENT_ID format looks incorrect (should be like: 1234567890.1234567890)")
        print(f"   ⚠️  SET but format looks wrong: {client_id[:20]}...")
    else:
        print(f"   ✅ SET: {client_id[:20]}...")

    # Test Client Secret
    print("\n2. Testing SLACK_CLIENT_SECRET...")
    if not client_secret:
        errors.append("SLACK_CLIENT_SECRET is not set")
        print("   ❌ NOT SET")
    elif len(client_secret) < 20:
        warnings.append("SLACK_CLIENT_SECRET seems too short")
        print(f"   ⚠️  SET but seems short (length: {len(client_secret)})")
    else:
        print(f"   ✅ SET (length: {len(client_secret)})")

    # Test Redirect URI
    print("\n3. Testing SLACK_REDIRECT_URI...")
    if not redirect_uri:
        warnings.append("SLACK_REDIRECT_URI not set (will use default)")
        print("   ⚠️  NOT SET (will use default: http://localhost:8000/api/auth/slack/callback)")
    elif not redirect_uri.startswith("http"):
        errors.append("SLACK_REDIRECT_URI must start with http:// or https://")
        print(f"   ❌ INVALID: {redirect_uri}")
    elif not "/api/auth/slack/callback" in redirect_uri:
        warnings.append("SLACK_REDIRECT_URI should end with /api/auth/slack/callback")
        print(f"   ⚠️  SET but path looks wrong: {redirect_uri}")
    else:
        print(f"   ✅ SET: {redirect_uri}")

    # Test slack-sdk installation
    print("\n4. Testing slack-sdk installation...")
    try:
        from slack_sdk import WebClient
        from slack_sdk.oauth import AuthorizeUrlGenerator
        print("   ✅ slack-sdk is installed")
    except ImportError as e:
        errors.append("slack-sdk is not installed")
        print(f"   ❌ NOT INSTALLED: {e}")
        print("      Run: pip install slack-sdk")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if errors:
        print("\n❌ ERRORS (must fix):")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print("\n⚠️  WARNINGS (should review):")
        for warning in warnings:
            print(f"   • {warning}")

    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nYou're ready to use Slack OAuth!")
        print("Start the backend and click 'Connect Slack' in the UI.")
    elif not errors:
        print("\n⚠️  Configuration is functional but has warnings.")
        print("Review the warnings above, but OAuth should work.")
    else:
        print("\n❌ Configuration has errors that must be fixed.")
        print("\nQuick fix:")
        print("1. Copy .env.example to .env")
        print("2. Get credentials from https://api.slack.com/apps")
        print("3. Add SLACK_CLIENT_ID and SLACK_CLIENT_SECRET to .env")
        print("4. Run this test again")

    print("\n" + "=" * 60)
    print("For detailed setup instructions, see: SLACK_OAUTH_SETUP.md")
    print("=" * 60)

    return len(errors) == 0


if __name__ == "__main__":
    success = test_oauth_config()
    exit(0 if success else 1)
