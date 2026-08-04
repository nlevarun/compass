#!/bin/bash
# Slack OAuth Installation Script for Compass

set -e  # Exit on error

echo "=================================================="
echo "Compass - Slack OAuth Installation"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main_simple.py" ]; then
    echo "❌ Error: Please run this script from the compass directory"
    echo "   cd /home/wsl-user/compass && ./install_slack_oauth.sh"
    exit 1
fi

# Check Python installation
echo "1. Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "   ✅ $PYTHON_VERSION"

# Install Python dependencies
echo ""
echo "2. Installing Python dependencies..."
cd backend
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment..."
source venv/bin/activate

echo "   Installing packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "   ✅ Dependencies installed"

# Create .env file if it doesn't exist
cd ..
echo ""
echo "3. Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env
    echo "   ✅ Created .env file"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env and add your Slack credentials:"
    echo "      - SLACK_CLIENT_ID"
    echo "      - SLACK_CLIENT_SECRET"
    echo ""
    echo "   Get these from: https://api.slack.com/apps"
else
    echo "   ✅ .env file already exists"
fi

# Test OAuth configuration
echo ""
echo "4. Testing OAuth configuration..."
cd backend
source venv/bin/activate
python3 test_slack_oauth.py

# Summary
echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. If you haven't already, get Slack credentials:"
echo "   → https://api.slack.com/apps"
echo "   See SLACK_OAUTH_SETUP.md for detailed instructions"
echo ""
echo "2. Edit .env file with your credentials:"
echo "   → vim .env  (or your preferred editor)"
echo ""
echo "3. Start the backend server:"
echo "   → cd backend"
echo "   → source venv/bin/activate"
echo "   → python3 main_simple.py"
echo ""
echo "4. Start the frontend (in another terminal):"
echo "   → cd frontend"
echo "   → npm install"
echo "   → npm run dev"
echo ""
echo "5. Open http://localhost:5173 and click 'Connect Slack'!"
echo ""
echo "=================================================="
