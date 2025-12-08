#!/bin/bash

# ============================================================================
# CloudWaste - Local Staging Test Script
# ============================================================================
#
# This script launches a local staging environment that mirrors production,
# runs smoke tests, and cleans up afterward.
#
# Use this to verify your changes work in a production-like environment
# BEFORE pushing to master.
#
# Usage:
#   cd /path/to/CloudWaste
#   bash deployment/test-staging.sh
#
# Options:
#   --no-cleanup    Don't tear down the environment after tests
#   --rebuild       Force rebuild of Docker images
#   --quick         Skip waiting for frontend (faster but less thorough)
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
NO_CLEANUP=false
REBUILD=""
QUICK=false

for arg in "$@"; do
    case $arg in
        --no-cleanup)
            NO_CLEANUP=true
            ;;
        --rebuild)
            REBUILD="--build --no-cache"
            ;;
        --quick)
            QUICK=true
            ;;
    esac
done

COMPOSE_FILE="deployment/docker-compose.staging.yml"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🧪 LOCAL STAGING ENVIRONMENT TEST                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================

echo -e "${BLUE}📋 Step 1: Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}✗${NC} Docker daemon is not running"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is ready"

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}✗${NC} Compose file not found: $COMPOSE_FILE"
    exit 1
fi

echo -e "${GREEN}✓${NC} Compose file found"
echo ""

# ============================================================================
# Step 2: Stop Any Existing Staging Containers
# ============================================================================

echo -e "${BLUE}📋 Step 2: Cleaning up any existing staging containers...${NC}"

docker compose -f "$COMPOSE_FILE" down --volumes 2>/dev/null || true

echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# ============================================================================
# Step 3: Build and Start Staging Environment
# ============================================================================

echo -e "${BLUE}📋 Step 3: Building and starting staging environment...${NC}"
echo -e "${YELLOW}⚠${NC} This may take several minutes on first run..."
echo ""

if [ -n "$REBUILD" ]; then
    echo "Force rebuilding images..."
    docker compose -f "$COMPOSE_FILE" build --no-cache
fi

docker compose -f "$COMPOSE_FILE" up -d --build

echo ""
echo -e "${GREEN}✓${NC} Containers started"
echo ""

# ============================================================================
# Step 4: Wait for Services to be Ready
# ============================================================================

echo -e "${BLUE}📋 Step 4: Waiting for services to be ready...${NC}"

# Function to check if a service is healthy
wait_for_service() {
    local service_name=$1
    local container_name=$2
    local max_attempts=$3
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "unknown")

        if [ "$STATUS" == "healthy" ]; then
            echo -e "${GREEN}✓${NC} $service_name is healthy"
            return 0
        fi

        echo "   Waiting for $service_name... (attempt $attempt/$max_attempts, status: $STATUS)"
        sleep 5
        attempt=$((attempt + 1))
    done

    echo -e "${RED}✗${NC} $service_name failed to become healthy"
    return 1
}

# Wait for database
wait_for_service "PostgreSQL" "staging_postgres" 12

# Wait for Redis
wait_for_service "Redis" "staging_redis" 12

# Wait for backend
wait_for_service "Backend API" "staging_backend" 24

# Wait for frontend (takes longest)
if [ "$QUICK" != true ]; then
    wait_for_service "Frontend" "staging_frontend" 36
else
    echo -e "${YELLOW}⚠${NC} Skipping frontend wait (--quick mode)"
fi

echo ""

# ============================================================================
# Step 5: Run Smoke Tests
# ============================================================================

echo -e "${BLUE}📋 Step 5: Running smoke tests...${NC}"
echo ""

# Give services a moment to stabilize
sleep 5

# Run smoke tests
if bash deployment/smoke-tests.sh http://localhost:3000; then
    TESTS_PASSED=true
else
    TESTS_PASSED=false
fi

echo ""

# ============================================================================
# Step 6: Show Container Status
# ============================================================================

echo -e "${BLUE}📋 Step 6: Container status...${NC}"
echo ""

docker compose -f "$COMPOSE_FILE" ps

echo ""

# ============================================================================
# Step 7: Cleanup (unless --no-cleanup)
# ============================================================================

if [ "$NO_CLEANUP" = true ]; then
    echo -e "${YELLOW}ℹ${NC} Skipping cleanup (--no-cleanup flag)"
    echo ""
    echo "To manually clean up later:"
    echo "  docker compose -f $COMPOSE_FILE down -v"
    echo ""
    echo "To view logs:"
    echo "  docker compose -f $COMPOSE_FILE logs -f"
    echo ""
else
    echo -e "${BLUE}📋 Step 7: Cleaning up staging environment...${NC}"
    docker compose -f "$COMPOSE_FILE" down -v
    echo -e "${GREEN}✓${NC} Cleanup complete"
    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo "════════════════════════════════════════════════════════════════════"
echo ""

if [ "$TESTS_PASSED" = true ]; then
    echo -e "${GREEN}✅ STAGING TESTS PASSED${NC}"
    echo ""
    echo "Your changes are ready for production!"
    echo ""
    echo "Next steps:"
    echo "  1. Commit your changes"
    echo "  2. Push to master: git push origin master"
    echo "  3. GitHub Actions will run CI tests and deploy automatically"
    echo ""
    exit 0
else
    echo -e "${RED}❌ STAGING TESTS FAILED${NC}"
    echo ""
    echo "Fix the issues before pushing to production."
    echo ""
    echo "Debugging tips:"
    echo "  # View logs"
    echo "  docker compose -f $COMPOSE_FILE logs -f"
    echo ""
    echo "  # Check specific service"
    echo "  docker compose -f $COMPOSE_FILE logs backend"
    echo "  docker compose -f $COMPOSE_FILE logs frontend"
    echo ""
    echo "  # Run staging without cleanup for debugging"
    echo "  bash deployment/test-staging.sh --no-cleanup"
    echo ""
    exit 1
fi
