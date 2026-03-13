"""Add password_hash and role to users table

Revision ID: 002_add_user_fields
Revises: 001_initial
Create Date: 2026-03-08 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_user_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create UserRole enum type
    op.execute("CREATE TYPE userrole AS ENUM ('user', 'admin', 'super_admin')")
    
    # Add password_hash column
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    
    # Add role column with default value
    op.add_column('users', sa.Column('role', postgresql.ENUM('user', 'admin', 'super_admin', name='userrole'), nullable=False, server_default='user'))
    
    # Create index on role
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Update existing admin users (if any) based on is_admin flag
    # Set role to 'admin' for users with is_admin = true
    op.execute("""
        UPDATE users 
        SET role = 'admin' 
        WHERE is_admin = true AND role = 'user'
    """)
    
    # Drop is_admin column (replaced by role)
    op.drop_column('users', 'is_admin')


def downgrade() -> None:
    # Add back is_admin column
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    
    # Update is_admin based on role
    op.execute("""
        UPDATE users 
        SET is_admin = true 
        WHERE role IN ('admin', 'super_admin')
    """)
    
    # Drop index
    op.drop_index('idx_users_role', table_name='users')
    
    # Drop role column
    op.drop_column('users', 'role')
    
    # Drop password_hash column
    op.drop_column('users', 'password_hash')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS userrole')
