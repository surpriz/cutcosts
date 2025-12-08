"""Tests for health check endpoint - CRITICAL for PROD deployment."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(async_client: AsyncClient) -> None:
    """Test that /api/v1/health returns 200 - CRITICAL for PROD health checks."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_returns_healthy_status(async_client: AsyncClient) -> None:
    """Test that /api/v1/health returns 'healthy' status."""
    response = await async_client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_endpoint_returns_service_name(async_client: AsyncClient) -> None:
    """Test that health endpoint returns service name."""
    response = await async_client.get("/api/v1/health")
    data = response.json()
    assert "service" in data
    assert data["service"] is not None


@pytest.mark.asyncio
async def test_health_endpoint_returns_environment(async_client: AsyncClient) -> None:
    """Test that health endpoint returns environment."""
    response = await async_client.get("/api/v1/health")
    data = response.json()
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_endpoint_no_auth_required(async_client: AsyncClient) -> None:
    """Test that health endpoint does not require authentication."""
    # No auth header provided, should still work
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_endpoint_returns_200(async_client: AsyncClient) -> None:
    """Test that root endpoint returns 200."""
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_docs_accessible(async_client: AsyncClient) -> None:
    """Test that API docs endpoint is accessible."""
    response = await async_client.get("/api/docs")
    # Docs endpoint redirects or returns HTML
    assert response.status_code in [200, 307]
