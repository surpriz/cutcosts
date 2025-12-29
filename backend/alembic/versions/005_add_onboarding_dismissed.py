"""Add onboarding_dismissed to user_preferences

Revision ID: 005_add_onboarding_dismissed
Revises: 004_add_bonus_scans
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_onboarding_dismissed'
down_revision: Union[str, None] = '004_add_bonus_scans'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add onboarding_dismissed column to user_preferences table."""
    op.add_column(
        'user_preferences',
        sa.Column(
            'onboarding_dismissed',
            sa.Boolean(),
            nullable=False,
            server_default='false'
        )
    )


def downgrade() -> None:
    """Remove onboarding_dismissed column from user_preferences table."""
    op.drop_column('user_preferences', 'onboarding_dismissed')
