"""Scan API endpoints."""

import uuid
from typing import Annotated

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.rate_limit import scan_limit
from app.core.subscription_dependencies import check_scan_limit
from app.crud import cloud_account as cloud_account_crud
from app.crud import scan as scan_crud
from app.models.scan import ScanType
from app.models.user import User
from app.schemas.scan import Scan, ScanCreate, ScanProgress, ScanSummary, ScanWithResources
from app.services.subscription_service import SubscriptionService
from app.workers.celery_app import celery_app
from app.workers.tasks import scan_cloud_account

router = APIRouter()


@router.post(
    "/",
    response_model=Scan,
    status_code=status.HTTP_201_CREATED,
    summary="Create scan job",
    description="""
Create a new scan job to detect orphaned cloud resources.

## Process
1. Validates cloud account ownership
2. Checks subscription scan limits
3. Creates scan record
4. Queues async Celery task
5. Returns scan details with task ID

Scans run asynchronously in the background. Use `/scans/{scan_id}/progress` to monitor progress.

## Subscription Limits
- **Free**: 10 scans/month
- **Pro**: 100 scans/month
- **Enterprise**: Unlimited

## Rate Limiting
Limited to 10 scans per hour per user.
""",
    response_description="Scan job created and queued",
    responses={
        201: {
            "description": "Scan created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "scan-123",
                        "cloud_account_id": "account-456",
                        "status": "pending",
                        "scan_type": "manual",
                        "celery_task_id": "task-789",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Cloud account is inactive",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account is inactive"}
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Scan limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Monthly scan limit reached. Your Free plan allows 10 scans/month."}
                }
            }
        },
        404: {
            "description": "Cloud account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found or you don't have permission to access it"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 10 per 1 hour"}
                }
            }
        }
    }
)
@scan_limit
async def create_scan(
    request: Request,
    response: Response,
    scan_in: ScanCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(check_scan_limit)],
) -> Scan:
    """
    Create a new scan job for a cloud account.

    Validates that the account belongs to the current user and queues
    a background task to perform the scan.

    Checks subscription limits before allowing scan.
    """
    # Verify account belongs to user
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, scan_in.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found or you don't have permission to access it",
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cloud account is inactive",
        )

    # Increment scan usage counter BEFORE creating scan to prevent race condition
    # This ensures parallel requests cannot bypass the limit check
    subscription_service = SubscriptionService(db)
    await subscription_service.increment_scan_usage(current_user.id)
    await db.commit()  # Commit immediately to persist the counter

    # Create scan record
    scan = await scan_crud.create_scan(db, scan_in)

    # Ensure database transaction is fully committed before queuing task
    await db.commit()

    # Queue background task and store task ID
    task = scan_cloud_account.delay(str(scan.id), str(account.id))
    scan.celery_task_id = task.id
    await db.commit()

    return scan


class InventoryScanRequest(BaseModel):
    """Request schema for inventory scan."""
    cloud_account_id: uuid.UUID


@router.post(
    "/inventory",
    response_model=Scan,
    status_code=status.HTTP_201_CREATED,
    summary="Create inventory scan",
    description="""
Create comprehensive inventory scan for Cost Optimization Hub.

## Difference from Regular Scan
- **Regular scan** (`POST /scans`): Detects orphaned/wasted resources only
- **Inventory scan** (`POST /scans/inventory`): Scans ALL resources for cost optimization

## Use Cases
- Complete resource inventory
- Cost breakdown analysis
- Optimization recommendations
- Resource utilization reports

**Rate Limited**: 10 scans per hour per user.
""",
    response_description="Inventory scan job created",
    responses={
        201: {
            "description": "Inventory scan created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "scan-123",
                        "cloud_account_id": "account-456",
                        "status": "pending",
                        "scan_type": "inventory",
                        "celery_task_id": "task-789",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Cloud account is inactive",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account is inactive"}
                }
            }
        },
        403: {
            "description": "Scan limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Monthly scan limit reached"}
                }
            }
        },
        404: {
            "description": "Cloud account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found or you don't have permission to access it"}
                }
            }
        }
    }
)
@scan_limit
async def create_inventory_scan(
    request: Request,
    response: Response,
    scan_request: InventoryScanRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(check_scan_limit)],
) -> Scan:
    """
    Create a new inventory scan job for Cost Optimization Hub.

    This endpoint triggers a comprehensive inventory scan that collects
    ALL cloud resources (not just orphaned ones) for cost optimization analysis.

    Difference from regular scan:
    - Regular scan: Detects orphaned/wasted resources → Waste Detection tab
    - Inventory scan: Scans ALL resources → Cost Optimization Hub tab

    Checks subscription limits before allowing scan.

    Args:
        cloud_account_id: UUID of the cloud account to scan

    Returns:
        Scan object with scan_type='inventory'
    """
    # Verify account belongs to user
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, scan_request.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found or you don't have permission to access it",
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cloud account is inactive",
        )

    # Create inventory scan record
    from app.schemas.scan import ScanCreate

    scan_in = ScanCreate(
        cloud_account_id=scan_request.cloud_account_id,
        scan_type=ScanType.INVENTORY  # Key difference: INVENTORY type
    )

    scan = await scan_crud.create_scan(db, scan_in)

    # Increment scan usage counter
    subscription_service = SubscriptionService(db)
    await subscription_service.increment_scan_usage(current_user.id)

    # Ensure database transaction is fully committed before queuing task
    await db.commit()

    # Queue background task and store task ID
    task = scan_cloud_account.delay(str(scan.id), str(account.id))
    scan.celery_task_id = task.id
    await db.commit()

    return scan


