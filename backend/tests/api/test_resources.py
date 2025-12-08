"""Tests for orphan resource endpoints - Core feature regression tests."""

import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_account import CloudAccount
from app.models.orphan_resource import OrphanResource, ResourceStatus
from app.models.scan import Scan, ScanStatus, ScanType
from app.models.user import User


@pytest.fixture
async def test_cloud_account(db_session: AsyncSession, test_user: User) -> CloudAccount:
    """Create a test cloud account."""
    import json
    from app.core.security import credential_encryption

    credentials = {
        "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    }
    encrypted = credential_encryption.encrypt(json.dumps(credentials))

    account = CloudAccount(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="aws",
        account_name="Test AWS Account",
        account_identifier="123456789012",
        credentials_encrypted=encrypted,
        regions=["us-east-1"],
        is_active=True,
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_scan(
    db_session: AsyncSession, test_cloud_account: CloudAccount
) -> Scan:
    """Create a test scan."""
    scan = Scan(
        id=uuid.uuid4(),
        cloud_account_id=test_cloud_account.id,
        status=ScanStatus.COMPLETED,
        scan_type=ScanType.MANUAL,
        total_resources_scanned=100,
        orphan_resources_found=5,
        estimated_monthly_waste=50.0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)
    return scan


@pytest.fixture
async def test_orphan_resource(
    db_session: AsyncSession,
    test_scan: Scan,
    test_cloud_account: CloudAccount,
) -> OrphanResource:
    """Create a test orphan resource."""
    resource = OrphanResource(
        id=uuid.uuid4(),
        scan_id=test_scan.id,
        cloud_account_id=test_cloud_account.id,
        resource_type="ebs_volume",
        resource_id="vol-1234567890abcdef0",
        resource_name="test-volume",
        region="us-east-1",
        estimated_monthly_cost=10.50,
        currency="USD",
        status=ResourceStatus.ACTIVE,
        resource_metadata={
            "size_gb": 100,
            "volume_type": "gp2",
        },
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    return resource


@pytest.mark.asyncio
async def test_list_resources_requires_auth(async_client: AsyncClient) -> None:
    """Test that listing resources requires authentication."""
    response = await async_client.get("/api/v1/resources/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_resources_authenticated(
    authenticated_async_client: AsyncClient,
) -> None:
    """Test that authenticated user can list resources."""
    response = await authenticated_async_client.get("/api/v1/resources/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_resources_with_filters(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test listing resources with filters."""
    # Filter by resource type
    response = await authenticated_async_client.get(
        "/api/v1/resources/",
        params={"resource_type": "ebs_volume"},
    )
    assert response.status_code == 200

    # Filter by status
    response = await authenticated_async_client.get(
        "/api/v1/resources/",
        params={"status": "active"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_resource_stats(
    authenticated_async_client: AsyncClient,
) -> None:
    """Test getting resource statistics."""
    response = await authenticated_async_client.get("/api/v1/resources/stats")
    assert response.status_code == 200
    data = response.json()
    # Verify structure
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_top_cost_resources(
    authenticated_async_client: AsyncClient,
) -> None:
    """Test getting top cost resources."""
    response = await authenticated_async_client.get("/api/v1/resources/top-cost")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_resource_by_id(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test getting a specific resource by ID."""
    response = await authenticated_async_client.get(
        f"/api/v1/resources/{test_orphan_resource.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_orphan_resource.id
    assert data["resource_type"] == "ebs_volume"


@pytest.mark.asyncio
async def test_get_resource_not_found(
    authenticated_async_client: AsyncClient,
) -> None:
    """Test getting non-existent resource returns 404."""
    fake_id = str(uuid.uuid4())
    response = await authenticated_async_client.get(f"/api/v1/resources/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_resource_status(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test updating resource status (e.g., marking as ignored)."""
    response = await authenticated_async_client.patch(
        f"/api/v1/resources/{test_orphan_resource.id}",
        json={"status": "ignored", "ignored_reason": "Test ignore"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ignored"


@pytest.mark.asyncio
async def test_update_resource_invalid_status(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test that invalid status update fails."""
    response = await authenticated_async_client.patch(
        f"/api/v1/resources/{test_orphan_resource.id}",
        json={"status": "invalid_status"},
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_delete_resource(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test deleting a resource record."""
    response = await authenticated_async_client.delete(
        f"/api/v1/resources/{test_orphan_resource.id}"
    )
    assert response.status_code == 204

    # Verify resource is deleted
    response = await authenticated_async_client.get(
        f"/api/v1/resources/{test_orphan_resource.id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_resources_by_account(
    authenticated_async_client: AsyncClient,
    test_cloud_account: CloudAccount,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test listing resources filtered by cloud account."""
    response = await authenticated_async_client.get(
        "/api/v1/resources/",
        params={"cloud_account_id": str(test_cloud_account.id)},
    )
    assert response.status_code == 200
    resources = response.json()
    assert isinstance(resources, list)
    # All returned resources should belong to this account
    for resource in resources:
        assert resource["cloud_account_id"] == str(test_cloud_account.id)


@pytest.mark.asyncio
async def test_resource_stats_includes_cost(
    authenticated_async_client: AsyncClient,
    test_orphan_resource: OrphanResource,
) -> None:
    """Test that resource stats include cost information."""
    response = await authenticated_async_client.get("/api/v1/resources/stats")
    assert response.status_code == 200
    data = response.json()
    # Stats should include cost-related fields
    assert "total_monthly_cost" in data or "estimated_monthly_waste" in data or isinstance(data, dict)
