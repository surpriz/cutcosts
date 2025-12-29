"""User preferences API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.cloud_account import CloudAccount
from app.schemas.user_preferences import (
    OnboardingStatusResponse,
    UserPreferencesCreate,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)

router = APIRouter()


@router.get("/me", response_model=UserPreferencesResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's preferences.

    If preferences don't exist, create default preferences.
    """
    # Try to get existing preferences
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    # If no preferences exist, create default ones
    if not preferences:
        preferences = UserPreferences(
            user_id=current_user.id,
            ml_data_collection_consent=False,
            email_scan_summaries=True,
            email_cost_alerts=True,
            email_marketing=False,
            data_retention_years="3",
        )
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)

    return preferences


@router.post("/me", response_model=UserPreferencesResponse, status_code=status.HTTP_201_CREATED)
async def create_my_preferences(
    preferences_in: UserPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create preferences for current user.

    Raises 400 if preferences already exist.
    """
    # Check if preferences already exist
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User preferences already exist. Use PATCH to update.",
        )

    # Create new preferences
    preferences = UserPreferences(
        user_id=current_user.id,
        ml_data_collection_consent=preferences_in.ml_data_collection_consent,
        ml_consent_date=datetime.now() if preferences_in.ml_data_collection_consent else None,
        anonymized_industry=preferences_in.anonymized_industry,
        anonymized_company_size=preferences_in.anonymized_company_size,
        email_scan_summaries=preferences_in.email_scan_summaries,
        email_cost_alerts=preferences_in.email_cost_alerts,
        email_marketing=preferences_in.email_marketing,
        data_retention_years=preferences_in.data_retention_years,
    )

    db.add(preferences)
    await db.commit()
    await db.refresh(preferences)

    return preferences


@router.patch("/me", response_model=UserPreferencesResponse)
async def update_my_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's preferences.

    Creates default preferences if they don't exist.
    """
    # Get existing preferences or create default
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        # Create default preferences
        preferences = UserPreferences(
            user_id=current_user.id,
            ml_data_collection_consent=False,
            email_scan_summaries=True,
            email_cost_alerts=True,
            email_marketing=False,
            data_retention_years="3",
        )
        db.add(preferences)

    # Update fields
    update_data = preferences_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(preferences, field, value)

    # Set ml_consent_date if consent is being given for the first time
    if (
        preferences_update.ml_data_collection_consent is True
        and not preferences.ml_consent_date
    ):
        preferences.ml_consent_date = datetime.now()

    # Clear ml_consent_date if consent is being withdrawn
    if preferences_update.ml_data_collection_consent is False:
        preferences.ml_consent_date = None

    await db.commit()
    await db.refresh(preferences)

    return preferences


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user's preferences.

    This will also trigger GDPR data deletion if ML consent was previously given.
    """
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    await db.delete(preferences)
    await db.commit()

    return None


@router.post("/me/withdraw-ml-consent", response_model=UserPreferencesResponse)
async def withdraw_ml_consent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Withdraw ML data collection consent and trigger GDPR data deletion.

    This endpoint:
    1. Sets ml_data_collection_consent to False
    2. Clears ml_consent_date
    3. Triggers deletion of all user's ML data (handled separately by GDPR service)
    """
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    # Withdraw consent
    preferences.ml_data_collection_consent = False
    preferences.ml_consent_date = None

    await db.commit()
    await db.refresh(preferences)

    # TODO: Trigger GDPR data deletion task here
    # from app.services.gdpr_compliance import delete_user_ml_data
    # await delete_user_ml_data(current_user.id, db)

    return preferences


@router.get("/me/onboarding-status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get onboarding status for the current user.

    Returns whether onboarding should be shown based on:
    1. User's explicit dismissal preference (onboarding_dismissed)
    2. Whether user has connected at least one cloud account

    Logic: should_show_onboarding = NOT (onboarding_dismissed OR has_accounts)
    """
    # Get user preferences
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    # Get onboarding_dismissed from preferences (default False if no preferences)
    onboarding_dismissed = preferences.onboarding_dismissed if preferences else False

    # Count user's cloud accounts
    account_count_result = await db.execute(
        select(func.count(CloudAccount.id)).where(
            CloudAccount.user_id == current_user.id,
            CloudAccount.is_active == True,  # noqa: E712
        )
    )
    account_count = account_count_result.scalar() or 0

    has_accounts = account_count > 0

    # Calculate whether to show onboarding
    should_show_onboarding = not (onboarding_dismissed or has_accounts)

    return OnboardingStatusResponse(
        should_show_onboarding=should_show_onboarding,
        has_accounts=has_accounts,
        onboarding_dismissed=onboarding_dismissed,
        account_count=account_count,
    )


@router.post("/me/dismiss-onboarding", response_model=UserPreferencesResponse)
async def dismiss_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Dismiss the onboarding wizard permanently.

    Sets onboarding_dismissed to True in user preferences.
    Creates default preferences if they don't exist.
    """
    # Get existing preferences or create default
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        # Create default preferences with onboarding_dismissed = True
        preferences = UserPreferences(
            user_id=current_user.id,
            ml_data_collection_consent=False,
            email_scan_summaries=True,
            email_cost_alerts=True,
            email_marketing=False,
            data_retention_years="3",
            onboarding_dismissed=True,
        )
        db.add(preferences)
    else:
        # Update existing preferences
        preferences.onboarding_dismissed = True

    await db.commit()
    await db.refresh(preferences)

    return preferences
