"""Orphan resource API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.paywall_dependencies import get_paywall_context, require_paid_for_resource_actions
from app.crud import cloud_account as cloud_account_crud
from app.crud import orphan_resource as orphan_resource_crud
from app.models.orphan_resource import ResourceStatus
from app.models.user import User
from app.schemas.orphan_resource import (
    OrphanResource,
    OrphanResourceStats,
    OrphanResourceUpdate,
    redact_orphan_resource,
)
from app.schemas.paywall import PaywallContext
from app.services.user_action_tracker import track_user_action

router = APIRouter()


@router.get(
    "/",
    response_model=list[OrphanResource],
    summary="List orphaned resources",
    description="""
List all orphaned resources detected from scans with flexible filtering.

By default, shows resources from the **latest completed scan** per cloud account
(excludes inventory scans).

## Filters
- **cloud_account_id**: Filter by specific cloud account
- **status**: Filter by resource status (active, ignored, marked_for_deletion, deleted)
- **resource_type**: Filter by resource type (e.g., "ec2_instance", "ebs_volume")

## Resource Status Values
- **active**: Resource is detected and active (default state)
- **ignored**: User marked resource to be ignored in future scans
- **marked_for_deletion**: User marked resource for deletion (ready for cleanup)
- **deleted**: Resource has been deleted

## Pagination
Use `skip` and `limit` parameters for pagination (max 100 per page).

## Rate Limiting
Standard rate limit: 60 requests/minute
""",
    response_description="List of orphaned resources matching filters",
    responses={
        200: {
            "description": "Resources retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "scan_id": "scan-uuid",
                            "cloud_account_id": "account-uuid",
                            "resource_id": "vol-0123456789abcdef0",
                            "resource_type": "ebs_volume",
                            "resource_name": "unused-volume",
                            "region": "us-east-1",
                            "status": "active",
                            "estimated_monthly_cost": 8.00,
                            "details": {"size_gb": 100, "state": "available"},
                            "reason": "Volume not attached to any instance for 30+ days",
                            "detected_at": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }
        },
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        404: {"description": "Cloud account not found", "content": {"application/json": {"example": {"detail": "Cloud account not found"}}}},
    }
)
async def list_orphan_resources(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    paywall_ctx: Annotated[PaywallContext, Depends(get_paywall_context)],
    cloud_account_id: uuid.UUID | None = Query(None),
    status_filter: ResourceStatus | None = Query(None, alias="status"),
    resource_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> list[OrphanResource]:
    """
    List orphan resources.

    Can filter by cloud account, status, and resource type.
    """
    if cloud_account_id:
        # Verify account belongs to user
        account = await cloud_account_crud.get_cloud_account_by_id(
            db, cloud_account_id, current_user.id
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cloud account not found",
            )

        resources = await orphan_resource_crud.get_orphan_resources_by_account(
            db, cloud_account_id, status_filter, resource_type, skip, limit
        )
    else:
        # Get resources for all user's accounts
        # Only show resources from the latest scan per account
        from app.models.cloud_account import CloudAccount
        from app.models.orphan_resource import OrphanResource as OrphanResourceModel
        from app.models.scan import Scan
        from sqlalchemy import select, and_, func

        # Subquery to get the latest ORPHAN scan ID per cloud account
        # Filter out INVENTORY scans to avoid interference
        latest_scan_subquery = (
            select(
                Scan.cloud_account_id,
                func.max(Scan.created_at).label("max_created_at")
            )
            .where(
                Scan.status == "completed",
                Scan.scan_type != "inventory"
            )
            .group_by(Scan.cloud_account_id)
            .subquery()
        )

        latest_scan_ids = (
            select(Scan.id)
            .join(
                latest_scan_subquery,
                and_(
                    Scan.cloud_account_id == latest_scan_subquery.c.cloud_account_id,
                    Scan.created_at == latest_scan_subquery.c.max_created_at
                )
            )
            .subquery()
        )

        query = (
            select(OrphanResourceModel)
            .join(CloudAccount)
            .where(
                and_(
                    CloudAccount.user_id == current_user.id,
                    OrphanResourceModel.scan_id.in_(select(latest_scan_ids))
                )
            )
        )

        if status_filter:
            query = query.where(OrphanResourceModel.status == status_filter.value)

        if resource_type:
            query = query.where(OrphanResourceModel.resource_type == resource_type)

        result = await db.execute(query.offset(skip).limit(limit))
        resources = list(result.scalars().all())

    # Redact resource details for free-tier users (only for post-paywall resources)
    if not paywall_ctx.is_paid:
        return [
            redact_orphan_resource(r) if r.created_at >= paywall_ctx.paywall_cutoff_date
            else OrphanResource.model_validate(r)
            for r in resources
        ]

    return resources


@router.get(
    "/stats",
    response_model=OrphanResourceStats,
    summary="Get orphaned resource statistics",
    description="""
