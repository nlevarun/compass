#!/bin/bash
# Script to push Compass to GitHub

cd /home/wsl-user/compass

echo "🔄 Pushing Compass to GitHub..."
echo ""

# Check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI for authentication..."
    gh auth status || gh auth login
    git push -u origin main
else
    echo "GitHub CLI not found. Attempting git push with credentials..."
    echo ""
    echo "Note: You may need to enter your GitHub username and Personal Access Token"
    echo "Create a token at: https://github.com/settings/tokens"
    echo ""
    git push -u origin main
fi

echo ""
echo "✅ Push complete!"
