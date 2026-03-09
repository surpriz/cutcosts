"""Paywall access control dependencies for resource visibility."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.paywall import PaywallContext
from app.services.subscription_service import SubscriptionService

# Scans completed before this date remain fully visible to free users
PAYWALL_EFFECTIVE_DATE = datetime(2026, 3, 9, 0, 0, 0)


async def get_paywall_context(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaywallContext:
    """Resolve the current user's paywall state.

    Never raises - always returns a PaywallContext.
    Endpoints use this to branch between full and redacted responses.
    """
    service = SubscriptionService(db)
    subscription = await service.get_or_create_user_subscription(current_user.id)
    plan_name = subscription.plan.name
    is_paid = plan_name in ("pro", "enterprise")

    return PaywallContext(
        is_paid=is_paid,
        plan_name=plan_name,
        paywall_cutoff_date=PAYWALL_EFFECTIVE_DATE,
    )


async def require_paid_for_resource_actions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Block resource mutation actions for free-tier users.

    Applies to: PATCH /resources/{id}, DELETE /resources/{id}.
    Free users cannot ignore, mark for deletion, or delete resource records.

    Raises:
        HTTPException: 403 if user is on free plan.
    """
    service = SubscriptionService(db)
    subscription = await service.get_or_create_user_subscription(current_user.id)

    if subscription.plan.name == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Managing resource status requires a Pro or Enterprise subscription. "
                "Upgrade to take action on wasteful resources."
            ),
        )

    return current_user
