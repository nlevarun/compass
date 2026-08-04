#!/bin/bash

# Webhook System Integration Test
# Tests all webhook endpoints without requiring external services

set -e

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0

echo "=================================="
echo "Compass Webhook System Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))

        # Show processing time if available
        if echo "$body" | grep -q "processing_time_ms"; then
            latency=$(echo "$body" | grep -o '"processing_time_ms":[0-9.]*' | grep -o '[0-9.]*')
            echo "  → Latency: ${latency}ms"
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $http_code)"
        FAILED=$((FAILED + 1))
        echo "  Response: $body"
    fi
}

echo "1. Testing Backend Health"
echo "-------------------------"
test_endpoint "API Docs" "$BASE_URL/docs" 200
test_endpoint "API Root" "$BASE_URL/" 200
echo ""

echo "2. Testing Webhook Receivers"
echo "----------------------------"
test_endpoint "Slack Test Endpoint" "$BASE_URL/webhooks/slack/test"
test_endpoint "GitHub Test Endpoint" "$BASE_URL/webhooks/github/test"
test_endpoint "Intercom Test Endpoint" "$BASE_URL/webhooks/intercom/test"
echo ""

echo "3. Testing Setup Guides"
echo "----------------------"
test_endpoint "Slack Setup Guide" "$BASE_URL/webhooks/slack/setup-guide"
test_endpoint "GitHub Setup Guide" "$BASE_URL/webhooks/github/setup-guide"
test_endpoint "Intercom Setup Guide" "$BASE_URL/webhooks/intercom/setup-guide"
echo ""

echo "4. Performance Benchmark"
echo "-----------------------"
echo "Running 10 concurrent webhook requests..."

start_time=$(date +%s%N)
for i in {1..10}; do
    curl -s "$BASE_URL/webhooks/slack/test" > /dev/null &
done
wait
end_time=$(date +%s%N)

elapsed_ms=$(( (end_time - start_time) / 1000000 ))
avg_latency=$(( elapsed_ms / 10 ))

echo -e "${GREEN}✓ Complete${NC}"
echo "  → Total time: ${elapsed_ms}ms"
echo "  → Average latency: ${avg_latency}ms per request"

if [ $avg_latency -lt 500 ]; then
    echo -e "  → ${GREEN}Excellent performance! (<500ms)${NC}"
    PASSED=$((PASSED + 1))
elif [ $avg_latency -lt 1000 ]; then
    echo -e "  → ${YELLOW}Good performance (500-1000ms)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "  → ${RED}Slow performance (>1000ms)${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""

echo "=================================="
echo "Test Results"
echo "=================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Your webhook system is ready to use! 🎉"
    echo ""
    echo "Next steps:"
    echo "  1. Configure external services (Slack/GitHub/Intercom)"
    echo "  2. Set environment variables (signing secrets)"
    echo "  3. Test with real webhooks"
    echo ""
    echo "See QUICKSTART_WEBHOOKS.md for setup instructions."
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Is the backend running? (python main.py)"
    echo "  - Check backend logs for errors"
    echo "  - Verify database is migrated (python migrate_webhook_tables.py)"
    exit 1
fi
