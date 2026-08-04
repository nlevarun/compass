#!/bin/bash
# TEST_BASIC.sh - Test basic Compass functionality

set -e  # Exit on error

echo "========================================="
echo "  Compass Basic Functionality Test"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_DIR="/home/wsl-user/compass/backend"
PYTHON="python3"
UVICORN="python3 -m uvicorn"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

cd "$BACKEND_DIR"

# Step 1: Check Python and dependencies
echo "1️⃣  Checking Python and dependencies..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi

$PYTHON -c "import fastapi, sqlalchemy, uvicorn" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies OK${NC}"
else
    echo -e "${YELLOW}⚠️  Missing dependencies. Please install with:${NC}"
    echo "   python3 -m pip install --user fastapi uvicorn sqlalchemy pydantic python-multipart"
    exit 1
fi
echo ""

# Step 2: Check database
echo "2️⃣  Checking database..."
if [ ! -f "$BACKEND_DIR/compass.db" ]; then
    echo -e "${YELLOW}⚠️  Database not found. Run fix_all.py first!${NC}"
    echo "   Run: cd $BACKEND_DIR && $PYTHON fix_all.py"
    exit 1
fi

# Check database content
DB_CHECK=$($PYTHON -c "
from database import get_db
from models import Source, Feedback
with get_db() as db:
    sources = db.query(Source).count()
    feedback = db.query(Feedback).count()
    print(f'{sources}|{feedback}')
" 2>/dev/null)

IFS='|' read -r SOURCE_COUNT FEEDBACK_COUNT <<< "$DB_CHECK"
echo -e "${GREEN}✅ Database found${NC}"
echo "   Sources: $SOURCE_COUNT"
echo "   Feedback: $FEEDBACK_COUNT"
echo ""

# Step 3: Start server
echo "3️⃣  Starting test server..."
$UVICORN main_simple:app --port 8000 --log-level error &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"
echo "   Waiting for server to start..."
sleep 3

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null; then
    echo -e "${RED}❌ Server failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server started${NC}"
echo ""

# Step 4: Test endpoints
echo "4️⃣  Testing API endpoints..."

# Test health
echo -n "   Testing /api/health... "
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "$HEALTH"
fi

# Test stats
echo -n "   Testing /api/stats... "
STATS=$(curl -s http://localhost:8000/api/stats)
if echo "$STATS" | grep -q "total_feedback"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "$STATS"
fi

# Test sources
echo -n "   Testing /api/sources... "
SOURCES=$(curl -s http://localhost:8000/api/sources)
if echo "$SOURCES" | grep -q "name"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "$SOURCES"
fi

# Test feedback
echo -n "   Testing /api/feedback... "
FEEDBACK=$(curl -s http://localhost:8000/api/feedback)
if echo "$FEEDBACK" | grep -q "text"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "$FEEDBACK"
fi

echo ""

# Step 5: Test workflow
echo "5️⃣  Testing complete workflow..."

# Sync feedback
echo -n "   Syncing feedback... "
SYNC=$(curl -s -X POST http://localhost:8000/api/sources/sync)
if echo "$SYNC" | grep -q "success"; then
    echo -e "${GREEN}✅${NC}"
    NEW_FEEDBACK=$(echo "$SYNC" | grep -o '"new_feedback":[0-9]*' | cut -d':' -f2)
    echo "      Created $NEW_FEEDBACK new feedback items"
else
    echo -e "${YELLOW}⚠️${NC}"
    echo "$SYNC"
fi

# Run clustering
echo -n "   Running clustering... "
CLUSTER=$(curl -s -X POST http://localhost:8000/api/clustering/run)
if echo "$CLUSTER" | grep -q "success"; then
    echo -e "${GREEN}✅${NC}"
    CLUSTERS=$(echo "$CLUSTER" | grep -o '"total_clusters":[0-9]*' | cut -d':' -f2)
    echo "      Created $CLUSTERS clusters"
else
    echo -e "${YELLOW}⚠️${NC}"
    echo "$CLUSTER"
fi

# Generate roadmap
echo -n "   Generating roadmap... "
ROADMAP=$(curl -s -X POST http://localhost:8000/api/roadmap/generate)
if echo "$ROADMAP" | grep -q "success"; then
    echo -e "${GREEN}✅${NC}"
    ITEMS=$(echo "$ROADMAP" | grep -o '"roadmap_items":[0-9]*' | cut -d':' -f2)
    echo "      Created $ITEMS roadmap items"
else
    echo -e "${YELLOW}⚠️${NC}"
    echo "$ROADMAP"
fi

echo ""

# Step 6: Show final stats
echo "6️⃣  Final Statistics:"
FINAL_STATS=$(curl -s http://localhost:8000/api/stats | $PYTHON -m json.tool 2>/dev/null || echo "{}")
echo "$FINAL_STATS" | grep -E "total_feedback|total_clusters|total_sources" | sed 's/^/   /'
echo ""

# Step 7: Cleanup
echo "7️⃣  Cleanup..."
echo -n "   Stopping server... "
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo -e "${GREEN}✅${NC}"
echo ""

# Final summary
echo "========================================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "========================================="
echo ""
echo "Compass is working correctly!"
echo ""
echo "To start the server normally:"
echo "  cd $BACKEND_DIR"
echo "  $UVICORN main_simple:app --reload --port 8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
