# Batch 4: Additional Implemented Resources (~€20/month)
# These resources have waste detection scanners already implemented in azure.py
# - Azure Cache for Redis (idle, over-sized tier)
# - Synapse SQL Pool (paused)
# - Azure Files (empty file share, over-provisioned)

# ============================================
# 1. AZURE CACHE FOR REDIS (~€15/month)
# ============================================
# Basic C0 tier - cheapest option for testing
# Triggers: scan_redis_idle_cache (zero connections)
#           scan_redis_over_sized_tier (memory <30%)

resource "azurerm_redis_cache" "idle" {
  count               = var.enable_batch_4 ? 1 : 0
  name                = "${var.project_name}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 0
  family              = "C"
  sku_name            = "Basic"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {}

  tags = {
    Name         = "${var.project_name}-redis"
    TestScenario = "Azure Cache for Redis - Idle (zero connections)"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

# ============================================
# 2. SYNAPSE SQL POOL - PAUSED (~€1/month storage only)
# ============================================
# DW100c is the smallest dedicated SQL pool
# Immediately paused after creation to minimize cost
# Triggers: scan_synapse_sql_pool_paused

resource "azurerm_storage_account" "synapse" {
  count                    = var.enable_batch_4 ? 1 : 0
  name                     = "${replace(var.project_name, "-", "")}synsa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true

  tags = {
    Name        = "${var.project_name}-synapse-storage"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
  count              = var.enable_batch_4 ? 1 : 0
  name               = "synapsefs"
  storage_account_id = azurerm_storage_account.synapse[0].id
}

resource "azurerm_synapse_workspace" "test" {
  count                                = var.enable_batch_4 ? 1 : 0
  name                                 = "${var.project_name}-synapse-ws"
  resource_group_name                  = azurerm_resource_group.main.name
  location                             = azurerm_resource_group.main.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse[0].id
  sql_administrator_login              = "sqladmin"
  sql_administrator_login_password     = "P@ssw0rd1234!"

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Name         = "${var.project_name}-synapse-ws"
    TestScenario = "Synapse Workspace with Paused SQL Pool"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

resource "azurerm_synapse_sql_pool" "paused" {
  count                = var.enable_batch_4 ? 1 : 0
  name                 = "cutcoststestpool"
  synapse_workspace_id = azurerm_synapse_workspace.test[0].id
  sku_name             = "DW100c"
  create_mode          = "Default"
  collation            = "SQL_Latin1_General_CP1_CI_AS"

  tags = {
    Name         = "${var.project_name}-synapse-sql-pool"
    TestScenario = "Synapse SQL Pool - Paused"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

# Pause the SQL pool immediately after creation to minimize cost
# When paused, only storage is billed (~€1/month)
resource "null_resource" "pause_synapse_pool" {
  count = var.enable_batch_4 ? 1 : 0

  depends_on = [azurerm_synapse_sql_pool.paused]

  provisioner "local-exec" {
    command = "az synapse sql pool pause --resource-group ${azurerm_resource_group.main.name} --workspace-name ${azurerm_synapse_workspace.test[0].name} --name ${azurerm_synapse_sql_pool.paused[0].name}"
  }
}

# ============================================
# 3. AZURE FILES - EMPTY FILE SHARE (~€1/month)
# ============================================
# Storage account with an empty file share
# Triggers: scan_azure_file_shares (file_share_empty, file_share_over_provisioned)

resource "azurerm_storage_account" "file_share" {
  count                    = var.enable_batch_4 ? 1 : 0
  name                     = "${replace(var.project_name, "-", "")}filesa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    Name         = "${var.project_name}-file-share-storage"
    TestScenario = "Azure Files - Empty file share"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

resource "azurerm_storage_share" "empty" {
  count                = var.enable_batch_4 ? 1 : 0
  name                 = "cutcosts-empty-share"
  storage_account_name = azurerm_storage_account.file_share[0].name
  quota                = 100 # 100 GB quota but 0 GB used = over-provisioned

  # No files uploaded = empty share + over-provisioned scenario
}

resource "azurerm_storage_share" "over_provisioned" {
  count                = var.enable_batch_4 ? 1 : 0
  name                 = "cutcosts-oversized-share"
  storage_account_name = azurerm_storage_account.file_share[0].name
  quota                = 500 # 500 GB quota but 0 GB used = heavily over-provisioned
}