Get aggregated statistics about orphaned resources across all or specific cloud accounts.

## Statistics Included
- **total_resources**: Total count of orphaned resources
- **total_estimated_cost**: Sum of all estimated monthly costs
- **by_provider**: Breakdown by cloud provider (AWS, Azure, GCP, M365)
- **by_type**: Breakdown by resource type (EC2, EBS, RDS, etc.)
- **by_region**: Breakdown by cloud region
- **by_status**: Breakdown by status (active, ignored, marked_for_deletion)

## Filters
- **cloud_account_id**: Get stats for specific account only
- **status**: Filter by resource status

## Use Cases
- Dashboard summary cards
- Cost savings reports
- Resource distribution charts
""",
    response_description="Aggregated statistics of orphaned resources",
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_resources": 45,
                        "total_estimated_cost": 1250.00,
                        "by_provider": {"aws": 30, "azure": 10, "gcp": 5},
                        "by_type": {"ebs_volume": 20, "ec2_instance": 10, "rds_instance": 5},
                        "by_region": {"us-east-1": 25, "eu-west-1": 20},
                        "by_status": {"active": 40, "ignored": 3, "marked_for_deletion": 2}
                    }
                }
            }
        },
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        404: {"description": "Cloud account not found", "content": {"application/json": {"example": {"detail": "Cloud account not found"}}}},
    }
)
async def get_orphan_resource_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    cloud_account_id: uuid.UUID | None = Query(None),
    status_filter: ResourceStatus | None = Query(None, alias="status"),
) -> OrphanResourceStats:
    """
    Get orphan resource statistics.

    Optionally filter by cloud account and status.
    """
    if cloud_account_id:
        # Verify account belongs to user
        account = await cloud_account_crud.get_cloud_account_by_id(
            db, cloud_account_id, current_user.id
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cloud account not found",
            )

    stats = await orphan_resource_crud.get_orphan_resource_statistics(
        db, cloud_account_id, status_filter, user_id=current_user.id
    )
    return OrphanResourceStats(**stats)


@router.get(
    "/top-cost",
    response_model=list[OrphanResource],
    summary="Get highest-cost orphaned resources",
    description="""
Get the most expensive orphaned resources sorted by estimated monthly cost.

Perfect for **quick wins** - identify resources that will save the most money if cleaned up.

## Sorting
Resources are sorted by `estimated_monthly_cost` in descending order (highest first).

## Filters
- **cloud_account_id**: Filter by specific cloud account
- **limit**: Number of results to return (1-50, default 10)

## Use Cases
- Prioritize cleanup efforts
- Quick wins dashboard
- Executive cost savings reports
- "Low-hanging fruit" identification

