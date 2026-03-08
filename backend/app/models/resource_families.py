"""Resource families mappings for Basic/Expert mode in detection rules."""

from typing import Dict, List

# AWS Resource Families (Big 4 with granular scenarios)
RESOURCE_FAMILIES: Dict[str, List[str]] = {
    # EBS Volumes (10 scenarios)
    "ebs_volume": [
        "ebs_volume_unattached",
        "ebs_volume_on_stopped_instance",
        "ebs_volume_gp2_migration",
        "ebs_volume_unnecessary_io2",
        "ebs_volume_overprovisioned_iops",
        "ebs_volume_overprovisioned_throughput",
        "ebs_volume_idle",
        "ebs_volume_low_iops_usage",
        "ebs_volume_low_throughput_usage",
        "ebs_volume_type_downgrade",
    ],
    # Elastic IPs (10 scenarios)
    "elastic_ip": [
        "elastic_ip_unassociated",
        "elastic_ip_on_stopped_instance",
        "elastic_ip_multiple_per_instance",
        "elastic_ip_on_detached_eni",
        "elastic_ip_never_used",
        "elastic_ip_on_unused_nat_gateway",
        "elastic_ip_idle",
        "elastic_ip_low_traffic",
        "elastic_ip_unused_nat_gateway",
        "elastic_ip_on_failed_instance",
    ],
    # EBS Snapshots (10 scenarios)
    "ebs_snapshot": [
        "ebs_snapshot_orphaned",
        "ebs_snapshot_redundant",
        "ebs_snapshot_unused_ami",
        "ebs_snapshot_old_unused",
        "ebs_snapshot_from_deleted_instance",
        "ebs_snapshot_incomplete_failed",
        "ebs_snapshot_untagged",
        "ebs_snapshot_excessive_retention",
        "ebs_snapshot_duplicate",
        "ebs_snapshot_never_restored",
    ],
    # EC2 Instances (10 scenarios)
    "ec2_instance": [
        "ec2_instance_stopped",
        "ec2_instance_idle_running",
        "ec2_instance_oversized",
        "ec2_instance_old_generation",
        "ec2_instance_burstable_credit_waste",
        "ec2_instance_dev_test_24_7",
        "ec2_instance_untagged",
        "ec2_instance_right_sizing_opportunity",
        "ec2_instance_spot_eligible",
        "ec2_instance_scheduled_unused",
    ],
    # Other AWS resources (grouped but already have single types)
    "load_balancer": ["load_balancer"],
    "rds_instance": ["rds_instance"],
    "fsx_file_system": ["fsx_file_system"],
    "neptune_cluster": ["neptune_cluster"],
    "msk_cluster": ["msk_cluster"],
    "eks_cluster": ["eks_cluster"],
    "sagemaker_endpoint": ["sagemaker_endpoint"],
    "redshift_cluster": ["redshift_cluster"],
    "elasticache_cluster": ["elasticache_cluster"],
    "vpn_connection": ["vpn_connection"],
    "transit_gateway_attachment": ["transit_gateway_attachment"],
    "opensearch_domain": ["opensearch_domain"],
    "global_accelerator": ["global_accelerator"],
    "kinesis_stream": ["kinesis_stream"],
    "vpc_endpoint": ["vpc_endpoint"],
    "documentdb_cluster": ["documentdb_cluster"],
    "s3_bucket": ["s3_bucket"],
    "lambda_function": ["lambda_function"],
    "dynamodb_table": ["dynamodb_table"],
    # Cost Intelligence Hub - Additional AWS resources (17 new)
    "fargate_task": ["fargate_task"],
    "api_gateway": ["api_gateway"],
    "ecs_cluster": ["ecs_cluster"],
    "cloudwatch_log_group": ["cloudwatch_log_group"],
    "ecr_repository": ["ecr_repository"],
    "sns_topic": ["sns_topic"],
    "sqs_queue": ["sqs_queue"],
    "secrets_manager_secret": ["secrets_manager_secret"],
    "backup_vault": ["backup_vault"],
    "app_runner_service": ["app_runner_service"],
    "emr_cluster": ["emr_cluster"],
    "sagemaker_notebook": ["sagemaker_notebook"],
    "transfer_family_server": ["transfer_family_server"],
    "elastic_beanstalk_environment": ["elastic_beanstalk_environment"],
    "direct_connect_connection": ["direct_connect_connection"],
    "mq_broker": ["mq_broker"],
    "cloudfront_distribution": ["cloudfront_distribution"],
    "kendra_index": ["kendra_index"],
    "cloudformation_stack": ["cloudformation_stack"],
    # Note: fsx_file_system, vpc_endpoint, transit_gateway_attachment, opensearch_domain,
    # global_accelerator, kinesis_stream, documentdb_cluster already existed above (lines 62-75)
}

