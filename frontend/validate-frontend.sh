#!/bin/bash

# Frontend Validation Script
# Checks that all required files and dependencies are in place

echo "🔍 Compass Frontend Validation"
echo "=============================="
echo ""

ERRORS=0
WARNINGS=0

# Check Node.js
echo "✓ Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "  ✓ Node.js installed: $NODE_VERSION"
else
    echo "  ✗ Node.js not found! Please install Node.js"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
echo "✓ Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo "  ✓ npm installed: $NPM_VERSION"
else
    echo "  ✗ npm not found! Please install npm"
    ERRORS=$((ERRORS + 1))
fi

# Check package.json
echo "✓ Checking package.json..."
if [ -f "package.json" ]; then
    echo "  ✓ package.json exists"
else
    echo "  ✗ package.json not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check node_modules
echo "✓ Checking node_modules..."
if [ -d "node_modules" ]; then
    echo "  ✓ node_modules directory exists"
else
    echo "  ⚠ node_modules not found. Run 'npm install'"
    WARNINGS=$((WARNINGS + 1))
fi

# Check required source files
echo "✓ Checking source files..."
REQUIRED_FILES=(
    "src/main.jsx"
    "src/App.jsx"
    "src/index.css"
    "src/services/api.js"
    "src/services/websocket.js"
    "src/components/Dashboard.jsx"
    "src/components/FeedbackInbox.jsx"
    "src/components/ClusterView.jsx"
    "src/components/RoadmapDashboard.jsx"
    "src/components/PriorityAnalysis.jsx"
    "src/components/ErrorBoundary.jsx"
    "src/components/Toast.jsx"
    "src/components/OfflineBanner.jsx"
    "src/components/InstallPrompt.jsx"
    "src/hooks/useOnlineStatus.js"
    "src/hooks/usePWAInstall.js"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file missing!"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for .env configuration
echo "✓ Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✓ .env file exists"
    if grep -q "VITE_API_URL" .env; then
        echo "  ✓ VITE_API_URL configured"
    else
        echo "  ⚠ VITE_API_URL not found in .env"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "  ⚠ .env file not found (will use defaults)"
    if [ -f ".env.example" ]; then
        echo "  ℹ Copy .env.example to .env to customize settings"
    fi
    WARNINGS=$((WARNINGS + 1))
fi

# Check index.html
echo "✓ Checking index.html..."
if [ -f "index.html" ]; then
    echo "  ✓ index.html exists"
else
    echo "  ✗ index.html not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check for common issues
echo "✓ Checking for common issues..."

# Check if React is installed
if [ -d "node_modules" ] && [ -d "node_modules/react" ]; then
    echo "  ✓ React is installed"
else
    echo "  ⚠ React not installed. Run 'npm install'"
    WARNINGS=$((WARNINGS + 1))
fi

# Check if axios is installed
if [ -d "node_modules" ] && [ -d "node_modules/axios" ]; then
    echo "  ✓ Axios is installed"
else
    echo "  ⚠ Axios not installed. Run 'npm install'"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "=============================="
echo "Validation Summary"
echo "=============================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✓ All checks passed! Frontend is ready to run."
    echo ""
    echo "To start the development server:"
    echo "  npm run dev"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠ $WARNINGS warning(s) found, but frontend should work."
    echo ""
    echo "To start the development server:"
    echo "  npm run dev"
    exit 0
else
    echo "✗ $ERRORS error(s) and $WARNINGS warning(s) found."
    echo ""
    echo "Please fix the errors above before running the frontend."
    exit 1
fi
