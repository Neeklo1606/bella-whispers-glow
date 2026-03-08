"""Add telegram_invite_link fields to subscriptions table

Revision ID: 003_add_sub_telegram
Revises: 002_add_user_fields
Create Date: 2026-03-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_sub_telegram'
down_revision: Union[str, None] = '002_add_user_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add telegram_invite_link column
    op.add_column('subscriptions', sa.Column('telegram_invite_link', sa.String(length=512), nullable=True))
    
    # Add telegram_invite_link_expires column
    op.add_column('subscriptions', sa.Column('telegram_invite_link_expires', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove telegram_invite_link_expires column
    op.drop_column('subscriptions', 'telegram_invite_link_expires')
    
    # Remove telegram_invite_link column
    op.drop_column('subscriptions', 'telegram_invite_link')
