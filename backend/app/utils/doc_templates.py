"""Reusable documentation templates for API endpoints.

This module provides standardized response templates and utilities
to ensure consistent API documentation across all endpoints.
"""

# Standard error responses that appear across most endpoints
STANDARD_ERROR_RESPONSES = {
    400: {
        "description": "Bad request - Invalid input data or validation failed",
        "content": {
            "application/json": {
                "examples": {
                    "validation_error": {
                        "summary": "Validation failed",
                        "value": {"detail": "Invalid input data"}
                    },
                    "invalid_credentials": {
                        "summary": "Invalid credentials",
                        "value": {"detail": "Credentials validation failed"}
                    }
                }
            }
        }
    },
    401: {
        "description": "Authentication required or token invalid/expired",
        "content": {
            "application/json": {
                "examples": {
                    "missing_token": {
                        "summary": "Missing authorization header",
                        "value": {"detail": "Could not validate credentials"}
                    },
                    "invalid_token": {
                        "summary": "Invalid or expired token",
                        "value": {"detail": "Could not validate credentials"}
                    }
                }
            }
        }
    },
    403: {
        "description": "Forbidden - Insufficient permissions or subscription limit exceeded",
        "content": {
            "application/json": {
                "examples": {
                    "insufficient_permissions": {
                        "summary": "Insufficient permissions",
                        "value": {"detail": "Not enough permissions"}
                    },
                    "subscription_limit": {
                        "summary": "Subscription limit exceeded",
                        "value": {
                            "detail": "Cloud account limit reached. Your Free plan allows 1 account. Upgrade to Pro for 5 accounts."
                        }
                    }
                }
            }
        }
    },
    404: {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "example": {"detail": "Resource not found"}
            }
        }
    },
    422: {
        "description": "Validation error - Request body doesn't match schema",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "password"],
                            "msg": "String should have at least 8 characters",
                            "input": "short"
                        }
                    ]
                }
            }
        }
    },
    429: {
        "description": "Rate limit exceeded",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Rate limit exceeded: 60 per 1 minute"
                }
            }
        }
    },
    500: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}


def get_standard_responses(*codes: int) -> dict:
    """Get standard error responses for specified status codes.

    Usage:
        @router.get(
            "/resource",
            responses={
                200: {...},  # Success response
                **get_standard_responses(401, 404, 500)  # Standard errors
            }
        )

    Args:
        *codes: HTTP status codes to include (e.g., 401, 403, 404, 422, 500)

    Returns:
        Dictionary of OpenAPI response objects for the specified codes

    Example:
        >>> get_standard_responses(401, 404, 500)
        {401: {...}, 404: {...}, 500: {...}}
    """
    return {
        code: STANDARD_ERROR_RESPONSES[code]
        for code in codes
        if code in STANDARD_ERROR_RESPONSES
    }


def create_list_endpoint_description(
    resource_name: str,
    filters: list[str] | None = None,
    sorting: list[str] | None = None,
    pagination: bool = True
) -> str:
    """Generate standard description for list endpoints.

    Args:
        resource_name: Name of the resource (plural form, e.g., "cloud accounts")
        filters: List of available filter parameters
        sorting: List of available sort fields
        pagination: Whether pagination is supported

    Returns:
        Formatted markdown description for the endpoint

    Example:
        >>> create_list_endpoint_description(
        ...     resource_name="cloud accounts",
        ...     filters=["provider", "is_active", "region"],
        ...     sorting=["created_at", "account_name"]
        ... )
    """
    desc = f"List all {resource_name} for the current user.\n\n"

    if filters:
        desc += "## Available Filters\n\n"
        for filter_name in filters:
            desc += f"- `{filter_name}`: Filter by {filter_name.replace('_', ' ')}\n"
        desc += "\n"

    if sorting:
        desc += "## Sorting\n\n"
        desc += "Use the `sort` parameter with one of the following fields:\n"
        for sort_field in sorting:
            desc += f"- `{sort_field}`: Sort by {sort_field.replace('_', ' ')}\n"
        desc += "\nPrefix with `-` for descending order (e.g., `-created_at`)\n\n"

    if pagination:
        desc += """## Pagination

Use `skip` and `limit` parameters to paginate results:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 100, max: 100)

Example: `?skip=0&limit=20` returns first 20 items
"""

    return desc


# Standard CRUD operation descriptions
CRUD_DESCRIPTIONS = {
    "create": "Create a new {resource}",
    "read": "Get details of a specific {resource} by ID",
    "list": "List all {resources} for the current user",
    "update": "Update an existing {resource}",
    "delete": "Delete a {resource}",
    "validate": "Validate {resource} credentials or configuration"
}


def get_crud_description(operation: str, resource: str, resources: str | None = None) -> str:
    """Get standard description for CRUD operations.

    Args:
        operation: CRUD operation (create, read, list, update, delete, validate)
        resource: Resource name in singular form (e.g., "cloud account")
        resources: Resource name in plural form (optional, defaults to resource + "s")

    Returns:
        Formatted description for the operation

    Example:
        >>> get_crud_description("create", "cloud account")
        'Create a new cloud account'
        >>> get_crud_description("list", "cloud account", "cloud accounts")
        'List all cloud accounts for the current user'
    """
    if operation not in CRUD_DESCRIPTIONS:
        raise ValueError(f"Invalid operation: {operation}. Must be one of {list(CRUD_DESCRIPTIONS.keys())}")

    if resources is None:
        resources = f"{resource}s"

    template = CRUD_DESCRIPTIONS[operation]
    return template.format(resource=resource, resources=resources)
