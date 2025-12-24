"""Cloud accounts API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.rate_limit import api_default_limit
from app.core.subscription_dependencies import check_cloud_account_limit
from app.crud import cloud_account as cloud_account_crud
from app.models.user import User
from app.schemas.cloud_account import (
    AWSCredentials,
    AzureCredentials,
    GCPCredentials,
    Microsoft365Credentials,
    CloudAccount,
    CloudAccountCreate,
    CloudAccountUpdate,
)
from app.services.aws_validator import AWSValidationError, validate_aws_credentials
from app.services.azure_validator import AzureValidationError, validate_azure_credentials
from app.services.microsoft365_validator import (
    Microsoft365ValidationError,
    validate_microsoft365_credentials,
)

router = APIRouter()


@router.post(
    "/",
    response_model=CloudAccount,
    status_code=status.HTTP_201_CREATED,
    summary="Create cloud account",
    description="""
Connect a cloud provider account to CloudWaste for resource waste detection.

## Supported Providers
- **AWS**: Access Key ID + Secret Access Key
- **Azure**: Service Principal (Tenant ID, Client ID, Client Secret, Subscription ID)
- **GCP**: Service Account JSON key
- **Microsoft 365**: App Registration credentials

## Process
1. Checks subscription limits
2. Validates credentials with provider
3. Encrypts credentials using Fernet
4. Stores account configuration

**Note**: Credentials are never returned in responses.

## Subscription Limits
- **Free**: 1 account
- **Pro**: 5 accounts
- **Enterprise**: Unlimited
""",
    response_description="Cloud account created with encrypted credentials",
    responses={
        201: {
            "description": "Account created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "987e6543-e21b-12d3-a456-426614174000",
                        "provider": "aws",
                        "account_name": "Production AWS",
                        "account_identifier": "123456789012",
                        "regions": ["us-east-1", "eu-west-1"],
                        "is_active": True,
                        "scheduled_scan_enabled": False,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid credentials or missing required fields",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Credentials validation failed",
                            "value": {"detail": "AWS credentials validation failed: Invalid access key ID"}
                        },
                        "missing_fields": {
                            "summary": "Missing required fields",
                            "value": {"detail": "AWS Access Key ID and Secret Access Key are required for AWS accounts"}
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
            "description": "Subscription limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account limit reached. Your Free plan allows 1 account. Upgrade to Pro for 5 accounts."}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_pattern_mismatch",
                                "loc": ["body", "provider"],
                                "msg": "String should match pattern '^(aws|azure|gcp|microsoft365)$'"
                            }
                        ]
                    }
                }
            }
        }
    }
)
@api_default_limit
async def create_cloud_account(
    request: Request,
    response: Response,
    account_in: CloudAccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(check_cloud_account_limit)],
) -> CloudAccount:
    """
    Create a new cloud account connection.

    This endpoint:
    1. Checks subscription limits for cloud accounts
    2. Validates the provided credentials
    3. Encrypts the credentials before storage
    4. Creates the cloud account record

    Args:
        account_in: Cloud account creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created cloud account (without credentials)

    Raises:
        HTTPException: If validation fails, limit exceeded, or account creation fails
    """
    # Validate credentials before storing
    if account_in.provider == "aws":
        if not account_in.aws_access_key_id or not account_in.aws_secret_access_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AWS Access Key ID and Secret Access Key are required for AWS accounts",
            )

        # Validate AWS credentials
        try:
            credentials = AWSCredentials(
                access_key_id=account_in.aws_access_key_id,
                secret_access_key=account_in.aws_secret_access_key,
                region=account_in.regions[0] if account_in.regions else "us-east-1",
            )
            account_info = await validate_aws_credentials(credentials)

            # Optionally update account_identifier with actual AWS account ID
            if not account_in.account_identifier:
                account_in.account_identifier = account_info["account_id"]

        except AWSValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AWS credentials validation failed: {str(e)}",
            )

    elif account_in.provider == "azure":
        if (
            not account_in.azure_tenant_id
            or not account_in.azure_client_id
            or not account_in.azure_client_secret
            or not account_in.azure_subscription_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Azure Tenant ID, Client ID, Client Secret, and Subscription ID are required for Azure accounts",
            )

        # Validate Azure credentials
        try:
            credentials = AzureCredentials(
                tenant_id=account_in.azure_tenant_id,
                client_id=account_in.azure_client_id,
                client_secret=account_in.azure_client_secret,
                subscription_id=account_in.azure_subscription_id,
            )
            subscription_info = await validate_azure_credentials(credentials)

            # Optionally update account_identifier with subscription ID
            if not account_in.account_identifier:
                account_in.account_identifier = subscription_info["subscription_id"]

        except AzureValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Azure credentials validation failed: {str(e)}",
            )

    elif account_in.provider == "gcp":
        if not account_in.gcp_project_id or not account_in.gcp_service_account_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GCP Project ID and Service Account JSON are required for GCP accounts",
            )

        # For MVP, we skip validation and directly create the account
        # GCP validation will be implemented in Phase 2
        if not account_in.account_identifier:
            account_in.account_identifier = account_in.gcp_project_id

    elif account_in.provider == "microsoft365":
        if (
            not account_in.microsoft365_tenant_id
            or not account_in.microsoft365_client_id
            or not account_in.microsoft365_client_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Microsoft 365 Tenant ID, Client ID, and Client Secret are required for Microsoft 365 accounts",
            )

        # Validate Microsoft 365 credentials
        try:
            credentials = Microsoft365Credentials(
                tenant_id=account_in.microsoft365_tenant_id,
                client_id=account_in.microsoft365_client_id,
                client_secret=account_in.microsoft365_client_secret,
            )
            org_info = await validate_microsoft365_credentials(credentials)

            # Use tenant_id as account_identifier
            if not account_in.account_identifier:
                account_in.account_identifier = org_info["tenant_id"]

        except Microsoft365ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Microsoft 365 credentials validation failed: {str(e)}",
            )

    # Create cloud account with encrypted credentials
    try:
        cloud_account = await cloud_account_crud.create_cloud_account(
            db=db,
            user_id=current_user.id,
            account_in=account_in,
        )
        return cloud_account

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/validate-credentials",
    response_model=dict,
    summary="Validate credentials",
    description="""