## Example Response
Returns resources like idle RDS instances ($500/month), unused NAT Gateways ($45/month),
detached EBS volumes ($8/month) sorted by cost.
""",
    response_description="List of top resources by cost",
    responses={
        200: {
            "description": "Top cost resources retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "uuid-1",
                            "resource_type": "rds_instance",
                            "resource_name": "staging-db-unused",
                            "region": "us-east-1",
                            "estimated_monthly_cost": 487.20,
                            "reason": "Database instance with no connections for 30+ days",
                            "status": "active"
                        },
                        {
                            "id": "uuid-2",
                            "resource_type": "nat_gateway",
                            "resource_name": "unused-nat",
                            "region": "eu-west-1",
                            "estimated_monthly_cost": 45.00,
                            "reason": "NAT Gateway with no traffic",
                            "status": "active"
                        }
                    ]
                }
            }
        },
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        404: {"description": "Cloud account not found", "content": {"application/json": {"example": {"detail": "Cloud account not found"}}}},
    }
)
async def get_top_cost_resources(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    paywall_ctx: Annotated[PaywallContext, Depends(get_paywall_context)],
    cloud_account_id: uuid.UUID | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
) -> list[OrphanResource]:
    """
    Get top orphan resources by estimated monthly cost.

    Requires Pro or Enterprise subscription.
    """
    if not paywall_ctx.is_paid:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Top cost resources require a Pro or Enterprise subscription.",
        )

    if cloud_account_id:
        # Verify account belongs to user
        account = await cloud_account_crud.get_cloud_account_by_id(
            db, cloud_account_id, current_user.id
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cloud account not found",
            )

    resources = await orphan_resource_crud.get_top_cost_resources(
        db, cloud_account_id, limit, user_id=current_user.id
    )
    return resources


@router.get(
    "/{resource_id}",
    response_model=OrphanResource,
    summary="Get specific orphaned resource",
    description="""
Retrieve detailed information about a specific orphaned resource.

Includes all resource metadata, cost estimates, detection reason, and current status.

## Access Control
Only accessible if the resource belongs to one of the user's cloud accounts.

## Response Fields
- **resource_id**: Cloud provider's resource ID (e.g., "vol-0123abc")
- **resource_type**: Type of resource (e.g., "ebs_volume", "ec2_instance")
- **resource_name**: Human-readable name or tag
- **region**: Cloud region where resource exists
- **estimated_monthly_cost**: Estimated cost if resource remains orphaned
- **details**: Provider-specific metadata (size, state, tags, etc.)
- **reason**: Why this resource was flagged as orphaned
- **detected_at**: When resource was first detected
- **status**: Current status (active, ignored, marked_for_deletion, deleted)
""",
    response_description="Detailed resource information",
    responses={
        200: {
            "description": "Resource retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "scan_id": "scan-uuid",
                        "cloud_account_id": "account-uuid",
                        "resource_id": "vol-0123456789abcdef0",
                        "resource_type": "ebs_volume",
                        "resource_name": "old-backup-volume",
                        "region": "us-east-1",
                        "status": "active",
                        "estimated_monthly_cost": 8.00,
                        "details": {
                            "size_gb": 100,
                            "state": "available",
                            "volume_type": "gp2",
                            "tags": {"Environment": "staging"}
                        },
                        "reason": "Volume not attached to any instance for 30+ days",
                        "detected_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        403: {"description": "Not authorized to view this resource", "content": {"application/json": {"example": {"detail": "Not authorized to view this resource"}}}},
        404: {"description": "Resource not found", "content": {"application/json": {"example": {"detail": "Orphan resource not found"}}}},
    }
)
async def get_orphan_resource(
    resource_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    paywall_ctx: Annotated[PaywallContext, Depends(get_paywall_context)],
) -> OrphanResource:
    """
    Get a specific orphan resource by ID.

    Requires Pro or Enterprise subscription.
    """
    if not paywall_ctx.is_paid:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Resource details require a Pro or Enterprise subscription.",
        )

    resource = await orphan_resource_crud.get_orphan_resource_by_id(db, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orphan resource not found",
        )

    # Verify resource belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, resource.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this resource",
        )

    return resource


@router.patch(
    "/{resource_id}",
    response_model=OrphanResource,
    summary="Update orphaned resource status",
    description="""
Update the status of an orphaned resource to manage cleanup workflow.

## Common Operations
- **Mark as ignored**: Prevent resource from appearing in future reports
- **Mark for deletion**: Flag resource for cleanup (manual or automated)
- **Reactivate**: Change status back to active if needed

## Status Transitions
- **active** → **ignored**: Resource is intentional, not orphaned
- **active** → **marked_for_deletion**: Resource ready for cleanup
- **ignored** → **active**: Re-include in reports
- **marked_for_deletion** → **deleted**: After manual deletion in cloud

## Machine Learning
Status updates are tracked for ML-based detection improvement. The system learns from
your decisions to better identify orphaned resources in future scans.

