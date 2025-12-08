#!/bin/bash

# ============================================================================
# CloudWaste - Smoke Tests Script
# ============================================================================
#
# This script performs quick smoke tests to verify that the deployed
# application is functioning correctly. Run after deployment to catch
# any obvious issues.
#
# Usage:
#   bash deployment/smoke-tests.sh [BASE_URL]
#
# Examples:
#   bash deployment/smoke-tests.sh                          # Default: https://cutcosts.tech
#   bash deployment/smoke-tests.sh http://localhost:3000    # Local staging
#   bash deployment/smoke-tests.sh https://staging.cutcosts.tech
#
# Exit codes:
#   0 - All smoke tests passed
#   1 - One or more critical tests failed
#
# ============================================================================

set -e

# Configuration
BASE_URL="${1:-https://cutcosts.tech}"
TIMEOUT=10
FAILED=0
PASSED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED=$((PASSED + 1))
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              🧪 SMOKE TESTS POST-DÉPLOIEMENT                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Testing: $BASE_URL"
echo ""

# ============================================================================
# Test 1: Frontend Accessibility
# ============================================================================

echo "📋 Test 1: Frontend Accessibility"

FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL" 2>/dev/null || echo "000")

if [ "$FRONTEND_STATUS" == "200" ] || [ "$FRONTEND_STATUS" == "304" ]; then
    print_pass "Frontend accessible (HTTP $FRONTEND_STATUS)"
else
    print_fail "Frontend not accessible (HTTP $FRONTEND_STATUS)"
fi

# ============================================================================
# Test 2: API Health Check
# ============================================================================

echo ""
echo "📋 Test 2: API Health Check"

HEALTH_RESPONSE=$(curl -s --max-time $TIMEOUT "$BASE_URL/api/v1/health" 2>/dev/null || echo '{"status":"error"}')
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "error")

if [ "$HEALTH_STATUS" == "healthy" ]; then
    print_pass "API health check passed (status: healthy)"
else
    print_fail "API health check failed (status: $HEALTH_STATUS)"
    print_info "Response: $HEALTH_RESPONSE"
fi

# ============================================================================
# Test 3: API Docs Accessibility
# ============================================================================

echo ""
echo "📋 Test 3: API Documentation"

DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/api/docs" 2>/dev/null || echo "000")

if [ "$DOCS_STATUS" == "200" ] || [ "$DOCS_STATUS" == "307" ]; then
    print_pass "API docs accessible (HTTP $DOCS_STATUS)"
else
    print_fail "API docs not accessible (HTTP $DOCS_STATUS)"
fi

# ============================================================================
# Test 4: Login Page Accessibility
# ============================================================================

echo ""
echo "📋 Test 4: Login Page"

LOGIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/auth/login" 2>/dev/null || echo "000")

if [ "$LOGIN_STATUS" == "200" ] || [ "$LOGIN_STATUS" == "304" ]; then
    print_pass "Login page accessible (HTTP $LOGIN_STATUS)"
else
    print_fail "Login page not accessible (HTTP $LOGIN_STATUS)"
fi

# ============================================================================
# Test 5: Register Page Accessibility
# ============================================================================

echo ""
echo "📋 Test 5: Register Page"

REGISTER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/auth/register" 2>/dev/null || echo "000")

if [ "$REGISTER_STATUS" == "200" ] || [ "$REGISTER_STATUS" == "304" ]; then
    print_pass "Register page accessible (HTTP $REGISTER_STATUS)"
else
    print_fail "Register page not accessible (HTTP $REGISTER_STATUS)"
fi

# ============================================================================
# Test 6: Static Assets (CSS/JS)
# ============================================================================

echo ""
echo "📋 Test 6: Static Assets"

# Check if Next.js is serving static files (look for _next in response)
STATIC_CHECK=$(curl -s --max-time $TIMEOUT "$BASE_URL" 2>/dev/null | grep -c "_next" || echo "0")

if [ "$STATIC_CHECK" -gt 0 ]; then
    print_pass "Static assets (_next) are being served"
else
    print_warn "Could not verify static assets"
fi

# ============================================================================
# Test 7: CORS Headers (Optional)
# ============================================================================

echo ""
echo "📋 Test 7: CORS Headers"

CORS_HEADERS=$(curl -s -I --max-time $TIMEOUT "$BASE_URL/api/v1/health" 2>/dev/null | grep -i "access-control" || echo "")

if [ -n "$CORS_HEADERS" ]; then
    print_pass "CORS headers present"
else
    print_warn "CORS headers not detected (may be normal for same-origin)"
fi

# ============================================================================
# Test 8: SSL Certificate (if HTTPS)
# ============================================================================

echo ""
echo "📋 Test 8: SSL Certificate"

if [[ "$BASE_URL" == https://* ]]; then
    SSL_CHECK=$(curl -s -o /dev/null -w "%{ssl_verify_result}" --max-time $TIMEOUT "$BASE_URL" 2>/dev/null || echo "1")

    if [ "$SSL_CHECK" == "0" ]; then
        print_pass "SSL certificate valid"
    else
        print_fail "SSL certificate issue (code: $SSL_CHECK)"
    fi
else
    print_info "Skipping SSL check (not using HTTPS)"
fi

# ============================================================================
# Test 9: Response Time
# ============================================================================

echo ""
echo "📋 Test 9: Response Time"

RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" --max-time $TIMEOUT "$BASE_URL/api/v1/health" 2>/dev/null || echo "999")
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc 2>/dev/null | cut -d. -f1 || echo "999")

if [ "$RESPONSE_TIME_MS" -lt 1000 ]; then
    print_pass "API response time: ${RESPONSE_TIME_MS}ms (< 1s)"
elif [ "$RESPONSE_TIME_MS" -lt 3000 ]; then
    print_warn "API response time: ${RESPONSE_TIME_MS}ms (< 3s, but slow)"
else
    print_fail "API response time: ${RESPONSE_TIME_MS}ms (> 3s, too slow)"
fi

# ============================================================================
# Test 10: Error Handling
# ============================================================================

echo ""
echo "📋 Test 10: Error Handling (404)"

NOT_FOUND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/api/v1/this-endpoint-should-not-exist" 2>/dev/null || echo "000")

if [ "$NOT_FOUND_STATUS" == "404" ]; then
    print_pass "404 error handling works correctly"
elif [ "$NOT_FOUND_STATUS" == "422" ]; then
    print_pass "API returns validation error for invalid routes"
else
    print_warn "Unexpected response for non-existent endpoint (HTTP $NOT_FOUND_STATUS)"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

TOTAL=$((PASSED + FAILED))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SMOKE TESTS PASSED${NC}"
    echo "   $PASSED/$TOTAL tests passed"
    echo ""
    echo "   Application is ready for use!"
    exit 0
else
    echo -e "${RED}❌ SMOKE TESTS FAILED${NC}"
    echo "   $PASSED passed, $FAILED failed (total: $TOTAL)"
    echo ""
    echo "   Review the failed tests above and check application logs."
    exit 1
fi
