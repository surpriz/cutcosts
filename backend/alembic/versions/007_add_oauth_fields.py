"""Add OAuth fields to users table

Revision ID: 007_add_oauth_fields
Revises: 006_paywall_scans_unlimited
Create Date: 2026-03-09

Makes hashed_password nullable for OAuth-only users and adds
oauth_provider column to track which OAuth provider created the account.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision: str = "007_add_oauth_fields"
down_revision: Union[str, None] = "006_paywall_scans_unlimited"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make hashed_password nullable for OAuth-only users
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=True,
    )

    # Add oauth_provider column ("google", "github", or NULL for email/password)
    op.add_column(
        "users",
        sa.Column("oauth_provider", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    # Remove OAuth-only users before making hashed_password non-nullable again
    op.execute("DELETE FROM users WHERE hashed_password IS NULL")

    op.drop_column("users", "oauth_provider")

    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=False,
    )