Test cloud provider credentials without creating an account.

Use this endpoint to verify credentials are valid before submitting account creation.
Provides immediate feedback on credential validity.

**No authentication required** - can be used before registration.
""",
    response_description="Credentials are valid",
    responses={
        200: {
            "description": "Credentials validated successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "aws": {
                            "summary": "AWS validation success",
                            "value": {
                                "valid": True,
                                "provider": "aws",
                                "account_id": "123456789012",
                                "message": "✅ AWS credentials are valid! Account ID: 123456789012"
                            }
                        },
                        "azure": {
                            "summary": "Azure validation success",
                            "value": {
                                "valid": True,
                                "provider": "azure",
                                "subscription_id": "abc-123",
                                "subscription_name": "Production",
                                "message": "✅ Azure credentials are valid! Subscription: Production"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid credentials or missing fields",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_aws": {
                            "summary": "Invalid AWS credentials",
                            "value": {"detail": "❌ AWS validation failed: Invalid access key ID"}
                        },
                        "missing_fields": {
                            "summary": "Missing required fields",
                            "value": {"detail": "AWS Access Key ID and Secret Access Key are required"}
                        }
                    }
                }
            }
        }
    }
)
async def validate_credentials_before_creation(
    credentials_data: CloudAccountCreate,
) -> dict:
    """
    Validate cloud provider credentials without creating an account.

    This endpoint allows users to test their credentials before account creation,
    providing immediate feedback on whether the credentials are valid.

    Args:
        credentials_data: Cloud account credentials to validate

    Returns:
        Dict with validation result including provider info

    Raises:
        HTTPException: If validation fails or required fields are missing
    """
    if credentials_data.provider == "aws":
        if not credentials_data.aws_access_key_id or not credentials_data.aws_secret_access_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AWS Access Key ID and Secret Access Key are required",
            )

        credentials = AWSCredentials(
            access_key_id=credentials_data.aws_access_key_id,
            secret_access_key=credentials_data.aws_secret_access_key,
            region=credentials_data.regions[0] if credentials_data.regions else "us-east-1",
        )

        try:
            account_info = await validate_aws_credentials(credentials)
            return {
                "valid": True,
                "provider": "aws",
                "account_id": account_info["account_id"],
                "message": f"✅ AWS credentials are valid! Account ID: {account_info['account_id']}",
            }
        except AWSValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ AWS validation failed: {str(e)}",
            )

    elif credentials_data.provider == "azure":
        if not all([
            credentials_data.azure_tenant_id,
            credentials_data.azure_client_id,
            credentials_data.azure_client_secret,
            credentials_data.azure_subscription_id,
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Azure Tenant ID, Client ID, Client Secret, and Subscription ID are required",
            )

        credentials = AzureCredentials(
            tenant_id=credentials_data.azure_tenant_id,
            client_id=credentials_data.azure_client_id,
            client_secret=credentials_data.azure_client_secret,
            subscription_id=credentials_data.azure_subscription_id,
        )

        try:
            subscription_info = await validate_azure_credentials(credentials)
            return {
                "valid": True,
                "provider": "azure",
                "subscription_id": subscription_info["subscription_id"],
                "subscription_name": subscription_info.get("subscription_name", "N/A"),
                "message": f"✅ Azure credentials are valid! Subscription: {subscription_info.get('subscription_name', subscription_info['subscription_id'])}",
            }
        except AzureValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Azure validation failed: {str(e)}",
            )

    elif credentials_data.provider == "gcp":
        if not credentials_data.gcp_project_id or not credentials_data.gcp_service_account_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GCP Project ID and Service Account JSON are required",
            )

        # For MVP, we skip actual validation and return success
        # GCP validation will be implemented in Phase 2
        try:
            import json
            json_data = json.loads(credentials_data.gcp_service_account_json)
            project_id = json_data.get("project_id", credentials_data.gcp_project_id)

            return {
                "valid": True,
                "provider": "gcp",
                "project_id": project_id,
                "message": f"✅ GCP credentials format is valid! Project ID: {project_id}",
            }
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Invalid JSON format for Service Account: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ GCP validation failed: {str(e)}",
            )

    elif credentials_data.provider == "microsoft365":
        if not all([
            credentials_data.microsoft365_tenant_id,
            credentials_data.microsoft365_client_id,
            credentials_data.microsoft365_client_secret,
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Microsoft 365 Tenant ID, Client ID, and Client Secret are required",
            )

        credentials = Microsoft365Credentials(
            tenant_id=credentials_data.microsoft365_tenant_id,
            client_id=credentials_data.microsoft365_client_id,
            client_secret=credentials_data.microsoft365_client_secret,
        )

        try:
            org_info = await validate_microsoft365_credentials(credentials)
            return {
                "valid": True,
                "provider": "microsoft365",
                "tenant_id": org_info["tenant_id"],
                "organization_name": org_info["organization_name"],
                "verified_domains": org_info["verified_domains"],
                "message": f"✅ Microsoft 365 credentials are valid! Organization: {org_info['organization_name']}",
            }
        except Microsoft365ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Microsoft 365 validation failed: {str(e)}",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {credentials_data.provider}",
        )


@router.get(
    "/",
    response_model=list[CloudAccount],
    summary="List cloud accounts",
    description="""
