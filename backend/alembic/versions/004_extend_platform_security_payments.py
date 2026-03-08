"""Extend platform with security, payments, and logging

Revision ID: 004_extend_platform
Revises: 003_add_subscription_telegram_fields
Create Date: 2026-03-08 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_extend_platform'
down_revision: Union[str, None] = '003_add_sub_telegram'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create channel_access_logs table
    op.create_table(
        'channel_access_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('event_type', sa.Enum('JOIN', 'LEFT', 'KICKED', 'EXPIRED', 'INVITE_CREATED', 'INVITE_REVOKED', name='channelaccesseventtype'), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_channel_access_logs_user_id', 'channel_access_logs', ['user_id'])
    op.create_index('idx_channel_access_logs_event_type', 'channel_access_logs', ['event_type'])
    op.create_index('idx_channel_access_logs_created_at', 'channel_access_logs', ['created_at'])
    
    # Add currency and telegram_channel_id to subscription_plans
    op.add_column('subscription_plans', sa.Column('currency', sa.String(length=3), nullable=False, server_default='RUB'))
    op.add_column('subscription_plans', sa.Column('telegram_channel_id', sa.String(length=50), nullable=True))
    
    # Add plan_id to payments (if not exists)
    # Check if column exists first
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('payments')]
    if 'plan_id' not in columns:
        op.add_column('payments', sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_payments_plan_id', 'payments', 'subscription_plans', ['plan_id'], ['id'])
        op.create_index('idx_payments_plan_id', 'payments', ['plan_id'])
    
    # Rename payment_provider to provider in payments (if exists)
    if 'payment_provider' in columns:
        op.alter_column('payments', 'payment_provider', new_column_name='provider')
    
    # Add payment_id to subscriptions
    op.add_column('subscriptions', sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_subscriptions_payment_id', 'subscriptions', 'payments', ['payment_id'], ['id'])
    op.create_index('idx_subscriptions_payment_id', 'subscriptions', ['payment_id'])


def downgrade() -> None:
    # Remove payment_id from subscriptions
    op.drop_index('idx_subscriptions_payment_id', table_name='subscriptions')
    op.drop_constraint('fk_subscriptions_payment_id', 'subscriptions', type_='foreignkey')
    op.drop_column('subscriptions', 'payment_id')
    
    # Revert provider rename
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('payments')]
    if 'provider' in columns and 'payment_provider' not in columns:
        op.alter_column('payments', 'provider', new_column_name='payment_provider')
    
    # Remove plan_id from payments
    if 'plan_id' in columns:
        op.drop_index('idx_payments_plan_id', table_name='payments')
        op.drop_constraint('fk_payments_plan_id', 'payments', type_='foreignkey')
        op.drop_column('payments', 'plan_id')
    
    # Remove currency and telegram_channel_id from subscription_plans
    op.drop_column('subscription_plans', 'telegram_channel_id')
    op.drop_column('subscription_plans', 'currency')
    
    # Drop channel_access_logs table
    op.drop_index('idx_channel_access_logs_created_at', table_name='channel_access_logs')
    op.drop_index('idx_channel_access_logs_event_type', table_name='channel_access_logs')
    op.drop_index('idx_channel_access_logs_user_id', table_name='channel_access_logs')
    op.drop_table('channel_access_logs')
    op.execute('DROP TYPE IF EXISTS channelaccesseventtype')
