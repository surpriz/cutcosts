"""add_password_reset_fields

Add password reset token fields to users table for forgot password functionality.

Revision ID: 003_add_password_reset
Revises: 002_merge_heads
Create Date: 2025-12-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_password_reset'
down_revision: Union[str, None] = '002_merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_reset_token column (nullable, indexed for lookup)
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_password_reset_token'), 'users', ['password_reset_token'], unique=False)

    # Add password_reset_token_expires_at column (nullable)
    op.add_column('users', sa.Column('password_reset_token_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Drop columns in reverse order
    op.drop_column('users', 'password_reset_token_expires_at')
    op.drop_index(op.f('ix_users_password_reset_token'), table_name='users')
    op.drop_column('users', 'password_reset_token')
