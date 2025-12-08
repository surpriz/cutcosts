#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory (works from anywhere)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "CutCosts Azure Resources Status"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    echo "Expected location: $PROJECT_DIR/.env"
    exit 1
fi

# Source .env
source "$PROJECT_DIR/.env"

# Export batch control variables from .env
export TF_VAR_enable_batch_1="${TF_VAR_enable_batch_1:-true}"
export TF_VAR_enable_batch_2="${TF_VAR_enable_batch_2:-false}"
export TF_VAR_enable_batch_3="${TF_VAR_enable_batch_3:-false}"

# Change to terraform directory
cd "$PROJECT_DIR/terraform"

# Check if terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo -e "${YELLOW}⚠ No terraform state found${NC}"
    echo "No resources have been created yet"
    echo "Run: ./scripts/create.sh"
    exit 0
fi

# Check Azure login
echo "Checking Azure login..."
if ! az account show &> /dev/null; then
    echo -e "${RED}✗ Not logged in to Azure${NC}"
    echo "Please login with: az login --tenant $ARM_TENANT_ID"
    exit 1
fi

# Verify correct subscription
CURRENT_SUB=$(az account show --query id -o tsv 2>/dev/null)
if [ "$CURRENT_SUB" != "$ARM_SUBSCRIPTION_ID" ]; then
    az account set --subscription "$ARM_SUBSCRIPTION_ID"
fi

# Get terraform outputs
echo "Fetching resource information..."
echo ""

# Resource Group Info
RG_NAME=$(terraform output -raw resource_group_name 2>/dev/null || echo "N/A")
RG_LOCATION=$(terraform output -raw resource_group_location 2>/dev/null || echo "N/A")
echo -e "${BLUE}Resource Group:${NC}"
echo "  Name: $RG_NAME"
echo "  Location: $RG_LOCATION"
echo ""

# Batch 1 Resources
if [ "${TF_VAR_enable_batch_1}" = "true" ]; then
    echo -e "${BLUE}Batch 1 Resources (Core):${NC}"

    # Managed Disk
    DISK_ID=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"managed_disk_id":"[^"]*' | cut -d'"' -f4)
    if [ -n "$DISK_ID" ] && [ "$DISK_ID" != "null" ]; then
        DISK_NAME=$(basename "$DISK_ID")
        DISK_STATE=$(az disk show --ids "$DISK_ID" --query "diskState" -o tsv 2>/dev/null || echo "unknown")
        DISK_SIZE=$(az disk show --ids "$DISK_ID" --query "diskSizeGb" -o tsv 2>/dev/null || echo "?")
        echo "  ✓ Managed Disk: $DISK_NAME - ${DISK_SIZE}GB - $DISK_STATE (~€1/month)"
    fi

    # Public IP
    PIP=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"public_ip_address":"[^"]*' | cut -d'"' -f4)
    if [ -n "$PIP" ] && [ "$PIP" != "null" ]; then
        echo "  ✓ Public IP: $PIP - Unassociated (~€3/month)"
    fi

    # Virtual Machine
    VM_NAME=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"vm_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$VM_NAME" ] && [ "$VM_NAME" != "null" ]; then
        VM_STATE=$(az vm show -g "$RG_NAME" -n "$VM_NAME" --query "powerState" -o tsv 2>/dev/null || echo "unknown")
        echo "  ✓ Virtual Machine: $VM_NAME - $VM_STATE (~€0/month when deallocated)"
    fi

    # Load Balancer
    LB_ID=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"load_balancer_id":"[^"]*' | cut -d'"' -f4)
    if [ -n "$LB_ID" ] && [ "$LB_ID" != "null" ]; then
        LB_NAME=$(basename "$LB_ID")
        LB_STATE=$(az network lb show --ids "$LB_ID" --query "provisioningState" -o tsv 2>/dev/null || echo "unknown")
        echo "  ✓ Load Balancer: $LB_NAME - $LB_STATE (~€18/month)"
    fi

    # Storage Account
    STORAGE_NAME=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"storage_account_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$STORAGE_NAME" ] && [ "$STORAGE_NAME" != "null" ]; then
        STORAGE_STATE=$(az storage account show -g "$RG_NAME" -n "$STORAGE_NAME" --query "provisioningState" -o tsv 2>/dev/null || echo "unknown")
        echo "  ✓ Storage Account: $STORAGE_NAME - $STORAGE_STATE (~€1/month)"
    fi

    # ExpressRoute Circuit
    ER_ID=$(terraform output -json batch_1_resources 2>/dev/null | grep -o '"expressroute_circuit_id":"[^"]*' | cut -d'"' -f4)
    if [ -n "$ER_ID" ] && [ "$ER_ID" != "null" ]; then
        ER_NAME=$(basename "$ER_ID")
        ER_STATE=$(az network express-route show --ids "$ER_ID" --query "serviceProviderProvisioningState" -o tsv 2>/dev/null || echo "unknown")
        echo "  ✓ ExpressRoute Circuit: $ER_NAME - $ER_STATE (~€45/month)"
    fi

    echo ""