@router.get(
    "/",
    response_model=list[Scan],
    summary="List all scans",
    description="""
List all scans for the current user's cloud accounts.

Supports pagination with `skip` and `limit` parameters.
""",
    response_description="List of scans",
    responses={
        200: {
            "description": "Scans retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "scan-123",
                            "cloud_account_id": "account-456",
                            "status": "completed",
                            "scan_type": "manual",
                            "total_resources_scanned": 1547,
                            "orphan_resources_found": 23,
                            "estimated_monthly_waste": 457.89,
                            "created_at": "2024-01-15T10:30:00Z",
                            "completed_at": "2024-01-15T10:42:00Z"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
async def list_scans(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> list[Scan]:
    """
    List all scans for the current user's cloud accounts.
    """
    scans = await scan_crud.get_scans_by_user(db, current_user.id, skip, limit)
    return scans


@router.get(
    "/summary",
    response_model=ScanSummary,
    summary="Get scan statistics",
    description="""
Get aggregated scan statistics and summary.

Optionally filter by cloud account ID.

Returns total scans, resources found, estimated waste, etc.
""",
    response_description="Scan summary statistics",
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_scans": 45,
                        "completed_scans": 42,
                        "failed_scans": 2,
                        "pending_scans": 1,
                        "total_resources_scanned": 68542,
                        "total_orphan_resources_found": 387,
                        "total_estimated_monthly_waste": 15678.45,
                        "last_scan_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        404: {
            "description": "Cloud account not found (if cloud_account_id provided)",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def get_scan_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    cloud_account_id: uuid.UUID | None = Query(None),
) -> ScanSummary:
    """
    Get scan summary statistics.

    Optionally filter by cloud account ID.
    """
    # If cloud_account_id provided, verify it belongs to user
    if cloud_account_id:
        account = await cloud_account_crud.get_cloud_account_by_id(
            db, cloud_account_id, current_user.id
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cloud account not found",
            )

    stats = await scan_crud.get_scan_statistics(db, cloud_account_id, user_id=current_user.id)
    return ScanSummary(**stats)


@router.get(
    "/{scan_id}",
    response_model=ScanWithResources,
    summary="Get scan details",
    description="""
Get detailed scan information including all detected orphan resources.

Returns scan metadata, statistics, and full list of orphaned resources found.
""",
    response_description="Scan details with resources",
    responses={
        200: {
            "description": "Scan found",
            "content": {
                "application/json": {
                    "example": {
                        "id": "scan-123",
                        "cloud_account_id": "account-456",
                        "status": "completed",
                        "total_resources_scanned": 1547,
                        "orphan_resources_found": 23,
                        "estimated_monthly_waste": 457.89,
                        "orphan_resources": [
                            {
                                "id": "resource-001",
                                "resource_type": "ebs_volume_unattached",
                                "resource_id": "vol-0abc123",
                                "region": "us-east-1",
                                "estimated_monthly_cost": 32.00
                            }
                        ],
                        "completed_at": "2024-01-15T10:42:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Not authorized to view this scan",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to view this scan"}
                }
            }
        },
        404: {
            "description": "Scan not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Scan not found"}
                }
            }
        }
    }
)
async def get_scan(
    scan_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ScanWithResources:
    """
    Get a specific scan by ID with its orphan resources.
    """
    scan = await scan_crud.get_scan_by_id(db, scan_id, load_resources=True)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    # Verify scan belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, scan.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this scan",
        )

    return scan


@router.get(
    "/account/{cloud_account_id}",
    response_model=list[Scan],
    summary="List scans by account",
    description="""
List all scans for a specific cloud account.

Supports pagination with `skip` and `limit` parameters.
""",
    response_description="List of scans for the account",
    responses={
        200: {
            "description": "Scans retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "scan-123",
                            "cloud_account_id": "account-456",
                            "status": "completed",
                            "scan_type": "manual",
                            "orphan_resources_found": 23,
                            "created_at": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        404: {
            "description": "Cloud account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def list_scans_by_account(
    cloud_account_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> list[Scan]:
    """
    List all scans for a specific cloud account.
    """
    # Verify account belongs to user
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    scans = await scan_crud.get_scans_by_account(db, cloud_account_id, skip, limit)
    return scans


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all scans",
    description="""
Delete all scans for the current user's cloud accounts.

**Warning**: This will delete all scan history and associated orphan resources.
""",
    response_description="All scans deleted successfully",
    responses={
        204: {
            "description": "All scans deleted (no content)"
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
async def delete_all_scans(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Delete all scans for the current user's cloud accounts.
    """
    # Delete all scans for the user
    await scan_crud.delete_all_scans_by_user(db, current_user.id)


@router.get(
    "/{scan_id}/progress",
    response_model=ScanProgress,
    summary="Get scan progress",
    description="""
Get real-time progress of an ongoing scan.

## Task States
- **PENDING**: Task queued, not started yet
- **PROGRESS**: Task running (includes detailed progress info)
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with error

## Use for Polling
Poll this endpoint every 2-5 seconds to monitor scan progress in real-time.
""",
    response_description="Current scan progress",
    responses={
        200: {
            "description": "Progress retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "in_progress": {
                            "summary": "Scan in progress",
                            "value": {
                                "state": "PROGRESS",
                                "current": 3,
                                "total": 10,
                                "percent": 30,
                                "current_step": "Scanning EC2 instances in us-east-1",
                                "region": "us-east-1",
                                "resources_found": 12,
                                "elapsed_seconds": 45
                            }
                        },
                        "completed": {
                            "summary": "Scan completed",
                            "value": {
                                "state": "SUCCESS",
                                "current": 10,
                                "total": 10,
                                "percent": 100,
                                "current_step": "Completed",
                                "resources_found": 23,
                                "elapsed_seconds": 120
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Not authorized to view this scan",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to view this scan"}
                }
            }
        },
        404: {
            "description": "Scan not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Scan not found"}
                }
            }
        }
    }
)
async def get_scan_progress(
    scan_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ScanProgress:
    """
    Get real-time progress of an ongoing scan.

    Returns Celery task state and progress metadata:
    - PENDING: Task not started yet
    - PROGRESS: Task is running (with detailed progress info)
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed with an error
    """
    # Get scan
    scan = await scan_crud.get_scan_by_id(db, scan_id)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    # Verify scan belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, scan.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this scan",
        )

    # If scan doesn't have a task ID or is already completed/failed, return default state
    if not scan.celery_task_id or scan.status in ["completed", "failed"]:
        return ScanProgress(
            state=scan.status.upper(),
            current=scan.total_resources_scanned,
            total=scan.total_resources_scanned,
            percent=100 if scan.status == "completed" else 0,
            current_step="Completed" if scan.status == "completed" else "Failed",
            region="",
            resources_found=scan.orphan_resources_found,
            elapsed_seconds=0,
        )

    # Get Celery task result
    task_result = AsyncResult(scan.celery_task_id, app=celery_app)

    # Extract progress info from Celery task
    if task_result.state == "PENDING":
        return ScanProgress(
            state="PENDING",
            current=0,
            total=1,
            percent=0,
            current_step="Waiting to start...",
            region="",
            resources_found=0,
            elapsed_seconds=0,
        )
    elif task_result.state == "PROGRESS":
        info = task_result.info or {}
        return ScanProgress(
            state="PROGRESS",
            current=info.get("current", 0),
            total=info.get("total", 1),
            percent=info.get("percent", 0),
            current_step=info.get("current_step", "Processing..."),
            region=info.get("region", ""),
            resources_found=info.get("resources_found", 0),
            elapsed_seconds=info.get("elapsed_seconds", 0),
        )
    elif task_result.state == "SUCCESS":
        return ScanProgress(
            state="SUCCESS",
            current=scan.total_resources_scanned,
            total=scan.total_resources_scanned,
            percent=100,
            current_step="Completed",
            region="",
            resources_found=scan.orphan_resources_found,
            elapsed_seconds=0,
        )
    elif task_result.state == "FAILURE":
        return ScanProgress(
            state="FAILURE",
            current=0,
            total=1,
            percent=0,
            current_step=f"Failed: {str(task_result.info)}",
            region="",
            resources_found=0,
            elapsed_seconds=0,
        )
    else:
        # Unknown state
        return ScanProgress(
            state=task_result.state,
            current=0,
            total=1,
            percent=0,
            current_step=task_result.state,
            region="",
            resources_found=0,
            elapsed_seconds=0,
        )


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete scan",
    description="""
Delete a specific scan and all its associated orphan resources.

**Warning**: This will permanently delete the scan and all detected resources.
""",
    response_description="Scan deleted successfully",
    responses={
        204: {
            "description": "Scan deleted (no content)"
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Not authorized to delete this scan",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to delete this scan"}
                }
            }
        },
        404: {
            "description": "Scan not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Scan not found"}
                }
            }
        }
    }
)
async def delete_scan(
    scan_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Delete a scan and all its associated orphan resources.
    """
    # Get scan to verify ownership
    scan = await scan_crud.get_scan_by_id(db, scan_id)

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    # Verify scan belongs to user's account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db, scan.cloud_account_id, current_user.id
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this scan",
        )

    # Delete scan (cascade will delete orphan resources)
    await scan_crud.delete_scan(db, scan_id)

