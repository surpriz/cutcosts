"""Orphan resource Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.orphan_resource import ResourceStatus


class OrphanResourceBase(BaseModel):
    """Base orphan resource schema."""

    resource_type: str = Field(description="Type of resource (e.g., ebs_volume)")
    resource_id: str | None = Field(default=None, description="Unique resource identifier")
    resource_name: str | None = Field(default=None, description="Human-readable name")
    region: str = Field(description="Cloud region")
    estimated_monthly_cost: float | None = Field(
        default=None, description="Monthly cost in USD"
    )
    resource_metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )


class OrphanResourceCreate(BaseModel):
    """Schema for creating an orphan resource."""

    resource_type: str
    resource_id: str
    resource_name: str | None = None
    region: str
    estimated_monthly_cost: float
    resource_metadata: dict[str, Any] | None = None
    scan_id: uuid.UUID
    cloud_account_id: uuid.UUID


class OrphanResourceUpdate(BaseModel):
    """Schema for updating an orphan resource."""

    status: ResourceStatus | None = None
    resource_name: str | None = None


class OrphanResource(OrphanResourceBase):
    """Schema for orphan resource response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    cloud_account_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    is_redacted: bool = Field(
        default=False,
        description="True when sensitive fields are hidden for free tier",
    )


def redact_orphan_resource(orm_obj: Any) -> OrphanResource:
    """Serialize an ORM orphan resource with sensitive fields nulled (free tier).

    Keeps: id, resource_type, region, status, created_at, updated_at, scan_id,
           cloud_account_id.
    Nullifies: resource_id, resource_name, estimated_monthly_cost, resource_metadata.
    """
    full = OrphanResource.model_validate(orm_obj)
    return full.model_copy(update={
        "resource_id": None,
        "resource_name": None,
        "estimated_monthly_cost": None,
        "resource_metadata": None,
        "is_redacted": True,
    })


class OrphanResourceStats(BaseModel):
    """Schema for orphan resource statistics."""

    total_resources: int
    by_type: dict[str, int]
    by_region: dict[str, int]
    by_status: dict[str, int]
    total_monthly_cost: float
    total_annual_cost: float


class ResourceCostBreakdown(BaseModel):
    """Schema for resource cost breakdown."""

    resource_type: str
    count: int
    total_monthly_cost: float
    percentage: float
