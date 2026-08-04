#!/bin/bash
# Verification script for Linear OAuth integration

echo "=========================================="
echo "Linear Integration - Verification Check"
echo "=========================================="
echo ""

ERRORS=0

# Check backend files
echo "✓ Checking backend files..."
if [ -f "backend/connectors/linear.py" ]; then
    LINES=$(wc -l < backend/connectors/linear.py)
    echo "  ✓ backend/connectors/linear.py exists ($LINES lines)"
else
    echo "  ✗ backend/connectors/linear.py MISSING"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "# --- Linear OAuth Integration" backend/main.py; then
    echo "  ✓ Linear endpoints added to main.py"
else
    echo "  ✗ Linear endpoints NOT found in main.py"
    ERRORS=$((ERRORS + 1))
fi

# Check frontend files
echo ""
echo "✓ Checking frontend files..."
if [ -f "frontend/src/components/LinearConnector.jsx" ]; then
    LINES=$(wc -l < frontend/src/components/LinearConnector.jsx)
    echo "  ✓ LinearConnector.jsx exists ($LINES lines)"
else
    echo "  ✗ LinearConnector.jsx MISSING"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "import LinearConnector" frontend/src/App.jsx; then
    echo "  ✓ LinearConnector imported in App.jsx"
else
    echo "  ✗ LinearConnector NOT imported in App.jsx"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "<LinearConnector />" frontend/src/App.jsx; then
    echo "  ✓ LinearConnector used in App.jsx"
else
    echo "  ✗ LinearConnector NOT used in App.jsx"
    ERRORS=$((ERRORS + 1))
fi

# Check configuration
echo ""
echo "✓ Checking configuration..."
if grep -q "LINEAR_CLIENT_ID" .env.example; then
    echo "  ✓ Linear variables in .env.example"
else
    echo "  ✗ Linear variables NOT in .env.example"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "httpx" backend/requirements.txt; then
    echo "  ✓ httpx in requirements.txt"
else
    echo "  ✗ httpx NOT in requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

# Check documentation
echo ""
echo "✓ Checking documentation..."
DOC_FILES=(
    "LINEAR_QUICKSTART.md"
    "LINEAR_SETUP.md"
    "TEST_LINEAR.md"
    "LINEAR_INTEGRATION_README.md"
    "LINEAR_IMPLEMENTATION_SUMMARY.md"
    "LINEAR_QUICK_REFERENCE.md"
    "LINEAR_BUILD_COMPLETE.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        echo "  ✓ $file exists ($SIZE)"
    else
        echo "  ✗ $file MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

# Summary
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED - Integration Complete!"
    echo ""
    echo "Next steps:"
    echo "1. Read LINEAR_QUICKSTART.md for 5-minute setup"
    echo "2. Create Linear OAuth app"
    echo "3. Add credentials to .env"
    echo "4. Restart backend: ./start.sh"
    echo "5. Connect in UI at http://localhost:5173"
else
    echo "❌ $ERRORS ERRORS FOUND - Check above for details"
    exit 1
fi
echo "=========================================="
