#!/bin/bash
# Quick setup script for macOS

set -e

echo "======================================"
echo "  Compass - macOS Setup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3.12 &> /dev/null; then
    echo "⚠️  Python 3.12 not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install python@3.12
    else
        echo "❌ Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
fi

echo "✓ Python 3.12 found"

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3.12 -m venv venv
    echo "✓ Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
echo "✓ Backend dependencies installed"

python database.py
echo "✓ Database initialized"

cd ..

# Frontend setup
echo ""
echo "Setting up frontend..."
cd frontend

if ! command -v npm &> /dev/null; then
    echo "⚠️  npm not found. Installing Node.js..."
    brew install node
fi

npm install
echo "✓ Frontend dependencies installed"

cd ..

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "To start Compass:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
