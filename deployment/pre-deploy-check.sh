#!/bin/bash

# ============================================================================
# CloudWaste - Pre-Deploy Check Script
# ============================================================================
#
# This script validates critical environment variables and configuration
# before allowing deployment to proceed. It helps catch common DEV/PROD
# configuration mismatches.
#
# Usage:
#   cd /opt/cloudwaste
#   bash deployment/pre-deploy-check.sh
#
# Exit codes:
#   0 - All checks passed
#   1 - Critical check failed (deployment should abort)
#   2 - Warning (deployment can proceed with caution)
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

print_check() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🔍 PRE-DEPLOY ENVIRONMENT CHECK                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# Check 1: Critical Environment Variables
# ============================================================================

echo "📋 Checking critical environment variables..."

# Database URL
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL is not set"
else
    print_check "DATABASE_URL is set"
fi

# Secret Key
if [ -z "$SECRET_KEY" ]; then
    print_error "SECRET_KEY is not set"
else
    if [ ${#SECRET_KEY} -lt 32 ]; then
        print_warning "SECRET_KEY seems too short (< 32 chars)"
    else
        print_check "SECRET_KEY is set"
    fi
fi

# JWT Secret
if [ -z "$JWT_SECRET_KEY" ]; then
    print_error "JWT_SECRET_KEY is not set"
else
    print_check "JWT_SECRET_KEY is set"
fi

# Encryption Key
if [ -z "$ENCRYPTION_KEY" ]; then
    print_error "ENCRYPTION_KEY is not set"
else
    print_check "ENCRYPTION_KEY is set"
fi

# CORS Origins
if [ -z "$ALLOWED_ORIGINS" ]; then
    print_error "ALLOWED_ORIGINS is not set"
else
    if [[ "$ALLOWED_ORIGINS" == *"cutcosts.tech"* ]]; then
        print_check "ALLOWED_ORIGINS contains cutcosts.tech"
    else
        print_warning "ALLOWED_ORIGINS does not contain cutcosts.tech"
        echo "         Current value: $ALLOWED_ORIGINS"
    fi
fi

echo ""

# ============================================================================
# Check 2: Sentry Configuration (Critical for Frontend)
# ============================================================================

echo "📋 Checking Sentry configuration..."

if [ -z "$NEXT_PUBLIC_SENTRY_DSN" ]; then
    print_warning "NEXT_PUBLIC_SENTRY_DSN is not set (frontend errors won't be tracked)"
else
    print_check "NEXT_PUBLIC_SENTRY_DSN is set"
fi

if [ -z "$SENTRY_DSN" ]; then
    print_warning "SENTRY_DSN is not set (backend errors won't be tracked)"
else
    print_check "SENTRY_DSN is set"
fi

echo ""

# ============================================================================
# Check 3: Debug Mode (MUST be False in production)
# ============================================================================

echo "📋 Checking debug mode..."

if [ "$DEBUG" == "True" ] || [ "$DEBUG" == "true" ] || [ "$DEBUG" == "1" ]; then
    print_error "DEBUG is enabled! Must be False in production"
else
    print_check "DEBUG is disabled (correct for production)"
fi

echo ""

# ============================================================================
# Check 4: Required Files
# ============================================================================

echo "📋 Checking required files..."

if [ -f ".env.prod" ]; then
    print_check ".env.prod exists"
else
    print_error ".env.prod not found"
fi

if [ -f "deployment/docker-compose.prod.yml" ]; then
    print_check "docker-compose.prod.yml exists"
else
    print_error "docker-compose.prod.yml not found"
fi

if [ -f "deployment/zero-downtime-deploy.sh" ]; then
    print_check "zero-downtime-deploy.sh exists"
else
    print_error "zero-downtime-deploy.sh not found"
fi

echo ""

# ============================================================================
# Check 5: Docker Status
# ============================================================================

echo "📋 Checking Docker status..."

if command -v docker &> /dev/null; then
    print_check "Docker is installed"

    if docker info &> /dev/null; then
        print_check "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
    fi
else
    print_error "Docker is not installed"
fi

echo ""

# ============================================================================
# Check 6: Disk Space
# ============================================================================

echo "📋 Checking disk space..."

DISK_USAGE=$(df /opt/cloudwaste 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")

if [ "$DISK_USAGE" -gt 90 ]; then
    print_error "Disk usage is critical: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -gt 80 ]; then
    print_warning "Disk usage is high: ${DISK_USAGE}%"
else
    print_check "Disk space OK: ${DISK_USAGE}% used"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo "════════════════════════════════════════════════════════════════════"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Pre-deploy check FAILED${NC}"
    echo "   $ERRORS error(s), $WARNINGS warning(s)"
    echo ""
    echo "   Fix the errors above before deploying."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Pre-deploy check passed with warnings${NC}"
    echo "   0 error(s), $WARNINGS warning(s)"
    echo ""
    echo "   Deployment can proceed, but review warnings above."
    exit 0
else
    echo -e "${GREEN}✅ Pre-deploy check PASSED${NC}"
    echo "   All checks passed successfully."
    exit 0
fi
