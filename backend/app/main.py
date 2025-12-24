"""FastAPI Application Entry Point."""

import hashlib
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter
from app.middleware import CORSLoggingMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
# IMPORTANT: Must be done BEFORE creating FastAPI app
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        # Performance monitoring
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),  # Track API endpoint performance
            SqlalchemyIntegration(),  # Track database queries
            RedisIntegration(),  # Track Redis operations
            CeleryIntegration(),  # Track Celery tasks
        ],
        # User context (GDPR: Only enable if user consents)
        send_default_pii=False,  # Don't send PII by default
        # Release tracking (helps identify which version introduced bugs)
        release=f"cutcosts-backend@{os.getenv('GIT_COMMIT', 'dev')}",
        # Additional configuration
        attach_stacktrace=True,  # Attach stack traces to messages
        max_breadcrumbs=50,  # Number of breadcrumbs to keep
    )
    logger.info(f"✅ Sentry initialized (environment: {settings.SENTRY_ENVIRONMENT})")
else:
    logger.info("⚠️  Sentry DSN not set - Error tracking disabled")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
# CutCosts API - Cloud Waste Detection Platform

Detect and eliminate orphaned cloud resources across AWS, Azure, GCP, and Microsoft 365.

## Authentication

All endpoints (except `/api/v1/auth/register` and `/api/v1/auth/login`) require JWT authentication.

### Getting Started

1. **Register**: `POST /api/v1/auth/register`
2. **Verify Email**: Check your email and click the verification link
3. **Login**: `POST /api/v1/auth/login` → Returns `access_token` and `refresh_token`
4. **Use Token**: Include in `Authorization` header: `Bearer <access_token>`
5. **Refresh**: Use `POST /api/v1/auth/refresh` when token expires

### Token Lifetimes
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days (30 days with "remember me")

### Example Authentication Flow

```bash
# 1. Register
curl -X POST https://api.cutcosts.com/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "securepass123", "full_name": "John Doe"}'

# 2. Login after email verification
curl -X POST https://api.cutcosts.com/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=user@example.com&password=securepass123"

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "refresh_token": "eyJhbGc...",
#   "token_type": "bearer"
# }

# 3. Use token for authenticated requests
curl -X GET https://api.cutcosts.com/api/v1/accounts \\
  -H "Authorization: Bearer eyJhbGc..."
```

## Rate Limiting

Rate limits are applied per endpoint to ensure fair usage:

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Authentication endpoints | 5 requests/minute |
| Scan operations | 10 requests/hour |
| Standard endpoints | 60 requests/minute |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

## Subscription Plans

Different features and limits based on your subscription tier:

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Cloud Accounts | 1 | 5 | Unlimited |
| Scans per Month | 10 | 100 | Unlimited |
| Detection Rules | Default | Custom | Custom |
| API Access | Limited | Full | Full |
| Support | Community | Email | Priority |

