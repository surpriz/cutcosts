#!/bin/bash

# ============================================================================
# Fix Alembic Version Table - Remove Ghost Migration Reference
# ============================================================================
#
# This script fixes the issue where the alembic_version table references
# a migration (004_payment_reminders) that no longer exists in the codebase.
#
# What it does:
#   1. Connect to production database
#   2. Check current alembic_version
#   3. Update to correct version (003_add_password_reset)
#
# Usage (run on VPS):
#   cd /opt/cloudwaste
#   bash deployment/fix-alembic-version.sh
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}         ${GREEN}🔧 FIX ALEMBIC VERSION TABLE${NC}                             ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Load environment variables
APP_DIR="/opt/cloudwaste"
ENV_FILE=".env.prod"

if [ ! -f "$ENV_FILE" ]; then
    print_error "File $ENV_FILE not found!"
    exit 1
fi

print_step "Loading environment variables..."
set -a
source "$ENV_FILE"
set +a
print_success "Environment loaded"

# Extract PostgreSQL connection details from DATABASE_URL
# Format: postgresql+asyncpg://user:password@host:port/dbname
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

print_step "Database connection details:"
echo "   • Host: $DB_HOST"
echo "   • Port: $DB_PORT"
echo "   • Database: $DB_NAME"
echo "   • User: $DB_USER"
echo ""

# Check current alembic_version
print_step "Checking current alembic_version..."
CURRENT_VERSION=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null | xargs || echo "none")

if [ "$CURRENT_VERSION" == "none" ]; then
    print_warning "No alembic_version found (fresh database)"
    print_step "Stamping database with latest version (003_add_password_reset)..."
    docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic stamp 003_add_password_reset
    print_success "Database stamped successfully"
else
    echo "   • Current version: $CURRENT_VERSION"
    echo ""

    # If version is 004_payment_reminders (the ghost migration), fix it
    if [ "$CURRENT_VERSION" == "004_payment_reminders" ]; then
        print_warning "Found ghost migration: 004_payment_reminders"
        print_step "Updating to correct version: 003_add_password_reset..."

        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME <<EOF
-- Update alembic_version to the correct latest migration
UPDATE alembic_version SET version_num = '003_add_password_reset';
EOF

        print_success "Alembic version updated to: 003_add_password_reset"
    else
        print_success "Alembic version is correct: $CURRENT_VERSION"
    fi
fi

# Verify fix
print_step "Verifying fix..."
NEW_VERSION=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT version_num FROM alembic_version;" | xargs)
echo "   • New version: $NEW_VERSION"

# Test migrations
print_step "Testing migrations (dry-run)..."
if docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic check 2>&1 | grep -q "Target database is up to date"; then
    print_success "Migrations are in sync!"
else
    print_warning "Migrations may need to be applied"
    print_step "Running migrations..."
    docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic upgrade head
    print_success "Migrations applied"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}         ${GREEN}✅ ALEMBIC VERSION FIXED${NC}                                 ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📋 Summary:${NC}"
echo "   • Old version: $CURRENT_VERSION"
echo "   • New version: $NEW_VERSION"
echo ""
echo -e "${GREEN}✅ Next steps:${NC}"
echo "   1. Run deployment: bash deployment/zero-downtime-deploy.sh"
echo "   2. Verify app is working: curl https://cutcosts.tech/api/v1/health"
echo ""