## Access Control
Only accessible if the resource belongs to one of the user's cloud accounts.

## Request Body
Update any of these fields:
- **status**: New status (active, ignored, marked_for_deletion, deleted)
- **notes**: Optional user notes about the decision
""",
    response_description="Updated resource with new status",
    responses={
        200: {
            "description": "Resource updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "resource_id": "vol-0123456789abcdef0",
                        "resource_type": "ebs_volume",
                        "status": "ignored",
                        "reason": "Volume not attached to any instance for 30+ days",
                        "notes": "This volume is used for manual backups",
                        "updated_at": "2024-01-15T11:00:00Z"
                    }
                }
            }
        },
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        403: {"description": "Not authorized to update this resource", "content": {"application/json": {"example": {"detail": "Not authorized to update this resource"}}}},
        404: {"description": "Resource not found", "content": {"application/json": {"example": {"detail": "Orphan resource not found"}}}},
        422: {"description": "Invalid status value", "content": {"application/json": {"example": {"detail": [{"loc": ["body", "status"], "msg": "Invalid status"}]}}}},
    }
)
async def update_orphan_resource(
    resource_id: uuid.UUID,
    resource_update: OrphanResourceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_paid_for_resource_actions)],
) -> OrphanResource:
    """
    Update an orphan resource (e.g., mark as ignored or for deletion).
    """
    resource = await orphan_resource_crud.get_orphan_resource_by_id(db, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orphan resource not found",
        )

    # Verify resource belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, resource.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this resource",
        )

    updated_resource = await orphan_resource_crud.update_orphan_resource(
        db, resource_id, resource_update
    )

    if not updated_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orphan resource not found",
        )

    # Track user action for ML if status was updated
    if resource_update.status:
        try:
            # Map status to action for ML tracking
            action_mapping = {
                ResourceStatus.DELETED: "deleted",
                ResourceStatus.IGNORED: "ignored",
                ResourceStatus.ACTIVE: "kept",
                ResourceStatus.MARKED_FOR_DELETION: "deleted",  # Treat as deleted for ML
            }
            action = action_mapping.get(ResourceStatus(resource_update.status), "kept")

            await track_user_action(
                resource=updated_resource,
                action=action,
                user=current_user,
                cloud_account=account,
                db=db,
            )
        except Exception as e:
            # Log but don't fail the request
            print(f"⚠️ Failed to track user action: {e}")

    return updated_resource


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete orphaned resource record",
    description="""
Delete an orphaned resource record from the database.

**⚠️ Important**: This endpoint only deletes the **record** from CutCosts database.
It does **NOT** delete the actual resource in your cloud provider.

## Use Cases
- Remove false positives from reports
- Clean up records after manually deleting resources in cloud
- Remove outdated scan results

## To Delete Actual Cloud Resources
1. Use PATCH endpoint to mark resource as `marked_for_deletion`
2. Manually delete the resource in your cloud provider console/CLI
3. Update status to `deleted` or use this endpoint to remove the record

## Access Control
Only accessible if the resource belongs to one of the user's cloud accounts.

## Response
Returns `204 No Content` on success (no response body).
""",
    response_description="Resource record deleted successfully",
    responses={
        204: {"description": "Resource record deleted (no content returned)"},
        401: {"description": "Authentication required", "content": {"application/json": {"example": {"detail": "Could not validate credentials"}}}},
        403: {"description": "Not authorized to delete this resource", "content": {"application/json": {"example": {"detail": "Not authorized to delete this resource"}}}},
        404: {"description": "Resource not found", "content": {"application/json": {"example": {"detail": "Orphan resource not found"}}}},
    }
)
async def delete_orphan_resource(
    resource_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_paid_for_resource_actions)],
) -> None:
    """
    Delete an orphan resource record.

    Note: This only removes the record from our database, it does not
    delete the actual cloud resource.
    """
    resource = await orphan_resource_crud.get_orphan_resource_by_id(db, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orphan resource not found",
        )

    # Verify resource belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, resource.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this resource",
        )

    await orphan_resource_crud.delete_orphan_resource(db, resource_id)
