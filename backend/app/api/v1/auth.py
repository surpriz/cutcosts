"""Authentication endpoints."""

import secrets as _secrets
from datetime import timedelta
from typing import Annotated
from urllib.parse import urlencode

import httpx
import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.config import settings
from app.core.rate_limit import auth_login_limit, auth_refresh_limit, auth_register_limit, limiter
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import User as UserSchema
from app.schemas.user import (
    ForgotPasswordRequest,
    PasswordChangeRequest,
    ResetPasswordRequest,
    UserCreate,
    UserUpdate,
)
from app.services import email_service
from app.services.subscription_service import SubscriptionService

router = APIRouter()
logger = structlog.get_logger()


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=r"""
Register a new user account and send email verification.

## Process
1. Validates email is not already registered
2. Creates user account with hashed password
3. Creates free subscription for the new user
4. Sends verification email with token
5. Returns user details (email_verified=False)

**Important**: Users must verify their email before logging in.

## Code Examples

### cURL
\```bash
curl -X POST https://api.cutcosts.com/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
\```

### Python (httpx)
\```python
import httpx

url = "https://api.cutcosts.com/api/v1/auth/register"
data = {
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
}

response = httpx.post(url, json=data)
user = response.json()
print(f"User created: {user['id']}, email_verified: {user['email_verified']}")
\```

### JavaScript (fetch)
\```javascript
const response = await fetch('https://api.cutcosts.com/api/v1/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepass123',
    full_name: 'John Doe'
  })
});
const user = await response.json();
console.log('Check your email for verification link');
\```

## Rate Limiting
Limited to 5 requests per minute to prevent abuse.

## Security
- Password is hashed using bcrypt with cost factor 12
- Email verification required before login
- Free subscription automatically created
""",
    response_description="User account created successfully, verification email sent",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "email_verified": False,
                        "is_superuser": False,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
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
                    "example": {"detail": "Rate limit exceeded: 5 per 1 minute"}
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
)
@auth_register_limit
async def register(
    request: Request,
    response: Response,
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Register a new user and send verification email.

    Args:
        user_in: User registration data
        db: Database session

    Returns:
        Created user (email_verified=False)

    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    user = await user_crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user (email_verified defaults to False)
    user = await user_crud.create_user(db, user_in)

    # Create free subscription for new user
    subscription_service = SubscriptionService(db)
    try:
        await subscription_service.create_free_subscription(user.id)
        logger.info(
            "auth.free_subscription_created",
            user_id=str(user.id),
        )
    except Exception as e:
        logger.error(
            "auth.free_subscription_failed",
            user_id=str(user.id),
            error=str(e),
        )

    # Generate verification token
    verification_token = await user_crud.set_verification_token(db, user)

    # Send verification email (async but don't wait)
    email_sent = email_service.send_verification_email(
        email=user.email,
        full_name=user.full_name or "User",
        verification_token=verification_token,
    )

    if not email_sent:
        logger.warning(
            "auth.verification_email_failed",
            user_id=str(user.id),
            email=user.email,
        )

    logger.info(
        "auth.user_registered",
        user_id=str(user.id),
        email=user.email,
        email_sent=email_sent,
    )

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access tokens",
    description=r"""
Authenticate user and receive JWT access and refresh tokens.

## Requirements
- Email must be verified before login
- Correct email and password required

## Token Types
- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 or 30 days), used to get new access tokens

## Remember Me
Set `remember_me=true` to extend refresh token lifetime to 30 days instead of 7 days.

## Code Examples

### cURL
\```bash
curl -X POST https://api.cutcosts.com/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=user@example.com&password=securepass123&remember_me=false"
\```

### Python (httpx)
\```python
import httpx

url = "https://api.cutcosts.com/api/v1/auth/login"
data = {
    "username": "user@example.com",
    "password": "securepass123",
    "remember_me": False
}

response = httpx.post(url, data=data)
tokens = response.json()

# Store tokens securely
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# Use access_token for authenticated requests
headers = {"Authorization": f"Bearer {access_token}"}
\```

### JavaScript (fetch)
\```javascript
const formData = new URLSearchParams({
  username: 'user@example.com',
  password: 'securepass123',
  remember_me: 'false'
});

const response = await fetch('https://api.cutcosts.com/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: formData
});

const tokens = await response.json();
// Store tokens in localStorage or secure storage
localStorage.setItem('access_token', tokens.access_token);
localStorage.setItem('refresh_token', tokens.refresh_token);
\```

## Rate Limiting
Limited to 5 requests per minute to prevent brute force attacks.

## Security Notes
- Always use HTTPS in production
- Store tokens securely (httpOnly cookies recommended for web apps)
- Never expose tokens in client-side code or logs
""",
    response_description="Authentication successful, tokens returned",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "examples": {
                        "incorrect_credentials": {
                            "summary": "Wrong email or password",
                            "value": {"detail": "Incorrect email or password"}
                        }
                    }
                }
            }
        },
        403: {
            "description": "Account inactive or email not verified",
            "content": {
                "application/json": {
                    "examples": {
                        "email_not_verified": {
                            "summary": "Email not verified",
                            "value": {"detail": "Email not verified. Please check your email and click the verification link."}
                        },
                        "inactive_user": {
                            "summary": "Account inactive",
                            "value": {"detail": "Inactive user"}
                        }
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 5 per 1 minute"}
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
)
@auth_login_limit
async def login(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    remember_me: Annotated[bool, Form()] = False,
) -> dict[str, str]:
    """
    OAuth2 compatible token login.

    Args:
        db: Database session
        form_data: OAuth2 form with username (email) and password
        remember_me: If True, refresh token expires after 30 days instead of 7

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are incorrect
    """
    user = await user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not await user_crud.is_user_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and click the verification link.",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Create refresh token with appropriate expiration
    if remember_me:
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_REMEMBER_ME_EXPIRE_DAYS)
    else:
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "remember_me": remember_me},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description=r"""
Get new access and refresh tokens using a valid refresh token.

## When to Use
Call this endpoint when your access token expires (after 30 minutes) to get a new one without requiring the user to login again.

## Code Examples

### cURL
\```bash
curl -X POST https://api.cutcosts.com/api/v1/auth/refresh \\
  -H "Content-Type: application/json" \\
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
\```

### Python (httpx)
\```python
import httpx

url = "https://api.cutcosts.com/api/v1/auth/refresh"
data = {"refresh_token": refresh_token}

response = httpx.post(url, json=data)
tokens = response.json()

# Update stored tokens
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
\```

### JavaScript (fetch)
\```javascript
const response = await fetch('https://api.cutcosts.com/api/v1/auth/refresh', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});

const tokens = await response.json();
localStorage.setItem('access_token', tokens.access_token);
localStorage.setItem('refresh_token', tokens.refresh_token);
\```

## Rate Limiting
Limited to 10 requests per minute.
""",
    response_description="New tokens generated successfully",
    responses={
        200: {
            "description": "Tokens refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "summary": "Invalid refresh token",
                            "value": {"detail": "Invalid refresh token"}
                        },
                        "wrong_type": {
                            "summary": "Wrong token type",
                            "value": {"detail": "Invalid token type"}
                        }
                    }
                }
            }
        },
        403: {
            "description": "User account inactive",
            "content": {
                "application/json": {
                    "example": {"detail": "Inactive user"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 10 per 1 minute"}
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
)
@auth_refresh_limit
async def refresh_token(
    request: Request,
    response: Response,
    refresh_request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Refresh access token using refresh token.

    Args:
        refresh_request: Refresh token request
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    payload = decode_token(refresh_request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify user exists
    import uuid

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    user = await user_crud.get_user_by_id(db, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not await user_crud.is_user_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create new tokens, preserving remember_me from original refresh token
    remember_me = bool(payload.get("remember_me", False))
    refresh_token_expires = (
        timedelta(days=settings.REFRESH_TOKEN_REMEMBER_ME_EXPIRE_DAYS)
        if remember_me
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "remember_me": remember_me},
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user profile",
    description="""
Get information about the currently authenticated user.

Requires valid access token in Authorization header.
""",
    response_description="Current user profile",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "email_verified": True,
                        "is_superuser": False,
                        "email_scan_notifications": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
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
        }
    }
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user
    """
    return current_user


@router.get(
    "/verify-email/{token}",
    summary="Verify email address",
    description="""
Verify user email address using the token sent via email after registration.

Users receive this link in their registration email. After verification, they can login.
""",
    response_description="Email verified successfully",
    responses={
        200: {
            "description": "Email verified successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Email verified successfully. You can now login."}
                }
            }
        },
        400: {
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired verification token"}
                }
            }
        }
    }
)
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Verify user email with token.

    Args:
        token: Email verification token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Get user by verification token
    user = await user_crud.get_user_by_verification_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # Verify email
    await user_crud.verify_user_email(db, user)

    # Send welcome email (non-blocking - don't fail if email fails)
    try:
        email_sent = email_service.send_welcome_email(
            email=user.email,
            full_name=user.full_name or "User",
        )
        logger.info(
            "auth.email_verified",
            user_id=str(user.id),
            email=user.email,
            welcome_email_sent=email_sent,
        )
    except Exception as e:
        # Log error but don't fail verification
        logger.error(
            "auth.welcome_email_failed",
            user_id=str(user.id),
            email=user.email,
            error=str(e),
        )

    return {
        "message": "Email verified successfully. You can now login.",
    }


@router.post(
    "/resend-verification",
    summary="Resend verification email",
    description="""
Resend email verification link to user's email address.

Use this if the user didn't receive the initial verification email or if the token expired.

**Rate Limited**: 5 requests/minute to prevent email spam.
""",
    response_description="Verification email resent",
    responses={
        200: {
            "description": "Verification email sent (or email already verified)",
            "content": {
                "application/json": {
                    "example": {"message": "If the email exists and is not verified, a new verification email has been sent."}
                }
            }
        },
        400: {
            "description": "Email already verified",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already verified"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 5 per 1 minute"}
                }
            }
        },
        500: {
            "description": "Failed to send email",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to send verification email"}
                }
            }
        }
    }
)
@auth_register_limit  # Same limit as register to prevent email spam
async def resend_verification_email(
    request: Request,
    response: Response,
    email: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Resend verification email to user.

    Args:
        email: User email address
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or already verified
    """
    # Get user by email
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        # Don't reveal that user doesn't exist for security
        return {
            "message": "If the email exists and is not verified, a new verification email has been sent.",
        }

    # Check if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    # Generate new verification token
    verification_token = await user_crud.set_verification_token(db, user)

    # Send verification email
    email_sent = email_service.send_verification_email(
        email=user.email,
        full_name=user.full_name or "User",
        verification_token=verification_token,
    )

    if not email_sent:
        logger.error(
            "auth.resend_verification_failed",
            user_id=str(user.id),
            email=user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )

    logger.info(
        "auth.verification_email_resent",
        user_id=str(user.id),
        email=user.email,
    )

    return {
        "message": "Verification email sent successfully",
    }


@router.patch(
    "/me",
    response_model=UserSchema,
    summary="Update user profile",
    description="""
Update current user's profile information and preferences.

Can update: email, full_name, password, email_scan_notifications.
""",
    response_description="User profile updated successfully",
    responses={
        200: {
            "description": "Profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "newemail@example.com",
                        "full_name": "John Smith",
                        "email_scan_notifications": False,
                        "is_active": True,
                        "email_verified": True,
                        "updated_at": "2024-01-15T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Email already taken",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
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
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Update current user information and preferences.

    Args:
        user_update: User update data (email, password, full_name, email_scan_notifications)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: If email is already taken by another user
    """
    # Check if email is being changed and is already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_crud.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update user
    updated_user = await user_crud.update_user(db, current_user, user_update)

    logger.info(
        "auth.user_updated",
        user_id=str(updated_user.id),
        email=updated_user.email,
        email_scan_notifications=updated_user.email_scan_notifications,
    )

    return updated_user


@router.post(
    "/forgot-password",
    summary="Request password reset",
    description="""
Request a password reset email with reset token.

**Security**: Always returns success to prevent email enumeration attacks, even if email doesn't exist.

**Rate Limited**: 5 requests/minute to prevent abuse.
""",
    response_description="Password reset email sent (if email exists)",
    responses={
        200: {
            "description": "Password reset request processed",
            "content": {
                "application/json": {
                    "example": {"message": "If an account with this email exists, a password reset link has been sent."}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 5 per 1 minute"}
                }
            }
        }
    }
)
@auth_register_limit  # Same rate limit as register to prevent abuse
async def forgot_password(
    request: Request,
    response: Response,
    forgot_request: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Request password reset email.

    Always returns success to prevent email enumeration attacks.

    Args:
        forgot_request: Forgot password request with email
        db: Database session

    Returns:
        Success message (always, even if email doesn't exist)
    """
    # Get user by email
    user = await user_crud.get_user_by_email(db, forgot_request.email)

    if user and user.email_verified:
        # Generate password reset token
        reset_token = await user_crud.set_password_reset_token(db, user)

        # Send password reset email
        email_sent = email_service.send_password_reset_email(
            email=user.email,
            full_name=user.full_name or "User",
            reset_token=reset_token,
        )

        if email_sent:
            logger.info(
                "auth.password_reset_requested",
                user_id=str(user.id),
                email=user.email,
            )
        else:
            logger.error(
                "auth.password_reset_email_failed",
                user_id=str(user.id),
                email=user.email,
            )
    else:
        # Log for monitoring but don't reveal to user
        logger.info(
            "auth.password_reset_requested_unknown",
            email=forgot_request.email,
        )

    # Always return success to prevent email enumeration
    return {
        "message": "If an account with this email exists, a password reset link has been sent.",
    }


@router.post(
    "/reset-password",
    summary="Reset password with token",
    description="""
Reset password using the token received via email.

Users receive this token after requesting password reset via `/forgot-password`.
""",
    response_description="Password reset successfully",
    responses={
        200: {
            "description": "Password reset successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset successfully. You can now login with your new password."}
                }
            }
        },
        400: {
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired password reset token"}
                }
            }
        },
        422: {
            "description": "Validation error (e.g., password too short)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_short",
                                "loc": ["body", "new_password"],
                                "msg": "String should have at least 8 characters"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def reset_password(
    reset_request: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Reset password using token from email.

    Args:
        reset_request: Reset password request with token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Get user by reset token
    user = await user_crud.get_user_by_password_reset_token(db, reset_request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    # Reset password
    await user_crud.reset_user_password(db, user, reset_request.new_password)

    logger.info(
        "auth.password_reset_completed",
        user_id=str(user.id),
        email=user.email,
    )

    return {
        "message": "Password reset successfully. You can now login with your new password.",
    }


@router.post(
    "/change-password",
    summary="Change password (authenticated)",
    description="""
Change password for currently authenticated user.

**Requires**: Current password for verification before changing to new password.

**Authentication**: Requires valid access token.
""",
    response_description="Password changed successfully",
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Password changed successfully."}
                }
            }
        },
        400: {
            "description": "Current password is incorrect",
            "content": {
                "application/json": {
                    "example": {"detail": "Current password is incorrect"}
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
        422: {
            "description": "Validation error (e.g., password too short)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_short",
                                "loc": ["body", "new_password"],
                                "msg": "String should have at least 8 characters"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def change_password(
    change_request: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Change password for authenticated user.

    Requires current password verification before changing.

    Args:
        change_request: Change password request with current and new password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    # OAuth-only users cannot change password (they have no password set)
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for accounts linked via Google. Use password reset to set a password.",
        )

    # Verify current password
    if not verify_password(change_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    await user_crud.reset_user_password(db, current_user, change_request.new_password)

    logger.info(
        "auth.password_changed",
        user_id=str(current_user.id),
        email=current_user.email,
    )

    return {
        "message": "Password changed successfully.",
    }


# ---------------------------------------------------------------------------
# Google OAuth endpoints
# ---------------------------------------------------------------------------


async def _get_oauth_redis() -> aioredis.Redis:
    """Get a Redis client for OAuth state management."""
    return aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)


@router.get(
    "/google/login",
    summary="Initiate Google OAuth flow",
    description="Redirects the browser to Google's OAuth consent page.",
    responses={302: {"description": "Redirect to Google OAuth consent"}},
)
@auth_login_limit
async def google_login(request: Request, response: Response) -> RedirectResponse:
    """
    Initiate Google OAuth by redirecting to Google's consent screen.

    Generates a CSRF state token stored in Redis with 10-minute TTL.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    state = _secrets.token_urlsafe(32)
    redis_client = await _get_oauth_redis()
    try:
        await redis_client.setex(f"oauth_state:{state}", 600, "1")
    finally:
        await redis_client.aclose()

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    logger.info("auth.google_oauth_initiated")
    return RedirectResponse(url=google_auth_url, status_code=302)


@router.get(
    "/google/callback",
    summary="Handle Google OAuth callback",
    description="Processes the OAuth callback from Google, creates or logs in the user, and redirects to the frontend with JWT tokens.",
    responses={302: {"description": "Redirect to frontend with tokens or error"}},
)
@auth_login_limit
async def google_callback(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    """
    Process Google OAuth callback.

    - Validates CSRF state against Redis
    - Exchanges authorization code for Google tokens
    - Fetches user info from Google
    - Creates new user or logs in existing Google user
    - Refuses login if email already registered with password (no merge)
    - Redirects to frontend with JWT tokens in query params
    """
    frontend_callback = f"{settings.FRONTEND_URL}/auth/oauth-callback"

    # Handle Google-side errors (user denied access, etc.)
    if error:
        logger.warning("auth.google_oauth_error", error=error)
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed", status_code=302
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed", status_code=302
        )

    # Validate CSRF state (atomic delete = one-time use)
    redis_client = await _get_oauth_redis()
    try:
        state_key = f"oauth_state:{state}"
        deleted = await redis_client.delete(state_key)
        if deleted != 1:
            logger.warning("auth.google_invalid_state")
            return RedirectResponse(
                url=f"{frontend_callback}?error=oauth_failed", status_code=302
            )
    finally:
        await redis_client.aclose()

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()
        except httpx.HTTPError as exc:
            logger.error("auth.google_token_exchange_failed", error=str(exc))
            return RedirectResponse(
                url=f"{frontend_callback}?error=oauth_failed", status_code=302
            )

    # Fetch user info from Google
    async with httpx.AsyncClient() as client:
        try:
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
        except httpx.HTTPError as exc:
            logger.error("auth.google_userinfo_failed", error=str(exc))
            return RedirectResponse(
                url=f"{frontend_callback}?error=oauth_failed", status_code=302
            )

    google_email: str = userinfo.get("email", "").lower().strip()
    google_name: str | None = userinfo.get("name")

    # Verify Google confirmed the email is valid
    if not google_email or not userinfo.get("email_verified", False):
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed", status_code=302
        )

    # Check for existing user
    existing_user = await user_crud.get_user_by_email(db, google_email)

    if existing_user:
        # Email exists but was registered with password - refuse merge (Option B)
        if existing_user.oauth_provider is None:
            logger.info(
                "auth.google_oauth_email_conflict",
                email=google_email,
            )
            return RedirectResponse(
                url=f"{frontend_callback}?error=use_password", status_code=302
            )
        # Existing Google user - log them in
        user = existing_user
        logger.info("auth.google_oauth_login", user_id=str(user.id))
    else:
        # New user - create account via OAuth
        user = await user_crud.create_oauth_user(
            db,
            email=google_email,
            full_name=google_name,
            oauth_provider="google",
        )
        # Create free subscription
        subscription_service = SubscriptionService(db)
        try:
            await subscription_service.create_free_subscription(user.id)
            logger.info(
                "auth.google_free_subscription_created",
                user_id=str(user.id),
            )
        except Exception as exc:
            logger.error(
                "auth.google_free_subscription_failed",
                user_id=str(user.id),
                error=str(exc),
            )
        # Send welcome email (non-blocking)
        try:
            email_service.send_welcome_email(
                email=user.email,
                full_name=user.full_name or "User",
            )
        except Exception:
            pass
        logger.info("auth.google_oauth_registered", user_id=str(user.id))

    # Check user is active and email is verified
    if not user.is_active:
        return RedirectResponse(
            url=f"{frontend_callback}?error=account_inactive", status_code=302
        )
    if not user.email_verified:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed", status_code=302
        )

    # Issue JWT pair (same as password login)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "remember_me": False},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    params = urlencode({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    return RedirectResponse(url=f"{frontend_callback}?{params}", status_code=302)