# Azure Resource Families (logically grouped)
AZURE_RESOURCE_FAMILIES: Dict[str, List[str]] = {
    "managed_disk": [
        "managed_disk_unattached",
        "managed_disk_on_stopped_vm",
        "managed_disk_unnecessary_zrs",
        "managed_disk_unnecessary_cmk",
        "managed_disk_idle",
        "managed_disk_unused_bursting",
        "managed_disk_overprovisioned",
        "managed_disk_underutilized_hdd",
    ],
    "disk_snapshot": [
        "disk_snapshot_orphaned",
        "disk_snapshot_redundant",
        "disk_snapshot_very_old",
        "disk_snapshot_premium_source",
        "disk_snapshot_large_unused",
        "disk_snapshot_full_instead_incremental",
        "disk_snapshot_excessive_retention",
        "disk_snapshot_manual_without_policy",
        "disk_snapshot_never_restored",
        "disk_snapshot_frequent_creation",
    ],
    "public_ip": [
        "public_ip_unassociated",
        "public_ip_on_stopped_resource",
        "public_ip_dynamic_unassociated",
        "public_ip_unnecessary_standard_sku",
        "public_ip_unnecessary_zone_redundancy",
        "public_ip_ddos_protection_unused",
        "public_ip_on_nic_without_vm",
        "public_ip_reserved_but_unused",
        "public_ip_no_traffic",
        "public_ip_very_low_traffic",
    ],
    "virtual_machine": [
        "virtual_machine_deallocated",
        "virtual_machine_stopped_not_deallocated",
        "virtual_machine_never_started",
        "virtual_machine_oversized_premium",
        "virtual_machine_untagged_orphan",
        "virtual_machine_idle",
        "virtual_machine_old_generation",
        "virtual_machine_spot_convertible",
        "virtual_machine_underutilized",
        "virtual_machine_memory_overprovisioned",
    ],
    # Azure - NAT Gateway scenarios
    "nat_gateway": [
        "nat_gateway_no_subnet",
        "nat_gateway_never_used",
        "nat_gateway_no_public_ip",
        "nat_gateway_single_vm",
        "nat_gateway_redundant",
        "nat_gateway_dev_test_always_on",
        "nat_gateway_unnecessary_zones",
        "nat_gateway_no_traffic",
        "nat_gateway_very_low_traffic",
        "nat_gateway_private_link_alternative",
    ],
    # Azure Load Balancers & Application Gateways (10 scenarios)
    "load_balancer_appgw": [
        "load_balancer_no_backend_instances",
        "load_balancer_all_backends_unhealthy",
        "load_balancer_no_inbound_rules",
        "load_balancer_basic_sku_retired",
        "application_gateway_no_backend_targets",
        "application_gateway_stopped",
        "load_balancer_never_used",
        "load_balancer_no_traffic",
        "application_gateway_no_requests",
        "application_gateway_underutilized",
    ],
    # Azure SQL Database (4 scenarios)
    "sql_database": [
        "sql_database_stopped",
        "sql_database_idle_connections",
        "sql_database_over_provisioned_dtu",
        "sql_database_serverless_not_pausing",
    ],
    # Azure Cosmos DB Core/SQL API (3 scenarios)
    "cosmosdb": [
        "cosmosdb_over_provisioned_ru",
        "cosmosdb_idle_containers",
        "cosmosdb_hot_partitions_idle_others",
    ],
    # Azure PostgreSQL/MySQL Flexible Server (4 scenarios)
    "postgres_mysql": [
        "postgres_mysql_stopped",
        "postgres_mysql_idle_connections",
        "postgres_mysql_over_provisioned_vcores",
        "postgres_mysql_burstable_always_bursting",
    ],
    # Azure Synapse Analytics (2 scenarios)
    "synapse": [
        "synapse_sql_pool_paused",
        "synapse_sql_pool_idle_queries",
    ],
    # Azure Cache for Redis (18 scenarios)
    "redis": [
        "redis_idle_cache",
        "redis_over_sized_tier",
        "redis_premium_in_dev",
        "redis_non_ssl_port_enabled",
        "redis_no_backup_configured",
        "redis_old_version",
        "redis_no_firewall_rules",
        "redis_multiple_caches_same_rg",
        "redis_no_private_endpoint",
        "redis_basic_tier_in_production",
        "redis_low_cpu_utilization",
        "redis_low_cache_hit_ratio",
        "redis_low_operations_per_second",
        "redis_high_eviction_rate",
        "redis_high_memory_fragmentation",
        "redis_low_network_bandwidth",
        "redis_high_server_load",
        "redis_no_minimum_tls",
    ],
    # Azure Event Hubs (18 scenarios)
    "eventhub": [
        "eventhub_namespace_idle",
        "eventhub_premium_in_dev",
        "eventhub_no_consumer_groups",
        "eventhub_empty_namespace",
        "eventhub_excessive_throughput_units",
        "eventhub_auto_inflate_disabled",
        "eventhub_no_capture_configured",
        "eventhub_excessive_retention",
        "eventhub_no_private_endpoint",
        "eventhub_multiple_namespaces_same_rg",
        "eventhub_low_incoming_messages",
        "eventhub_low_outgoing_messages",
        "eventhub_low_throughput_utilization",
        "eventhub_high_throttled_requests",
        "eventhub_zero_active_connections",
        "eventhub_low_capture_utilization",
        "eventhub_high_server_errors",
        "eventhub_low_incoming_bytes",
    ],
    # Azure NetApp Files (18 scenarios)
    "netapp": [
        "netapp_volume_idle",
        "netapp_premium_in_dev",
        "netapp_volume_over_provisioned",
        "netapp_no_snapshot_policy",
        "netapp_orphan_snapshots",
        "netapp_no_replication",
        "netapp_old_snapshots",
        "netapp_empty_capacity_pool",
        "netapp_pool_over_provisioned",
        "netapp_multiple_pools_consolidation",
        "netapp_low_iops",
        "netapp_low_throughput",
        "netapp_low_read_ops",
        "netapp_low_write_ops",
        "netapp_high_latency",
        "netapp_low_volume_allocated",
        "netapp_low_snapshot_usage",
        "netapp_pool_low_utilization",
    ],
    # Azure Cognitive Search / AI Search (18 scenarios)
    "search": [
        "search_service_idle",
        "search_premium_in_dev",
        "search_no_indexes",
        "search_over_provisioned_replicas",
        "search_no_private_endpoint",
        "search_old_api_version",
        "search_multiple_services_same_rg",
        "search_excessive_partitions",
        "search_no_diagnostic_logs",
        "search_free_tier_in_production",
        "search_low_query_volume",
        "search_low_document_count",
        "search_high_query_latency",
        "search_high_throttled_queries",
        "search_low_cpu_utilization",
        "search_low_storage_utilization",
        "search_low_skillset_executions",
        "search_low_indexer_utilization",
    ],
    # Azure Storage Accounts (8 scenarios)
    "storage_account": [
        "storage_account_never_used",
        "storage_account_empty",
        "storage_no_lifecycle_policy",
        "storage_unnecessary_grs",
        "soft_deleted_blobs_accumulated",
        "blobs_hot_tier_unused",
        "storage_account_no_transactions",
        "blob_old_versions_accumulated",
    ],
    # Azure Functions (10 scenarios)
    "functions": [
        "functions_never_invoked",
        "functions_premium_plan_idle",
        "functions_consumption_over_allocated_memory",
        "functions_always_on_consumption",
        "functions_premium_plan_oversized",
        "functions_dev_test_premium",
        "functions_multiple_plans_same_app",
        "functions_low_invocation_rate_premium",
        "functions_high_error_rate",
        "functions_long_execution_time",
    ],
    # Azure Cosmos DB Table API (12 scenarios)
    "cosmosdb_table": [
        "cosmosdb_table_api_low_traffic",
        "cosmosdb_table_over_provisioned_ru",
        "cosmosdb_table_high_storage_low_throughput",
        "cosmosdb_table_idle",
        "cosmosdb_table_autoscale_not_scaling_down",
        "cosmosdb_table_unnecessary_multi_region",
        "cosmosdb_table_continuous_backup_unused",
        "cosmosdb_table_empty_tables",
        "cosmosdb_table_throttled_need_autoscale",
        "cosmosdb_table_never_used",
        "cosmosdb_table_unnecessary_zone_redundancy",
        "cosmosdb_table_analytical_storage_never_used",
    ],
    # Azure Container Apps (16 scenarios)
    "container_app": [
        "container_app_stopped",
        "container_app_zero_replicas",
        "container_app_unnecessary_premium_tier",
        "container_app_dev_zone_redundancy",
        "container_app_no_ingress_configured",
        "container_app_empty_environment",
        "container_app_unused_revision",
        "container_app_overprovisioned_cpu_memory",
        "container_app_custom_domain_unused",
        "container_app_secrets_unused",
        "container_app_low_cpu_utilization",
        "container_app_low_memory_utilization",
        "container_app_zero_http_requests",
        "container_app_high_replica_low_traffic",
        "container_app_autoscaling_not_triggering",
        "container_app_cold_start_issues",
    ],
    # Azure Virtual Desktop (18 scenarios)
    "avd": [
        "avd_host_pool_empty",
        "avd_session_host_stopped",
        "avd_session_host_never_used",
        "avd_host_pool_no_autoscale",
        "avd_host_pool_over_provisioned",
        "avd_application_group_empty",
        "avd_workspace_empty",
        "avd_premium_disk_in_dev",
        "avd_unnecessary_availability_zones",
        "avd_personal_desktop_never_used",
        "avd_fslogix_oversized",
        "avd_session_host_old_vm_generation",
        "avd_low_cpu_utilization",
        "avd_low_memory_utilization",
        "avd_zero_user_sessions",
        "avd_high_host_count_low_users",
        "avd_disconnected_sessions_waste",
        "avd_peak_hours_mismatch",
    ],
    # Azure HDInsight Spark (18 scenarios)
    "hdinsight_spark": [
        "hdinsight_spark_cluster_stopped",
        "hdinsight_spark_cluster_never_used",
        "hdinsight_spark_premium_storage_dev",
        "hdinsight_spark_no_autoscale",
        "hdinsight_spark_outdated_version",
        "hdinsight_spark_external_metastore_unused",
        "hdinsight_spark_empty_cluster",
        "hdinsight_spark_oversized_head_nodes",
        "hdinsight_spark_unnecessary_edge_node",
        "hdinsight_spark_undersized_disks",
        "hdinsight_spark_low_cpu_utilization",
        "hdinsight_spark_zero_jobs_metrics",
        "hdinsight_spark_idle_business_hours",
        "hdinsight_spark_high_yarn_memory_waste",
        "hdinsight_spark_excessive_shuffle_data",
        "hdinsight_spark_autoscale_not_working",
        "hdinsight_spark_low_memory_utilization",
        "hdinsight_spark_high_job_failure_rate",
    ],
    # Azure ML Compute Instance (18 scenarios)
    "ml_compute_instance": [
        "ml_compute_instance_no_auto_shutdown",
        "ml_compute_instance_gpu_for_cpu_workload",
        "ml_compute_instance_stopped_30_days",
        "ml_compute_instance_over_provisioned",
        "ml_compute_instance_never_accessed",
        "ml_compute_instance_multiple_per_user",
        "ml_compute_instance_premium_ssd_unnecessary",
        "ml_compute_instance_no_idle_shutdown",
        "ml_compute_instance_dev_high_performance_sku",
        "ml_compute_instance_old_sdk_deprecated_image",
        "ml_compute_instance_low_cpu_utilization",
        "ml_compute_instance_low_gpu_utilization",
        "ml_compute_instance_idle_business_hours",
        "ml_compute_instance_no_jupyter_activity",
        "ml_compute_instance_no_training_jobs",
        "ml_compute_instance_low_memory_utilization",
        "ml_compute_instance_network_idle",
        "ml_compute_instance_disk_io_near_zero",
    ],
    # Azure App Service (18 scenarios)
    "app_service": [
        "app_service_plan_empty",
        "app_service_premium_in_dev",
        "app_service_no_auto_scale",
        "app_service_always_on_low_traffic",
        "app_service_unused_deployment_slots",
        "app_service_over_provisioned_plan",
        "app_service_stopped_apps_paid_plan",
        "app_service_multiple_plans_consolidation",
        "app_service_vnet_integration_unused",
        "app_service_old_runtime_version",
        "app_service_low_cpu_utilization",
        "app_service_low_memory_utilization",
        "app_service_low_request_count",
        "app_service_no_traffic_business_hours",
        "app_service_high_http_error_rate",
        "app_service_slow_response_time",
        "app_service_auto_scale_never_triggers",
        "app_service_cold_start_excessive",
    ],
    # Azure ExpressRoute (4 scenarios)
    "expressroute": [
        "expressroute_circuit_not_provisioned",
        "expressroute_circuit_no_connection",
        "expressroute_gateway_orphaned",
        "expressroute_circuit_underutilized",
    ],
    # Azure VPN Gateway (3 scenarios)
    "vpn_gateway": [
        "vpn_gateway_disconnected",
        "vpn_gateway_basic_sku_deprecated",
        "vpn_gateway_no_connections",
    ],
    # Azure Network Interfaces (1 scenario)
    "network_interface": [
        "network_interface_orphaned",
    ],
    # Other Azure resources (each as its own family)
    "azure_aks_cluster": ["azure_aks_cluster"],
}

