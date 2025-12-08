# Batch 3: Advanced Azure Resources (~€105/month)
# These resources test Cost Optimization detection for advanced Azure services
# - Container Apps (idle)
# - Virtual Desktop (Host Pool + Session Host VM)
# - Azure ML Compute Instance (idle)
# - App Service (zero traffic)

# ============================================
# Data sources
# ============================================

data "azurerm_client_config" "current" {}

# ============================================
# 1. CONTAINER APPS (~€15/month)
# ============================================
# Container Apps Environment requires Log Analytics Workspace

resource "azurerm_log_analytics_workspace" "batch3" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-log-analytics"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    Name        = "${var.project_name}-log-analytics"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_container_app_environment" "test" {
  count                      = var.enable_batch_3 ? 1 : 0
  name                       = "${var.project_name}-container-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.batch3[0].id

  tags = {
    Name        = "${var.project_name}-container-env"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_container_app" "idle" {
  count                        = var.enable_batch_3 ? 1 : 0
  name                         = "${var.project_name}-container-app"
  container_app_environment_id = azurerm_container_app_environment.test[0].id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "nginx"
      image  = "nginx:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }

    # Scale to 0 replicas (idle)
    min_replicas = 0
    max_replicas = 1
  }

  tags = {
    Name         = "${var.project_name}-container-app"
    TestScenario = "Container App - Idle (0 replicas)"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

# ============================================
# 2. VIRTUAL DESKTOP (~€50/month)
# ============================================
# Host Pool + Application Group + Workspace + Session Host VM

resource "azurerm_virtual_desktop_host_pool" "test" {
  count                            = var.enable_batch_3 ? 1 : 0
  name                             = "${var.project_name}-hostpool"
  location                         = azurerm_resource_group.main.location
  resource_group_name              = azurerm_resource_group.main.name
  type                             = "Pooled"
  load_balancer_type               = "BreadthFirst"
  maximum_sessions_allowed         = 5
  friendly_name                    = "CutCosts Test Host Pool"
  validate_environment             = false
  start_vm_on_connect              = false
  custom_rdp_properties            = "audiocapturemode:i:0;audiomode:i:0;"

  tags = {
    Name         = "${var.project_name}-hostpool"
    TestScenario = "Virtual Desktop Host Pool - No sessions"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

resource "azurerm_virtual_desktop_host_pool_registration_info" "test" {
  count           = var.enable_batch_3 ? 1 : 0
  hostpool_id     = azurerm_virtual_desktop_host_pool.test[0].id
  expiration_date = timeadd(timestamp(), "48h")
}

resource "azurerm_virtual_desktop_application_group" "test" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-appgroup"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "Desktop"
  host_pool_id        = azurerm_virtual_desktop_host_pool.test[0].id
  friendly_name       = "CutCosts Test Desktop"

  tags = {
    Name        = "${var.project_name}-appgroup"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_virtual_desktop_workspace" "test" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-workspace"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  friendly_name       = "CutCosts Test Workspace"

  tags = {
    Name        = "${var.project_name}-workspace"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_virtual_desktop_workspace_application_group_association" "test" {
  count                = var.enable_batch_3 ? 1 : 0
  workspace_id         = azurerm_virtual_desktop_workspace.test[0].id
  application_group_id = azurerm_virtual_desktop_application_group.test[0].id
}

# Session Host VM (Windows 10)
resource "azurerm_network_interface" "session_host" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-session-host-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.private.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = {
    Name        = "${var.project_name}-session-host-nic"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_windows_virtual_machine" "session_host" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "cutcosts-sh-vm"  # Max 15 chars for Windows computer_name
  computer_name       = "cutcosts-sh"     # Explicit computer name (max 15 chars)
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B2s"
  admin_username      = "azureadmin"
  admin_password      = "CutCosts@Test2024!"  # Test environment only
  network_interface_ids = [
    azurerm_network_interface.session_host[0].id,
  ]

  os_disk {
    name                 = "${var.project_name}-session-host-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsDesktop"
    offer     = "Windows-10"
    sku       = "win10-22h2-pro"
    version   = "latest"
  }

  tags = {
    Name         = "${var.project_name}-session-host"
    TestScenario = "Virtual Desktop Session Host - Deallocated"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

# Deallocate the session host VM after creation
resource "null_resource" "deallocate_session_host" {
  count = var.enable_batch_3 ? 1 : 0

  depends_on = [azurerm_windows_virtual_machine.session_host]

  provisioner "local-exec" {
    command = "az vm deallocate --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_windows_virtual_machine.session_host[0].name}"
  }
}

# ============================================
# 3. AZURE ML COMPUTE (~€30/month)
# ============================================
# Requires: Application Insights, Key Vault, Storage Account, ML Workspace

resource "azurerm_application_insights" "ml" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-ml-appinsights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.batch3[0].id

  tags = {
    Name        = "${var.project_name}-ml-appinsights"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_key_vault" "ml" {
  count                      = var.enable_batch_3 ? 1 : 0
  name                       = "${replace(var.project_name, "-", "")}mlkv"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  tags = {
    Name        = "${var.project_name}-ml-keyvault"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_storage_account" "ml" {
  count                    = var.enable_batch_3 ? 1 : 0
  name                     = "${replace(var.project_name, "-", "")}mlsa"
  location                 = azurerm_resource_group.main.location
  resource_group_name      = azurerm_resource_group.main.name
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    Name        = "${var.project_name}-ml-storage"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_machine_learning_workspace" "test" {
  count                         = var.enable_batch_3 ? 1 : 0
  name                          = "${var.project_name}-ml-ws-v2"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  application_insights_id       = azurerm_application_insights.ml[0].id
  key_vault_id                  = azurerm_key_vault.ml[0].id
  storage_account_id            = azurerm_storage_account.ml[0].id
  public_network_access_enabled = true

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Name         = "${var.project_name}-ml-ws-v2"
    TestScenario = "Azure ML Workspace with Idle Compute"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

resource "azurerm_machine_learning_compute_instance" "idle" {
  count                         = var.enable_batch_3 ? 1 : 0
  name                          = "cutcostsmlcompute"  # No hyphens allowed
  machine_learning_workspace_id = azurerm_machine_learning_workspace.test[0].id
  virtual_machine_size          = "Standard_DS1_v2"
  authorization_type            = "personal"

  tags = {
    Name         = "${var.project_name}-ml-compute"
    TestScenario = "ML Compute Instance - Idle"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}

# ============================================
# 4. APP SERVICE (~€10/month)
# ============================================
# Service Plan (B1) + Linux Web App

resource "azurerm_service_plan" "batch3" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-app-service-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"

  tags = {
    Name        = "${var.project_name}-app-service-plan"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner_email
  }
}

resource "azurerm_linux_web_app" "idle" {
  count               = var.enable_batch_3 ? 1 : 0
  name                = "${var.project_name}-web-app"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.batch3[0].id

  site_config {
    application_stack {
      node_version = "18-lts"
    }
  }

  tags = {
    Name         = "${var.project_name}-web-app"
    TestScenario = "App Service - Zero traffic"
    Environment  = var.environment
    Project      = var.project_name
    Owner        = var.owner_email
  }
}
