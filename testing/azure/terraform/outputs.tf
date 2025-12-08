# Resource Group Outputs
output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource Group location"
  value       = azurerm_resource_group.main.location
}

# Virtual Network Outputs
output "vnet_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.main.id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = azurerm_subnet.public.id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = azurerm_subnet.private.id
}

output "nsg_id" {
  description = "Network Security Group ID"
  value       = azurerm_network_security_group.default.id
}

# Batch 1 Outputs
output "batch_1_resources" {
  description = "Batch 1 resource IDs and names"
  value = var.enable_batch_1 ? {
    managed_disk_id        = try(azurerm_managed_disk.unattached[0].id, null)
    public_ip_address      = try(azurerm_public_ip.unassociated[0].ip_address, null)
    vm_id                  = try(azurerm_linux_virtual_machine.stopped[0].id, null)
    vm_name                = try(azurerm_linux_virtual_machine.stopped[0].name, null)
    load_balancer_id       = try(azurerm_lb.zero_traffic[0].id, null)
    storage_account_name   = try(azurerm_storage_account.minimal[0].name, null)
    expressroute_circuit_id = try(azurerm_express_route_circuit.local[0].id, null)
  } : null
}

# Batch 2 Outputs
output "batch_2_resources" {
  description = "Batch 2 resource IDs and names"
  value = var.enable_batch_2 ? {
    disk_snapshot_id         = try(azurerm_snapshot.orphaned[0].id, null)
    nat_gateway_id           = try(azurerm_nat_gateway.no_subnet[0].id, null)
    sql_server_name          = try(azurerm_mssql_server.test[0].name, null)
    sql_database_name        = try(azurerm_mssql_database.stopped[0].name, null)
    aks_cluster_name         = try(azurerm_kubernetes_cluster.test[0].name, null)
    function_app_name        = try(azurerm_linux_function_app.test[0].name, null)
    cosmosdb_account_name    = try(azurerm_cosmosdb_account.test[0].name, null)
  } : null
}

# Batch 3 Outputs
output "batch_3_resources" {
  description = "Batch 3 resource IDs and names"
  value = var.enable_batch_3 ? {
    # Container Apps
    log_analytics_workspace_id = try(azurerm_log_analytics_workspace.batch3[0].id, null)
    container_app_env_id       = try(azurerm_container_app_environment.test[0].id, null)
    container_app_name         = try(azurerm_container_app.idle[0].name, null)
    # Virtual Desktop
    host_pool_id               = try(azurerm_virtual_desktop_host_pool.test[0].id, null)
    host_pool_name             = try(azurerm_virtual_desktop_host_pool.test[0].name, null)
    app_group_id               = try(azurerm_virtual_desktop_application_group.test[0].id, null)
    workspace_id               = try(azurerm_virtual_desktop_workspace.test[0].id, null)
    session_host_vm_name       = try(azurerm_windows_virtual_machine.session_host[0].name, null)
    # Azure ML
    ml_workspace_id            = try(azurerm_machine_learning_workspace.test[0].id, null)
    ml_workspace_name          = try(azurerm_machine_learning_workspace.test[0].name, null)
    ml_compute_instance_name   = try(azurerm_machine_learning_compute_instance.idle[0].name, null)
    # App Service
    app_service_plan_id        = try(azurerm_service_plan.batch3[0].id, null)
    web_app_name               = try(azurerm_linux_web_app.idle[0].name, null)
    web_app_url                = try(azurerm_linux_web_app.idle[0].default_hostname, null)
  } : null
}

# Cost Estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost in EUR"
  value = {
    batch_1 = var.enable_batch_1 ? 68 : 0
    batch_2 = var.enable_batch_2 ? 71 : 0
    batch_3 = var.enable_batch_3 ? 105 : 0
    total   = (var.enable_batch_1 ? 68 : 0) + (var.enable_batch_2 ? 71 : 0) + (var.enable_batch_3 ? 105 : 0)
  }
}

# Detailed Cost Breakdown (Batch 1)
output "batch_1_cost_breakdown" {
  description = "Detailed monthly cost breakdown for Batch 1 in EUR"
  value = var.enable_batch_1 ? {
    managed_disk        = 1
    public_ip          = 3
    virtual_machine    = 0  # €0 when stopped/deallocated
    load_balancer      = 18
    storage_account    = 1
    expressroute_circuit = 45
    total              = 68
  } : null
}

# Detailed Cost Breakdown (Batch 2)
output "batch_2_cost_breakdown" {
  description = "Detailed monthly cost breakdown for Batch 2 in EUR"
  value = var.enable_batch_2 ? {
    disk_snapshot       = 2
    nat_gateway        = 35
    sql_database       = 4
    aks_cluster        = 30
    function_app       = 0  # €0 pay-per-execution (Consumption plan)
    cosmosdb           = 0  # €0 pay-per-request (Serverless)
    total              = 71
  } : null
}

# Detailed Cost Breakdown (Batch 3)
output "batch_3_cost_breakdown" {
  description = "Detailed monthly cost breakdown for Batch 3 in EUR"
  value = var.enable_batch_3 ? {
    container_app_env    = 15  # Container App Environment + Container App
    virtual_desktop      = 50  # Host Pool + Session Host VM (deallocated €0, but reserves capacity)
    azure_ml_compute     = 30  # ML Workspace + Compute Instance (Standard_DS1_v2)
    app_service          = 10  # Service Plan B1 + Web App
    total                = 105
  } : null
}