# GCP Resource Families (logically grouped - 12 major services with ~152 scenarios)
GCP_RESOURCE_FAMILIES: Dict[str, List[str]] = {
    # Compute Engine Instances
    "compute_instance": [
        "compute_instance_stopped",
        "compute_instance_idle",
        "compute_instance_overprovisioned",
        "compute_instance_old_generation",
        "compute_instance_no_spot",
        "compute_instance_untagged",
        "compute_instance_memory_waste",
        "compute_instance_rightsizing",
        "compute_instance_burstable_waste",
    ],
    # Persistent Disks
    "persistent_disk": [
        "persistent_disk_unattached",
        "persistent_disk_attached_stopped",
        "persistent_disk_never_used",
        "persistent_disk_orphan_snapshots",
        "persistent_disk_oversized",
        "persistent_disk_underutilized",
        "persistent_disk_overprovisioned_type",
        "persistent_disk_old_type",
        "persistent_disk_readonly",
        "persistent_disk_untagged",
    ],
    # Cloud SQL
    "cloud_sql": [
        "cloud_sql_stopped",
        "cloud_sql_idle",
        "cloud_sql_overprovisioned",
        "cloud_sql_storage_overprovisioned",
        "cloud_sql_unnecessary_ha",
        "cloud_sql_old_machine_type",
        "cloud_sql_unused_replicas",
        "cloud_sql_zero_io",
        "cloud_sql_untagged",
        "cloud_sql_alternative_cost_per_gb",
    ],
    # GKE Clusters
    "gke_cluster": [
        "gke_cluster_empty",
        "gke_cluster_no_workloads",
        "gke_cluster_no_autoscaling",
        "gke_cluster_nodes_inactive",
        "gke_cluster_nodes_underutilized",
        "gke_cluster_nodepool_overprovisioned",
        "gke_cluster_pods_overrequested",
        "gke_cluster_old_machine_type",
        "gke_cluster_untagged",
    ],
    # Dataflow Jobs
    "dataflow": [
        "dataflow_streaming_job_idle",
        "dataflow_job_low_cpu_utilization",
        "dataflow_job_low_throughput",
        "dataflow_job_oversized_workers",
        "dataflow_oversized_disk",
        "dataflow_no_max_workers",
        "dataflow_batch_without_flexrs",
        "dataflow_streaming_without_engine",
        "dataflow_streaming_high_backlog",
        "dataflow_job_failed_with_resources",
    ],
    # Dataproc Clusters
    "dataproc_cluster": [
        "dataproc_cluster_stopped",
        "dataproc_cluster_idle",
        "dataproc_cluster_low_cpu_utilization",
        "dataproc_cluster_low_memory_utilization",
        "dataproc_cluster_no_autoscaling",
        "dataproc_cluster_oversized_workers",
        "dataproc_cluster_unnecessary_ssd",
        "dataproc_cluster_underutilized_hdfs",
        "dataproc_cluster_no_scheduled_delete",
        "dataproc_cluster_single_node_prod",
    ],
    # BigQuery
    "bigquery": [
        "bigquery_unused_materialized_views",
        "bigquery_never_queried_tables",
        "bigquery_empty_datasets",
        "bigquery_unpartitioned_large_tables",
        "bigquery_unclustered_large_tables",
        "bigquery_no_expiration",
        "bigquery_active_storage_waste",
        "bigquery_expensive_queries",
        "bigquery_ondemand_vs_flatrate",
        "bigquery_untagged_datasets",
    ],
    # Memorystore Redis
    "memorystore_redis": [
        "memorystore_redis_idle",
        "memorystore_redis_overprovisioned",
        "memorystore_redis_low_hit_rate",
        "memorystore_redis_wrong_tier",
        "memorystore_redis_wrong_size",
        "memorystore_redis_wrong_eviction",
        "memorystore_redis_cross_zone_traffic",
        "memorystore_redis_high_connection_churn",
        "memorystore_redis_no_cud",
        "memorystore_redis_untagged",
    ],
    # Cloud Functions
    "gcp_cloud_function": [
        "gcp_cloud_function_never_invoked",
        "gcp_cloud_function_memory_overprovisioning",
        "gcp_cloud_function_excessive_timeout",
        "gcp_cloud_function_excessive_concurrency",
        "gcp_cloud_function_excessive_max_instances",
        "gcp_cloud_function_idle_min_instances",
        "gcp_cloud_function_duplicate",
        "gcp_cloud_function_cold_start_over_optimization",
        "gcp_cloud_function_untagged",
    ],
    # Cloud Run
    "gcp_cloud_run": [
        "gcp_cloud_run_never_used",
        "gcp_cloud_run_overprovisioned",
        "gcp_cloud_run_excessive_min_instances",
        "gcp_cloud_run_excessive_max_instances",
        "gcp_cloud_run_idle_min_instances",
        "gcp_cloud_run_nonprod_min_instances",
        "gcp_cloud_run_cpu_always_allocated",
        "gcp_cloud_run_low_concurrency",
        "gcp_cloud_run_multi_region_redundant",
        "gcp_cloud_run_untagged",
    ],
    # Vertex AI
    "vertex_ai": [
        "vertex_ai_idle_endpoints",
        "vertex_ai_zero_predictions",
        "vertex_ai_overprovisioned_machines",
        "vertex_ai_unused_traffic_split",
        "vertex_ai_old_model_versions",
        "vertex_ai_gpu_waste",
        "vertex_ai_failed_training_jobs",
        "vertex_ai_unused_feature_store",
        "vertex_ai_untagged_endpoints",
    ],
    # AI Platform Notebooks
    "notebook_instance": [
        "notebook_instance_stopped",
        "notebook_instance_idle_no_shutdown",
        "notebook_instance_running_no_activity",
        "notebook_instance_oversized_machine_type",
        "notebook_instance_oversized_disk",
        "notebook_instance_low_cpu_utilization",
        "notebook_instance_low_memory_utilization",
        "notebook_instance_low_gpu_utilization",
        "notebook_instance_gpu_attached_unused",
        "notebook_instance_unnecessary_gpu_in_dev",
    ],
}

