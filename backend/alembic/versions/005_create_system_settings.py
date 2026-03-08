"""Create system_settings table

Revision ID: 005_create_system_settings
Revises: 004_extend_platform
Create Date: 2026-03-08 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_create_system_settings'
down_revision: Union[str, None] = '004_extend_platform'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # system_settings may already exist from 001_initial; create only if missing
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'system_settings' in inspector.get_table_names():
        return
    op.create_table(
        'system_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('key', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index('idx_system_settings_key', 'system_settings', ['key'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_system_settings_key', table_name='system_settings')
    
    # Drop table
    op.drop_table('system_settings')
