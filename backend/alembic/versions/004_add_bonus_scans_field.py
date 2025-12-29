"""Add bonus_scans_this_month to user_subscriptions

Revision ID: 004_add_bonus_scans
Revises: 003_add_password_reset
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_bonus_scans'
down_revision: Union[str, None] = '003_add_password_reset'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add bonus_scans_this_month column to user_subscriptions table."""
    op.add_column(
        'user_subscriptions',
        sa.Column(
            'bonus_scans_this_month',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )


def downgrade() -> None:
    """Remove bonus_scans_this_month column from user_subscriptions table."""
    op.drop_column('user_subscriptions', 'bonus_scans_this_month')