# Inverse mapping: resource_type -> family
RESOURCE_TYPE_TO_FAMILY: Dict[str, str] = {}
for family, types in RESOURCE_FAMILIES.items():
    for resource_type in types:
        RESOURCE_TYPE_TO_FAMILY[resource_type] = family

for family, types in AZURE_RESOURCE_FAMILIES.items():
    for resource_type in types:
        RESOURCE_TYPE_TO_FAMILY[resource_type] = family

for family, types in GCP_RESOURCE_FAMILIES.items():
    for resource_type in types:
        RESOURCE_TYPE_TO_FAMILY[resource_type] = family


def get_resource_family(resource_type: str) -> str:
    """Get the family name for a given resource_type."""
    return RESOURCE_TYPE_TO_FAMILY.get(resource_type, resource_type)


def get_family_scenarios(family: str) -> List[str]:
    """Get all scenario resource_types for a given family."""
    if family in RESOURCE_FAMILIES:
        return RESOURCE_FAMILIES[family]
    elif family in AZURE_RESOURCE_FAMILIES:
        return AZURE_RESOURCE_FAMILIES[family]
    elif family in GCP_RESOURCE_FAMILIES:
        return GCP_RESOURCE_FAMILIES[family]
    else:
        return [family]  # Single-scenario family


def extract_common_params(rules_dict: Dict[str, any]) -> Dict[str, any]:
    """
    Extract common parameters from a rule dictionary.

    Common params are typically: enabled, min_age_days, confidence_threshold_days, etc.
    """
    common_keys = [
        "enabled",
        "min_age_days",
        "confidence_threshold_days",
        "min_stopped_days",
        "description",
    ]

    return {key: rules_dict.get(key) for key in common_keys if key in rules_dict}
