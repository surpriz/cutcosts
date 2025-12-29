"""User preferences Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserPreferencesBase(BaseModel):
    """Base user preferences schema."""

    ml_data_collection_consent: bool = Field(
        default=False, description="User consent for ML data collection"
    )
    anonymized_industry: str | None = Field(
        default=None,
        max_length=50,
        description="Anonymized industry (tech, finance, healthcare, etc.)",
    )
    anonymized_company_size: str | None = Field(
        default=None,
        description="Company size bucket (small, medium, large, enterprise)",
    )
    email_scan_summaries: bool = Field(default=True, description="Email scan summary notifications")
    email_cost_alerts: bool = Field(default=True, description="Email cost alert notifications")
    email_marketing: bool = Field(default=False, description="Marketing emails")
    data_retention_years: str = Field(
        default="3", description="ML data retention period in years (1, 2, or 3)"
    )
    onboarding_dismissed: bool = Field(
        default=False, description="Whether user has permanently dismissed the onboarding wizard"
    )


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences."""

    pass


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""

    ml_data_collection_consent: bool | None = None
    anonymized_industry: str | None = None
    anonymized_company_size: str | None = None
    email_scan_summaries: bool | None = None
    email_cost_alerts: bool | None = None
    email_marketing: bool | None = None
    data_retention_years: str | None = None
    onboarding_dismissed: bool | None = None


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response."""

    id: str
    user_id: str
    ml_consent_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OnboardingStatusResponse(BaseModel):
    """Schema for onboarding status response."""

    should_show_onboarding: bool = Field(
        description="Whether the onboarding wizard should be displayed"
    )
    has_accounts: bool = Field(
        description="Whether the user has connected at least one cloud account"
    )
    onboarding_dismissed: bool = Field(
        description="Whether the user has permanently dismissed the onboarding wizard"
    )
    account_count: int = Field(
        description="Number of cloud accounts connected by the user"
    )
