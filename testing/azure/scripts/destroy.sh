#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "CutCosts Azure Resource Destruction"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    exit 1
fi

# Source .env but DON'T export ARM_CLIENT_ID and ARM_CLIENT_SECRET
source "$PROJECT_DIR/.env"

# Export only the variables needed (NOT the Service Principal credentials)
export TF_VAR_azure_subscription_id="$ARM_SUBSCRIPTION_ID"
export TF_VAR_azure_tenant_id="$ARM_TENANT_ID"
export TF_VAR_azure_region="${AZURE_REGION:-westeurope}"
export TF_VAR_environment="${TF_VAR_environment:-test}"
export TF_VAR_project_name="${TF_VAR_project_name:-cutcosts-testing}"
export TF_VAR_owner_email="${TF_VAR_owner_email}"

# Force all batches to true for destroy - ensures ALL resources in state are destroyed
# regardless of .env settings
export TF_VAR_enable_batch_1=true
export TF_VAR_enable_batch_2=true
export TF_VAR_enable_batch_3=true

# Unset Service Principal credentials to force az login usage
unset ARM_CLIENT_ID
unset ARM_CLIENT_SECRET

# Parse command line arguments
AUTO_APPROVE=""
BATCH_SPECIFIC=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            AUTO_APPROVE="-auto-approve"
            shift
            ;;
        --batch)
            shift
            BATCH_SPECIFIC="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--batch N]"
            exit 1
            ;;
    esac
done

# Change to terraform directory
cd "$PROJECT_DIR/terraform"

# Check if terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo -e "${YELLOW}⚠ No terraform state found${NC}"
    echo "No resources to destroy"
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
echo -e "${GREEN}✓ Azure authenticated${NC}"
echo ""

# Pre-destruction: Start ALL deallocated VMs in the resource group
echo ""
echo "Checking for deallocated VMs..."

RG_NAME=$(terraform output -raw resource_group_name 2>/dev/null || echo "cutcosts-testing-rg")

# Get all deallocated VMs in the resource group (handles batch_1, batch_3, etc.)
# Note: -d (--show-details) is required to get powerState
DEALLOCATED_VMS=$(az vm list -g "$RG_NAME" -d --query "[?powerState=='VM deallocated'].name" -o tsv 2>/dev/null || echo "")

if [ -n "$DEALLOCATED_VMS" ]; then
    echo "Found deallocated VMs: $DEALLOCATED_VMS"

    for VM_NAME in $DEALLOCATED_VMS; do
        echo -e "${YELLOW}Starting VM '$VM_NAME' to allow proper cleanup...${NC}"
        az vm start --resource-group "$RG_NAME" --name "$VM_NAME" --no-wait
    done

    # Wait for all VMs to start
    echo "Waiting for VMs to start..."
    for VM_NAME in $DEALLOCATED_VMS; do
        az vm wait --resource-group "$RG_NAME" --name "$VM_NAME" --custom "instanceView.statuses[?code=='PowerState/running']"
        echo -e "${GREEN}✓ VM '$VM_NAME' started successfully${NC}"
    done
else
    echo "No deallocated VMs found"
fi

# Show what will be destroyed
echo ""
echo "Analyzing resources to destroy..."
terraform plan -destroy

# Calculate current cost
TOTAL_COST=0
[ "${TF_VAR_enable_batch_1}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 68))
[ "${TF_VAR_enable_batch_2}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 71))
[ "${TF_VAR_enable_batch_3}" = "true" ] && TOTAL_COST=$((TOTAL_COST + 105))

echo ""
echo -e "${YELLOW}This will destroy ALL test resources (saving ~€${TOTAL_COST}/month)${NC}"
echo ""

# Confirmation (unless --force)
if [ -z "$AUTO_APPROVE" ]; then
    echo -e "${RED}⚠ WARNING: This action cannot be undone!${NC}"
    read -p "Type 'destroy' to confirm: " CONFIRM
    if [ "$CONFIRM" != "destroy" ]; then
        echo "Aborted."
        exit 0
    fi
fi

# Pre-destruction: Delete auto-created Azure resources that block RG deletion
echo ""
echo "Checking for auto-created resources..."

# Azure auto-creates "Application Insights Smart Detection" action groups
# These block Resource Group deletion by Terraform
SMART_DETECTION_AG=$(az monitor action-group list -g "$RG_NAME" --query "[?name=='Application Insights Smart Detection'].name" -o tsv 2>/dev/null || echo "")
if [ -n "$SMART_DETECTION_AG" ]; then
    echo -e "${YELLOW}Deleting auto-created action group 'Application Insights Smart Detection'...${NC}"
    az monitor action-group delete --name "Application Insights Smart Detection" --resource-group "$RG_NAME" 2>/dev/null
    echo -e "${GREEN}✓ Action group deleted${NC}"
else
    echo "No auto-created action groups found"
fi

# Destroy resources
echo ""
echo "Destroying Azure resources..."
terraform destroy $AUTO_APPROVE

echo ""
echo -e "${GREEN}=========================================="
echo "All resources destroyed successfully!"
echo "==========================================${NC}"
echo ""
echo "Cost savings: ~€${TOTAL_COST}/month"
echo ""

# Cleanup terraform files
read -p "Remove local terraform state? (y/n): " CLEANUP
if [ "$CLEANUP" = "y" ]; then
    rm -rf .terraform terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl
    echo -e "${GREEN}✓ Local state cleaned up${NC}"
fi

echo ""
