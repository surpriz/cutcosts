"""Set all subscription plans to unlimited scans (pay-for-value model)

Revision ID: 006_paywall_scans_unlimited
Revises: 005_add_onboarding_dismissed
Create Date: 2026-03-08

Scans are now free and unlimited for all plans.
The paywall gates visibility of waste details instead of scan creation.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "006_paywall_scans_unlimited"
down_revision: Union[str, None] = "005_add_onboarding_dismissed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Set max_scans_per_month to NULL for all plans (unlimited scans)."""
    op.execute("UPDATE subscription_plans SET max_scans_per_month = NULL")


def downgrade() -> None:
    """Restore previous scan limits."""
    op.execute(
        "UPDATE subscription_plans SET max_scans_per_month = 5 WHERE name = 'free'"
    )
    op.execute(
        "UPDATE subscription_plans SET max_scans_per_month = 50 WHERE name = 'pro'"
    )
    op.execute(
        "UPDATE subscription_plans SET max_scans_per_month = 200 WHERE name = 'enterprise'"
    )