List all cloud accounts for the current user.

Supports pagination with `skip` and `limit` parameters.

**Credentials are never returned** - only metadata and configuration.
""",
    response_description="List of cloud accounts",
    responses={
        200: {
            "description": "Cloud accounts retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "provider": "aws",
                            "account_name": "Production AWS",
                            "account_identifier": "123456789012",
                            "regions": ["us-east-1"],
                            "is_active": True,
                            "last_scan_at": "2024-01-14T08:00:00Z"
                        },
                        {
                            "id": "987e6543-e21b-12d3-a456-426614174000",
                            "provider": "azure",
                            "account_name": "Dev Azure",
                            "account_identifier": "sub-456",
                            "resource_groups": ["rg-dev"],
                            "is_active": True,
                            "last_scan_at": None
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
async def list_cloud_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
) -> list[CloudAccount]:
    """
    List all cloud accounts for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of cloud accounts (without credentials)
    """
    accounts = await cloud_account_crud.get_cloud_accounts_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return accounts


@router.get(
    "/{account_id}",
    response_model=CloudAccount,
    summary="Get cloud account details",
    description="""
Get details of a specific cloud account by ID.

Returns account metadata including last scan time and configuration.
""",
    response_description="Cloud account details",
    responses={
        200: {
            "description": "Account found",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "provider": "aws",
                        "account_name": "Production AWS",
                        "account_identifier": "123456789012",
                        "regions": ["us-east-1", "eu-west-1"],
                        "is_active": True,
                        "last_scan_at": "2024-01-14T08:00:00Z",
                        "scheduled_scan_enabled": True,
                        "scheduled_scan_frequency": "daily",
                        "scheduled_scan_hour": 2
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
            "description": "Account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def get_cloud_account(
    account_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CloudAccount:
    """
    Get a specific cloud account by ID.

    Args:
        account_id: Cloud account UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Cloud account (without credentials)

    Raises:
        HTTPException: If account not found
    """
    account = await cloud_account_crud.get_cloud_account_by_id(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    return account


@router.patch(
    "/{account_id}",
    response_model=CloudAccount,
    summary="Update cloud account",
    description="""
Update cloud account configuration, credentials, or settings.

Can update: account name, regions, credentials, scheduled scan settings, active status.