Upgrade your plan at `/api/v1/subscriptions` or through the web dashboard.

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`/`201`: Success
- `400`: Bad request (validation error, invalid input)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions or subscription limits)
- `404`: Not found
- `422`: Validation error (Pydantic schema validation)
- `429`: Rate limit exceeded
- `500`: Internal server error

## Multi-Cloud Support

CutCosts supports multiple cloud providers:

- **AWS**: EC2, EBS, RDS, S3, and more
- **Azure**: Virtual Machines, Disks, Storage, SQL, and more
- **GCP**: Compute Engine, Persistent Disks, Cloud Storage, and more
- **Microsoft 365**: SharePoint, OneDrive, Teams, and more

Each provider requires specific credentials (see `/api/v1/accounts` endpoints for details).

## Getting Help

- **Documentation**: `/api/docs` (Swagger UI) or `/api/redoc` (ReDoc)
- **Health Check**: `/api/v1/health`
- **Support**: support@cutcosts.com
- **Status Page**: status.cutcosts.com
""",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User registration, login, email verification, password management, and account updates. "
                          "Public endpoints: `/register` and `/login`. All other endpoints require JWT authentication.",
        },
        {
            "name": "cloud-accounts",
            "description": "Manage multi-cloud account connections (AWS, Azure, GCP, Microsoft 365). "
                          "Create accounts, validate credentials, and configure scheduled scans. "
                          "Credentials are encrypted using Fernet encryption before storage.",
        },
        {
            "name": "scans",
            "description": "Trigger and manage cloud resource scans for waste detection. "
                          "Scans run asynchronously using Celery. Monitor progress in real-time "
                          "and retrieve results when complete. Supports manual and scheduled scans.",
        },
        {
            "name": "resources",
            "description": "View and manage detected orphaned resources. "
                          "Filter by provider, resource type, region, and status. "
                          "Mark resources for deletion or ignore them. Includes cost estimates.",
        },
        {
            "name": "detection-rules",
            "description": "Customize detection rules for different resource types. "
                          "Define thresholds, conditions, and exclusions. "
                          "Override default rules with custom logic per resource type.",
        },
        {
            "name": "cost-intelligence",
            "description": "Cost analysis, inventory management, and optimization recommendations. "
                          "Get detailed cost breakdowns by provider, region, and resource type.",
        },
        {
            "name": "impact-savings",
            "description": "Calculate impact and savings from detected orphaned resources. "
                          "Track historical savings and export reports.",
        },
        {
            "name": "subscriptions",
            "description": "Manage subscription plans and billing. "
                          "View current plan, usage limits, and upgrade options. "
                          "Stripe integration for payment processing.",
        },
        {
            "name": "user-preferences",
            "description": "User settings and preferences. "
                          "Configure email notifications, UI preferences, and default settings.",
        },
        {
            "name": "gdpr-compliance",
            "description": "GDPR compliance endpoints for data export and deletion. "
                          "Request complete data export or account deletion per GDPR Article 17.",
        },
        {
            "name": "ai-assistant",
            "description": "AI-powered assistant for cloud cost optimization advice. "
                          "Ask questions about your resources, get recommendations, and analyze patterns.",
        },
        {
            "name": "admin",
            "description": "Admin-only endpoints for user management, system configuration, and platform administration. "
                          "Requires superuser permissions.",
        },
        {
            "name": "admin-pricing",
            "description": "Admin endpoints for managing subscription plans and pricing tiers. "
                          "Create, update, and delete subscription plans.",
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints. Public access, no authentication required.",
        },
        {
            "name": "root",
            "description": "Root API endpoint with links to documentation and health check.",
        },
        {
            "name": "testing",
            "description": "Testing endpoints for development and debugging. "
                          "Available in development mode only. Not for production use.",
        },
    ],
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS logging middleware for security monitoring (OPTIONAL)
# ⚠️  NOTE: CORSLoggingMiddleware is available but currently disabled
# due to compatibility issues with BaseHTTPMiddleware in test environment
# To enable: uncomment the line below
# app.add_middleware(CORSLoggingMiddleware, log_all_requests=False)

# Configure CORS with strict security rules
# Security rationale:
# - allow_origins: Validated whitelist from settings (no wildcards)
# - allow_credentials: Allows cookies/authorization headers (required for JWT)
# - allow_methods: Explicit list (no wildcard for security)
# - allow_headers: Explicit whitelist (no wildcard to prevent header injection)
# - max_age: Cache preflight for 10 minutes to reduce requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    max_age=settings.CORS_MAX_AGE,
)


# Encryption Key Validation
def validate_encryption_key() -> None:
    """
    Validate ENCRYPTION_KEY at startup to prevent data loss.

    ⚠️  CRITICAL: This function ensures that ENCRYPTION_KEY hasn't changed
    since the last run. If the key changes, all encrypted data (cloud accounts
    credentials) becomes UNRECOVERABLE.

    Checks:
    1. ENCRYPTION_KEY is set in environment
    2. Key hash is logged (for audit trail)
    3. Warns if key appears to be a placeholder

    Raises:
        SystemExit: If ENCRYPTION_KEY is missing or invalid
    """
    logger.info("🔐 Validating ENCRYPTION_KEY...")

    # Check if ENCRYPTION_KEY is set
    if not settings.ENCRYPTION_KEY:
        logger.error("❌ ENCRYPTION_KEY not set in environment!")
        logger.error("   This will prevent encryption/decryption of cloud credentials")
        raise SystemExit(1)

    # Check if key is a placeholder
    placeholder_keywords = ["your-", "change-", "example", "placeholder"]
    if any(keyword in settings.ENCRYPTION_KEY.lower() for keyword in placeholder_keywords):
        logger.error("❌ ENCRYPTION_KEY appears to be a placeholder!")
        logger.error("   Please generate a proper Fernet key using:")
        logger.error("   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
        raise SystemExit(1)

    # Calculate and log key hash (for audit trail, not security)
    key_hash = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).hexdigest()
    logger.info(f"✅ ENCRYPTION_KEY validated")
    logger.info(f"   Key hash (first 16 chars): {key_hash[:16]}...")

    # Warn about key importance
    logger.info("")
    logger.info("⚠️  ENCRYPTION_KEY SECURITY:")
    logger.info("   - This key encrypts ALL cloud account credentials")
    logger.info("   - If this key changes, ALL encrypted data is LOST")
    logger.info("   - Never modify this key in production without migration")
    logger.info("   - Backup this key in a secure, separate location")
    logger.info("")


@app.on_event("startup")
async def startup_event() -> None:
    """Run validation checks on application startup."""
    validate_encryption_key()


@app.get("/api/v1/health", tags=["health"])
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "environment": settings.APP_ENV,
        },
    )


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to CutCosts API",
        "docs": "/api/docs",
        "health": "/api/v1/health",
    }


# Include API v1 routers
from app.api.v1 import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