fi

# Batch 3 Resources
if [ "${TF_VAR_enable_batch_3}" = "true" ]; then
    echo -e "${BLUE}Batch 3 Resources (Advanced):${NC}"

    # Container App
    CONTAINER_APP_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"container_app_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$CONTAINER_APP_NAME" ] && [ "$CONTAINER_APP_NAME" != "null" ]; then
        echo "  ✓ Container App: $CONTAINER_APP_NAME - Idle (0 replicas) (~€15/month)"
    fi

    # Virtual Desktop Host Pool
    HOST_POOL_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"host_pool_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$HOST_POOL_NAME" ] && [ "$HOST_POOL_NAME" != "null" ]; then
        echo "  ✓ Virtual Desktop Host Pool: $HOST_POOL_NAME - No sessions"
    fi

    # Session Host VM
    SESSION_HOST_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"session_host_vm_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$SESSION_HOST_NAME" ] && [ "$SESSION_HOST_NAME" != "null" ]; then
        VM_STATE=$(az vm show -g "$RG_NAME" -n "$SESSION_HOST_NAME" --query "powerState" -o tsv 2>/dev/null || echo "unknown")
        echo "  ✓ Session Host VM: $SESSION_HOST_NAME - $VM_STATE (~€50/month total VD)"
    fi

    # Azure ML Workspace
    ML_WORKSPACE_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"ml_workspace_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$ML_WORKSPACE_NAME" ] && [ "$ML_WORKSPACE_NAME" != "null" ]; then
        echo "  ✓ ML Workspace: $ML_WORKSPACE_NAME"
    fi

    # ML Compute Instance
    ML_COMPUTE_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"ml_compute_instance_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$ML_COMPUTE_NAME" ] && [ "$ML_COMPUTE_NAME" != "null" ]; then
        echo "  ✓ ML Compute Instance: $ML_COMPUTE_NAME - Idle (~€30/month)"
    fi

    # Web App
    WEB_APP_NAME=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"web_app_name":"[^"]*' | cut -d'"' -f4)
    if [ -n "$WEB_APP_NAME" ] && [ "$WEB_APP_NAME" != "null" ]; then
        WEB_APP_URL=$(terraform output -json batch_3_resources 2>/dev/null | grep -o '"web_app_url":"[^"]*' | cut -d'"' -f4)
        echo "  ✓ Web App: $WEB_APP_NAME - Zero traffic (~€10/month)"
        [ -n "$WEB_APP_URL" ] && echo "    URL: https://$WEB_APP_URL"
    fi

    echo ""
fi

# Calculate total cost
TOTAL_COST=0
[ "${TF_VAR_enable_batch_1}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 68))
[ "${TF_VAR_enable_batch_2}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 71))
[ "${TF_VAR_enable_batch_3}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 105))

echo -e "${YELLOW}=========================================="
echo "Estimated Total Cost: ~€${TOTAL_COST}/month"
echo "==========================================${NC}"
echo ""
echo "Commands:"
echo "  View detailed costs: terraform -chdir=$PROJECT_DIR/terraform show"
echo "  Destroy resources: $PROJECT_DIR/scripts/destroy.sh"
echo ""