**Note**: When updating credentials, all credential fields for that provider must be provided together.
""",
    response_description="Account updated successfully",
    responses={
        200: {
            "description": "Account updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "provider": "aws",
                        "account_name": "Production AWS (Updated)",
                        "regions": ["us-east-1", "eu-west-1", "ap-south-1"],
                        "is_active": True,
                        "updated_at": "2024-01-15T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation failed",
            "content": {
                "application/json": {
                    "example": {"detail": "AWS credentials validation failed: Invalid access key"}
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
            "description": "Account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def update_cloud_account(
    account_id: uuid.UUID,
    account_in: CloudAccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CloudAccount:
    """
    Update a cloud account.

    Note: If updating AWS credentials, both access_key_id and secret_access_key
    must be provided together.

    Args:
        account_id: Cloud account UUID
        account_in: Cloud account update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated cloud account (without credentials)

    Raises:
        HTTPException: If account not found or validation fails
    """
    # Get existing account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    # If updating AWS credentials, validate them
    if account_in.aws_access_key_id and account_in.aws_secret_access_key:
        try:
            credentials = AWSCredentials(
                access_key_id=account_in.aws_access_key_id,
                secret_access_key=account_in.aws_secret_access_key,
                region=account.regions[0] if account.regions else "us-east-1",
            )
            await validate_aws_credentials(credentials)

        except AWSValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AWS credentials validation failed: {str(e)}",
            )

    # If updating Azure credentials, validate them
    if (
        account_in.azure_tenant_id
        and account_in.azure_client_id
        and account_in.azure_client_secret
        and account_in.azure_subscription_id
    ):
        try:
            credentials = AzureCredentials(
                tenant_id=account_in.azure_tenant_id,
                client_id=account_in.azure_client_id,
                client_secret=account_in.azure_client_secret,
                subscription_id=account_in.azure_subscription_id,
            )
            await validate_azure_credentials(credentials)

        except AzureValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Azure credentials validation failed: {str(e)}",
            )

    # Update account
    updated_account = await cloud_account_crud.update_cloud_account(
        db=db,
        db_account=account,
        account_in=account_in,
    )

    return updated_account


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete cloud account",
    description="""
Delete a cloud account and all associated data.

**Warning**: This will also delete all scan history and detected resources for this account.
""",
    response_description="Account deleted successfully",
    responses={
        204: {
            "description": "Account deleted (no content)"
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
            "description": "Account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def delete_cloud_account(
    account_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Delete a cloud account.

    Args:
        account_id: Cloud account UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If account not found
    """
    # Get existing account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    # Delete account
    await cloud_account_crud.delete_cloud_account(db=db, db_account=account)


@router.post(
    "/{account_id}/validate",
    response_model=dict,
    summary="Validate stored credentials",
    description="""
Re-validate stored credentials and check permissions for an existing account.

Use this to verify credentials are still valid and have required permissions.
""",
    response_description="Validation results with permissions",
    responses={
        200: {
            "description": "Validation successful",
            "content": {
                "application/json": {
                    "examples": {
                        "aws": {
                            "summary": "AWS validation with permissions",
                            "value": {
                                "status": "valid",
                                "provider": "aws",
                                "account_info": {
                                    "account_id": "123456789012",
                                    "arn": "arn:aws:iam::123456789012:user/cloudwaste"
                                },
                                "permissions": {
                                    "ec2:DescribeInstances": True,
                                    "ec2:DescribeVolumes": True,
                                    "rds:DescribeDBInstances": True
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation failed: Invalid credentials"}
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
            "description": "Account not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Cloud account not found"}
                }
            }
        }
    }
)
async def validate_cloud_account(
    account_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """
    Validate cloud account credentials and permissions.

    This endpoint re-validates the stored credentials and checks
    for required read permissions.

    Args:
        account_id: Cloud account UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Validation result with account info and permissions

    Raises:
        HTTPException: If account not found or validation fails
    """
    # Get existing account
    account = await cloud_account_crud.get_cloud_account_by_id(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    # Get decrypted credentials (internal use only)
    account_with_creds = await cloud_account_crud.get_decrypted_credentials(account)

    if account.provider == "aws" and account_with_creds.aws_credentials:
        try:
            # Validate credentials
            account_info = await validate_aws_credentials(account_with_creds.aws_credentials)

            # Check permissions
            from app.services.aws_validator import check_aws_read_permissions

            permissions = await check_aws_read_permissions(account_with_creds.aws_credentials)

            return {
                "status": "valid",
                "provider": "aws",
                "account_info": account_info,
                "permissions": permissions,
            }

        except AWSValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {str(e)}",
            )

    elif account.provider == "azure" and account_with_creds.azure_credentials:
        try:
            # Validate credentials
            subscription_info = await validate_azure_credentials(account_with_creds.azure_credentials)

            # Check permissions
            from app.services.azure_validator import check_azure_read_permissions

            permissions = await check_azure_read_permissions(account_with_creds.azure_credentials)

            return {
                "status": "valid",
                "provider": "azure",
                "subscription_info": subscription_info,
                "permissions": permissions,
            }

        except AzureValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {str(e)}",
            )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Provider {account.provider} is not yet supported for validation",
    )
